<script>
  import NetworkMap from "../components/map/NetworkMap.svelte";
  import MapControls from "../components/map/MapControls.svelte";

  let mapComponent;
</script>

<div class="map-page">
  <div class="map-header">
    <h2>Network Map</h2>
    <MapControls on:relayout={() => mapComponent?.relayout()} on:resetLayout={() => mapComponent?.resetLayout()} />
  </div>
  <div class="map-container">
    <NetworkMap bind:this={mapComponent} />
  </div>
</div>

<style>
  .map-page {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 3rem);
  }
  .map-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  .map-header h2 {
    margin: 0;
  }
  .map-container {
    flex: 1;
    border: 1px solid var(--pico-muted-border-color, #333);
    border-radius: 8px;
    overflow: hidden;
    position: relative;
  }
</style>
