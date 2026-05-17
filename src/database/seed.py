import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.connection import SessionLocal, engine, Base
from src.database.models import ClassificationRule

Base.metadata.create_all(bind=engine)

RULES = [
    ClassificationRule(
        sector=None,
        keyword="social scoring",
        risk_tier="unacceptable",
        justification_template="System description contains indicators of prohibited AI: 'social scoring'. This system is banned under EU AI Act Article 5.",
        priority=1,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        keyword="mass surveillance",
        risk_tier="unacceptable",
        justification_template="System description contains indicators of prohibited AI: 'mass surveillance'. This system is banned under EU AI Act Article 5.",
        priority=1,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        keyword="biometric surveillance",
        risk_tier="unacceptable",
        justification_template="System description contains indicators of prohibited AI: 'biometric surveillance'. This system is banned under EU AI Act Article 5.",
        priority=1,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        keyword="subliminal manipulation",
        risk_tier="unacceptable",
        justification_template="System description contains indicators of prohibited AI: 'subliminal manipulation'. This system is banned under EU AI Act Article 5.",
        priority=1,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        keyword="exploit vulnerability",
        risk_tier="unacceptable",
        justification_template="System description contains indicators of prohibited AI: 'exploit vulnerability'. This system is banned under EU AI Act Article 5.",
        priority=1,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        keyword="real-time biometric",
        risk_tier="unacceptable",
        justification_template="System description contains indicators of prohibited AI: 'real-time biometric'. This system is banned under EU AI Act Article 5.",
        priority=1,
        is_active=True
    ),
    ClassificationRule(
        sector="healthcare",
        risk_tier="high",
        justification_template="System operates in the 'healthcare' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="employment",
        risk_tier="high",
        justification_template="System operates in the 'employment' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="education",
        risk_tier="high",
        justification_template="System operates in the 'education' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="law_enforcement",
        risk_tier="high",
        justification_template="System operates in the 'law_enforcement' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="border_control",
        risk_tier="high",
        justification_template="System operates in the 'border_control' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="critical_infrastructure",
        risk_tier="high",
        justification_template="System operates in the 'critical_infrastructure' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="justice",
        risk_tier="high",
        justification_template="System operates in the 'justice' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector="finance",
        risk_tier="high",
        justification_template="System operates in the 'finance' sector which is listed under Annex III of the EU AI Act as High Risk.",
        priority=2,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        interacts_with_humans=True,
        risk_tier="limited",
        justification_template="System interacts directly with humans. Transparency obligations apply under EU AI Act Article 50.",
        priority=3,
        is_active=True
    ),
    ClassificationRule(
        sector=None,
        risk_tier="minimal",
        justification_template="System does not fall under any high-risk category defined in EU AI Act Annex III and does not interact directly with humans in a way that triggers transparency obligations.",
        priority=4,
        is_active=True
    ),
]

def seed():
    db = SessionLocal()
    try:
        existing = db.query(ClassificationRule).first()
        if existing:
            print("Database already seeded. Skipping.")
            return

        for rule in RULES:
            db.add(rule)

        db.commit()
        print(f"Seeded {len(RULES)} rules successfully.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()