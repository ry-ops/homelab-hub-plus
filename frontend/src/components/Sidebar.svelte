<script>
  import { location } from "svelte-spa-router";

  const inventoryTypes = [
    { key: "hardware", label: "Hardware" },
    { key: "vms", label: "VMs" },
    { key: "apps", label: "Apps" },
    { key: "storage", label: "Storage" },
    { key: "networks", label: "Networks" },
    { key: "misc", label: "Misc" },
  ];

  let inventoryExpanded = true;

  function isActive(itemPath, currentPath) {
    if (itemPath === "/") return currentPath === "/";
    return currentPath.startsWith(itemPath);
  }

  function isInventoryActive(currentPath) {
    return currentPath.startsWith("/inventory") || currentPath === "/";
  }

  function toggleInventory() {
    inventoryExpanded = !inventoryExpanded;
  }
</script>

<nav class="sidebar">
  <div class="sidebar-header">
    <h2>HomeLab Hub</h2>
  </div>
  <ul class="nav-list">
    <li class="section">
      <div 
        class="section-header" 
        class:active={isInventoryActive($location)}
        on:click={toggleInventory}
        on:keydown={(e) => e.key === 'Enter' && toggleInventory()}
        role="button"
        tabindex="0"
      >
        <span class="icon">&#9776;</span>
        <span class="section-title">Inventory</span>
        <span class="expand-icon">{inventoryExpanded ? '▼' : '▶'}</span>
      </div>
      {#if inventoryExpanded}
        <ul class="subsection">
          {#each inventoryTypes as type}
            <li>
              <a
                href={"#/inventory/" + type.key}
                class:active={$location === "/inventory/" + type.key || ($location === "/" && type.key === "hardware")}
              >
                {type.label}
              </a>
            </li>
          {/each}
        </ul>
      {/if}
    </li>
    <li>
      <a
        href="#/map"
        class:active={isActive("/map", $location)}
      >
        <span class="icon">&#127758;</span>
        Map
      </a>
    </li>
    <li>
      <a
        href="#/docs"
        class:active={isActive("/docs", $location)}
      >
        <span class="icon">&#128196;</span>
        Docs
      </a>
    </li>
  </ul>
</nav>

<style>
  .sidebar {
    width: 220px;
    min-width: 220px;
    background: var(--pico-card-background-color, #1a1a2e);
    border-right: 1px solid var(--pico-muted-border-color, #333);
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow-y: auto;
    flex-shrink: 0;
    height: 100vh;
    position: sticky;
    top: 0;
  }
  .sidebar-header {
    padding: 1rem 1rem 1rem;
    border-bottom: 1px solid var(--pico-muted-border-color, #333);
    flex-shrink: 0;
  }
  .sidebar-header h2 {
    margin: 0;
    font-size: 1.2rem;
  }
  .nav-list {
    list-style: none;
    padding: 0.5rem 0;
    margin: 0;
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  .nav-list > li {
    display: block;
    width: 100%;
  }
  .sidebar li a {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    text-decoration: none;
    color: var(--pico-color, #ccc);
    border-radius: 0;
    transition: background 0.15s;
    width: 100%;
    box-sizing: border-box;
  }
  .sidebar li a:hover {
    background: var(--pico-primary-hover-background, rgba(255, 255, 255, 0.05));
  }
  .sidebar li a.active {
    color: var(--pico-primary, #6366f1);
    font-weight: 600;
  }
  .icon {
    font-size: 1.1rem;
    width: 1.5rem;
    text-align: center;
    flex-shrink: 0;
  }
  .section {
    margin: 0;
    display: block;
  }
  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    color: var(--pico-color, #ccc);
    font-weight: 500;
    cursor: pointer;
    width: 100%;
    box-sizing: border-box;
    transition: background 0.15s;
  }
  .section-header:hover {
    background: var(--pico-primary-hover-background, rgba(255, 255, 255, 0.05));
  }
  .section-header.active {
    color: var(--pico-primary, #6366f1);
    background: transparent !important;
  }
  .section-title {
    flex: 1;
  }
  .expand-icon {
    font-size: 0.7rem;
    flex-shrink: 0;
  }
  .subsection {
    padding: 0;
    margin: 0;
    list-style: none;
    display: flex;
    flex-direction: column;
  }
  .subsection li {
    margin: 0;
    display: block;
    width: 100%;
  }
  .subsection a {
    padding: 0.5rem 1rem 0.5rem 2.5rem;
    font-size: 0.9rem;
    display: flex;
    width: 100%;
    box-sizing: border-box;
  }
</style>
