<script>
  import { onMount, onDestroy } from "svelte";

  export let content = "";
  export let onChange = () => {};

  let editorEl;
  let previewEl;
  let mode = "split"; // "edit", "preview", "split"
  let localContent = content;

  // Update local content when prop changes (doc switch)
  $: localContent = content;

  function handleInput(e) {
    localContent = e.target.value;
    onChange(localContent);
  }

  // Simple markdown-to-HTML renderer for preview
  function renderMarkdown(md) {
    if (!md) return "<p></p>";
    let html = md
      // Code blocks
      .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
      // Inline code
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      // Headers
      .replace(/^#### (.+)$/gm, "<h4>$1</h4>")
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      // Bold & italic
      .replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
      // Unordered lists
      .replace(/^[-*] (.+)$/gm, "<li>$1</li>")
      // Blockquotes
      .replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>")
      // Horizontal rules
      .replace(/^---$/gm, "<hr>")
      // Line breaks / paragraphs
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br>");
    return `<p>${html}</p>`;
  }
</script>

<div class="editor-container">
  <div class="editor-toolbar">
    <button class:active={mode === "edit"} on:click={() => (mode = "edit")}>Edit</button>
    <button class:active={mode === "split"} on:click={() => (mode = "split")}>Split</button>
    <button class:active={mode === "preview"} on:click={() => (mode = "preview")}>Preview</button>
  </div>

  <div class="editor-panels" class:split={mode === "split"}>
    {#if mode !== "preview"}
      <textarea
        class="editor-textarea"
        bind:this={editorEl}
        value={localContent}
        on:input={handleInput}
        placeholder="Write markdown here..."
        spellcheck="false"
      ></textarea>
    {/if}
    {#if mode !== "edit"}
      <div class="editor-preview" bind:this={previewEl}>
        {@html renderMarkdown(localContent)}
      </div>
    {/if}
  </div>
</div>

<style>
  .editor-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }
  .editor-toolbar {
    display: flex;
    gap: 0;
    padding: 0.25rem 0.5rem;
    border-bottom: 1px solid var(--pico-muted-border-color, #333);
  }
  .editor-toolbar button {
    padding: 0.25rem 0.75rem;
    font-size: 0.8rem;
    margin: 0;
    background: none;
    border: 1px solid var(--pico-muted-border-color, #333);
    color: var(--pico-muted-color, #999);
    cursor: pointer;
  }
  .editor-toolbar button.active {
    background: var(--pico-primary-background, rgba(99, 102, 241, 0.15));
    color: var(--pico-primary, #6366f1);
  }
  .editor-panels {
    flex: 1;
    display: flex;
    overflow: hidden;
  }
  .editor-panels.split {
    gap: 1px;
  }
  .editor-textarea {
    flex: 1;
    resize: none;
    border: none;
    border-radius: 0;
    padding: 1rem;
    font-family: monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
  }
  .editor-preview {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    border-left: 1px solid var(--pico-muted-border-color, #333);
  }
  .editor-preview :global(pre) {
    background: var(--pico-card-background-color, #1e1e2e);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
  }
  .editor-preview :global(code) {
    font-size: 0.85rem;
  }
</style>
