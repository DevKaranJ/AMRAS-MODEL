# AMRAS Project Constitution

This document defines the core principles, values, and standards of the AMRAS project.

## Mission

AMRAS aims to automate the creation of high-quality manga recap videos, making content creation accessible while maintaining artistic integrity and narrative quality.

## Core Principles

### 1. Quality First

Every output must meet professional standards. We never sacrifice quality for speed.

### 2. Modular Architecture

Components are loosely coupled and independently testable. Changes to one module should not require changes to others.

### 3. Test-Driven Development

All code must be tested. Tests are not optional.

### 4. Type Safety

Python type annotations are mandatory. mypy strict mode is enforced.

### 5. Documentation

Code must be self-documenting. Public APIs require docstrings. Complex logic requires comments.

### 6. Simplicity

Write simple, readable code. Avoid clever tricks. Optimize for maintainability.

### 7. Consistency

Follow established patterns. Maintain consistent naming, formatting, and structure.

## Technical Standards

### Code Quality

- **Formatting:** Ruff (line length: 120)
- **Linting:** Ruff (rules: E, W, F, I, C, B)
- **Type Checking:** mypy (strict mode)
- **Coverage:** >90% for all new code

### Git Workflow

- **Branches:** `feat/*`, `fix/*`, `docs/*`, `refactor/*`
- **Commits:** Conventional Commits format
- **Reviews:** At least one approval required
- **CI:** All checks must pass before merge

### Architecture

- **Pattern:** Clean Architecture
- **DI:** dependency-injector
- **ORM:** SQLAlchemy 2.0 (async)
- **API:** FastAPI
- **Agents:** BaseAgent ABC pattern

## Code Review Checklist

- [ ] Tests included
- [ ] Type annotations present
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows coding standards
- [ ] CI passes

## Decision Making

### Technical Decisions

- Discuss in PRs or issues
- Prefer simple solutions
- Document rationale

### Architecture Changes

- Require team discussion
- Document in ARCHITECTURE.md
- Update relevant guides

## Communication

- **Issues:** Bug reports, feature requests
- **PRs:** Code review, discussion
- **Discussions:** Questions, ideas

## Values

1. **Transparency** -- Open development
2. **Quality** -- Professional standards
3. **Collaboration** -- Team-oriented
4. **Continuous Improvement** -- Always learning
5. **User Focus** -- End-user experience matters
