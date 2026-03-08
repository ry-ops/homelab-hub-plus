from flask import jsonify

from ..models import db, VM
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("vms", VM, detail_route=False)


@bp.route("/<int:item_id>", methods=["GET"], endpoint="get_vm_detail")
def get_vm_detail(item_id):
    """Override GET detail to include related apps and storage."""
    vm = db.get_or_404(VM, item_id)
    result = vm.to_dict()
    result["apps"] = [app.to_dict() for app in vm.apps]
    result["storage_pools"] = [s.to_dict() for s in vm.storage_pools]
    if vm.hardware:
        result["hardware_name"] = vm.hardware.name
    return jsonify(data=result)
