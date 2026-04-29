# Architecture & Tech Stack

## System Architecture
Talynx ATA is fundamentally split into a stateless Next.js Frontend and a FastAPI Backend powered by MongoDB Atlas. The backend processes long-running agentic tasks utilizing a multi-node Graph state machine.

### Frontend
- **Framework:** Next.js (App Router)
- **Styling:** Tailwind CSS + Radix UI components
- **Routing:** Standard Next.js navigation (`useRouter`, `useSearchParams`). Navigation is strictly passed via `jdId` to maintain Context across the 4 major application stages.

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** MongoDB Atlas (NoSQL Document Store)
- **AI/LLM:** LangGraph state machines for orchestration. Direct integrations with OpenAI APIs.
- **Embeddings:** `sentence-transformers` for calculating semantic candidate-to-JD fit natively without relying on heavy external vector databases.

## MongoDB Document Model

The application operates on primarily two collections:

**1. `threads` (Feature 1)**
- Contains the Job Description data, `role_brief`, LLM chat history, and configuration states.
- Re-used heavily by pipeline components as the baseline for skills and requirements.

**2. `sourcing_candidates` (Features 2, 3, 4)**
- Unified document model. Instead of moving candidates to different tables as they progress, we maintain a single large document for each candidate.
- We mutate the `status` enum string (`pending`, `shortlisted`, `contacted`, `responded`, `evaluated`, `offered`).
- Extended fields like `evaluation` and `decision` dictionaries are appended to the document as the candidate moves through the pipeline.
