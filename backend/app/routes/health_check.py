"""
Host health/ping endpoints.

GET  /api/health-check?hosts=192.168.1.1,192.168.1.2
POST /api/health-check  { "hosts": ["192.168.1.1", "myhost.local"] }

Results are cached in Redis for 60 seconds.
"""
from flask import Blueprint, jsonify, request

from ..services.cache import cache
from ..services.health import ping_hosts

bp = Blueprint("health_check", __name__, url_prefix="/api/health-check")


def _do_ping(hosts: list[str]):
    results = ping_hosts(hosts)
    return jsonify(data=results, count=len(results))


@bp.route("", methods=["GET"])
def ping_get():
    raw = request.args.get("hosts", "")
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    if not hosts:
        return jsonify(error="hosts parameter required"), 400
    return _do_ping(hosts)


@bp.route("", methods=["POST"])
def ping_post():
    body = request.get_json() or {}
    hosts = body.get("hosts", [])
    if not hosts:
        return jsonify(error="hosts array required"), 400
    return _do_ping(hosts)
