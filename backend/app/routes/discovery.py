"""
Discovery routes: subnet scan + bulk import.

POST /api/discovery/scan   — scan a CIDR block
POST /api/discovery/import — import selected hosts into inventory
"""
from __future__ import annotations

import ipaddress
import time

from flask import Blueprint, jsonify, request

from ..services.gitstore import get_store
from ..services.discovery import scan_cidr
from ..services.search import SearchService

try:
    from ..services.cache import cache as _cache
    def _invalidate_graph_cache():
        try:
            _cache.delete("map_graph")
        except Exception:
            pass
except Exception:
    def _invalidate_graph_cache():
        pass

bp = Blueprint("discovery", __name__, url_prefix="/api/discovery")

# Map suggested_type → entity type
_TYPE_MAP = {
    "hardware": "hardware",
    "apps": "apps",
    "misc": "misc",
}


@bp.route("/scan", methods=["POST"])
def scan():
    data = request.get_json(silent=True) or {}
    cidr = data.get("cidr", "").strip()

    if not cidr:
        return jsonify(error="'cidr' is required"), 400

    try:
        network = ipaddress.ip_network(cidr, strict=False)
    except ValueError as exc:
        return jsonify(error=f"Invalid CIDR: {exc}"), 400

    if network.prefixlen < 16:
        return jsonify(error="Prefix length must be >= 16 (max 65535 hosts)"), 400

    concurrency = int(data.get("concurrency", 50))
    timeout = float(data.get("timeout", 1.0))

    t0 = time.monotonic()
    hosts = scan_cidr(cidr, concurrency=concurrency, timeout=timeout)
    duration_ms = round((time.monotonic() - t0) * 1000, 1)

    alive_count = sum(1 for h in hosts if h.get("alive"))

    return jsonify(hosts=hosts, total=len(hosts), alive=alive_count, duration_ms=duration_ms)


@bp.route("/import", methods=["POST"])
def import_hosts():
    data = request.get_json(silent=True) or {}
    hosts = data.get("hosts", [])

    if not hosts:
        return jsonify(error="'hosts' list is required"), 400

    store = get_store()
    imported = 0
    by_type: dict[str, int] = {}
    errors: list[dict] = []

    for host in hosts:
        ip = host.get("ip", "")
        entity_type = _TYPE_MAP.get(host.get("type", "misc"), "misc")
        name = host.get("name") or ip
        hostname = host.get("hostname") or ip
        notes = host.get("notes", "")

        try:
            item = store.create(entity_type, {
                "name": name,
                "hostname": hostname,
                "ip_address": ip,
                "notes": notes,
            })
            SearchService.upsert(entity_type, item["id"], item)
            imported += 1
            by_type[entity_type] = by_type.get(entity_type, 0) + 1
        except Exception as exc:
            errors.append({"ip": ip, "error": str(exc)})

    if imported:
        _invalidate_graph_cache()

    return jsonify(imported=imported, by_type=by_type, errors=errors)
