<script>
  import { push } from "svelte-spa-router";
  import { get, post, del } from "../../lib/api.js";
  import { addToast } from "../../lib/stores.js";
  import EntityDetail from "./EntityDetail.svelte";

  export let type = "hardware";

  let items = [];
  let loading = true;
  let search = "";
  let showCreate = false;

  const COLUMNS = {
    hardware: ["name", "hostname", "ip_address", "os", "cpu", "ram_gb"],
    vms: ["name", "hostname", "ip_address", "os", "cpu_cores", "ram_gb"],
    apps: ["name", "hostname", "ip_address", "external_hostname", "port"],
    storage: ["name", "storage_type", "raid_type", "raw_space_tb", "usable_space_tb"],
    networks: ["name", "vlan_id", "subnet", "gateway"],
    misc: ["name", "category", "hostname", "ip_address"],
  };

  const LABELS = {
    ip_address: "IP Address",
    ram_gb: "RAM (GB)",
    cpu_cores: "CPU Cores",
    external_hostname: "External Host",
    vlan_id: "VLAN ID",
    raw_space_tb: "Raw (TB)",
    usable_space_tb: "Usable (TB)",
    storage_type: "Type",
    raid_type: "RAID",
  };

  function label(col) {
    return LABELS[col] || col.charAt(0).toUpperCase() + col.slice(1).replace(/_/g, " ");
  }

  $: columns = COLUMNS[type] || ["name"];

  async function loadItems() {
    loading = true;
    items = []; // Clear items before loading
    try {
      const res = await get(`/${type}`);
      items = res.data;
    } catch (e) {
      addToast(e.message, "error");
    }
    loading = false;
  }

  // Reload whenever type changes
  $: type, loadItems();

  $: filtered = search
    ? items.filter((item) =>
        Object.values(item).some(
          (v) => v && String(v).toLowerCase().includes(search.toLowerCase())
        )
      )
    : items;

  async function deleteItem(id) {
    if (!confirm("Delete this item?")) return;
    try {
      await del(`/${type}/${id}`);
      addToast("Deleted", "success");
      loadItems();
    } catch (e) {
      addToast(e.message, "error");
    }
  }

  async function duplicateItem(item) {
    try {
      // Create a copy of the item
      const duplicate = { ...item };
      // Remove id and update name
      delete duplicate.id;
      duplicate.name = `Copy of ${item.name}`;
      
      // Create the duplicate
      await post(`/${type}`, duplicate);
      addToast("Duplicated successfully", "success");
      loadItems();
    } catch (e) {
      addToast(e.message, "error");
    }
  }

  function handleSaved() {
    showCreate = false;
    loadItems();
  }
</script>

<div class="entity-list">
  <div class="list-header">
    <h2>{type.charAt(0).toUpperCase() + type.slice(1)}</h2>
    <div class="actions">
      <input type="search" placeholder="Filter..." bind:value={search} />
      <button on:click={() => (showCreate = true)}>+ Add</button>
    </div>
  </div>

  {#if showCreate}
    <div class="create-panel">
      <EntityDetail {type} id={null} on:saved={handleSaved} on:cancel={() => (showCreate = false)} />
    </div>
  {/if}

  {#if loading}
    <p aria-busy="true">Loading...</p>
  {:else if filtered.length === 0}
    <p>No items found.</p>
  {:else}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            {#each columns as col}
              <th>{label(col)}</th>
            {/each}
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each filtered as item (item.id)}
            <tr on:click={() => push(`/inventory/${type}/${item.id}`)} class="clickable">
              {#each columns as col}
                <td>{item[col] ?? ""}</td>
              {/each}
              <td>
                <div class="button-group">
                  <button class="outline secondary small" on:click|stopPropagation={() => duplicateItem(item)}>
                    Duplicate
                  </button>
                  <button class="outline secondary small" on:click|stopPropagation={() => deleteItem(item.id)}>
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  .list-header h2 {
    margin: 0;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  .actions input {
    margin: 0;
    max-width: 200px;
  }
  .actions button {
    margin: 0;
    white-space: nowrap;
  }
  .table-wrap {
    overflow-x: auto;
  }
  tr.clickable {
    cursor: pointer;
  }
  tr.clickable:hover {
    background: var(--pico-primary-hover-background, rgba(255, 255, 255, 0.03));
  }
  .create-panel {
    margin-bottom: 2rem;
    padding: 1.5rem;
    border: 1px solid var(--pico-muted-border-color, #333);
    border-radius: 8px;
  }
  .small {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
  .button-group {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
  }
</style>
