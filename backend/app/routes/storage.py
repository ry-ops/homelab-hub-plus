from flask import jsonify

from ..services.gitstore import get_store
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("storage", detail_route=False)


@bp.route("/<int:item_id>", methods=["GET"], endpoint="get_storage_detail")
def get_storage_detail(item_id):
    """Override GET detail to include nested shares."""
    store = get_store()
    item = store.get("storage", item_id)
    if item is None:
        return jsonify(error="Not found"), 404
    result = dict(item)
    result["shares"] = [s for s in store.list_all("shares") if s.get("storage_id") == item_id]
    return jsonify(data=result)


@bp.route("", methods=["GET"])
def list_storage():
    """Override list to include nested shares per storage item."""
    store = get_store()
    items = store.list_all("storage")
    all_shares = store.list_all("shares")
    for item in items:
        item["shares"] = [s for s in all_shares if s.get("storage_id") == item.get("id")]
    return jsonify(data=items, count=len(items))
