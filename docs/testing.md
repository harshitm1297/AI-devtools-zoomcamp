# Testing

Run the full local verification suite with `./scripts/verify.ps1`. The suite contains:

- Unit tests for threshold boundaries, insufficient history, embedding behavior, and grounding.
- Integration tests for extraction → confirmation → assessment → feedback, media validation, and
  duplicate-confirmation protection.
- Frontend unit tests for upload validation, mode messaging, and result formatting.
- Six transparent deterministic evaluation cases.

All automated tests run in deterministic demo mode and make no network calls. Before release also run:

```powershell
uv run python agent-hooks/privacy_guard.py
npm test
npm run check
uv run python scripts/evaluate.py
docker compose config
docker compose build
```

Generate the committed security reports with:

```powershell
uvx --from bandit bandit -r backend incident-response mcp-server -x tests -f json -o security/bandit-report.json
uv export --frozen --no-dev --no-emit-project --format requirements-txt --output-file security/requirements-audit.txt
uv run --with pip-audit pip-audit --requirement security/requirements-audit.txt --format json --output security/pip-audit-report.json
```

CI also runs Trivy over the repository and fails on high or critical vulnerability, secret, or
misconfiguration findings.

Manual smoke test: load the demo receipt, confirm `€78.40`, observe an unusual result with five
evidence rows, submit feedback, and verify that no image exists in `data/`.

