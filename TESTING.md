# Testing Guide for ATA Feature 1

This document provides step-by-step instructions to test the complete end-to-end flow of Feature 1.

## Prerequisites

1. Docker Desktop must be running
2. OpenAI API key must be set in `.env` file

## Setup Steps

### 1. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Start the System

```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Use docker-compose directly
docker-compose up --build
```

Wait for all services to start. You should see:
- PostgreSQL ready on port 5432
- Backend API ready on port 8000
- Frontend ready on port 3000

### 3. Verify Services

Open these URLs in your browser:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Backend Health: http://localhost:8000/health

## End-to-End Test Scenarios

### Test Scenario 1: Happy Path (Approve on First Try)

1. Navigate to http://localhost:3000
2. Click "Create New Role"
3. Fill out the intake form:
   - Role Title: "Senior Full Stack Engineer"
   - Team: "Engineering"
   - Seniority: Senior
   - Work Type: Hybrid
   - Location: "San Francisco, CA"
   - Must-have skills: "React", "Node.js", "PostgreSQL", "TypeScript"
   - Nice-to-have: "Docker", "AWS"
   - Salary: $140,000 - $180,000 USD
   - Headcount: 1
   - Years of Experience: 5
   - Reports to: "VP of Engineering"
   - Context Note: "We need someone who can work across the stack and mentor junior developers"
   - Tone: Conversational

4. Click "Generate job description with AI"
5. You should be redirected to `/review/{thread_id}`
6. Wait for the AI to generate the JD (30-60 seconds)
7. Review the generated JD and guardrail banner
8. Click "Approve & Publish"
9. Wait for publishing to complete
10. You should see the success screen

### Test Scenario 2: Revision Flow

1. Create a new role (follow steps 1-6 from Scenario 1)
2. Instead of approving, click "Re-generate with Feedback"
3. Enter feedback: "Make the responsibilities section more focused on backend work"
4. Submit feedback
5. Wait for the revision (AI will regenerate)
6. Review the updated JD
7. Approve and publish

### Test Scenario 3: Inline Edit

1. Create a new role (follow steps 1-6 from Scenario 1)
2. Click "Edit Inline"
3. Modify the job title, tagline, or any section
4. Click "Save & Publish"
5. Verify the edited version is published

### Test Scenario 4: Validation Errors

1. Go to create new role
2. Submit the form with missing required fields
3. Verify appropriate error messages appear
4. Try salary_max < salary_min
5. Verify validation catches this

### Test Scenario 5: Maximum Revisions

1. Create a new role
2. Request revision 3 times with different feedback
3. On the 3rd revision, verify you cannot request another
4. Verify the UI shows "Maximum revisions reached"
5. Use inline edit instead

## Database Verification

Check that records were created correctly:

```bash
# Access the PostgreSQL container
docker-compose exec postgres psql -U ata_user -d ata_db

# Check role briefs
SELECT id, thread_id, status, role_title FROM role_briefs;

# Check job descriptions
SELECT id, thread_id, version, status FROM job_descriptions;

# Check sourcing queue
SELECT id, thread_id, status FROM sourcing_queue;

# Exit
\q
```

## Expected Results

After a successful run through any scenario, you should have:

1. **role_briefs table**: One record with status "published"
2. **job_descriptions table**: One or more records (depending on revisions) with the latest marked as "published"
3. **sourcing_queue table**: One record with status "pending" (ready for Feature 2)

## Troubleshooting

### Backend Issues

```bash
# View backend logs
docker-compose logs backend -f

# Check if migrations ran
docker-compose exec backend alembic current

# Manually run migrations
docker-compose exec backend alembic upgrade head
```

### Frontend Issues

```bash
# View frontend logs
docker-compose logs frontend -f

# Rebuild frontend
docker-compose up --build frontend
```

### Database Issues

```bash
# Check if database is accessible
docker-compose exec postgres pg_isready -U ata_user

# View all tables
docker-compose exec postgres psql -U ata_user -d ata_db -c "\dt"
```

### API Testing with cURL

Test the API directly:

```bash
# Start job generation
curl -X POST http://localhost:8000/api/v1/feature1/start \
  -H "Content-Type: application/json" \
  -d '{
    "role_title": "Software Engineer",
    "team": "Engineering",
    "seniority": "mid",
    "work_type": "remote",
    "location": "Remote (US)",
    "must_have_skills": ["Python", "FastAPI"],
    "salary_min": 100000,
    "salary_max": 140000,
    "currency": "USD",
    "headcount": 1,
    "tone_preference": "conversational"
  }'

# Check status (replace THREAD_ID)
curl http://localhost:8000/api/v1/feature1/status/THREAD_ID

# Submit approval (replace THREAD_ID)
curl -X POST http://localhost:8000/api/v1/feature1/review/THREAD_ID \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
```

## Clean Reset

To start fresh:

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

## Success Criteria

Feature 1 is working correctly if:

1. Form submission creates a role brief in the database
2. LangGraph starts and runs the 5 nodes in sequence
3. JD generation completes with valid JSON output
4. Guardrail check runs and flags/corrects any issues
5. Graph pauses at review node (interrupt works)
6. Status endpoint returns current state while paused
7. Approval resumes graph and publishes JD
8. Revision loops back to JD generation with feedback
9. Inline edit saves changes and publishes
10. Published JD appears in database with sourcing_queue record
11. Frontend polling works and updates UI in real-time
12. All state persists through server restarts (checkpointer works)
