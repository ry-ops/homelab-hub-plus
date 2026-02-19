# MCP Server

The `mcp/` directory contains a standalone [Model Context Protocol](https://modelcontextprotocol.io) server that gives Claude Desktop and Claude Code direct, structured access to your homelab inventory.

Once registered, you can ask Claude things like:

> "List all my VMs and check if their host IPs are reachable."

> "Create a new hardware entry for my new Raspberry Pi 5 — 8GB RAM, ARM64."

> "Search my inventory for anything related to Proxmox and summarize what I have."

---

## Architecture

```
Claude Desktop / Claude Code
         │  StdioTransport (JSON-RPC over stdin/stdout)
         ▼
  homelab-hub-mcp (Node.js)
         │  HTTP + Bearer token
         ▼
  Flask API (homelab-hub-plus)
         │
         ▼
  SQLite / Redis / Qdrant
```

The MCP server is a thin translation layer — it holds no state of its own. Every tool call becomes an authenticated HTTP request to your Flask backend.

---

## Prerequisites

- Node.js 18+
- The homelab-hub-plus backend running and reachable
- Your `API_TOKEN` (from `.env`)

---

## Build

```bash
cd mcp
npm install
npm run build
```

This compiles TypeScript to `mcp/dist/`. The compiled output is what `bin/cli.js` imports.

To rebuild after making changes to `src/`:

```bash
npm run build
# or watch mode during development:
npm run dev
```

---

## Configuration

The server reads config from two sources, in priority order:

### 1. Environment variables (highest priority)

| Variable | Description |
|---|---|
| `HOMELAB_URL` | Base URL of your Flask backend, e.g. `http://192.168.1.100:8000` |
| `HOMELAB_TOKEN` | Bearer token (same value as `API_TOKEN` in your `.env`) |

### 2. Config file (fallback)

`~/.config/homelab-hub/config.json`

```json
{
  "url": "http://192.168.1.100:8000",
  "token": "a771885feea9aaf0e8400ac24b2fab34bb2ad76ef9dcb1a8"
}
```

Create or update it with:

```bash
mkdir -p ~/.config/homelab-hub
cat > ~/.config/homelab-hub/config.json <<EOF
{
  "url": "http://192.168.1.100:8000",
  "token": "your-token-here"
}
EOF
```

### Verify config

```bash
node mcp/bin/cli.js status
# HOMELAB_URL : http://192.168.1.100:8000
# Token set   : yes
```

---

## Claude Desktop registration

Add this to `~/.config/claude/claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "homelab-hub": {
      "command": "node",
      "args": ["/Users/ryandahlberg/Projects/homelab-hub-plus/mcp/bin/cli.js"],
      "env": {
        "HOMELAB_URL": "http://192.168.1.100:8000",
        "HOMELAB_TOKEN": "a771885feea9aaf0e8400ac24b2fab34bb2ad76ef9dcb1a8"
      }
    }
  }
}
```

Restart Claude Desktop after saving. You should see **homelab-hub** appear in the tools panel.

---

## Claude Code registration

Add to your project's `.mcp.json` or run:

```bash
claude mcp add homelab-hub \
  --command "node" \
  --args "/path/to/homelab-hub-plus/mcp/bin/cli.js" \
  --env HOMELAB_URL=http://192.168.1.100:8000 \
  --env HOMELAB_TOKEN=your-token
```

---

## Tool reference

### `inventory_list`

List all entities of a given type.

| Parameter | Type | Required | Values |
|---|---|---|---|
| `type` | string | yes | `hardware`, `vms`, `apps`, `storage`, `networks`, `misc`, `shares`, `documents` |

**Maps to:** `GET /api/{type}`

**Example prompt:** *"List all my hardware."*

---

### `inventory_search`

Semantic search across all entity types using Qdrant vector similarity.

| Parameter | Type | Required | Default |
|---|---|---|---|
| `q` | string | yes | — |
| `limit` | number | no | 20 |

**Maps to:** `GET /api/search?q=&limit=`

**Example prompt:** *"Search my inventory for anything related to storage or NAS."*

Returns ranked results with `entity_type`, `entity_id`, `name`, and `score`.

---

### `inventory_create`

Create a new entity.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | Entity type |
| `data` | object | yes | Entity fields |

**Maps to:** `POST /api/{type}`

**Example prompt:** *"Add a new VM called 'pihole' — Ubuntu 22.04, 1 vCPU, 512MB RAM, running on hardware ID 2."*

**Example tool call:**
```json
{
  "type": "vms",
  "data": {
    "name": "pihole",
    "os": "Ubuntu 22.04",
    "cpu_cores": 1,
    "ram_gb": 0.5,
    "hardware_id": 2
  }
}
```

---

### `inventory_update`

Update an existing entity by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | Entity type |
| `id` | number | yes | Entity ID |
| `data` | object | yes | Fields to update (partial OK) |

**Maps to:** `PUT /api/{type}/{id}`

**Example prompt:** *"Update hardware ID 3 — change RAM to 64GB."*

---

### `inventory_delete`

Delete an entity. Requires explicit confirmation.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | Entity type |
| `id` | number | yes | Entity ID |
| `confirm` | boolean | yes | Must be `true` to proceed |

**Maps to:** `DELETE /api/{type}/{id}`

The `confirm: true` requirement is a safety guard — if Claude calls this tool without it explicitly set, the server returns an error instead of deleting.

**Example prompt:** *"Delete VM ID 7, I've confirmed this is safe."*

---

### `health_check`

Ping one or more hosts and return alive/latency status.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `hosts` | string[] | yes | IP addresses or hostnames |

**Maps to:** `POST /api/health-check`

**Example prompt:** *"Check if 192.168.1.1, 192.168.1.10, and nas.local are reachable."*

**Example response:**
```json
{
  "192.168.1.1":  { "alive": true,  "latency_ms": 0.8,  "method": "icmp" },
  "192.168.1.10": { "alive": true,  "latency_ms": 1.2,  "method": "icmp" },
  "nas.local":    { "alive": false, "latency_ms": null,  "method": "tcp:80" }
}
```

---

### `search_index`

Trigger a full Qdrant backfill of all existing inventory entities. Idempotent — safe to run multiple times.

No parameters required.

**Maps to:** `POST /api/search/index`

**Example prompt:** *"Reindex all my inventory in Qdrant."*

**Example response:**
```json
{
  "indexed": 42,
  "by_type": { "hardware": 5, "vms": 12, "apps": 8, ... },
  "errors": [],
  "status": "ok"
}
```

---

### `map_graph`

Retrieve the full infrastructure map as a graph of nodes and edges.

No parameters required.

**Maps to:** `GET /api/map/graph`

**Example prompt:** *"Show me my infrastructure map graph."*

---

### `app_status`

Check whether the homelab-hub-plus backend is healthy.

No parameters required.

**Maps to:** `GET /api/health`

**Example prompt:** *"Is the homelab-hub backend up?"*

**Response:** `{ "status": "ok" }`

---

### `inventory_all`

Fetch all inventory across all entity types in a single call.

No parameters required.

**Maps to:** `GET /api/inventory`

**Example prompt:** *"Give me a complete snapshot of everything in my homelab inventory."*

Returns a nested object keyed by entity type.

---

## Example Claude conversations

**Auditing your lab:**
> "Use inventory_all to get everything, then health_check on all IP addresses you find. Give me a summary of what's alive and what's not."

**Keeping things tidy:**
> "Search for anything with 'test' in the name. List them and ask me which ones I want to delete."

**Adding a new machine:**
> "I just got a new mini PC — Intel N100, 16GB RAM, 512GB NVMe, running Proxmox. Add it to hardware."

**Disaster recovery prep:**
> "Get my full inventory and format it as a markdown table grouped by type."

---

## CLI commands

```bash
# Start the MCP server (used by Claude Desktop — you rarely run this directly)
node mcp/bin/cli.js start

# Check current config
node mcp/bin/cli.js status

# With env override
HOMELAB_URL=http://192.168.1.100:8000 node mcp/bin/cli.js status
```

---

## Source files

| File | Purpose |
|---|---|
| `mcp/src/server.ts` | Tool definitions and MCP request handlers |
| `mcp/src/client.ts` | HTTP client — sends authenticated requests to Flask |
| `mcp/src/config.ts` | Loads config from env vars then `~/.config/homelab-hub/config.json` |
| `mcp/src/index.ts` | Public exports |
| `mcp/bin/cli.js` | CLI entry point (`start` / `status` commands) |
