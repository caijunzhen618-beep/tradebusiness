#!/usr/bin/env bash
# Authorization Fix Verification Script
# Run this to test if the authorization fixes are working

set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$ROOT"

echo "============================================================"
echo "Authorization Fix Verification"
echo "============================================================"
echo ""

echo "Checking if Python is available..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ to run this verification script"
    exit 1
fi

echo ""
echo "Running verification tests..."
echo ""

python3 "$ROOT/scripts/verify_auth_fix.py"

echo ""
