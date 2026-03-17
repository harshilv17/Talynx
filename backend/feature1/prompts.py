def get_jd_generation_prompt(role_brief: dict, tone: str, is_revision: bool = False, 
                              previous_jd: dict = None, feedback: str = None) -> str:
    """Generate the system prompt for JD generation."""
    
    tone_guidance = {
        "formal": "Use a formal, professional tone with structured language.",
        "conversational": "Use a warm, conversational tone that feels human and approachable.",
        "technical": "Use a technical, precise tone focused on technical details and accuracy."
    }
    
    base_prompt = f"""You are an expert job description writer. Generate a comprehensive, inclusive job description based on the role brief provided.

CRITICAL REQUIREMENTS:
- Write in second person (you will, you'll be responsible for)
- Use action verbs to start every responsibility bullet
- NEVER use gendered language (he/she, his/her, guys, chairman)
- NEVER use age signals (recent grad, digital native, young, energetic)
- NEVER use exclusionary terms (rockstar, ninja, guru, manpower)
- Keep total length under 600 words
- ALWAYS show the full salary band, never just a midpoint
- Tone: {tone_guidance.get(tone, tone_guidance['conversational'])}
- Return ONLY valid JSON with no markdown, no explanation, no commentary

OUTPUT STRUCTURE:
{{
  "job_title": "Full job title",
  "tagline": "One compelling sentence about the role",
  "about_role": "2-3 sentence overview of what this person will do and why it matters",
  "responsibilities": ["Action-verb led bullet 1", "Action-verb led bullet 2", ...],
  "requirements": ["Requirement 1", "Requirement 2", ...],
  "nice_to_haves": ["Nice to have 1", "Nice to have 2", ...],
  "company_blurb": "2-3 sentences about the company and team",
  "salary_range": "Formatted salary string including currency",
  "location_work_type": "Location and work type string"
}}

ROLE BRIEF:
- Title: {role_brief.get('role_title')}
- Team: {role_brief.get('team')}
- Seniority: {role_brief.get('seniority')}
- Work Type: {role_brief.get('work_type')}
- Location: {role_brief.get('location')}
- Must-have skills: {', '.join(role_brief.get('must_have_skills', []))}
- Nice-to-have skills: {', '.join(role_brief.get('nice_to_have_skills', []))}
- Salary: {role_brief.get('currency', 'USD')} {role_brief.get('salary_min'):,} - {role_brief.get('salary_max'):,}
- Headcount: {role_brief.get('headcount', 1)}
"""

    if role_brief.get('years_of_experience'):
        base_prompt += f"- Years of experience: {role_brief['years_of_experience']}\n"
    
    if role_brief.get('reports_to'):
        base_prompt += f"- Reports to: {role_brief['reports_to']}\n"
    
    if role_brief.get('key_outcomes'):
        base_prompt += f"- Key outcomes: {', '.join(role_brief['key_outcomes'])}\n"
        base_prompt += "\nIMPORTANT: The responsibilities section MUST map directly to these key outcomes.\n"
    
    if role_brief.get('context_note'):
        base_prompt += f"\nADDITIONAL CONTEXT:\n{role_brief['context_note']}\n"
    
    if is_revision and previous_jd and feedback:
        base_prompt += f"""

THIS IS A REVISION REQUEST.

PREVIOUS JD:
{previous_jd}

HIRING MANAGER FEEDBACK:
{feedback}

INSTRUCTIONS:
- ONLY change the sections or elements mentioned in the feedback
- Keep all other sections exactly as they were
- Maintain the same tone and style for unchanged sections
- Return the complete updated JD in the same JSON format
"""
    
    return base_prompt


def get_guardrail_prompt() -> str:
    """Generate the system prompt for guardrail checking."""
    
    return """You are a job description compliance reviewer. Analyze the provided job description for issues and return a structured assessment.

CHECK FOR THESE ISSUES:

1. BIASED OR EXCLUSIONARY LANGUAGE:
   - Terms like rockstar, ninja, guru, manpower, chairman
   - Gendered language (he/she, his/her, guys)
   - Age signals (recent grad, digital native, young, energetic)

2. REQUIREMENT INFLATION:
   - More than 8 bullets in the requirements section
   - Preferences disguised as requirements

3. SALARY CLARITY:
   - Missing salary information
   - Vague ranges like "competitive" or "market rate"
   - Only showing midpoint instead of full band

4. EXCESSIVE JARGON:
   - Overuse of corporate buzzwords
   - Unclear or vague language

SCORING:
- Tone score: 0-100 based on clarity, inclusivity, and professionalism

RETURN FORMAT (ONLY valid JSON, no markdown, no explanation):
{{
  "passed": true or false,
  "issues": [
    {{
      "issue": "Brief description of the issue",
      "original_text": "The problematic text from the JD",
      "suggested_fix": "Recommended replacement text"
    }}
  ],
  "corrected_jd": {{
    "job_title": "...",
    "tagline": "...",
    "about_role": "...",
    "responsibilities": [...],
    "requirements": [...],
    "nice_to_haves": [...],
    "company_blurb": "...",
    "salary_range": "...",
    "location_work_type": "..."
  }},
  "tone_score": 85.5
}}

RULES:
- If passed is true, issues should be empty array and corrected_jd should be null
- If passed is false, provide corrected_jd with ALL issues fixed
- Always provide tone_score regardless of pass/fail
- Return ONLY the JSON object, no markdown formatting
"""


def format_jd_for_guardrail(jd: dict) -> str:
    """Format JD content for guardrail review."""
    
    sections = []
    sections.append(f"JOB TITLE: {jd.get('job_title', '')}")
    sections.append(f"TAGLINE: {jd.get('tagline', '')}")
    sections.append(f"\nABOUT THE ROLE:\n{jd.get('about_role', '')}")
    
    sections.append("\nRESPONSIBILITIES:")
    for resp in jd.get('responsibilities', []):
        sections.append(f"- {resp}")
    
    sections.append("\nREQUIREMENTS:")
    for req in jd.get('requirements', []):
        sections.append(f"- {req}")
    
    sections.append("\nNICE TO HAVE:")
    for nth in jd.get('nice_to_haves', []):
        sections.append(f"- {nth}")
    
    sections.append(f"\nCOMPANY:\n{jd.get('company_blurb', '')}")
    sections.append(f"\nCOMPENSATION: {jd.get('salary_range', '')}")
    sections.append(f"LOCATION: {jd.get('location_work_type', '')}")
    
    return "\n".join(sections)
