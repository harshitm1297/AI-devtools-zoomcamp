# Sanitized incident drill

Date: 2026-10-22

The allowlisted evidence collector was run against the local Guardian Angel process using the
synthetic alert in `evidence/alert-input.json`. It collected application health and version without
customer fields. Prometheus and Loki were intentionally absent from this lightweight local run, so
their evidence files record controlled `URLError` states.

Expected production behavior is documented in `incident-response/responder-task.md`: collect
evidence first, default to read-only investigation, never deploy or restart automatically, and
escalate when evidence is insufficient.

Result: operational evidence collection degraded safely and did not contain receipt images,
merchant names, amounts, prompts, credentials, or unrestricted logs.
