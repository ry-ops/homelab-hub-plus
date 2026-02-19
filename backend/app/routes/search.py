"""
Semantic search endpoint backed by Qdrant.

GET /api/search?q=<query>[&limit=20]

Returns ranked results with entity_type, entity_id, name, and score.
Falls back gracefully if Qdrant is unavailable.

POST /api/search/index

One-time (idempotent) backfill of all existing entities into Qdrant.
Returns { indexed, by_type, errors, status }.
"""
from flask import Blueprint, jsonify, request

from ..services.search import SearchService

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
    from ..models import Hardware, VM, AppService, Storage, Share, Network, Misc, Document

    entity_map = {
        "hardware": Hardware,
        "vms": VM,
        "apps": AppService,
        "storage": Storage,
        "networks": Network,
        "misc": Misc,
        "shares": Share,
        "documents": Document,
    }

    indexed = 0
    by_type = {}
    errors = []

    for entity_type, model in entity_map.items():
        count = 0
        try:
            items = model.query.all()
            for item in items:
                try:
                    SearchService.upsert(entity_type, item.id, item.to_dict())
                    count += 1
                except Exception as e:
                    errors.append({"type": entity_type, "id": item.id, "error": str(e)})
        except Exception as e:
            errors.append({"type": entity_type, "error": str(e)})
        by_type[entity_type] = count
        indexed += count

    status = "ok" if not errors else "partial"
    return jsonify(indexed=indexed, by_type=by_type, errors=errors, status=status)
