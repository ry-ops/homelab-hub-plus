from flask import Blueprint, jsonify, request

from ..services.gitstore import get_store

bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

ENTITY_TYPES = ["hardware", "vms", "apps", "storage", "networks", "misc"]


@bp.route("", methods=["GET"])
def get_all_inventory():
    """Return all inventory items across all types."""
    store = get_store()
    result = {}
    for etype in ENTITY_TYPES:
        result[etype] = store.list_all(etype)
    return jsonify(data=result)


@bp.route("/search", methods=["GET"])
def search_inventory():
    """Search across all entity types by name."""
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify(data=[], count=0)

    store = get_store()
    results = []
    for etype in ENTITY_TYPES:
        for item in store.list_all(etype):
            name = (item.get("name") or "").lower()
            if q in name:
                d = dict(item)
                d["_type"] = etype
                results.append(d)

    return jsonify(data=results, count=len(results))


@bp.route('/export', methods=['GET'])
def export_database():
    """Export all data."""
    try:
        store = get_store()
        data = {}
        for etype in ENTITY_TYPES:
            data[etype] = store.list_all(etype)
        data["documents"] = store.list_all("documents")
        data["shares"] = store.list_all("shares")
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/import', methods=['POST'])
def import_database():
    """Import data — clears existing and recreates."""
    try:
        import_data = request.get_json()
        store = get_store()

        # Clear all types
        all_types = ["shares", "apps", "vms", "storage", "networks", "misc", "documents", "hardware"]
        for etype in all_types:
            store.delete_all(etype)

        def clean_item(item):
            c = item.copy()
            c.pop("id", None)
            c.pop("created_at", None)
            c.pop("updated_at", None)
            c.pop("shares", None)
            return c

        # Import in dependency order
        id_maps = {}

        if "hardware" in import_data:
            for item in import_data["hardware"]:
                store.create("hardware", clean_item(item))

        if "vms" in import_data:
            for item in import_data["vms"]:
                store.create("vms", clean_item(item))

        if "apps" in import_data:
            for item in import_data["apps"]:
                store.create("apps", clean_item(item))

        if "storage" in import_data:
            for item in import_data["storage"]:
                shares_data = item.get("shares", [])
                created = store.create("storage", clean_item(item))
                # Import nested shares
                for share in shares_data:
                    share_clean = clean_item(share)
                    share_clean["storage_id"] = created["id"]
                    store.create("shares", share_clean)

        if "shares" in import_data:
            for item in import_data["shares"]:
                store.create("shares", clean_item(item))

        if "networks" in import_data:
            for item in import_data["networks"]:
                store.create("networks", clean_item(item))

        if "misc" in import_data:
            for item in import_data["misc"]:
                store.create("misc", clean_item(item))

        if "documents" in import_data:
            for item in import_data["documents"]:
                store.create("documents", clean_item(item))

        return jsonify({'message': 'Data imported successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
