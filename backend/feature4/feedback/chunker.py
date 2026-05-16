"""Semantic text chunker for resume documents.

Splits resume text into semantically meaningful chunks using sentence
boundaries with configurable size and overlap. Designed for resumes that
already exist as plain text (not PDF extraction).
"""
import re
import logging

logger = logging.getLogger(__name__)

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_CHUNK_SIZE = 400      # target tokens per chunk (approx chars / 4)
DEFAULT_CHUNK_OVERLAP = 80    # overlap tokens between consecutive chunks
DEFAULT_MIN_CHUNK_SIZE = 50   # discard chunks smaller than this


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex heuristics."""
    # Split on period/newline boundaries but keep abbreviations intact
    sentences = re.split(r'(?<=[.!?])\s+|\n{1,}', text)
    return [s.strip() for s in sentences if s.strip()]


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    return max(1, len(text) // 4)


def semantic_chunk(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE,
) -> list[dict]:
    """
    Split resume text into semantically meaningful chunks.

    Each chunk dict contains:
        - text: str          — the chunk content
        - index: int         — 0-based chunk position
        - token_estimate: int — approximate token count
        - char_start: int    — character offset in original text
        - char_end: int      — character end offset

    Parameters
    ----------
    text : str
        Raw resume text.
    chunk_size : int
        Target tokens per chunk.
    chunk_overlap : int
        Overlap tokens between consecutive chunks.
    min_chunk_size : int
        Discard chunks with fewer tokens than this.
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return [{"text": text.strip(), "index": 0,
                 "token_estimate": _estimate_tokens(text),
                 "char_start": 0, "char_end": len(text)}]

    chunks: list[dict] = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sent_tokens = _estimate_tokens(sentence)

        if current_tokens + sent_tokens > chunk_size and current_sentences:
            chunk_text = " ".join(current_sentences)
            chunk_tokens = _estimate_tokens(chunk_text)

            if chunk_tokens >= min_chunk_size:
                char_start = text.find(current_sentences[0])
                char_end = char_start + len(chunk_text) if char_start >= 0 else len(chunk_text)
                chunks.append({
                    "text": chunk_text,
                    "index": len(chunks),
                    "token_estimate": chunk_tokens,
                    "char_start": max(0, char_start),
                    "char_end": char_end,
                })

            # Keep overlap sentences
            overlap_tokens = 0
            overlap_start = len(current_sentences)
            for i in range(len(current_sentences) - 1, -1, -1):
                overlap_tokens += _estimate_tokens(current_sentences[i])
                if overlap_tokens >= chunk_overlap:
                    overlap_start = i
                    break
            current_sentences = current_sentences[overlap_start:]
            current_tokens = sum(_estimate_tokens(s) for s in current_sentences)

        current_sentences.append(sentence)
        current_tokens += sent_tokens

    # Flush remaining
    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunk_tokens = _estimate_tokens(chunk_text)
        if chunk_tokens >= min_chunk_size:
            char_start = text.find(current_sentences[0])
            char_end = char_start + len(chunk_text) if char_start >= 0 else len(chunk_text)
            chunks.append({
                "text": chunk_text,
                "index": len(chunks),
                "token_estimate": chunk_tokens,
                "char_start": max(0, char_start),
                "char_end": char_end,
            })

    logger.info("Chunked resume into %d chunks (avg ~%d tokens)",
                len(chunks),
                sum(c["token_estimate"] for c in chunks) // max(1, len(chunks)))
    return chunks
