# Agent and extension permissions

| Component | Read | Write | Network |
|---|---|---|---|
| Finance agent | One purchase and retrieved synthetic evidence | Assessment only after validation | Configured model provider |
| Privacy reviewer | Source, specs, sanitized tests | Review findings | None required |
| MCP server | Synthetic evaluation cases and incident status | Nothing | None |
| Privacy hook | Source and tests | Nothing | None |
| Incident responder | Sanitized evidence and source | Explicit isolated worktree only | Local telemetry endpoints; model through Codex CLI |

No agent may access banking systems, payment services, secrets, original receipt images, or arbitrary
filesystem paths. Production deployment and rollback always require a human-controlled workflow.

