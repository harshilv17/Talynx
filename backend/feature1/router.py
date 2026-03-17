from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from feature1.schemas import (
    RoleBriefInput, StartJobResponse, StatusResponse, 
    ReviewDecisionInput, ReviewDecisionResponse, PublishedJDResponse,
    JDContent, GuardrailResult
)
from feature1.models import RoleBrief, JobDescription, RoleBriefStatus
from feature1.state import Feature1State
from feature1.graph import create_feature1_graph
from feature1.checkpointer import get_checkpointer
from core.db import get_db
from datetime import datetime

router = APIRouter(prefix="/api/v1/feature1", tags=["feature1"])


def run_graph_background(thread_id: str, initial_state: Feature1State):
    """Run the graph as a background task."""
    from core.db import SessionLocal
    
    db = SessionLocal()
    try:
        checkpointer = get_checkpointer()
        graph = create_feature1_graph(db, checkpointer)
        
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        graph.invoke(initial_state, config)
    
    except Exception as e:
        db_role_brief = db.query(RoleBrief).filter(
            RoleBrief.thread_id == thread_id
        ).first()
        if db_role_brief:
            db_role_brief.status = RoleBriefStatus.FAILED
            db_role_brief.error_message = str(e)
            db.commit()
    
    finally:
        db.close()


@router.post("/start", response_model=StartJobResponse)
def start_job_generation(
    role_brief_input: RoleBriefInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start the JD generation process."""
    
    thread_id = str(uuid.uuid4())
    
    role_brief_data = role_brief_input.dict()
    
    db_role_brief = RoleBrief(
        thread_id=thread_id,
        status=RoleBriefStatus.PENDING,
        **role_brief_data
    )
    db.add(db_role_brief)
    db.commit()
    db.refresh(db_role_brief)
    
    initial_state: Feature1State = {
        "thread_id": thread_id,
        "role_brief": role_brief_data,
        "validation_errors": None,
        "jd_draft": None,
        "guardrail_result": None,
        "review_decision": None,
        "edited_jd": None,
        "feedback": None,
        "version": 1,
        "revision_count": 0,
        "status": "validating",
        "error_message": None
    }
    
    background_tasks.add_task(run_graph_background, thread_id, initial_state)
    
    return StartJobResponse(thread_id=thread_id, status="validating")


@router.get("/status/{thread_id}", response_model=StatusResponse)
def get_status(thread_id: str, db: Session = Depends(get_db)):
    """Get current status of the JD generation process."""
    
    db_role_brief = db.query(RoleBrief).filter(
        RoleBrief.thread_id == thread_id
    ).first()
    
    if not db_role_brief:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    checkpointer = get_checkpointer()
    
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    try:
        checkpoint = checkpointer.get(config)
        
        if checkpoint and checkpoint.channel_values:
            state = checkpoint.channel_values
            
            jd_draft = None
            if state.get("jd_draft"):
                jd_draft = JDContent(**state["jd_draft"])
            
            guardrail_result = None
            if state.get("guardrail_result"):
                gr = state["guardrail_result"]
                guardrail_result = GuardrailResult(**gr)
            
            role_brief_dict = {
                "role_title": db_role_brief.role_title,
                "team": db_role_brief.team,
                "seniority": db_role_brief.seniority,
                "work_type": db_role_brief.work_type,
                "location": db_role_brief.location,
                "must_have_skills": db_role_brief.must_have_skills,
                "nice_to_have_skills": db_role_brief.nice_to_have_skills,
                "salary_min": db_role_brief.salary_min,
                "salary_max": db_role_brief.salary_max,
                "currency": db_role_brief.currency,
                "headcount": db_role_brief.headcount,
                "tone_preference": db_role_brief.tone_preference,
            }
            
            return StatusResponse(
                thread_id=thread_id,
                status=state.get("status", db_role_brief.status.value),
                role_brief=role_brief_dict,
                jd_draft=jd_draft,
                guardrail_result=guardrail_result,
                version=state.get("version", 1),
                error_message=state.get("error_message") or db_role_brief.error_message
            )
    
    except Exception:
        pass
    
    return StatusResponse(
        thread_id=thread_id,
        status=db_role_brief.status.value,
        error_message=db_role_brief.error_message
    )


@router.post("/review/{thread_id}", response_model=ReviewDecisionResponse)
def submit_review_decision(
    thread_id: str,
    decision: ReviewDecisionInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit review decision and resume the graph."""
    
    db_role_brief = db.query(RoleBrief).filter(
        RoleBrief.thread_id == thread_id
    ).first()
    
    if not db_role_brief:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if db_role_brief.status != RoleBriefStatus.PENDING_REVIEW:
        raise HTTPException(status_code=400, detail="Job is not pending review")
    
    checkpointer = get_checkpointer()
    
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    checkpoint = checkpointer.get(config)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="No checkpoint found for this thread")
    
    state = checkpoint.channel_values
    revision_count = state.get("revision_count", 0)
    
    if decision.action == "revise" and revision_count >= 3:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 3 revisions reached. Please use inline edit instead."
        )
    
    def resume_graph():
        db_local = SessionLocal()
        try:
            checkpointer_local = get_checkpointer()
            graph = create_feature1_graph(db_local, checkpointer_local)
            
            checkpoint = checkpointer_local.get(config)
            if checkpoint:
                current_state = dict(checkpoint.channel_values)
                
                current_state["review_decision"] = decision.action.value
                
                if decision.action == "edit" and decision.edited_jd:
                    current_state["edited_jd"] = decision.edited_jd.dict()
                
                elif decision.action == "revise" and decision.feedback:
                    current_state["feedback"] = decision.feedback
                
                graph.invoke(current_state, config)
        finally:
            db_local.close()
    
    from core.db import SessionLocal
    background_tasks.add_task(resume_graph)
    
    new_status = "publishing" if decision.action in ["approve", "edit"] else "generating"
    
    return ReviewDecisionResponse(
        success=True,
        message="Review decision submitted",
        new_status=new_status
    )


@router.get("/published/{thread_id}", response_model=PublishedJDResponse)
def get_published_jd(thread_id: str, db: Session = Depends(get_db)):
    """Get the published job description."""
    
    jd_record = db.query(JobDescription).filter(
        JobDescription.thread_id == thread_id,
        JobDescription.status == JDStatus.PUBLISHED
    ).first()
    
    if not jd_record:
        raise HTTPException(status_code=404, detail="Published JD not found")
    
    return PublishedJDResponse(
        thread_id=thread_id,
        jd_content=JDContent(**jd_record.jd_content),
        published_at=jd_record.published_at.isoformat(),
        version=jd_record.version
    )
