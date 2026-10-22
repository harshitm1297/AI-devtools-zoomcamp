# Agent extension pack

Guardian Angel includes a complete bounded extension pack:

| Element | Location | Purpose |
|---|---|---|
| Project instructions | `AGENTS.md` | Commands, boundaries, workflow, and required context |
| Reusable workflow | `agent-capabilities/evaluate-agent-change/SKILL.md` | Repeatable evaluation of agent-facing changes |
| Specialist | `agent-capabilities/privacy-reviewer.md` | Independent privacy and grounding review |
| Custom-agent manifest | `custom-agent/README.md` | Entry point and activation contract for the specialist |
| MCP server | `mcp-server/server.py` | Read-only sanitized evaluation and incident tools |
| Hook/guardrail | `agent-hooks/privacy_guard.py` | Deterministic secret/card-data source scan |
| Permission model | `docs/permissions.md` | Read, write, network, and human approval boundaries |

The pack never grants payment or banking capabilities. Model output cannot change the deterministic
risk result, and evidence citations are validated before persistence.

## Demonstration

1. Run `uv run python agent-hooks/privacy_guard.py`.
2. Run `uv run python scripts/evaluate.py`.
3. Install the optional agent dependency and run `uv run python mcp-server/server.py`.
4. Apply the evaluation workflow to a change and record the specialist findings in the PR template.
