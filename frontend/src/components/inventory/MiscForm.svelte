<script>
  import IconPicker from "./IconPicker.svelte";

  export let item = {};
</script>

<div class="grid">
  <label>Name *<input type="text" bind:value={item.name} required /></label>
  <label>Category<input type="text" bind:value={item.category} /></label>
</div>
<div class="grid">
  <label>Hostname<input type="text" bind:value={item.hostname} /></label>
  <label>IP Address<input type="text" bind:value={item.ip_address} /></label>
</div>
<label>Description<textarea bind:value={item.description} rows="2"></textarea></label>
<IconPicker bind:value={item.icon} />
<label>Notes<textarea bind:value={item.notes} rows="3"></textarea></label>
