const BASE = "/api";
const TOKEN_KEY = "homelab_api_token";

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

async function request(path, options = {}) {
  const token = getToken();
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...authHeader, ...options.headers },
    ...options,
  });

  if (res.status === 401 || res.status === 403) {
    throw new Error("Authentication required. Please set a valid API token in Settings.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

export function get(path) {
  return request(path);
}

export function post(path, data) {
  return request(path, { method: "POST", body: JSON.stringify(data) });
}

export function put(path, data) {
  return request(path, { method: "PUT", body: JSON.stringify(data) });
}

export function patch(path, data) {
  return request(path, { method: "PATCH", body: JSON.stringify(data) });
}

export function del(path) {
  return request(path, { method: "DELETE" });
}

/**
 * Semantic search via Qdrant.
 * Returns [{ entity_type, entity_id, name, score }, ...]
 */
export function searchSemantic(q, limit = 20) {
  return request(`/search?q=${encodeURIComponent(q)}&limit=${limit}`);
}

/**
 * Ping one or more hosts.
 * hosts: string[] — IP addresses or hostnames
 * Returns { [host]: { alive, latency_ms, method } }
 */
export function pingHosts(hosts) {
  return request("/health-check", {
    method: "POST",
    body: JSON.stringify({ hosts }),
  });
}

/**
 * Trigger a full Qdrant backfill of all existing entities.
 * Returns { indexed, by_type, errors, status }
 */
export function reindexSearch() {
  return request("/search/index", { method: "POST" });
}

/**
 * Scan a subnet CIDR for live hosts with port fingerprinting.
 * Returns { hosts, total, alive, duration_ms }
 */
export function scanSubnet(cidr, concurrency = 50, timeout = 1.0) {
  return post("/discovery/scan", { cidr, concurrency, timeout });
}

/**
 * Import selected discovered hosts into inventory.
 * hosts: [{ ip, type, name, hostname?, notes? }]
 * Returns { imported, by_type, errors }
 */
export function importDiscovery(hosts) {
  return post("/discovery/import", { hosts });
}
