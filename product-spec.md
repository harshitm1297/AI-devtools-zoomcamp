# Guardian Angel product specification

## Problem

People often cannot tell whether one receipt is unusually expensive compared with similar recent
purchases. Manually searching history is slow, while generic warnings rarely show their evidence.

Guardian Angel extracts five fields from a receipt, retrieves comparable synthetic purchases,
applies one deterministic threshold, and explains the result with citations. The user confirms all
extracted data and remains responsible for every decision.

## User

A single demonstration user reviewing one personal receipt at a time.

## Primary journey

1. Upload a PNG or JPEG receipt no larger than 5 MB.
2. Review and edit merchant, date, currency, total, and category.
3. Confirm the fields.
4. Retrieve up to five similar purchases in the same currency.
5. Calculate the comparison median and 1.5× threshold in application code.
6. Generate and validate a grounded explanation.
7. Mark the explanation helpful or incorrect.

## Acceptance criteria

### Extraction and confirmation

- A supported image produces five proposed fields.
- No purchase is created until the user confirms those fields.
- An already-confirmed receipt cannot create a second purchase.
- The original image is not persisted.

### Retrieval and calculation

- Retrieval excludes the current purchase and filters to the same currency.
- No more than five evidence purchases are returned.
- With fewer than three examples, the result is `insufficient_history`.
- Otherwise, a purchase is `unusual` only when its amount is strictly greater than 1.5 times the
  median evidence amount.

### Grounding

- Every cited evidence ID must occur in the retrieved set.
- An explanation with an invented ID is rejected and not persisted.
- The model cannot change the calculated classification, median, or threshold.

### Privacy and failure behavior

- Receipt images, merchant names, amounts, extracted text, and credentials are absent from telemetry.
- Unsupported images receive a controlled 4xx response.
- Provider or grounding failures receive a controlled 502 response without a partial assessment.
- No component can move money, contact a bank, block a card, or provide investment advice.

## Non-goals

Authentication, multiple users, bank connections, CSV import, payment actions, budgets, duplicate
detection, receipt-to-bank matching, notifications, model training, multi-currency comparison, a
chat interface, and production financial recommendations.

## Success measures

- All deterministic unit and integration tests pass.
- All six synthetic evaluation cases are classified correctly.
- All stored citations refer to retrieved evidence.
- A user completes the demo journey without documentation.
- Assessment failures are visible in correlated telemetry and trigger the configured alert.

