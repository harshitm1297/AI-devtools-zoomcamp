# AI tool and data policy

## Allowed

- Synthetic purchase records.
- The currently uploaded receipt image, only for the user-requested extraction.
- Confirmed merchant/category/currency data needed to construct an embedding.
- Retrieved synthetic evidence needed to explain the deterministic result.
- Sanitized operational metadata: route, outcome, error type, duration, version, and trace ID.

## Prohibited

- Real banking credentials or account access.
- Payment-card data.
- Customer identity data.
- Receipt images in persistent storage, logs, traces, incident packets, or source control.
- Merchant names, amounts, descriptions, or prompts in telemetry.
- Using model output as a monetary calculation or autonomous financial action.

Ollama mode sends receipt images only to the configured Ollama server, which defaults to the local
machine. OpenAI Responses requests set `store: false`; provider-side retention and account policy
must still be reviewed before real personal data is used. The public demo should use synthetic
receipts only.

