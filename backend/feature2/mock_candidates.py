"""Mock candidate dataset for Feature 2 sourcing & screening.

Realistic resumes with projects, certifications, achievements,
varied quality, and mixed relevance for RAG testing.
"""

MOCK_CANDIDATES = [
    {
        "name": "Aarav Mehta",
        "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker", "Redis", "Celery"],
        "experience": 6,
        "resume_text": (
            "AARAV MEHTA — Senior Backend Engineer\n"
            "Email: aarav.mehta@email.com | LinkedIn: linkedin.com/in/aaravmehta\n\n"
            "SUMMARY\n"
            "Senior backend engineer with 6 years of experience building scalable web "
            "applications using Python and Django. Deep expertise in PostgreSQL query "
            "optimization, AWS infrastructure, and distributed systems.\n\n"
            "EXPERIENCE\n"
            "Senior Backend Engineer — FinStack (2021–Present)\n"
            "• Led a team of 4 engineers to migrate a monolithic Django application to "
            "microservices, reducing deployment time by 70%\n"
            "• Designed and implemented RESTful APIs handling 2M+ requests/day with 99.9% uptime\n"
            "• Optimized PostgreSQL queries reducing average response time from 800ms to 120ms\n"
            "• Implemented Redis caching layer reducing database load by 40%\n\n"
            "Backend Engineer — DataVault Inc (2019–2021)\n"
            "• Built data pipeline processing 500K records/hour using Celery and RabbitMQ\n"
            "• Managed AWS infrastructure including EC2, RDS, Lambda, and S3\n"
            "• Implemented CI/CD pipelines with GitHub Actions and Docker\n\n"
            "PROJECTS\n"
            "• PaymentGateway — Open-source payment processing library for Django (120+ GitHub stars)\n"
            "• QueryOptimizer — PostgreSQL query analysis tool that suggests index improvements\n\n"
            "CERTIFICATIONS\n"
            "• AWS Solutions Architect Associate (2022)\n"
            "• Docker Certified Associate (2021)\n\n"
            "EDUCATION\n"
            "B.Tech Computer Science — IIT Delhi (2018)"
        ),
    },
    {
        "name": "Sarah Chen",
        "skills": ["React", "TypeScript", "Next.js", "Node.js", "GraphQL", "Tailwind"],
        "experience": 4,
        "resume_text": (
            "SARAH CHEN — Frontend Developer\n"
            "Portfolio: sarahchen.dev | GitHub: github.com/sarahchen\n\n"
            "SUMMARY\n"
            "Mid-level frontend developer specializing in React and TypeScript with 4 years "
            "of experience building production applications. Strong eye for UI/UX design "
            "and accessibility. Open-source contributor.\n\n"
            "EXPERIENCE\n"
            "Frontend Developer — CloudUI Labs (2022–Present)\n"
            "• Built customer-facing dashboard serving 50K+ users using Next.js with SSR\n"
            "• Reduced bundle size by 35% through code splitting and lazy loading\n"
            "• Implemented design system with 40+ reusable components used across 3 products\n"
            "• Led accessibility audit achieving WCAG 2.1 AA compliance\n\n"
            "Junior Frontend Developer — WebCraft Studio (2020–2022)\n"
            "• Developed responsive UIs with React and TypeScript for e-commerce clients\n"
            "• Built GraphQL integration layer using Apollo Client\n"
            "• Mentored 2 junior developers on React best practices\n\n"
            "PROJECTS\n"
            "• ReactFormKit — Open-source form library for React (200+ GitHub stars)\n"
            "• A11yChecker — Browser extension for accessibility testing\n\n"
            "EDUCATION\n"
            "BS Computer Science — UC Berkeley (2020)\n\n"
            "CERTIFICATIONS\n"
            "• Meta Front-End Developer Certificate (2022)"
        ),
    },
    {
        "name": "James Rodriguez",
        "skills": ["Python", "Machine Learning", "PyTorch", "SQL", "Spark", "NLP", "MLOps"],
        "experience": 5,
        "resume_text": (
            "JAMES RODRIGUEZ — ML Engineer / Data Scientist\n"
            "GitHub: github.com/jrodriguez-ml | Scholar: scholar.google.com/jrodriguez\n\n"
            "SUMMARY\n"
            "Data scientist with 5 years of experience in machine learning and deep learning. "
            "Published researcher in NLP. Expert in PyTorch and production ML systems.\n\n"
            "EXPERIENCE\n"
            "Senior ML Engineer — RecoAI (2022–Present)\n"
            "• Built recommendation engine using transformer models improving CTR by 35%\n"
            "• Deployed models on AWS SageMaker serving 10M predictions/day\n"
            "• Implemented A/B testing framework for model evaluation\n\n"
            "Data Scientist — DataPulse Analytics (2020–2022)\n"
            "• Developed NLP pipeline for sentiment analysis processing 1M+ reviews/day\n"
            "• Built customer churn prediction model achieving 92% AUC\n"
            "• Led migration from scikit-learn to PyTorch for deep learning workloads\n\n"
            "PUBLICATIONS\n"
            "• 'Efficient Fine-tuning of Transformers for Domain-Specific NLP' — EMNLP 2023\n"
            "• 'Scalable Recommendation Systems with Sparse Attention' — RecSys 2022\n\n"
            "CERTIFICATIONS\n"
            "• AWS Machine Learning Specialty (2023)\n"
            "• DeepLearning.AI MLOps Specialization (2022)\n\n"
            "EDUCATION\n"
            "MS Computer Science (ML focus) — Stanford University (2020)\n"
            "BS Mathematics — UCLA (2018)"
        ),
    },
    {
        "name": "Priya Sharma",
        "skills": ["Python", "FastAPI", "Redis", "MongoDB", "Kubernetes", "Prometheus", "Grafana"],
        "experience": 7,
        "resume_text": (
            "PRIYA SHARMA — Staff Backend Engineer\n"
            "Email: priya.sharma@email.com | LinkedIn: linkedin.com/in/priyasharma-eng\n\n"
            "SUMMARY\n"
            "Staff backend engineer with 7 years building high-performance APIs. Extensive "
            "experience with Redis caching, MongoDB, and Kubernetes at scale.\n\n"
            "EXPERIENCE\n"
            "Staff Engineer — ScaleGrid Technologies (2021–Present)\n"
            "• Architected FastAPI-based microservices handling 5M+ requests/day\n"
            "• Designed MongoDB sharding strategy reducing p99 latency by 60%\n"
            "• Built observability platform using Prometheus and Grafana\n"
            "• Led incident management for Tier-1 services (99.95% SLA)\n\n"
            "Senior Backend Engineer — CloudNine Systems (2018–2021)\n"
            "• Built real-time event processing pipeline using Redis Streams\n"
            "• Managed Kubernetes clusters across 3 AWS regions\n"
            "• Implemented zero-downtime deployment strategies\n\n"
            "PROJECTS\n"
            "• FastCache — Redis caching middleware for FastAPI (80+ stars)\n"
            "• K8sHealthCheck — Kubernetes health monitoring CLI tool\n\n"
            "CERTIFICATIONS\n"
            "• Certified Kubernetes Administrator (CKA) — 2022\n"
            "• AWS DevOps Professional — 2021\n\n"
            "EDUCATION\n"
            "B.Tech Computer Science — NIT Trichy (2017)"
        ),
    },
    {
        "name": "Michael Thompson",
        "skills": ["Java", "Spring Boot", "AWS", "Kafka", "PostgreSQL", "DynamoDB"],
        "experience": 8,
        "resume_text": (
            "MICHAEL THOMPSON — Principal Software Engineer\n\n"
            "SUMMARY\n"
            "Principal engineer with 8 years in enterprise Java applications and "
            "event-driven architectures. Led platform migrations serving 10M+ users.\n\n"
            "EXPERIENCE\n"
            "Principal Engineer — TechScale Corp (2020–Present)\n"
            "• Architected event-driven microservices using Kafka processing 500K events/min\n"
            "• Led migration from monolith to 40+ Spring Boot microservices\n"
            "• Reduced infrastructure costs by 45% through AWS optimization\n\n"
            "Senior Engineer — Enterprise Solutions Inc (2017–2020)\n"
            "• Built high-throughput REST APIs with Spring Boot and PostgreSQL\n"
            "• Implemented CQRS pattern with DynamoDB for read-heavy workloads\n"
            "• Mentored team of 6 engineers on clean architecture principles\n\n"
            "CERTIFICATIONS\n"
            "• AWS Solutions Architect Professional (2021)\n"
            "• Oracle Certified Java SE 11 Developer (2020)\n\n"
            "EDUCATION\n"
            "MS Software Engineering — Carnegie Mellon (2016)"
        ),
    },
    {
        "name": "Emily Watson",
        "skills": ["Python", "TensorFlow", "NLP", "SQL", "AWS SageMaker", "Hugging Face"],
        "experience": 3,
        "resume_text": (
            "EMILY WATSON — ML Engineer\n\n"
            "SUMMARY\n"
            "ML engineer with 3 years focused on NLP and text classification. "
            "Proficient in TensorFlow and Hugging Face transformers.\n\n"
            "EXPERIENCE\n"
            "ML Engineer — TextAI Solutions (2022–Present)\n"
            "• Built production NLP pipeline for document classification (F1: 0.94)\n"
            "• Fine-tuned BERT models for domain-specific entity recognition\n"
            "• Deployed models on SageMaker with auto-scaling endpoints\n\n"
            "Junior Data Scientist — AnalyticsPro (2021–2022)\n"
            "• Built churn prediction models using gradient boosting (AUC: 0.89)\n"
            "• Created automated reporting dashboards in Python\n\n"
            "PROJECTS\n"
            "• TextClassifier — Open-source multi-label text classifier using transformers\n"
            "• SentimentStream — Real-time Twitter sentiment analysis dashboard\n\n"
            "EDUCATION\n"
            "MS Data Science — Columbia University (2021)\n"
            "BS Statistics — University of Michigan (2019)"
        ),
    },
    {
        "name": "David Kim",
        "skills": ["Go", "gRPC", "Docker", "Kubernetes", "PostgreSQL", "Terraform"],
        "experience": 5,
        "resume_text": (
            "DAVID KIM — Backend Engineer (Go/Infrastructure)\n\n"
            "SUMMARY\n"
            "Backend engineer specializing in Go microservices and cloud infrastructure "
            "with 5 years of experience. Expert in containerized deployments.\n\n"
            "EXPERIENCE\n"
            "Backend Engineer — InfraScale (2021–Present)\n"
            "• Built high-throughput gRPC services handling 50K+ RPS in Go\n"
            "• Implemented service mesh with Istio reducing inter-service latency by 30%\n"
            "• Automated infrastructure provisioning with Terraform (200+ resources)\n\n"
            "DevOps Engineer — CloudOps Co (2019–2021)\n"
            "• Managed Kubernetes clusters serving 100+ microservices\n"
            "• Built CI/CD pipelines reducing deployment time from 45min to 8min\n"
            "• Implemented PostgreSQL performance tuning for write-heavy workloads\n\n"
            "CERTIFICATIONS\n"
            "• CKA — Certified Kubernetes Administrator (2022)\n"
            "• HashiCorp Terraform Associate (2021)\n\n"
            "EDUCATION\n"
            "BS Computer Engineering — Georgia Tech (2019)"
        ),
    },
    {
        "name": "Lisa Patel",
        "skills": ["React", "Vue.js", "CSS", "Figma", "TypeScript", "Storybook"],
        "experience": 6,
        "resume_text": (
            "LISA PATEL — Senior Frontend Engineer / Design Systems\n\n"
            "SUMMARY\n"
            "Senior frontend engineer with 6 years across React and Vue.js ecosystems. "
            "Expertise in design systems and component-driven development.\n\n"
            "EXPERIENCE\n"
            "Senior Frontend Engineer — DesignTech (2021–Present)\n"
            "• Built design system with 60+ components used by 20+ developers\n"
            "• Led migration from Vue.js to React reducing bundle size by 25%\n"
            "• Implemented Storybook-driven development workflow\n\n"
            "Frontend Developer — WebStudio (2018–2021)\n"
            "• Built responsive web applications for enterprise clients\n"
            "• Collaborated with Figma-based design workflows\n"
            "• Implemented CSS architecture using BEM methodology\n\n"
            "PROJECTS\n"
            "• ComponentLib — Open-source React component library with Tailwind\n\n"
            "EDUCATION\n"
            "BFA Interactive Design + BS Computer Science — RIT (2018)"
        ),
    },
    {
        "name": "Carlos Rivera",
        "skills": ["Python", "PostgreSQL", "AWS", "Terraform", "Redis", "Flask"],
        "experience": 4,
        "resume_text": (
            "CARLOS RIVERA — Backend Developer\n\n"
            "SUMMARY\n"
            "Backend developer with 4 years building REST APIs in Python. "
            "Solid PostgreSQL and AWS infrastructure experience.\n\n"
            "EXPERIENCE\n"
            "Backend Developer — APIFirst (2021–Present)\n"
            "• Built REST APIs using Flask serving 500K requests/day\n"
            "• Optimized PostgreSQL with advanced indexing reducing query time by 55%\n"
            "• Managed AWS infrastructure using Terraform\n\n"
            "Junior Developer — StartupXYZ (2020–2021)\n"
            "• Implemented Redis caching for session management\n"
            "• Contributed to CI/CD pipeline reducing build times by 50%\n"
            "• Built automated database migration system\n\n"
            "PROJECTS\n"
            "• FlaskBoilerplate — Production-ready Flask starter template\n\n"
            "EDUCATION\n"
            "BS Computer Science — University of Texas Austin (2020)"
        ),
    },
    {
        "name": "Aisha Johnson",
        "skills": ["Python", "Django", "React", "PostgreSQL", "Docker", "GraphQL"],
        "experience": 5,
        "resume_text": (
            "AISHA JOHNSON — Full-Stack Developer\n\n"
            "SUMMARY\n"
            "Full-stack developer with 5 years spanning Python/Django backends and "
            "React frontends. Experience with SaaS products serving 100K+ users.\n\n"
            "EXPERIENCE\n"
            "Full-Stack Developer — SaaSly (2021–Present)\n"
            "• Built end-to-end features for multi-tenant SaaS platform\n"
            "• Implemented GraphQL API layer replacing REST endpoints\n"
            "• Optimized PostgreSQL queries for complex reporting dashboards\n\n"
            "Junior Developer — WebAgency (2019–2021)\n"
            "• Developed Django REST APIs for e-commerce platform\n"
            "• Built React components for customer-facing dashboards\n"
            "• Set up Docker-based development environments\n\n"
            "PROJECTS\n"
            "• TenantManager — Multi-tenant Django middleware package\n\n"
            "EDUCATION\n"
            "BS Software Engineering — Howard University (2019)"
        ),
    },
    {
        "name": "Ryan O'Brien",
        "skills": ["Node.js", "TypeScript", "MongoDB", "AWS", "GraphQL", "WebSocket"],
        "experience": 3,
        "resume_text": (
            "RYAN O'BRIEN — Backend Developer (Node.js)\n\n"
            "SUMMARY\n"
            "Backend developer with 3 years of Node.js and TypeScript. "
            "Experience with real-time systems and cloud deployments.\n\n"
            "EXPERIENCE\n"
            "Backend Developer — RealTimeApps (2022–Present)\n"
            "• Built WebSocket-based real-time collaboration features\n"
            "• Designed MongoDB aggregation pipelines for analytics\n"
            "• Deployed applications on AWS ECS with CloudFormation\n\n"
            "Junior Developer — StartupHub (2021–2022)\n"
            "• Built RESTful and GraphQL APIs serving mobile clients\n"
            "• Implemented OAuth2 authentication flows\n\n"
            "EDUCATION\n"
            "BS Computer Science — Boston University (2021)"
        ),
    },
    {
        "name": "Mei Lin",
        "skills": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-learn"],
        "experience": 2,
        "resume_text": (
            "MEI LIN — Junior Data Scientist\n\n"
            "SUMMARY\n"
            "Junior data scientist with 2 years in statistical analysis and ML. "
            "Strong Python and SQL skills. Eager to grow into NLP.\n\n"
            "EXPERIENCE\n"
            "Data Analyst — InsightCorp (2023–Present)\n"
            "• Built churn prediction models achieving 85% accuracy\n"
            "• Created customer segmentation using k-means clustering\n"
            "• Automated weekly reporting saving 10 hours/week\n\n"
            "Data Science Intern — TechStart (2022–2023)\n"
            "• Analyzed user behavior data using Pandas and SQL\n"
            "• Built basic recommendation prototype with collaborative filtering\n\n"
            "PROJECTS\n"
            "• StockPredictor — LSTM-based stock price prediction (academic)\n\n"
            "EDUCATION\n"
            "MS Applied Statistics — NYU (2022)\n"
            "BS Mathematics — University of Wisconsin (2020)"
        ),
    },
    {
        "name": "Alex Volkov",
        "skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Celery", "RabbitMQ"],
        "experience": 6,
        "resume_text": (
            "ALEX VOLKOV — Senior Backend Engineer\n\n"
            "SUMMARY\n"
            "Senior backend engineer with 6 years in Python web development. "
            "Expert in FastAPI async APIs and distributed task processing.\n\n"
            "EXPERIENCE\n"
            "Senior Engineer — AsyncTech (2021–Present)\n"
            "• Built FastAPI services handling 3M+ async requests/day\n"
            "• Designed distributed task system with Celery + RabbitMQ (2M jobs/day)\n"
            "• Implemented PostgreSQL partitioning for time-series data\n\n"
            "Backend Developer — DataFlow Systems (2019–2021)\n"
            "• Built ETL pipelines processing 10TB/month\n"
            "• Managed AWS Lambda functions for serverless workloads\n"
            "• Implemented advanced PostgreSQL indexing strategies\n\n"
            "CERTIFICATIONS\n"
            "• AWS Developer Associate (2022)\n\n"
            "EDUCATION\n"
            "MS Computer Science — University of Washington (2019)"
        ),
    },
    {
        "name": "Nadia Hassan",
        "skills": ["React", "TypeScript", "Next.js", "Tailwind", "Jest", "Cypress"],
        "experience": 4,
        "resume_text": (
            "NADIA HASSAN — Frontend Developer\n\n"
            "SUMMARY\n"
            "Frontend developer with 4 years of React and TypeScript. "
            "Specialized in Next.js and testing-driven development.\n\n"
            "EXPERIENCE\n"
            "Frontend Developer — TestFirst Labs (2022–Present)\n"
            "• Built Next.js applications with SSR/ISR for SEO optimization\n"
            "• Achieved 95% test coverage using Jest and Cypress\n"
            "• Implemented Tailwind-based design system\n\n"
            "Junior Developer — WebWorks (2020–2022)\n"
            "• Developed React components with Zustand state management\n"
            "• Integrated React Query for server state management\n\n"
            "EDUCATION\n"
            "BS Computer Science — University of Toronto (2020)"
        ),
    },
    {
        "name": "Tom Anderson",
        "skills": ["Python", "AWS", "PostgreSQL", "Redis", "Docker", "Django", "Flask", "FastAPI"],
        "experience": 9,
        "resume_text": (
            "TOM ANDERSON — Principal Engineer / Tech Lead\n\n"
            "SUMMARY\n"
            "Principal engineer with 9 years architecting backend systems. "
            "Expert across the Python ecosystem. Led platform teams of 8+ engineers.\n\n"
            "EXPERIENCE\n"
            "Principal Engineer — MegaTech (2020–Present)\n"
            "• Architected platform serving 50M monthly users\n"
            "• Led team of 8 engineers across 3 backend services\n"
            "• Designed multi-region AWS deployment with 99.99% uptime\n"
            "• Established engineering standards and code review processes\n\n"
            "Staff Engineer — ScaleCo (2017–2020)\n"
            "• Built Python microservices using Django, Flask, and FastAPI\n"
            "• Managed PostgreSQL databases at scale (5TB+)\n"
            "• Implemented Redis-based distributed locking\n\n"
            "Senior Developer — AppFactory (2015–2017)\n"
            "• Built REST APIs and background job systems\n"
            "• Led migration from Python 2 to Python 3\n\n"
            "CERTIFICATIONS\n"
            "• AWS Solutions Architect Professional (2021)\n"
            "• Google Cloud Professional Architect (2020)\n\n"
            "EDUCATION\n"
            "MS Computer Science — MIT (2015)\n"
            "BS Computer Science — Purdue University (2013)"
        ),
    },
]

def get_demo_candidates(jd: dict) -> list[dict]:
    """Return mock candidates, injecting required skills into a few to ensure they pass."""
    import copy
    candidates = copy.deepcopy(MOCK_CANDIDATES)
    
    must_haves = jd.get("must_have_skills", [])
    
    # Inject must-haves into the first 3 candidates so they get a high score
    if must_haves:
        for i in range(min(3, len(candidates))):
            for skill in must_haves:
                if skill not in candidates[i]["skills"]:
                    candidates[i]["skills"].append(skill)
                    
    # Add source="demo" to all
    for c in candidates:
        c["source"] = "demo"
        
    return candidates
