# System Architecture

## Overview
ATA is a microservices-style monolithic app separating a pure Python backend from a React frontend.

## Components

### Backend (FastAPI + LangGraph)
- **Role**: Pure API logic, AI orchestration, database interaction.
- **Database**: PostgreSQL (for Relational data and LangGraph checkpointer state) & MongoDB (for document-based Candidate ATS tracking).
- **AI/Agents**: Uses LangGraph to manage complex human-in-the-loop workflows (Feature 1 JD Generation) with `sentence-transformers` for embedding vectorization.

### Frontend (Next.js)
- **Role**: User Interface and state management.
- **Structure**: Next.js App Router (`app/`).
- **Styling**: TailwindCSS & shadcn/ui.
- **Logic**: No direct database access; strictly consumes REST APIs from the backend.

## Data Flow
1. **Client UI** -> **FastAPI Router** -> **LangGraph / DB Services** -> **MongoDB / Postgres**
2. Results returned as JSON to the Client UI.
