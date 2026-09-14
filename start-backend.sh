#!/bin/bash
# Start Backend API Server (Linux/Mac)

echo "Starting Backend API..."

cd tradebusiness-backend || exit 1

# Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start backend
echo "Starting on http://localhost:8000"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
