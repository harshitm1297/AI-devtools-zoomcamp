# Agent team and process

| Role | Responsibility | May change | Must not do |
|---|---|---|---|
| Product manager | Refine issues and acceptance criteria | Specs and tracker | Implement or approve code |
| Engineer | Implement one accepted issue | Scoped source and tests | Weaken tests or privacy rules |
| QA reviewer | Test acceptance criteria independently | Tests and review notes | Approve its own implementation |
| Privacy reviewer | Audit prompts, data flow, telemetry, citations | Findings and privacy tests | Expand data access |
| Incident responder | Diagnose one validated alert | Isolated worktree only when explicitly allowed | Commit, push, deploy, restart, or access customer data |

The product manager creates a public issue. The engineer references that issue in its work. QA and
privacy review the resulting diff independently. A human accepts the change and controls production.
Failed verification returns the issue to engineering with concrete evidence.

