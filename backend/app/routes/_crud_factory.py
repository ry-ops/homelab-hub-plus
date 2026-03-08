from flask import Blueprint, jsonify, request

from ..services.gitstore import get_store
from ..services.cache import cache
from ..services.search import SearchService


def create_crud_blueprint(name, entity_type=None, url_prefix=None, detail_route=True):
    """Generate a Flask Blueprint with standard CRUD endpoints backed by GitStore.

    Automatically:
    - Invalidates the map graph cache on writes
    - Upserts/deletes Qdrant vectors on writes
    """
    etype = entity_type or name
    prefix = url_prefix or f"/api/{name}"
    bp = Blueprint(name, __name__, url_prefix=prefix)

    @bp.route("", methods=["GET"])
    def list_items():
        store = get_store()
        items = store.list_all(etype)
        return jsonify(data=items, count=len(items))

    if detail_route:
        @bp.route("/<int:item_id>", methods=["GET"])
        def get_item(item_id):
            store = get_store()
            item = store.get(etype, item_id)
            if item is None:
                return jsonify(error="Not found"), 404
            return jsonify(data=item)

    @bp.route("", methods=["POST"])
    def create_item():
        data = request.get_json()
        if not data:
            return jsonify(error="Request body required"), 400
        try:
            store = get_store()
            item = store.create(etype, data)
            _invalidate_graph_cache()
            SearchService.upsert(name, item["id"], item)
            return jsonify(data=item), 201
        except Exception as e:
            print(f"Error creating {etype}: {str(e)}")
            return jsonify(error=str(e)), 500

    @bp.route("/<int:item_id>", methods=["PUT"])
    def update_item(item_id):
        store = get_store()
        existing = store.get(etype, item_id)
        if existing is None:
            return jsonify(error="Not found"), 404
        data = request.get_json()
        if not data:
            return jsonify(error="Request body required"), 400
        try:
            item = store.update(etype, item_id, data)
            _invalidate_graph_cache()
            SearchService.upsert(name, item["id"], item)
            return jsonify(data=item)
        except Exception as e:
            print(f"Error updating {etype}: {str(e)}")
            return jsonify(error=str(e)), 500

    @bp.route("/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        store = get_store()
        deleted = store.delete(etype, item_id)
        if not deleted:
            return jsonify(error="Not found"), 404
        _invalidate_graph_cache()
        SearchService.delete(name, item_id)
        return jsonify(message="Deleted"), 200

    return bp


def _invalidate_graph_cache():
    try:
        cache.delete("map_graph")
    except Exception:
        pass
