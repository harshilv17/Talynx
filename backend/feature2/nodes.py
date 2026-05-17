"""LangGraph nodes for Feature 2: Sourcing & Screening."""
import numpy as np
from core.embedder import embed_texts, cosine_similarity_matrix, calibrate_score
from feature2.state import Feature2State
from feature2 import db_ops
from feature1.db_ops import get_role_brief_by_thread
from feature2.mock_candidates import MOCK_CANDIDATES
from feature1.models import SourcingQueueStatus
from feature2.sourcing import fetch_github_candidates
from feature4.evaluation import evaluate_candidate
from feature4.decision import generate_decision
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
logger = logging.getLogger(__name__)






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
    logger.info("[Feature2] fetch_jd_node STARTED")
    t_start = time.time()
    thread_id = state.get("thread_id")
    
    if not thread_id:
        err = "Missing thread_id in state"
        logger.error(f"[Feature2] {err}")
        state["status"] = "failed"
        state["error_message"] = err
        return state

    db_ops.update_sourcing_progress(thread_id, "in_progress", "loading_job", 15, "Loading and parsing job description...")

    def _do_work():
        jd_doc = db_ops.get_published_jd(thread_id)
        role_brief = get_role_brief_by_thread(thread_id)
        return jd_doc, role_brief

    try:
        logger.info(f"[Feature2] {thread_id} fetching DB docs...")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_work)
            jd_doc, role_brief = future.result(timeout=30)
            
        logger.info(f"[Feature2] {thread_id} DB fetch took {time.time()-t_start:.2f}s")
        
        if not jd_doc:
            raise ValueError("No published JD found for this thread")
        if not role_brief:
            raise ValueError("No role brief found for this thread")

        state["jd_content"] = jd_doc["jd_content"]
        state["role_brief"] = role_brief
        state["status"] = "in_progress"
        return state
        
    except TimeoutError:
        err = "Database fetch timed out after 30s"
        logger.error(f"[Feature2] fetch_jd_node TIMEOUT: {err}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "loading_job", 15, "Failed.", error_message=err)
        return state
    except Exception as e:
        err = f"fetch_jd_node crashed: {str(e)}"
        logger.error(f"[Feature2] fetch_jd_node EXCEPTION:\n{traceback.format_exc()}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "loading_job", 15, "Failed.", error_message=err)
        return state


def fetch_candidates_node(state: Feature2State) -> Feature2State:
    logger.info("[Feature2] fetch_candidates_node STARTED")
    t_start = time.time()
    thread_id = state.get("thread_id")
    if state.get("status") == "failed":
        return state

    db_ops.update_sourcing_progress(thread_id, "in_progress", "loading_candidates", 35, "Scanning profiles and scraping candidates...")

    def _do_work():
        role_brief = state.get("role_brief", {})
        from feature2.mock_candidates import get_demo_candidates
        logger.info(f"[Feature2] Loading demo candidates...")
        demo_cands = get_demo_candidates(role_brief)
        
        cands = []
        try:
            logger.info(f"[Feature2] Fetching live GitHub candidates...")
            cands = fetch_github_candidates(role_brief)
            if not cands:
                logger.warning("[Feature2] GitHub sourcing returned no candidates.")
        except Exception as api_e:
            logger.warning(f"[Feature2] Error fetching GitHub candidates: {api_e}")
            
        cands.extend(demo_cands)
        
        # Deduplication by candidate name
        unique = {}
        for c in cands:
            key = c["name"].lower().strip()
            if key not in unique:
                unique[key] = c
                
        cands = list(unique.values())
        import random
        random.shuffle(cands)
        return cands

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_work)
            candidates = future.result(timeout=45) # Give 45s for external APIs
            
        logger.info(f"[Feature2] {thread_id} Candidate fetch took {time.time()-t_start:.2f}s")
        state["candidates"] = candidates
        return state
        
    except TimeoutError:
        err = "Candidate loading timed out after 45s"
        logger.error(f"[Feature2] fetch_candidates_node TIMEOUT: {err}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "loading_candidates", 35, "Failed.", error_message=err)
        return state
    except Exception as e:
        err = f"fetch_candidates_node crashed: {str(e)}"
        logger.error(f"[Feature2] fetch_candidates_node EXCEPTION:\n{traceback.format_exc()}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "loading_candidates", 35, "Failed.", error_message=err)
        return state


def embedding_node(state: Feature2State) -> Feature2State:
    logger.info("[Feature2] embedding_node STARTED")
    t_start = time.time()
    thread_id = state.get("thread_id")
    if state.get("status") == "failed":
        return state

    db_ops.update_sourcing_progress(thread_id, "in_progress", "generating_embeddings", 60, "Generating multi-dimensional semantic vectors via HuggingFace...")

    if not state.get("jd_content") or not state.get("candidates"):
        err = "Missing JD content or candidates for embedding"
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "generating_embeddings", 60, "Failed.", error_message=err)
        return state

    def _do_work():
        logger.info(f"[Feature2] Sending {len(state['candidates']) + 1} texts to HuggingFace...")
        jd_text = _jd_to_text(state["jd_content"])
        candidate_texts = [c["resume_text"] for c in state["candidates"]]
        all_texts = [jd_text] + candidate_texts
        return embed_texts(all_texts)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_work)
            all_embeddings = future.result(timeout=60) # 60s timeout for ML model wake up
            
        logger.info(f"[Feature2] {thread_id} Embeddings took {time.time()-t_start:.2f}s")
        state["jd_embedding"] = all_embeddings[0].tolist()
        state["candidate_embeddings"] = [e.tolist() for e in all_embeddings[1:]]
        return state
        
    except TimeoutError:
        err = "HuggingFace API timed out after 60s"
        logger.error(f"[Feature2] embedding_node TIMEOUT: {err}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "generating_embeddings", 60, "Failed.", error_message=err)
        return state
    except Exception as e:
        err = f"embedding_node crashed: {str(e)}"
        logger.error(f"[Feature2] embedding_node EXCEPTION:\n{traceback.format_exc()}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "generating_embeddings", 60, "Failed.", error_message=err)
        return state


def ranking_node(state: Feature2State) -> Feature2State:
    logger.info("[Feature2] ranking_node STARTED")
    t_start = time.time()
    thread_id = state.get("thread_id")
    if state.get("status") == "failed":
        return state

    db_ops.update_sourcing_progress(thread_id, "in_progress", "ranking_candidates", 85, "Executing cosine similarity matrix and ranking algorithms...")

    def _do_work():
        jd_embedding = np.array(state["jd_embedding"])
        candidates = state["candidates"]
        candidate_embeddings = np.array(state["candidate_embeddings"])
        raw_scores = cosine_similarity_matrix(jd_embedding, candidate_embeddings)

        ranked = []
        for i, cand in enumerate(candidates):
            calibrated = calibrate_score(float(raw_scores[i]))
            ranked.append({
                "name": cand["name"],
                "skills": cand["skills"],
                "experience": cand["experience"],
                "resume_text": cand["resume_text"],
                "score": calibrated,
                "source": cand.get("source", "github"),
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_work)
            ranked = future.result(timeout=20)
            
        logger.info(f"[Feature2] {thread_id} Ranking took {time.time()-t_start:.2f}s")
        state["ranked_candidates"] = ranked
        return state
        
    except TimeoutError:
        err = "Ranking computation timed out after 20s"
        logger.error(f"[Feature2] ranking_node TIMEOUT: {err}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "ranking_candidates", 85, "Failed.", error_message=err)
        return state
    except Exception as e:
        err = f"ranking_node crashed: {str(e)}"
        logger.error(f"[Feature2] ranking_node EXCEPTION:\n{traceback.format_exc()}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "ranking_candidates", 85, "Failed.", error_message=err)
        return state


def shortlist_node(state: Feature2State) -> Feature2State:
    logger.info("[Feature2] shortlist_node STARTED")
    t_start = time.time()
    thread_id = state.get("thread_id")
    if state.get("status") == "failed":
        return state

    db_ops.update_sourcing_progress(thread_id, "in_progress", "shortlisting", 95, "Running rule-based screening and evaluation agents...")

    def _do_work():
        role_brief = state["role_brief"]
        candidate_docs = []
        
        for cand in state["ranked_candidates"]:
            status, reason = screen_candidate(cand, role_brief)
            evaluation = evaluate_candidate(cand, role_brief)
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
                "source": cand.get("source", "github"),
            })
        
        db_ops.insert_sourcing_candidates(candidate_docs)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_work)
            future.result(timeout=180) # 3 min for multiple AI evaluations
            
        logger.info(f"[Feature2] {thread_id} Final eval took {time.time()-t_start:.2f}s")
        db_ops.update_sourcing_progress(thread_id, "completed", "completed", 100, "Pipeline finished successfully.")
        state["shortlisted"] = []
        state["status"] = "completed"
        return state
        
    except TimeoutError:
        err = "Final evaluation agents timed out after 3m"
        logger.error(f"[Feature2] shortlist_node TIMEOUT: {err}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "shortlisting", 95, "Failed.", error_message=err)
        return state
    except Exception as e:
        err = f"shortlist_node crashed: {str(e)}"
        logger.error(f"[Feature2] shortlist_node EXCEPTION:\n{traceback.format_exc()}")
        state["status"] = "failed"
        state["error_message"] = err
        db_ops.update_sourcing_progress(thread_id, "failed", "shortlisting", 95, "Failed.", error_message=err)
        return state
