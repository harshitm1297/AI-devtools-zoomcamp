# Threat model

## Assets and trust boundaries

- Assets: receipt image in memory, confirmed purchase fields, assessments, feedback, and model
  configuration.
- Untrusted boundaries: browser input, model output, alert payloads, and deployment hooks.
- Explicitly excluded assets: bank credentials, card data, bank connectivity, and payment authority.

## Threats and controls

| Threat | Control | Verification |
|---|---|---|
| Oversized or unsupported image | MIME allowlist, base64 validation, 5 MB limit | Integration tests |
| Model invents fields or citations | Pydantic schemas, human confirmation, evidence-ID subset check | Unit/integration tests |
| Receipt persisted accidentally | Store SHA-256 and extracted fields only | Privacy guard and DB review |
| Sensitive telemetry | Bounded allowlisted attributes only | Privacy guard and manual review |
| Prompt injection in receipt/alert | Model has no money-moving tools; incident evidence is treated as data | Architecture and permissions |
| Dependency or source vulnerability | pip-audit, Bandit, and Trivy in CI | Saved reports and workflow |
| Unreviewed production change | CI-gated development deploy and manual protected production workflow | Workflow review |

Residual risk: local vision extraction can be inaccurate. Every proposed field therefore requires
human confirmation, and the product is explicitly not fraud detection or financial advice.
