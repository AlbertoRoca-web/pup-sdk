# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

WORKDIR /app

# Environment variables for builds
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install build dependencies and runtime deps
RUN --mount=type=cache,target=/root/.cache/pip \
    set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Source stage
FROM python:3.11-slim

WORKDIR /app

# Production environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    MPLCONFIGDIR=/tmp/mpl

# Install runtime only dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
        gunicorn \
        fastapi \
        uvicorn[standard] \
        openai \
        python-dotenv \
        python-multipart \
        aiofiles

# Copy application files from builder
COPY --from=builder /app /app

# Expose the port (HuggingFace Spaces uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/health || exit 1

# Use gunicorn with multiple workers like PointKedex
CMD gunicorn -b 0.0.0.0:${PORT:-7860} app:app --workers 2 --threads 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50