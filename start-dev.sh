#!/bin/bash
# Development Mode Startup - TradeBusiness (Linux/Mac)
# Starts services with hot-reload and debug mode

echo ""
echo "========================================"
echo "  Starting Dev Environment"
echo "========================================"
echo ""

# Create logs directory
mkdir -p logs

# Start backend with debug mode
echo "[1/3] Starting Backend (Debug Mode)..."
cd tradebusiness-backend
source venv/bin/activate 2>/dev/null || {
    echo "Creating venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -q
}
export DEBUG=True
export PYTHONPATH=.
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../.backend_pid
echo "Backend started (PID: $BACKEND_PID)"
cd ..

sleep 3

# Start admin frontend
echo "[2/3] Starting Admin Frontend (Dev Mode)..."
if [ -d "tradebusiness-admin" ]; then
    cd tradebusiness-admin
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    nohup npm run dev > ../logs/admin.log 2>&1 &
    ADMIN_PID=$!
    echo $ADMIN_PID > ../.admin_pid
    echo "Admin started (PID: $ADMIN_PID)"
    cd ..
    sleep 2
fi

# Start client frontend
echo "[3/3] Starting Client Frontend (Dev Mode)..."
if [ -d "tradebusiness-client" ]; then
    cd tradebusiness-client
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    nohup npm run dev > ../logs/client.log 2>&1 &
    CLIENT_PID=$!
    echo $CLIENT_PID > ../.client_pid
    echo "Client started (PID: $CLIENT_PID)"
    cd ..
fi

echo ""
echo "========================================"
echo "  Dev Environment Ready!"
echo "========================================"
echo ""
echo "Services running:"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/docs"
echo "  Admin Frontend:  http://localhost:3000"
echo "  Client Frontend: http://localhost:3001"
echo ""
echo "Debug features enabled:"
echo "  - Hot reload: ON"
echo "  - Debug logs: ON"
echo "  - API docs:   ON"
echo ""
echo "Logs:"
tail -f logs/backend.log &
TAIL_PID=$!
trap "kill $TAIL_PID 2>/dev/null" EXIT
