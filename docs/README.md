# ATA - Autonomous Talent Acquisition

## Project Overview
ATA (Autonomous Talent Acquisition) is an AI-powered hiring automation system designed to streamline the recruitment process from intake to offer generation. It provides a multi-agent orchestration platform that evaluates candidates and makes autonomous hiring decisions.

## Features
1. **Feature 1: JD Generation** - Creates AI-generated, compliant job descriptions from a simple intake role brief.
2. **Feature 2: Sourcing & Screening** - Automatically sources candidates, generates semantic embeddings, and filters candidate profiles based on the generated JD.
3. **Feature 3: Outreach** - Handles automated candidate outreach and schedules interviews seamlessly.
4. **Feature 4: Evaluation & Offer** - Evaluates candidates post-interview, generates comprehensive scoring metrics, displays decision recommendations, and automatically generates a downloadable offer letter.

## System Flow
1. **Intake**: Recruiter submits a basic role requirement.
2. **JD Generation**: The system creates a full job description (Feature 1).
3. **Sourcing**: Candidates are matched and ranked against the JD (Feature 2).
4. **Outreach**: Automated emails are sent for interview scheduling (Feature 3).
5. **Evaluation**: Interview data is processed to generate candidate scorecards (Feature 4).
6. **Offer**: A finalized offer letter is generated for successful candidates.

## Tech Stack
- **Backend**: Python, FastAPI, MongoDB
- **Frontend**: Next.js 14, React, Tailwind CSS
- **AI/LLM**: Groq / OpenAI Integration
