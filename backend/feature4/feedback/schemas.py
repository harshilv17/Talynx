"""Pydantic models for the rejection feedback API."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SkillGap(BaseModel):
    skill: str
    importance: str  # "must_have" | "nice_to_have"
    recommendation: str


class RAGMetadata(BaseModel):
    chunks_used: int
    retrieval_scores: List[float]
    embedding_model: str
    total_chunks: int


class RejectionFeedback(BaseModel):
    feedback_id: str
    generated_at: datetime
    model_used: str
    version: int
    strengths: List[str]
    skill_gaps: List[SkillGap]
    experience_gaps: List[str]
    improvement_suggestions: List[str]
    technologies_to_learn: List[str]
    overall_summary: str
    encouragement: str
    rag_metadata: RAGMetadata
    email_sent: bool
    email_sent_at: Optional[datetime] = None


class FeedbackResponse(BaseModel):
    success: bool
    candidate_id: str
    candidate_name: str
    feedback: RejectionFeedback


class FeedbackListItem(BaseModel):
    candidate_id: str
    candidate_name: str
    status: str
    feedback_version: int
    generated_at: datetime
    email_sent: bool


class FeedbackListResponse(BaseModel):
    job_id: str
    total: int
    feedbacks: List[FeedbackListItem]


class SendFeedbackResponse(BaseModel):
    success: bool
    message: str
    candidate_id: str

class BulkResultError(BaseModel):
    candidate_id: str
    candidate_name: str
    error: str

class BulkFeedbackGenerateResponse(BaseModel):
    success: bool
    job_id: str
    total_processed: int
    success_count: int
    failure_count: int
    errors: List[BulkResultError]

class BulkFeedbackSendResponse(BaseModel):
    success: bool
    job_id: str
    total_processed: int
    success_count: int
    failure_count: int
    errors: List[BulkResultError]
