# Nginx Performance Configuration for Codeteki

Update your Nginx config at `/etc/nginx/sites-available/codeteki` with this configuration:

```nginx
server {
    listen 80;
    server_name codeteki.au www.codeteki.au;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/x-javascript application/xml application/json;
    gzip_comp_level 6;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # Static files with hash in filename (JS/CSS bundles) - cache forever
    location /static/ {
        alias /home/codeteki/apps/codeteki/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        add_header Vary "Accept-Encoding";

        # Enable pre-compressed files from WhiteNoise
        gzip_static on;

        # CORS headers if needed
        add_header Access-Control-Allow-Origin "*";
    }

    # Root level static assets (images, logos, webp files)
    location ~* \.(png|jpg|jpeg|gif|webp|svg|ico|woff|woff2|ttf|eot)$ {
        root /home/codeteki/apps/codeteki/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }

    # Media files (user uploads) - cache for 7 days
    location /media/ {
        alias /home/codeteki/apps/codeteki/backend/media/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    # Django app
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        client_max_body_size 250m;
    }
}
```

## After updating, run:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Verify cache headers are working:

```bash
curl -I https://codeteki.au/static/js/main.f6467577.js | grep -i cache
# Should show: Cache-Control: public, max-age=31536000, immutable
```

## Expected Impact

| Issue | Current | After Fix |
|-------|---------|-----------|
| Cache efficiency | 0% (no cache) | 100% (1 year cache) |
| Repeat visit load | Full download | From cache |
| Performance score | ~55 | 75+ |
