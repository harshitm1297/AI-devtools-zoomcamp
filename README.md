# Sprintlane

Sprintlane is an invite-only Kanban board for a project manager and their team.
It is being built for Homework 2 of the AI Dev Tools Zoomcamp.

## Current status

The frontend, OpenAPI contract, FastAPI backend, SQLAlchemy persistence, and
automated tests are implemented. The backend begins with SQLite and can switch
to another SQLAlchemy-supported database through configuration.

## Run the frontend prototype

```powershell
cd frontend
npm install
npm run dev
```

The frontend calls the FastAPI backend through `frontend/src/services/api.js`.
Its default API base URL is `http://localhost:8091`; set `VITE_API_BASE_URL` to
override it for another environment.

## Run the backend

```powershell
cd backend
uv sync --all-groups
uv run uvicorn app.main:app --reload --port 8091
```

The interactive API documentation is available at
`http://localhost:8091/docs`. Data is stored in `backend/sprintlane.db` by
default (and is ignored by Git). Set `DATABASE_URL` before starting the server
to use a different SQLAlchemy-compatible database. The demo login is
`maya@example.com` with password `demo-password`; it returns bearer token
`demo-token`.

Run its contract tests with:

```powershell
cd backend
uv run pytest
```

## Documentation

- [_docs/specs.md](_docs/specs.md) — product specification and scope
- [AGENTS.md](AGENTS.md) — instructions for coding agents working in this repo

## Planned structure

```text
frontend/      # interactive web client
backend/       # FastAPI service
openapi.yaml   # API contract
tests/         # automated tests
```
