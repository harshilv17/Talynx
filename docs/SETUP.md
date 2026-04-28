# Setup & Installation

## Environment Variables
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
MONGO_DB_NAME=ata
CORS_ORIGINS=http://localhost:3000
```

Create a `.env.local` file in the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`

## Running the Project
### Terminal 1 (Backend)
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Terminal 2 (Frontend)
```bash
cd frontend
npm run dev
```

The frontend will be accessible at `http://localhost:3000` and the API docs at `http://localhost:8000/docs`.
