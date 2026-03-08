from flask import Blueprint, jsonify, request
from ipaddress import ip_address, ip_network, AddressValueError

from ..services.gitstore import get_store
from ..services.cache import cache

bp = Blueprint("map", __name__, url_prefix="/api/map")

ENTITY_TYPES = ["hardware", "vms", "apps", "storage", "networks", "misc"]


def get_network_for_ip(ip_addr, networks=None):
    """Determine which network an IP address belongs to based on subnet matching."""
    if not ip_addr:
        return None
    try:
        ip = ip_address(ip_addr)
        if networks is None:
            networks = get_store().list_all("networks")
        for network in networks:
            subnet = network.get("subnet")
            if subnet:
                try:
                    net = ip_network(subnet, strict=False)
                    if ip in net:
                        return network
                except (AddressValueError, ValueError):
                    continue
    except (AddressValueError, ValueError):
        pass
    return None


@bp.route("/graph", methods=["GET"])
@cache.cached(timeout=60, key_prefix="map_graph")
def get_graph():
    """Return full graph data: nodes + edges for Cytoscape.js."""
    store = get_store()
    nodes = []
    edges = []
    networks = store.list_all("networks")

    rank_map = {"hardware": 0, "vms": 1, "apps": 2, "storage": 2, "misc": 3}

    # Collect all nodes (exclude networks — shown in separate panel)
    for etype in ENTITY_TYPES:
        if etype == "networks":
            continue
        for item in store.list_all(etype):
            node_data = {
                "id": f"{etype}-{item['id']}",
                "label": item.get("name", ""),
                "type": etype,
                "entity_id": item["id"],
                "rawName": item.get("name", ""),
                "rank": rank_map.get(etype, 3),
            }
            icon = item.get("icon")
            if icon:
                if icon.startswith("data:image/"):
                    node_data["imageIcon"] = icon
                    node_data["label"] = ""
                else:
                    node_data["icon"] = icon
                    node_data["label"] = icon

            ip_addr = item.get("ip_address")
            if ip_addr:
                network = get_network_for_ip(ip_addr, networks)
                if network:
                    node_data["networkId"] = network["id"]
                    node_data["networkName"] = network.get("name")
                    node_data["networkColor"] = network.get("color") or "#E74C3C"

            nodes.append({"data": node_data})

    # Edges from FK relationships
    for vm in store.list_all("vms"):
        if vm.get("hardware_id"):
            edges.append({"data": {
                "source": f"hardware-{vm['hardware_id']}",
                "target": f"vms-{vm['id']}",
                "label": "hosts",
            }})

    for app in store.list_all("apps"):
        if app.get("hardware_id"):
            edges.append({"data": {
                "source": f"hardware-{app['hardware_id']}",
                "target": f"apps-{app['id']}",
                "label": "runs",
            }})
        elif app.get("vm_id"):
            edges.append({"data": {
                "source": f"vms-{app['vm_id']}",
                "target": f"apps-{app['id']}",
                "label": "runs",
            }})

    for s in store.list_all("storage"):
        if s.get("hardware_id"):
            edges.append({"data": {
                "source": f"hardware-{s['hardware_id']}",
                "target": f"storage-{s['id']}",
                "label": "storage",
            }})
        elif s.get("vm_id"):
            edges.append({"data": {
                "source": f"vms-{s['vm_id']}",
                "target": f"storage-{s['id']}",
                "label": "storage",
            }})

    # Shares as nodes + edges
    for share in store.list_all("shares"):
        node_data = {
            "id": f"shares-{share['id']}",
            "label": share.get("name", ""),
            "type": "shares",
            "entity_id": share["id"],
            "rawName": share.get("name", ""),
            "rank": 3,
            "shareType": share.get("share_type"),
        }
        if share.get("ip"):
            network = get_network_for_ip(share["ip"], networks)
            if network:
                node_data["networkId"] = network["id"]
                node_data["networkName"] = network.get("name")
                node_data["networkColor"] = network.get("color") or "#E74C3C"
        nodes.append({"data": node_data})
        edges.append({"data": {
            "source": f"storage-{share['storage_id']}",
            "target": f"shares-{share['id']}",
            "label": share.get("share_type") or "share",
        }})

    # Generic relationships
    for rel in store.get_special("relationships.json"):
        edges.append({"data": {
            "source": f"{rel['source_type']}-{rel['source_id']}",
            "target": f"{rel['target_type']}-{rel['target_id']}",
            "label": rel.get("label", ""),
        }})

    # Manual map edges
    for edge in store.get_special("map_edges.json"):
        edges.append({"data": {
            "source": f"{edge['source_type']}-{edge['source_id']}",
            "target": f"{edge['target_type']}-{edge['target_id']}",
            "label": edge.get("label", ""),
            "manual": True,
        }})

    return jsonify(nodes=nodes, edges=edges)


@bp.route("/networks", methods=["GET"])
def get_networks():
    """Return all networks for display in a separate panel."""
    store = get_store()
    networks = []
    for n in store.list_all("networks"):
        networks.append({
            "id": n["id"],
            "name": n.get("name"),
            "color": n.get("color") or "#E74C3C",
            "vlan_id": n.get("vlan_id"),
            "notes": n.get("notes"),
        })
    return jsonify(networks=networks)


@bp.route("/layout", methods=["GET"])
def get_layout():
    """Get all saved node positions."""
    store = get_store()
    layouts = store.get_special("map_layout.json")
    result = {}
    for layout in layouts:
        key = f"{layout['node_type']}-{layout['node_id']}"
        result[key] = {"x": layout["x"], "y": layout["y"], "pinned": layout.get("pinned", False)}
    return jsonify(data=result)


@bp.route("/layout", methods=["PUT"])
def save_layout():
    """Bulk save node positions."""
    data = request.get_json()
    if not data or "positions" not in data:
        return jsonify(error="positions required"), 400

    store = get_store()
    layouts = store.get_special("map_layout.json")
    layout_map = {f"{l['node_type']}-{l['node_id']}": i for i, l in enumerate(layouts)}

    for node_key, pos in data["positions"].items():
        parts = node_key.rsplit("-", 1)
        if len(parts) != 2:
            continue
        node_type, node_id = parts[0], int(parts[1])

        existing_idx = layout_map.get(node_key)
        if existing_idx is not None:
            layouts[existing_idx]["x"] = pos["x"]
            layouts[existing_idx]["y"] = pos["y"]
            layouts[existing_idx]["pinned"] = pos.get("pinned", True)
        else:
            layouts.append({
                "node_type": node_type, "node_id": node_id,
                "x": pos["x"], "y": pos["y"], "pinned": pos.get("pinned", True),
            })

    store.put_special("map_layout.json", layouts, "Update map layout")
    return jsonify(message="Saved")


@bp.route("/edges", methods=["POST"])
def create_edge():
    data = request.get_json()
    if not data:
        return jsonify(error="Request body required"), 400
    store = get_store()
    all_edges = store.get_special("map_edges.json")
    max_id = max((e.get("id", 0) for e in all_edges), default=0)
    edge = {
        "id": max_id + 1,
        "source_type": data["source_type"],
        "source_id": data["source_id"],
        "target_type": data["target_type"],
        "target_id": data["target_id"],
        "label": data.get("label"),
        "style": data.get("style"),
    }
    all_edges.append(edge)
    store.put_special("map_edges.json", all_edges, "Add map edge")
    return jsonify(data={"id": edge["id"]}), 201


@bp.route("/edges/<int:edge_id>", methods=["DELETE"])
def delete_edge(edge_id):
    store = get_store()
    all_edges = store.get_special("map_edges.json")
    filtered = [e for e in all_edges if e.get("id") != edge_id]
    if len(filtered) == len(all_edges):
        return jsonify(error="Not found"), 404
    store.put_special("map_edges.json", filtered, f"Delete map edge {edge_id}")
    return jsonify(message="Deleted")
