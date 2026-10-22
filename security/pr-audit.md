# Pre-publication audit

Date: 2026-10-22

Scope: application, frontend, agent extension pack, CI/CD definitions, telemetry, and incident
responder. This is a local audit because no pull request exists yet.

## Findings

1. **Resolved — high correctness risk:** arbitrary images in demo mode previously received fixed
   sample receipt fields. Demo extraction is now explicitly marked and normal uploads are rejected.
2. **Resolved — deployment ordering risk:** development deployment previously ran independently of
   CI. It now starts only from a successful `CI` workflow run on `main`.
3. **Resolved — test coverage gap:** frontend validation, money formatting, and mode messaging now
   have Node tests and run in CI.
4. **Accepted — model accuracy risk:** local vision output can be wrong. Structured output,
   deterministic temperature, mandatory confirmation, and bounded financial behavior limit impact.
5. **Open external prerequisite:** cloud deployment and GitHub branch protection require repository
   and hosting configuration by the project owner.
6. **Resolved — medium URL handling risk:** the incident collector used `urllib`, which could accept
   configured non-HTTP schemes. It now validates HTTP(S) and uses `httpx`.
7. **Accepted — two low subprocess findings:** the responder intentionally invokes the Codex CLI.
   Arguments are a fixed list, shell execution is disabled, workspace write requires multiple
   explicit gates, and the default mode is read-only.

Verification: backend tests, frontend tests, deterministic evaluation cases, privacy guard, Bandit,
pip-audit, JavaScript syntax checks, and a sanitized incident drill. The current Bandit report has
zero medium/high findings; pip-audit found zero known vulnerabilities across 32 locked runtime
dependencies.
