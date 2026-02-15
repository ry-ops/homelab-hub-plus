from flask import Blueprint, jsonify, request

from ..models import db


def create_crud_blueprint(name, model_class, url_prefix=None):
    """Generate a Flask Blueprint with standard CRUD endpoints for a model."""
    prefix = url_prefix or f"/api/{name}"
    bp = Blueprint(name, __name__, url_prefix=prefix)

    @bp.route("", methods=["GET"])
    def list_items():
        items = model_class.query.all()
        return jsonify(data=[item.to_dict() for item in items], count=len(items))

    @bp.route("/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        item = db.get_or_404(model_class, item_id)
        return jsonify(data=item.to_dict())

    @bp.route("", methods=["POST"])
    def create_item():
        data = request.get_json()
        if not data:
            return jsonify(error="Request body required"), 400
        item = model_class()
        item.update_from_dict(data)
        db.session.add(item)
        db.session.commit()
        return jsonify(data=item.to_dict()), 201

    @bp.route("/<int:item_id>", methods=["PUT"])
    def update_item(item_id):
        item = db.get_or_404(model_class, item_id)
        data = request.get_json()
        if not data:
            return jsonify(error="Request body required"), 400
        item.update_from_dict(data)
        db.session.commit()
        return jsonify(data=item.to_dict())

    @bp.route("/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        item = db.get_or_404(model_class, item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify(message="Deleted"), 200

    return bp
