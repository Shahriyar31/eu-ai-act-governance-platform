from src.database.connection import SessionLocal
from src.database.models import ClassificationRule

def seed_rules():
    db = SessionLocal()
    try:
        existing = db.query(ClassificationRule).count()
        if existing >= 30:
            print(f"Rules already seeded ({existing} rules). Skipping.")
            return

        rules = [
            # Annex III — Biometric identification
            ClassificationRule(
                keyword="facial recognition",
                risk_tier="high",
                justification_template="Biometric identification systems are listed in EU AI Act Annex III Article 1(a) as high-risk.",
                priority=1, is_active=True
            ),
            ClassificationRule(
                keyword="biometric",
                risk_tier="high",
                justification_template="Biometric categorisation systems fall under EU AI Act Annex III and require full conformity assessment.",
                priority=2, is_active=True
            ),
            ClassificationRule(
                keyword="emotion recognition",
                risk_tier="high",
                justification_template="Emotion recognition systems in workplaces and education are high-risk under EU AI Act Annex III.",
                priority=3, is_active=True
            ),
            # Annex III — Critical infrastructure
            ClassificationRule(
                keyword="power grid",
                risk_tier="high",
                justification_template="AI managing critical infrastructure components is high-risk under EU AI Act Annex III Article 1(b).",
                priority=4, is_active=True
            ),
            ClassificationRule(
                keyword="water treatment",
                risk_tier="high",
                justification_template="AI in critical infrastructure (water, energy, transport) is high-risk under EU AI Act Annex III.",
                priority=5, is_active=True
            ),
            # Annex III — Education
            ClassificationRule(
                keyword="student assessment",
                risk_tier="high",
                justification_template="AI determining access to education or assessing students is high-risk under EU AI Act Annex III Article 1(c).",
                priority=6, is_active=True
            ),
            ClassificationRule(
                keyword="admission",
                risk_tier="high",
                justification_template="AI used in educational admissions decisions is high-risk under EU AI Act Annex III.",
                priority=7, is_active=True
            ),
            # Annex III — Employment
            ClassificationRule(
                keyword="recruitment",
                risk_tier="high",
                justification_template="AI used in recruitment, CV screening, and hiring decisions is high-risk under EU AI Act Annex III Article 1(d).",
                priority=8, is_active=True
            ),
            ClassificationRule(
                keyword="hiring",
                risk_tier="high",
                justification_template="Automated hiring systems must comply with EU AI Act Annex III high-risk requirements.",
                priority=9, is_active=True
            ),
            ClassificationRule(
                keyword="performance evaluation",
                risk_tier="high",
                justification_template="AI evaluating employee performance is high-risk under EU AI Act Annex III.",
                priority=10, is_active=True
            ),
            # Annex III — Essential services
            ClassificationRule(
                keyword="credit score",
                risk_tier="high",
                justification_template="AI evaluating creditworthiness is high-risk under EU AI Act Annex III Article 1(e).",
                priority=11, is_active=True
            ),
            ClassificationRule(
                keyword="loan approval",
                risk_tier="high",
                justification_template="Automated loan decisions are high-risk under EU AI Act Annex III.",
                priority=12, is_active=True
            ),
            ClassificationRule(
                keyword="insurance",
                risk_tier="high",
                justification_template="AI assessing insurance risk or setting premiums is high-risk under EU AI Act Annex III.",
                priority=13, is_active=True
            ),
            # Annex III — Law enforcement
            ClassificationRule(
                keyword="predictive policing",
                risk_tier="high",
                justification_template="Predictive policing systems are high-risk under EU AI Act Annex III Article 1(f).",
                priority=14, is_active=True
            ),
            ClassificationRule(
                keyword="lie detection",
                risk_tier="high",
                justification_template="AI-based lie detection or emotion assessment by law enforcement is high-risk.",
                priority=15, is_active=True
            ),
            # Article 5 — Prohibited systems
            ClassificationRule(
                keyword="social scoring",
                risk_tier="unacceptable",
                justification_template="Social scoring systems by public authorities are prohibited under EU AI Act Article 5(1)(c).",
                priority=16, is_active=True
            ),
            ClassificationRule(
                keyword="subliminal",
                risk_tier="unacceptable",
                justification_template="AI using subliminal techniques to manipulate behaviour is prohibited under EU AI Act Article 5(1)(a).",
                priority=17, is_active=True
            ),
            ClassificationRule(
                keyword="real-time biometric surveillance",
                risk_tier="unacceptable",
                justification_template="Real-time remote biometric identification in public spaces is prohibited under EU AI Act Article 5(1)(d).",
                priority=18, is_active=True
            ),
            ClassificationRule(
                keyword="exploit vulnerability",
                risk_tier="unacceptable",
                justification_template="AI exploiting vulnerabilities of specific groups is prohibited under EU AI Act Article 5(1)(b).",
                priority=19, is_active=True
            ),
            # Limited risk — transparency obligations
            ClassificationRule(
                keyword="chatbot",
                risk_tier="limited",
                justification_template="Chatbots must disclose their AI nature to users under EU AI Act Article 52(1).",
                priority=20, is_active=True
            ),
            ClassificationRule(
                keyword="deepfake",
                risk_tier="limited",
                justification_template="AI generating deepfakes must label content as artificially generated under EU AI Act Article 52(3).",
                priority=21, is_active=True
            ),
            ClassificationRule(
                keyword="synthetic media",
                risk_tier="limited",
                justification_template="Synthetic media generation systems must mark output as AI-generated under EU AI Act Article 52.",
                priority=22, is_active=True
            ),
            # Minimal risk
            ClassificationRule(
                keyword="spam filter",
                risk_tier="minimal",
                justification_template="Spam filters pose minimal risk and have no mandatory EU AI Act obligations.",
                priority=23, is_active=True
            ),
            ClassificationRule(
                keyword="recommendation",
                risk_tier="minimal",
                justification_template="Content recommendation systems carry minimal risk unless used in critical contexts.",
                priority=24, is_active=True
            ),
        ]

        db.bulk_save_objects(rules)
        db.commit()
        print(f"Seeded {len(rules)} EU AI Act classification rules.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_rules()