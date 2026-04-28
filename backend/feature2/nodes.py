"""LangGraph nodes for Feature 2: Sourcing & Screening."""
import numpy as np
from sentence_transformers import SentenceTransformer
from feature2.state import Feature2State
from feature2 import db_ops
from feature1.db_ops import get_role_brief_by_thread
from feature2.mock_candidates import MOCK_CANDIDATES
from feature1.models import SourcingQueueStatus
from feature2.sourcing import fetch_github_candidates
from feature4.evaluation import evaluate_candidate
from feature4.decision import generate_decision
import logging
logger = logging.getLogger(__name__)


_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot = np.dot(a_arr, b_arr)
    norm = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if norm == 0:
        return 0.0
    return float(dot / norm)


def _jd_to_text(jd: dict) -> str:
    parts = [
        jd.get("job_title", ""),
        jd.get("tagline", ""),
        jd.get("about_role", ""),
        " ".join(jd.get("responsibilities") or []),
        " ".join(jd.get("requirements") or []),
        " ".join(jd.get("nice_to_haves") or []),
    ]
    return " ".join(p for p in parts if p)


def _get_embeddings(texts: list[str]) -> list[list[float]]:
    return _embedding_model.encode(texts).tolist()


def _normalize_skill(skill: str) -> str:
    """Normalize a skill string by lowercasing, stripping, and applying aliases."""
    s = skill.lower().strip()
    aliases = {
        "node": "nodejs",
        "node.js": "nodejs",
        "react": "reactjs",
        "react.js": "reactjs",
        "js": "javascript",
        "ts": "typescript"
    }
    return aliases.get(s, s)

def screen_candidate(candidate: dict, role_brief: dict) -> tuple[str, str | None]:
    """Screen candidate against JD requirements. Returns (status, rejection_reason)."""
    # 1. Experience check
    required_exp = role_brief.get("years_of_experience") or 0
    candidate_exp = candidate.get("experience") or 0
    
    if candidate_exp < required_exp:
        return "rejected", f"Experience ({candidate_exp} yrs) is less than required ({required_exp} yrs)"

    # 2. Must-have skills check
    must_haves = {_normalize_skill(s) for s in role_brief.get("must_have_skills", [])}
    cand_skills = {_normalize_skill(s) for s in candidate.get("skills", [])}
    
    # We allow partial match if normalized skill is contained within candidate skill, e.g. "python" in "python3"
    missing = []
    for mh in must_haves:
        if not any(mh in cs or cs in mh for cs in cand_skills):
            missing.append(mh)
    
    if missing:
        return "rejected", f"Missing must-have skills: {', '.join(missing)}"
        
    return "pending", None


def fetch_jd_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Fetching JD...")
    thread_id = state["thread_id"]

    jd_doc = db_ops.get_published_jd(thread_id)
    if not jd_doc:
        state["status"] = "failed"
        state["error_message"] = "No published JD found for this thread"
        return state
        
    role_brief = get_role_brief_by_thread(thread_id)
    if not role_brief:
        state["status"] = "failed"
        state["error_message"] = "No role brief found for this thread"
        return state

    state["jd_content"] = jd_doc["jd_content"]
    state["role_brief"] = role_brief
    state["status"] = "in_progress"

    db_ops.update_sourcing_queue_status(thread_id, SourcingQueueStatus.IN_PROGRESS)
    return state


def fetch_candidates_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Loading candidates...")
    if state.get("status") == "failed":
        return state

    role_brief = state.get("role_brief", {})
    try:
        candidates = fetch_github_candidates(role_brief)
        if not candidates or len(candidates) < 5:
            from feature2.demo_candidates import get_demo_candidates
            logger.warning("[Feature2] GitHub sourcing returned < 5 candidates. Falling back to demo data.")
            candidates = get_demo_candidates(role_brief)
    except Exception as e:
        from feature2.demo_candidates import get_demo_candidates
        logger.warning(f"[Feature2] Error fetching GitHub candidates: {e}. Falling back to demo data.")
        candidates = get_demo_candidates(role_brief)

    state["candidates"] = candidates
    return state


def embedding_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Generating embeddings...")
    if state.get("status") == "failed":
        return state

    if not state.get("jd_content"):
        state["status"] = "failed"
        state["error_message"] = "No JD content available for embedding"
        return state

    if not state.get("candidates"):
        state["status"] = "failed"
        state["error_message"] = "No candidates available for embedding"
        return state

    try:
        jd_text = _jd_to_text(state["jd_content"])

        candidate_texts = [c["resume_text"] for c in state["candidates"]]

        all_texts = [jd_text] + candidate_texts
        all_embeddings = _get_embeddings(all_texts)

        state["jd_embedding"] = all_embeddings[0]
        state["candidate_embeddings"] = all_embeddings[1:]
        return state

    except Exception as e:
        state["status"] = "failed"
        state["error_message"] = f"Embedding generation failed: {str(e)}"
        return state


def ranking_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Ranking candidates...")
    if state.get("status") == "failed":
        return state

    jd_embedding = state["jd_embedding"]
    candidates = state["candidates"]
    candidate_embeddings = state["candidate_embeddings"]

    ranked = []
    for i, cand in enumerate(candidates):
        score = _cosine_similarity(jd_embedding, candidate_embeddings[i])
        ranked.append({
            "name": cand["name"],
            "skills": cand["skills"],
            "experience": cand["experience"],
            "resume_text": cand["resume_text"],
            "score": round(score * 100, 2),
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    state["ranked_candidates"] = ranked
    return state


def shortlist_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Creating shortlist...")
    if state.get("status") == "failed":
        return state

    thread_id = state["thread_id"]
    role_brief = state["role_brief"]

    candidate_docs = []
    
    for cand in state["ranked_candidates"]:
        status, reason = screen_candidate(cand, role_brief)

        # Phase 1 – Evaluation Scorecard (feature4)
        evaluation = evaluate_candidate(cand, role_brief)

        # Phase 2 – Hire / No-Hire Decision Engine (feature4)
        decision = generate_decision({
            "status": status,
            "evaluation": evaluation,
        })

        candidate_docs.append({
            "job_id": thread_id,
            "name": cand["name"],
            "skills": cand["skills"],
            "experience": cand["experience"],
            "resume_text": cand["resume_text"],
            "score": cand["score"],
            "status": status,
            "rejection_reason": reason,
            "evaluation": evaluation,
            "decision": decision,
        })

    # Insert individual candidates into sourcing_candidates
    db_ops.insert_sourcing_candidates(candidate_docs)
    
    db_ops.update_sourcing_queue_status(thread_id, SourcingQueueStatus.COMPLETED)

    # We don't need 'shortlisted' array anymore in state, but keeping for compatibility if needed.
    # We will just fetch from API.
    state["shortlisted"] = []
    state["status"] = "completed"
    return state
