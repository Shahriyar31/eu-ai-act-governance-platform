from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from src.database.connection import Base

class ClassificationRule(Base):
    __tablename__ = "classification_rules"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String, nullable=True)
    automated_decision = Column(Boolean, nullable=True)
    processes_personal_data = Column(Boolean, nullable=True)
    interacts_with_humans = Column(Boolean, nullable=True)
    keyword = Column(String, nullable=True)
    risk_tier = Column(String, nullable=False)
    justification_template = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())