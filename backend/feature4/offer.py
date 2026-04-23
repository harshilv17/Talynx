import datetime

def generate_offer(candidate: dict, jd: dict) -> str:
    """
    Generate a deterministic, structured offer letter for a candidate.
    """
    # Safe extraction with fallbacks
    name = candidate.get("name", "Candidate")
    role = jd.get("job_title") or jd.get("role") or "Software Engineer"
    score = float(candidate.get("score", 0.0))
    company_name = "Talynx AI"
    
    # Compensation logic based on score
    if score > 80:
        compensation = "₹18,00,000 LPA"
    elif score >= 60:
        compensation = "₹14,00,000 LPA"
    else:
        compensation = "₹10,00,000 LPA"
        
    # Joining date (30 days from today)
    joining_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%d %B %Y")
    
    # Format the offer letter
    offer_letter = f"""Dear {name},

Congratulations! We are thrilled to offer you the position of {role} at {company_name}. 

Throughout our evaluation process, your skills and experience stood out, and we are excited about the value you will bring to our team.

Offer Details:
• Role: {role}
• Compensation: {compensation}
• Expected Joining Date: {joining_date}
• Location: Remote / HQ

We believe you will be a great addition to {company_name} and look forward to welcoming you aboard. Please let us know if you accept this offer by replying to this letter.

Best regards,
Talent Acquisition Team
{company_name}
"""
    return offer_letter


def send_offer_email(candidate_name: str, offer_text: str):
    """
    Simulate sending an offer email to the candidate.
    """
    print(f"Sending offer to {candidate_name}")
    print(offer_text)
    