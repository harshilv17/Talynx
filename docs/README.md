# Talynx Autonomous Talent Acquisition (ATA)

Talynx ATA is an end-to-end, AI-powered Applicant Tracking System (ATS) that automates the entire recruitment lifecycle from Job Description creation to finalizing an offer.

## Features

- **Feature 1: Intake & Job Description Generation**
  Conversational AI agent for gathering role requirements from hiring managers via chat, automatically generating and publishing highly optimized job descriptions.
  
- **Feature 2: Sourcing & Screening**
  Implements a **dual-stream candidate sourcing architecture**, seamlessly integrating high-quality "Demo" candidates (featuring structured ATS-style resumes) alongside "Live" developer profiles sourced natively via the GitHub API. Features robust sourcing intelligence using LLM-generated dynamic queries, paired with semantic skill matching via SentenceTransformers to accurately score and rank candidate fit.
  - **Candidate Comparison Matrix:** Compare selected candidates side-by-side.
  - **HR Notes:** Real-time notes synchronization.
  - **Dedicated Profile Viewers:** Advanced UX supporting both modal-based ATS resume viewing and native GitHub profile rendering.

- **Feature 3: Outreach Sequences**
  Generates personalized outreach sequences based on candidate profiles. Automatically manages replies (simulated in demo mode) and transitions interested respondents directly to the evaluation queue.

- **Feature 4: Evaluation & Offer**
  Calculates deep technical, experience, and holistic match scores.
  - **"Why this candidate?":** AI-generated explanations of the candidate's fit.
  - **Hiring Decisions:** Outputs structured recommendations (e.g. `HIRE (Strong)` vs `NO HIRE`).
  - **Offer Management:** Automatically generates tailored offer letters (for "Interested" candidates only) and closes the loop (marks Candidate as Hired, JD as Closed).

## Tech Stack
- **Frontend:** Next.js (App Router), Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, LangGraph, Python
- **Database:** MongoDB Atlas

## End-to-End Workflow

1. Start by clicking **Create New Role** on the Dashboard. Chat with the AI to refine your requirements, then **Publish**.
2. Advance to the **Pipeline (Sourcing)**. The AI will autonomously find and screen real developers on GitHub and combine them with demo dataset profiles. Compare top candidates and add HR notes.
3. Once satisfied, Shortlist your top choices and proceed to **Outreach**.
4. Start the outreach sequence. The system will email the candidates, simulating their responses behind the scenes. 
5. Proceed to the **Evaluation** hub. You will only see candidates who responded positively ("Interested"). Read the AI explanation for their fit.
6. Click **Evaluate** to trigger the final scorecard algorithm. 
7. If the candidate clears the high-bar recommendation, click **Generate Offer Letter**, preview it, and securely send it via email to close the loop! The dashboard will now show the JD as Closed with the hired candidate's name.

## Documentation Navigation
- [Setup & Installation](./SETUP.md)
- [Architecture & Tech Stack](./ARCHITECTURE.md)
- [Automated Testing](./TESTING.md)
