"""Shared sentence-transformers embedding service.

Used by:
  - Feature 2: semantic candidate-JD matching (replaces TF-IDF)
  - Feature 4: RAG retrieval for rejection feedback

Model: all-MiniLM-L6-v2 (384-dim, ~80MB, no GPU needed)
"""
import logging
import numpy as np
from functools import lru_cache

logger = logging.getLogger(__name__)

_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def _get_model():
    """Lazy-load the sentence-transformer model (singleton)."""
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model: %s", _MODEL_NAME)
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("Model loaded successfully (dim=%d)", _model.get_sentence_embedding_dimension())
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Encode a list of texts into dense embeddings.

    Returns
    -------
    np.ndarray of shape (len(texts), 384)
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embeddings)


def embed_single(text: str) -> np.ndarray:
    """Encode a single text into a 384-dim embedding vector."""
    return embed_texts([text])[0]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors (already L2-normalized)."""
    return float(np.dot(a, b))


def cosine_similarity_matrix(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarities between a query vector and a corpus matrix.

    Parameters
    ----------
    query : np.ndarray of shape (384,)
    corpus : np.ndarray of shape (N, 384)

    Returns
    -------
    np.ndarray of shape (N,) — similarity scores in [-1, 1]
    """
    return np.dot(corpus, query)


def calibrate_score(raw_similarity: float) -> float:
    """
    Calibrate raw cosine similarity [0, 1] to a realistic ATS match
    percentage that feels natural to recruiters.

    Strategy: sigmoid-like mapping that spreads the typical 0.3-0.8
    similarity range into a 30-95% display range.
    """
    # Shift and scale: map [0.2, 0.85] → [20, 98]
    # Using a piecewise linear approach for interpretability
    if raw_similarity <= 0.15:
        return round(max(5.0, raw_similarity * 100), 1)
    elif raw_similarity <= 0.35:
        # Low match: 15-40%
        return round(15 + (raw_similarity - 0.15) * 125, 1)
    elif raw_similarity <= 0.55:
        # Medium match: 40-65%
        return round(40 + (raw_similarity - 0.35) * 125, 1)
    elif raw_similarity <= 0.75:
        # Good match: 65-85%
        return round(65 + (raw_similarity - 0.55) * 100, 1)
    else:
        # Excellent match: 85-98%
        return round(min(98.0, 85 + (raw_similarity - 0.75) * 52), 1)
