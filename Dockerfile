# -------------------------------
# 1) Build Tailwind / frontend
# -------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Install Node deps
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

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# These are just *names*. Values are injected at runtime
# (via docker -e or HuggingFace Space "Secrets").
ENV OPEN_API_KEY="" \
    SYN_API_KEY="" \
    HUGGINGPUP=""

# Non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Python deps
COPY --chown=user requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Static CSS built in stage 1
COPY --from=frontend-builder --chown=user /app/pup_sdk/web/static ./pup_sdk/web/static

# App source
COPY --chown=user . .

# HF routes 7860 → your container
EXPOSE 7860

# FastAPI app entrypoint
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
