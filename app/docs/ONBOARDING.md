# AMRAS Developer Onboarding

Welcome to the AMRAS team. This document outlines the foundational standards for developing the AI Manga Recap Automation System.

## Technology Stack
- **Language:** Python 3.12+
- **Dependency Management:** Poetry
- **Configuration:** pydantic-settings
- **Logging:** structlog
- **Dependency Injection:** dependency-injector
- **Testing:** pytest, pytest-cov
- **Linting & Formatting:** ruff
- **Type Checking:** mypy

## Project Structure (Clean Architecture)
- `app/core/`: Foundation logic, configuration, logging, and exceptions.
- `app/shared/`: Shared utilities, DI containers, and common models.
- `app/api/` & `app/ui/`: Presentation layers.
- `app/<domain>/`: Specific bounded contexts (e.g., `ocr`, `vision`, `story`).

## Development Workflow
1. Create a feature branch.
2. Implement your feature with comprehensive tests.
3. Run formatting and linting: `poetry run ruff check .`
4. Run type checks: `poetry run mypy app`
5. Run tests: `poetry run pytest`
6. Create a Pull Request for review.
