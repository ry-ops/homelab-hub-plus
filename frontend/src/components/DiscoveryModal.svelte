<script>
  import { scanSubnet, importDiscovery } from "../lib/api.js";
  import { addToast } from "../lib/stores.js";

  export let show = false;

  // State machine: "configure" | "scanning" | "results"
  let state = "configure";

  // Configure
  let cidr = "192.168.1.0/24";
  let concurrency = 50;
  let timeout = 1.0;

  // Results
  let hosts = [];
  let scanSummary = { total: 0, alive: 0, duration_ms: 0 };
  let showDead = false;

  // Per-row editable state
  let rows = [];

  // Import state
  let importing = false;

  function close() {
    show = false;
    state = "configure";
    hosts = [];
    rows = [];
  }

  async function startScan() {
    if (!cidr.trim()) return;
    state = "scanning";
    try {
      const result = await scanSubnet(cidr.trim(), concurrency, timeout);
      hosts = result.hosts || [];
      scanSummary = {
        total: result.total,
        alive: result.alive,
        duration_ms: result.duration_ms,
      };

      // Build editable row state — pre-select alive hosts
      rows = hosts.map((h) => ({
        ...h,
        selected: h.alive,
        editType: h.suggested_type || "misc",
        editName: h.suggested_name || h.ip,
      }));

      state = "results";
    } catch (err) {
      addToast("Scan failed: " + err.message, "error");
      state = "configure";
    }
  }

  function selectAll() {
    rows = rows.map((r) => ({ ...r, selected: r.alive }));
  }

  function selectNone() {
    rows = rows.map((r) => ({ ...r, selected: false }));
  }

  $: visibleRows = showDead ? rows : rows.filter((r) => r.alive);
  $: selectedCount = rows.filter((r) => r.selected).length;

  const TYPE_OPTIONS = ["hardware", "vms", "apps", "storage", "networks", "misc"];

  async function doImport() {
    const selected = rows.filter((r) => r.selected);
    if (!selected.length) return;
    importing = true;
    try {
      const payload = selected.map((r) => ({
        ip: r.ip,
        type: r.editType,
        name: r.editName,
        hostname: r.hostname || r.ip,
        notes: [
          r.fingerprint !== "Unknown" ? `Fingerprint: ${r.fingerprint}` : null,
          r.open_ports?.length ? `Open ports: ${r.open_ports.join(", ")}` : null,
          r.http_title ? `HTTP title: ${r.http_title}` : null,
          r.ssh_banner ? `SSH banner: ${r.ssh_banner}` : null,
        ]
          .filter(Boolean)
          .join("\n"),
      }));
      const result = await importDiscovery(payload);
      addToast(
        `Imported ${result.imported} host${result.imported !== 1 ? "s" : ""}` +
          (result.errors?.length ? ` (${result.errors.length} errors)` : ""),
        result.errors?.length ? "warn" : "success"
      );
      close();
    } catch (err) {
      addToast("Import failed: " + err.message, "error");
    } finally {
      importing = false;
    }
  }
</script>

{#if show}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="backdrop" on:click|self={close}>
    <div class="modal" class:wide={state === "results"}>
      <!-- Header -->
      <div class="modal-header">
        <h2>Subnet Discovery</h2>
        <button class="close-btn" on:click={close} aria-label="Close">✕</button>
      </div>

      <!-- ----------------------------------------------------------------- -->
      <!-- STATE: configure                                                    -->
      <!-- ----------------------------------------------------------------- -->
      {#if state === "configure"}
        <div class="modal-body">
          <label class="field-label">
            CIDR Block
            <input
              class="text-input"
              type="text"
              placeholder="e.g. 192.168.1.0/24"
              bind:value={cidr}
              on:keydown={(e) => e.key === "Enter" && startScan()}
            />
          </label>

          <label class="field-label">
            Concurrency: {concurrency} threads
            <input type="range" min="1" max="200" bind:value={concurrency} />
          </label>

          <label class="field-label">
            Timeout: {timeout.toFixed(1)}s per probe
            <input type="range" min="0.1" max="5" step="0.1" bind:value={timeout} />
          </label>

          <p class="hint">
            Prefix length must be /16 or smaller (max 65 535 hosts). ICMP
            requires the backend container to have network privileges.
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={close}>Cancel</button>
          <button class="btn btn-primary" on:click={startScan} disabled={!cidr.trim()}>
            Scan
          </button>
        </div>

      <!-- ----------------------------------------------------------------- -->
      <!-- STATE: scanning                                                     -->
      <!-- ----------------------------------------------------------------- -->
      {:else if state === "scanning"}
        <div class="modal-body centered">
          <div class="spinner" aria-label="Scanning…"></div>
          <p class="scanning-label">Scanning {cidr}…</p>
          <p class="hint">This may take up to {Math.ceil(timeout * 3)}s per batch.</p>
        </div>

      <!-- ----------------------------------------------------------------- -->
      <!-- STATE: results                                                      -->
      <!-- ----------------------------------------------------------------- -->
      {:else if state === "results"}
        <div class="modal-body">
          <!-- Summary bar -->
          <div class="summary-bar">
            <span class="badge badge-alive">{scanSummary.alive} alive</span>
            <span class="badge badge-total">{scanSummary.total} total</span>
            <span class="badge badge-time">{scanSummary.duration_ms} ms</span>
            <label class="dead-toggle">
              <input type="checkbox" bind:checked={showDead} />
              Show dead hosts
            </label>
            <span class="spacer"></span>
            <button class="btn-link" on:click={selectAll}>All alive</button>
            <button class="btn-link" on:click={selectNone}>None</button>
          </div>

          <!-- Results table -->
          <div class="table-wrap">
            <table class="results-table">
              <thead>
                <tr>
                  <th class="col-check"></th>
                  <th class="col-ip">IP</th>
                  <th class="col-host">Hostname</th>
                  <th class="col-fp">Fingerprint</th>
                  <th class="col-ports">Ports</th>
                  <th class="col-type">Type</th>
                  <th class="col-name">Name</th>
                </tr>
              </thead>
              <tbody>
                {#each visibleRows as row, i (row.ip)}
                  <tr class:dead={!row.alive}>
                    <td class="col-check">
                      <input
                        type="checkbox"
                        bind:checked={rows[rows.indexOf(row)].selected}
                        disabled={!row.alive}
                      />
                    </td>
                    <td class="col-ip mono">{row.ip}</td>
                    <td class="col-host mono">{row.hostname || "—"}</td>
                    <td class="col-fp">
                      {#if row.alive}
                        <span class="fp-badge">{row.fingerprint}</span>
                      {:else}
                        <span class="dead-label">dead</span>
                      {/if}
                    </td>
                    <td class="col-ports mono">
                      {row.open_ports?.length ? row.open_ports.join(", ") : "—"}
                    </td>
                    <td class="col-type">
                      {#if row.alive}
                        <select bind:value={rows[rows.indexOf(row)].editType} class="type-select">
                          {#each TYPE_OPTIONS as opt}
                            <option value={opt}>{opt}</option>
                          {/each}
                        </select>
                      {:else}
                        —
                      {/if}
                    </td>
                    <td class="col-name">
                      {#if row.alive}
                        <input
                          class="name-input"
                          type="text"
                          bind:value={rows[rows.indexOf(row)].editName}
                        />
                      {:else}
                        —
                      {/if}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => (state = "configure")}>
            ← Back
          </button>
          <button
            class="btn btn-primary"
            on:click={doImport}
            disabled={importing || selectedCount === 0}
          >
            {importing ? "Importing…" : `Import ${selectedCount} selected`}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal {
    background: #fff;
    border-radius: 8px;
    width: 480px;
    max-width: 95vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .modal.wide {
    width: 900px;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    color: #6b7280;
    padding: 0.25rem;
    line-height: 1;
  }

  .close-btn:hover { color: #111; }

  .modal-body {
    padding: 1.25rem;
    overflow-y: auto;
    flex: 1;
  }

  .modal-body.centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    min-height: 180px;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 1rem 1.25rem;
    border-top: 1px solid #e5e7eb;
  }

  /* Fields */
  .field-label {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
  }

  .text-input {
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.875rem;
    font-family: monospace;
  }

  .text-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
  }

  input[type="range"] {
    width: 100%;
  }

  .hint {
    font-size: 0.8rem;
    color: #6b7280;
    margin: 0.5rem 0 0;
  }

  /* Spinner */
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .scanning-label {
    font-size: 1rem;
    font-weight: 500;
    color: #374151;
    margin: 0;
  }

  /* Summary bar */
  .summary-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
  }

  .spacer { flex: 1; }

  .badge {
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .badge-alive  { background: #d1fae5; color: #065f46; }
  .badge-total  { background: #e5e7eb; color: #374151; }
  .badge-time   { background: #dbeafe; color: #1e40af; }

  .dead-toggle {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.8rem;
    color: #6b7280;
    cursor: pointer;
  }

  .btn-link {
    background: none;
    border: none;
    color: #3b82f6;
    font-size: 0.8rem;
    cursor: pointer;
    padding: 0;
    text-decoration: underline;
  }

  .btn-link:hover { color: #1d4ed8; }

  /* Table */
  .table-wrap {
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
  }

  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
  }

  .results-table th {
    background: #f9fafb;
    padding: 0.5rem 0.6rem;
    text-align: left;
    font-weight: 600;
    color: #374151;
    border-bottom: 1px solid #e5e7eb;
    white-space: nowrap;
  }

  .results-table td {
    padding: 0.4rem 0.6rem;
    border-bottom: 1px solid #f3f4f6;
    vertical-align: middle;
  }

  .results-table tr:last-child td { border-bottom: none; }

  .results-table tr.dead td { color: #9ca3af; }

  .col-check  { width: 32px; }
  .col-ip     { width: 110px; }
  .col-host   { width: 140px; }
  .col-fp     { width: 130px; }
  .col-ports  { width: 100px; }
  .col-type   { width: 110px; }
  .col-name   { min-width: 120px; }

  .mono { font-family: monospace; }

  .fp-badge {
    background: #ede9fe;
    color: #5b21b6;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.75rem;
    white-space: nowrap;
  }

  .dead-label {
    color: #9ca3af;
    font-style: italic;
    font-size: 0.75rem;
  }

  .type-select {
    padding: 0.2rem 0.3rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.8rem;
    width: 100%;
  }

  .name-input {
    padding: 0.2rem 0.4rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.8rem;
    width: 100%;
    box-sizing: border-box;
  }

  /* Buttons */
  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .btn-primary  { background: #3b82f6; color: #fff; }
  .btn-primary:hover:not(:disabled)  { background: #2563eb; }

  .btn-secondary { background: #6b7280; color: #fff; }
  .btn-secondary:hover:not(:disabled) { background: #4b5563; }
</style>
