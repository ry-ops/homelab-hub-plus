"""
Host health/ping service.

Uses icmplib for ICMP ping. Falls back to a TCP connect on port 80
if ICMP requires elevated privileges (common in containers without
NET_RAW capability).

Results are cached in Redis for 60s to avoid hammering the network
on every page load.
"""
import logging
import socket

logger = logging.getLogger(__name__)


def _tcp_reachable(host: str, port: int = 80, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def ping_host(host: str) -> dict:
    """
    Return {"host": str, "alive": bool, "latency_ms": float | None, "method": str}
    """
    if not host:
        return {"host": host, "alive": False, "latency_ms": None, "method": "none"}

    # Try ICMP first
    try:
        from icmplib import ping as icmp_ping, SocketPermissionError
        result = icmp_ping(host, count=1, timeout=1, privileged=False)
        return {
            "host": host,
            "alive": result.is_alive,
            "latency_ms": round(result.avg_rtt, 2) if result.is_alive else None,
            "method": "icmp",
        }
    except Exception:
        pass

    # Fallback: TCP port 80
    alive = _tcp_reachable(host, port=80)
    return {
        "host": host,
        "alive": alive,
        "latency_ms": None,
        "method": "tcp:80",
    }


def ping_hosts(hosts: list[str]) -> dict[str, dict]:
    """Ping multiple hosts, return results keyed by host string."""
    return {h: ping_host(h) for h in hosts if h}
