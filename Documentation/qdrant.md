# Qdrant Semantic Search

homelab-hub+ replaces the original keyword filter search with full semantic (vector) search powered by [Qdrant](https://qdrant.tech/) and [sentence-transformers](https://www.sbert.net/).

---

## How it works

When an entity is created or updated, its fields are flattened into a text blob and embedded using the `all-MiniLM-L6-v2` model (384-dimensional vectors). The vector is stored in Qdrant alongside a payload containing `entity_type`, `entity_id`, and `name`.

At query time the search string is embedded the same way and Qdrant returns the closest vectors by cosine similarity.

```
"old nas box basement"
        ↓ embed (384-dim)
    Qdrant cosine search
        ↓
[{ entity_type: "storage", entity_id: 3, name: "Synology NAS", score: 0.91 }, ...]
```

This means queries like `"noisy server near the router"` can find an entity whose name is just `"Dell R720"` — as long as the notes or other fields contain those words.

---

## Embedding model

| Property | Value |
|---|---|
| Model | `all-MiniLM-L6-v2` |
| Dimensions | 384 |
| Size on disk | ~80 MB |
| Hardware | CPU-only, no GPU required |
| Distance metric | Cosine similarity |

The model is downloaded on first use and cached by sentence-transformers in `~/.cache/huggingface/`.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant HTTP API URL |
| `QDRANT_COLLECTION` | `homelab` | Collection name |

In `docker-compose.yml`:

```yaml
environment:
  - QDRANT_URL=http://qdrant:6333
  - QDRANT_COLLECTION=homelab
```

---

## Docker setup

Qdrant runs as a sidecar container:

```yaml
qdrant:
  image: qdrant/qdrant:latest
  container_name: homelab-hub-plus-qdrant
  ports:
    - "6333:6333"   # HTTP REST API
    - "6334:6334"   # gRPC API
  volumes:
    - qdrant_data:/qdrant/storage
  restart: unless-stopped
```

Vector data is persisted to the `qdrant_data` named volume. The collection is created automatically on first use.

---

## Entity types indexed

All 8 entity types are indexed:

| Type | Namespace prefix |
|---|---|
| `hardware` | 1 × 10,000,000 + id |
| `vms` | 2 × 10,000,000 + id |
| `apps` | 3 × 10,000,000 + id |
| `storage` | 4 × 10,000,000 + id |
| `networks` | 5 × 10,000,000 + id |
| `misc` | 6 × 10,000,000 + id |
| `shares` | 7 × 10,000,000 + id |
| `documents` | 8 × 10,000,000 + id |

The namespace formula ensures point IDs are unique across types even though each entity type has its own auto-increment ID sequence.

---

## Backfill (indexing existing data)

Entities created before Qdrant was added are not in the vector store. Run the backfill:

### Via the UI

Click **Reindex Search** in the header. The button disables while the job runs and shows a toast on completion.

### Via the API

```bash
curl -X POST http://localhost:8000/api/search/index \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{
  "indexed": 42,
  "by_type": {
    "hardware": 5,
    "vms": 12,
    "apps": 8,
    "storage": 3,
    "networks": 4,
    "misc": 2,
    "shares": 6,
    "documents": 2
  },
  "errors": [],
  "status": "ok"
}
```

The backfill is **idempotent** — running it multiple times will upsert (overwrite) existing vectors without creating duplicates. Safe to run any time.

### Via MCP (Claude)

```
search_index()
```

---

## Search API

### `GET /api/search`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `q` | string | required | Natural language query |
| `limit` | integer | 20 | Max results (capped at 100) |

```bash
curl "http://localhost:8000/api/search?q=hypervisor+running+vms&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{
  "data": [
    { "entity_type": "hardware", "entity_id": 2, "name": "Proxmox Node", "score": 0.9312 },
    { "entity_type": "vms", "entity_id": 7, "name": "Ubuntu VM", "score": 0.8741 }
  ],
  "count": 2
}
```

Results are ranked by cosine similarity score (0–1, higher is better).

---

## Automatic indexing on writes

The CRUD factory upserts into Qdrant on every `POST` and `PUT`, and deletes from Qdrant on every `DELETE`. You don't need to manually reindex after normal operations — the backfill is only needed for data that existed before the search service was added.

---

## Fallback behavior

If Qdrant is unreachable, `SearchService.query()` catches the exception, logs it, and returns an empty list. The app continues to function; search just returns no results.

---

## Checking Qdrant health

```bash
# REST API health
curl http://localhost:6333/healthz

# Collection info
curl http://localhost:6333/collections/homelab

# Count vectors
curl http://localhost:6333/collections/homelab/points/count \
  -H "Content-Type: application/json" \
  -d '{"exact": true}'
```

Or open the Qdrant Web UI at `http://localhost:6333/dashboard`.

---

## Clearing the index

To wipe and rebuild from scratch:

```bash
# Delete the collection
curl -X DELETE http://localhost:6333/collections/homelab

# Re-run the backfill — collection is recreated automatically
curl -X POST http://localhost:8000/api/search/index \
  -H "Authorization: Bearer $TOKEN"
```
