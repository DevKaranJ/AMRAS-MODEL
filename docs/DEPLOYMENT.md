# Deployment Guide

This document covers deploying AMRAS in various environments.

## Quick Start (Docker)

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## Docker Deployment

### Dockerfile

The production Dockerfile uses a multi-stage build:

```dockerfile
FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc libpq-dev ffmpeg tesseract-ocr tesseract-ocr-eng

# Non-root user
RUN useradd -m -s /bin/bash amras
USER amras

# Poetry and dependencies
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction

# Application
COPY . .
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build

```bash
docker build -t amras .
```

### Run

```bash
docker run -d \
  --name amras \
  -p 8000:8000 \
  -v ./storage:/app/storage \
  -e DB__URL=sqlite+aiosqlite:////app/dev.db \
  amras
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - ./storage:/app/storage
    environment:
      - DB__URL=sqlite+aiosqlite:////app/dev.db
    restart: unless-stopped
```

## Production Deployment

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ (recommended for production)
- FFmpeg
- Tesseract OCR
- Sufficient disk storage for manga/videos
- GPU (optional, for AI model acceleration)

### Environment Configuration

Create a `.env.production` file:

```env
# Application
DEBUG=false
PROJECT_NAME=AMRAS Production

# Database (PostgreSQL)
DB__URL=postgresql+asyncpg://user:password@localhost:5432/amras
DB__POOL_SIZE=20
DB__MAX_OVERFLOW=40

# AI Providers
AI__PROVIDER=openai
AI__API_KEY=sk-your-key-here
AI__MODEL=gpt-4

# Storage
STORAGE__BASE_DIR=/data/amras/storage

# Logging
LOG__LEVEL=INFO
LOG__FORMAT=json
LOG__FILE=/var/log/amras/app.log

# Video
VIDEO__RESOLUTION=1920x1080
VIDEO__FPS=30

# GPU
GPU__ENABLED=true
GPU__DEVICE=cuda
GPU__MEMORY_FRACTION=0.8
```

### Database Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb amras

# Run migrations
poetry run alembic upgrade head
```

### Running with Uvicorn

```bash
# Single worker
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# Multiple workers (recommended)
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# With TLS
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

### Running with Gunicorn (Production)

```bash
# Install gunicorn
poetry add gunicorn

# Run with gunicorn + uvicorn workers
poetry run gunicorn app.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Systemd Service

Create `/etc/systemd/system/amras.service`:

```ini
[Unit]
Description=AMRAS API
After=network.target postgresql.service

[Service]
User=amras
Group=amras
WorkingDirectory=/opt/amras
Environment=PATH=/opt/amras/.venv/bin
ExecStart=/opt/amras/.venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable amras
sudo systemctl start amras
sudo systemctl status amras
```

### Nginx Reverse Proxy

```nginx
upstream amras {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://amras;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://amras;
    }
}
```

## Desktop Application Deployment

### Build for Distribution

```bash
cd desktop
npm install
npm run build
```

### Electron Builder

```bash
# Build for current platform
npm run build

# Build for specific platform
npx electron-builder --mac
npx electron-builder --win
npx electron-builder --linux
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# System resources
curl http://localhost:8000/production/system/resources
```

### Log Monitoring

```bash
# Follow logs
tail -f /var/log/amras/app.log

# Search for errors
grep "ERROR" /var/log/amras/app.log
```

### Metrics

Track these metrics:
- API response times
- Pipeline completion rates
- AI provider latency and costs
- Storage usage
- GPU utilization

## Backup

### Database Backup

```bash
# PostgreSQL
pg_dump -U user amras > backup_$(date +%Y%m%d).sql

# SQLite
cp dev.db backup_$(date +%Y%m%d).db
```

### Storage Backup

```bash
tar -czf storage_$(date +%Y%m%d).tar.gz storage/
```

### Automated Backup

Add to crontab:

```bash
0 2 * * * /opt/amras/scripts/backup.sh
```

## Scaling

### Horizontal Scaling

- Deploy multiple API instances behind a load balancer
- Use shared PostgreSQL database
- Use shared storage (NFS, S3)

### Vertical Scaling

- Increase API workers: `--workers N`
- Increase database connection pool
- Add GPU resources for AI models

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common deployment issues.
