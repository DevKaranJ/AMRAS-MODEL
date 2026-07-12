# Performance Guide

This document covers performance optimization and monitoring in AMRAS.

## Overview

AMRAS is designed for high-performance content generation. This guide covers optimization strategies, monitoring, and troubleshooting.

## Performance Metrics

### Key Metrics

| Metric | Target | Description |
|---|---|---|
| API Response Time | < 200ms | Health check endpoints |
| Pipeline Throughput | > 100 pages/hour | Manga processing rate |
| Video Render Time | < 2x duration | Render time vs video length |
| Memory Usage | < 4GB | Peak memory during pipeline |
| GPU Utilization | > 80% | When GPU acceleration enabled |

## Monitoring

### System Resources

```bash
# Check system resources
curl http://localhost:8000/production/system/resources

# Response
{
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "memory_used_mb": 2450,
    "memory_total_mb": 8192,
    "disk_free_gb": 150,
    "gpu_available": true,
    "gpu_memory_used_mb": 4000,
    "gpu_memory_total_mb": 8192,
    "gpu_utilization": 75.0
}
```

### Pipeline Metrics

```python
# Track pipeline performance
POST /production/pipeline/metrics
{
    "pipeline_id": "uuid",
    "stage": "vision",
    "duration_seconds": 45.2,
    "pages_processed": 20,
    "memory_peak_mb": 2100
}
```

### Render Statistics

```python
# Get render statistics
GET /render/jobs/{job_id}/statistics

# Response
{
    "render_time_seconds": 180.5,
    "video_duration_seconds": 120.0,
    "real_time_factor": 1.5,
    "scenes_rendered": 23,
    "avg_scene_time": 7.8
}
```

## Optimization Strategies

### 1. GPU Acceleration

Enable GPU for AI model inference:

```env
GPU__ENABLED=true
GPU__DEVICE=cuda
GPU__MEMORY_FRACTION=0.8
```

### 2. Parallel Processing

The QA engine runs agents in parallel:

```python
# 10 QA agents run simultaneously
# Reduces QA time from ~50s to ~10s
```

### 3. Batch Processing

Process multiple items at once:

```python
# Batch OCR extraction
POST /ocr/extract
{
    "page_ids": [1, 2, 3, 4, 5],  # Process 5 pages at once
    "language": "eng"
}
```

### 4. Caching

The AI Gateway caches responses:

```python
# Cache check
POST /ai-gateway/check-cache
{
    "request_hash": "abc123"
}

# Cache hit reduces latency from 2s to 10ms
```

### 5. Connection Pooling

Database connection pooling:

```env
DB__POOL_SIZE=20
DB__MAX_OVERFLOW=40
```

### 6. Async Operations

All operations are async-first:

```python
# Parallel API calls
async with aiohttp.ClientSession() as session:
    tasks = [fetch_page(session, url) for url in urls]
    results = await asyncio.gather(*tasks)
```

## Resource Management

### Memory

| Stage | Typical Usage | Optimization |
|---|---|---|
| Ingestion | 500MB | Process files sequentially |
| Vision | 1.5GB | Process pages in batches |
| OCR | 800MB | Batch OCR requests |
| Story | 1GB | Limit context window |
| Voice | 2GB | Process segments individually |
| Video | 3GB | Use GPU, batch encoding |

### CPU

| Stage | Typical Usage | Optimization |
|---|---|---|
| Image preprocessing | 60% | Multi-threaded |
| OCR | 40% | Tesseract multi-core |
| Video encoding | 80% | GPU acceleration |
| AI inference | 30% | GPU acceleration |

### GPU

| Model | VRAM Usage | Speedup |
|---|---|---|
| llama3 (7B) | 4GB | 10x vs CPU |
| llama3 (13B) | 8GB | 15x vs CPU |
| Image models | 2GB | 5x vs CPU |

## Profiling

### Python Profiling

```bash
# Profile a specific function
python -m cProfile -o output.prof -m pytest tests/

# Visualize with snakeviz
snakeviz output.prof
```

### Memory Profiling

```python
import tracemalloc

tracemalloc.start()

# Your code here
result = await engine.run(...)

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

### API Profiling

```bash
# Time API calls
time curl http://localhost:8000/health

# Use httpstat
curl -o /dev/null -s -w "time_total: %{time_total}\n" http://localhost:8000/health
```

## Performance Testing

### Load Testing

```python
import asyncio
import aiohttp

async def test_concurrent_requests(n: int = 100):
    """Test API with concurrent requests."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(n):
            task = session.get("http://localhost:8000/health")
            tasks.append(task)

        start = time.perf_counter()
        responses = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        print(f"{n} requests in {elapsed:.2f}s")
        print(f"Avg: {elapsed/n*1000:.0f}ms per request")

asyncio.run(test_concurrent_requests())
```

### Benchmark Suite

```python
# Run benchmarks
poetry run pytest tests/performance/ -v --benchmark-only

# Compare benchmarks
poetry run pytest tests/performance/ -v --benchmark-compare
```

## Troubleshooting Performance

### High Memory Usage

```bash
# Check memory usage
ps aux | grep uvicorn

# Reduce batch size
# Process fewer items at once
```

### Slow API Response

```bash
# Check database queries
DB__ECHO=true

# Monitor slow queries
# Add indexes for frequent queries
```

### Slow Video Rendering

```bash
# Check GPU utilization
nvidia-smi

# Use faster encoding preset
VIDEO__PRESET=fast

# Reduce resolution for development
VIDEO__RESOLUTION=1280x720
```

### High CPU Usage

```bash
# Check what's using CPU
top -p $(pgrep -d, python)

# Reduce worker count
--workers 2
```

## Best Practices

1. **Enable GPU** for AI model inference
2. **Use batch processing** for multiple items
3. **Cache AI responses** to reduce API calls
4. **Monitor resources** during pipeline execution
5. **Profile before optimizing** to find actual bottlenecks
6. **Use async operations** for I/O-bound tasks
7. **Set appropriate timeouts** to prevent resource exhaustion
