# AGENTS.md

This file provides guidance to AI coding assistants working in this repository.

## Graphify Knowledge Graph Integration

**When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.** This loads the full graphify pipeline instructions from `~/.config/opencode/skills/graphify/SKILL.md`.

### Graphify Workflow

1. **First run**: Execute `/graphify .` in the project root to build the knowledge graph from your codebase
2. **Subsequent queries**: Use `/graphify query "<question>"` to answer questions from the graph instead of reading raw files
3. **Path tracing**: Use `/graphify path "A" "B"` to trace connections between concepts
4. **Explanations**: Use `/graphify explain "<concept>"` for plain-language explanations

### Graph Outputs (in `graphify-out/`)

- `GRAPH_REPORT.md` - One-page audit report with god nodes, surprising connections, and suggested questions
- `graph.json` - Queryable graph data (nodes, edges, communities)
- `graph.html` - Interactive visualization (open in browser)
- `.graphify_analysis.json` - Community analysis, cohesion scores, god nodes

### Token Optimization

Graphify reduces token usage by **71.5×** on mixed corpora by letting agents query a structured graph instead of re-reading raw files. The `GRAPH_REPORT.md` serves as a cold-start map — read it before searching files.

### Honesty Rules

- Every edge is tagged `EXTRACTED` (explicit in source), `INFERRED` (reasonable inference), or `AMBIGUOUS` (flagged for review)
- Token costs are reported in every run
- Cohesion scores are shown as raw numbers

---

## Project-Specific Guidance

This is the **AMRAS (AI Manga Recap Automation System)** - a production-grade platform that automates end-to-end workflow of transforming manga series into YouTube recap videos.

### Architecture

- **Clean Architecture** with plugin-based modular design
- **FastAPI** backend with 13 domain routers
- **SQLAlchemy 2.0** + **Alembic** for database (100+ models across 13 domains)
- **Electron + React + TypeScript** desktop application
- **AI Gateway** for provider-agnostic LLM/TTS access (local, OpenAI, Anthropic, ElevenLabs)

### Key Modules

| Module | Purpose |
|--------|---------|
| `modules/ingestion` | Manga import (CBZ, PDF, folder, remote) |
| `modules/vision` | Panel detection, layout analysis, character recognition |
| `modules/ocr` | Tesseract-based text extraction |
| `modules/story` | Multi-agent story analysis |
| `modules/memory` | Versioned knowledge base |
| `modules/narration` | 9-agent narration pipeline |
| `modules/voice` | Emotion-aware TTS |
| `modules/timeline` | Camera direction, panel selection |
| `modules/video` | Scene rendering, FFmpeg encoding |
| `modules/subtitles` | Multi-format subtitle generation |
| `modules/qa` | 10 parallel QA agents |
| `modules/youtube` | Publishing, SEO, analytics |
| `modules/ai_gateway` | Model registry, routing |

### Development Commands

```bash
# Install dependencies
poetry install

# Run linting
poetry run ruff check .
poetry run ruff format --check .

# Run type checking
poetry run mypy app

# Run tests
poetry run pytest

# Start server
poetry run uvicorn app.api.main:app --reload

# Database migrations
poetry run alembic upgrade head
```

### Testing

- **Framework**: pytest with pytest-asyncio
- **Database**: In-memory SQLite for isolation
- **Target**: >90% code coverage

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
