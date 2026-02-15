from flask import Blueprint, jsonify, request

from ..models import db, Document

bp = Blueprint("documents", __name__, url_prefix="/api/docs")


@bp.route("", methods=["GET"])
def list_docs():
    """Return all documents as a flat list (frontend builds tree from parent_id)."""
    docs = Document.query.order_by(Document.sort_order).all()
    return jsonify(data=[d.to_dict() for d in docs], count=len(docs))


@bp.route("/<int:doc_id>", methods=["GET"])
def get_doc(doc_id):
    doc = db.get_or_404(Document, doc_id)
    return jsonify(data=doc.to_dict())


@bp.route("", methods=["POST"])
def create_doc():
    data = request.get_json() or {}
    doc = Document(
        title=data.get("title", "Untitled"),
        content=data.get("content", ""),
        parent_id=data.get("parent_id"),
        sort_order=data.get("sort_order", 0),
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(data=doc.to_dict()), 201


@bp.route("/<int:doc_id>", methods=["PUT"])
def update_doc(doc_id):
    doc = db.get_or_404(Document, doc_id)
    data = request.get_json()
    if not data:
        return jsonify(error="Request body required"), 400
    doc.update_from_dict(data)
    db.session.commit()
    return jsonify(data=doc.to_dict())


@bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    doc = db.get_or_404(Document, doc_id)
    # Orphan children to root level
    for child in doc.children:
        child.parent_id = None
    db.session.delete(doc)
    db.session.commit()
    return jsonify(message="Deleted"), 200


@bp.route("/<int:doc_id>/move", methods=["PATCH"])
def move_doc(doc_id):
    doc = db.get_or_404(Document, doc_id)
    data = request.get_json() or {}
    if "parent_id" in data:
        doc.parent_id = data["parent_id"]
    if "sort_order" in data:
        doc.sort_order = data["sort_order"]
    db.session.commit()
    return jsonify(data=doc.to_dict())
