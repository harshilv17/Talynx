"""Shared sentence-transformers embedding service.

Used by:
  - Feature 2: semantic candidate-JD matching (replaces TF-IDF)
  - Feature 4: RAG retrieval for rejection feedback

Model: all-MiniLM-L6-v2 (384-dim, ~80MB, no GPU needed)
"""
import os
import logging
import numpy as np
import httpx

logger = logging.getLogger(__name__)

# Hugging Face serverless inference API endpoint
_HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{_HF_MODEL}"


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Encode a list of texts into dense 384-dimensional embeddings 
    using the serverless Hugging Face Inference API.
    
    This keeps the Render deployment extremely lightweight and 100% free of local ML packages.
    """
    if not texts:
        return np.array([])

    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                _API_URL,
                headers=headers,
                json={"inputs": texts, "options": {"wait_for_model": True}}
            )
            
            if response.status_code != 200:
                logger.error(f"HuggingFace API failed ({response.status_code}): {response.text}")
                response.raise_for_status()
                
            embeddings = response.json()
            
            # Verify shape/format
            if not isinstance(embeddings, list):
                raise ValueError(f"Unexpected response format: {embeddings}")
                
            return np.array(embeddings)
            
    except Exception as e:
        logger.error(f"Failed to generate embeddings via HuggingFace API: {e}")
        # Fallback to zero-vectors of shape (len(texts), 384) to prevent dashboard/sourcing crash
        logger.warning("Falling back to zero-vectors to prevent backend pipeline crashes.")
        return np.zeros((len(texts), 384))


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
