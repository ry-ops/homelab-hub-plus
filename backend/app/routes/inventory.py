from flask import Blueprint, jsonify, request
from ..models import *
from ..models.base import db
import json

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

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


@bp.route('/export', methods=['GET'])
def export_database():
    """Export all data from the database"""
    try:
        # Define the order of data to export to maintain relationships
        data = {
            'hardware': [h.to_dict() for h in Hardware.query.all()],
            'vms': [vm.to_dict() for vm in VM.query.all()],
            'apps': [app.to_dict() for app in AppService.query.all()],
            'storage': [s.to_dict() for s in Storage.query.all()],
            'networks': [n.to_dict() for n in Network.query.all()],
            'misc': [m.to_dict() for m in Misc.query.all()],
            'documents': [d.to_dict() for d in Document.query.all()]
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/import', methods=['POST'])
def import_database():
    """Import data into the database"""
    try:
        import_data = request.get_json()

        # Clear existing data
        db.session.query(AppService).delete()
        db.session.query(VM).delete()
        db.session.query(Hardware).delete()
        db.session.query(Storage).delete()
        db.session.query(Network).delete()
        db.session.query(Misc).delete()
        db.session.query(Document).delete()

        # Import new data
        if 'hardware' in import_data:
            for item in import_data['hardware']:
                hardware = Hardware(**item)
                db.session.add(hardware)

        if 'vms' in import_data:
            for item in import_data['vms']:
                vm = VM(**item)
                db.session.add(vm)

        if 'apps' in import_data:
            for item in import_data['apps']:
                app = AppService(**item)
                db.session.add(app)

        if 'storage' in import_data:
            for item in import_data['storage']:
                storage = Storage(**item)
                db.session.add(storage)

        if 'networks' in import_data:
            for item in import_data['networks']:
                network = Network(**item)
                db.session.add(network)

        if 'misc' in import_data:
            for item in import_data['misc']:
                misc = Misc(**item)
                db.session.add(misc)

        if 'documents' in import_data:
            for item in import_data['documents']:
                document = Document(**item)
                db.session.add(document)

        db.session.commit()
        return jsonify({'message': 'Database imported successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
