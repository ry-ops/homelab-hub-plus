<script>
  import { onMount } from "svelte";
  import { get } from "../../lib/api.js";

  export let item = {};

  let hardwareOptions = [];
  let vmOptions = [];
  let parentType = item.vm_id ? "vm" : item.hardware_id ? "hardware" : "none";

  onMount(async () => {
    try {
      const [hwRes, vmRes] = await Promise.all([get("/hardware"), get("/vms")]);
      hardwareOptions = hwRes.data;
      vmOptions = vmRes.data;
    } catch (e) {
      // ignore
    }
    if (item.vm_id) parentType = "vm";
    else if (item.hardware_id) parentType = "hardware";
  });

  $: {
    if (parentType === "none") {
      item.hardware_id = null;
      item.vm_id = null;
    } else if (parentType === "hardware") {
      item.vm_id = null;
    } else if (parentType === "vm") {
      item.hardware_id = null;
    }
  }
</script>

<div class="grid">
  <label>Name *<input type="text" bind:value={item.name} required /></label>
  <label>
    Runs on
    <select bind:value={parentType}>
      <option value="none">Standalone</option>
      <option value="hardware">Hardware (bare metal)</option>
      <option value="vm">VM</option>
    </select>
  </label>
</div>

{#if parentType === "hardware"}
  <label>
    Hardware
    <select bind:value={item.hardware_id}>
      <option value="">Select...</option>
      {#each hardwareOptions as hw}
        <option value={hw.id}>{hw.name}</option>
      {/each}
    </select>
  </label>
{:else if parentType === "vm"}
  <label>
    VM
    <select bind:value={item.vm_id}>
      <option value="">Select...</option>
      {#each vmOptions as vm}
        <option value={vm.id}>{vm.name}</option>
      {/each}
    </select>
  </label>
{/if}

<label>Description<input type="text" bind:value={item.description} /></label>
<div class="grid">
  <label>Hostname<input type="text" bind:value={item.hostname} /></label>
  <label>External Hostname<input type="text" bind:value={item.external_hostname} /></label>
</div>
<div class="grid">
  <label>Port<input type="number" bind:value={item.port} /></label>
  <label>URL<input type="url" bind:value={item.url} /></label>
</div>
<label>Notes<textarea bind:value={item.notes} rows="3"></textarea></label>
