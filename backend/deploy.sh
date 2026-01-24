#!/bin/bash

# ============================================
# Codeteki Deployment Script
# Run this when pulling new code
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/home/codeteki/codeteki-react.js-django"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

cd $PROJECT_DIR

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Codeteki Deployment${NC}"
echo -e "${YELLOW}========================================${NC}"

echo -e "\n${YELLOW}Pulling latest code...${NC}"
git fetch origin
git reset --hard origin/main
echo -e "${GREEN}✓ Code updated${NC}"

echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
cd $BACKEND_DIR
pip install -r requirements.txt --quiet

echo -e "\n${YELLOW}Running migrations...${NC}"
python manage.py migrate --noinput

echo -e "\n${YELLOW}Building frontend...${NC}"
cd $PROJECT_DIR/frontend
npm install --silent
npm run build
echo -e "${GREEN}✓ Frontend built${NC}"

echo -e "\n${YELLOW}Collecting static files...${NC}"
cd $BACKEND_DIR
python manage.py collectstatic --noinput --verbosity 0

# ============================================
# RESTART SERVICES
# ============================================
echo -e "\n${YELLOW}Restarting services...${NC}"

# Check Redis is running (don't restart - would clear cache)
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}Redis not responding, starting...${NC}"
    sudo systemctl start redis-server
fi

# Restart application services
sudo systemctl restart gunicorn
sudo systemctl restart celery-worker
sudo systemctl restart celerybeat 2>/dev/null || true
sudo systemctl reload nginx

# ============================================
# STATUS CHECK
# ============================================
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo ""

# Check services
for service in gunicorn celery-worker nginx; do
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓ $service running${NC}"
    else
        echo -e "${RED}✗ $service not running${NC}"
    fi
done

# Check Celerybeat (optional)
if systemctl is-active --quiet celerybeat 2>/dev/null; then
    echo -e "${GREEN}✓ celerybeat running${NC}"
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ redis running${NC}"
else
    echo -e "${RED}✗ redis not responding${NC}"
fi

echo ""
echo -e "${GREEN}Site: https://codeteki.au${NC}"
