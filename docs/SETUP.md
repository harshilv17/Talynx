# Setup & Installation

## Prerequisites
- Docker Desktop
- OpenAI API Key

## Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=sk-your-openai-key
DATABASE_URL=postgresql://ata_user:ata_password@localhost:5432/ata_db
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
MONGODB_DB_NAME=ata
CORS_ORIGINS=http://localhost:3000
```
For the frontend, create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Project

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```
This starts PostgreSQL, the FastAPI backend (port 8000), and the Next.js frontend (port 3000).

### Option 2: Manual Local Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Accessing Services
- **Frontend App**: `http://localhost:3000`
- **Backend API Docs**: `http://localhost:8000/docs`
