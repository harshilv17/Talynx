#!/usr/bin/env python3
"""
system_test.py — Full end-to-end pipeline test for Feature 4.

What this does
--------------
1. Connects directly to MongoDB and seeds:
   • A test job description + role brief
   • Three candidates already in INTERVIEWED status
     (covering hire_high / hire_moderate / no_hire bands)
2. POSTs to  POST /api/v1/candidates/process  (the automation endpoint)
3. Validates results against expected outcomes
4. Cleans up all seeded test documents

Usage
-----
  # With server already running:
  python3 system_test.py

  # Keep test data in DB for inspection:
  python3 system_test.py --no-cleanup

Candidate design
----------------
Weights: technical 30% + experience 20% + skill_match 20% + interview 30%
JD requires 4 yrs exp, must-have skills: [Python, FastAPI, Machine Learning]
Min salary ₹12 LPA  Max salary ₹24 LPA

  Alice  score=85  exp=5  skills=all  interview=82  → overall≈83  hire_high
  Bob    score=62  exp=2  skills=2/3  interview=55  → overall≈57  hire_moderate
  Carol  score=28  exp=0.5 skills=0/3 interview=20 → overall≈24  no_hire
"""

import sys
import os
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# ─── Load .env so MONGO_URI is available ──────────────────────────────────────
for _p in [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(_p)
        break

from pymongo import MongoClient
from bson import ObjectId

# ─── Config ───────────────────────────────────────────────────────────────────
MONGO_URI   = os.getenv("MONGO_URI", "")
BASE_URL    = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API         = f"{BASE_URL}/api/v1"
TEST_JOB_ID = "system-test-feature4-v1"

if not MONGO_URI:
    print("ERROR: MONGO_URI not set — check your .env file")
    sys.exit(1)

# ─── Colours ──────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}✓{RESET}  {msg}")
def fail(msg): print(f"  {RED}✗{RESET}  {msg}")
def info(msg): print(f"  {CYAN}→{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}!{RESET}  {msg}")
def head(msg): print(f"\n{BOLD}{msg}{RESET}")


# ─── Test data ────────────────────────────────────────────────────────────────
TEST_JD_DOC = {
    "thread_id": TEST_JOB_ID,
    "status":    "PUBLISHED",
    "version":   1,
    "jd_content": {
        "job_title":     "Senior AI Engineer",
        "company_blurb": "Talynx AI builds autonomous hiring pipelines powered by LLMs.",
        "about_role":    "Design and ship production-grade ML systems end-to-end.",
        "requirements":  ["5+ years Python", "FastAPI expertise", "ML/AI background"],
        "min_salary":    1_200_000,   # ₹12 LPA
        "max_salary":    2_400_000,   # ₹24 LPA
    },
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

TEST_ROLE_BRIEF_DOC = {
    "thread_id":          TEST_JOB_ID,
    "status":             "PUBLISHED",
    "years_of_experience": 4,
    "must_have_skills":   ["Python", "FastAPI", "Machine Learning"],
    "created_at":         datetime.utcnow(),
    "updated_at":         datetime.utcnow(),
}

# Three candidates in INTERVIEWED status covering all three decision tiers
TEST_CANDIDATES = [
    {
        "job_id":          TEST_JOB_ID,
        "name":            "Alice Chen",
        "skills":          ["Python", "FastAPI", "Machine Learning", "PostgreSQL", "Docker"],
        "experience":      5.0,
        "score":           85.0,    # technical score proxy
        "interview_score": 82.0,
        "status":          "interviewed",
        "outreach":        {"email_address": "alice.chen@example.com", "status": "sent"},
        "expected_tier":   "hire_high",
        "created_at":      datetime.utcnow(),
        "updated_at":      datetime.utcnow(),
    },
    {
        "job_id":          TEST_JOB_ID,
        "name":            "Bob Sharma",
        "skills":          ["Python", "Django"],
        "experience":      2.0,
        "score":           62.0,
        "interview_score": 55.0,
        "status":          "interviewed",
        "outreach":        {"email_address": "bob.sharma@example.com", "status": "sent"},
        "expected_tier":   "hire_moderate",
        "created_at":      datetime.utcnow(),
        "updated_at":      datetime.utcnow(),
    },
    {
        "job_id":          TEST_JOB_ID,
        "name":            "Carol Mistry",
        "skills":          ["Java"],
        "experience":      0.5,
        "score":           28.0,
        "interview_score": 20.0,
        "status":          "interviewed",
        "outreach":        {"email_address": "carol.mistry@example.com", "status": "sent"},
        "expected_tier":   "no_hire",
        "created_at":      datetime.utcnow(),
        "updated_at":      datetime.utcnow(),
    },
]


# ─── DB helpers ───────────────────────────────────────────────────────────────

def get_db():
    use_tls = MONGO_URI.startswith("mongodb+srv://")
    kwargs: dict = {"serverSelectionTimeoutMS": 15000}
    if use_tls:
        kwargs["tls"] = True
        kwargs["tlsAllowInvalidCertificates"] = True
    client = MongoClient(MONGO_URI, **kwargs)
    db_name = "talynx" if MONGO_URI.startswith("mongodb+srv://") else "Talynx"
    return client[db_name]


def seed_test_data(db) -> list[str]:
    """Insert test JD, role_brief, and candidates. Returns candidate ID list."""
    # Upsert JD
    db["job_descriptions"].update_one(
        {"thread_id": TEST_JOB_ID},
        {"$set": TEST_JD_DOC},
        upsert=True,
    )
    # Upsert role brief
    db["role_briefs"].update_one(
        {"thread_id": TEST_JOB_ID},
        {"$set": TEST_ROLE_BRIEF_DOC},
        upsert=True,
    )
    # Remove any leftover candidates from a previous run
    db["sourcing_candidates"].delete_many({"job_id": TEST_JOB_ID})
    # Insert fresh candidates
    result = db["sourcing_candidates"].insert_many(
        [{k: v for k, v in c.items() if k != "expected_tier"} for c in TEST_CANDIDATES]
    )
    return [str(oid) for oid in result.inserted_ids]


def cleanup_test_data(db):
    db["job_descriptions"].delete_many({"thread_id": TEST_JOB_ID})
    db["role_briefs"].delete_many({"thread_id": TEST_JOB_ID})
    db["sourcing_candidates"].delete_many({"job_id": TEST_JOB_ID})


def fetch_candidates_from_db(db) -> list[dict]:
    return list(db["sourcing_candidates"].find({"job_id": TEST_JOB_ID}))


# ─── API call helpers ─────────────────────────────────────────────────────────

def call(method: str, path: str, **kwargs):
    url = f"{API}{path}"
    try:
        resp = getattr(requests, method)(url, timeout=30, **kwargs)
        return resp.status_code, resp.json()
    except Exception as exc:
        return None, {"error": str(exc)}


# ─── Test steps ───────────────────────────────────────────────────────────────

def step_health_check() -> bool:
    head("STEP 0 — Health check")
    status, data = call("get", "/../../health")
    # direct call since health is at root
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            ok("Server is healthy")
            return True
        else:
            fail(f"Health returned {r.status_code}")
            return False
    except Exception as exc:
        fail(f"Cannot reach server: {exc}")
        print(f"\n  Start the server first:\n"
              f"  cd backend && uvicorn main:app --reload --port 8000\n")
        return False


def step_seed(db) -> list[str]:
    head("STEP 1 — Seed test data into MongoDB")
    ids = seed_test_data(db)
    ok(f"JD '{TEST_JOB_ID}' upserted")
    ok(f"Role brief upserted (4 yrs req, skills: Python/FastAPI/ML)")
    for i, (cid, c) in enumerate(zip(ids, TEST_CANDIDATES)):
        ok(f"Candidate {i+1}: {c['name']}  score={c['score']}  "
           f"interview={c['interview_score']}  expected={c['expected_tier']}  id={cid}")
    return ids


def step_process(db) -> tuple[bool, dict]:
    head("STEP 2 — POST /api/v1/candidates/process")
    info(f"Triggering automation loop for job_id='{TEST_JOB_ID}'")

    status_code, data = call("post", "/candidates/process",
                             json={"job_id": TEST_JOB_ID})

    if status_code is None:
        fail(f"Request failed: {data.get('error')}")
        return False, {}

    if status_code != 200:
        fail(f"HTTP {status_code}: {data}")
        return False, data

    ok(f"HTTP 200 received")
    info(f"Total processed : {data.get('total_processed')}")
    info(f"Hired           : {len(data.get('hired', []))}")
    info(f"Pending review  : {len(data.get('pending_review', []))}")
    info(f"Rejected        : {len(data.get('rejected', []))}")
    if data.get("errors"):
        warn(f"Errors ({len(data['errors'])}): {json.dumps(data['errors'], indent=4)}")

    return True, data


def step_verify(db, response: dict, candidate_ids: list[str]) -> bool:
    head("STEP 3 — Validate outcomes")

    db_docs = {str(d["_id"]): d for d in fetch_candidates_from_db(db)}
    all_pass = True

    expected_map = {
        c["name"]: c["expected_tier"] for c in TEST_CANDIDATES
    }

    hired_names          = {c["name"] for c in response.get("hired", [])}
    pending_review_names = {c["name"] for c in response.get("pending_review", [])}
    rejected_names       = {c["name"] for c in response.get("rejected", [])}

    for name, expected in expected_map.items():
        doc = next((d for d in db_docs.values() if d.get("name") == name), None)
        if not doc:
            fail(f"{name}: not found in DB after processing")
            all_pass = False
            continue

        actual_status = doc.get("status")
        evaluation    = doc.get("evaluation") or {}
        decision      = doc.get("decision") or {}
        overall       = evaluation.get("overall_score", 0)
        recommendation = decision.get("recommendation", "?")

        line = (
            f"{name:15s}  overall={overall:5.1f}  "
            f"rec={recommendation:15s}  db_status={actual_status}"
        )

        if expected == "hire_high":
            passed = (
                actual_status == "offered"
                and recommendation == "hire_high"
                and name in hired_names
            )
        elif expected == "hire_moderate":
            passed = (
                actual_status == "evaluated"
                and recommendation == "hire_moderate"
                and name in pending_review_names
            )
        else:  # no_hire
            passed = (
                actual_status == "rejected"
                and recommendation == "no_hire"
                and name in rejected_names
            )

        if passed:
            ok(line)
        else:
            fail(line + f"  [expected tier={expected}]")
            all_pass = False

    return all_pass


def step_evaluation_api(job_id: str):
    head("STEP 4 — GET /api/v1/feature4/evaluation/{job_id}")
    status_code, data = call("get", f"/feature4/evaluation/{job_id}")
    if status_code == 200:
        candidates = data.get("candidates", [])
        ok(f"Found {len(candidates)} evaluated candidate(s) in evaluation view")
        for c in candidates:
            ev = c.get("evaluation") or {}
            dc = c.get("decision") or {}
            info(
                f"  {c['name']:15s}  status={c['status']:12s}  "
                f"overall={ev.get('overall_score', 0):5.1f}  "
                f"rec={dc.get('recommendation','?')}"
            )
    else:
        warn(f"Evaluation GET returned HTTP {status_code}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-cleanup", action="store_true",
                        help="Keep test data in DB for manual inspection")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  SYSTEM TEST — Feature 4 Autonomous Pipeline")
    print(f"  Server  : {BASE_URL}")
    print(f"  Job ID  : {TEST_JOB_ID}")
    print(f"{'='*60}")

    # 0. Health check
    if not step_health_check():
        sys.exit(1)

    # Connect to DB
    db = get_db()

    # 1. Seed
    candidate_ids = step_seed(db)
    print()

    # 2. Process
    success, response = step_process(db)
    if not success:
        if not args.no_cleanup:
            cleanup_test_data(db)
        sys.exit(1)
    print()

    # Small pause for any async writes
    time.sleep(0.5)

    # 3. Validate
    all_passed = step_verify(db, response, candidate_ids)
    print()

    # 4. Evaluation view
    step_evaluation_api(TEST_JOB_ID)
    print()

    # Cleanup
    if args.no_cleanup:
        warn(f"--no-cleanup set: test data preserved in DB under job_id='{TEST_JOB_ID}'")
    else:
        cleanup_test_data(db)
        ok("Test data cleaned up from DB")

    print(f"\n{'='*60}")
    if all_passed:
        print(f"  {GREEN}{BOLD}ALL TESTS PASSED{RESET}")
    else:
        print(f"  {RED}{BOLD}SOME TESTS FAILED — see details above{RESET}")
    print(f"{'='*60}\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
