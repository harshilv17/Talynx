# Setup & Installation

Follow these steps to configure and run the Autonomous Talent Acquisition (ATA) system locally.

## Prerequisites
- Node.js (v18+)
- Python 3.10+
- MongoDB Atlas account (or local MongoDB)

## 1. Environment Configuration

### Backend
Create a `.env` file in the `backend` directory based on `.env.example`:

```env
# backend/.env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=talynx_db
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
CORS_ORIGINS=http://localhost:3000
```

### Frontend
Create a `.env.local` or `.env` file in the `frontend` directory:

```env
# frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 2. Backend Setup
Navigate to the `backend` directory and install the Python requirements:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Run the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

## 3. Frontend Setup
Navigate to the `frontend` directory and install the Node dependencies:

```bash
cd frontend
npm install
```

Run the Next.js development server:
```bash
npm run dev
```

Visit `http://localhost:3000` to start using the system.
