from flask import Blueprint, jsonify, request

from ..models import (
    db, Hardware, VM, AppService, Storage, Network, Misc,
    NetworkMember, Relationship, MapLayout, MapEdge,
)

bp = Blueprint("map", __name__, url_prefix="/api/map")

ENTITY_MAP = {
    "hardware": Hardware,
    "vms": VM,
    "apps": AppService,
    "storage": Storage,
    "networks": Network,
    "misc": Misc,
}


@bp.route("/graph", methods=["GET"])
def get_graph():
    """Return full graph data: nodes + edges for Cytoscape.js."""
    nodes = []
    edges = []

    # Collect all nodes
    for entity_type, model in ENTITY_MAP.items():
        for item in model.query.all():
            nodes.append({
                "data": {
                    "id": f"{entity_type}-{item.id}",
                    "label": item.name,
                    "type": entity_type,
                    "entity_id": item.id,
                }
            })

    # Edges from FK relationships
    for vm in VM.query.all():
        edges.append({
            "data": {
                "source": f"hardware-{vm.hardware_id}",
                "target": f"vms-{vm.id}",
                "label": "hosts",
            }
        })

    for app in AppService.query.all():
        if app.hardware_id:
            edges.append({
                "data": {
                    "source": f"hardware-{app.hardware_id}",
                    "target": f"apps-{app.id}",
                    "label": "runs",
                }
            })
        elif app.vm_id:
            edges.append({
                "data": {
                    "source": f"vms-{app.vm_id}",
                    "target": f"apps-{app.id}",
                    "label": "runs",
                }
            })

    for s in Storage.query.all():
        if s.hardware_id:
            edges.append({
                "data": {
                    "source": f"hardware-{s.hardware_id}",
                    "target": f"storage-{s.id}",
                    "label": "storage",
                }
            })
        elif s.vm_id:
            edges.append({
                "data": {
                    "source": f"vms-{s.vm_id}",
                    "target": f"storage-{s.id}",
                    "label": "storage",
                }
            })

    # Edges from network memberships
    for member in NetworkMember.query.all():
        edges.append({
            "data": {
                "source": f"networks-{member.network_id}",
                "target": f"{member.member_type}-{member.member_id}",
                "label": "network",
            }
        })

    # Edges from generic relationships
    for rel in Relationship.query.all():
        edges.append({
            "data": {
                "source": f"{rel.source_type}-{rel.source_id}",
                "target": f"{rel.target_type}-{rel.target_id}",
                "label": rel.label or "",
            }
        })

    # Manual map edges
    for edge in MapEdge.query.all():
        edges.append({
            "data": {
                "source": f"{edge.source_type}-{edge.source_id}",
                "target": f"{edge.target_type}-{edge.target_id}",
                "label": edge.label or "",
                "manual": True,
            }
        })

    return jsonify(nodes=nodes, edges=edges)


@bp.route("/layout", methods=["GET"])
def get_layout():
    """Get all saved node positions."""
    layouts = MapLayout.query.all()
    result = {}
    for layout in layouts:
        result[f"{layout.node_type}-{layout.node_id}"] = {
            "x": layout.x,
            "y": layout.y,
            "pinned": layout.pinned,
        }
    return jsonify(data=result)


@bp.route("/layout", methods=["PUT"])
def save_layout():
    """Bulk save node positions."""
    data = request.get_json()
    if not data or "positions" not in data:
        return jsonify(error="positions required"), 400

    for node_key, pos in data["positions"].items():
        parts = node_key.rsplit("-", 1)
        if len(parts) != 2:
            continue
        node_type, node_id = parts[0], int(parts[1])

        layout = MapLayout.query.filter_by(node_type=node_type, node_id=node_id).first()
        if layout:
            layout.x = pos["x"]
            layout.y = pos["y"]
            layout.pinned = pos.get("pinned", True)
        else:
            layout = MapLayout(
                node_type=node_type, node_id=node_id,
                x=pos["x"], y=pos["y"], pinned=pos.get("pinned", True),
            )
            db.session.add(layout)

    db.session.commit()
    return jsonify(message="Saved")


@bp.route("/edges", methods=["POST"])
def create_edge():
    data = request.get_json()
    if not data:
        return jsonify(error="Request body required"), 400
    edge = MapEdge(
        source_type=data["source_type"],
        source_id=data["source_id"],
        target_type=data["target_type"],
        target_id=data["target_id"],
        label=data.get("label"),
        style=data.get("style"),
    )
    db.session.add(edge)
    db.session.commit()
    return jsonify(data={"id": edge.id}), 201


@bp.route("/edges/<int:edge_id>", methods=["DELETE"])
def delete_edge(edge_id):
    edge = db.get_or_404(MapEdge, edge_id)
    db.session.delete(edge)
    db.session.commit()
    return jsonify(message="Deleted")
