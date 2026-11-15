#!/bin/bash
# Ironory — Local Development Launcher
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Starting Ironory Local Development Services ==="
cd "$ROOT_DIR"

# Ensure venv exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment in .venv..."
    /opt/homebrew/bin/python3.11 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r backend/requirements.txt
fi

# Apply migrations
echo "Applying database migrations..."
.venv/bin/alembic -c backend/alembic.ini upgrade head

# Start Backend API
echo "Starting Backend API on http://localhost:8000..."
.venv/bin/uvicorn backend.app.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# Start Frontend Next.js
echo "Starting Next.js Frontend on http://localhost:3000..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Stopping Ironory services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Ironory is active!"
echo "-> Frontend: http://localhost:3000"
echo "-> Backend API: http://localhost:8000"
echo "-> Interactive API Docs: http://localhost:8000/api/v1/docs"
echo "Press Ctrl+C to terminate."

wait
