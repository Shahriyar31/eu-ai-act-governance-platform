from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from src.database.connection import Base
from pgvector.sqlalchemy import Vector


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


class AssessmentHistory(Base):
    __tablename__ = "assessment_history"
    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    risk_tier = Column(String, nullable=False)
    dpia_required = Column(Boolean, nullable=False)
    justification = Column(Text, nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=True)

    # which organisation this assessment belongs to
    org_id = Column(Integer, nullable=True)

class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    plan = Column(String, default="free", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # which organisation this user belongs to
    # nullable=True so existing users without an org don't break
    org_id = Column(Integer, nullable=True)

    # role within the organisation
    role = Column(String, default="analyst", nullable=True)


class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    action = Column(String, nullable=False)
    system_name = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    previous_hash = Column(String, nullable=False)
    record_hash = Column(String, nullable=False)
    signature = Column(String, nullable=False)


class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    regulation = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
