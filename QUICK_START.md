# Quick Start Guide

Get ATA Feature 1 running in 3 minutes.

## Prerequisites

- Docker Desktop running
- OpenAI API key

## Steps

### 1. Configure

```bash
# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
echo "DATABASE_URL=postgresql://ata_user:ata_password@localhost:5432/ata_db" >> .env
```

### 2. Start

```bash
# Make sure Docker Desktop is running, then:
docker-compose up --build
```

Wait 2-3 minutes for initial build and startup.

### 3. Test

1. Open http://localhost:3000
2. Click "Create New Role"
3. Fill the form:
   - Role: "Software Engineer"
   - Team: "Engineering"
   - Seniority: Mid-Level
   - Work Type: Remote
   - Location: "Remote (US)"
   - Must-have skills: "Python", "FastAPI"
   - Salary: $100,000 - $140,000 USD
4. Click "Generate job description with AI"
5. Wait 30-60 seconds
6. Review the generated JD
7. Click "Approve & Publish"
8. See success screen

## Verify

Check database:
```bash
docker-compose exec postgres psql -U ata_user -d ata_db -c "SELECT role_title, status FROM role_briefs;"
```

You should see your role with status "PUBLISHED".

## Troubleshooting

**Can't connect to Docker?**
Start Docker Desktop application.

**API key error?**
Verify your OpenAI API key in `.env` is correct.

**Port conflicts?**
Stop other services using ports 3000, 8000, or 5432.

## What's Next

- Test the revision flow
- Test inline editing
- Try different tone preferences
- Experiment with key outcomes

See TESTING.md for complete test scenarios.
