<script>
  const dashboards = [
    {
      name: "ArgoCD",
      url: "https://argocd.ry-ops.dev",
      description: "GitOps continuous delivery for Kubernetes",
      icon: "argocd",
    },
    {
      name: "Grafana",
      url: "https://grafana.ry-ops.dev",
      description: "Observability and monitoring dashboards",
      icon: "grafana",
    },
    {
      name: "Prometheus",
      url: "https://prometheus.ry-ops.dev",
      description: "Metrics collection and alerting",
      icon: "prometheus",
    },
    {
      name: "Longhorn",
      url: "https://longhorn.ry-ops.dev",
      description: "Distributed block storage for Kubernetes",
      icon: "longhorn",
    },
    {
      name: "Sandfly",
      url: "https://sandfly.ry-ops.dev",
      description: "Linux security and intrusion detection",
      icon: "sandfly",
    },
    {
      name: "Fabric Dashboard",
      url: "https://fabric.ry-ops.dev",
      description: "Fabric SDK service overview",
      icon: "fabric",
    },
  ];
</script>

<div class="dashboards-page">
  <h2>Dashboards</h2>
  <div class="grid">
    {#each dashboards as d}
      <a href={d.url} target="_blank" rel="noopener noreferrer" class="card">
        <div class="card-header">
          <span class="card-title">{d.name}</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        </div>
        <p class="card-desc">{d.description}</p>
        {#if d.note}
          <span class="card-note">{d.note}</span>
        {/if}
      </a>
    {/each}
  </div>
</div>

<style>
  .dashboards-page {
    padding: 1.5rem;
    max-width: 900px;
  }

  h2 {
    margin: 0 0 1.5rem;
    font-size: 1.4rem;
    font-weight: 600;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
  }

  .card {
    display: block;
    padding: 1.2rem;
    background: var(--pico-card-background-color, #1a1a2e);
    border: 1px solid var(--pico-muted-border-color, #333);
    border-radius: 8px;
    text-decoration: none;
    color: inherit;
    transition: border-color 0.2s, transform 0.15s;
  }

  .card:hover {
    border-color: var(--pico-primary, #6366f1);
    transform: translateY(-2px);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--pico-color, #fff);
  }

  .card-header svg {
    color: var(--pico-muted-color, #aaa);
    flex-shrink: 0;
  }

  .card-desc {
    margin: 0;
    font-size: 0.85rem;
    color: var(--pico-muted-color, #aaa);
    line-height: 1.4;
  }

  .card-note {
    display: inline-block;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: var(--pico-muted-color, #888);
    background: var(--pico-background-color, #111);
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
  }
</style>
