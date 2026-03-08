from flask import Blueprint, jsonify, request

from ..services.gitstore import get_store
from ._crud_factory import create_crud_blueprint

bp = create_crud_blueprint("networks")


@bp.route("/<int:network_id>/members", methods=["GET"], endpoint="list_members")
def list_members(network_id):
    store = get_store()
    network = store.get("networks", network_id)
    if network is None:
        return jsonify(error="Not found"), 404
    all_members = store.get_special("network_members.json")
    members = [m for m in all_members if m.get("network_id") == network_id]
    return jsonify(data=members)


@bp.route("/<int:network_id>/members", methods=["POST"], endpoint="add_member")
def add_member(network_id):
    store = get_store()
    network = store.get("networks", network_id)
    if network is None:
        return jsonify(error="Not found"), 404
    data = request.get_json()
    if not data or "member_type" not in data or "member_id" not in data:
        return jsonify(error="member_type and member_id required"), 400

    all_members = store.get_special("network_members.json")
    # Auto-assign ID
    max_id = max((m.get("id", 0) for m in all_members), default=0)
    member = {
        "id": max_id + 1,
        "network_id": network_id,
        "member_type": data["member_type"],
        "member_id": data["member_id"],
        "ip_on_network": data.get("ip_on_network"),
    }
    all_members.append(member)
    store.put_special("network_members.json", all_members, f"Add member to network {network_id}")
    return jsonify(data=member), 201


@bp.route(
    "/<int:network_id>/members/<string:member_type>/<int:member_id>",
    methods=["DELETE"],
    endpoint="remove_member",
)
def remove_member(network_id, member_type, member_id):
    store = get_store()
    all_members = store.get_special("network_members.json")
    filtered = [
        m for m in all_members
        if not (m.get("network_id") == network_id and m.get("member_type") == member_type and m.get("member_id") == member_id)
    ]
    if len(filtered) == len(all_members):
        return jsonify(error="Not found"), 404
    store.put_special("network_members.json", filtered, f"Remove member from network {network_id}")
    return jsonify(message="Removed"), 200
