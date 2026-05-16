"""
High-quality demo candidates dataset for Talynx.
Contains realistic resumes for AI/ML, Frontend, and Backend engineers.
"""

DEMO_CANDIDATES = [
    {
        "name": "Alex Chen",
        "email": "alex.chen.ai@example.com",
        "github_username": "alexc-ai",
        "type": "demo",
        "skills": ["Python", "PyTorch", "LangChain", "LLMs", "RAG", "FastAPI", "Vector Databases", "Docker"],
        "experience": 5,
        "resume_text": """
Alex Chen
San Francisco, CA | alex.chen.ai@example.com | github.com/alexc-ai

PROFESSIONAL EXPERIENCE
Senior AI Engineer | Vertex Analytics | 2021 - Present
- Designed and deployed an enterprise Retrieval-Augmented Generation (RAG) pipeline using LangChain, Pinecone, and OpenAI APIs, reducing customer support resolution time by 40%.
- Optimized LLM inference latency by 30% through prompt engineering and switching to vLLM on Kubernetes.
- Led a team of 3 engineers to build an internal semantic search tool for legal document analysis, processing over 1M+ PDF documents.

Machine Learning Engineer | DataCore Solutions | 2018 - 2021
- Developed predictive models using PyTorch and Scikit-learn for churn prediction, increasing retention by 15%.
- Built RESTful APIs with FastAPI to serve ML models in production, handling 500+ requests per second.
- Orchestrated ML workflows using Airflow and MLflow for experiment tracking and model registry.

EDUCATION
M.S. Computer Science (Specialization in AI) | Stanford University | 2018
B.S. Computer Science | UC Berkeley | 2016

PROJECTS
Autonomous Code Reviewer: Open-source project leveraging GPT-4 to review GitHub pull requests autonomously. 500+ stars.
Semantic DocSearch: A vector-based search engine built from scratch using sentence-transformers and FAISS.

SKILLS
Languages: Python, JavaScript, SQL, C++
Frameworks: PyTorch, TensorFlow, LangChain, FastAPI, React
Tools: Pinecone, Weaviate, Docker, Kubernetes, AWS (SageMaker, EC2, S3), Git
"""
    },
    {
        "name": "Sarah Jenkins",
        "email": "sarah.j.dev@example.com",
        "github_username": "sjenkins-dev",
        "type": "demo",
        "skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "Node.js", "GraphQL"],
        "experience": 6,
        "resume_text": """
Sarah Jenkins
New York, NY | sarah.j.dev@example.com

SUMMARY
Frontend-focused Fullstack Engineer with 6 years of experience building high-performance, accessible, and scalable web applications using React, Next.js, and TypeScript. Passionate about UX and performance optimization.

EXPERIENCE
Lead Frontend Engineer | FinTech Innovations | 2020 - Present
- Spearheaded the migration of a legacy SPA to Next.js 13 (App Router), improving Lighthouse performance scores from 65 to 98 and boosting SEO rankings.
- Developed a comprehensive component library using Radix UI and Tailwind CSS, standardizing design across 4 internal products.
- Mentored 4 junior developers and established strict CI/CD pipelines with GitHub Actions and Cypress for E2E testing.

Software Engineer | WebWorks Media | 2017 - 2020
- Built highly interactive dashboards using React and Redux for real-time analytics.
- Integrated GraphQL APIs to reduce frontend payload size by 40%.
- Collaborated with UX designers to implement pixel-perfect, responsive interfaces.

EDUCATION
B.S. Software Engineering | University of Washington | 2017

SKILLS
Frontend: React, Next.js, TypeScript, Tailwind CSS, Redux, HTML5, CSS3
Backend: Node.js, Express, PostgreSQL, GraphQL
Testing: Jest, React Testing Library, Cypress
Tools: Git, Webpack, Vite, Vercel, AWS
"""
    },
    {
        "name": "David Rodriguez",
        "email": "david.r.backend@example.com",
        "github_username": "david-sys",
        "type": "demo",
        "skills": ["Go", "Python", "Kubernetes", "Kafka", "PostgreSQL", "AWS", "Microservices"],
        "experience": 8,
        "resume_text": """
David Rodriguez
Austin, TX | david.r.backend@example.com

SUMMARY
Senior Backend & Systems Engineer with deep expertise in distributed systems, high-throughput microservices, and cloud infrastructure. Proficient in Go and Python.

EXPERIENCE
Staff Backend Engineer | CloudScale Inc. | 2019 - Present
- Architected a distributed event streaming platform using Apache Kafka and Go, processing over 50 million events daily with 99.99% uptime.
- Transitioned monolithic architecture to Kubernetes-based microservices, reducing deployment times from hours to 10 minutes.
- Optimized complex PostgreSQL queries, reducing database load by 60% and improving API response times by 300ms.

Backend Developer | StartupX | 2015 - 2019
- Developed REST APIs in Python using Django and Django Rest Framework for a B2B SaaS platform.
- Implemented caching layers using Redis to handle traffic spikes during product launches.
- Managed AWS infrastructure (EC2, RDS, S3) using Terraform.

EDUCATION
B.S. Computer Science | University of Texas at Austin | 2015

SKILLS
Languages: Go, Python, Java, SQL
Databases: PostgreSQL, MongoDB, Redis
Infrastructure: Kubernetes, Docker, AWS, Terraform, Kafka, gRPC
"""
    },
    {
        "name": "Priya Sharma",
        "email": "priya.mlops@example.com",
        "github_username": "priya-mlops",
        "type": "demo",
        "skills": ["MLOps", "Kubeflow", "Docker", "Python", "TensorFlow", "AWS SageMaker", "CI/CD"],
        "experience": 4,
        "resume_text": """
Priya Sharma
Seattle, WA | priya.mlops@example.com

SUMMARY
MLOps Engineer specializing in bridging the gap between data science and operations. Proven track record of operationalizing machine learning models and building robust ML pipelines.

EXPERIENCE
MLOps Engineer | AI Solutions Corp | 2021 - Present
- Built end-to-end automated ML training and deployment pipelines using Kubeflow and GitHub Actions.
- Reduced model deployment time from 2 weeks to 2 days by containerizing model serving APIs using Docker and FastAPI.
- Implemented model monitoring using Prometheus and Grafana to track data drift and performance degradation.

Data Engineer | TechLogix | 2019 - 2021
- Developed ETL pipelines using Apache Spark and Airflow to process terabytes of raw telemetry data.
- Optimized data storage formats in S3 (Parquet) to reduce AWS storage costs by 20%.

EDUCATION
B.S. Data Science | University of Michigan | 2019

SKILLS
MLOps: Kubeflow, MLflow, Airflow, Model Monitoring
Engineering: Python, Bash, Docker, Kubernetes, Terraform
Cloud: AWS (SageMaker, EKS, S3), GCP
"""
    },
    {
        "name": "Marcus Johnson",
        "email": "marcus.j.ai@example.com",
        "github_username": "marcus-genai",
        "type": "demo",
        "skills": ["GenAI", "Prompt Engineering", "LLMOps", "Python", "HuggingFace", "LangGraph"],
        "experience": 3,
        "resume_text": """
Marcus Johnson
Boston, MA | marcus.j.ai@example.com

SUMMARY
Forward-thinking AI Developer focused on Generative AI applications. Experienced with LangChain, LangGraph, and deploying custom LLM agents for enterprise use cases.

EXPERIENCE
AI Applications Developer | NextGen Tech | 2022 - Present
- Developed an autonomous multi-agent system using LangGraph to assist the HR team with resume screening and candidate evaluation.
- Fine-tuned open-source LLMs (Llama-2, Mistral) using PEFT and LoRA on custom enterprise datasets, achieving a 20% improvement in domain-specific tasks.
- Integrated Retrieval-Augmented Generation (RAG) with a Chroma vector database to ground chatbot responses in company documentation.

Software Engineer Intern | InnovateAI | 2021 - 2022
- Contributed to an internal dashboard built with React and FastAPI to monitor API usage and latency for OpenAI endpoints.
- Wrote data scraping scripts in Python (BeautifulSoup) to collect and clean 50GB of training text data.

EDUCATION
B.S. Computer Science | Boston University | 2022

SKILLS
GenAI: Prompt Engineering, Fine-tuning, RAG, LangChain, LangGraph, HuggingFace
Languages: Python, JavaScript
Tools: Chroma, Pinecone, FastAPI, Docker
"""
    }
]

def get_demo_candidates(job_title: str, required_skills: list[str], limit: int = 3) -> list[dict]:
    """Return a curated list of demo candidates relevant to the job."""
    # Simple semantic match: count overlapping skills or text match
    search_terms = [s.lower() for s in required_skills] + [job_title.lower()]
    
    scored_candidates = []
    for cand in DEMO_CANDIDATES:
        score = 0
        cand_text = cand["resume_text"].lower()
        for term in search_terms:
            if term in cand_text:
                score += 1
        scored_candidates.append((score, cand))
    
    # Sort by score desc
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in scored_candidates[:limit]]
