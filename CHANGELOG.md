# Changelog

All notable changes to AMRAS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete documentation suite
- Architecture documentation with Mermaid diagrams
- API reference documentation
- Database schema documentation
- AI Gateway documentation
- Pipeline documentation for all modules
- Troubleshooting guide
- Contributing guidelines
- Security policy
- Desktop application guide
- Performance guide
- Operations manual

### Changed
- Rewrote README.md with industry-standard format
- Expanded ARCHITECTURE.md with detailed layer descriptions
- Updated DEVELOPMENT.md with comprehensive workflow
- Enhanced ONBOARDING.md with code examples

## [0.1.0] - 2024-01-01

### Added
- Initial project scaffolding
- Clean Architecture structure
- FastAPI application with 13 domain routers
- SQLAlchemy models (100+ models, 13 domains)
- Alembic migrations (8 versions)
- BaseAgent ABC and plugin system
- AI Provider abstraction with MockProvider
- Storage management with path traversal protection
- Structured logging with structlog
- Exception hierarchy
- Cache system (memory and disk backends)
- Vision pipeline (mock implementation)
- OCR pipeline (mock implementation)
- Story engine (mock implementation)
- Memory engine (mock implementation)
- Narration engine (mock implementation)
- Voice engine (mock implementation)
- Timeline service (mock implementation)
- Video rendering (mock implementation)
- Subtitle engine (mock implementation)
- QA engine (mock implementation)
- YouTube publishing (mock implementation)
- Ingestion pipeline (mock implementation)
- Electron desktop application shell
- Docker configuration
- CI/CD pipeline (GitHub Actions)
- Test suite with pytest
- Code quality tools (Ruff, mypy)

[Unreleased]: https://github.com/DevKaranJ/AMRAS-MODEL/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DevKaranJ/AMRAS-MODEL/releases/tag/v0.1.0
