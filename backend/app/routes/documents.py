from flask import Blueprint, jsonify, request

from ..services.gitstore import get_store

bp = Blueprint("documents", __name__, url_prefix="/api/docs")


@bp.route("", methods=["GET"])
def list_docs():
    """Return all documents as a flat list (frontend builds tree from parent_id)."""
    store = get_store()
    docs = store.list_all("documents")
    docs.sort(key=lambda d: d.get("sort_order", 0))
    return jsonify(data=docs, count=len(docs))


@bp.route("/<int:doc_id>", methods=["GET"])
def get_doc(doc_id):
    store = get_store()
    doc = store.get("documents", doc_id)
    if doc is None:
        return jsonify(error="Not found"), 404
    return jsonify(data=doc)


@bp.route("", methods=["POST"])
def create_doc():
    data = request.get_json() or {}
    store = get_store()
    doc_data = {
        "title": data.get("title", "Untitled"),
        "content": data.get("content", ""),
        "parent_id": data.get("parent_id"),
        "sort_order": data.get("sort_order", 0),
    }
    doc = store.create("documents", doc_data)
    return jsonify(data=doc), 201


@bp.route("/<int:doc_id>", methods=["PUT"])
def update_doc(doc_id):
    store = get_store()
    doc = store.get("documents", doc_id)
    if doc is None:
        return jsonify(error="Not found"), 404
    data = request.get_json()
    if not data:
        return jsonify(error="Request body required"), 400
    updated = store.update("documents", doc_id, data)
    return jsonify(data=updated)


@bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    store = get_store()
    doc = store.get("documents", doc_id)
    if doc is None:
        return jsonify(error="Not found"), 404
    # Orphan children to root level
    all_docs = store.list_all("documents")
    for child in all_docs:
        if child.get("parent_id") == doc_id:
            store.update("documents", child["id"], {"parent_id": None})
    store.delete("documents", doc_id)
    return jsonify(message="Deleted"), 200


@bp.route("/<int:doc_id>/move", methods=["PATCH"])
def move_doc(doc_id):
    store = get_store()
    doc = store.get("documents", doc_id)
    if doc is None:
        return jsonify(error="Not found"), 404
    data = request.get_json() or {}
    updates = {}
    if "parent_id" in data:
        updates["parent_id"] = data["parent_id"]
    if "sort_order" in data:
        updates["sort_order"] = data["sort_order"]
    updated = store.update("documents", doc_id, updates)
    return jsonify(data=updated)
