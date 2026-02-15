from flask import Blueprint, jsonify, request

from ..models import Hardware, VM, AppService, Storage, Network, Misc

bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")

ENTITY_MAP = {
    "hardware": Hardware,
    "vms": VM,
    "apps": AppService,
    "storage": Storage,
    "networks": Network,
    "misc": Misc,
}


@bp.route("", methods=["GET"])
def get_all_inventory():
    """Return all inventory items across all types."""
    result = {}
    for entity_type, model in ENTITY_MAP.items():
        result[entity_type] = [item.to_dict() for item in model.query.all()]
    return jsonify(data=result)


@bp.route("/search", methods=["GET"])
def search_inventory():
    """Search across all entity types by name."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify(data=[], count=0)

    results = []
    pattern = f"%{q}%"
    for entity_type, model in ENTITY_MAP.items():
        matches = model.query.filter(model.name.ilike(pattern)).all()
        for item in matches:
            d = item.to_dict()
            d["_type"] = entity_type
            results.append(d)

    return jsonify(data=results, count=len(results))
