<script>
  import { params } from "svelte-spa-router";
  import InventoryNav from "../components/inventory/InventoryNav.svelte";
  import EntityList from "../components/inventory/EntityList.svelte";
  import EntityDetail from "../components/inventory/EntityDetail.svelte";

  $: type = $params?.type || "hardware";
  $: entityId = $params?.id ? parseInt($params.id) : null;
</script>

<div class="inventory-page">
  <InventoryNav activeType={type} />

  {#if entityId}
    <EntityDetail {type} id={entityId} />
  {:else}
    <EntityList {type} />
  {/if}
</div>

<style>
  .inventory-page {
    max-width: 1200px;
  }
</style>
