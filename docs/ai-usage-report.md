# AI-assisted development report

AI assistance was used to turn the course rubric and an earlier large-scale finance-assistant idea
into a bounded product specification, scaffold the modular application, draft tests, and review the
operational design. Human review fixed the scope at one receipt journey and required deterministic
money calculations, offline execution, evidence validation, and explicit permission boundaries.

Verification is code-driven: schema validation, unit tests, integration tests, the privacy hook,
container health checks, smoke tests, and human review. Generated code is not accepted because it
looks plausible; each behavior is tied to an acceptance criterion and executable evidence.

The app supports optional AI calls, but tests use deterministic substitutes. This separates model
availability and variability from core correctness.

The detailed, chronological evidence is in `docs/ai-development-log.md`. Changes are accepted only
after inspecting the affected source, running focused and full tests, and checking privacy and
grounding boundaries. The pull-request template records prompts, human review, rejected suggestions,
and exact verification commands so future contributions follow the same process.

