# Sprintlane Agent Instructions

## Source of truth

- Read `_docs/specs.md` before making product decisions.
- Keep `openapi.yaml` as the explicit contract between `frontend/` and
  `backend/` once it exists.
- Preserve the stated non-goals unless the user explicitly changes the scope.

## Project conventions

- Keep frontend code in `frontend/` and backend code in `backend/`.
- Use npm for frontend dependencies and scripts.
- Use `uv` for backend dependency management; do not use `pip install` directly.
- Use FastAPI and SQLAlchemy for the backend.
- Keep database configuration environment-driven and avoid SQLite-specific
  application logic.
- Centralize frontend API calls in one service/client layer; mock that layer
  before a real backend is connected.

## Quality checks

- Add or update tests with each behavior change.
- Run relevant frontend and backend tests before declaring work complete.
- Do not commit secrets, virtual environments, `node_modules`, generated
  database files, or local environment files.
- Update the README when setup, run, or test commands change.
