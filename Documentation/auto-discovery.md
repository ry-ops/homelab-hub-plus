# Auto-Discovery: Subnet / CIDR Scanning

Scan an entire subnet, fingerprint every live host with port probing and banner grabbing, then selectively import results straight into your inventory — all from the UI or via the MCP server.

---

## How it works

```
scan_cidr(cidr)
  └─ per IP (thread pool, default 50 workers):
       1. ping_host(ip)              ← ICMP then TCP:80 fallback
       2. socket.gethostbyaddr(ip)   ← reverse DNS
       3. TCP connect to 12 ports    ← collect open ports
       4. Banner grab:
            port 22        → raw socket → SSH identification string
            port 80/443/…  → HTTP GET  → <title> parse
       5. fingerprint_host()         ← map ports+banners → label + type
```

All code is pure Python stdlib — no new pip dependencies.

---

## Fingerprint rules

Rules are evaluated in priority order. The first match wins.

| Open ports | Fingerprint | Suggested type |
|---|---|---|
| 8006 | Proxmox VE | hardware |
| 9090 | Cockpit | hardware |
| 6443 | Kubernetes API | misc |
| 5900 | VNC Host | hardware |
| 22 (no HTTP) | SSH Host | hardware |
| 80 or 443 | Web Server | apps |
| any | Unknown | misc |

---

## UI walkthrough

1. Click **Discover** (purple button) in the header.
2. Enter a CIDR block such as `192.168.1.0/24`.
3. Adjust concurrency and timeout sliders if needed.
4. Click **Scan** — a spinner shows while the backend probes the subnet.
5. The results table appears with columns:
   - Checkbox (pre-selected for alive hosts)
   - IP · Hostname · Fingerprint · Open Ports
   - **Type** dropdown (editable per row)
   - **Name** text field (pre-filled from reverse DNS or IP)
6. Toggle **Show dead hosts** to see the full subnet picture.
7. Click **All alive / None** to bulk-select.
8. Click **Import N selected** → hosts land in inventory and a toast confirms the result.

---

## API reference

### `POST /api/discovery/scan`

Scan a CIDR block.

**Request body**

```json
{
  "cidr": "192.168.1.0/24",
  "concurrency": 50,
  "timeout": 1.0
}
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `cidr` | string | required | Must be valid CIDR, prefix ≥ /16 |
| `concurrency` | integer | 50 | Parallel probe threads |
| `timeout` | float | 1.0 | Per-probe socket timeout (seconds) |

**Response**

```json
{
  "hosts": [
    {
      "ip": "192.168.1.42",
      "alive": true,
      "latency_ms": 1.2,
      "hostname": "pve.local",
      "open_ports": [22, 8006],
      "services": {"22": "SSH", "8006": "Proxmox"},
      "http_title": "Proxmox Virtual Environment",
      "ssh_banner": "SSH-2.0-OpenSSH_9.2",
      "fingerprint": "Proxmox VE",
      "suggested_type": "hardware",
      "suggested_name": "pve.local"
    }
  ],
  "total": 254,
  "alive": 12,
  "duration_ms": 3821.4
}
```

Dead hosts are included (`alive: false`, minimal fields) so you see the complete subnet picture.

---

### `POST /api/discovery/import`

Import selected hosts into inventory.

**Request body**

```json
{
  "hosts": [
    {
      "ip": "192.168.1.42",
      "type": "hardware",
      "name": "pve.local",
      "hostname": "pve.local",
      "notes": "Fingerprint: Proxmox VE\nOpen ports: 22, 8006"
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `ip` | string | Required |
| `type` | string | `hardware`, `vms`, `apps`, `storage`, `networks`, `misc` |
| `name` | string | Display name |
| `hostname` | string | Hostname or IP |
| `notes` | string | Optional freeform notes |

**Response**

```json
{
  "imported": 3,
  "by_type": {"hardware": 2, "misc": 1},
  "errors": []
}
```

---

## MCP tool reference

### `discover_subnet`

Exposes the scan (and optional auto-import) to Claude.

**Input schema**

```json
{
  "cidr": "192.168.1.0/24",
  "concurrency": 50,
  "timeout": 1.0,
  "import_alive": false
}
```

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `cidr` | string | required | CIDR block |
| `concurrency` | number | 50 | Parallel threads |
| `timeout` | number | 1.0 | Seconds per probe |
| `import_alive` | boolean | false | If true, auto-imports all alive hosts |

**Example prompts**

```
Scan 192.168.1.0/24 and tell me what you find.

Scan 10.0.0.0/24 and automatically import every alive host.

What fingerprint is 192.168.1.100?
```

When `import_alive=false` the tool returns the raw scan result.
When `import_alive=true` it returns `{ scan: {...}, import: {...} }`.

---

## CIDR size limits

| Prefix | Hosts | Notes |
|---|---|---|
| /32 | 1 | Single host (allowed) |
| /24 | 254 | Typical home subnet |
| /22 | 1 022 | ~20 s at default settings |
| /20 | 4 094 | ~80 s at default settings |
| /16 | 65 534 | Maximum allowed by the API |
| /15 | 131 070 | **Rejected** (prefix must be ≥ /16) |

---

## Docker / container notes

ICMP (raw ping) inside Docker requires one of:

- `--cap-add NET_ADMIN` (preferred)
- `--network host`
- `privileged: true`

The backend `ping_host()` function falls back to `TCP:80` if ICMP is unavailable, so discovery still works — it just can't measure latency for hosts that don't have port 80 open.

If you see all hosts reported as dead, check the backend container's network capabilities:

```bash
docker compose exec backend python -c "from icmplib import ping; print(ping('8.8.8.8', count=1, privileged=False))"
```

---

## curl examples

```bash
TOKEN="your-api-token"

# Scan
curl -s -X POST http://localhost:8000/api/discovery/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cidr":"192.168.1.0/24"}' | jq .

# Import one host
curl -s -X POST http://localhost:8000/api/discovery/import \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hosts":[{"ip":"192.168.1.42","type":"hardware","name":"pve","hostname":"pve.local"}]}' | jq .
```
