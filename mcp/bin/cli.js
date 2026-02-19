#!/usr/bin/env node
/**
 * homelab-hub-mcp CLI
 *
 * Usage:
 *   homelab-hub-mcp start   — start the MCP server (default command)
 *   homelab-hub-mcp status  — show current config
 */
import { createRequire } from "module";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

// Support running from source (dist/) or via ts-node
const __dirname = dirname(fileURLToPath(import.meta.url));

// Dynamically import commander so it works before npm install in some edge cases
const { Command } = await import("commander").catch(async () => {
  console.error("commander not found — run: npm install");
  process.exit(1);
});

const { HomelabMCPServer } = await import("../dist/index.js").catch(async () => {
  console.error("dist/index.js not found — run: npm run build");
  process.exit(1);
});

const pkg = createRequire(import.meta.url)("../package.json");

const program = new Command();

program
  .name("homelab-hub-mcp")
  .description("MCP server for homelab-hub-plus")
  .version(pkg.version);

program
  .command("start", { isDefault: true })
  .description("Start the MCP server (StdioTransport)")
  .action(async () => {
    const server = new HomelabMCPServer();
    await server.start();
  });

program
  .command("status")
  .description("Show current configuration")
  .action(async () => {
    const { loadConfig } = await import("../dist/config.js");
    const config = loadConfig();
    console.log("HOMELAB_URL :", config.url);
    console.log("Token set   :", config.token ? "yes" : "no (dev mode)");
  });

program.parseAsync(process.argv);
