from flask import jsonify

from ..services.gitstore import get_store
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("vms", detail_route=False)


@bp.route("/<int:item_id>", methods=["GET"], endpoint="get_vm_detail")
def get_vm_detail(item_id):
    """Override GET detail to include related apps and storage."""
    store = get_store()
    vm = store.get("vms", item_id)
    if vm is None:
        return jsonify(error="Not found"), 404
    result = dict(vm)
    result["apps"] = [a for a in store.list_all("apps") if a.get("vm_id") == item_id]
    result["storage_pools"] = [s for s in store.list_all("storage") if s.get("vm_id") == item_id]
    hw_id = vm.get("hardware_id")
    if hw_id:
        hw = store.get("hardware", hw_id)
        if hw:
            result["hardware_name"] = hw.get("name")
    return jsonify(data=result)
