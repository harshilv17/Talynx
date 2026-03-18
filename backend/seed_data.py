#!/usr/bin/env python3
"""Seed MongoDB with sample entries for testing."""
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from datetime import datetime, timezone
from feature1.db_ops import (
    create_role_brief,
    insert_job_description,
    insert_sourcing_queue,
    update_role_brief_status,
    get_role_brief_by_thread,
)
from feature1.models import RoleBriefStatus, JDStatus

import uuid


def seed():
    # Sample role brief 1 - Senior Backend Engineer
    thread_id_1 = str(uuid.uuid4())
    rb1 = create_role_brief(thread_id_1, {
        "role_title": "Senior Backend Engineer",
        "team": "Platform",
        "seniority": "senior",
        "work_type": "hybrid",
        "location": "San Francisco, CA",
        "must_have_skills": ["Python", "PostgreSQL", "Redis", "AWS"],
        "nice_to_have_skills": ["Kubernetes", "GraphQL"],
        "salary_min": 150000,
        "salary_max": 200000,
        "currency": "USD",
        "headcount": 1,
        "years_of_experience": 5,
        "reports_to": "Engineering Manager",
        "key_outcomes": ["Scale API to 10M requests/day", "Lead migration to microservices"],
        "context_note": "Fast-growing fintech startup",
        "tone_preference": "conversational",
    })
    update_role_brief_status(thread_id_1, RoleBriefStatus.PUBLISHED)

    jd_content_1 = {
        "job_title": "Senior Backend Engineer",
        "tagline": "Scale our platform and lead our microservices migration",
        "about_role": "Join our Platform team to scale our APIs and lead our microservices migration. We're a fast-growing fintech startup building the future of payments.",
        "responsibilities": [
            "Design and implement high-performance APIs",
            "Lead migration from monolith to microservices",
            "Mentor junior engineers",
        ],
        "requirements": [
            "5+ years Python experience",
            "Strong PostgreSQL and Redis",
            "Experience with AWS",
        ],
        "nice_to_haves": ["Kubernetes", "GraphQL"],
        "company_blurb": "We're a fast-growing fintech startup building the future of payments.",
        "salary_range": "$150,000 - $200,000 USD",
        "location_work_type": "San Francisco, CA · Hybrid",
    }
    jd1 = insert_job_description(thread_id_1, rb1["_id"], {
        "version": 1,
        "status": JDStatus.PUBLISHED,
        "jd_content": jd_content_1,
        "guardrail_passed": 1,
        "guardrail_issues": [],
        "tone_score": 95.0,
        "published_at": datetime.now(timezone.utc),
    })
    insert_sourcing_queue(rb1["_id"], jd1["_id"], thread_id_1)

    # Sample role brief 2 - Frontend Developer
    thread_id_2 = str(uuid.uuid4())
    rb2 = create_role_brief(thread_id_2, {
        "role_title": "Frontend Developer",
        "team": "Product",
        "seniority": "mid",
        "work_type": "remote",
        "location": "Remote (US)",
        "must_have_skills": ["React", "TypeScript", "CSS"],
        "nice_to_have_skills": ["Next.js", "Tailwind"],
        "salary_min": 120000,
        "salary_max": 160000,
        "currency": "USD",
        "headcount": 2,
        "tone_preference": "technical",
    })
    update_role_brief_status(thread_id_2, RoleBriefStatus.PENDING_REVIEW)

    jd_content_2 = {
        "job_title": "Frontend Developer",
        "tagline": "Craft exceptional user experiences with React and TypeScript",
        "about_role": "Help us build beautiful, performant web applications. Collaborate with design to create exceptional user experiences.",
        "responsibilities": [
            "Build responsive UIs with React",
            "Collaborate with design team",
            "Write maintainable TypeScript",
        ],
        "requirements": [
            "3+ years React experience",
            "Strong TypeScript skills",
            "Eye for design",
        ],
        "nice_to_haves": ["Next.js", "Tailwind"],
        "company_blurb": "We build beautiful, performant web applications.",
        "salary_range": "$120,000 - $160,000 USD",
        "location_work_type": "Remote (US)",
    }
    insert_job_description(thread_id_2, rb2["_id"], {
        "version": 1,
        "status": JDStatus.PENDING_REVIEW,
        "jd_content": jd_content_2,
        "guardrail_passed": 1,
        "guardrail_issues": [],
        "tone_score": 92.0,
    })

    # Sample role brief 3 - Data Scientist
    thread_id_3 = str(uuid.uuid4())
    rb3 = create_role_brief(thread_id_3, {
        "role_title": "Data Scientist",
        "team": "ML",
        "seniority": "senior",
        "work_type": "hybrid",
        "location": "New York, NY",
        "must_have_skills": ["Python", "SQL", "Machine Learning", "PyTorch"],
        "nice_to_have_skills": ["LLMs", "MLOps"],
        "salary_min": 160000,
        "salary_max": 220000,
        "currency": "USD",
        "headcount": 1,
        "years_of_experience": 4,
        "tone_preference": "formal",
    })
    update_role_brief_status(thread_id_3, RoleBriefStatus.GENERATING)

    print("Seeded 3 role briefs:")
    print(f"  1. {thread_id_1} - Senior Backend Engineer (PUBLISHED)")
    print(f"  2. {thread_id_2} - Frontend Developer (PENDING_REVIEW)")
    print(f"  3. {thread_id_3} - Data Scientist (GENERATING)")
    print("\nYou can fetch published JD at: GET /api/v1/feature1/published/{thread_id_1}")


if __name__ == "__main__":
    seed()
