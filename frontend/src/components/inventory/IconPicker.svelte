<script>
  import { onMount } from "svelte";
  
  export let value = "";

  let fileInput;
  let activeTab = "emoji"; // emoji, browse, upload
  let dashboardIcons = [];
  let searchQuery = "";
  let loadingIcons = false;

  // Fetch available icons from GitHub using Git Trees API
  async function loadDashboardIcons() {
    if (dashboardIcons.length > 0) return; // Already loaded
    
    loadingIcons = true;
    try {
      // First get the default branch
      const repoResponse = await fetch(
        "https://api.github.com/repos/homarr-labs/dashboard-icons"
      );
      const repo = await repoResponse.json();
      const defaultBranch = repo.default_branch || 'main';
      
      // Get the tree recursively
      const treeResponse = await fetch(
        `https://api.github.com/repos/homarr-labs/dashboard-icons/git/trees/${defaultBranch}?recursive=1`
      );
      const tree = await treeResponse.json();
      
      // Filter for PNG files in the png directory
      dashboardIcons = tree.tree
        .filter(item => item.path.startsWith('png/') && item.path.endsWith('.png'))
        .map(item => ({
          name: item.path.replace('png/', '').replace('.png', ''),
          url: `https://raw.githubusercontent.com/homarr-labs/dashboard-icons/${defaultBranch}/${item.path}`
        }))
        .sort((a, b) => a.name.localeCompare(b.name));
    } catch (e) {
      console.error('Failed to load dashboard icons:', e);
    }
    loadingIcons = false;
  }

  $: filteredIcons = searchQuery
    ? dashboardIcons.filter(icon => 
        icon.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : dashboardIcons;

  async function selectDashboardIcon(iconUrl) {
    try {
      const response = await fetch(iconUrl);
      const blob = await response.blob();
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          // Create canvas to resize image with padding
          const canvas = document.createElement('canvas');
          const iconSize = 64;
          const canvasSize = 96;
          
          let width = img.width;
          let height = img.height;
          
          // Calculate new dimensions maintaining aspect ratio
          if (width > height) {
            if (width > iconSize) {
              height = (height * iconSize) / width;
              width = iconSize;
            }
          } else {
            if (height > iconSize) {
              width = (width * iconSize) / height;
              height = iconSize;
            }
          }
          
          canvas.width = canvasSize;
          canvas.height = canvasSize;
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvasSize, canvasSize);
          
          const x = (canvasSize - width) / 2;
          const y = (canvasSize - height) / 2;
          ctx.drawImage(img, x, y, width, height);
          
          value = canvas.toDataURL('image/png');
          activeTab = "emoji"; // Close the browser after selection
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(blob);
    } catch (e) {
      console.error('Failed to load icon:', e);
      alert('Failed to load icon');
    }
  }

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      alert("Please select an image file");
      return;
    }

    // Validate file size (max 1MB)
    if (file.size > 1024 * 1024) {
      alert("Image must be smaller than 1MB");
      return;
    }

    // Convert to data URL and resize
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Create canvas to resize image with padding
        const canvas = document.createElement('canvas');
        const iconSize = 64; // Actual icon size
        const canvasSize = 96; // Canvas size with padding
        
        let width = img.width;
        let height = img.height;
        
        // Calculate new dimensions maintaining aspect ratio
        if (width > height) {
          if (width > iconSize) {
            height = (height * iconSize) / width;
            width = iconSize;
          }
        } else {
          if (height > iconSize) {
            width = (width * iconSize) / height;
            height = iconSize;
          }
        }
        
        // Set canvas to full size
        canvas.width = canvasSize;
        canvas.height = canvasSize;
        const ctx = canvas.getContext('2d');
        
        // Clear with transparent background
        ctx.clearRect(0, 0, canvasSize, canvasSize);
        
        // Draw image centered with padding
        const x = (canvasSize - width) / 2;
        const y = (canvasSize - height) / 2;
        ctx.drawImage(img, x, y, width, height);
        
        // Convert to data URL
        value = canvas.toDataURL('image/png');
        activeTab = "emoji"; // Close after upload
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  function clearIcon() {
    value = "";
    if (fileInput) fileInput.value = "";
  }

  $: isImage = value && value.startsWith("data:image/");
  
  $: if (activeTab === "browse") {
    loadDashboardIcons();
  }
</script>

<div class="icon-picker">
  <div class="icon-label">Icon</div>

  <div class="tab-buttons">
    <button 
      type="button" 
      class={activeTab === "emoji" ? "active" : "secondary outline"}
      on:click={() => activeTab = "emoji"}
    >
      Emoji/Text
    </button>
    <button 
      type="button" 
      class={activeTab === "browse" ? "active" : "secondary outline"}
      on:click={() => activeTab = "browse"}
    >
      Browse Icons
    </button>
    <button 
      type="button" 
      class={activeTab === "upload" ? "active" : "secondary outline"}
      on:click={() => activeTab = "upload"}
    >
      Upload Custom
    </button>
  </div>

  {#if activeTab === "emoji"}
    <div class="tab-content">
      <input type="text" bind:value placeholder="Enter emoji or text (e.g., 🚀)" />
      {#if value && !isImage}
        <button type="button" class="secondary outline" on:click={clearIcon}>Clear</button>
      {/if}
    </div>
  {/if}

  {#if activeTab === "browse"}
    <div class="tab-content">
      <input 
        type="text" 
        bind:value={searchQuery} 
        placeholder="Search icons..." 
      />
      
      {#if loadingIcons}
        <p>Loading icons...</p>
      {:else if dashboardIcons.length === 0}
        <p>No icons loaded</p>
      {:else}
        <p class="result-count">{dashboardIcons.length} icons available. {searchQuery ? `Showing ${Math.min(50, filteredIcons.length)} of ${filteredIcons.length} matching.` : 'Use search to find icons.'}</p>
        <div class="icon-grid">
          {#each filteredIcons.slice(0, 50) as icon}
            <button
              type="button"
              class="icon-option"
              on:click={() => selectDashboardIcon(icon.url)}
              title={icon.name}
            >
              <img src={icon.url} alt={icon.name} />
              <span class="icon-name">{icon.name}</span>
            </button>
          {/each}
        </div>
        {#if filteredIcons.length === 0}
          <p>No icons match "{searchQuery}"</p>
        {/if}
      {/if}
    </div>
  {/if}

  {#if activeTab === "upload"}
    <div class="tab-content">
      <button type="button" class="secondary" on:click={() => fileInput.click()}>
        Choose File
      </button>
      <p class="help-text">Max size: 1MB. Images will be resized to 128x128px.</p>
      <input
        bind:this={fileInput}
        type="file"
        accept="image/*"
        on:change={handleFileSelect}
        style="display: none"
      />
    </div>
  {/if}

  {#if value}
    <div class="icon-preview">
      <strong>Current Icon:</strong>
      {#if isImage}
        <img src={value} alt="Icon preview" />
      {:else}
        <span class="emoji-preview">{value}</span>
      {/if}
      <button type="button" class="secondary outline" on:click={clearIcon}>Clear</button>
    </div>
  {/if}
</div>

<style>
  .icon-picker {
    margin-bottom: 1rem;
  }

  .tab-buttons {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .tab-buttons button {
    flex: 1;
    margin: 0;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

  .tab-buttons button.active {
    background: var(--pico-primary-background);
    color: var(--pico-primary-inverse);
    border-color: var(--pico-primary-background);
  }

  .tab-content {
    padding: 1rem;
    border: 1px solid var(--pico-muted-border-color);
    border-radius: 4px;
    background: var(--pico-background-color);
  }

  .tab-content input[type="text"] {
    margin-bottom: 0.5rem;
  }

  .tab-content .help-text {
    margin: 0.5rem 0 0 0;
    font-size: 0.875rem;
    color: var(--pico-muted-color);
  }

  .icon-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.5rem;
    max-height: 400px;
    overflow-y: auto;
    margin-top: 1rem;
    padding: 0.5rem;
    background: var(--pico-card-background-color);
    border-radius: 4px;
  }

  .icon-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem;
    border: 1px solid var(--pico-muted-border-color);
    border-radius: 4px;
    background: var(--pico-background-color);
    cursor: pointer;
    transition: all 0.2s;
    margin: 0;
    min-height: 90px;
  }

  .icon-option:hover {
    border-color: var(--pico-primary);
    background: var(--pico-primary-focus);
    transform: scale(1.05);
  }

  .icon-option img {
    width: 40px;
    height: 40px;
    object-fit: contain;
  }

  .icon-name {
    font-size: 0.65rem;
    text-align: center;
    word-break: break-word;
    line-height: 1.2;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .result-count {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: var(--pico-muted-color);
    text-align: center;
  }

  .icon-label {
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .icon-preview {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid var(--pico-muted-border-color);
    border-radius: 4px;
    background: var(--pico-background-color);
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .icon-preview img {
    width: 48px;
    height: 48px;
    object-fit: contain;
    border-radius: 4px;
    background: white;
    padding: 4px;
  }

  .icon-preview .emoji-preview {
    font-size: 2rem;
    line-height: 1;
  }

  .icon-preview button {
    margin-left: auto;
    margin-top: 0;
    margin-bottom: 0;
  }
</style>
