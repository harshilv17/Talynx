# ATA Deployment Guide

This guide covers deploying the ATA Feature 1 application to production.

## Overview

- **Backend**: FastAPI (Python) + LangGraph + MongoDB
- **Frontend**: Next.js
- **Database**: MongoDB (Atlas free tier works great)

MongoDB makes deployment easy: no migrations, no Docker, no PostgreSQL setup. Use MongoDB Atlas for a free hosted database.

---

## Quick Start (Railway + MongoDB Atlas – ~10 min)

1. **Create MongoDB Atlas** (free):
   - Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
   - Create a free cluster
   - Create a database user, get the connection string
   - Add your IP (or `0.0.0.0/0` for Railway) to Network Access

2. Push your code to GitHub

3. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub

4. Add **two services** from the same repo:
   - **Backend**: Root dir `backend`, add:
     - `OPENAI_API_KEY` = your key
     - `MONGODB_URI` = your Atlas connection string (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/`)
     - `MONGODB_DB_NAME` = `ata`
     - `CORS_ORIGINS` = your frontend URL (add after you have it)
   - **Frontend**: Root dir `frontend`, add `NEXT_PUBLIC_API_URL` (your backend URL)

5. Generate domains for both, then set `CORS_ORIGINS` and `NEXT_PUBLIC_API_URL` to those URLs

6. Redeploy if needed

---

## Option 1: Railway (Recommended)

### Backend
- **Root Directory**: `backend`
- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Env**: `OPENAI_API_KEY`, `MONGODB_URI`, `MONGODB_DB_NAME`, `CORS_ORIGINS`

### Frontend
- **Root Directory**: `frontend`
- **Build**: `npm install && npm run build`
- **Start**: `npm start`
- **Env**: `NEXT_PUBLIC_API_URL`

---

## Option 2: Render

### Backend
1. New → Web Service
2. Root Directory: `backend`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Env: `OPENAI_API_KEY`, `MONGODB_URI`, `MONGODB_DB_NAME`, `CORS_ORIGINS`

### Frontend
1. New → Web Service
2. Root Directory: `frontend`
3. Build: `npm install && npm run build`
4. Start: `npm start`
5. Env: `NEXT_PUBLIC_API_URL`

---

## Option 3: Vercel (Frontend) + Railway (Backend)

Vercel hosts the frontend only. Backend must run on Railway, Render, or similar.

### Backend (Railway)
- `OPENAI_API_KEY`, `MONGODB_URI`, `MONGODB_DB_NAME`
- `CORS_ORIGINS` = your Vercel URL (e.g. `https://ata-frontend.vercel.app`)

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` = your Railway backend URL

---

## MongoDB Atlas Setup

1. Create account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a free M0 cluster
3. Database Access → Add User → create username/password
4. Network Access → Add IP Address → allow `0.0.0.0/0` for cloud deploys (or your Railway IP)
5. Connect → Drivers → copy connection string
6. Replace `<password>` with your user password
7. Use as `MONGODB_URI` (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority`)

No migrations needed. Collections (`role_briefs`, `job_descriptions`, `sourcing_queue`, `checkpoints`, `checkpoint_writes`) are created automatically.

---

## Environment Variables

| Variable | Backend | Frontend | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | ❌ | Your OpenAI API key |
| `MONGODB_URI` | ✅ | ❌ | MongoDB connection string (Atlas or local) |
| `MONGODB_DB_NAME` | ✅ | ❌ | Database name (default: `ata`) |
| `CORS_ORIGINS` | ✅ | ❌ | Comma-separated frontend URLs |
| `NEXT_PUBLIC_API_URL` | ❌ | ✅ | Full backend URL |

---

## Local Development

1. Copy `.env.example` to `.env`
2. Set `OPENAI_API_KEY`
3. Run MongoDB locally (`mongod`) or use Atlas
4. `./start-backend.sh` and `./start-frontend.sh`

---

## Checklist Before Deploy

- [ ] Push code to GitHub
- [ ] Create MongoDB Atlas cluster and get connection string
- [ ] Add `OPENAI_API_KEY` and `MONGODB_URI` to backend
- [ ] Set `NEXT_PUBLIC_API_URL` on frontend
- [ ] Update `CORS_ORIGINS` with frontend URL
- [ ] Test the full flow after deploy
