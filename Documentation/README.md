# homelab-hub+ Documentation

This folder contains in-depth documentation for everything added in the **homelab-hub+** fork. For a high-level overview, see the [project README](../README.md).

---

## Contents

| Document | What it covers |
|---|---|
| [Authentication](./authentication.md) | Bearer token setup, dev mode, how the middleware works |
| [Redis Caching](./redis.md) | Cache configuration, TTLs, manual invalidation, Docker setup |
| [Qdrant Semantic Search](./qdrant.md) | Vector search setup, embedding model, backfill, query API |
| [Host Health Checks](./health-checks.md) | ICMP/TCP ping service, API usage, HealthBadge component |
| [MCP Server](./mcp-server.md) | Full MCP tool reference, Claude Desktop + Claude Code setup, config |
| [CI/CD Pipeline](./cicd.md) | GitHub Actions workflow, secrets, multi-arch builds, tagging strategy |
| [Auto-Discovery](./auto-discovery.md) | Subnet/CIDR scanning, fingerprinting, bulk import, MCP tool |

---

## Quick links

- [Project README](../README.md)
- [docker-compose.yml](../docker-compose.yml)
- [MCP source](../mcp/src/)
- [Backend middleware](../backend/app/middleware/)
- [Backend services](../backend/app/services/)
