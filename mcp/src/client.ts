/**
 * HTTP client for the homelab-hub-plus Flask API.
 * Injects Bearer token when configured.
 */
import { loadConfig } from "./config.js";

export class HomelabClient {
  private url: string;
  private token: string;

  constructor() {
    const config = loadConfig();
    this.url = config.url.replace(/\/$/, "");
    this.token = config.token;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.token) {
      h["Authorization"] = `Bearer ${this.token}`;
    }
    return h;
  }

  async get<T = unknown>(path: string): Promise<T> {
    const res = await fetch(`${this.url}${path}`, { headers: this.headers() });
    return this.handleResponse<T>(res);
  }

  async post<T = unknown>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(`${this.url}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return this.handleResponse<T>(res);
  }

  async put<T = unknown>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${this.url}${path}`, {
      method: "PUT",
      headers: this.headers(),
      body: JSON.stringify(body),
    });
    return this.handleResponse<T>(res);
  }

  async delete<T = unknown>(path: string): Promise<T> {
    const res = await fetch(`${this.url}${path}`, {
      method: "DELETE",
      headers: this.headers(),
    });
    return this.handleResponse<T>(res);
  }

  private async handleResponse<T>(res: Response): Promise<T> {
    const text = await res.text();
    if (!res.ok) {
      let msg = res.statusText;
      try {
        const json = JSON.parse(text) as { error?: string };
        if (json.error) msg = json.error;
      } catch {}
      throw new Error(`HTTP ${res.status}: ${msg}`);
    }
    return JSON.parse(text) as T;
  }
}
