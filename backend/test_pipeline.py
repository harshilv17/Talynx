from feature2.router import run_sourcing_background

def test():
    print("Testing pipeline initialization...")
    try:
        run_sourcing_background("test_thread", {
            "thread_id": "test_thread",
            "role_brief": None,
            "jd_content": None,
            "candidates": None,
            "jd_embedding": None,
            "candidate_embeddings": None,
            "ranked_candidates": None,
            "shortlisted": None,
            "status": "in_progress",
            "error_message": None,
        })
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
