from flask import Blueprint, jsonify, request
from ..models import Share, Storage
from ..models.base import db

bp = Blueprint('shares', __name__, url_prefix='/api/shares')


@bp.route('', methods=['GET'])
def get_shares():
    """Get all shares or shares for a specific storage"""
    storage_id = request.args.get('storage_id')
    
    if storage_id:
        shares = Share.query.filter_by(storage_id=storage_id).all()
    else:
        shares = Share.query.all()
    
    return jsonify([share.to_dict() for share in shares])


@bp.route('/<int:share_id>', methods=['GET'])
def get_share(share_id):
    """Get a specific share by ID"""
    share = Share.query.get_or_404(share_id)
    return jsonify(data=share.to_dict())


@bp.route('', methods=['POST'])
def create_share():
    """Create a new share"""
    data = request.get_json()
    
    # Verify storage exists
    storage = Storage.query.get(data.get('storage_id'))
    if not storage:
        return jsonify({'error': 'Storage not found'}), 404
    
    share = Share(
        storage_id=data.get('storage_id'),
        name=data.get('name'),
        hostname=data.get('hostname'),
        ip=data.get('ip'),
        share_type=data.get('share_type'),
        notes=data.get('notes')
    )
    
    db.session.add(share)
    db.session.commit()
    
    return jsonify(share.to_dict()), 201


@bp.route('/<int:share_id>', methods=['PUT'])
def update_share(share_id):
    """Update an existing share"""
    share = Share.query.get_or_404(share_id)
    data = request.get_json()
    
    # Update fields
    for field in ['name', 'hostname', 'ip', 'share_type', 'notes', 'storage_id']:
        if field in data:
            setattr(share, field, data[field])
    
    db.session.commit()
    return jsonify(share.to_dict())


@bp.route('/<int:share_id>', methods=['DELETE'])
def delete_share(share_id):
    """Delete a share"""
    share = Share.query.get_or_404(share_id)
    db.session.delete(share)
    db.session.commit()
    return '', 204
