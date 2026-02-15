<script>
  import { onMount, onDestroy } from "svelte";
  import cytoscape from "cytoscape";
  import dagre from "cytoscape-dagre";
  import { get, put } from "../../lib/api.js";
  import { addToast } from "../../lib/stores.js";

  cytoscape.use(dagre);

  let container;
  let cy;
  let saveTimeout;

  const NODE_STYLES = {
    hardware:  { shape: "round-rectangle", color: "#4A90D9" },
    vms:       { shape: "ellipse",          color: "#7EC850" },
    apps:      { shape: "round-rectangle", color: "#F5A623" },
    storage:   { shape: "barrel",           color: "#9B59B6" },
    networks:  { shape: "diamond",          color: "#E74C3C" },
    misc:      { shape: "tag",              color: "#95A5A6" },
  };

  onMount(async () => {
    try {
      const [graphRes, layoutRes] = await Promise.all([
        get("/map/graph"),
        get("/map/layout"),
      ]);

      const savedPositions = layoutRes.data || {};

      // Apply saved positions to nodes
      const nodes = graphRes.nodes.map((n) => {
        const saved = savedPositions[n.data.id];
        if (saved) {
          n.position = { x: saved.x, y: saved.y };
          n.locked = saved.pinned;
        }
        return n;
      });

      cy = cytoscape({
        container,
        elements: { nodes, edges: graphRes.edges },
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              "text-valign": "center",
              "text-halign": "center",
              "font-size": "11px",
              color: "#fff",
              "text-outline-width": 2,
              "text-outline-color": "#333",
              width: 50,
              height: 50,
            },
          },
          // Per-type styles
          ...Object.entries(NODE_STYLES).map(([type, s]) => ({
            selector: `node[type="${type}"]`,
            style: {
              shape: s.shape,
              "background-color": s.color,
            },
          })),
          {
            selector: "edge",
            style: {
              width: 2,
              "line-color": "#666",
              "target-arrow-color": "#666",
              "target-arrow-shape": "triangle",
              "curve-style": "bezier",
              label: "data(label)",
              "font-size": "9px",
              color: "#999",
              "text-rotation": "autorotate",
            },
          },
          {
            selector: "edge[?manual]",
            style: {
              "line-style": "dashed",
              "line-color": "#888",
            },
          },
        ],
        layout: { name: "preset" }, // Use saved positions first
        minZoom: 0.2,
        maxZoom: 3,
      });

      // If no saved positions, run dagre layout
      const hasSavedPositions = Object.keys(savedPositions).length > 0;
      if (!hasSavedPositions && nodes.length > 0) {
        runDagreLayout();
      }

      // Persist positions on drag end
      cy.on("dragfree", "node", () => {
        debounceSaveLayout();
      });

      // Show details on tap
      cy.on("tap", "node", (evt) => {
        const node = evt.target;
        const data = node.data();
        addToast(`${data.type}: ${data.label}`, "info");
      });
    } catch (e) {
      addToast("Failed to load map: " + e.message, "error");
    }
  });

  onDestroy(() => {
    if (cy) cy.destroy();
    clearTimeout(saveTimeout);
  });

  function runDagreLayout() {
    if (!cy) return;
    cy.layout({
      name: "dagre",
      rankDir: "TB",
      nodeSep: 60,
      rankSep: 100,
      animate: true,
      animationDuration: 300,
    }).run();
  }

  function debounceSaveLayout() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(saveLayout, 500);
  }

  async function saveLayout() {
    if (!cy) return;
    const positions = {};
    cy.nodes().forEach((node) => {
      const pos = node.position();
      positions[node.id()] = { x: pos.x, y: pos.y, pinned: true };
    });
    try {
      await put("/map/layout", { positions });
    } catch (e) {
      // silent fail on layout save
    }
  }

  export function relayout() {
    runDagreLayout();
    setTimeout(saveLayout, 500);
  }

  export function resetLayout() {
    if (!cy) return;
    cy.nodes().unlock();
    runDagreLayout();
    setTimeout(saveLayout, 500);
  }
</script>

<div class="cy-container" bind:this={container}></div>

<div class="legend">
  {#each Object.entries(NODE_STYLES) as [type, style]}
    <span class="legend-item">
      <span class="legend-dot" style="background: {style.color}"></span>
      {type}
    </span>
  {/each}
</div>

<style>
  .cy-container {
    width: 100%;
    height: 100%;
    min-height: 400px;
  }
  .legend {
    position: absolute;
    bottom: 0.75rem;
    left: 0.75rem;
    display: flex;
    gap: 0.75rem;
    background: rgba(0, 0, 0, 0.6);
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-size: 0.75rem;
    color: #ccc;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }
  .legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
  }
</style>
