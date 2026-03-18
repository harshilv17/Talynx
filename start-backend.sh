#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# ── Validate .env ─────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "❌  .env not found. Copy .env.example and add your OPENAI_API_KEY."
  exit 1
fi
source .env
if [[ "$OPENAI_API_KEY" == *"your-openai"* ]] || [ -z "$OPENAI_API_KEY" ]; then
  echo "❌  Please set a real OPENAI_API_KEY in .env"
  exit 1
fi

# ── Python venv ───────────────────────────────────────────────────────────────
PYTHON_BIN="/opt/homebrew/opt/python@3.13/bin/python3.13"
if [ ! -f "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

if [ ! -d "venv" ]; then
  echo "→ Creating Python virtual environment..."
  "$PYTHON_BIN" -m venv venv
fi
source venv/bin/activate

# ── Dependencies ──────────────────────────────────────────────────────────────
echo "→ Checking Python dependencies..."
pip install -r backend/requirements.txt -q

# ── Start ─────────────────────────────────────────────────────────────────────
echo ""
echo "✅  Backend starting at  http://localhost:8000"
echo "    API docs:            http://localhost:8000/docs"
echo ""
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
