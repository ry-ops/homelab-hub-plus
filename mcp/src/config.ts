/**
 * Config loader for homelab-hub-mcp.
 *
 * Priority:
 *   1. HOMELAB_URL / HOMELAB_TOKEN env vars
 *   2. ~/.config/homelab-hub/config.json
 *   3. Defaults (localhost:8000, no token)
 */
import fs from "fs";
import os from "os";
import path from "path";

export interface HomelabConfig {
  url: string;
  token: string;
}

const CONFIG_PATH = path.join(
  os.homedir(),
  ".config",
  "homelab-hub",
  "config.json"
);

function readFileConfig(): Partial<HomelabConfig> {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
    return JSON.parse(raw) as Partial<HomelabConfig>;
  } catch {
    return {};
  }
}

export function loadConfig(): HomelabConfig {
  const fileConfig = readFileConfig();

  return {
    url:
      process.env["HOMELAB_URL"] ||
      fileConfig.url ||
      "http://localhost:8000",
    token:
      process.env["HOMELAB_TOKEN"] ||
      fileConfig.token ||
      "",
  };
}

export function saveConfig(config: Partial<HomelabConfig>): void {
  const dir = path.dirname(CONFIG_PATH);
  fs.mkdirSync(dir, { recursive: true });
  const existing = readFileConfig();
  fs.writeFileSync(CONFIG_PATH, JSON.stringify({ ...existing, ...config }, null, 2));
}
