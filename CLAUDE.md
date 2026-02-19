# homelab-hub-plus

A self-hosted homelab inventory dashboard — Flask + Svelte + SQLite — extended with Redis caching, Qdrant semantic search, Bearer token auth, subnet auto-discovery, and an MCP server for Claude AI control.

## Project structure

```
backend/          Flask API (Python 3.14)
  app/
    middleware/   Bearer token auth
    models/       SQLAlchemy models
    routes/       Flask blueprints (CRUD factory + custom)
    services/     cache.py, search.py, health.py, discovery.py
  migrations/     Alembic
frontend/         Svelte 4 SPA (Vite)
  src/
    components/   Layout, DiscoveryModal, HealthBadge, map/, inventory/
    lib/          api.js (central fetch + auth), stores.js
    pages/        InventoryPage, MapPage, DocsPage
mcp/              MCP server (TypeScript/Node)
  src/
    server.ts     11 tools — inventory CRUD, search, health, discovery
    client.ts     HTTP client → Flask API
    config.ts     HOMELAB_URL / HOMELAB_TOKEN config
  bin/cli.js      CLI entry point
.github/
  workflows/
    docker-publish.yml   Multi-arch Docker build + push
```

## Development

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python wsgi.py          # :5001

# Frontend
cd frontend
npm install
npm run dev             # :3000, proxies /api → :5001

# MCP server
cd mcp
npm install
npm run build
node bin/cli.js status
```

## Docker (full stack)

```bash
echo "API_TOKEN=$(openssl rand -hex 24)" > .env
docker compose --env-file .env up -d --build
# → http://localhost:8000
```

## Key patterns

- **CRUD factory**: `backend/app/routes/_crud_factory.py` generates standard REST endpoints; override per-route for custom logic
- **Auth**: `API_TOKEN` env var; unset = dev passthrough; set = Bearer required on all `/api/*`
- **Cache**: Flask-Caching + Redis; invalidate with `cache.delete("map_graph")` on writes
- **Search**: `SearchService.upsert(type, id, dict)` / `.delete(type, id)` — call on every write
- **Toast**: `addToast(message, type)` from `frontend/src/lib/stores.js`
- **MCP tools**: add to `TOOLS` array in `mcp/src/server.ts` + matching `case` in `executeTool()`

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:////data/homelab-hub.db` | SQLAlchemy URI |
| `REDIS_URL` | `redis://redis:6379/0` | Flask-Caching backend |
| `QDRANT_URL` | `http://qdrant:6333` | Vector search |
| `QDRANT_COLLECTION` | `homelab` | Collection name |
| `API_TOKEN` | _(empty = dev mode)_ | Bearer token |

## Aiana integration

Aiana is available as an MCP server for conversation memory. Use her proactively:

- `memory_recall` — get context about homelab-hub-plus from past sessions
- `memory_search` — search past conversations for relevant info
- `memory_add` — save important decisions or patterns

When working on homelab-hub-plus, check Aiana for:
- Previous architecture decisions
- Patterns established in past sessions
- User preferences for this project
