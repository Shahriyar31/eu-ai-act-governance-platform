import pytest
from unittest.mock import MagicMock
from src.models.schemas import ClassificationRequest, RiskTierEnum, SectorEnum
from src.governance.classifier import classify_ai_system, _rule_matches, _get_obligations
from src.database.models import ClassificationRule


def make_rule(risk_tier, keyword=None, sector=None, automated_decision=None,
              processes_personal_data=None, interacts_with_humans=None,
              justification_template="Test justification.", priority=1):
    """Create a mock ClassificationRule — avoids needing a real database."""
    rule = MagicMock(spec=ClassificationRule)
    rule.keyword = keyword
    rule.sector = sector
    rule.automated_decision = automated_decision
    rule.processes_personal_data = processes_personal_data
    rule.interacts_with_humans = interacts_with_humans
    rule.risk_tier = risk_tier
    rule.justification_template = justification_template
    rule.priority = priority
    rule.is_active = True
    return rule


def make_request(**kwargs):
    """Create a ClassificationRequest with safe defaults for testing."""
    defaults = dict(
        system_name="Test System",
        description="A generic AI system",
        sector=SectorEnum.finance,
        automated_decision=False,
        processes_personal_data=False,
        interacts_with_humans=False
    )
    defaults.update(kwargs)
    return ClassificationRequest(**defaults)


def make_db(rules):
    """Create a mock DB session that returns the given list of rules."""
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = rules
    return db


class TestRuleMatching:
    """Tests for the _rule_matches helper function."""

    def test_keyword_present_in_description_matches(self):
        rule = make_rule("high", keyword="facial recognition")
        request = make_request(description="A facial recognition system for police")
        assert _rule_matches(rule, request, "a facial recognition system for police") is True

    def test_keyword_absent_from_description_no_match(self):
        rule = make_rule("high", keyword="facial recognition")
        request = make_request(description="A spam filter")
        assert _rule_matches(rule, request, "a spam filter") is False

    def test_sector_match_returns_true(self):
        rule = make_rule("high", keyword=None, sector="healthcare")
        request = make_request(sector=SectorEnum.healthcare)
        assert _rule_matches(rule, request, "a medical system") is True

    def test_sector_mismatch_returns_false(self):
        rule = make_rule("high", keyword=None, sector="healthcare")
        request = make_request(sector=SectorEnum.finance)
        assert _rule_matches(rule, request, "a finance system") is False

    def test_automated_decision_flag_matches(self):
        rule = make_rule("high", keyword=None, automated_decision=True)
        request = make_request(automated_decision=True)
        assert _rule_matches(rule, request, "some system") is True

    def test_automated_decision_flag_mismatch(self):
        rule = make_rule("high", keyword=None, automated_decision=True)
        request = make_request(automated_decision=False)
        assert _rule_matches(rule, request, "some system") is False


class TestClassification:
    """Tests for the main classify_ai_system function."""

    def test_keyword_rule_classifies_as_high_risk(self):
        rules = [make_rule("high", keyword="facial recognition",
                           justification_template="Facial recognition is high risk.")]
        db = make_db(rules)
        request = make_request(description="A facial recognition system")
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.high

    def test_no_matching_rule_defaults_to_minimal(self):
        # Empty rule set — system doesn't match any known risk category
        db = make_db([])
        request = make_request(description="A simple recommendation engine")
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.minimal

    def test_unacceptable_system_dpia_not_required(self):
        # Prohibited systems don't need DPIA — they must be shut down entirely
        rules = [make_rule("unacceptable", keyword="social scoring",
                           justification_template="Social scoring is prohibited under Article 5.")]
        db = make_db(rules)
        request = make_request(description="A social scoring system", processes_personal_data=True)
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.unacceptable
        assert result.dpia_required is False

    def test_high_risk_with_personal_data_requires_dpia(self):
        rules = [make_rule("high", keyword="loan",
                           justification_template="Credit scoring is high risk.")]
        db = make_db(rules)
        request = make_request(description="A loan approval system", processes_personal_data=True)
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.high
        assert result.dpia_required is True

    def test_high_risk_without_personal_data_no_dpia(self):
        rules = [make_rule("high", keyword="loan",
                           justification_template="Credit scoring is high risk.")]
        db = make_db(rules)
        request = make_request(description="A loan approval system", processes_personal_data=False)
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.high
        assert result.dpia_required is False

    def test_minimal_risk_never_requires_dpia(self):
        # Even if system processes personal data, minimal risk = no DPIA required
        db = make_db([])
        request = make_request(description="A spam filter", processes_personal_data=True)
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.minimal
        assert result.dpia_required is False

    def test_automated_decision_adds_warning_to_justification(self):
        rules = [make_rule("high", keyword="hiring",
                           justification_template="Hiring AI is high risk.")]
        db = make_db(rules)
        request = make_request(description="A hiring system", automated_decision=True)
        result = classify_ai_system(request, db)
        assert "Automated decision-making" in result.justification

    def test_human_oversight_noted_in_justification(self):
        rules = [make_rule("high", keyword="hiring",
                           justification_template="Hiring AI is high risk.")]
        db = make_db(rules)
        request = make_request(description="A hiring system", automated_decision=False)
        result = classify_ai_system(request, db)
        assert "Human oversight" in result.justification

    def test_system_name_preserved_in_response(self):
        db = make_db([])
        request = make_request(system_name="AcmeCorp AI Recruiter")
        result = classify_ai_system(request, db)
        assert result.system_name == "AcmeCorp AI Recruiter"

    def test_first_matching_rule_wins_by_priority(self):
        # Both rules match — lower priority number (1) wins over (2)
        rule_high = make_rule("high", keyword="medical", priority=1,
                              justification_template="Medical AI is high risk.")
        rule_limited = make_rule("limited", keyword="medical", priority=2,
                                 justification_template="Medical AI has limited risk.")
        db = make_db([rule_high, rule_limited])
        request = make_request(description="A medical diagnosis system")
        result = classify_ai_system(request, db)
        assert result.risk_tier == RiskTierEnum.high


class TestObligations:
    """Tests for sector and flag-specific obligation generation."""

    def test_unacceptable_risk_includes_prohibition_notice(self):
        request = make_request()
        obligations = _get_obligations(RiskTierEnum.unacceptable, request)
        assert any("prohibited" in o.lower() for o in obligations)

    def test_healthcare_sector_includes_mdr_requirement(self):
        request = make_request(sector=SectorEnum.healthcare)
        obligations = _get_obligations(RiskTierEnum.high, request)
        assert any("Medical Device Regulation" in o for o in obligations)

    def test_personal_data_adds_dpia_obligation(self):
        request = make_request(processes_personal_data=True)
        obligations = _get_obligations(RiskTierEnum.high, request)
        assert any("Data Protection Impact Assessment" in o for o in obligations)

    def test_automated_decision_adds_human_review_obligation(self):
        request = make_request(automated_decision=True)
        obligations = _get_obligations(RiskTierEnum.high, request)
        assert any("human review" in o.lower() for o in obligations)

    def test_minimal_risk_states_no_mandatory_obligations(self):
        request = make_request()
        obligations = _get_obligations(RiskTierEnum.minimal, request)
        assert any("No mandatory" in o for o in obligations)

    def test_high_risk_includes_article_9_risk_management(self):
        request = make_request()
        obligations = _get_obligations(RiskTierEnum.high, request)
        assert any("Article 9" in o for o in obligations)