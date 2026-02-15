<script>
  import Router from "svelte-spa-router";
  import Layout from "./components/Layout.svelte";
  import DocsPage from "./pages/DocsPage.svelte";
  import InventoryPage from "./pages/InventoryPage.svelte";
  import MapPage from "./pages/MapPage.svelte";
  import Toast from "./components/Toast.svelte";

  const routes = {
    "/": InventoryPage,
    "/docs": DocsPage,
    "/docs/:id": DocsPage,
    "/inventory": InventoryPage,
    "/inventory/:type": InventoryPage,
    "/inventory/:type/:id": InventoryPage,
    "/map": MapPage,
  };
</script>

<Layout>
  <Router {routes} />
</Layout>
<Toast />

<style>
  :global(body) {
    margin: 0;
    min-height: 100vh;
  }
  :global(#app) {
    min-height: 100vh;
  }
</style>
