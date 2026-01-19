# Codeteki Server Configuration Reference

## Server Details

| Setting | Value |
|---------|-------|
| Domain | codeteki.au |
| Server | Ubuntu (DigitalOcean/AWS) |
| User | codeteki |
| Project Path | `/home/codeteki/codeteki-react.js-django` |
| Backend Path | `/home/codeteki/codeteki-react.js-django/backend` |
| Virtualenv | `/home/codeteki/codeteki-react.js-django/venv` |
| Static Files | `/home/codeteki/codeteki-react.js-django/backend/staticfiles` |
| Media Files | `/home/codeteki/codeteki-react.js-django/backend/media` |

## Service Names

| Service | Systemd Unit | Socket/PID |
|---------|--------------|------------|
| Gunicorn | `gunicorn` | `/run/gunicorn.sock` |
| Celery Worker | `celery-worker` | `/var/run/celery/worker.pid` |
| Celery Beat | `celerybeat` | `/var/run/celery/beat.pid` |
| Nginx | `nginx` | - |
| Redis | `redis-server` | - |

## Service Files Location

```
/etc/systemd/system/gunicorn.service
/etc/systemd/system/gunicorn.socket
/etc/systemd/system/celery-worker.service
/etc/systemd/system/celerybeat.service
```

## Common Commands

### Deployment
```bash
cd /home/codeteki/codeteki-react.js-django/backend
./deploy.sh
```

### Manual Service Control
```bash
# Restart all services
sudo systemctl restart gunicorn
sudo systemctl restart celery-worker
sudo systemctl restart celerybeat
sudo systemctl reload nginx

# Check status
sudo systemctl status gunicorn
sudo systemctl status celery-worker
sudo systemctl status celerybeat

# View logs
sudo journalctl -u gunicorn -f
sudo journalctl -u celery-worker -f
tail -f /var/log/celery/worker.log
```

### Database
```bash
cd /home/codeteki/codeteki-react.js-django/backend
source ../venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

## Nginx Config

Location: `/etc/nginx/sites-available/codeteki`

Key settings:
- Proxy to Gunicorn socket: `proxy_pass http://unix:/run/gunicorn.sock`
- Static files: `/home/codeteki/codeteki-react.js-django/backend/staticfiles/`
- Media files: `/home/codeteki/codeteki-react.js-django/backend/media/`
- Max upload: `client_max_body_size 250m`

## Gunicorn Service Example

```ini
# /etc/systemd/system/gunicorn.service
[Unit]
Description=Gunicorn daemon for Codeteki
Requires=gunicorn.socket
After=network.target

[Service]
User=codeteki
Group=www-data
WorkingDirectory=/home/codeteki/codeteki-react.js-django/backend
ExecStart=/home/codeteki/codeteki-react.js-django/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    codeteki_site.wsgi:application

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/gunicorn.socket
[Unit]
Description=Gunicorn socket for Codeteki

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

## Celery Worker Service

```ini
# /etc/systemd/system/celery-worker.service
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
```

## Celery Beat Service (Scheduler)

```ini
# /etc/systemd/system/celerybeat.service
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
```

## Environment Variables

Create `/home/codeteki/codeteki-react.js-django/backend/.env`:

```bash
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=codeteki.au,www.codeteki.au

# Database
DATABASE_URL=postgres://user:pass@localhost/codeteki

# Redis
REDIS_URL=redis://localhost:6379/0

# Zoho Mail (CRM)
ZOHO_CLIENT_ID=xxx
ZOHO_CLIENT_SECRET=xxx
ZOHO_REFRESH_TOKEN=xxx
ZOHO_ACCOUNT_ID=xxx
ZOHO_FROM_EMAIL=outreach@codeteki.au
ZOHO_API_DOMAIN=zoho.com

# AI
ANTHROPIC_API_KEY=xxx
```

## First-Time Setup on New Server

```bash
# 1. Create directories
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown -R codeteki:codeteki /var/log/celery /var/run/celery

# 2. Copy service files
sudo cp gunicorn.service /etc/systemd/system/
sudo cp gunicorn.socket /etc/systemd/system/
sudo cp celery-worker.service /etc/systemd/system/
sudo cp celerybeat.service /etc/systemd/system/

# 3. Enable services
sudo systemctl daemon-reload
sudo systemctl enable gunicorn.socket
sudo systemctl enable celery-worker
sudo systemctl enable celerybeat
sudo systemctl enable redis-server

# 4. Start services
sudo systemctl start gunicorn.socket
sudo systemctl start celery-worker
sudo systemctl start celerybeat
```
