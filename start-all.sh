#!/usr/bin/env bash
# TradeBusiness - Ubuntu/Linux 一键启动脚本

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/tradebusiness-backend"
ADMIN_DIR="$PROJECT_ROOT/tradebusiness-admin"
CLIENT_DIR="$PROJECT_ROOT/tradebusiness-client"
LOG_DIR="$PROJECT_ROOT/logs"

cd "$PROJECT_ROOT"

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_port() {
    local port="$1"
    if command_exists ss; then
        ss -ltn "sport = :$port" 2>/dev/null | grep -q ":$port"
    elif command_exists lsof; then
        lsof -nP -iTCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1
    else
        echo "WARNING: ss/lsof 未安装，跳过端口 $port 检查" >&2
        return 1
    fi
}

check_dir() {
    [ -d "$1" ] || fail "目录不存在：$1"
}

start_service() {
    local name="$1"
    local workdir="$2"
    local logfile="$3"
    shift 3

    echo "Starting $name..."
    (
        cd "$workdir"
        nohup "$@" >>"$logfile" 2>&1 < /dev/null &
        echo $! > "$PROJECT_ROOT/.${name,,}_pid"
    )
}

start_backend_service() {
    local name="$1"
    local logfile="$2"
    shift 2
    echo "Starting $name..."
    cd "$BACKEND_DIR"
    nohup "$@" >>"$logfile" 2>&1 < /dev/null &
    echo $! > "$PROJECT_ROOT/.${name,,}_pid"
    cd "$PROJECT_ROOT"
}

echo ""
echo "========================================"
echo " TradeBusiness - Starting All Services"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo ""

check_dir "$BACKEND_DIR"
check_dir "$ADMIN_DIR"
check_dir "$CLIENT_DIR"
command_exists python3 || fail "未找到 Python 3，请先安装 python3 和 python3-venv"
command_exists node || fail "未找到 Node.js，请先安装 Node.js 18+"
command_exists npm || fail "未找到 npm，请先安装 npm"

echo "Python: $(python3 --version)"
echo "Node:   $(node --version)"
echo "npm:    $(npm --version)"

echo ""
echo "[1/4] Preparing backend..."
cd "$BACKEND_DIR"
if [ ! -f "venv/bin/activate" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv || fail "创建 Python 虚拟环境失败，请安装 python3-venv"
fi
source venv/bin/activate
if [ ! -f "requirements.txt" ]; then
    fail "未找到 $BACKEND_DIR/requirements.txt"
fi
if [ "${INSTALL_DEPS:-0}" = "1" ] || [ ! -f "venv/.tradebusiness_requirements_ready" ]; then
    echo "Installing backend dependencies..."
    python -m pip install -r requirements.txt || fail "后端依赖安装失败"
    touch venv/.tradebusiness_requirements_ready
else
    echo "Backend dependencies already prepared (如需重新安装，请执行 INSTALL_DEPS=1 ./start-all.sh)"
fi

echo ""
echo "[2/4] Preparing frontends..."
if [ "${INSTALL_DEPS:-0}" = "1" ] || [ ! -d "$ADMIN_DIR/node_modules" ]; then
    (cd "$ADMIN_DIR" && npm install) || fail "管理端依赖安装失败"
else
    echo "Admin frontend dependencies already installed"
fi
if [ "${INSTALL_DEPS:-0}" = "1" ] || [ ! -d "$CLIENT_DIR/node_modules" ]; then
    (cd "$CLIENT_DIR" && npm install) || fail "客户端依赖安装失败"
else
    echo "Client frontend dependencies already installed"
fi

echo ""
echo "[3/5] Checking ports..."
for port in 8000 3000 3001; do
    if check_port "$port"; then
        fail "端口 $port 已被占用，请先执行 ./stop-all.sh，或手动停止占用该端口的进程"
    fi
done

echo ""
echo "[4/5] Building production frontends..."
(cd "$ADMIN_DIR" && npm run build -- --mode production) || fail "管理端生产构建失败"
(cd "$CLIENT_DIR" && npm run build -- --mode production) || fail "客户端生产构建失败"

echo ""
echo "[5/5] Starting production services..."
mkdir -p "$LOG_DIR"

rm -f "$PROJECT_ROOT/.backend_pid" "$PROJECT_ROOT/.celery_worker_pid" \
    "$PROJECT_ROOT/.celery_beat_pid" "$PROJECT_ROOT/.admin_pid" "$PROJECT_ROOT/.client_pid"

if [ ! -f "$BACKEND_DIR/.env" ]; then
    fail "未找到 $BACKEND_DIR/.env，请先配置正式环境变量"
fi

source "$BACKEND_DIR/venv/bin/activate"
start_backend_service "backend" "$LOG_DIR/backend.log" \
    "$BACKEND_DIR/venv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
start_backend_service "celery_worker" "$LOG_DIR/celery-worker.log" \
    "$BACKEND_DIR/venv/bin/celery" -A app.tasks.automation_tasks:celery_app worker --loglevel=info --concurrency="${CELERY_CONCURRENCY:-4}"
start_backend_service "celery_beat" "$LOG_DIR/celery-beat.log" \
    "$BACKEND_DIR/venv/bin/celery" -A app.tasks.automation_tasks:celery_app beat --loglevel=info

start_service "admin" "$ADMIN_DIR" "$LOG_DIR/admin.log" npm run preview -- --host 0.0.0.0 --port 3000
start_service "client" "$CLIENT_DIR" "$LOG_DIR/client.log" npm run preview -- --host 0.0.0.0 --port 3001

sleep 2

echo ""
echo "========================================"
echo " All Services Started Successfully!"
echo "========================================"
echo "Backend API:     http://localhost:8000"
echo "API docs:        http://localhost:8000/docs"
echo "Admin Frontend:  http://localhost:3000"
echo "Client Frontend: http://localhost:3001"
echo ""
echo "Logs: $LOG_DIR/backend.log, $LOG_DIR/celery-worker.log, $LOG_DIR/celery-beat.log"
echo "      $LOG_DIR/admin.log, $LOG_DIR/client.log"
echo "Stop: ./stop-all.sh"
echo ""
