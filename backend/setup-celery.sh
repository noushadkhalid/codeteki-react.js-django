#!/bin/bash
# Celery Setup Script for Codeteki Server
# Run this script on your server to set up Celery with Redis
#
# Usage: sudo bash setup-celery.sh

set -e

echo "=== Codeteki Celery Setup ==="

# 1. Install Redis
echo "Installing Redis..."
apt update
apt install -y redis-server

# Enable and start Redis
systemctl enable redis-server
systemctl start redis-server

# Verify Redis is running
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# 2. Install Python dependencies (run in your virtualenv)
echo "Installing Python packages..."
cd /var/www/codeteki
source .venv/bin/activate
pip install celery redis django-celery-results

# 3. Run Django migrations for celery results
echo "Running migrations..."
cd backend
python manage.py migrate django_celery_results
python manage.py migrate

# 4. Create directories for Celery
echo "Creating Celery directories..."
mkdir -p /var/log/celery
mkdir -p /var/run/celery
chown -R www-data:www-data /var/log/celery
chown -R www-data:www-data /var/run/celery

# 5. Install systemd service
echo "Installing Celery systemd service..."
cp celery-worker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable celery-worker
systemctl start celery-worker

# Check if Celery is running
sleep 2
if systemctl is-active --quiet celery-worker; then
    echo "✅ Celery worker is running"
else
    echo "❌ Celery worker failed to start. Check logs:"
    echo "   journalctl -u celery-worker -f"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Useful commands:"
echo "  sudo systemctl status celery-worker   # Check status"
echo "  sudo systemctl restart celery-worker  # Restart worker"
echo "  sudo journalctl -u celery-worker -f   # View logs"
echo "  tail -f /var/log/celery/worker.log    # View Celery logs"
echo ""
echo "Now you can run Site Audits from Django Admin without timeouts!"
