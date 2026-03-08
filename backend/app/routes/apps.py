from flask import request, jsonify

from ..services.gitstore import get_store
from ..services.search import SearchService
from ._crud_factory import create_crud_blueprint, _invalidate_graph_cache

bp = create_crud_blueprint("apps")


def _set_default_hostname(data):
    """Set hostname to parent's hostname if not provided."""
    if data.get("hostname"):
        return data
    store = get_store()
    hw_id = data.get("hardware_id")
    vm_id = data.get("vm_id")
    if hw_id:
        hw = store.get("hardware", hw_id)
        if hw and hw.get("hostname"):
            data["hostname"] = hw["hostname"]
    elif vm_id:
        vm = store.get("vms", vm_id)
        if vm and vm.get("hostname"):
            data["hostname"] = vm["hostname"]
    return data


@bp.route("", methods=["POST"])
def create_app():
    data = request.get_json()
    if not data:
        return jsonify(error="Request body required"), 400
    data = _set_default_hostname(data)
    store = get_store()
    item = store.create("apps", data)
    _invalidate_graph_cache()
    SearchService.upsert("apps", item["id"], item)
    return jsonify(data=item), 201


@bp.route("/<int:item_id>", methods=["PUT"])
def update_app(item_id):
    store = get_store()
    existing = store.get("apps", item_id)
    if existing is None:
        return jsonify(error="Not found"), 404
    data = request.get_json()
    if not data:
        return jsonify(error="Request body required"), 400
    data = _set_default_hostname(data)
    item = store.update("apps", item_id, data)
    _invalidate_graph_cache()
    SearchService.upsert("apps", item["id"], item)
    return jsonify(data=item)
