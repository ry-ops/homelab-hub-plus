<script>
  import Sidebar from "./Sidebar.svelte";
</script>

<div class="app-layout">
  <Sidebar />
  <main class="main-content">
    <slot />
  </main>
</div>

<style>
  .app-layout {
    display: flex;
    min-height: 100vh;
  }
  .main-content {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
  }
</style>
