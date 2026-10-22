# Privacy reviewer specialist

Use `agent-capabilities/privacy-reviewer.md` as this project's custom specialist prompt. Activate it
after any change to receipt handling, prompts, telemetry, persistence, evidence retrieval, or model
configuration. It is read-only and returns file/line findings; it must not implement its own fixes.

The specialist's permissions and prohibited actions are defined in `docs/permissions.md`.
