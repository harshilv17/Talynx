from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum


class Seniority(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    LEAD = "lead"


class WorkType(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class TonePreference(str, Enum):
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"


class RoleBriefInput(BaseModel):
    role_title: str = Field(..., min_length=1)
    team: str = Field(..., min_length=1)
    seniority: Seniority
    work_type: WorkType
    location: str = Field(..., min_length=1)
    
    must_have_skills: List[str] = Field(..., min_length=1)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    
    salary_min: int = Field(..., gt=0)
    salary_max: int = Field(..., gt=0)
    currency: str = Field(default="USD")
    
    headcount: int = Field(default=1, gt=0)
    
    years_of_experience: Optional[int] = Field(default=None, ge=0)
    reports_to: Optional[str] = None
    key_outcomes: Optional[List[str]] = None
    context_note: Optional[str] = None
    tone_preference: TonePreference = Field(default=TonePreference.CONVERSATIONAL)

    @field_validator("salary_max")
    @classmethod
    def validate_salary_range(cls, v, info):
        if "salary_min" in info.data and v < info.data["salary_min"]:
            raise ValueError("salary_max must be greater than or equal to salary_min")
        return v


class StartJobResponse(BaseModel):
    thread_id: str
    status: str


class JDContent(BaseModel):
    job_title: str
    tagline: str
    about_role: str
    responsibilities: List[str]
    requirements: List[str]
    nice_to_haves: List[str]
    company_blurb: str
    salary_range: str
    location_work_type: str


class GuardrailIssue(BaseModel):
    issue: str
    original_text: str
    suggested_fix: str


class GuardrailResult(BaseModel):
    passed: bool
    issues: List[GuardrailIssue]
    corrected_jd: Optional[JDContent]
    tone_score: float


class StatusResponse(BaseModel):
    thread_id: str
    status: str
    role_brief: Optional[Dict[str, Any]] = None
    jd_draft: Optional[JDContent] = None
    guardrail_result: Optional[GuardrailResult] = None
    version: Optional[int] = None
    error_message: Optional[str] = None


class ReviewAction(str, Enum):
    APPROVE = "approve"
    EDIT = "edit"
    REVISE = "revise"


class ReviewDecisionInput(BaseModel):
    action: ReviewAction
    edited_jd: Optional[JDContent] = None
    feedback: Optional[str] = None


class ReviewDecisionResponse(BaseModel):
    success: bool
    message: str
    new_status: str


class PublishedJDResponse(BaseModel):
    thread_id: str
    jd_content: JDContent
    published_at: str
    version: int
