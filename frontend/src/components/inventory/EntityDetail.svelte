<script>
  import { onMount, createEventDispatcher } from "svelte";
  import { get, post, put } from "../../lib/api.js";
  import { addToast } from "../../lib/stores.js";
  import HardwareForm from "./HardwareForm.svelte";
  import VmForm from "./VmForm.svelte";
  import AppForm from "./AppForm.svelte";
  import StorageForm from "./StorageForm.svelte";
  import NetworkForm from "./NetworkForm.svelte";
  import MiscForm from "./MiscForm.svelte";

  export let type;
  export let id = null;

  const dispatch = createEventDispatcher();

  let item = {};
  let loading = !!id;

  const FORMS = {
    hardware: HardwareForm,
    vms: VmForm,
    apps: AppForm,
    storage: StorageForm,
    networks: NetworkForm,
    misc: MiscForm,
  };

  $: FormComponent = FORMS[type];

  onMount(async () => {
    if (id) {
      try {
        const res = await get(`/${type}/${id}`);
        item = res.data;
      } catch (e) {
        addToast(e.message, "error");
      }
      loading = false;
    }
  });

  async function handleSubmit() {
    try {
      if (id) {
        await put(`/${type}/${id}`, item);
        addToast("Updated", "success");
      } else {
        await post(`/${type}`, item);
        addToast("Created", "success");
      }
      dispatch("saved");
    } catch (e) {
      addToast(e.message, "error");
    }
  }
</script>

{#if loading}
  <p aria-busy="true">Loading...</p>
{:else}
  <form on:submit|preventDefault={handleSubmit}>
    <h3>{id ? "Edit" : "New"} {type.charAt(0).toUpperCase() + type.slice(1).replace(/s$/, "")}</h3>

    <svelte:component this={FormComponent} bind:item />

    <div class="form-actions">
      <button type="submit">{id ? "Save" : "Create"}</button>
      <button type="button" class="outline secondary" on:click={() => {
        dispatch("cancel");
        if (id) history.back();
      }}>
        Cancel
      </button>
    </div>
  </form>
{/if}

<style>
  .form-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  form {
    max-width: 700px;
  }
</style>
