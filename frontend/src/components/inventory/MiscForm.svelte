<script>
  export let item = {};
</script>

<div class="grid">
  <label>Name *<input type="text" bind:value={item.name} required /></label>
  <label>Category<input type="text" bind:value={item.category} /></label>
</div>
<label>Description<textarea bind:value={item.description} rows="2"></textarea></label>
<label>Notes<textarea bind:value={item.notes} rows="3"></textarea></label>
