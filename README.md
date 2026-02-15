# HomeLab Hub

A self-hosted web application for managing and visualizing home lab infrastructure. Track hardware, virtual machines, applications, storage, networks, and more — all in one place.

## Features

- **Inventory Management** — Full CRUD for hardware, VMs, apps/services, storage, networks, and miscellaneous items
- **Network Visualization** — Interactive graph map showing relationships between infrastructure components (powered by Cytoscape.js)
- **Documentation** — Hierarchical markdown-based docs with live preview and auto-save
- **Cross-Entity Search** — Search across all inventory types from a single interface
- **Relationship Tracking** — Automatic and manual relationship mapping between entities

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Svelte 4, Vite 5, Cytoscape.js, ByteMD, Pico CSS |
| Backend | Python 3.12, Flask 3, SQLAlchemy 2, Alembic |
| Database | SQLite (default, configurable) |
| Deployment | Docker, Docker Compose, Gunicorn |

## Quick Start (Docker)

```bash
docker compose up -d --build
```

The application will be available at `http://localhost:8000`.

Data is persisted in the `./data/` directory.

## Development Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python wsgi.py
```

The API server runs on `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` with hot reload.

### Database Migrations

Migrations are managed with Alembic. From the `backend/` directory:

```bash
# Apply migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"
```

Note: The app also calls `db.create_all()` on startup as a fallback for fresh databases.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/homelab-hub.db` | SQLAlchemy database URI |
| `FLASK_ENV` | `production` | Flask environment |

## Project Structure

```
homelab-hub/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   └── routes/       # Flask API blueprints
│   ├── migrations/       # Alembic migrations
│   ├── requirements.txt
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   ├── components/   # Svelte components
│   │   ├── pages/        # Page-level components
│   │   └── lib/          # API client, stores
│   └── package.json
├── data/                 # SQLite database (gitignored)
├── Dockerfile
└── docker-compose.yml
```

## API

All endpoints are prefixed with `/api/`.

| Resource | Endpoints |
|----------|-----------|
| Health | `GET /api/health` |
| Hardware | `GET/POST /api/hardware`, `GET/PUT/DELETE /api/hardware/:id` |
| VMs | `GET/POST /api/vms`, `GET/PUT/DELETE /api/vms/:id` |
| Apps | `GET/POST /api/apps`, `GET/PUT/DELETE /api/apps/:id` |
| Storage | `GET/POST /api/storage`, `GET/PUT/DELETE /api/storage/:id` |
| Networks | `GET/POST /api/networks`, `GET/PUT/DELETE /api/networks/:id` |
| Misc | `GET/POST /api/misc`, `GET/PUT/DELETE /api/misc/:id` |
| Documents | `GET/POST /api/docs`, `GET/PUT/DELETE /api/docs/:id`, `PATCH /api/docs/:id/move` |
| Inventory | `GET /api/inventory`, `GET /api/inventory/search?q=` |
| Map | `GET /api/map/graph`, `GET/PUT /api/map/layout`, `POST/DELETE /api/map/edges` |

## License

MIT
