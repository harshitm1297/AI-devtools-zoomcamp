# guardian_angel

## Problem

People often cannot tell whether one receipt is unusually expensive compared with similar recent
purchases. Searching transaction history manually is slow, while generic spending warnings rarely
show their evidence. Guardian Angel turns one receipt into a reviewable, evidence-backed comparison
without connecting to a bank or taking any financial action.

Guardian Angel is an explainable, multimodal spending-risk assistant. A user uploads a receipt,
confirms five extracted fields, and receives an evidence-backed comparison with similar synthetic
purchases. Deterministic code decides whether the amount is unusual; an AI model may extract and
explain, but cannot change the calculation or perform a financial action.

> Educational prototype. It is not financial advice, fraud detection, or a banking product.

## What works

- Single-page responsive receipt journey
- PNG/JPEG receipt extraction with mandatory confirmation
- Offline deterministic demo mode with a generated sample receipt and 75 synthetic purchases
- Free local vision and explanation calls through Ollama
- Deterministic local embeddings for Ollama/demo mode, with optional OpenAI support
- Read-only agent tools, evidence-ID grounding validation, and stored feedback
- SQLite persistence without retaining receipt images
- Unit and integration tests
- Dependency, source, secret, and configuration security scans
- Docker Compose application and Grafana observability stack
- User-impact alert and policy-constrained engineering responder
- Project instructions, reusable workflow, specialist, MCP server, hook, and permission notes

## Quick start

Requirements: Python 3.11+ and `uv`.

```powershell
uv sync
$env:AI_MODE = "demo"
uv run uvicorn backend.app.main:app --reload
```

Open <http://127.0.0.1:8000> and select **Use demo receipt**. API documentation is available at
<http://127.0.0.1:8000/docs>.

Run all tests:

```powershell
./scripts/verify.ps1
```

The verification script runs backend tests, frontend tests, six deterministic evaluation cases,
the privacy guard, syntax checks, and Docker validation when Docker is available. Individual
commands are documented in [docs/testing.md](docs/testing.md).

Run the full local application and telemetry stack:

```powershell
docker compose up --build -d --wait
```

- Application: <http://127.0.0.1:8000>
- Grafana: <http://127.0.0.1:3000> (`admin` / `admin` locally)
- Prometheus: <http://127.0.0.1:9090>

Stop without deleting the database:

```powershell
docker compose down
```

Add `-v` only when you intentionally want to delete all persisted local data.

## Free local receipt reading (recommended)

Demo mode is the default and needs no external service. It intentionally extracts only the generated
sample receipt; uploaded images are rejected instead of being assigned fake sample values. To read
real uploaded receipts locally, install [Ollama](https://ollama.com/download), then run:

```powershell
ollama pull gemma3:4b
$env:AI_MODE = "ollama"
uv run uvicorn backend.app.main:app --reload
```

The initial model download is approximately 3.4 GB. Receipt images and prompts are sent only to the
local Ollama server at `http://127.0.0.1:11434`; no API key is needed. Override these settings when
needed:

```text
OLLAMA_BASE_URL
OLLAMA_MODEL
```

For Docker Compose, start Ollama on the host, pull the model, and set `AI_MODE=ollama`. The app
container reaches it through `http://host.docker.internal:11434`.

## Optional OpenAI mode

The original hosted provider remains available as an opt-in alternative:

```powershell
$env:AI_MODE = "openai"
$env:OPENAI_API_KEY = "your-key-in-the-shell-only"
uv run uvicorn backend.app.main:app
```

Model identifiers are configuration, not hard-coded policy:

```text
OPENAI_VISION_MODEL
OPENAI_EXPLANATION_MODEL
OPENAI_EMBEDDING_MODEL
```

In `ollama` mode, images stay on the machine running Ollama. In `openai` mode, the application sends
the image to that provider and sets `store: false` on Responses API calls. Never put keys in `.env`
files committed to the repository.

## Architecture

```text
Browser → FastAPI → SQLite
             ├─ extraction service
             ├─ retrieval + deterministic risk rule
             └─ bounded explanation agent

FastAPI → OpenTelemetry Collector → Prometheus / Loki / Tempo → Grafana alert
                                                                  ↓
                                                        engineering responder
```

The only risk rule is visible and testable:

```text
unusual when receipt total > 1.5 × median of five retrieved purchases
```

See [product-spec.md](product-spec.md), [architecture](docs/architecture.md), and the
[data policy](docs/data-policy.md) for the complete contract.

## AI-assisted development and review

The implementation was developed with an AI coding agent under the boundaries in `AGENTS.md`.
Representative prompts, decisions, rejected behavior, manual review, and executable verification
are recorded in [docs/ai-development-log.md](docs/ai-development-log.md). Pull requests use a
template that preserves the linked issue, AI contribution, human review, and test evidence.

## Deployment status

Container and CI/CD definitions are ready, but a public deployment URL requires repository and
hosting configuration by the project owner. Development deployment is triggered only after a
successful CI run; production deployment is manual and intended for a protected environment. See
[docs/deployment.md](docs/deployment.md) and [docs/deployment-proof.md](docs/deployment-proof.md).

## Repository map

```text
backend/               application, retrieval, risk rule, and agent
frontend/              single-page interface
tests/                 unit and integration tests
observability/         collector, stores, dashboard, and alert
incident-response/     evidence collector and bounded responder
security/              threat model, scan reports, and audit findings
ops/                   sanitized operational drill evidence
agent-capabilities/    reusable workflow and specialist
agent-hooks/           deterministic privacy guard
custom-agent/          specialist entry point
mcp-server/            read-only tools for sanitized evidence
docs/                  architecture, testing, deployment, permissions, evaluation
```

## Project evidence

The public task tracker should be created as GitHub Issues or a GitHub Project when this folder is
published to its own repository. Use the issue template in `docs/task-tracker.md`, link every change
to an issue, and preserve agent prompts/reviews in pull-request descriptions. Deployment workflows
are present but require repository environment URLs and deploy-hook secrets described in
`docs/deployment.md`.

