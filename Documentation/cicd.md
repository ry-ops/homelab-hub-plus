# CI/CD Pipeline

homelab-hub+ ships with a GitHub Actions workflow that automatically builds and pushes multi-architecture Docker images to Docker Hub on every push to `main` and on version tags.

---

## Workflow file

`.github/workflows/docker-publish.yml`

---

## Triggers

| Event | Result |
|---|---|
| Push to `main` | Builds and pushes `:latest` |
| Push tag `v1.2.3` | Builds and pushes `:1.2.3` and `:1.2` |

---

## What it does

1. Checks out the repository
2. Sets up QEMU (for cross-compilation to ARM64)
3. Sets up Docker Buildx (multi-platform build support)
4. Logs in to Docker Hub using repository secrets
5. Computes image tags via `docker/metadata-action`
6. Builds the image for `linux/amd64` and `linux/arm64`
7. Pushes to Docker Hub
8. Uses GitHub Actions layer cache (`type=gha`) to speed up subsequent builds

---

## Required secrets

Add these in your GitHub repository under **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | A Docker Hub access token (not your password) |

### Generating a Docker Hub token

1. Log in to [hub.docker.com](https://hub.docker.com)
2. Go to **Account Settings → Security → Access Tokens**
3. Click **New Access Token**
4. Name it `homelab-hub-plus-ci`, set permissions to **Read & Write**
5. Copy the token and add it as `DOCKERHUB_TOKEN` in GitHub secrets

---

## Tagging a release

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers the workflow and produces:
- `yourusername/homelab-hub-plus:1.0.0`
- `yourusername/homelab-hub-plus:1.0`

---

## Pulling the built image

```bash
# Latest
docker pull yourusername/homelab-hub-plus:latest

# Specific version
docker pull yourusername/homelab-hub-plus:1.0.0
```

Replace your `docker-compose.yml` `build: .` with `image:` to use the pre-built image:

```yaml
app:
  image: yourusername/homelab-hub-plus:latest
  # build: .   ← remove or comment out
```

---

## Platform support

| Platform | Hardware |
|---|---|
| `linux/amd64` | Standard x86-64 servers and PCs |
| `linux/arm64` | Raspberry Pi 4/5, Apple Silicon, AWS Graviton |

---

## Build cache

The workflow uses GitHub Actions cache (`type=gha, mode=max`) to cache Docker layers between runs. This dramatically speeds up builds when only a small part of the image changes (e.g., a Python file change won't re-download all pip packages).

Cache is scoped per branch — `main` has its own cache that arm and amd64 builds share.
