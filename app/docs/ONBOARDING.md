# AMRAS Developer Onboarding

Welcome to the AMRAS team. This document outlines the foundational standards for developing the AI Manga Recap Automation System.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| Dependency Management | Poetry 2.0+ |
| Configuration | pydantic-settings |
| Logging | structlog |
| Dependency Injection | dependency-injector |
| Web Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Testing | pytest, pytest-cov, pytest-asyncio |
| Linting & Formatting | Ruff |
| Type Checking | mypy (strict) |
| Desktop | Electron + React + TypeScript |

## Project Structure (Clean Architecture)

```
app/
├── agents/       # BaseAgent ABC definition
├── api/          # FastAPI endpoints (presentation layer)
├── config/       # Pydantic Settings configuration
├── core/         # Foundation: logging, cache, storage, plugins, exceptions
├── database/     # Async SQLAlchemy session management
├── domain/       # Domain logic (reserved)
├── infrastructure/ # Infrastructure implementations (reserved)
├── jobs/         # Job execution framework
├── models/       # SQLAlchemy ORM models (100+ models)
├── schemas/      # Pydantic request/response schemas
├── services/     # Service layer (reserved)
├── shared/       # Shared utilities, AI provider interface
└── utils/        # Utility functions (reserved)

modules/
├── ai_gateway/   # AI model registry and routing
├── ingestion/    # Manga import pipeline
├── memory/       # Persistent story knowledge
├── narration/    # Script generation
├── ocr/          # Text extraction
├── production/   # System management
├── qa/           # Quality assurance
├── story/        # Story analysis
├── subtitles/    # Subtitle generation
├── thumbnails/   # Thumbnail generation
├── timeline/     # Timeline creation
├── video/        # Video rendering
├── vision/       # Image analysis
├── voice/        # Voice synthesis
└── youtube/      # YouTube publishing
```

## Key Concepts

### BaseAgent

All AI agents implement the `BaseAgent` ABC:

```python
from app.agents.base import BaseAgent

class MyAgent(BaseAgent):
    name = "my_agent"
    description = "Does something useful"
    version = "1.0.0"

    async def execute(self, context: JobContext) -> dict:
        # Your agent logic here
        return {"result": "success"}

    async def validate(self, input_data: dict) -> bool:
        return "required_key" in input_data

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context: JobContext) -> bool:
        return True
```

### Engine Pattern

Modules use engines to orchestrate multiple agents:

```python
class MyEngine:
    def __init__(self, agents: list[BaseAgent]):
        self.agents = agents

    async def run(self, input_data: dict) -> dict:
        result = input_data
        for agent in self.agents:
            result = await agent.execute(result)
        return result
```

### Database Sessions

All database operations use async sessions:

```python
from app.database.session import get_db_session

async with get_db_session() as session:
    # Use session for queries
    result = await session.execute(select(Manga))
```

## Development Workflow

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Implement your feature with comprehensive tests
3. Run formatting and linting:
   ```bash
   poetry run ruff format .
   poetry run ruff check .
   ```
4. Run type checks:
   ```bash
   poetry run mypy app
   ```
5. Run tests:
   ```bash
   poetry run pytest
   ```
6. Create a Pull Request for review

## Getting Help

- **Architecture:** See [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Development:** See [docs/DEVELOPMENT.md](DEVELOPMENT.md)
- **API Reference:** See [docs/API.md](API.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
