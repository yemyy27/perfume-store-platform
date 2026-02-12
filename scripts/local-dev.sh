#!/bin/bash
# =============================================================================
# Perfume Store Platform - Local Development Runner
# Starts all microservices + frontend on localhost
# =============================================================================

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PIDS=()

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down all services...${NC}"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait 2>/dev/null
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Perfume Store - Local Development     ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# --- Step 1: Create virtual environment if needed ---
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# --- Step 2: Install dependencies ---
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --quiet --upgrade pip

# Combine all requirements
pip install --quiet \
    "fastapi==0.104.1" \
    "uvicorn[standard]==0.24.0" \
    "pydantic==2.5.0" \
    "pydantic[email]==2.5.0" \
    "pyjwt==2.8.0" \
    "bcrypt==4.1.2" \
    "python-multipart==0.0.6" \
    "httpx==0.25.2" \
    "sqlalchemy==2.0.23"

echo -e "${GREEN}Dependencies installed.${NC}"
echo ""

# --- Step 3: Set environment variables ---
export JWT_SECRET_KEY="local-dev-secret-key-not-for-production"
export CORS_ORIGINS="http://localhost:8080,http://localhost:3000,http://127.0.0.1:8080"
export PRODUCT_SERVICE_URL="http://localhost:8001"
export USER_SERVICE_URL="http://localhost:8003"

# --- Step 4: Start Product Service (port 8001) ---
echo -e "${CYAN}Starting Product Service on port 8001...${NC}"
PORT=8001 python3 "$ROOT_DIR/applications/product-service/main.py" &
PIDS+=($!)

# --- Step 5: Start User Service (port 8003) ---
echo -e "${CYAN}Starting User Service on port 8003...${NC}"
PORT=8003 python3 "$ROOT_DIR/applications/user-service/main.py" &
PIDS+=($!)

# Short wait for services to be ready before starting order service
sleep 2

# --- Step 6: Start Order Service (port 8002) ---
echo -e "${CYAN}Starting Order Service on port 8002...${NC}"
PORT=8002 python3 "$ROOT_DIR/applications/order-service/main.py" &
PIDS+=($!)

# --- Step 7: Start Frontend (port 8080) ---
echo -e "${CYAN}Starting Frontend on port 8080...${NC}"
cd "$ROOT_DIR/frontend-oud"
python3 -m http.server 8080 --bind 0.0.0.0 &
PIDS+=($!)
cd "$ROOT_DIR"

# --- Wait for everything to start ---
sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All services running!                 ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "  Frontend:         ${CYAN}http://localhost:8080${NC}"
echo -e "  Product Service:  ${CYAN}http://localhost:8001${NC}  (docs: http://localhost:8001/docs)"
echo -e "  User Service:     ${CYAN}http://localhost:8003${NC}  (docs: http://localhost:8003/docs)"
echo -e "  Order Service:    ${CYAN}http://localhost:8002${NC}  (docs: http://localhost:8002/docs)"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for all background processes
wait
