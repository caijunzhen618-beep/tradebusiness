#!/usr/bin/env bash
# Restart Backend Service (Linux/Mac)

set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$ROOT"

echo "Restarting Backend Service..."

# Stop backend
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid 2>/dev/null || true)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm -f .backend_pid
fi

pkill -f "uvicorn app.main:app" 2>/dev/null || true

sleep 2

# Start backend
echo "Starting backend..."
cd "$ROOT/tradebusiness-backend" || exit 1
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Python virtual environment not found"
    exit 1
fi
source venv/bin/activate
mkdir -p logs
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$ROOT/logs/backend.log" 2>&1 < /dev/null &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$ROOT/.backend_pid"

sleep 2

# Check if started
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "Backend restarted successfully (PID: $BACKEND_PID)"
else
    echo "Error: Backend failed to start"
    tail -20 "$ROOT/logs/backend.log"
    exit 1
fi
