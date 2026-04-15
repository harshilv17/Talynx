"""LangGraph nodes for Feature 2: Sourcing & Screening."""
import numpy as np
from sentence_transformers import SentenceTransformer
from feature2.state import Feature2State
from feature2 import db_ops
from feature2.mock_candidates import MOCK_CANDIDATES
from feature1.models import SourcingQueueStatus


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
        " ".join(jd.get("responsibilities", [])),
        " ".join(jd.get("requirements", [])),
        " ".join(jd.get("nice_to_haves", [])),
    ]
    return " ".join(p for p in parts if p)


def _get_embeddings(texts: list[str]) -> list[list[float]]:
    return _embedding_model.encode(texts).tolist()


def fetch_jd_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Fetching JD...")
    thread_id = state["thread_id"]

    jd_doc = db_ops.get_published_jd(thread_id)
    if not jd_doc:
        state["status"] = "failed"
        state["error_message"] = "No published JD found for this thread"
        return state

    state["jd_content"] = jd_doc["jd_content"]
    state["status"] = "in_progress"

    db_ops.update_sourcing_queue_status(thread_id, SourcingQueueStatus.IN_PROGRESS)
    return state


def fetch_candidates_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Loading candidates...")
    if state.get("status") == "failed":
        return state

    state["candidates"] = MOCK_CANDIDATES
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
            "match_score": round(score * 100, 2),
        })

    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    state["ranked_candidates"] = ranked
    return state


def shortlist_node(state: Feature2State) -> Feature2State:
    print("[Feature2] Creating shortlist...")
    if state.get("status") == "failed":
        return state

    thread_id = state["thread_id"]
    top_n = 5

    shortlisted = state["ranked_candidates"][:top_n]
    state["shortlisted"] = shortlisted

    db_ops.insert_shortlisted_candidates(thread_id, shortlisted)
    db_ops.update_sourcing_queue_status(thread_id, SourcingQueueStatus.COMPLETED)

    state["status"] = "completed"
    return state
