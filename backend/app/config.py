import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Allow larger request bodies for base64 image uploads (5MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Redis — used for caching and rate limiting
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 60  # seconds

    # Qdrant — vector search
    QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "homelab")

    # Auth — Bearer token. Empty string means dev mode (no auth).
    API_TOKEN = os.environ.get("API_TOKEN", "")

    # GitStore — GitHub-backed JSON persistence
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
    GITHUB_REPO = os.environ.get("GITHUB_REPO", "ry-ops/homelab-hub-state")
    GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
    GITSTORE_CACHE_TTL = int(os.environ.get("GITSTORE_CACHE_TTL", "300"))
