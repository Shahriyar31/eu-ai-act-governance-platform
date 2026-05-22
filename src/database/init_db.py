from src.database.connection import engine, Base
from src.database.models import ClassificationRule, AssessmentHistory

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables verified.")
