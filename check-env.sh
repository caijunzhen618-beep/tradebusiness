#!/usr/bin/env bash
# Environment Check Script (Linux/Mac)

set -u

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$ROOT"

echo ""
echo "========================================"
echo "  Environment Check"
echo "========================================"
echo ""

PASS=0
FAIL=0

# Function to check command
check_cmd() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "  ✓ $1: $(command -v "$1")"
        ((PASS++))
        return 0
    else
        echo "  ✗ $1: NOT FOUND"
        ((FAIL++))
        return 1
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo "  ✓ $1 exists"
        ((PASS++))
        return 0
    else
        echo "  ✗ $1 missing"
        ((FAIL++))
        return 1
    fi
}

# Function to check directory
check_dir() {
    if [ -d "$1" ]; then
        echo "  ✓ $1 exists"
        ((PASS++))
        return 0
    else
        echo "  ✗ $1 missing"
        ((FAIL++))
        return 1
    fi
}

echo "[System Requirements]"
check_cmd python3
check_cmd node
check_cmd npm
check_cmd git
echo ""

echo "[Backend Dependencies]"
if cd "$ROOT/tradebusiness-backend" 2>/dev/null; then
    check_file "requirements.txt"
    check_dir "venv"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        check_cmd pip
    fi
else
    echo "  ✗ tradebusiness-backend missing"
    ((FAIL++))
fi
cd "$ROOT"
echo ""

echo "[Frontend Dependencies]"
check_dir "tradebusiness-admin/node_modules"
check_dir "tradebusiness-client/node_modules"
echo ""

echo "[Configuration Files]"
check_file "tradebusiness-backend/.env"
check_file "tradebusiness-admin/.env"
check_file "tradebusiness-client/.env"
echo ""

echo "[Database]"
if [ -f "$ROOT/tradebusiness-backend/.env" ]; then
    DB_URL=$(grep -E '^DATABASE_URL=' "$ROOT/tradebusiness-backend/.env" | cut -d'=' -f2-)
    if [ -n "$DB_URL" ]; then
        echo "  ✓ DATABASE_URL configured"
        ((PASS++))
    else
        echo "  ✗ DATABASE_URL not found"
        ((FAIL++))
    fi
fi
echo ""

echo "========================================"
echo "  Check Complete"
echo "========================================"
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ Environment is ready!"
    exit 0
else
    echo "✗ Some checks failed"
    echo "Run ./create-env.sh to create missing files"
    exit 1
fi
