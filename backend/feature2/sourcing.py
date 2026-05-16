import httpx
import logging
from datetime import datetime
import json
from core.config import get_settings
from feature2.demo_candidates import get_demo_candidates
from core.openai_client import get_groq_client

logger = logging.getLogger(__name__)

def _generate_github_query(role_brief: dict) -> str:
    """Use LLM to generate an optimized GitHub search query based on the role."""
    client = get_groq_client()
    title = role_brief.get("role_title", role_brief.get("job_title", "Software Engineer"))
    skills = role_brief.get("must_have_skills", ["Python"])
    
    prompt = f"""
    You are an expert tech recruiter. We need to search GitHub for candidates for a '{title}' role.
    Required skills: {', '.join(skills)}.
    
    Generate ONLY a GitHub search query string. 
    Use the 'language:' filter for the primary language.
    Include 2-3 relevant keywords.
    Example for Frontend: "react nextjs language:typescript"
    Example for AI: "langchain pytorch language:python"
    
    Return JUST the query string, no quotes, no markdown.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )
        query = response.choices[0].message.content.strip().replace('"', '')
        if "language:" not in query:
            query += f" language:{skills[0].lower() if skills else 'python'}"
        return query
    except Exception as e:
        logger.error(f"Failed to generate query: {e}")
        return f"{skills[0].lower() if skills else 'python'} language:{skills[0].lower() if skills else 'python'}"

def _fetch_live_github_candidates(role_brief: dict) -> list[dict]:
    """Search GitHub using dynamic query and extract profile metrics."""
    settings = get_settings()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Talynx-ATS"
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    query = _generate_github_query(role_brief)
    
    location = role_brief.get("location", "remote").lower()
    if location and location != "remote":
        query += f" location:{location}"

    url = f"https://api.github.com/search/users?q={query}&per_page=10"
    candidates = []
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"GitHub API Error: {resp.status_code}")
                return candidates
            
            users = resp.json().get("items", [])
            for u in users:
                user_url = u["url"]
                user_resp = client.get(user_url, headers=headers)
                if user_resp.status_code != 200:
                    continue
                    
                user_data = user_resp.json()
                
                # Quality heuristics
                if user_data.get("type", "").lower() == "organization": continue
                login = (user_data.get("login") or "").lower()
                if any(b in login for b in ["bot", "ci-", "auto"]): continue
                if not user_data.get("name") or len(login) <= 2: continue
                
                public_repos = user_data.get('public_repos', 0)
                followers = user_data.get('followers', 0)
                if public_repos < 3 or (followers == 0 and user_data.get('following', 0) == 0):
                    continue
                
                repos_resp = client.get(f"{user_url}/repos?sort=stargazers&per_page=5", headers=headers)
                repo_languages = set()
                repo_descriptions = []
                repos_list = []
                
                if repos_resp.status_code == 200:
                    for repo in repos_resp.json():
                        lang = repo.get("language")
                        if lang: repo_languages.add(lang)
                        desc = repo.get("description")
                        if desc: repo_descriptions.append(desc)
                        repos_list.append({
                            "name": repo.get("name"),
                            "stars": repo.get("stargazers_count"),
                            "description": desc,
                            "language": lang
                        })
                
                if not repo_languages: continue
                
                exp_years = 0
                created_at = user_data.get("created_at")
                if created_at:
                    exp_years = datetime.now().year - int(created_at[:4])
                
                name = user_data.get("name") or user_data.get("login")
                bio = user_data.get("bio") or ""
                
                must_have_skills = role_brief.get("must_have_skills", [])
                base_skills = {must_have_skills[0].capitalize() if must_have_skills else "Python"}
                skills = list(base_skills | repo_languages)
                
                # Profile payload for frontend viewer
                github_profile = {
                    "username": login,
                    "bio": bio,
                    "followers": followers,
                    "public_repos": public_repos,
                    "avatar_url": user_data.get("avatar_url"),
                    "top_repositories": repos_list,
                    "activity_summary": f"Active developer primarily coding in {', '.join(repo_languages)}."
                }
                
                # Resume text equivalent for RAG
                resume_text = (
                    f"Name: {name}\n"
                    f"Role: Open Source Developer\n"
                    f"Bio: {bio}\n"
                    f"GitHub Metrics: {public_repos} repositories, {followers} followers.\n"
                    f"Languages: {', '.join(repo_languages)}\n"
                    f"Project Descriptions: {' | '.join(repo_descriptions)}"
                )

                candidates.append({
                    "name": name,
                    "skills": skills,
                    "experience": exp_years,
                    "resume_text": resume_text,
                    "source": "github",
                    "type": "live",
                    "github_profile": github_profile
                })
                
            return candidates[:5] # Max 5 live candidates

    except Exception as e:
        logger.warning(f"Failed to fetch live GitHub candidates: {e}")
        return []

def fetch_github_candidates(role_brief: dict) -> list[dict]:
    """
    Main entrypoint: combines high-fidelity Demo candidates and live Job-Aware GitHub candidates.
    """
    title = role_brief.get("role_title", role_brief.get("job_title", "Software Engineer"))
    skills = role_brief.get("must_have_skills", [])
    
    # 1. Get high-quality demo candidates (Resumes)
    demo_cands = get_demo_candidates(title, skills, limit=3)
    
    # 2. Get live GitHub candidates (Profiles)
    live_cands = _fetch_live_github_candidates(role_brief)
    
    # Combine
    combined = demo_cands + live_cands
    return combined
