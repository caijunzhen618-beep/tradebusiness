#!/usr/bin/env bash
# TradeBusiness - Ubuntu/Linux 停止脚本

set -Eeuo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$PROJECT_ROOT"

stop_pid_file() {
    local label="$1"
    local pid_file="$2"
    if [ ! -f "$pid_file" ]; then
        return 0
    fi

    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
        echo "Stopping $label (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
}

echo "Stopping TradeBusiness services..."
stop_pid_file "backend" "$PROJECT_ROOT/.backend_pid"
stop_pid_file "celery worker" "$PROJECT_ROOT/.celery_worker_pid"
stop_pid_file "celery beat" "$PROJECT_ROOT/.celery_beat_pid"
stop_pid_file "admin" "$PROJECT_ROOT/.admin_pid"
stop_pid_file "client" "$PROJECT_ROOT/.client_pid"

# Vite/uvicorn --reload 会产生子进程，按命令特征补充清理。
pkill -f "$PROJECT_ROOT/tradebusiness-backend.*uvicorn app.main:app" 2>/dev/null || true
pkill -f "$PROJECT_ROOT/tradebusiness-admin.*vite" 2>/dev/null || true
pkill -f "$PROJECT_ROOT/tradebusiness-client.*vite" 2>/dev/null || true
pkill -f "celery -A app.tasks.automation_tasks:celery_app" 2>/dev/null || true

if command -v lsof >/dev/null 2>&1; then
    for port in 8000 3000 3001; do
        lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | xargs -r kill 2>/dev/null || true
    done
fi

echo "All TradeBusiness services stopped."
