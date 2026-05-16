"""Top-K retrieval over resume chunks using semantic similarity.

Retrieves the most relevant resume chunks given a query built from
the JD requirements, evaluation summary, and rejection reason.
"""
import logging
import numpy as np
from core.embedder import embed_texts, embed_single, cosine_similarity_matrix
from feature4.feedback.chunker import semantic_chunk

logger = logging.getLogger(__name__)


def _build_retrieval_query(
    jd_text: str,
    rejection_reason: str | None = None,
    evaluation_summary: str | None = None,
    hr_notes: str | None = None,
) -> str:
    """
    Construct a composite retrieval query from all available context.

    The query is optimized to retrieve resume sections most relevant
    to the candidate's gaps and the job requirements.
    """
    parts = [
        f"Job requirements: {jd_text}",
    ]
    if rejection_reason:
        parts.append(f"Rejection reason: {rejection_reason}")
    if evaluation_summary:
        parts.append(f"Evaluation: {evaluation_summary}")
    if hr_notes:
        parts.append(f"HR notes: {hr_notes}")

    return " ".join(parts)


def retrieve_relevant_chunks(
    resume_text: str,
    jd_text: str,
    rejection_reason: str | None = None,
    evaluation_summary: str | None = None,
    hr_notes: str | None = None,
    top_k: int = 5,
) -> dict:
    """
    Chunk the resume, embed chunks, and retrieve top-K most relevant.

    Returns
    -------
    dict with keys:
        chunks: list[dict]   — top-K chunks with text + score
        query: str            — the composite query used
        total_chunks: int     — total chunks before filtering
        retrieval_scores: list[float] — similarity scores of returned chunks
    """
    # 1. Chunk the resume
    chunks = semantic_chunk(resume_text)
    if not chunks:
        logger.warning("No chunks produced from resume text")
        return {
            "chunks": [],
            "query": "",
            "total_chunks": 0,
            "retrieval_scores": [],
        }

    # 2. Build retrieval query
    query = _build_retrieval_query(jd_text, rejection_reason, evaluation_summary, hr_notes)

    # 3. Embed everything
    chunk_texts = [c["text"] for c in chunks]
    chunk_embeddings = embed_texts(chunk_texts)
    query_embedding = embed_single(query)

    # 4. Compute similarities
    scores = cosine_similarity_matrix(query_embedding, chunk_embeddings)

    # 5. Rank and select top-K
    top_indices = np.argsort(scores)[::-1][:top_k]

    retrieved = []
    retrieval_scores = []
    for idx in top_indices:
        chunk = chunks[idx].copy()
        chunk["relevance_score"] = round(float(scores[idx]), 4)
        retrieved.append(chunk)
        retrieval_scores.append(round(float(scores[idx]), 4))

    logger.info(
        "Retrieved %d/%d chunks (scores: %s)",
        len(retrieved), len(chunks),
        [f"{s:.3f}" for s in retrieval_scores],
    )

    return {
        "chunks": retrieved,
        "query": query,
        "total_chunks": len(chunks),
        "retrieval_scores": retrieval_scores,
    }
