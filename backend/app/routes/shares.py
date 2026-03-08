from flask import Blueprint, jsonify, request

from ..services.gitstore import get_store

bp = Blueprint('shares', __name__, url_prefix='/api/shares')


@bp.route('', methods=['GET'])
def get_shares():
    """Get all shares or shares for a specific storage"""
    store = get_store()
    storage_id = request.args.get('storage_id', type=int)
    shares = store.list_all("shares")
    if storage_id:
        shares = [s for s in shares if s.get("storage_id") == storage_id]
    return jsonify(shares)


@bp.route('/<int:share_id>', methods=['GET'])
def get_share(share_id):
    """Get a specific share by ID"""
    store = get_store()
    share = store.get("shares", share_id)
    if share is None:
        return jsonify(error="Not found"), 404
    return jsonify(data=share)


@bp.route('', methods=['POST'])
def create_share():
    """Create a new share"""
    store = get_store()
    data = request.get_json()
    # Verify storage exists
    storage = store.get("storage", data.get("storage_id"))
    if not storage:
        return jsonify({'error': 'Storage not found'}), 404
    item = store.create("shares", data)
    return jsonify(item), 201


@bp.route('/<int:share_id>', methods=['PUT'])
def update_share(share_id):
    """Update an existing share"""
    store = get_store()
    existing = store.get("shares", share_id)
    if existing is None:
        return jsonify(error="Not found"), 404
    data = request.get_json()
    item = store.update("shares", share_id, data)
    return jsonify(item)


@bp.route('/<int:share_id>', methods=['DELETE'])
def delete_share(share_id):
    """Delete a share"""
    store = get_store()
    deleted = store.delete("shares", share_id)
    if not deleted:
        return jsonify(error="Not found"), 404
    return '', 204
