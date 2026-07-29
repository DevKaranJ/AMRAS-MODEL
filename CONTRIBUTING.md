# Contributing to AMRAS

Thank you for your interest in contributing to AMRAS! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry 2.0+
- Git
- Node.js 18+ (for desktop app changes)

### Setup

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/DevKaranJ/AMRAS-MODEL.git
cd amras

# Install dependencies
poetry install

# Setup pre-commit hooks
poetry run pre-commit install

# Create a feature branch
git checkout -b feat/your-feature-name
```

## Development Process

### 1. Write Your Code

Follow the [coding standards](docs/DEVELOPMENT.md#coding-standards):
- Type annotations required (mypy strict mode)
- Ruff for formatting and linting
- Google-style docstrings

### 2. Write Tests

All new features must include tests:

```bash
# Run tests to verify
poetry run pytest tests/ -v

# Check coverage
poetry run pytest --cov=app --cov-report=html
```

### 3. Verify Quality Checks

```bash
# Linting
poetry run ruff check .

# Formatting
poetry run ruff format --check .

# Type checking
poetry run mypy app

# All checks combined
poetry run ruff check . && poetry run ruff format --check . && poetry run mypy app && poetry run pytest
```

### 4. Commit Your Changes

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat` -- New feature
- `fix` -- Bug fix
- `docs` -- Documentation changes
- `style` -- Code style changes (formatting, etc.)
- `refactor` -- Code refactoring
- `test` -- Adding or updating tests
- `chore` -- Maintenance tasks

Examples:
```
feat(ocr): add multi-language text extraction
fix(voice): resolve audio stitching timing issue
docs: update API reference for new endpoints
refactor(story): simplify character analysis pipeline
test(memory): add version conflict resolution tests
```

### 5. Create a Pull Request

1. Push your branch to your fork
2. Create a Pull Request against `main`
3. Fill out the PR template
4. Link any related issues
5. Wait for CI to pass
6. Request review from maintainers

## Pull Request Guidelines

### Title

Use the same Conventional Commits format as commit messages:

```
feat(voice): add emotion-aware TTS generation
```

### Description

Include:
- **What** the change does
- **Why** the change is needed
- **How** the change works
- Any breaking changes
- Screenshots (for UI changes)

### Checklist

- [ ] Code follows project coding standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented in PR)
- [ ] All CI checks pass
- [ ] PR approved by at least one reviewer

## Code Review Process

1. **Automated checks** must pass (CI)
2. **At least one approval** from a maintainer
3. **Address all feedback** before merging
4. **Squash and merge** for clean history

## Reporting Issues

### Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs

### Feature Requests

Include:
- Problem statement
- Proposed solution
- Alternatives considered
- Use cases

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers
- Attribute credit where due

## Questions?

- Open a discussion on GitHub
- Check existing documentation in `docs/`
- Review `TROUBLESHOOTING.md` for common issues
