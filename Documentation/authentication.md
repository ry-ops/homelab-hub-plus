# Authentication

homelab-hub+ protects its API with a shared Bearer token. The system is designed to be zero-friction in development and secure in production.

---

## How it works

All `/api/*` routes pass through a Flask `before_request` hook defined in `backend/app/middleware/auth.py`. The hook:

1. Checks whether the request path starts with `/api/`
2. Skips public endpoints (see below)
3. Reads `API_TOKEN` from the app config
4. If `API_TOKEN` is empty → **dev mode**, all requests pass
5. If set → requires an `Authorization: Bearer <token>` header; returns `401` if missing, `403` if wrong

### Public endpoints (no token required)

| Path | Why it's public |
|---|---|
| `GET /api/health` | Uptime monitoring — must be reachable without auth |
| `GET /api/config` | Lets the frontend discover whether auth is required at startup |

---

## Dev mode (no token)

If `API_TOKEN` is unset or empty, **every API request passes through with no auth check**. This is intentional — during local development you don't want to manage tokens.

```bash
# Dev mode — just run without setting API_TOKEN
python wsgi.py
```

`GET /api/config` will return `{ "requiresAuth": false }` in this state, so the frontend knows not to prompt for a token.

---

## Production setup

### 1. Generate a token

```bash
openssl rand -hex 24
# example output: a771885feea9aaf0e8400ac24b2fab34bb2ad76ef9dcb1a8
```

### 2. Write to `.env`

```bash
echo "API_TOKEN=<your-token>" > .env
```

`.env` is gitignored — it will never be committed.

### 3. Start the stack

```bash
docker compose --env-file .env up -d
```

Docker Compose passes `API_TOKEN` into the container via the environment block in `docker-compose.yml`:

```yaml
environment:
  - API_TOKEN=${API_TOKEN:-}
```

The `:-` fallback means if `API_TOKEN` is not in the environment, it defaults to an empty string (dev mode).

---

## Using the token in the browser

1. Open `http://localhost:8000`
2. Click the **⚙** button in the top-right header
3. Paste your token into the input and click **Save**

The token is stored in `localStorage` under the key `homelab_api_token` and injected automatically into every API request via the `Authorization: Bearer` header in `frontend/src/lib/api.js`.

To clear the token, open the ⚙ modal, blank the field, and save.

---

## Using the token in curl

```bash
TOKEN="a771885feea9aaf0e8400ac24b2fab34bb2ad76ef9dcb1a8"

# List all hardware
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/hardware

# Export inventory
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/inventory/export -o backup.json
```

---

## Using the token with the MCP server

Set `HOMELAB_TOKEN` as an environment variable (see [MCP Server docs](./mcp-server.md)):

```json
{
  "mcpServers": {
    "homelab-hub": {
      "command": "node",
      "args": ["/path/to/mcp/bin/cli.js"],
      "env": {
        "HOMELAB_URL": "http://192.168.1.100:8000",
        "HOMELAB_TOKEN": "a771885feea9aaf0e8400ac24b2fab34bb2ad76ef9dcb1a8"
      }
    }
  }
}
```

---

## Response codes

| Code | Meaning |
|---|---|
| `401 Unauthorized` | No `Authorization` header, or header doesn't start with `Bearer ` |
| `403 Forbidden` | Token present but incorrect |

---

## Middleware source

`backend/app/middleware/auth.py`

```python
PUBLIC_PATHS = {"/api/health", "/api/config"}

def register_auth_middleware(app):
    @app.before_request
    def check_auth():
        if not request.path.startswith("/api/"):
            return
        if request.path in PUBLIC_PATHS:
            return
        api_token = current_app.config.get("API_TOKEN") or ""
        if not api_token:
            return  # dev mode
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(error="Unauthorized"), 401
        if auth_header[len("Bearer "):] != api_token:
            return jsonify(error="Forbidden"), 403
```
