# AI Manga Recap Automation System (AMRAS)

A production-grade desktop application that converts complete manga series into high-quality, human-like YouTube recap videos with minimal manual intervention.

## Core Principles
* **Architecture:** Clean Architecture, SOLID, Plugin-based.
* **Testing:** Comprehensive test suites (Unit, Integration, E2E).
* **Quality:** Strict typing, formatting, and linting.

## Quickstart

1. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
2. Install Dependencies: `poetry install`
3. Run Database Migrations: `poetry run alembic upgrade head`
4. Start Server: `poetry run uvicorn app.api.main:app --reload`
5. Run Tests: `poetry run pytest`

See `docs/ARCHITECTURE.md` and `docs/DEVELOPMENT.md` for more information.
