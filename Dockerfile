FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Add a non-root user
RUN useradd -m -s /bin/bash amras
USER amras

# Install poetry for the amras user
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
ENV PATH="/home/amras/.local/bin:$PATH"

WORKDIR /app

# Copy poetry files
COPY --chown=amras:amras pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY --chown=amras:amras . .

# Set python path
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
