from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP


ROOT = Path(__file__).resolve().parents[1]
mcp = FastMCP("guardian-angel-readonly")


@mcp.tool()
def list_evaluation_cases() -> list[dict[str, object]]:
    """List sanitized synthetic evaluation cases. No customer data is exposed."""
    return json.loads((ROOT / "data" / "evaluation-cases.json").read_text(encoding="utf-8"))


@mcp.tool()
def read_incident_status(incident_id: str) -> dict[str, object]:
    """Read the status summary of one local incident; raw logs are not exposed."""
    if not incident_id.startswith("INC-") or not incident_id.replace("-", "").isalnum():
        raise ValueError("Invalid incident ID")
    target = ROOT / "incident-response" / "incidents" / incident_id / "status.json"
    if not target.is_file():
        raise FileNotFoundError("Incident not found")
    return json.loads(target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    mcp.run()

