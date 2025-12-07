# -------------------------------
# 1) Build Tailwind / frontend
# -------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Node deps
COPY package*.json ./
RUN npm ci

# Tailwind / Vite config + source
COPY vite.config.js tailwind.config.js ./
COPY frontend/ ./frontend/

# Build CSS into pup_sdk/web/static
RUN npm run build

# -------------------------------
# 2) Python backend image
# -------------------------------
FROM python:3.9-slim

# Keep logs unbuffered & pip lean
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Default env names your app will read.
# **Values are injected at runtime** by HF or `docker run -e`.
ENV OPEN_API_KEY="" \
    SYN_API_KEY=""

# Non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install Python deps
COPY --chown=user requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Static CSS built in stage 1
COPY --from=frontend-builder --chown=user /app/pup_sdk/web/static ./pup_sdk/web/static

# App source
COPY --chown=user . .

# HuggingFace will hit 7860 by default
EXPOSE 7860

# FastAPI app entrypoint
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
