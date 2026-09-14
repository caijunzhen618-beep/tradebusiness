#!/bin/bash
# Clean project cache and temporary files (Linux/Mac version)

echo ""
echo "========================================"
echo "  Clean Project Cache Files"
echo "========================================"
echo ""

echo "[1/5] Cleaning Python cache..."
find tradebusiness-backend/app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "Python cache cleaned"

echo ""
echo "[2/5] Cleaning frontend cache..."
rm -rf tradebusiness-admin/node_modules/.vite 2>/dev/null
rm -rf tradebusiness-client/node_modules/.vite 2>/dev/null
echo "Frontend cache cleaned"

echo ""
echo "[3/5] Cleaning log files..."
if [ -d "tradebusiness-backend/logs" ]; then
    rm -f tradebusiness-backend/logs/*.log 2>/dev/null
    echo "Log files cleaned"
else
    echo "No log files found"
fi

echo ""
echo "[4/5] Cleaning temporary files..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.bak" -delete 2>/dev/null
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null
echo "Temporary files cleaned"

echo ""
echo "[5/5] Cleaning Python cache directories..."
find . -type d -name "__pycache__" -delete 2>/dev/null
echo "Python cache directories cleaned"

echo ""
echo "========================================"
echo "  Cleanup Complete!"
echo "========================================"
echo ""
echo "Note: node_modules folders are preserved"
echo "For full cleanup, manually delete:"
echo "  - tradebusiness-admin/node_modules"
echo "  - tradebusiness-client/node_modules"
echo "  - tradebusiness-backend/venv"
echo ""
