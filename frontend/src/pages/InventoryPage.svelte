<script>
  import { params } from "svelte-spa-router";
  import EntityList from "../components/inventory/EntityList.svelte";
  import EntityDetail from "../components/inventory/EntityDetail.svelte";

  $: type = $params?.type || "hardware";
  $: entityId = $params?.id ? parseInt($params.id) : null;
</script>

<div class="inventory-page">
  {#if entityId}
    <EntityDetail {type} id={entityId} />
  {:else}
    <EntityList {type} />
  {/if}
</div>

<style>
  .inventory-page {
    /* Removed max-width to allow tables to use full horizontal space */
  }
</style>
