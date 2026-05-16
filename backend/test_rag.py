import os
import json
import logging
from pprint import pprint

# Ensure we're in the right directory and path is set for imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feature4.feedback.generator import generate_rejection_feedback
from feature4.feedback.retriever import retrieve_relevant_chunks

logging.basicConfig(level=logging.INFO)

def test_rag_grounding():
    print("=" * 80)
    print("TESTING RAG GROUNDING & RETRIEVAL")
    print("=" * 80)

    # Fake Candidate with specific inject keywords
    unique_skill = "Quantum Kubernetes Orchestration"
    candidate = {
        "name": "Test Candidate",
        "skills": ["Python", unique_skill],
        "experience": 5,
        "resume_text": f"""
        Experienced software engineer with a strong background in distributed systems.
        I worked at Google for 3 years, building high-throughput microservices.
        I specialized in {unique_skill} and built a custom scheduler that reduced latency by 40%.
        Also I am learning Rust in my free time to improve memory safety in systems programming.
        Before that, I was at a startup where I configured AWS environments, wrote Terraform modules, and managed CI/CD pipelines.
        I am very passionate about backend engineering, automation, and reliability engineering.
        """,
        "rejection_reason": f"Lacks practical experience in standard Kubernetes, despite knowing {unique_skill}.",
        "evaluation": {
            "summary": "Strong theoretical knowledge but missing standard industry tools."
        },
        "notes": "Good culture fit, but technical skills are too niche."
    }

    jd_content = {
        "job_title": "Senior DevOps Engineer",
        "about_role": "We need someone to manage our standard Kubernetes clusters.",
        "responsibilities": ["Manage K8s", "Write Helm charts"],
        "requirements": ["Standard Kubernetes", "Helm"],
    }
    
    role_brief = {
        "must_have_skills": ["Kubernetes", "Helm"]
    }

    # 1. Test Retrieval
    print("\n[1] Testing Semantic Retrieval...")
    jd_text = "Senior DevOps Engineer. We need someone to manage our standard Kubernetes clusters."
    retrieval_result = retrieve_relevant_chunks(
        resume_text=candidate["resume_text"],
        jd_text=jd_text,
        rejection_reason=candidate["rejection_reason"],
        evaluation_summary=candidate["evaluation"]["summary"],
        hr_notes=candidate["notes"],
        top_k=3
    )
    
    chunks = retrieval_result["chunks"]
    print(f"Retrieved {len(chunks)} chunks.")
    found_unique_skill = any(unique_skill in c["text"] for c in chunks)
    print(f"Unique skill '{unique_skill}' found in retrieved chunks? {found_unique_skill}")
    assert found_unique_skill, "Retrieval failed to find the highly relevant unique skill chunk."

    for i, c in enumerate(chunks):
        print(f"  Chunk {i+1} [score={c['relevance_score']:.3f}]: {c['text'].strip()}")

    # 2. Test Full Generation
    print("\n[2] Testing Full Generation (LLM)...")
    feedback = generate_rejection_feedback(candidate, jd_content, role_brief, version=1)
    
    print("\nGenerated Feedback Summary:")
    print(feedback.get("overall_summary"))
    
    print("\nSkill Gaps:")
    for gap in feedback.get("skill_gaps", []):
        print(f" - {gap.get('skill')}: {gap.get('recommendation')}")
        
    print("\nStrengths:")
    for s in feedback.get("strengths", []):
        print(f" - {s}")

    # Validate Grounding
    feedback_str = json.dumps(feedback)
    if unique_skill in feedback_str:
        print(f"\n✅ SUCCESS: The unique skill '{unique_skill}' was successfully injected and used by the LLM.")
    else:
        print(f"\n❌ WARNING: The unique skill '{unique_skill}' was NOT found in the final feedback. LLM might have ignored it.")
        
    print("\nMetadata:")
    pprint(feedback.get("rag_metadata"))

if __name__ == "__main__":
    test_rag_grounding()
