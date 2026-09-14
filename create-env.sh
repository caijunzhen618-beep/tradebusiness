#!/usr/bin/env bash
# Create Environment Files (Linux/Mac)

set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$ROOT"

echo ""
echo "========================================"
echo "  Create Environment Configuration"
echo "========================================"
echo ""

# Function to create .env from template
create_env() {
    local ENV_FILE="$1"
    local TEMPLATE="$2"

    if [ -f "$ENV_FILE" ]; then
        echo "  ✓ $ENV_FILE already exists, skipping"
        return 0
    fi

    if [ -f "$TEMPLATE" ]; then
        cp "$TEMPLATE" "$ENV_FILE"
        echo "  ✓ Created $ENV_FILE from template"
    else
        echo "  ⚠ No template found for $ENV_FILE"
    fi
}

echo "[1/4] Backend Environment"
cd "$ROOT/tradebusiness-backend"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  ✓ Created .env from .env.example"
    else
        cat > .env << 'ENVFILE'
# Application
APP_NAME=TradeBusiness API
APP_VERSION=0.1.0
DEBUG=true
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Database (MySQL 8.0)
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/tradebusiness?charset=utf8mb4
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Email (configure with your settings)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM=your-email@example.com
SMTP_FROM_NAME=TradeBusiness
ENVFILE
        echo "  ✓ Created .env with defaults"
    fi
else
    echo "  ✓ .env already exists"
fi
cd "$ROOT"

echo ""
echo "[2/4] Admin Frontend Environment"
cd "$ROOT/tradebusiness-admin"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  ✓ Created .env from .env.example"
    else
        cat > .env << 'ENVFILE'
# API Base URL
VITE_APP_BASE_API=http://localhost:8000
VITE_APP_TITLE=TradeBusiness Admin

# Other configuration
VITE_APP_PORT=3000
ENVFILE
        echo "  ✓ Created .env with defaults"
    fi
else
    echo "  ✓ .env already exists"
fi
cd "$ROOT"

echo ""
echo "[3/4] Client Frontend Environment"
cd "$ROOT/tradebusiness-client"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  ✓ Created .env from .env.example"
    else
        cat > .env << 'ENVFILE'
# API Base URL
VITE_APP_BASE_API=http://localhost:8000
VITE_APP_TITLE=TradeBusiness Client

# Other configuration
VITE_APP_PORT=3001
ENVFILE
        echo "  ✓ Created .env with defaults"
    fi
else
    echo "  ✓ .env already exists"
fi
cd "$ROOT"

echo ""
echo "[4/4] Logs Directory"
mkdir -p tradebusiness-backend/logs
echo "  ✓ Created logs directory"

echo ""
echo "========================================"
echo "  Configuration Complete!"
echo "========================================"
echo ""
echo "Created files:"
echo "  - tradebusiness-backend/.env"
echo "  - tradebusiness-admin/.env"
echo "  - tradebusiness-client/.env"
echo "  - tradebusiness-backend/logs/"
echo ""
echo "IMPORTANT:"
echo "  1. Update DATABASE_URL in tradebusiness-backend/.env"
echo "  2. Update SMTP settings in tradebusiness-backend/.env"
echo "  3. Update SECRET_KEY and JWT_SECRET_KEY"
echo ""
echo "Run ./check-env.sh to verify configuration"
echo ""
