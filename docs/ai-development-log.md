# AI-assisted development log

This log records representative human prompts and the resulting review decisions. It is not a raw
chat transcript and intentionally excludes secrets, private receipt content, and hidden reasoning.

## Scope selection

- Human request: reduce an earlier consumer-finance agent idea into a project that can reasonably be
  implemented for the course.
- AI task: propose a bounded receipt journey with multimodal extraction, local retrieval, one
  deterministic risk rule, and grounded explanation.
- Human decision: name it `guardian_angel`; exclude bank connections, payment actions, fraud claims,
  authentication, and multi-user behavior.
- Verification: acceptance criteria were written in `product-spec.md` before implementation.

## Initial implementation

- Human request: implement the whole reduced project.
- AI task decomposition: specification, FastAPI API, SQLite storage, frontend, tests, containers,
  observability, incident response, and agent extension pack.
- Context files: `AGENTS.md`, `product-spec.md`, `docs/architecture.md`, and `docs/data-policy.md`.
- Manual review: monetary classification was kept in ordinary Python; models received no capability
  to change thresholds or take financial actions.
- Verification: unit/integration tests, browser smoke test, privacy guard, and syntax checks.

## Receipt-reading correction

- Human report: receipt images were being read incorrectly.
- Finding: demo mode returned the same sample fields for arbitrary uploads.
- Rejected behavior: silently treating a real upload as the generated demo receipt.
- Accepted change: require an explicit demo marker, reject ordinary uploads in demo mode, clarify the
  UI, and strengthen final-total extraction instructions.
- Verification: regression test proves a normal upload cannot create fake demo extraction data.

## Local-model migration

- Human request: use a simple free local model instead of requiring OpenAI.
- AI task: integrate Ollama `gemma3:4b` for images and structured output while preserving local hash
  embeddings and deterministic risk calculation.
- Manual review: images default to the loopback Ollama server; schema validation and confirmation
  remain mandatory; optional hosted mode remains isolated behind configuration.
- Verification: mocked adapter contract test, live Ollama health/model response, and full test suite.

## Rubric hardening

- Human request: check all project rubrics, then take the project to full marks.
- Review findings: missing frontend tests, deployment gating, security scan evidence, consolidated
  extension documentation, and public deployment proof.
- Accepted changes: Node frontend tests, successful-CI deployment trigger, Bandit/pip-audit/Trivy,
  threat model, audit record, incident drill, issue/PR templates, and reproducible verification.
- External decisions retained for the human: repository publication, hosting destination, secrets,
  protected environments, and peer review.
