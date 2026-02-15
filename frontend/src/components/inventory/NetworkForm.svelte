<script>
  export let item = {};
</script>

<div class="grid">
  <label>Name *<input type="text" bind:value={item.name} required /></label>
  <label>VLAN ID<input type="number" bind:value={item.vlan_id} /></label>
</div>
<div class="grid">
  <label>Subnet<input type="text" bind:value={item.subnet} placeholder="192.168.1.0/24" /></label>
  <label>Gateway<input type="text" bind:value={item.gateway} placeholder="192.168.1.1" /></label>
</div>
<label>DNS Servers<input type="text" bind:value={item.dns_servers} placeholder="1.1.1.1, 8.8.8.8" /></label>
<label>Notes<textarea bind:value={item.notes} rows="3"></textarea></label>
