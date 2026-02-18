"""
Semantic search endpoint backed by Qdrant.

GET /api/search?q=<query>[&limit=20]

Returns ranked results with entity_type, entity_id, name, and score.
Falls back gracefully if Qdrant is unavailable.
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
