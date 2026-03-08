"""
Semantic search endpoint backed by Qdrant.

GET /api/search?q=<query>[&limit=20]
POST /api/search/index
"""
from flask import Blueprint, jsonify, request

from ..services.search import SearchService
from ..services.gitstore import get_store

bp = Blueprint("search", __name__, url_prefix="/api/search")


@bp.route("", methods=["GET"])
def semantic_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify(data=[], count=0)

    limit = min(int(request.args.get("limit", 20)), 100)
    results = SearchService.query(q, limit=limit)
    return jsonify(data=results, count=len(results))


@bp.route("/index", methods=["POST"])
def index_all():
    """Backfill all existing entities into Qdrant (idempotent)."""
    store = get_store()
    entity_types = ["hardware", "vms", "apps", "storage", "networks", "misc", "shares", "documents"]

    indexed = 0
    by_type = {}
    errors = []

    for etype in entity_types:
        count = 0
        try:
            items = store.list_all(etype)
            for item in items:
                try:
                    SearchService.upsert(etype, item["id"], item)
                    count += 1
                except Exception as e:
                    errors.append({"type": etype, "id": item.get("id"), "error": str(e)})
        except Exception as e:
            errors.append({"type": etype, "error": str(e)})
        by_type[etype] = count
        indexed += count

    status = "ok" if not errors else "partial"
    return jsonify(indexed=indexed, by_type=by_type, errors=errors, status=status)
