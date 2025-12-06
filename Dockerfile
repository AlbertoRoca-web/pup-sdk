# Multi-stage build for Tailwind + Python setup
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy Node configuration
COPY package*.json ./
RUN npm ci

# Copy Tailwind config and frontend source
COPY vite.config.js tailwind.config.js ./
COPY frontend/ ./frontend/

# Build Tailwind CSS
RUN npm run build

# Python stage
FROM python:3.9

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy Python requirements and install
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy built CSS from frontend stage
COPY --from=frontend-builder --chown=user /app/pup_sdk/web/static ./pup_sdk/web/static

# Copy Python application code
COPY --chown=user . /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]