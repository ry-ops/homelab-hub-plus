# Redis Caching

homelab-hub+ adds Redis as a response cache layer between the Svelte frontend and the SQLite database. For read-heavy setups — dashboards that auto-refresh, multiple users — this eliminates redundant database queries.

---

## Architecture

```
Browser → Flask → Redis (cache hit?)
                       ↓ miss
                   SQLite → Redis (store) → Browser
```

The cache is powered by [Flask-Caching](https://flask-caching.readthedocs.io/) with the `RedisCache` backend.

---

## Configuration

Set via environment variables (or `docker-compose.yml`):

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `CACHE_DEFAULT_TIMEOUT` | `60` | Default TTL in seconds |

In `backend/app/config.py`:

```python
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = REDIS_URL
CACHE_DEFAULT_TIMEOUT = 60
```

---

## Docker setup

Redis runs as a sidecar container in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: homelab-hub-plus-redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  restart: unless-stopped
```

Data is persisted to the `redis_data` named volume. The Redis instance is not exposed to the internet — port `6379` binds to `localhost` only in a typical Docker setup.

---

## Using the cache in backend code

The cache singleton is in `backend/app/services/cache.py`:

```python
from app.services.cache import cache

# Cache a view for 30 seconds with a custom key
@cache.cached(timeout=30, key_prefix="map_graph")
def get_graph():
    ...

# Cache with a dynamic key based on request args
@cache.cached(timeout=60, key_prefix=cache.make_cache_key)
def list_hardware():
    ...

# Manually invalidate
cache.delete("map_graph")

# Invalidate all keys matching a prefix
cache.delete_many("hardware_*")

# Clear everything
cache.clear()
```

---

## Cache invalidation strategy

The CRUD factory (`backend/app/routes/_crud_factory.py`) calls cache invalidation on writes. The pattern is:

- `GET` (list/detail) — cached
- `POST` / `PUT` / `DELETE` — writes through and clears the relevant cache key

If you add a new cached route, follow this pattern:

```python
from app.services.cache import cache

@bp.route("", methods=["GET"])
@cache.cached(timeout=60, key_prefix="my_resource_list")
def list_items():
    ...

@bp.route("", methods=["POST"])
def create_item():
    cache.delete("my_resource_list")
    ...
```

---

## Checking Redis health

```bash
# From the host
redis-cli ping
# PONG

# From inside Docker
docker exec homelab-hub-plus-redis redis-cli ping
# PONG

# See all keys
docker exec homelab-hub-plus-redis redis-cli keys '*'

# Check memory usage
docker exec homelab-hub-plus-redis redis-cli info memory | grep used_memory_human
```

---

## Fallback behavior

If Redis is unreachable at startup, Flask-Caching logs a warning and falls back to **NullCache** — requests still succeed, just without caching. The app does not crash.

---

## Tuning the TTL

60 seconds is a reasonable default for homelab inventory (data doesn't change every second). Adjust in `config.py`:

```python
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
```

Or override per-route:

```python
@cache.cached(timeout=10)  # 10 seconds for health-sensitive data
def health_endpoint():
    ...
```
