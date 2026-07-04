# Development Guidelines

## Setup
1. `poetry install`
2. `poetry run pre-commit install`

## Standards
- Strict type checking with `mypy` is required.
- Code must be formatted with `ruff format`.
- Linting errors must be resolved (`ruff check`).

## Testing
- Ensure >90% code coverage.
- Write unit tests in `tests/`.
- Run tests via `poetry run pytest`.
