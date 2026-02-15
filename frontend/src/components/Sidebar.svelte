<script>
  import { location } from "svelte-spa-router";

  const navItems = [
    { path: "/inventory", label: "Inventory", icon: "&#9776;" },
    { path: "/docs", label: "Docs", icon: "&#128196;" },
    { path: "/map", label: "Map", icon: "&#127758;" },
  ];

  function isActive(itemPath, currentPath) {
    if (itemPath === "/") return currentPath === "/";
    return currentPath.startsWith(itemPath);
  }
</script>

<nav class="sidebar">
  <div class="sidebar-header">
    <h2>HomeLab Hub</h2>
  </div>
  <ul>
    {#each navItems as item}
      <li>
        <a
          href={"#" + item.path}
          class:active={isActive(item.path, $location)}
        >
          <span class="icon">{@html item.icon}</span>
          {item.label}
        </a>
      </li>
    {/each}
  </ul>
</nav>

<style>
  .sidebar {
    width: 220px;
    background: var(--pico-card-background-color, #1a1a2e);
    border-right: 1px solid var(--pico-muted-border-color, #333);
    display: flex;
    flex-direction: column;
    padding: 1rem 0;
  }
  .sidebar-header {
    padding: 0 1rem 1rem;
    border-bottom: 1px solid var(--pico-muted-border-color, #333);
  }
  .sidebar-header h2 {
    margin: 0;
    font-size: 1.2rem;
  }
  ul {
    list-style: none;
    padding: 0.5rem 0;
    margin: 0;
  }
  li a {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    text-decoration: none;
    color: var(--pico-color, #ccc);
    border-radius: 0;
    transition: background 0.15s;
  }
  li a:hover {
    background: var(--pico-primary-hover-background, rgba(255, 255, 255, 0.05));
  }
  li a.active {
    background: var(--pico-primary-background, rgba(99, 102, 241, 0.15));
    color: var(--pico-primary, #6366f1);
    font-weight: 600;
  }
  .icon {
    font-size: 1.1rem;
    width: 1.5rem;
    text-align: center;
  }
</style>
