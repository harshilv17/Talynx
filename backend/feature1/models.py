from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.sql import func
from core.db import Base
import enum


class RoleBriefStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    GENERATING = "generating"
    CHECKING = "checking"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    FAILED = "failed"


class JDStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"


class SourcingQueueStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class RoleBrief(Base):
    __tablename__ = "role_briefs"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(RoleBriefStatus), default=RoleBriefStatus.PENDING, nullable=False)
    
    role_title = Column(String, nullable=False)
    team = Column(String, nullable=False)
    seniority = Column(String, nullable=False)
    work_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    
    must_have_skills = Column(JSON, nullable=False)
    nice_to_have_skills = Column(JSON, default=list)
    
    salary_min = Column(Integer, nullable=False)
    salary_max = Column(Integer, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    
    headcount = Column(Integer, default=1, nullable=False)
    
    years_of_experience = Column(Integer, nullable=True)
    reports_to = Column(String, nullable=True)
    key_outcomes = Column(JSON, nullable=True)
    context_note = Column(Text, nullable=True)
    tone_preference = Column(String, default="conversational", nullable=False)
    
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    role_brief_id = Column(Integer, ForeignKey("role_briefs.id"), nullable=False)
    thread_id = Column(String, index=True, nullable=False)
    
    version = Column(Integer, default=1, nullable=False)
    status = Column(Enum(JDStatus), default=JDStatus.DRAFT, nullable=False)
    
    jd_content = Column(JSON, nullable=False)
    
    guardrail_passed = Column(Integer, nullable=False)
    guardrail_issues = Column(JSON, nullable=True)
    guardrail_corrected_jd = Column(JSON, nullable=True)
    tone_score = Column(Float, nullable=True)
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SourcingQueue(Base):
    __tablename__ = "sourcing_queue"

    id = Column(Integer, primary_key=True, index=True)
    role_brief_id = Column(Integer, ForeignKey("role_briefs.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    thread_id = Column(String, index=True, nullable=False)
    status = Column(Enum(SourcingQueueStatus), default=SourcingQueueStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
