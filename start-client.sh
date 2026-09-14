#!/bin/bash
# Start Client Frontend (Linux/Mac)

echo "Starting Client Frontend..."

cd tradebusiness-client || exit 1

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start client
echo "Starting on http://localhost:3001"
npm run dev
