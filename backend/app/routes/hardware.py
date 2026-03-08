from flask import jsonify

from ..services.gitstore import get_store
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("hardware", detail_route=False)


@bp.route("/<int:item_id>", methods=["GET"], endpoint="get_hardware_detail")
def get_hardware_detail(item_id):
    """Override GET detail to include related VMs, apps, and storage."""
    store = get_store()
    hw = store.get("hardware", item_id)
    if hw is None:
        return jsonify(error="Not found"), 404
    result = dict(hw)
    result["vms"] = [v for v in store.list_all("vms") if v.get("hardware_id") == item_id]
    result["apps"] = [a for a in store.list_all("apps") if a.get("hardware_id") == item_id]
    result["storage_pools"] = [s for s in store.list_all("storage") if s.get("hardware_id") == item_id]
    return jsonify(data=result)
