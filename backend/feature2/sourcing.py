import httpx
import logging
from datetime import datetime
from core.config import get_settings

logger = logging.getLogger(__name__)

def fetch_github_candidates(role_brief: dict) -> list[dict]:
    """
    Search GitHub users matching the primary skill and location,
    then fetch details and explicit repository data to construct high-quality candidate objects.
    """
    settings = get_settings()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Talynx-ATS"
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
    else:
        logger.warning("Using unauthenticated GitHub requests (low rate limit)")

    # Extract primary skill and location
    must_have_skills = role_brief.get("must_have_skills", [])
    primary_skill = must_have_skills[0].lower() if must_have_skills else "python"
    
    location = role_brief.get("location", "remote").lower()
    
    query = f"{primary_skill} in:bio language:{primary_skill}"
    if location and location != "remote":
        query += f" location:{location}"

    # Limit to 10 for safety
    url = f"https://api.github.com/search/users?q={query}&per_page=10"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 403:
                logger.warning("GitHub rate limit hit")
                return []
            if resp.status_code != 200:
                logger.warning(f"GitHub API Search Error: {resp.status_code} - {resp.text}")
                return []
            
            users = resp.json().get("items", [])
            candidates = []
            
            for u in users:
                user_url = u["url"]
                user_resp = client.get(user_url, headers=headers)
                
                if user_resp.status_code != 200:
                    continue
                    
                user_data = user_resp.json()
                
                public_repos = user_data.get('public_repos', 0)
                followers = user_data.get('followers', 0)
                
                # Rule: Skip users with less than 3 repositories (Inactive/noise)
                if public_repos < 3:
                    continue
                
                # Fetch repositories
                repos_resp = client.get(f"{user_url}/repos?sort=stargazers&per_page=5", headers=headers)
                
                repo_languages = set()
                repo_descriptions = []
                
                if repos_resp.status_code == 200:
                    for repo in repos_resp.json():
                        lang = repo.get("language")
                        if lang:
                            repo_languages.add(lang)
                            
                        desc = repo.get("description")
                        if desc:
                            repo_descriptions.append(desc)
                
                if not repo_languages:
                    continue
                
                # Map Experience dynamically based on account age
                exp_years = 0
                created_at = user_data.get("created_at")
                if created_at:
                    exp_years = datetime.now().year - int(created_at[:4])
                
                name = user_data.get("name") or user_data.get("login")
                bio = user_data.get("bio") or ""
                
                # Map Skills natively reflecting their repo outputs
                base_skills = {primary_skill.capitalize()}
                if len(must_have_skills) > 1:
                    base_skills.add(must_have_skills[1].capitalize())
                
                # Unify extracted languages from repos
                skills = list(base_skills | repo_languages)
                
                # Build a meaningful profile payload optimal for semantic embeddings
                desc_str = " ".join(repo_descriptions)
                top_langs = ", ".join(list(repo_languages)[:3])
                
                resume_text = (
                    f"{name} is a software engineer with visible projects spanning {top_langs}. "
                    f"Bio context: {bio}\n"
                    f"Activity metrics: {public_repos} public repos, {followers} followers.\n"
                    f"Relevant capabilities implied by recent work spanning concepts like: {desc_str}"
                ).strip()

                candidates.append({
                    "name": name,
                    "skills": skills,
                    "experience": exp_years,
                    "resume_text": resume_text
                })

            return candidates[:10]

    except Exception as e:
        logger.warning(f"Failed to fetch explicitly mapped GitHub candidates: {e}")
        return []
