# Database Schema Guide

Complete reference for the AMRAS database schema.

## Overview

AMRAS uses SQLAlchemy 2.0 with async support. The schema contains **100+ models** organized into **13 domains**.

| Environment | Database | Driver |
|---|---|---|
| Development | SQLite | aiosqlite |
| Production | PostgreSQL | asyncpg |
| Testing | In-memory SQLite | aiosqlite |

## Base Model

All models inherit from `DeclarativeBase` with `TimestampMixin`:

```python
# app/models/base.py
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

class Base(DeclarativeBase, TimestampMixin):
    pass
```

## Model Domains

### Core (`app/models/core.py`)

| Model | Description | Key Fields |
|---|---|---|
| `Project` | Production project | id, name, status, config |
| `Job` | Async job tracking | id, type, status, progress, result |
| `JobLog` | Job execution logs | id, job_id, level, message, timestamp |
| `AIProvider` | AI provider config | id, name, type, api_key, base_url |
| `Setting` | Application settings | id, key, value, category |
| `SystemState` | System state tracking | id, key, value, updated_at |

### Manga (`app/models/manga.py`)

| Model | Description | Key Fields |
|---|---|---|
| `Manga` | Manga series | id, title, author, status, cover_image |
| `Chapter` | Manga chapter | id, manga_id, number, title, page_count |
| `Page` | Individual page | id, chapter_id, number, image_path, ocr_text |
| `ImportJob` | Import job tracking | id, manga_id, status, source_type, source_path |
| `DownloadJob` | Download tracking | id, url, status, file_path, progress |

### Vision (`app/models/vision.py`)

| Model | Description | Key Fields |
|---|---|---|
| `VisionJob` | Vision analysis job | id, page_id, status, results |
| `Panel` | Detected panel | id, page_id, bbox, order, confidence |
| `SpeechBubble` | Detected speech bubble | id, panel_id, bbox, text, type |
| `Narration` | Detected narration | id, panel_id, text, position |
| `CharacterDetected` | Detected character | id, panel_id, name, bbox, confidence |
| `ObjectDetected` | Detected object | id, panel_id, label, bbox, confidence |
| `ActionDetected` | Detected action | id, panel_id, description, confidence |
| `SoundEffect` | Detected sound effect | id, panel_id, text, position, intensity |
| `ConfidenceScore` | Quality score | id, entity_type, entity_id, score, model |

### Memory (`app/models/memory.py`)

| Model | Description | Key Fields |
|---|---|---|
| `MemoryStore` | Main memory storage | id, type, key, value, version, metadata |
| `MemoryVersion` | Memory versions | id, memory_id, value, version, created_at |
| `CharacterMemory` | Character knowledge | id, name, description, attributes, manga_id |
| `RelationshipMemory` | Character relationships | id, source_id, target_id, type, strength |
| `EventMemory` | Story events | id, description, chapter, page, timestamp_narrative |
| `WorldMemory` | World knowledge | id, key, value, category, manga_id |
| `ObjectMemory` | Object tracking | id, name, description, first_appearance, manga_id |
| `AbilityMemory` | Character abilities | id, character_id, name, description, level |
| `Embedding` | Vector embeddings | id, entity_type, entity_id, embedding, model |
| `KnowledgeGraphNode` | Knowledge graph nodes | id, label, type, properties |
| `KnowledgeGraphNodeEdge` | Knowledge graph edges | id, source_id, target_id, relation, weight |
| `MemoryAudit` | Memory change audit | id, memory_id, action, old_value, new_value, timestamp |
| `ConflictReport` | Memory conflicts | id, memory_id, conflict_type, resolution, status |
| `RetrievalIndex` | Retrieval optimization | id, entity_type, entity_id, index_key, index_value |

### Story (`app/models/story.py`)

| Model | Description | Key Fields |
|---|---|---|
| `StoryCharacter` | Character profiles | id, name, description, role, manga_id |
| `StoryEvent` | Story events | id, description, chapter, page, type |
| `StoryRelationship` | Character relationships | id, source_id, target_id, type, description |
| `StoryLocation` | Locations | id, name, description, first_appearance |
| `StoryOrganization` | Groups/organizations | id, name, description, members |
| `StoryAbility` | Character abilities | id, character_id, name, description |
| `StoryItem` | Story items | id, name, description, owner_id, significance |
| `StoryGoal` | Character goals | id, character_id, description, status |
| `StoryConflict` | Story conflicts | id, description, parties, resolution |
| `StoryTimeline` | Timeline events | id, event_id, timestamp_narrative, order |
| `StoryGraphEdge` | Story graph edges | id, source_id, target_id, relation |
| `KnowledgeBaseEntry` | Knowledge base | id, key, value, category, source |

### Voice (`app/models/voice.py`)

| Model | Description | Key Fields |
|---|---|---|
| `VoiceProfile` | Voice configurations | id, name, provider, model, parameters |
| `AudioJob` | Audio generation job | id, script_id, status, output_path |
| `AudioSegment` | Individual audio segments | id, job_id, text, start_time, end_time, file_path |
| `PronunciationDictionary` | Pronunciation rules | id, word, phonemes, language |
| `TimestampIndex` | Audio timestamps | id, segment_id, word, start_ms, end_ms |
| `AudioVersion` | Audio versions | id, job_id, version, file_path, created_at |
| `AudioQualityReport` | Quality metrics | id, job_id, score, issues, recommendations |

### Video (`app/models/video.py`)

| Model | Description | Key Fields |
|---|---|---|
| `EncodingProfile` | Encoding settings | id, name, codec, resolution, fps, bitrate |
| `RenderJob` | Render job tracking | id, timeline_id, status, progress, output_path |
| `RenderScene` | Scene render data | id, job_id, scene_id, status, output_path |
| `EncodedVideo` | Encoded video files | id, job_id, path, size, duration, format |
| `RenderReport` | Render reports | id, job_id, duration, file_size, quality_score |
| `OutputFile` | Output file tracking | id, job_id, path, type, size |
| `RenderStatistic` | Render statistics | id, job_id, metric_name, metric_value |

### Timeline (`app/models/timeline.py`)

| Model | Description | Key Fields |
|---|---|---|
| `AnimationProfile` | Animation settings | id, name, parameters, style |
| `Timeline` | Video timelines | id, manga_id, chapter_id, duration, config |
| `Transition` | Scene transitions | id, timeline_id, type, duration, parameters |
| `SceneMetadata` | Scene information | id, scene_id, description, mood, pacing |
| `TimelineScene` | Timeline scenes | id, timeline_id, order, start_time, end_time |
| `CameraPath` | Camera movements | id, scene_id, type, start_pos, end_pos, easing |
| `TimelinePanel` | Panel assignments | id, scene_id, panel_id, start_time, end_time |
| `Synchronization` | Audio-visual sync | id, timeline_id, audio_track_id, offsets |

### Subtitles (`app/models/subtitles.py`)

| Model | Description | Key Fields |
|---|---|---|
| `SubtitleLanguage` | Supported languages | id, code, name, direction |
| `LocalizationProfile` | Localization settings | id, name, language_id, rules |
| `CaptionStyle` | Caption formatting | id, name, font, size, color, position |
| `SubtitleJob` | Subtitle generation job | id, timeline_id, status, format, output_path |
| `SubtitleSegment` | Individual subtitles | id, job_id, start_time, end_time, text, order |
| `TranslationJob` | Translation tracking | id, source_job_id, target_language_id, status |
| `SubtitleVersion` | Subtitle versions | id, job_id, version, file_path, created_at |

### YouTube (`app/models/youtube.py`)

| Model | Description | Key Fields |
|---|---|---|
| `PublishingJob` | Publishing tracking | id, video_id, status, youtube_id, published_at |
| `Thumbnail` | Video thumbnails | id, video_id, path, is_default |
| `ThumbnailVariant` | Thumbnail variants | id, thumbnail_id, style, path, dimensions |
| `SEOProfile` | SEO optimization | id, video_id, title_score, description_score, tags |
| `Title` | Optimized titles | id, profile_id, text, score, variant |
| `Description` | Optimized descriptions | id, profile_id, text, word_count |
| `Tag` | Video tags | id, profile_id, text, relevance_score |
| `Playlist` | YouTube playlists | id, name, youtube_id, description |
| `Schedule` | Publishing schedule | id, job_id, scheduled_time, timezone |
| `VideoMetadata` | Video metadata | id, video_id, duration, resolution, file_size |
| `PublishedVideo` | Published videos | id, job_id, youtube_url, view_count |
| `AnalyticsProfile` | Analytics tracking | id, video_id, tracking_id, metrics |

### QA (`app/models/qa.py`)

| Model | Description | Key Fields |
|---|---|---|
| `QAReport` | QA reports | id, project_id, status, overall_score |
| `QualityScore` | Quality metrics | id, report_id, category, score, details |
| `IssueReport` | Issues found | id, report_id, severity, category, description |
| `AutoFixHistory` | Auto-fix attempts | id, issue_id, action, result, success |
| `ManualReview` | Manual review items | id, issue_id, reviewer, status, notes |
| `PerformanceReport` | Performance metrics | id, report_id, metric, value, threshold |
| `ApprovalHistory` | Approval tracking | id, report_id, approver, status, timestamp |
| `ValidationMetric` | Validation results | id, report_id, check, passed, details |

### AI Gateway (`app/models/ai_gateway.py`)

| Model | Description | Key Fields |
|---|---|---|
| `AIGatewayProvider` | AI providers | id, name, type, api_key, base_url, status |
| `AIModel` | Available models | id, provider_id, name, capabilities, pricing |
| `ModelBenchmark` | Performance benchmarks | id, model_id, task, latency, quality |
| `RoutingPolicy` | Routing rules | id, name, conditions, target_model |
| `PromptTemplate` | Prompt templates | id, name, template, version |
| `PromptVersion` | Template versions | id, template_id, version, content |
| `AIRequest` | Request logging | id, model_id, prompt, response, latency |
| `AIResponse` | Response tracking | id, request_id, content, tokens, cost |
| `CacheEntry` | Response cache | id, request_hash, response, expires_at |
| `HealthReport` | Provider health | id, provider_id, status, latency, last_check |
| `UsageStatistic` | Usage tracking | id, provider_id, model_id, tokens, cost, period |
| `FailureHistory` | Failure tracking | id, provider_id, error_type, count, last_occurred |

### Production (`app/models/production.py`)

| Model | Description | Key Fields |
|---|---|---|
| `UserPreferences` | User settings | id, key, value, category |
| `ProjectHistory` | Project history | id, project_id, action, details, timestamp |
| `PipelineHistory` | Pipeline runs | id, project_id, stage, status, duration |
| `ApplicationSettings` | App settings | id, key, value, updated_at |
| `NotificationHistory` | Notifications | id, type, message, read, created_at |
| `BackupHistory` | Backup tracking | id, path, size, created_at, status |
| `InstalledModels` | Installed AI models | id, name, version, path, size |
| `StorageStatistics` | Storage metrics | id, category, file_count, total_size |
| `SystemHealth` | Health snapshots | id, cpu, memory, disk, gpu, timestamp |

## Migrations

Alembic manages database migrations with async support.

### Commands

```bash
# Check current migration state
poetry run alembic current

# Create a new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

### Migration Versions

| Version | Description |
|---|---|
| `3745f408bd3b` | Initial schema |
| `13bc1c478374` | Add manga ingestion tables |
| `1775c1189b9d` | Add production models |
| `367618f06535` | Add subtitles models |
| `96eb6297dae7` | Add subtitle and YouTube models |
| `bf6d04ac8efd` | Add QA models |
| `db8b0d5e648e` | Add memory models |
| `e8c68d1fa1bc` | Add voice models |
