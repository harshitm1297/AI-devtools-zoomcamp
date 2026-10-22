---
name: evaluate-guardian-agent-change
description: Evaluate changes to receipt extraction, retrieval, risk calculation, or grounded explanations.
---

# Evaluate a Guardian Angel agent change

1. Read `product-spec.md`, `docs/data-policy.md`, and the changed source.
2. Confirm monetary calculations remain deterministic and outside the model.
3. Run `pytest tests/unit -q`, then `pytest tests/integration -q`.
4. Run the cases in `data/evaluation-cases.json` and report classification accuracy.
5. Verify every cited evidence ID belongs to the retrieved set.
6. Check that logs and traces contain no merchant, amount, receipt text, or credentials.
7. Report regressions and uncertainty; never alter thresholds merely to improve the fixture score.

