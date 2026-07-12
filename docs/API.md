# API Reference

Complete reference for the AMRAS REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

AMRAS currently does not require authentication for development. For production, implement appropriate authentication middleware.

## Interactive Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## System Endpoints

### Health Check

```
GET /health
```

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Version

```
GET /version
```

Returns application version.

**Response:**
```json
{
  "version": "0.1.0"
}
```

### Settings

```
GET /settings
```

Returns current application settings (secrets redacted).

**Response:**
```json
{
  "project_name": "AI Manga Recap Automation System (AMRAS)",
  "version": "0.1.0",
  "debug": false,
  "db": {
    "url": "sqlite+aiosqlite:///dev.db",
    "echo": false
  }
}
```

## Ingestion Endpoints

### Import Manga

```
POST /ingestion/import
```

Import manga from local files.

**Request Body:** Multipart form data with manga files

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started",
  "manga_count": 5
}
```

### Download Manga

```
POST /ingestion/download
```

Download manga from a remote source.

**Request Body:**
```json
{
  "url": "https://example.com/manga.cbz",
  "manga_id": "optional-existing-id"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started"
}
```

### List Manga

```
GET /ingestion/manga
```

List all imported manga.

**Query Parameters:**
- `skip` (int, default 0): Pagination offset
- `limit` (int, default 100): Pagination limit

**Response:**
```json
{
  "manga": [
    {
      "id": 1,
      "title": "Example Manga",
      "chapters": 10,
      "status": "imported"
    }
  ],
  "total": 50
}
```

## Vision Endpoints

### Analyze Image

```
POST /vision/analyze
```

Run vision analysis pipeline on an image.

**Request Body:** Multipart form data with image file

**Response:**
```json
{
  "job_id": "uuid",
  "panels": [...],
  "characters": [...],
  "objects": [...]
}
```

## OCR Endpoints

### Extract Text

```
POST /ocr/extract
```

Extract text from manga pages.

**Request Body:**
```json
{
  "page_ids": [1, 2, 3],
  "language": "eng"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started"
}
```

## Story Endpoints

### Analyze Story

```
POST /story/analyze
```

Run multi-agent story analysis.

**Request Body:**
```json
{
  "manga_id": 1,
  "chapters": [1, 2, 3]
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started"
}
```

## Memory Endpoints

### Create Memory

```
POST /memory
```

Create a new memory entry.

**Request Body:**
```json
{
  "type": "character",
  "key": "protagonist_name",
  "value": "Goku",
  "metadata": {}
}
```

### Get Memory

```
GET /memory/{memory_id}
```

Retrieve a memory entry by ID.

### List Memories

```
GET /memory
```

List all memory entries with optional filters.

### Update Memory

```
PUT /memory/{memory_id}
```

Update an existing memory entry.

### Delete Memory

```
DELETE /memory/{memory_id}
```

Delete a memory entry.

## Voice Endpoints

### Generate Audio

```
POST /audio/generate
```

Generate audio from narration script.

**Request Body:**
```json
{
  "script_id": "uuid",
  "voice_profile": "narrator_1",
  "emotion": "neutral"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started"
}
```

## Timeline Endpoints

### Generate Timeline

```
POST /timeline/generate
```

Generate video timeline from story analysis.

**Request Body:**
```json
{
  "manga_id": 1,
  "audio_track_id": "uuid",
  "style": "dynamic"
}
```

### Get Timeline

```
GET /timeline/{timeline_id}
```

Retrieve a timeline by ID.

### Get Timeline Scenes

```
GET /timeline/{timeline_id}/scenes
```

Get all scenes in a timeline.

### Get Camera Directions

```
GET /timeline/{timeline_id}/cameras
```

Get camera paths for a timeline.

### Get Transitions

```
GET /timeline/{timeline_id}/transitions
```

Get transition effects for a timeline.

## Video Endpoints

### Create Render Job

```
POST /render/jobs
```

Create a video rendering job.

**Request Body:**
```json
{
  "timeline_id": "uuid",
  "resolution": "1920x1080",
  "fps": 30,
  "codec": "h264"
}
```

### Get Render Status

```
GET /render/jobs/{job_id}
```

Check render job status.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "rendering",
  "progress": 0.65,
  "current_scene": 15,
  "total_scenes": 23
}
```

## Subtitle Endpoints

### Generate Subtitles

```
POST /subtitles/generate
```

Generate subtitles from narration and timeline.

**Request Body:**
```json
{
  "timeline_id": "uuid",
  "audio_track_id": "uuid",
  "format": "srt",
  "language": "en"
}
```

### Export Subtitles

```
POST /subtitles/export/{job_id}
```

Export generated subtitles in specified format.

**Query Parameters:**
- `format` (string): srt, vtt, or ass

## Thumbnail Endpoints

### Generate Thumbnail

```
POST /thumbnail/generate
```

Generate a video thumbnail.

**Request Body:**
```json
{
  "manga_id": 1,
  "style": "dramatic",
  "text_overlay": "Epic Manga Recap"
}
```

## QA Endpoints

### Run QA

```
POST /qa/run
```

Run quality assurance checks on completed content.

**Request Body:**
```json
{
  "project_id": 1,
  "checks": ["ocr", "story", "narration", "voice", "timeline", "video"]
}
```

### Get QA Report

```
GET /qa/reports/{report_id}
```

Retrieve a QA report.

## YouTube / Publishing Endpoints

### Publish Video

```
POST /youtube/publish
```

Publish a video to YouTube.

**Request Body:**
```json
{
  "video_id": "uuid",
  "title": "Manga Recap: Chapter 1-5",
  "description": "An epic recap of...",
  "tags": ["manga", "recap", "anime"],
  "playlist_id": "optional-playlist-id",
  "schedule_time": "2024-01-15T18:00:00Z"
}
```

### Get Analytics

```
GET /youtube/analytics/{video_id}
```

Retrieve YouTube analytics for a published video.

## Production Endpoints

### System Health

```
GET /production/system/health
```

Detailed system health status.

### System Resources

```
GET /production/system/resources
```

System resource usage (CPU, memory, disk, GPU).

### Projects

```
GET /production/projects
```

List all production projects.

### Pipeline Status

```
GET /production/pipeline
```

Get current pipeline status.

### Start Pipeline

```
POST /production/pipeline
```

Start a production pipeline.

**Request Body:**
```json
{
  "manga_id": 1,
  "chapters": [1, 2, 3],
  "config": {
    "voice": "narrator_1",
    "style": "dynamic",
    "resolution": "1920x1080"
  }
}
```

## Job Management

### Create Job

```
POST /jobs
```

Create a new job.

### Get Job Status

```
GET /jobs/{job_id}
```

Check job status and progress.

## Error Responses

All endpoints return errors in a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...},
    "suggestion": "Check the request body format"
  }
}
```

### HTTP Status Codes

| Code | Description |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
