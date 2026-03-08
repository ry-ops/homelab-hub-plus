# ---- Stage 1: Build frontend ----
FROM node:24-alpine AS frontend-build
WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Production image ----
FROM python:3.12-slim
WORKDIR /app

# Install torch CPU-only first to avoid pulling 3GB of CUDA wheels
RUN pip install --no-cache-dir --upgrade pip==25.3 && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy built frontend into Flask static directory
COPY --from=frontend-build /build/dist/ /app/static/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Make entrypoint script executable and ensure Unix line endings
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

ENV FLASK_ENV=production

EXPOSE 8000

USER appuser

ENTRYPOINT ["/app/docker-entrypoint.sh"]
