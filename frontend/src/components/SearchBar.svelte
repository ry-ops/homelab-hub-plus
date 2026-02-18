<script>
  import { push } from "svelte-spa-router";
  import { searchSemantic } from "../lib/api.js";

  let query = "";
  let results = [];
  let loading = false;
  let open = false;
  let debounceTimer;
  let inputEl;

  const TYPE_LABELS = {
    hardware: "Hardware",
    vms: "VM",
    apps: "App",
    storage: "Storage",
    networks: "Network",
    shares: "Share",
    misc: "Misc",
    documents: "Doc",
  };

  function onInput() {
    clearTimeout(debounceTimer);
    if (!query.trim()) {
      results = [];
      open = false;
      return;
    }
    debounceTimer = setTimeout(doSearch, 300);
  }

  async function doSearch() {
    loading = true;
    open = true;
    try {
      const res = await searchSemantic(query, 10);
      results = res.data || [];
    } catch {
      results = [];
    }
    loading = false;
  }

  function navigate(result) {
    const type = result.entity_type;
    const id = result.entity_id;
    // documents live at /docs/:id, everything else at /inventory/:type/:id
    if (type === "documents") {
      push(`/docs/${id}`);
    } else {
      push(`/inventory/${type}/${id}`);
    }
    close();
  }

  function close() {
    open = false;
    query = "";
    results = [];
  }

  function onKeydown(e) {
    if (e.key === "Escape") close();
  }

  function onBlur(e) {
    // Delay so clicks on results register first
    setTimeout(() => { open = false; }, 150);
  }

  function scoreBar(score) {
    return Math.round(score * 100);
  }
</script>

<div class="search-wrap">
  <div class="search-input-wrap">
    <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <input
      bind:this={inputEl}
      bind:value={query}
      on:input={onInput}
      on:keydown={onKeydown}
      on:blur={onBlur}
      on:focus={() => { if (results.length) open = true; }}
      type="search"
      placeholder="Semantic search..."
      autocomplete="off"
      spellcheck="false"
    />
    {#if loading}
      <span class="spinner" aria-hidden="true"></span>
    {/if}
  </div>

  {#if open}
    <div class="dropdown">
      {#if results.length === 0 && !loading}
        <div class="empty">No results for "{query}"</div>
      {:else}
        {#each results as r}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-no-static-element-interactions -->
          <div class="result" on:click={() => navigate(r)}>
            <span class="type-badge">{TYPE_LABELS[r.entity_type] ?? r.entity_type}</span>
            <span class="name">{r.name}</span>
            <span class="score" title="Relevance score">{scoreBar(r.score)}%</span>
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</div>

<style>
  .search-wrap {
    position: relative;
    width: 280px;
  }

  .search-input-wrap {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 0.6rem;
    color: #888;
    pointer-events: none;
    flex-shrink: 0;
  }

  input {
    width: 100%;
    padding: 0.4rem 2rem 0.4rem 2rem;
    background: #2a2d35;
    border: 1px solid #444;
    border-radius: 6px;
    color: #eee;
    font-size: 0.875rem;
    outline: none;
    box-sizing: border-box;
    margin: 0;
  }

  input:focus {
    border-color: #6366f1;
  }

  input::placeholder {
    color: #666;
  }

  /* Hide browser default search clear button */
  input[type="search"]::-webkit-search-cancel-button {
    display: none;
  }

  .spinner {
    position: absolute;
    right: 0.6rem;
    width: 12px;
    height: 12px;
    border: 2px solid #444;
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .dropdown {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    right: 0;
    background: #1e2028;
    border: 1px solid #444;
    border-radius: 6px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    z-index: 10000;
    max-height: 360px;
    overflow-y: auto;
  }

  .empty {
    padding: 0.75rem 1rem;
    color: #888;
    font-size: 0.875rem;
  }

  .result {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    cursor: pointer;
    border-bottom: 1px solid #2a2d35;
    transition: background 0.1s;
  }

  .result:last-child {
    border-bottom: none;
  }

  .result:hover {
    background: #2a2d35;
  }

  .type-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    background: #6366f1;
    color: white;
    flex-shrink: 0;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .name {
    flex: 1;
    font-size: 0.875rem;
    color: #eee;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .score {
    font-size: 0.75rem;
    color: #666;
    flex-shrink: 0;
  }
</style>
