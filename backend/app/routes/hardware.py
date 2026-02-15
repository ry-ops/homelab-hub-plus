from flask import jsonify

from ..models import db, Hardware
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("hardware", Hardware)


@bp.route("/<int:item_id>", methods=["GET"], endpoint="get_hardware_detail")
def get_hardware_detail(item_id):
    """Override GET detail to include related VMs, apps, and storage."""
    hw = db.get_or_404(Hardware, item_id)
    result = hw.to_dict()
    result["vms"] = [vm.to_dict() for vm in hw.vms]
    result["apps"] = [app.to_dict() for app in hw.apps]
    result["storage_pools"] = [s.to_dict() for s in hw.storage_pools]
    return jsonify(data=result)
