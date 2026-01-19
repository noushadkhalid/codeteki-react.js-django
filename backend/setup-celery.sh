#!/bin/bash
# ============================================
# Celery Setup Script for Codeteki Server
# Run this script on your server to set up Celery with Redis
#
# Usage: sudo bash setup-celery.sh
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/home/codeteki/codeteki-react.js-django"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${YELLOW}=== Codeteki Celery Setup ===${NC}"

# 1. Install Redis
echo -e "\n${YELLOW}Installing Redis...${NC}"
apt update
apt install -y redis-server

# Enable and start Redis
systemctl enable redis-server
systemctl start redis-server

# Verify Redis is running
if redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis failed to start${NC}"
    exit 1
fi

# 2. Install Python dependencies
echo -e "\n${YELLOW}Installing Python packages...${NC}"
cd $PROJECT_DIR
source $VENV_DIR/bin/activate
pip install celery redis django-celery-results django-celery-beat

# 3. Run Django migrations
echo -e "\n${YELLOW}Running migrations...${NC}"
cd $BACKEND_DIR
python manage.py migrate django_celery_results
python manage.py migrate django_celery_beat
python manage.py migrate

# 4. Create directories for Celery
echo -e "\n${YELLOW}Creating Celery directories...${NC}"
mkdir -p /var/log/celery
mkdir -p /var/run/celery
chown -R codeteki:codeteki /var/log/celery
chown -R codeteki:codeteki /var/run/celery

# 5. Create Celery Worker service
echo -e "\n${YELLOW}Creating Celery Worker service...${NC}"
cat > /etc/systemd/system/celery-worker.service << 'EOF'
[Unit]
Description=Celery Worker for Codeteki
After=network.target redis-server.service

[Service]
Type=forking
User=codeteki
Group=codeteki
WorkingDirectory=/home/codeteki/codeteki-react.js-django/backend
Environment="PATH=/home/codeteki/codeteki-react.js-django/venv/bin"
ExecStart=/home/codeteki/codeteki-react.js-django/venv/bin/celery \
    -A codeteki_site worker \
    --loglevel=info \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid \
    --detach
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=10
RuntimeDirectory=celery
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
EOF

# 6. Create Celery Beat service
echo -e "\n${YELLOW}Creating Celery Beat service...${NC}"
cat > /etc/systemd/system/celerybeat.service << 'EOF'
[Unit]
Description=Celery Beat Scheduler for Codeteki
After=network.target redis-server.service

[Service]
Type=forking
User=codeteki
Group=codeteki
WorkingDirectory=/home/codeteki/codeteki-react.js-django/backend
Environment="PATH=/home/codeteki/codeteki-react.js-django/venv/bin"
ExecStart=/home/codeteki/codeteki-react.js-django/venv/bin/celery \
    -A codeteki_site beat \
    --loglevel=info \
    --logfile=/var/log/celery/beat.log \
    --pidfile=/var/run/celery/beat.pid \
    --detach
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 7. Enable and start services
echo -e "\n${YELLOW}Enabling and starting services...${NC}"
systemctl daemon-reload
systemctl enable celery-worker
systemctl enable celerybeat
systemctl start celery-worker
systemctl start celerybeat

# 8. Check if services are running
sleep 2
echo ""
if systemctl is-active --quiet celery-worker; then
    echo -e "${GREEN}✓ Celery worker is running${NC}"
else
    echo -e "${RED}✗ Celery worker failed to start${NC}"
    echo "   Check logs: journalctl -u celery-worker -f"
fi

if systemctl is-active --quiet celerybeat; then
    echo -e "${GREEN}✓ Celery beat is running${NC}"
else
    echo -e "${RED}✗ Celery beat failed to start${NC}"
    echo "   Check logs: journalctl -u celerybeat -f"
fi

echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status celery-worker   # Check worker status"
echo "  sudo systemctl status celerybeat      # Check beat status"
echo "  sudo systemctl restart celery-worker  # Restart worker"
echo "  sudo systemctl restart celerybeat     # Restart beat"
echo "  sudo journalctl -u celery-worker -f   # View worker logs"
echo "  tail -f /var/log/celery/worker.log    # View Celery logs"
echo ""
