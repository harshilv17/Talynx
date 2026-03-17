# ATA System Setup Guide

Complete setup instructions for the Autonomous Talent Acquisition (ATA) system Feature 1.

## System Requirements

- Docker Desktop installed and running
- OpenAI API key with access to GPT-4o and GPT-4o-mini
- Minimum 4GB RAM available for Docker
- Ports 3000, 8000, and 5432 available

## Installation Steps

### 1. Clone and Navigate

```bash
cd /Users/harshilvalecha/Desktop/ata-system
```

### 2. Configure Environment

```bash
# The .env file should already exist with a placeholder
# Edit it to add your actual OpenAI API key
nano .env

# Replace the placeholder with your actual key:
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### 3. Start Docker Desktop

Make sure Docker Desktop is running before proceeding.

### 4. Build and Start Services

```bash
# Option 1: Use the convenience script
./start.sh

# Option 2: Manual start
docker-compose up --build
```

The first build will take 3-5 minutes to:
- Pull Docker images (PostgreSQL, Node, Python)
- Install Python dependencies (FastAPI, LangGraph, OpenAI SDK)
- Install Node dependencies (Next.js, React, Tailwind)
- Run database migrations

### 5. Verify Services

Once all services are running, verify each one:

**PostgreSQL:**
```bash
docker-compose exec postgres pg_isready -U ata_user
# Expected: ata_user:5432 - accepting connections
```

**Backend:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

**Frontend:**
Open http://localhost:3000 in your browser
You should see the ATA welcome page.

### 6. Check Database Schema

```bash
docker-compose exec postgres psql -U ata_user -d ata_db -c "\dt"
```

Expected tables:
- role_briefs
- job_descriptions
- sourcing_queue
- checkpoints (created by LangGraph)
- writes (created by LangGraph)

## First Test Run

### Quick Smoke Test

1. Open http://localhost:3000
2. Click "Create New Role"
3. Fill out the form with test data:
   - Role: "Backend Engineer"
   - Team: "Engineering"
   - Seniority: Mid-Level
   - Must-have skills: "Python", "PostgreSQL"
   - Salary: $100,000 - $140,000
   - Fill other required fields
4. Click "Generate job description with AI"
5. You should be redirected to the review page
6. Wait 30-60 seconds for generation
7. Review and approve the JD
8. Verify you see the success screen

### Database Verification

```bash
# Check that records were created
docker-compose exec postgres psql -U ata_user -d ata_db

# View the role brief
SELECT role_title, status, thread_id FROM role_briefs LIMIT 1;

# View the job description
SELECT id, version, status FROM job_descriptions LIMIT 1;

# View the sourcing queue
SELECT id, status FROM sourcing_queue LIMIT 1;

# Exit
\q
```

## Common Issues and Solutions

### Issue: Docker daemon not running

**Error:** `unable to get image: failed to connect to docker API`

**Solution:** Start Docker Desktop application

### Issue: Port already in use

**Error:** `port is already allocated`

**Solution:**
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Stop conflicting services or change ports in docker-compose.yml
```

### Issue: OpenAI API key not working

**Error:** `OpenAI API call failed: authentication error`

**Solution:**
1. Verify your API key is correct in `.env`
2. Check you have access to GPT-4o and GPT-4o-mini
3. Verify your API key has credits available

### Issue: Database migration fails

**Error:** `alembic.util.exc.CommandError`

**Solution:**
```bash
# Stop all services
docker-compose down -v

# Rebuild
docker-compose up --build
```

### Issue: Frontend can't connect to backend

**Error:** Network errors in browser console

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check NEXT_PUBLIC_API_URL in frontend/.env.local
3. Check CORS settings in backend/main.py

## Development Workflow

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs backend -f
docker-compose logs frontend -f
docker-compose logs postgres -f
```

### Restart a Service

```bash
# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend
```

### Access Container Shell

```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Database
docker-compose exec postgres psql -U ata_user -d ata_db
```

### Stop Services

```bash
# Stop but keep data
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
```

## Architecture Verification

### Verify LangGraph Checkpointer

The PostgresSaver checkpointer should create two tables:
- `checkpoints`: Stores graph state snapshots
- `writes`: Stores state updates

```bash
docker-compose exec postgres psql -U ata_user -d ata_db -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
```

### Verify Interrupt/Resume Works

1. Start a JD generation
2. Let it reach the review stage
3. Restart the backend: `docker-compose restart backend`
4. Refresh the review page
5. The state should still be there (loaded from checkpoint)
6. Approve the JD
7. It should resume and complete

## API Testing

### Using the Interactive Docs

1. Open http://localhost:8000/docs
2. Try each endpoint:
   - POST `/api/v1/feature1/start`
   - GET `/api/v1/feature1/status/{thread_id}`
   - POST `/api/v1/feature1/review/{thread_id}`
   - GET `/api/v1/feature1/published/{thread_id}`

### Using cURL

See TESTING.md for cURL examples.

## Next Steps

Once Feature 1 is verified working:
1. The sourcing_queue table contains pending records
2. Feature 2 will read from this table
3. Feature 1 code should not need modification

## Support

If you encounter issues not covered here:
1. Check docker-compose logs for all services
2. Verify .env file is configured correctly
3. Ensure Docker has sufficient resources allocated
4. Check that all required ports are available
