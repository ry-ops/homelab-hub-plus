# Host Health Checks

homelab-hub+ can ping any host in your inventory and report whether it's alive, with latency. This is exposed as an API endpoint and surfaced in the UI via the `HealthBadge` component.

---

## How it works

The health service (`backend/app/services/health.py`) tries two methods in order:

1. **ICMP ping** via `icmplib` (unprivileged mode — works without root in most environments)
2. **TCP connect to port 80** as a fallback if ICMP fails or requires elevated privileges

Each host gets a result object:

```json
{
  "host": "192.168.1.10",
  "alive": true,
  "latency_ms": 1.43,
  "method": "icmp"
}
```

If the host is unreachable by both methods, `alive` is `false` and `latency_ms` is `null`.

---

## API

### `POST /api/health-check`

Ping one or more hosts simultaneously.

**Request:**

```bash
curl -X POST http://localhost:8000/api/health-check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "hosts": ["192.168.1.1", "192.168.1.10", "pve.local"] }'
```

**Response:**

```json
{
  "192.168.1.1":  { "host": "192.168.1.1",  "alive": true,  "latency_ms": 0.81, "method": "icmp" },
  "192.168.1.10": { "host": "192.168.1.10", "alive": true,  "latency_ms": 1.43, "method": "icmp" },
  "pve.local":    { "host": "pve.local",    "alive": false, "latency_ms": null,  "method": "tcp:80" }
}
```

**Fields:**

| Field | Type | Description |
|---|---|---|
| `host` | string | The host that was checked |
| `alive` | boolean | Whether the host responded |
| `latency_ms` | float \| null | Round-trip time in milliseconds (ICMP only) |
| `method` | string | `"icmp"`, `"tcp:80"`, or `"none"` |

---

## Using via MCP (Claude)

```
health_check(hosts=["192.168.1.1", "192.168.1.10", "nas.local"])
```

Claude will return a table of results for each host.

---

## HealthBadge component

`frontend/src/components/HealthBadge.svelte` displays an inline live/dead indicator for any host. It calls `POST /api/health-check` on mount and shows:

- Green dot — host is alive
- Red dot — host unreachable
- Grey dot — checking / unknown

Usage in inventory cards:

```svelte
<HealthBadge host={item.ip_address} />
```

---

## Docker / container notes

ICMP in Docker containers requires the `NET_RAW` capability or running in host network mode. The service handles this gracefully:

- If `icmplib` raises a permissions error, it falls through to TCP
- TCP on port 80 works without any special capabilities
- If you want full ICMP support in Docker, add to `docker-compose.yml`:

```yaml
app:
  cap_add:
    - NET_RAW
```

---

## Dependency

```
icmplib==3.0.4
```

Listed in `backend/requirements.txt`. No additional system packages required for unprivileged ICMP.
