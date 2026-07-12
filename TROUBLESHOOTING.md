# Troubleshooting Guide

Common issues and solutions for AMRAS development and deployment.

## Installation Issues

### Poetry Installation Fails

**Symptom:** `poetry install` fails with dependency conflicts.

**Solution:**
```bash
# Clear poetry cache
poetry cache clear --all pypi

# Update poetry
poetry self update

# Reinstall dependencies
poetry lock
poetry install
```

### Python Version Mismatch

**Symptom:** `python version not compatible` error.

**Solution:** Ensure Python 3.12+ is installed:
```bash
python --version
# Should show 3.12.x or higher
```

### Missing System Dependencies

**Symptom:** `ffmpeg` or `tesseract` not found.

**Solution:**

Ubuntu/Debian:
```bash
sudo apt-get install ffmpeg tesseract-ocr tesseract-ocr-eng
```

macOS:
```bash
brew install ffmpeg tesseract
```

Windows:
- Download FFmpeg from https://ffmpeg.org/download.html
- Download Tesseract from https://github.com/tesseract-ocr/tesseract

## Database Issues

### Migration Errors

**Symptom:** `alembic upgrade head` fails.

**Solution:**
```bash
# Check current migration state
poetry run alembic current

# If database is out of sync, stamp to current
poetry run alembic stamp head

# Then create a new migration if needed
poetry run alembic revision --autogenerate -m "description"

# Apply
poetry run alembic upgrade head
```

### SQLite Lock Errors

**Symptom:** `database is locked` error.

**Solution:**
- Ensure only one process is accessing the database
- For development, use in-memory SQLite for tests
- For production, switch to PostgreSQL

### Connection Pool Exhaustion

**Symptom:** `Too many connections` error.

**Solution:** Adjust pool settings in `.env`:
```env
DB__POOL_SIZE=10
DB__MAX_OVERFLOW=20
```

## API Issues

### Server Won't Start

**Symptom:** `uvicorn` fails to start.

**Solution:**
```bash
# Check if port 8000 is in use
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Use a different port
poetry run uvicorn app.api.main:app --port 8001

# Check for import errors
poetry run python -c "from app.api.main import app"
```

### 422 Validation Error

**Symptom:** API returns 422 Unprocessable Entity.

**Solution:**
- Check request body format against OpenAPI spec at `/docs`
- Ensure all required fields are provided
- Verify field types match the schema

### CORS Errors

**Symptom:** Browser blocks API requests.

**Solution:** Configure CORS in the FastAPI app or use a proxy in development.

## Testing Issues

### Async Tests Timeout

**Symptom:** Tests hang or timeout.

**Solution:**
```bash
# Ensure pytest-asyncio is installed
poetry install

# Check pytest.ini configuration
cat pytest.ini
# Should have: asyncio_mode = auto
```

### Test Database Issues

**Symptom:** Tests fail with database errors.

**Solution:**
- Tests use in-memory SQLite by default
- Check `tests/api/conftest.py` and `tests/modules/conftest.py`
- Ensure test fixtures properly set up and tear down

### Coverage Below Target

**Symptom:** Coverage report shows <90%.

**Solution:**
```bash
# Generate HTML coverage report
poetry run pytest --cov=app --cov-report=html

# Open htmlcov/index.html to see uncovered lines
# Add tests for uncovered code paths
```

## Docker Issues

### Build Fails

**Symptom:** `docker build` fails.

**Solution:**
```bash
# Build with verbose output
docker build --progress=plain -t amras .

# Check if Dockerfile syntax is correct
# Ensure all referenced files exist
```

### Container Can't Start

**Symptom:** Container exits immediately.

**Solution:**
```bash
# Check container logs
docker logs <container_id>

# Run interactively for debugging
docker run -it amras /bin/bash

# Verify the command works inside
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### Volume Mount Issues

**Symptom:** Files not visible inside container.

**Solution:**
- Ensure volume paths are correct in `docker-compose.yml`
- Check file permissions
- Use absolute paths for volumes

## Performance Issues

### Slow Pipeline Execution

**Symptom:** Pipeline takes too long to complete.

**Solutions:**
- Check GPU settings: `GPU__ENABLED=true`
- Verify AI provider response times
- Monitor system resources: `GET /production/system/resources`
- Consider batch processing for large manga series

### High Memory Usage

**Symptom:** Application runs out of memory.

**Solutions:**
- Reduce GPU memory fraction: `GPU__MEMORY_FRACTION=0.6`
- Process smaller batches
- Monitor with `psutil`: `GET /production/system/resources`

### Database Slow Queries

**Symptom:** API responses are slow.

**Solutions:**
- Enable query logging: `DB__ECHO=true`
- Check for missing indexes
- Consider PostgreSQL for production
- Review slow query logs

## AI Provider Issues

### Mock Provider Responses

**Symptom:** Agents return mock data instead of real results.

**Solution:** This is expected in development. To use real AI providers:
1. Set `AI__PROVIDER=openai` (or other provider)
2. Set `AI__API_KEY=your-key`
3. Set `AI__MODEL=gpt-4` (or other model)

### API Key Errors

**Symptom:** `Invalid API key` error.

**Solution:**
1. Verify the API key is correct
2. Check the API key has sufficient permissions
3. Ensure the key is set in `.env` (not hardcoded)
4. Check provider status page

### Rate Limiting

**Symptom:** `429 Too Many Requests` error.

**Solution:**
- Implement exponential backoff
- Use caching to reduce API calls
- Consider upgrading API plan
- Use local models for development

## Logging Issues

### No Log Output

**Symptom:** Application runs but no logs appear.

**Solution:**
```env
# Ensure logging is configured
LOG__LEVEL=DEBUG
LOG__FORMAT=console
```

### Too Verbose

**Symptom:** Too much log output.

**Solution:**
```env
LOG__LEVEL=WARNING
LOG__FORMAT=json
```

## Getting More Help

1. Check the [API Reference](API.md) for endpoint details
2. Review [Architecture](ARCHITECTURE.md) for system design
3. Search existing GitHub issues
4. Open a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Logs (if applicable)
