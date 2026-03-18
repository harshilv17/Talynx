#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/frontend"

if [ ! -d "node_modules" ]; then
  echo "→ Installing npm dependencies..."
  npm install
fi

echo ""
echo "✅  Frontend starting at http://localhost:3000"
echo ""
npm run dev
