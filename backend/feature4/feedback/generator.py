"""RAG pipeline orchestrator for rejection feedback generation.

Coordinates: retrieval → prompt assembly → LLM generation → parsing.
Uses Groq (Llama 3.3 70B) for fast, high-quality generation.
"""
import json
import uuid
import logging
from datetime import datetime, timezone

from core.openai_client import get_groq_client
from feature4.feedback.retriever import retrieve_relevant_chunks
from feature4.feedback.prompts import FEEDBACK_SYSTEM_PROMPT, FEEDBACK_USER_PROMPT

logger = logging.getLogger(__name__)

_MODEL = "llama-3.3-70b-versatile"


def _jd_to_text(jd_content: dict, role_brief: dict | None = None) -> str:
    """Flatten JD + role brief into a single text block for retrieval."""
    parts = [
        jd_content.get("job_title", ""),
        jd_content.get("about_role", ""),
        " ".join(jd_content.get("responsibilities") or []),
        " ".join(jd_content.get("requirements") or []),
        " ".join(jd_content.get("nice_to_haves") or []),
    ]
    if role_brief:
        parts.append(f"Must-have skills: {', '.join(role_brief.get('must_have_skills', []))}")
        parts.append(f"Nice-to-have skills: {', '.join(role_brief.get('nice_to_have_skills', []))}")
        yoe = role_brief.get("years_of_experience")
        if yoe:
            parts.append(f"Required experience: {yoe} years")
    return " ".join(p for p in parts if p)


def _parse_llm_response(content: str) -> dict:
    """Extract JSON from LLM response, handling markdown code fences."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last lines (code fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        content = "\n".join(lines)
    return json.loads(content)


def generate_rejection_feedback(
    candidate: dict,
    jd_content: dict,
    role_brief: dict | None = None,
    version: int = 1,
) -> dict:
    """
    Full RAG pipeline: retrieve relevant resume chunks → generate grounded feedback.

    Parameters
    ----------
    candidate : dict
        Must contain: name, skills, experience, resume_text, rejection_reason,
        and optionally evaluation.summary and notes.
    jd_content : dict
        The job description content dict.
    role_brief : dict | None
        The role brief with must_have_skills, years_of_experience, etc.
    version : int
        Feedback version number (incremented on regeneration).

    Returns
    -------
    dict — complete feedback document ready for MongoDB storage.
    """
    # ── 1. Gather candidate context ───────────────────────────────────────
    resume_text = candidate.get("resume_text", "")
    rejection_reason = candidate.get("rejection_reason", "Not specified")
    evaluation = candidate.get("evaluation") or {}
    evaluation_summary = evaluation.get("summary", "No evaluation summary available")
    hr_notes = candidate.get("notes", "No HR notes")
    candidate_name = candidate.get("name", "Candidate")
    candidate_skills = ", ".join(candidate.get("skills", []))
    candidate_experience = candidate.get("experience", 0)

    # ── 2. Build JD text ──────────────────────────────────────────────────
    jd_text = _jd_to_text(jd_content, role_brief)

    # ── 3. RAG Retrieval ──────────────────────────────────────────────────
    import time
    start_retrieval = time.time()
    retrieval_result = retrieve_relevant_chunks(
        resume_text=resume_text,
        jd_text=jd_text,
        rejection_reason=rejection_reason,
        evaluation_summary=evaluation_summary,
        hr_notes=hr_notes,
        top_k=5,
    )
    retrieval_time = time.time() - start_retrieval

    retrieved_chunks = retrieval_result["chunks"]
    chunks_text = "\n\n".join(
        f"[Chunk {i+1} | relevance={c['relevance_score']:.3f}]\n{c['text']}"
        for i, c in enumerate(retrieved_chunks)
    ) or "No resume chunks available."

    logger.info(f"Retrieval complete in {retrieval_time:.3f}s. Retrieved {len(retrieved_chunks)} chunks.")

    # ── 4. Assemble prompt ────────────────────────────────────────────────
    user_prompt = FEEDBACK_USER_PROMPT.format(
        jd_text=jd_text,
        rejection_reason=rejection_reason,
        evaluation_summary=evaluation_summary,
        hr_notes=hr_notes or "None provided",
        retrieved_chunks=chunks_text,
        candidate_name=candidate_name,
        candidate_skills=candidate_skills,
        candidate_experience=candidate_experience,
    )

    logger.debug(f"LLM Prompt length: {len(user_prompt)} characters.")

    # ── 5. LLM Generation ────────────────────────────────────────────────
    client = get_groq_client()
    start_gen = time.time()
    try:
        response = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": FEEDBACK_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        gen_time = time.time() - start_gen
        logger.info(f"LLM Generation complete in {gen_time:.3f}s.")
        
        raw_content = response.choices[0].message.content
        logger.debug(f"LLM Raw Output: {raw_content[:200]}...")
        feedback_data = _parse_llm_response(raw_content)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM JSON response: %s", e)
        feedback_data = _build_fallback_feedback(candidate, rejection_reason)
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        feedback_data = _build_fallback_feedback(candidate, rejection_reason)

    # ── 6. Assemble feedback document ─────────────────────────────────────
    return {
        "feedback_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc),
        "model_used": _MODEL,
        "version": version,
        "strengths": feedback_data.get("strengths", []),
        "skill_gaps": feedback_data.get("skill_gaps", []),
        "experience_gaps": feedback_data.get("experience_gaps", []),
        "improvement_suggestions": feedback_data.get("improvement_suggestions", []),
        "technologies_to_learn": feedback_data.get("technologies_to_learn", []),
        "overall_summary": feedback_data.get("overall_summary", ""),
        "encouragement": feedback_data.get("encouragement", ""),
        "rag_metadata": {
            "chunks_used": len(retrieved_chunks),
            "retrieval_scores": retrieval_result["retrieval_scores"],
            "embedding_model": "all-MiniLM-L6-v2",
            "total_chunks": retrieval_result["total_chunks"],
        },
        "email_sent": False,
        "email_sent_at": None,
    }


def _build_fallback_feedback(candidate: dict, rejection_reason: str) -> dict:
    """Deterministic fallback when LLM generation fails."""
    name = candidate.get("name", "Candidate")
    skills = candidate.get("skills", [])
    return {
        "strengths": [f"Demonstrated proficiency in {s}" for s in skills[:3]],
        "skill_gaps": [],
        "experience_gaps": [rejection_reason] if rejection_reason else [],
        "improvement_suggestions": [
            "Consider expanding your technical skill set in areas aligned with the role requirements",
            "Building portfolio projects can strengthen your candidacy for similar roles",
        ],
        "technologies_to_learn": [],
        "overall_summary": (
            f"Thank you for your interest, {name}. While your background shows "
            f"valuable experience, the role requirements did not fully align with "
            f"your current profile."
        ),
        "encouragement": (
            f"Your skills in {', '.join(skills[:2]) if skills else 'your domain'} "
            f"are valuable assets. We encourage you to continue developing your expertise."
        ),
    }
