from flask import Blueprint, jsonify, request

from ..models import db, Network, NetworkMember
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("networks", Network)


@bp.route("/<int:network_id>/members", methods=["GET"], endpoint="list_members")
def list_members(network_id):
    db.get_or_404(Network, network_id)
    members = NetworkMember.query.filter_by(network_id=network_id).all()
    return jsonify(data=[m.to_dict() for m in members])


@bp.route("/<int:network_id>/members", methods=["POST"], endpoint="add_member")
def add_member(network_id):
    db.get_or_404(Network, network_id)
    data = request.get_json()
    if not data or "member_type" not in data or "member_id" not in data:
        return jsonify(error="member_type and member_id required"), 400
    member = NetworkMember(
        network_id=network_id,
        member_type=data["member_type"],
        member_id=data["member_id"],
        ip_on_network=data.get("ip_on_network"),
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(data=member.to_dict()), 201


@bp.route(
    "/<int:network_id>/members/<string:member_type>/<int:member_id>",
    methods=["DELETE"],
    endpoint="remove_member",
)
def remove_member(network_id, member_type, member_id):
    member = NetworkMember.query.filter_by(
        network_id=network_id, member_type=member_type, member_id=member_id
    ).first_or_404()
    db.session.delete(member)
    db.session.commit()
    return jsonify(message="Removed"), 200
