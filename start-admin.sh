#!/bin/bash
# Start Admin Frontend (Linux/Mac)

echo "Starting Admin Frontend..."

cd tradebusiness-admin || exit 1

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start admin
echo "Starting on http://localhost:3000"
npm run dev
