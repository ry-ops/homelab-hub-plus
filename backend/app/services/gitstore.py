"""
Git-backed JSON store using the GitHub API.

Replaces SQLAlchemy/SQLite — all state is persisted as JSON files
in a GitHub repository (e.g. ry-ops/homelab-hub-state).

Directory layout:
    hardware/{id}.json
    vms/{id}.json
    apps/{id}.json
    storage/{id}.json
    shares/{id}.json
    networks/{id}.json
    documents/{id}.json
    misc/{id}.json
    _meta/counters.json        — auto-increment counters per entity type
    _meta/network_members.json — network membership records
    _meta/map_layout.json      — map node positions
    _meta/map_edges.json       — manual map edges
    _meta/relationships.json   — generic cross-entity relationships
"""
from __future__ import annotations

import base64
import json
import logging
import time
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

# Module-level singleton
_store: GitStore | None = None


def get_store() -> GitStore:
    if _store is None:
        raise RuntimeError("GitStore not initialized — call init_gitstore(app) first")
    return _store


def init_gitstore(app):
    global _store
    token = app.config.get("GITHUB_TOKEN", "")
    repo = app.config.get("GITHUB_REPO", "ry-ops/homelab-hub-state")
    branch = app.config.get("GITHUB_BRANCH", "main")
    cache_ttl = app.config.get("GITSTORE_CACHE_TTL", 300)
    _store = GitStore(repo, token, branch, cache_ttl)
    logger.info("GitStore initialized: %s@%s", repo, branch)


class GitStore:
    """GitHub-backed JSON persistence layer."""

    API = "https://api.github.com"

    def __init__(self, repo: str, token: str, branch: str = "main", cache_ttl: int = 300):
        self.repo = repo
        self.branch = branch
        self.cache_ttl = cache_ttl
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        # path -> (data, timestamp, sha)
        self._cache: dict[str, tuple[any, float, str | None]] = {}

    # ── Public CRUD ──────────────────────────────────────────────────

    def list_all(self, entity_type: str) -> list[dict]:
        """List all entities of a given type."""
        cache_key = f"__dir__{entity_type}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.API}/repos/{self.repo}/contents/{entity_type}"
        resp = self._session.get(url, params={"ref": self.branch})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()

        items = []
        for entry in resp.json():
            if not entry["name"].endswith(".json"):
                continue
            item = self._read_file(entry["path"])
            if item is not None:
                items.append(item[0])

        self._cache_set(cache_key, items)
        return items

    def get(self, entity_type: str, entity_id: int) -> dict | None:
        """Get a single entity by type and ID."""
        path = f"{entity_type}/{entity_id}.json"
        result = self._read_file(path)
        return result[0] if result else None

    def create(self, entity_type: str, data: dict) -> dict:
        """Create a new entity, auto-assigning an ID."""
        entity_id = self._next_id(entity_type)
        now = datetime.now(timezone.utc).isoformat()

        # Strip read-only fields from input
        clean = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}
        clean["id"] = entity_id
        clean["created_at"] = now
        clean["updated_at"] = now

        path = f"{entity_type}/{entity_id}.json"
        self._write_file(path, clean, f"Create {entity_type}/{entity_id}")
        self._invalidate_dir(entity_type)
        return clean

    def update(self, entity_type: str, entity_id: int, data: dict) -> dict | None:
        """Update an existing entity. Returns updated dict or None if not found."""
        path = f"{entity_type}/{entity_id}.json"
        result = self._read_file(path)
        if result is None:
            return None

        existing, sha = result
        now = datetime.now(timezone.utc).isoformat()

        # Merge — don't overwrite id, created_at
        for k, v in data.items():
            if k not in ("id", "created_at", "updated_at"):
                existing[k] = v
        existing["updated_at"] = now

        self._write_file(path, existing, f"Update {entity_type}/{entity_id}", sha=sha)
        self._invalidate_dir(entity_type)
        return existing

    def delete(self, entity_type: str, entity_id: int) -> bool:
        """Delete an entity. Returns True if deleted, False if not found."""
        path = f"{entity_type}/{entity_id}.json"
        result = self._read_file(path)
        if result is None:
            return False

        _, sha = result
        self._delete_file(path, f"Delete {entity_type}/{entity_id}", sha)
        self._invalidate_dir(entity_type)
        return True

    def create_with_id(self, entity_type: str, entity_id: int, data: dict) -> dict:
        """Create an entity with a specific ID (used for import)."""
        now = datetime.now(timezone.utc).isoformat()
        clean = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}
        clean["id"] = entity_id
        clean["created_at"] = data.get("created_at", now)
        clean["updated_at"] = data.get("updated_at", now)

        path = f"{entity_type}/{entity_id}.json"
        self._write_file(path, clean, f"Import {entity_type}/{entity_id}")
        return clean

    def delete_all(self, entity_type: str) -> int:
        """Delete all entities of a type. Returns count deleted."""
        url = f"{self.API}/repos/{self.repo}/contents/{entity_type}"
        resp = self._session.get(url, params={"ref": self.branch})
        if resp.status_code == 404:
            return 0
        resp.raise_for_status()

        count = 0
        for entry in resp.json():
            if entry["name"].endswith(".json"):
                self._delete_file(entry["path"], f"Clear {entity_type}/{entry['name']}", entry["sha"])
                count += 1
        self._invalidate_dir(entity_type)
        return count

    # ── Special files (arrays stored as single JSON files) ───────────

    def get_special(self, filename: str) -> list[dict]:
        """Read a special array file from _meta/."""
        path = f"_meta/{filename}"
        result = self._read_file(path)
        if result is None:
            return []
        data, _ = result
        return data if isinstance(data, list) else []

    def put_special(self, filename: str, data: list[dict], message: str) -> None:
        """Write a special array file to _meta/."""
        path = f"_meta/{filename}"
        existing = self._read_file(path)
        sha = existing[1] if existing else None
        self._write_file(path, data, message, sha=sha)

    # ── ID management ────────────────────────────────────────────────

    def _next_id(self, entity_type: str) -> int:
        path = "_meta/counters.json"
        result = self._read_file(path)
        if result is None:
            counters = {}
            sha = None
        else:
            counters, sha = result

        current = counters.get(entity_type, 0)
        next_val = current + 1
        counters[entity_type] = next_val
        self._write_file(path, counters, f"Increment {entity_type} counter to {next_val}", sha=sha)
        return next_val

    def set_counter(self, entity_type: str, value: int) -> None:
        """Set counter for an entity type (used during import)."""
        path = "_meta/counters.json"
        result = self._read_file(path)
        if result is None:
            counters = {}
            sha = None
        else:
            counters, sha = result
        counters[entity_type] = value
        self._write_file(path, counters, f"Set {entity_type} counter to {value}", sha=sha)

    # ── GitHub API primitives ────────────────────────────────────────

    def _read_file(self, path: str) -> tuple[dict | list, str] | None:
        """Read a JSON file. Returns (parsed_content, sha) or None."""
        cached = self._cache_get(path)
        if cached is not None:
            return cached

        url = f"{self.API}/repos/{self.repo}/contents/{path}"
        resp = self._session.get(url, params={"ref": self.branch})
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

        file_data = resp.json()
        content = base64.b64decode(file_data["content"])
        parsed = json.loads(content)
        sha = file_data["sha"]
        self._cache_set(path, (parsed, sha))
        return parsed, sha

    def _write_file(self, path: str, content: any, message: str, sha: str | None = None) -> str:
        """Create or update a JSON file. Returns new sha."""
        url = f"{self.API}/repos/{self.repo}/contents/{path}"
        encoded = base64.b64encode(json.dumps(content, indent=2, default=str).encode()).decode()
        body = {
            "message": message,
            "content": encoded,
            "branch": self.branch,
        }
        if sha:
            body["sha"] = sha

        resp = self._session.put(url, json=body)
        resp.raise_for_status()
        new_sha = resp.json()["content"]["sha"]
        # Update cache
        self._cache_set(path, (content, new_sha))
        return new_sha

    def _delete_file(self, path: str, message: str, sha: str) -> None:
        """Delete a file from the repo."""
        url = f"{self.API}/repos/{self.repo}/contents/{path}"
        body = {
            "message": message,
            "sha": sha,
            "branch": self.branch,
        }
        resp = self._session.delete(url, json=body)
        resp.raise_for_status()
        self._cache.pop(path, None)

    # ── Cache helpers ────────────────────────────────────────────────

    def _cache_get(self, key: str):
        entry = self._cache.get(key)
        if entry is None:
            return None
        data, ts, _ = entry
        if time.time() - ts > self.cache_ttl:
            del self._cache[key]
            return None
        return data

    def _cache_set(self, key: str, value):
        if isinstance(value, tuple):
            data, sha = value
            self._cache[key] = (data, time.time(), sha)
        else:
            self._cache[key] = (value, time.time(), None)

    def _invalidate_dir(self, entity_type: str):
        """Invalidate the directory listing cache for an entity type."""
        self._cache.pop(f"__dir__{entity_type}", None)
