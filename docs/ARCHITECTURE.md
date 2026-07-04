# AMRAS Architecture Overview

AMRAS follows a modular, plugin-based Clean Architecture design.

## Core Layers
1. **API Layer (`app/api/`)**: FastAPI endpoints for client interaction.
2. **Core/Domain Layer (`app/core/`, `app/domain/`)**: Fundamental business rules, shared logic, and configurations.
3. **Infrastructure Layer (`app/infrastructure/`, `app/database/`)**: Concrete implementations for DB, cache, and external APIs.
4. **Modules (`modules/`)**: Independent functional areas (e.g., OCR, Video Generation, Vision).

## Plugins & Agents
- Features are designed as plugins conforming to `app/core/plugins.py`.
- AI models conform to the `BaseAgent` interface in `app/agents/base.py`.
