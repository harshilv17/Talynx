from pydantic import BaseModel, field_validator
from typing import List, Optional


class OutreachTarget(BaseModel):
    """A single candidate + their email address for outreach."""
    candidate_id: str
    email:        str

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Not a valid email address")
        return v.strip().lower()


class OutreachRequest(BaseModel):
    job_id:     str
    candidates: List[OutreachTarget]


class OutreachSuccess(BaseModel):
    candidate_id: str
    name:         str
    email:        str
    subject:      str


class OutreachFailure(BaseModel):
    candidate_id: str
    email:        str
    error:        str


class OutreachResponse(BaseModel):
    job_id:    str
    sent:      List[OutreachSuccess]
    failed:    List[OutreachFailure]
    total:     int
    sent_count: int
    failed_count: int


class RetryRequest(BaseModel):
    job_id: str


class EmailPreviewRequest(BaseModel):
    candidate_id: str
    job_id:       str


class EmailPreviewResponse(BaseModel):
    candidate_id: str
    name:         str
    subject:      str
    body:         str
