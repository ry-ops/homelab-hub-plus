"""
Subnet auto-discovery service.

All stdlib — no new pip dependencies.
Reuses ping_host() from health.py.
"""
from __future__ import annotations

import ipaddress
import socket
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from typing import Optional

from .health import ping_host

# ---------------------------------------------------------------------------
# Port catalogue
# ---------------------------------------------------------------------------

KNOWN_PORTS: dict[int, str] = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    5900: "VNC",
    6443: "Kubernetes",
    8006: "Proxmox",
    8080: "HTTP-alt",
    8443: "HTTPS-alt",
    9090: "Cockpit",
    9100: "Node Exporter",
}

HTTP_PORTS = {80, 443, 8006, 8080, 8443, 9090}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class _TitleParser(HTMLParser):
    """Minimal HTML parser that extracts the <title> text."""

    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title and self.title is None:
            self.title = data.strip()


def _tcp_connect(ip: str, port: int, timeout: float) -> bool:
    """Return True if a TCP connection succeeds."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def _grab_ssh_banner(ip: str, timeout: float) -> Optional[str]:
    """Read the SSH identification string from port 22."""
    try:
        with socket.create_connection((ip, 22), timeout=timeout) as s:
            banner = s.recv(256)
            return banner.decode("ascii", errors="replace").strip()
    except OSError:
        return None


def _grab_http_title(ip: str, port: int, timeout: float) -> Optional[str]:
    """Perform a simple GET and extract the <title> from the response."""
    scheme = "https" if port in (443, 8443) else "http"
    url = f"{scheme}://{ip}:{port}/"
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "homelab-discovery/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read(4096)
            html = raw.decode("utf-8", errors="replace")
    except urllib.error.URLError:
        return None
    except Exception:
        return None

    parser = _TitleParser()
    try:
        parser.feed(html)
    except Exception:
        pass
    return parser.title


def _reverse_dns(ip: str) -> Optional[str]:
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except OSError:
        return None


def fingerprint_host(open_ports: list[int], http_title: Optional[str]) -> tuple[str, str]:
    """
    Map open ports (and optional HTTP title) to (fingerprint label, suggested_type).

    Priority order matches the plan.
    """
    port_set = set(open_ports)

    if 8006 in port_set:
        return "Proxmox VE", "hardware"
    if 9090 in port_set:
        return "Cockpit", "hardware"
    if 6443 in port_set:
        return "Kubernetes API", "misc"
    if 5900 in port_set:
        return "VNC Host", "hardware"
    if 22 in port_set and not port_set.intersection(HTTP_PORTS):
        return "SSH Host", "hardware"
    if port_set.intersection({80, 443}):
        return "Web Server", "apps"
    if open_ports:
        return "Unknown", "misc"
    return "Unknown", "misc"


# ---------------------------------------------------------------------------
# Per-host probe
# ---------------------------------------------------------------------------

def _probe_host(ip: str, timeout: float) -> dict:
    """Run the full fingerprinting pipeline for a single IP address."""
    start = time.monotonic()

    # 1. Ping
    ping_result = ping_host(ip)
    alive = ping_result.get("alive", False)
    latency_ms = ping_result.get("latency_ms")

    if not alive:
        return {
            "ip": ip,
            "alive": False,
            "latency_ms": None,
            "hostname": None,
            "open_ports": [],
            "services": {},
            "http_title": None,
            "ssh_banner": None,
            "fingerprint": "Unknown",
            "suggested_type": "misc",
            "suggested_name": ip,
        }

    # 2. Reverse DNS
    hostname = _reverse_dns(ip)

    # 3. TCP port scan
    open_ports: list[int] = []
    for port in KNOWN_PORTS:
        if _tcp_connect(ip, port, timeout):
            open_ports.append(port)
    open_ports.sort()

    # 4. Banner grabs
    services: dict[str, str] = {str(p): KNOWN_PORTS[p] for p in open_ports}

    ssh_banner: Optional[str] = None
    if 22 in open_ports:
        ssh_banner = _grab_ssh_banner(ip, timeout)

    http_title: Optional[str] = None
    for port in (8006, 80, 443, 8080, 8443, 9090):
        if port in open_ports:
            title = _grab_http_title(ip, port, timeout)
            if title:
                http_title = title
                break

    # 5. Fingerprint
    fingerprint, suggested_type = fingerprint_host(open_ports, http_title)
    suggested_name = hostname or ip

    return {
        "ip": ip,
        "alive": True,
        "latency_ms": latency_ms,
        "hostname": hostname,
        "open_ports": open_ports,
        "services": services,
        "http_title": http_title,
        "ssh_banner": ssh_banner,
        "fingerprint": fingerprint,
        "suggested_type": suggested_type,
        "suggested_name": suggested_name,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_cidr(
    cidr: str,
    concurrency: int = 50,
    timeout: float = 1.0,
) -> list[dict]:
    """
    Scan every host in *cidr* and return a list of probe results.

    Dead hosts are included so the caller sees the full subnet picture.
    """
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = list(network.hosts())

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(concurrency, len(hosts) or 1)) as pool:
        futures = {pool.submit(_probe_host, str(ip), timeout): str(ip) for ip in hosts}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                ip = futures[future]
                results.append({
                    "ip": ip,
                    "alive": False,
                    "latency_ms": None,
                    "hostname": None,
                    "open_ports": [],
                    "services": {},
                    "http_title": None,
                    "ssh_banner": None,
                    "fingerprint": "Unknown",
                    "suggested_type": "misc",
                    "suggested_name": ip,
                    "error": str(exc),
                })

    # Sort by IP address for deterministic output
    results.sort(key=lambda r: ipaddress.ip_address(r["ip"]))
    return results
