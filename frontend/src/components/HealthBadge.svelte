<script>
  import { onMount } from "svelte";
  import { pingHosts } from "../lib/api.js";

  /** IP address or hostname to ping */
  export let host = "";

  // States: "pending" | "alive" | "dead" | "unknown"
  let status = "pending";
  let latency = null;
  let method = null;

  onMount(async () => {
    if (!host) {
      status = "unknown";
      return;
    }
    try {
      const res = await pingHosts([host]);
      const result = res.data?.[host];
      if (!result) {
        status = "unknown";
        return;
      }
      status = result.alive ? "alive" : "dead";
      latency = result.latency_ms;
      method = result.method;
    } catch {
      status = "unknown";
    }
  });

  $: label = status === "pending"
    ? "Checking…"
    : status === "alive"
      ? latency !== null ? `Online · ${latency}ms` : "Online"
      : status === "dead"
        ? "Offline"
        : "Unknown";

  $: title = method ? `${label} (${method})` : label;
</script>

<span class="badge {status}" {title}>
  <span class="dot" aria-hidden="true"></span>
  {label}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    white-space: nowrap;
    cursor: default;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  /* pending */
  .badge.pending {
    background: rgba(100, 100, 120, 0.2);
    color: #888;
  }
  .badge.pending .dot {
    background: #666;
    animation: pulse 1.2s ease-in-out infinite;
  }

  /* alive */
  .badge.alive {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
  }
  .badge.alive .dot {
    background: #22c55e;
  }

  /* dead */
  .badge.dead {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
  }
  .badge.dead .dot {
    background: #ef4444;
  }

  /* unknown */
  .badge.unknown {
    background: rgba(100, 100, 120, 0.15);
    color: #666;
  }
  .badge.unknown .dot {
    background: #555;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
</style>
