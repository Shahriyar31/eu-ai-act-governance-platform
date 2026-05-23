from src.database.connection import engine, Base
from src.database.models import ClassificationRule, AssessmentHistory, User, AuditLedger, RefreshToken

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables verified.")
    _seed_rules_if_empty()

def _seed_rules_if_empty():
    from src.database.connection import SessionLocal
    from src.database.seed_rules import seed_rules
    seed_rules()
