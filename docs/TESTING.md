# Testing Guide

Comprehensive guide to testing in AMRAS.

## Overview

AMRAS uses **pytest** with **pytest-asyncio** for async test support. Tests run against an in-memory SQLite database for fast, isolated execution.

## Quick Start

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=xml --cov-report=html

# Run verbose
poetry run pytest -v
```

## Test Structure

```
tests/
├── api/                    # API endpoint tests
│   ├── conftest.py         # Async test fixtures
│   ├── test_production.py
│   ├── test_qa_endpoints.py
│   ├── test_story_endpoints.py
│   ├── test_subtitles_endpoints.py
│   ├── test_timeline.py
│   ├── test_video.py
│   ├── test_vision_endpoints.py
│   └── test_voice_api.py
├── modules/                # Module tests
│   ├── conftest.py         # Shared DB fixtures
│   ├── ai_gateway/
│   │   ├── test_registry.py
│   │   └── test_routing.py
│   ├── ingestion/
│   │   ├── test_importers.py
│   │   ├── test_ingestion_agents.py
│   │   └── test_pipeline.py
│   ├── narration/
│   │   ├── test_narration_agents.py
│   │   ├── test_narration_engine.py
│   │   └── test_narration_exceptions.py
│   ├── ocr/
│   │   ├── test_ocr_agents.py
│   │   └── test_ocr_pipeline.py
│   ├── story/
│   │   ├── test_agents.py
│   │   ├── test_engine.py
│   │   └── test_exceptions.py
│   ├── subtitles/
│   │   ├── test_formats.py
│   │   ├── test_subtitle_agents.py
│   │   └── test_subtitle_engine.py
│   ├── test_production_agents.py
│   ├── test_qa.py
│   ├── test_voice_agents.py
│   ├── test_voice_engine.py
│   ├── thumbnails/
│   │   └── test_thumb_agents.py
│   ├── timeline/
│   │   ├── test_db_perf.py
│   │   ├── test_service.py
│   │   └── test_timeline_agents.py
│   ├── video/
│   │   └── test_video_agents.py
│   ├── vision/
│   │   ├── test_preprocessing.py
│   │   ├── test_vision_agents.py
│   │   └── test_vision_pipeline.py
│   └── youtube/
│       └── test_yt_agents.py
├── test_api.py
├── test_cache.py
├── test_config.py
├── test_core_exceptions.py
├── test_database.py
├── test_jobs.py
├── test_logging.py
├── test_memory.py
├── test_memory_api.py
├── test_plugins.py
├── test_session.py
└── test_storage.py
```

## Test Configuration

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
```

### Fixtures

#### API Tests (`tests/api/conftest.py`)

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.models.base import Base
from app.database.session import get_db_session

@pytest.fixture
async def db_session():
    """Create in-memory SQLite database for tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest.fixture
async def client(db_session):
    """Async HTTP client for API tests."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

#### Module Tests (`tests/modules/conftest.py`)

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

@pytest.fixture
async def db_session():
    """Create in-memory SQLite database for module tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()
```

## Writing Tests

### API Endpoint Tests

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_import_manga(client: AsyncClient):
    """Test manga import endpoint."""
    response = await client.post(
        "/ingestion/import",
        files={"file": ("test.cbz", b"fake-cbz-data", "application/zip")}
    )
    assert response.status_code == 200
    assert "job_id" in response.json()
```

### Module Tests

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.story.agents import StoryAnalysisAgent
from app.agents.base import JobContext

@pytest.mark.asyncio
async def test_story_analysis_agent(db_session: AsyncSession):
    """Test story analysis agent execution."""
    agent = StoryAnalysisAgent()
    context = JobContext(
        manga_id=1,
        chapter_ids=[1, 2, 3],
        db_session=db_session
    )

    result = await agent.execute(context)

    assert result is not None
    assert "characters" in result
    assert "events" in result

@pytest.mark.asyncio
async def test_story_engine(db_session: AsyncSession):
    """Test story engine orchestration."""
    from modules.story.engine import StoryEngine

    engine = StoryEngine()
    result = await engine.run(
        manga_id=1,
        chapters=[1, 2],
        db_session=db_session
    )

    assert result is not None
    assert "analysis" in result
```

### Unit Tests

```python
import pytest
from app.core.cache import MemoryCache

def test_memory_cache_set_get():
    """Test memory cache set and get operations."""
    cache = MemoryCache()

    cache.set("key1", "value1", ttl=60)
    assert cache.get("key1") == "value1"

def test_memory_cache_expiry():
    """Test memory cache TTL expiration."""
    import time
    cache = MemoryCache()

    cache.set("key1", "value1", ttl=1)  # 1 second TTL
    time.sleep(2)
    assert cache.get("key1") is None
```

### Integration Tests

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_full_import_flow(client: AsyncClient, db_session: AsyncSession):
    """Test complete import flow from upload to storage."""
    # Upload manga
    upload_response = await client.post(
        "/ingestion/import",
        files={"file": ("test.cbz", b"fake-cbz-data", "application/zip")}
    )
    assert upload_response.status_code == 200
    job_id = upload_response.json()["job_id"]

    # Check job status (would need polling in real test)
    status_response = await client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
```

## Test Categories

### Unit Tests
- Test individual functions and classes
- Fast execution
- No external dependencies
- Example: `test_cache.py`, `test_config.py`

### Integration Tests
- Test multiple components working together
- Use in-memory database
- Example: `test_api.py`, engine tests

### End-to-End Tests
- Test complete workflows
- May require external services
- Example: `test_full_import_flow`

## Coverage

### Requirements

- **Target:** >90% code coverage
- **Scope:** `app/` directory (CI), full project (local)
- **Reporting:** Codecov integration in CI

### Commands

```bash
# Generate coverage report
poetry run pytest --cov=app --cov-report=xml --cov-report=html

# View HTML report
open htmlcov/index.html

# Check coverage for specific module
poetry run pytest --cov=app.core tests/test_core_exceptions.py
```

### Coverage Configuration

Add to `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 90
show_missing = true
```

## Running Specific Tests

```bash
# By file
poetry run pytest tests/modules/vision/test_vision_pipeline.py

# By function
poetry run pytest tests/modules/ocr/test_ocr_agents.py::test_ocr_extraction

# By marker
poetry run pytest -m "slow"
poetry run pytest -m "not slow"

# By pattern
poetry run pytest -k "ocr or vision"

# Stop on first failure
poetry run pytest -x

# Verbose output
poetry run pytest -v

# Show print output
poetry run pytest -s
```

## Test Markers

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    ...

@pytest.mark.integration
async def test_database_integration():
    ...

@pytest.mark.e2e
async def test_full_pipeline():
    ...
```

Configure markers in `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks integration tests
    e2e: marks end-to-end tests
```

## Best Practices

### Test Naming

```python
# Good
def test_memory_cache_returns_none_for_missing_key():
def test_ocr_agent_extracts_text_from_speech_bubble():
async def test_story_engine_processes_multiple_chapters():

# Bad
def test_cache():
def test_ocr():
async def test_engine():
```

### Arrange-Act-Assert

```python
def test_something():
    # Arrange
    cache = MemoryCache()
    cache.set("key", "value")

    # Act
    result = cache.get("key")

    # Assert
    assert result == "value"
```

### Test Isolation

- Each test should be independent
- Use fixtures for setup/teardown
- Use in-memory database
- Clean up after tests

### Mock External Dependencies

```python
from unittest.mock import AsyncMock, patch

@patch("modules.vision.agents.VisionAgent._call_model")
async def test_vision_agent_with_mock(mock_call):
    mock_call.return_value = {"detected": ["panel", "character"]}
    agent = VisionAgent()
    result = await agent.execute(...)
    assert "panel" in result["detected"]
```

## Performance Testing

```python
import time
import pytest

def test_cache_performance():
    """Test cache operations complete within threshold."""
    cache = MemoryCache()
    start = time.perf_counter()

    for i in range(10000):
        cache.set(f"key_{i}", f"value_{i}")
    for i in range(10000):
        cache.get(f"key_{i}")

    elapsed = time.perf_counter() - start
    assert elapsed < 1.0  # Should complete in under 1 second
```
