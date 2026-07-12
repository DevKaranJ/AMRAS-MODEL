# Operations Manual

This document covers operational procedures for running AMRAS in production.

## System Requirements

### Minimum Requirements

| Resource | Requirement |
|---|---|
| CPU | 4 cores |
| RAM | 8GB |
| Storage | 50GB free |
| OS | Linux, macOS, Windows |
| Python | 3.12+ |

### Recommended (Production)

| Resource | Requirement |
|---|---|
| CPU | 8+ cores |
| RAM | 16GB+ |
| Storage | 200GB+ SSD |
| GPU | NVIDIA GPU with 8GB+ VRAM |
| OS | Ubuntu 22.04 LTS |

## Deployment

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/amras.git
cd amras

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with production settings

# Initialize database
poetry run alembic upgrade head

# Start service
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```bash
# Build image
docker build -t amras:latest .

# Run container
docker run -d \
  --name amras \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /data/amras/storage:/app/storage \
  -v /data/amras/.env:/app/.env \
  amras:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/production/system/health

# System resources
curl http://localhost:8000/production/system/resources
```

### Log Monitoring

```bash
# Follow application logs
tail -f /var/log/amras/app.log

# Search for errors
grep "ERROR" /var/log/amras/app.log | tail -20

# Monitor real-time
watch -n 5 'curl -s http://localhost:8000/health | jq .'
```

### Process Monitoring

```bash
# Check running processes
ps aux | grep uvicorn

# Monitor CPU/memory
htop

# Check network connections
netstat -tulpn | grep 8000
```

## Database Operations

### Backup

```bash
# PostgreSQL backup
pg_dump -U user -d amras -f backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite backup
cp /path/to/dev.db /backup/dev_$(date +%Y%m%d_%H%M%S).db

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U user -d amras | gzip > /backup/amras_$DATE.sql.gz
```

### Restore

```bash
# PostgreSQL restore
psql -U user -d amras -f backup.sql

# SQLite restore
cp /backup/dev.db /path/to/dev.db
```

### Migration

```bash
# Apply migrations
poetry run alembic upgrade head

# Check current version
poetry run alembic current

# Rollback one version
poetry run alembic downgrade -1

# Create new migration
poetry run alembic revision --autogenerate -m "description"
```

## Maintenance

### Storage Management

```bash
# Check storage usage
du -sh /data/amras/storage/*

# Clean old files
find /data/amras/storage/videos -mtime +30 -delete

# Archive old projects
tar -czf archive_$(date +%Y%m%d).tar.gz /data/amras/storage/old_projects/
```

### Log Rotation

```bash
# Configure logrotate
cat > /etc/logrotate.d/amras << 'EOF'
/var/log/amras/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### Cache Clearing

```bash
# Clear AI response cache
curl -X POST http://localhost:8000/cache/clear

# Clear storage cache
rm -rf /data/amras/storage/cache/*
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple API instances
uvicorn app.api.main:app --port 8001 --workers 4
uvicorn app.api.main:app --port 8002 --workers 4
uvicorn app.api.main:app --port 8003 --workers 4

# Load balancer configuration (nginx)
upstream amras {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

### Vertical Scaling

```bash
# Increase workers
uvicorn app.api.main:app --workers 8

# Increase database connections
DB__POOL_SIZE=30
DB__MAX_OVERFLOW=60
```

## Security

### API Security

- Use HTTPS in production
- Implement authentication/authorization
- Rate limiting recommended
- Regular security audits

### Data Security

- Encrypt sensitive data at rest
- Use secure connections for databases
- Regular backups
- Access logging

### Dependency Security

```bash
# Check for vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies
poetry update
```

## Troubleshooting

### Service Won't Start

```bash
# Check port availability
lsof -i :8000

# Check logs
journalctl -u amras -n 50

# Check configuration
poetry run python -c "from app.config.settings import settings; print(settings)"
```

### High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Reduce worker count
--workers 2

# Restart service
systemctl restart amras
```

### Database Connection Issues

```bash
# Check database connectivity
psql -U user -d amras -c "SELECT 1"

# Check connection pool
curl http://localhost:8000/production/system/health | jq .database
```

### Slow Performance

```bash
# Check system resources
top
iostat -x 1 5

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Profile specific endpoints
poetry run python -m cProfile -m pytest tests/test_api.py
```

## Incident Response

### Severity Levels

| Level | Description | Response Time |
|---|---|---|
| P1 | System down | Immediate |
| P2 | Major feature broken | 1 hour |
| P3 | Minor issue | 4 hours |
| P4 | Cosmetic | 24 hours |

### Runbook

1. **Identify** the issue
2. **Contain** the impact
3. **Diagnose** root cause
4. **Fix** the issue
5. **Verify** the fix
6. **Document** the incident
