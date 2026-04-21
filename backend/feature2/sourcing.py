import httpx
import logging
from datetime import datetime
from core.config import get_settings

logger = logging.getLogger(__name__)

def fetch_github_candidates(role_brief: dict) -> list[dict]:
    """
    Search GitHub users matching the primary skill and location,
    then fetch details to construct candidate objects.
    """
    settings = get_settings()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Talynx-ATS"
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    # Extract primary skill and location
    must_have_skills = role_brief.get("must_have_skills", [])
    primary_skill = must_have_skills[0].lower() if must_have_skills else "python"
    
    location = role_brief.get("location", "remote").lower()
    
    query = f"language:{primary_skill}"
    if location and location != "remote":
        query += f" location:{location}"

    # GitHub limits unauthenticated requests to 60 per hour, we'll request a limit of 10 for safety.
    url = f"https://api.github.com/search/users?q={query}&per_page=10"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.error(f"GitHub API Error: {resp.status_code} - {resp.text}")
                return []
            
            data = resp.json()
            users = data.get("items", [])
            
            candidates = []
            for u in users:
                user_url = u["url"]
                user_resp = client.get(user_url, headers=headers)
                if user_resp.status_code == 200:
                    user_data = user_resp.json()
                    
                    created_at = user_data.get("created_at")
                    exp_years = 0
                    if created_at:
                        created_year = int(created_at[:4])
                        exp_years = datetime.now().year - created_year
                    
                    name = user_data.get("name") or user_data.get("login")
                    bio = user_data.get("bio") or ""
                    
                    skills = [primary_skill.capitalize()]
                    if len(must_have_skills) > 1:
                        skills.append(must_have_skills[1].capitalize())
                    
                    resume_text = (
                        f"{bio}\n"
                        f"GitHub Profile. {user_data.get('public_repos', 0)} public repos. "
                        f"{user_data.get('followers', 0)} followers. "
                        f"Account created in {created_year}. "
                        f"Link: {user_data.get('html_url')}"
                    ).strip()

                    candidates.append({
                        "name": name,
                        "skills": skills,
                        "experience": exp_years,
                        "resume_text": resume_text
                    })
            return candidates

    except Exception as e:
        logger.error(f"Failed to fetch GitHub candidates: {e}")
        return []
