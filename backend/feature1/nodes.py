from typing import Dict, Any
import json
import time
from openai import OpenAI
from feature1.state import Feature1State
from feature1.schemas import JDContent, GuardrailResult, GuardrailIssue
from feature1.prompts import get_jd_generation_prompt, get_guardrail_prompt, format_jd_for_guardrail
from feature1.models import RoleBriefStatus, JDStatus
from feature1 import db_ops
from core.openai_client import get_openai_client
from langgraph.types import interrupt


MAX_RETRIES = 2
INITIAL_BACKOFF = 1


def call_openai_with_retry(client: OpenAI, model: str, messages: list, max_retries: int = MAX_RETRIES) -> dict:
    """Call OpenAI API with exponential backoff retry logic."""
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            if attempt == max_retries:
                raise Exception(f"OpenAI API call failed after {max_retries + 1} attempts: {str(e)}")
            
            backoff_time = INITIAL_BACKOFF * (2 ** attempt)
            time.sleep(backoff_time)
    
    raise Exception("Unexpected error in retry logic")


def validate_node(state: Feature1State) -> Feature1State:
    """Validate the role brief input."""
    
    role_brief = state["role_brief"]
    errors = []
    
    required_fields = ["role_title", "team", "seniority", "work_type", "location", 
                       "must_have_skills", "salary_min", "salary_max"]
    
    for field in required_fields:
        if not role_brief.get(field):
            errors.append(f"Missing required field: {field}")
    
    if role_brief.get("must_have_skills") and len(role_brief["must_have_skills"]) == 0:
        errors.append("At least one must-have skill is required")
    
    if role_brief.get("salary_min") and role_brief.get("salary_max"):
        if role_brief["salary_max"] < role_brief["salary_min"]:
            errors.append("salary_max must be greater than or equal to salary_min")
    
    valid_seniority = ["entry", "junior", "mid", "senior", "staff", "principal", "lead"]
    if role_brief.get("seniority") and role_brief["seniority"] not in valid_seniority:
        errors.append(f"Invalid seniority: {role_brief['seniority']}")
    
    valid_work_types = ["remote", "hybrid", "onsite"]
    if role_brief.get("work_type") and role_brief["work_type"] not in valid_work_types:
        errors.append(f"Invalid work_type: {role_brief['work_type']}")
    
    if errors:
        state["validation_errors"] = errors
        state["status"] = "failed"
        db_ops.update_role_brief_status(state["thread_id"], RoleBriefStatus.FAILED, "; ".join(errors))
        return state
    
    state["validation_errors"] = None
    state["status"] = "generating"
    db_ops.update_role_brief_status(state["thread_id"], RoleBriefStatus.GENERATING)
    return state


def jd_generation_node(state: Feature1State) -> Feature1State:
    """Generate job description using GPT-4o."""
    
    client = get_openai_client()
    role_brief = state["role_brief"]
    
    is_revision = state.get("revision_count", 0) > 0 and state.get("feedback") is not None
    previous_jd = state.get("jd_draft")
    feedback = state.get("feedback")
    
    previous_jd_dict = None
    if previous_jd:
        if isinstance(previous_jd, dict):
            previous_jd_dict = previous_jd
        else:
            previous_jd_dict = previous_jd.dict()
    
    prompt = get_jd_generation_prompt(
        role_brief=role_brief,
        tone=role_brief.get("tone_preference", "conversational"),
        is_revision=is_revision,
        previous_jd=previous_jd_dict,
        feedback=feedback
    )
    
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Generate the job description based on the role brief provided. Return only valid JSON."}
        ]
        
        result = call_openai_with_retry(client, "gpt-4o", messages)
        
        jd_content = JDContent(**result)
        state["jd_draft"] = jd_content.dict()
        state["status"] = "checking"
        
        if is_revision:
            state["feedback"] = None
        
        db_ops.update_role_brief_status(state["thread_id"], RoleBriefStatus.CHECKING)
        return state
    
    except Exception as e:
        state["status"] = "failed"
        state["error_message"] = f"JD generation failed: {str(e)}"
        db_ops.update_role_brief_status(state["thread_id"], RoleBriefStatus.FAILED, state["error_message"])
        return state


def guardrail_node(state: Feature1State) -> Feature1State:
    """Check JD for compliance issues using GPT-4o-mini."""
    
    client = get_openai_client()
    jd_draft = state["jd_draft"]
    
    if not jd_draft:
        state["status"] = "failed"
        state["error_message"] = "No JD draft available for guardrail check"
        return state
    
    jd_dict = jd_draft if isinstance(jd_draft, dict) else jd_draft.dict()
    formatted_jd = format_jd_for_guardrail(jd_dict)
    system_prompt = get_guardrail_prompt()
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this job description:\n\n{formatted_jd}"}
        ]
        
        result = call_openai_with_retry(client, "gpt-4o-mini", messages)
        
        issues = [GuardrailIssue(**issue) for issue in result.get("issues", [])]
        corrected_jd = None
        
        if not result["passed"] and result.get("corrected_jd"):
            corrected_jd = JDContent(**result["corrected_jd"])
            state["jd_draft"] = corrected_jd.dict()
        
        guardrail_result = GuardrailResult(
            passed=result["passed"],
            issues=issues,
            corrected_jd=corrected_jd,
            tone_score=result.get("tone_score", 0.0)
        )
        
        state["guardrail_result"] = guardrail_result.dict()
        state["status"] = "pending_review"
        
        db_ops.update_role_brief_status(state["thread_id"], RoleBriefStatus.PENDING_REVIEW)
        
        role_brief = db_ops.get_role_brief_by_thread(state["thread_id"])
        if not role_brief:
            state["status"] = "failed"
            state["error_message"] = "Role brief not found"
            return state
        
        current_version = state.get("version", 1)
        jd_content = state["jd_draft"] if isinstance(state["jd_draft"], dict) else state["jd_draft"].dict()
        db_ops.insert_job_description(
            state["thread_id"],
            role_brief["_id"],
            {
                "version": current_version,
                "status": JDStatus.PENDING_REVIEW,
                "jd_content": jd_content,
                "guardrail_passed": 1 if result["passed"] else 0,
                "guardrail_issues": result.get("issues", []),
                "guardrail_corrected_jd": result.get("corrected_jd"),
                "tone_score": result.get("tone_score", 0.0),
            },
        )
        
        return state
    
    except Exception as e:
        state["status"] = "failed"
        state["error_message"] = f"Guardrail check failed: {str(e)}"
        db_ops.update_role_brief_status(state["thread_id"], RoleBriefStatus.FAILED, state["error_message"])
        return state


def review_node(state: Feature1State) -> Feature1State:
    """Human-in-the-loop review gate. Graph pauses here."""
    
    if state.get("review_decision"):
        decision = state["review_decision"]
        
        if decision == "edit" and state.get("edited_jd"):
            return state
        
        elif decision == "revise" and state.get("feedback"):
            state["revision_count"] = state.get("revision_count", 0) + 1
            state["version"] = state.get("version", 1) + 1
            return state
        
        elif decision == "approve":
            return state
    
    interrupt("awaiting_human_review")
    
    return state


def publish_node(state: Feature1State) -> Feature1State:
    """Publish the approved JD and create sourcing queue record."""
    
    thread_id = state["thread_id"]
    
    final_jd = state.get("edited_jd") or state.get("jd_draft")
    
    if not final_jd:
        state["status"] = "failed"
        state["error_message"] = "No JD available to publish"
        return state
    
    final_jd_dict = final_jd if isinstance(final_jd, dict) else final_jd.dict()
    
    role_brief = db_ops.get_role_brief_by_thread(thread_id)
    if not role_brief:
        state["status"] = "failed"
        state["error_message"] = "Role brief not found"
        return state
    
    version = state.get("version", 1)
    guardrail = state.get("guardrail_result") or {}
    jd_doc = db_ops.publish_job_description(
        thread_id,
        role_brief["_id"],
        version,
        final_jd_dict,
        guardrail_passed=guardrail.get("passed", True),
        guardrail_issues=guardrail.get("issues", []),
        tone_score=guardrail.get("tone_score", 100.0),
    )
    
    db_ops.insert_sourcing_queue(role_brief["_id"], jd_doc["_id"], thread_id)
    db_ops.update_role_brief_status(thread_id, RoleBriefStatus.PUBLISHED)
    
    state["status"] = "published"
    return state
