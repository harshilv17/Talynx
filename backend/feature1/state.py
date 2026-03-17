from typing import TypedDict, Optional, List
from feature1.schemas import JDContent, GuardrailResult, RoleBriefInput


class Feature1State(TypedDict):
    thread_id: str
    role_brief: dict
    
    validation_errors: Optional[List[str]]
    
    jd_draft: Optional[JDContent]
    
    guardrail_result: Optional[GuardrailResult]
    
    review_decision: Optional[str]
    edited_jd: Optional[JDContent]
    feedback: Optional[str]
    
    version: int
    revision_count: int
    
    status: str
    error_message: Optional[str]
