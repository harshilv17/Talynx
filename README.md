# ATA - Autonomous Talent Acquisition System

An agentic AI platform that automates the entire hiring pipeline, from intake to offer.

## Feature 1: Intake and JD Generation

Feature 1 enables hiring managers to submit a role brief and receive an AI-generated, guardrail-checked job description that they can review, edit, and approve.

### Features

- **Structured intake form** for role requirements, skills, compensation, and preferences
- **AI-powered JD generation** using GPT-4o with tone customization
- **Guardrail checks** for bias, clarity, and compliance using GPT-4o-mini
- **Human-in-the-loop review** with approval, inline editing, or revision requests
- **LangGraph orchestration** with PostgresSaver checkpointer for state persistence
- **Real-time status polling** from the frontend

### Tech Stack

- **Backend**: Python, FastAPI, LangGraph, OpenAI API, PostgreSQL, Alembic
- **Frontend**: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker Compose

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. Start all services:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Project Structure

```
ata-system/
├── backend/              # FastAPI backend
│   ├── core/            # Shared core modules
│   ├── feature1/        # Feature 1: Intake & JD Generation
│   └── migrations/      # Alembic database migrations
├── frontend/            # Next.js frontend
│   └── app/            # Next.js App Router
│       ├── new-role/   # Intake form
│       ├── review/     # JD review screen
│       └── components/ # React components
└── docker-compose.yml
```

### Database

The system uses PostgreSQL with three tables:
- `role_briefs`: Stores hiring manager input
- `job_descriptions`: Stores AI-generated JDs and versions
- `sourcing_queue`: Handoff point to Feature 2 (coming soon)

Migrations are automatically applied on startup.

### API Endpoints

- `POST /api/v1/feature1/start` - Submit role brief and start JD generation
- `GET /api/v1/feature1/status/{thread_id}` - Get current status and JD draft
- `POST /api/v1/feature1/review/{thread_id}` - Submit review decision
- `GET /api/v1/feature1/published/{thread_id}` - Get published JD

### Workflow

1. Hiring manager fills out intake form at `/new-role`
2. System validates input and generates JD using GPT-4o
3. Guardrail agent (GPT-4o-mini) checks for issues
4. Hiring manager reviews at `/review/{thread_id}`
5. Manager can approve, edit inline, or request revision (max 3 revisions)
6. Published JD is saved and queued for sourcing (Feature 2)

### Future Features

- **Feature 2**: Sourcing and Screening (coming soon)
- **Feature 3**: Outreach and Interviews (coming soon)
- **Feature 4**: Evaluation and Offer (coming soon)

### Development

To run backend tests or migrations manually:

```bash
# Access backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Architecture Notes

- LangGraph uses interrupt() for human-in-the-loop pauses
- PostgresSaver checkpointer ensures state survives restarts
- Feature 1 is isolated in its own module for clean extension
- All LLM calls use JSON mode and have retry logic
- Frontend polls every 2 seconds for status updates
