# Architecture

Guardian Angel is a deliberately small modular monolith. FastAPI serves both the static frontend
and JSON API, while SQLite stores confirmed fields, embeddings, assessments, and feedback.

## Request flow

```text
image data URL
  → size/type validation
  → demo or vision extraction
  → pending receipt metadata (image hash, not image)
  → human confirmation
  → purchase + embedding
  → same-currency similarity retrieval
  → deterministic median/threshold
  → grounded explanation
  → assessment + optional feedback
```

The default hash embedding makes the project reproducible. Ollama mode performs receipt extraction
and explanation locally while retaining those deterministic embeddings. Optional OpenAI mode
replaces extraction, embeddings, and explanation through narrow provider interfaces. Neither mode
can replace the threshold calculation.

## Trust boundaries

- Browser input is untrusted and validated by Pydantic and explicit image checks.
- Provider output is untrusted and validated against schemas.
- Model citations are untrusted until checked against retrieved IDs.
- Incident evidence is untrusted data, not agent instructions.
- Deployment and production remediation remain human-controlled.

## Storage

SQLite is appropriate for this single-user prototype. Connections are short-lived, foreign keys are
enabled, and original image bytes are discarded after extraction. A production multi-user version
would need identity, object-storage lifecycle controls, encryption, migrations, and a server database.

