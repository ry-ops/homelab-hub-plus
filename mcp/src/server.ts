/**
 * MCP server for homelab-hub-plus.
 *
 * Exposes 10 tools that map directly to Flask API endpoints.
 * Transport: StdioServerTransport (Claude Desktop / Claude Code compatible).
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { HomelabClient } from "./client.js";

// ---------------------------------------------------------------------------
// Tool definitions
// ---------------------------------------------------------------------------

const TOOLS = [
  {
    name: "inventory_list",
    description: "List all entities of a given type (hardware, vms, apps, storage, networks, misc, shares, documents).",
    inputSchema: {
      type: "object",
      properties: {
        type: {
          type: "string",
          enum: ["hardware", "vms", "apps", "storage", "networks", "misc", "shares", "documents"],
          description: "Entity type to list",
        },
      },
      required: ["type"],
    },
  },
  {
    name: "inventory_search",
    description: "Semantic search across all inventory entities using Qdrant.",
    inputSchema: {
      type: "object",
      properties: {
        q: { type: "string", description: "Search query" },
        limit: { type: "number", description: "Max results (default 20)", default: 20 },
      },
      required: ["q"],
    },
  },
  {
    name: "inventory_create",
    description: "Create a new inventory entity.",
    inputSchema: {
      type: "object",
      properties: {
        type: {
          type: "string",
          enum: ["hardware", "vms", "apps", "storage", "networks", "misc", "shares", "documents"],
        },
        data: { type: "object", description: "Entity fields" },
      },
      required: ["type", "data"],
    },
  },
  {
    name: "inventory_update",
    description: "Update an existing inventory entity by ID.",
    inputSchema: {
      type: "object",
      properties: {
        type: {
          type: "string",
          enum: ["hardware", "vms", "apps", "storage", "networks", "misc", "shares", "documents"],
        },
        id: { type: "number", description: "Entity ID" },
        data: { type: "object", description: "Fields to update" },
      },
      required: ["type", "id", "data"],
    },
  },
  {
    name: "inventory_delete",
    description: "Delete an inventory entity by ID. Requires confirm=true to proceed.",
    inputSchema: {
      type: "object",
      properties: {
        type: {
          type: "string",
          enum: ["hardware", "vms", "apps", "storage", "networks", "misc", "shares", "documents"],
        },
        id: { type: "number", description: "Entity ID" },
        confirm: { type: "boolean", description: "Must be true to confirm deletion" },
      },
      required: ["type", "id", "confirm"],
    },
  },
  {
    name: "health_check",
    description: "Ping one or more hosts and return alive/latency status.",
    inputSchema: {
      type: "object",
      properties: {
        hosts: {
          type: "array",
          items: { type: "string" },
          description: "IP addresses or hostnames to ping",
        },
      },
      required: ["hosts"],
    },
  },
  {
    name: "search_index",
    description: "Trigger a full Qdrant backfill of all existing inventory entities (idempotent).",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "map_graph",
    description: "Retrieve the network/infrastructure map graph (nodes + edges).",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "app_status",
    description: "Check if the homelab-hub-plus backend is healthy.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "inventory_all",
    description: "Retrieve all inventory items across all entity types in one call.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "discover_subnet",
    description:
      "Scan a subnet CIDR for live hosts with port fingerprinting and banner grabbing. " +
      "Optionally auto-import all alive hosts into inventory.",
    inputSchema: {
      type: "object",
      properties: {
        cidr: {
          type: "string",
          description: 'CIDR block to scan, e.g. "192.168.1.0/24". Prefix length must be /16 or smaller.',
        },
        concurrency: {
          type: "number",
          description: "Number of parallel probe threads (default 50)",
          default: 50,
        },
        timeout: {
          type: "number",
          description: "Per-probe timeout in seconds (default 1.0)",
          default: 1.0,
        },
        import_alive: {
          type: "boolean",
          description: "If true, automatically import all alive hosts into inventory after scanning",
          default: false,
        },
      },
      required: ["cidr"],
    },
  },
];

// ---------------------------------------------------------------------------
// Server class
// ---------------------------------------------------------------------------

export class HomelabMCPServer {
  private server: Server;
  private client: HomelabClient;

  constructor() {
    this.client = new HomelabClient();
    this.server = new Server(
      { name: "homelab-hub", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );
    this.setupHandlers();
  }

  private setupHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: TOOLS,
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (req) => {
      const { name, arguments: args = {} } = req.params;
      try {
        const result = await this.executeTool(name, args as Record<string, unknown>);
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return {
          content: [{ type: "text", text: `Error: ${message}` }],
          isError: true,
        };
      }
    });
  }

  private async executeTool(
    name: string,
    args: Record<string, unknown>
  ): Promise<unknown> {
    switch (name) {
      case "inventory_list": {
        const type = args["type"] as string;
        return this.client.get(`/api/${type}`);
      }

      case "inventory_search": {
        const q = encodeURIComponent(args["q"] as string);
        const limit = (args["limit"] as number | undefined) ?? 20;
        return this.client.get(`/api/search?q=${q}&limit=${limit}`);
      }

      case "inventory_create": {
        const type = args["type"] as string;
        return this.client.post(`/api/${type}`, args["data"]);
      }

      case "inventory_update": {
        const type = args["type"] as string;
        const id = args["id"] as number;
        return this.client.put(`/api/${type}/${id}`, args["data"]);
      }

      case "inventory_delete": {
        if (!args["confirm"]) {
          return { error: "Deletion requires confirm=true" };
        }
        const type = args["type"] as string;
        const id = args["id"] as number;
        return this.client.delete(`/api/${type}/${id}`);
      }

      case "health_check": {
        return this.client.post("/api/health-check", { hosts: args["hosts"] });
      }

      case "search_index": {
        return this.client.post("/api/search/index");
      }

      case "map_graph": {
        return this.client.get("/api/map/graph");
      }

      case "app_status": {
        return this.client.get("/api/health");
      }

      case "inventory_all": {
        return this.client.get("/api/inventory");
      }

      case "discover_subnet": {
        const cidr = args["cidr"] as string;
        const concurrency = (args["concurrency"] as number | undefined) ?? 50;
        const timeout = (args["timeout"] as number | undefined) ?? 1.0;
        const importAlive = (args["import_alive"] as boolean | undefined) ?? false;

        const scanResult = await this.client.post("/api/discovery/scan", {
          cidr,
          concurrency,
          timeout,
        });

        if (!importAlive) {
          return scanResult;
        }

        // Auto-import all alive hosts
        const scanData = scanResult as { hosts?: Array<Record<string, unknown>> };
        const aliveHosts = (scanData.hosts || [])
          .filter((h) => h["alive"])
          .map((h) => ({
            ip: h["ip"],
            type: h["suggested_type"] || "misc",
            name: h["suggested_name"] || h["ip"],
            hostname: h["hostname"] || h["ip"],
            notes: [
              h["fingerprint"] !== "Unknown" ? `Fingerprint: ${h["fingerprint"]}` : null,
              Array.isArray(h["open_ports"]) && (h["open_ports"] as number[]).length
                ? `Open ports: ${(h["open_ports"] as number[]).join(", ")}`
                : null,
              h["http_title"] ? `HTTP title: ${h["http_title"]}` : null,
              h["ssh_banner"] ? `SSH banner: ${h["ssh_banner"]}` : null,
            ]
              .filter(Boolean)
              .join("\n"),
          }));

        const importResult = aliveHosts.length
          ? await this.client.post("/api/discovery/import", { hosts: aliveHosts })
          : { imported: 0, by_type: {}, errors: [] };

        return { scan: scanResult, import: importResult };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  async start(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    // Server runs until stdin closes
  }

  async stop(): Promise<void> {
    await this.server.close();
  }
}
