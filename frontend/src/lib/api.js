const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
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
