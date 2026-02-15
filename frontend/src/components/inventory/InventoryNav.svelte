<script>
  export let activeType = "hardware";

  const types = [
    { key: "hardware", label: "Hardware" },
    { key: "vms", label: "VMs" },
    { key: "apps", label: "Apps" },
    { key: "storage", label: "Storage" },
    { key: "networks", label: "Networks" },
    { key: "misc", label: "Misc" },
  ];
</script>

<nav class="inventory-nav">
  {#each types as t}
    <a
      href={"#/inventory/" + t.key}
      class:active={activeType === t.key}
      role="tab"
    >
      {t.label}
    </a>
  {/each}
</nav>

<style>
  .inventory-nav {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--pico-muted-border-color, #333);
    margin-bottom: 1.5rem;
  }
  a {
    padding: 0.6rem 1.2rem;
    text-decoration: none;
    color: var(--pico-muted-color, #999);
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    font-size: 0.95rem;
    transition: color 0.15s, border-color 0.15s;
  }
  a:hover {
    color: var(--pico-color, #fff);
  }
  a.active {
    color: var(--pico-primary, #6366f1);
    border-bottom-color: var(--pico-primary, #6366f1);
    font-weight: 600;
  }
</style>
