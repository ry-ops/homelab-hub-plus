<script>
  import Sidebar from "./Sidebar.svelte";
  import SearchBar from "./SearchBar.svelte";
  import DiscoveryModal from "./DiscoveryModal.svelte";
  import { get, post, getToken, setToken, reindexSearch } from "../lib/api.js";

  let showDiscoveryModal = false;

  // Token settings modal state
  let showTokenModal = false;
  let tokenInput = getToken();

  function saveToken() {
    setToken(tokenInput.trim());
    showTokenModal = false;
  }

  // Toast state
  let toast = null;
  let toastTimer = null;

  function showToast(message, type = "info") {
    clearTimeout(toastTimer);
    toast = { message, type };
    toastTimer = setTimeout(() => { toast = null; }, 4000);
  }

  // Reindex
  let reindexing = false;

  async function handleReindex() {
    reindexing = true;
    try {
      const result = await reindexSearch();
      showToast(`Indexed ${result.indexed} entities (${result.status})`, result.status === "ok" ? "success" : "warn");
    } catch (err) {
      showToast("Reindex failed: " + err.message, "error");
    } finally {
      reindexing = false;
    }
  }

  // Export — uses api.js get() so auth header is injected automatically
  async function exportDatabase() {
    try {
      const data = await get("/inventory/export");
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "homelab-export.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      showToast("Export failed: " + error.message, "error");
    }
  }

  // Import — uses api.js post() so auth header is injected automatically
  async function importDatabase(event) {
    const file = event.target.files[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      await post("/inventory/import", data);
      showToast("Import completed successfully!", "success");
      setTimeout(() => window.location.reload(), 1200);
    } catch (error) {
      showToast("Import failed: " + error.message, "error");
    }
  }

  function triggerImport() {
    document.getElementById("import-file-input").click();
  }
</script>

<div class="layout">
  <header class="header">
    <h1>Home Lab Hub+</h1>
    <div class="header-center">
      <SearchBar />
    </div>
    <div class="header-actions">
      <button class="btn btn-success" on:click={handleReindex} disabled={reindexing}>
        {reindexing ? "Indexing…" : "Reindex Search"}
      </button>
      <button class="btn btn-discover" on:click={() => (showDiscoveryModal = true)}>Discover</button>
      <button class="btn btn-primary" on:click={exportDatabase}>Export Data</button>
      <button class="btn btn-secondary" on:click={triggerImport}>Import Data</button>
      <button class="btn btn-outline" on:click={() => { tokenInput = getToken(); showTokenModal = true; }} title="API Token Settings">⚙</button>
      <input id="import-file-input" type="file" accept=".json" style="display: none;" on:change={importDatabase} />
    </div>
  </header>

  <div class="content">
    <Sidebar />
    <main class="main">
      <slot />
    </main>
  </div>
</div>

<!-- Discovery modal -->
<DiscoveryModal bind:show={showDiscoveryModal} />

<!-- Token settings modal -->
{#if showTokenModal}
  <div class="modal-backdrop" on:click|self={() => showTokenModal = false}>
    <div class="modal">
      <h2>API Token</h2>
      <p>Enter the Bearer token for this homelab-hub instance. Leave blank for open (dev) access.</p>
      <input
        class="token-input"
        type="password"
        placeholder="Paste API token here…"
        bind:value={tokenInput}
        on:keydown={(e) => e.key === "Enter" && saveToken()}
      />
      <div class="modal-actions">
        <button class="btn btn-primary" on:click={saveToken}>Save</button>
        <button class="btn btn-secondary" on:click={() => showTokenModal = false}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- Toast notification -->
{#if toast}
  <div class="toast toast-{toast.type}">{toast.message}</div>
{/if}

<style>
  .layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .header {
    background-color: #1a1d23;
    color: white;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .header-center {
    flex: 1;
    display: flex;
    justify-content: center;
    max-width: 400px;
    margin: 0 auto;
  }

  .header h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    line-height: 1.5;
    text-align: center;
    vertical-align: middle;
    box-sizing: border-box;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-primary {
    background-color: #007bff;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #0056b3;
  }

  .btn-secondary {
    background-color: #6c757d;
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background-color: #545b62;
  }

  .btn-success {
    background-color: #28a745;
    color: white;
  }

  .btn-success:hover:not(:disabled) {
    background-color: #1e7e34;
  }

  .btn-discover {
    background-color: #7c3aed;
    color: white;
  }

  .btn-discover:hover {
    background-color: #6d28d9;
  }

  .btn-outline {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.4);
    color: white;
    font-size: 1.1rem;
    padding: 0.4rem 0.7rem;
  }

  .btn-outline:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .content {
    display: flex;
    flex: 1;
  }

  .main {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
  }

  /* Token modal */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: #fff;
    border-radius: 8px;
    padding: 2rem;
    width: 400px;
    max-width: 90vw;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  }

  .modal h2 {
    margin: 0 0 0.5rem;
    font-size: 1.2rem;
  }

  .modal p {
    margin: 0 0 1rem;
    font-size: 0.9rem;
    color: #555;
  }

  .token-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9rem;
    box-sizing: border-box;
    margin-bottom: 1rem;
  }

  .modal-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
  }

  /* Toast */
  .toast {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    padding: 0.75rem 1.25rem;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    color: white;
    z-index: 2000;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .toast-info    { background: #17a2b8; }
  .toast-success { background: #28a745; }
  .toast-warn    { background: #fd7e14; }
  .toast-error   { background: #dc3545; }
</style>
