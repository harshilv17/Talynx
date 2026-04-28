def get_demo_candidates(jd: dict) -> list[dict]:
    """Return a robust list of demo candidates to fallback to."""
    must_haves = jd.get("must_have_skills", ["Python", "React", "Nodejs"])
    
    return [
        {
            "name": "Alex Mercer",
            "skills": must_haves + ["Docker", "Kubernetes", "AWS"],
            "experience": 8,
            "resume_text": f"Senior Full Stack Engineer with 8 years of experience. Expert in {', '.join(must_haves)}. Led migration to microservices on AWS using Docker and Kubernetes. Strong background in scalable system design and performance optimization.",
            "source": "demo"
        },
        {
            "name": "Sarah Chen",
            "skills": must_haves + ["TypeScript", "GraphQL", "PostgreSQL"],
            "experience": 5,
            "resume_text": f"Software Developer specialized in web technologies. 5 years working with {', '.join(must_haves)} and modern frontend frameworks. Built highly responsive UIs and robust REST APIs.",
            "source": "demo"
        },
        {
            "name": "James Wilson",
            "skills": must_haves[:2] + ["Java", "Spring Boot"],  # Might miss some skills intentionally
            "experience": 4,
            "resume_text": f"Backend Engineer transitioning to full stack. Proficient in {', '.join(must_haves[:2])} and Java Spring Boot. 4 years of experience building scalable enterprise software.",
            "source": "demo"
        },
        {
            "name": "Elena Rodriguez",
            "skills": must_haves + ["MongoDB", "Express", "TailwindCSS"],
            "experience": 6,
            "resume_text": f"Experienced full-stack developer (6 years). Solid background using {', '.join(must_haves)}. Passionate about clean code, agile methodologies, and mentorship.",
            "source": "demo"
        },
        {
            "name": "David Kim",
            "skills": must_haves + ["Python", "Machine Learning", "Data Engineering"],
            "experience": 7,
            "resume_text": f"Data-focused Software Engineer with 7 years experience. Built complex data pipelines and integrated machine learning models into production systems using {', '.join(must_haves)}.",
            "source": "demo"
        },
        {
            "name": "Michael Chang",
            "skills": ["JavaScript", "HTML", "CSS"], # Will definitely be rejected
            "experience": 1,
            "resume_text": "Junior frontend developer with 1 year of experience building basic web apps with vanilla JavaScript and CSS.",
            "source": "demo"
        }
    ]
