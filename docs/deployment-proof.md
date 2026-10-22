# Deployment evidence checklist

Local proof collected on 2026-10-22:

- `/` returned HTTP 200 and contained the Guardian Angel frontend.
- `/healthz` returned `{"status":"ok"}`.
- `/version` reported `ai_mode=ollama` and `live_receipt_extraction=true`.
- Ollama 0.40.8 served `gemma3:4b` locally.

Public deployment proof is intentionally pending until the owner selects a repository and hosting
destination. Before submission, replace this paragraph with:

- public application URL;
- immutable image tag or commit SHA;
- successful CI and development deployment run links;
- `/healthz` and `/version` smoke-test output;
- screenshot of the deployed receipt journey; and
- rollback verification or a documented dry run.

Do not claim the cloud-deployment rubric points until those artifacts exist.
