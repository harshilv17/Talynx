# Autonomous Talent Acquisition (ATA) System

## Overview
ATA is an end-to-end AI-powered hiring automation system designed to streamline recruitment. It handles everything from job description generation to sourcing, screening, candidate evaluation, and automated offer generation.

## Features

### Feature 1: Intake & JD Generation
- **Intake**: Structured form for hiring managers to submit role requirements.
- **JD Generation**: AI generates bias-free, structured job descriptions using GPT-4o.
- **Guardrails**: Secondary AI pass verifies compliance, tone, and formatting.
- **Review Loop**: Human-in-the-loop review with inline editing and feedback cycles.

### Feature 2: Sourcing & Screening
- **Sourcing**: Fetches real candidate profiles via GitHub API matching the JD requirements.
- **Screening**: Automatically screens candidates based on hard minimums (years of experience, must-have skills).
- **Ranking**: Generates embeddings for candidates and JD to calculate a cosine-similarity match score.

### Feature 4: Evaluation & Offer
- **Evaluation Scorecard**: Deterministic scorecard assigning points for technical fit, experience, and skill match.
- **Decision Engine**: Automated 'Hire' vs 'No Hire' recommendation based on the overall score threshold.
- **Offer Generation**: Automatically generates a structured offer letter with dynamic compensation mapping.

## High-Level Flow
1. **Manager** submits a Role Brief.
2. **AI** creates and validates the Job Description (Feature 1).
3. **Manager** approves the JD, publishing it to the system.
4. **System** sources candidates and ranks them via embeddings (Feature 2).
5. **System** evaluates candidates and recommends decisions (Feature 4).
6. **Recruiter** reviews evaluations and clicks "Generate Offer" for selected candidates.
