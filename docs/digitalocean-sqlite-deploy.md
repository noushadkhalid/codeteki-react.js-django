## Deploying Codeteki (Django + React) on a DigitalOcean Droplet with SQLite

Codeteki is a Django backend with a CRA frontend. SQLite is the only database this guide configures so you don’t have to touch PostgreSQL, GDAL, or any heavy spatial libraries.

---

### 1. Update & Install System Packages

```bash
sudo apt update
sudo apt upgrade -y

# Default toolchain (node + npm); no GDAL or PostgreSQL needed
sudo apt install -y python3-venv python3-dev nginx build-essential nodejs npm

# If you prefer Yarn instead of npm (still no GDAL/Postgres packages):
# sudo apt install -y python3-venv python3-dev nginx build-essential nodejs yarn
```

**Install Yarn from the official repo (recommended):**

```bash
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install -y yarn   # Node.js must already be installed
```

---

### 2. Create a Deployment User

Avoid running everything as root. Create a new sudo-enabled user:

```bash
exit                       # if you're currently root in the console
sudo adduser codeteki      # or whatever username you prefer
sudo usermod -aG sudo codeteki
su - codeteki
```

> Replace `codeteki` throughout this doc with your actual username (e.g., `noushad`). If you decide to keep using root, note the permission differences in the later sections.

---

### 3. Clone the Project & Configure `.env`

```bash
cd ~
mkdir -p ~/apps
cd ~/apps
git clone <YOUR_GITHUB_URL> codeteki
cd codeteki
```

Initialize or copy `.env` files:

```bash
cp backend/.env.example backend/.env  # if you track one
nano backend/.env                     # otherwise create from scratch
```

Minimum settings (replace with your actual values):

```bash
# Django Core Settings
DJANGO_SECRET_KEY=your-generated-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP

# CSRF Protection (IMPORTANT!)
DJANGO_CSRF_TRUSTED_ORIGINS=http://yourdomain.com,https://yourdomain.com,http://www.yourdomain.com,https://www.yourdomain.com,http://YOUR_SERVER_IP

# API Keys
OPENAI_API_KEY=your-openai-api-key
```

Generate a strong Django secret key from the server shell:

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(52))
PY
```

Copy the output into `DJANGO_SECRET_KEY=...`.

**Example .env file:**

```bash
DJANGO_SECRET_KEY=xCotUWjXTsTPgk6lg2yTTdV97YMT117fSsE0ve7E_aESlGbFLc2fV46GpfaycX7YjSDs6w
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=codeteki.au,www.codeteki.au,170.64.215.170
DJANGO_CSRF_TRUSTED_ORIGINS=http://codeteki.au,https://codeteki.au,http://www.codeteki.au,https://www.codeteki.au,http://170.64.215.170,https://170.64.215.170
OPENAI_API_KEY=sk-proj-your-key-here
```

---

### 4. Python Virtualenv & Requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Frontend Build (npm or Yarn)

```bash
cd frontend
npm install        # or: yarn install
npm run build      # or: yarn build
cd ..
```

This populates `frontend/build`, which Django serves via WhiteNoise/Nginx.

---

### 6. Django Setup (inside `venv`)

```bash
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # optional
```

Deactivate when finished:

```bash
deactivate
cd ..
```

SQLite stays at `backend/db.sqlite3`. For multi-user droplet deployments, run Gunicorn under the same Unix user (easiest) or ensure that user has RW access to the SQLite file.

---

### 7. Gunicorn Socket + Service + Logs

#### 7.1 Socket file

Create `/etc/systemd/system/gunicorn.socket` (as root):

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

#### 7.2 Gunicorn log directory

```bash
sudo mkdir -p /var/log/gunicorn
sudo touch /var/log/gunicorn/access.log /var/log/gunicorn/error.log
sudo chown codeteki:www-data /var/log/gunicorn/*.log
sudo chmod 664 /var/log/gunicorn/*.log
```

Use your deployment user (`codeteki`/`noushad`/`root`) accordingly.

#### 7.3 Gunicorn service

`/etc/systemd/system/gunicorn.service`:

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=codeteki                
Group=www-data
WorkingDirectory=/home/codeteki/apps/codeteki/backend
ExecStart=/home/codeteki/apps/codeteki/venv/bin/gunicorn \
          --access-logfile /var/log/gunicorn/access.log \
          --error-logfile /var/log/gunicorn/error.log \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          codeteki_site.wsgi:application

[Install]
WantedBy=multi-user.target
```

If you insist on using root:

```
User=root
Group=www-data
WorkingDirectory=/root/your-project
ExecStart=/root/your-project/venv/bin/gunicorn ...
```

Reload + start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.socket
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

Tail logs if needed:

```bash
journalctl -u gunicorn -f
```

---

### 8. Directory Permissions (root vs non-root)

If the project lives under `/home/<user>` ensure execute + read perms:

```bash
sudo chmod +x /home/codeteki
sudo chmod +x /home/codeteki
sudo chmod +x /home/codeteki/codeteki-react.js-django
sudo chmod +x /home/codeteki/codeteki-react.js-django/backend/staticfiles
sudo chown -R codeteki:www-data /home/codeteki/codeteki-react.js-django
sudo chmod -R 755 /home/codeteki/codeteki-react.js-django
sudo chmod -R 775 /home/codeteki/codeteki-react.js-django/backend/staticfiles
```

If you deploy under `/root`:

```bash
sudo chmod +x /root
sudo chmod +x /root/codeteki
sudo chmod +x /root/codeteki/backend/staticfiles
sudo chown -R root:www-data /root/codeteki
sudo chmod -R 755 /root/codeteki
sudo chmod -R 775 /root/codeteki/backend/staticfiles
```

Adding `www-data` to the deployment user’s group (or vice versa) is optional:

```bash
sudo gpasswd -a www-data codeteki   # narrow scope
# or
sudo gpasswd -a www-data root       # broader system scope
```

Prefer `chown` if you only need to expose this project; use `gpasswd` only when you want `www-data` to access multiple root-owned locations.

---

### 9. Nginx Reverse Proxy

Remove default site if needed:

```bash
cd /etc/nginx/sites-enabled
sudo rm -f default my-old-site
```

Create `/etc/nginx/sites-available/codeteki` (must be done with `sudo` since `/etc/nginx` is root-owned):

```bash
sudo tee /etc/nginx/sites-available/codeteki >/dev/null <<'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/codeteki/codeteki-react.js-django/backend/staticfiles/;
    }

    location /media/ {
        alias /home/codeteki/codeteki-react.js-django/backend/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        client_max_body_size 250m;
    }
}
EOF
```

Or edit with `sudo nano /etc/nginx/sites-available/codeteki` and paste the same block.

Enable + restart:

```bash
sudo ln -s /etc/nginx/sites-available/codeteki /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Certificates (optional):

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### 10. Operations Checklist

- `sudo systemctl restart gunicorn` after code updates.
- `sudo systemctl restart nginx` after config changes.
- `journalctl -u gunicorn -f`, `/var/log/gunicorn/*.log`, `/var/log/nginx/error.log` for debugging.
- Back up `backend/db.sqlite3` plus `backend/media` periodically.
- Use `source venv/bin/activate && python manage.py shell` to test production settings directly on the droplet.

With these commands you’ll replicate the deployment approach we’ve used across other Django + React projects on DigitalOcean while sticking strictly to SQLite and avoiding GDAL/PostgreSQL dependencies.
