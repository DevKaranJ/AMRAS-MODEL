# Development Guidelines

This document covers the development workflow, coding standards, and tooling for AMRAS.

## Prerequisites

- Python 3.12+
- Poetry 2.0+
- Git
- Node.js 18+ (for desktop app development)
- FFmpeg (for video/audio processing)
- Tesseract OCR (for text extraction)

## Setup

```bash
# Clone the repository
git clone https://github.com/your-org/amras.git
cd amras

# Install dependencies
poetry install

# Setup pre-commit hooks
poetry run pre-commit install

# Run database migrations
poetry run alembic upgrade head

# Verify installation
poetry run ruff check .
poetry run mypy app
poetry run pytest
```

## Coding Standards

### Code Style

| Standard | Tool | Configuration |
|---|---|---|
| Formatting | Ruff | Line length: 120, target: py312 |
| Linting | Ruff | Rules: E, W, F, I, C, B |
| Type Checking | mypy | Strict mode, Python 3.12 |

### Commands

```bash
# Format code
poetry run ruff format .

# Check linting
poetry run ruff check .

# Fix auto-fixable lint issues
poetry run ruff check --fix .

# Type checking
poetry run mypy app

# Run all checks
poetry run ruff check . && poetry run ruff format --check . && poetry run mypy app
```

### Type Annotations

- All functions must have type annotations
- Use `typing` module for complex types
- Prefer `Optional[X]` over `X | None` for Python 3.12 compatibility
- Use `Any` sparingly and document why

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Classes | PascalCase | `StoryEngine`, `OCRAgent` |
| Functions | snake_case | `process_page`, `extract_text` |
| Variables | snake_case | `page_count`, `ocr_result` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private | Leading underscore | `_internal_method` |
| Modules | snake_case | `story_engine.py` |

### Import Order

1. Standard library
2. Third-party packages
3. Local modules
4. Absolute imports preferred

Ruff handles import sorting automatically via the `I` rule.

## Testing

### Framework

- **pytest** with **pytest-asyncio** (asyncio_mode = auto)
- **aiosqlite** for in-memory test databases
- **httpx** for async HTTP testing
- **pytest-cov** for coverage reporting

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=app --cov-report=xml --cov-report=html

# Run specific test file
poetry run pytest tests/modules/vision/test_vision_pipeline.py -v

# Run specific test
poetry run pytest tests/modules/ocr/test_ocr_agents.py::TestOCRAgent::test_execute -v

# Run tests matching pattern
poetry run pytest -k "ocr or vision" -v
```

### Writing Tests

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.main import app


@pytest.mark.asyncio
async def test_health_endpoint(db_session: AsyncSession):
    """Test the health endpoint returns 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Test Fixtures

- `tests/api/conftest.py` -- API test fixtures (overrides FastAPI dependencies)
- `tests/modules/conftest.py` -- Module test fixtures (in-memory DB session)

### Coverage Requirements

- **Target:** >90% code coverage
- **CI Scope:** `app/` directory
- **New code:** Must include tests

## Git Workflow

### Branching Strategy

```
main (production)
├── feat/feature-name
├── fix/bug-fix
├── docs/documentation-update
└── refactor/code-improvement
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add OCR text extraction pipeline
fix: resolve memory leak in video renderer
docs: update architecture documentation
refactor: simplify story engine orchestration
test: add unit tests for voice engine
chore: update dependencies
```

### Pull Request Process

1. Create a feature branch from `main`
2. Implement changes with tests
3. Ensure all checks pass:
   ```bash
   poetry run ruff check .
   poetry run ruff format --check .
   poetry run mypy app
   poetry run pytest
   ```
4. Create PR with descriptive title and description
5. Request review from team members
6. Address feedback
7. Merge after approval and CI passes

### Definition of Done

- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] >90% coverage for new code
- [ ] mypy strict checks pass
- [ ] Ruff lint and format checks pass
- [ ] Documentation updated
- [ ] PR approved by at least one reviewer

## Pre-commit Hooks

The following hooks run automatically on `git commit`:

- **Ruff lint** -- Check for linting errors
- **Ruff format** -- Check code formatting
- **mypy** -- Type checking

If any hook fails, fix the issues before committing.

## Debugging

### Logging

AMRAS uses structured logging via `structlog`:

```python
import structlog

logger = structlog.get_logger()

logger.info("processing_started", manga_id=manga.id, chapter=chapter.number)
logger.error("ocr_failed", page=page.id, error=str(e), exc_info=True)
```

### Configuration

Set `DEBUG=true` in `.env` for verbose logging:

```env
DEBUG=true
LOG__LEVEL=DEBUG
LOG__FORMAT=console
```

### Database

For debugging database queries:

```env
DB__ECHO=true
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Ruff
- mypy
- GitLens

Settings:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

## Performance

### Profiling

Use Python's built-in profiling tools:

```bash
python -m cProfile -o output.prof -m pytest
snakeviz output.prof
```

### Memory Monitoring

```python
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```
