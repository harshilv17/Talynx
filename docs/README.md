# Talynx Autonomous Talent Acquisition (ATA)

Talynx ATA is a next-generation, AI-driven Applicant Tracking System (ATS) that automates the entire recruitment pipeline, from Job Description generation to final Offer issuance.

## Features

- **Feature 1: JD Generation**  
  Interactively collect requirements from hiring managers via chat, then autonomously generate and publish highly optimized Job Descriptions.
- **Feature 2: Sourcing & Screening**  
  Uses the GitHub API (combined with rich Demo candidate fallbacks) to source candidates natively. Features semantic skill matching via SentenceTransformers to score and rank candidate fit. 
- **Feature 3: Outreach**  
  Generates personalized outreach sequences. Automatically manages replies (simulated in demo mode) and transitions interested respondents directly to the evaluation queue.
- **Feature 4: Evaluation & Offer**  
  Calculates deep technical, experience, and holistic match scores. Uses AI heuristics to output structured Hiring Decisions (e.g. `HIRE (Strong)` vs `NO HIRE`). Automatically generates tailored offer letters and manages the digital sign-off states.

## End-to-End Workflow

1. Start by clicking **Create New Role** on the Dashboard. Chat with the AI to refine your requirements, then **Publish**.
2. Advance to the **Pipeline (Sourcing)**. The AI will autonomously find and screen real developers on GitHub and combine them with demo dataset profiles.
3. Once satisfied, Shortlist your top choices and proceed to **Outreach**.
4. Start the outreach sequence. The system will email the candidates, simulating their responses behind the scenes. 
5. Proceed to the **Evaluation** hub. You will only see candidates who responded positively ("Interested").
6. Click **Evaluate** to trigger the final scorecard algorithm. 
7. If the candidate clears the high-bar recommendation (>=75%), generate their **Offer Letter**, preview it, and securely send it via email to close the loop!

## Documentation Navigation
- [Setup & Installation](./SETUP.md)
- [Architecture & Tech Stack](./ARCHITECTURE.md)
- [Automated Testing](./TESTING.md)
