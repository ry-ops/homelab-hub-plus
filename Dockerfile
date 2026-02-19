# ---- Stage 1: Build frontend ----
FROM node:24-alpine AS frontend-build
WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Production image ----
# Python 3.14 wheels are not yet available for torch/sentence-transformers.
# Pinned to 3.12-slim until upstream wheels ship for 3.14.
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==25.3 && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy built frontend into Flask static directory
COPY --from=frontend-build /build/dist/ /app/static/

RUN mkdir -p /data

# Make entrypoint script executable and ensure Unix line endings
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

ENV DATABASE_URL=sqlite:////data/homelab-hub.db
ENV FLASK_ENV=production

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
