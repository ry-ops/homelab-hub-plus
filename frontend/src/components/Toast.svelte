<script>
  import { toasts } from "../lib/stores.js";
</script>

{#if $toasts.length > 0}
  <div class="toast-container">
    {#each $toasts as toast (toast.id)}
      <div class="toast toast-{toast.type}">
        {toast.message}
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .toast {
    padding: 0.75rem 1.25rem;
    border-radius: 6px;
    color: #fff;
    font-size: 0.9rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.2s ease-out;
  }
  .toast-info {
    background: var(--pico-primary, #6366f1);
  }
  .toast-success {
    background: #22c55e;
  }
  .toast-error {
    background: #ef4444;
  }
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
</style>
