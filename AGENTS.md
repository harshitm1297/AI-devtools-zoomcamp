# Guardian Angel agent instructions

## Read first

Read `product-spec.md`, `docs/architecture.md`, and `docs/data-policy.md` before changing behavior.
For operational work also read `docs/permissions.md` and the relevant incident evidence.

## Commands

```powershell
uv sync
uv run pytest -q
uv run python agent-hooks/privacy_guard.py
uv run uvicorn backend.app.main:app --reload
docker compose up --build -d --wait
```

## Architectural boundaries

- Monetary calculations belong in `backend/app/risk.py`, never in prompts.
- Model and provider calls belong in `backend/app/ai.py`.
- Agent tools are read-only and orchestrated in `backend/app/agent.py`.
- Database access belongs in `backend/app/db.py`.
- The frontend calls the API only from `frontend/app.js`.
- Never persist uploaded image bytes.
- Never attach receipt, merchant, amount, description, prompt, or credentials to telemetry.
- Evidence IDs must be validated as a subset of retrieval results before persistence.

## Workflow

1. Work from one tracked issue with explicit acceptance criteria.
2. Make the smallest cohesive change.
3. Add or update a failing test first for behavior changes.
4. Run focused tests, the full suite, and the privacy guard.
5. Request independent QA/privacy review.
6. Do not commit, push, deploy, or change secrets without direct human authorization.

## Modular context

- Agent roles: `docs/agent-team.md`
- Testing: `docs/testing.md`
- Deployment and rollback: `docs/deployment.md`, `docs/release-process.md`
- AI use and verification: `docs/ai-usage-report.md`
- Permissions: `docs/permissions.md`
- Evaluation: `docs/evaluation.md`

