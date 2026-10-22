from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException

from collect_evidence import collect


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
INCIDENTS = HERE / "incidents"
RUN_LOCK = Lock()
app = FastAPI(title="Guardian Angel incident responder")


def _incident_id() -> str:
    return datetime.now(timezone.utc).strftime("INC-%Y%m%dT%H%M%S%fZ")


def _save_status(directory: Path, state: str, **extra: Any) -> None:
    (directory / "status.json").write_text(
        json.dumps({"incident_id": directory.name, "state": state, **extra}, indent=2),
        encoding="utf-8",
    )


def _primary_alert(payload: dict[str, Any]) -> dict[str, Any]:
    alerts = payload.get("alerts")
    if not isinstance(alerts, list) or not alerts or not isinstance(alerts[0], dict):
        raise HTTPException(422, "Payload must contain at least one alert")
    return alerts[0]


def _workspace_write_allowed(alert: dict[str, Any]) -> bool:
    labels = alert.get("labels") or {}
    worktree = Path(os.getenv("RESPONDER_WORKTREE", ""))
    return (
        os.getenv("RESPONDER_ALLOW_WORKSPACE_WRITE", "false").lower() == "true"
        and alert.get("status") == "firing"
        and labels.get("alertname") == "GuardianAngelAssessmentFailures"
        and labels.get("allow_fix") == "true"
        and worktree.is_dir()
        and worktree.resolve() != REPO_ROOT.resolve()
    )


def _run(payload: dict[str, Any], directory: Path, alert: dict[str, Any]) -> None:
    with RUN_LOCK:
        try:
            _save_status(directory, "collecting_evidence")
            collect(payload, directory)
            codex = os.getenv("CODEX_COMMAND") or shutil.which("codex")
            if not codex:
                _save_status(directory, "evidence_ready", note="Codex CLI was not available; escalate to a human.")
                return
            allow_write = _workspace_write_allowed(alert)
            workspace = Path(os.getenv("RESPONDER_WORKTREE")) if allow_write else REPO_ROOT
            prompt = (HERE / "responder-task.md").read_text(encoding="utf-8").format(
                incident_id=directory.name,
                incident_dir=directory,
                permission=(
                    "You may edit only this isolated worktree and run tests. Do not commit, push, or deploy."
                    if allow_write else
                    "Read-only investigation. Do not modify files or deployed systems."
                ),
            )
            response_path = directory / "response.json"
            command = [
                codex, "exec", "--ephemeral", "--sandbox",
                "workspace-write" if allow_write else "read-only",
                "--output-schema", str(HERE / "response.schema.json"),
                "--output-last-message", str(response_path),
                "-C", str(workspace), prompt,
            ]
            _save_status(directory, "agent_running", access="workspace-write" if allow_write else "read-only")
            completed = subprocess.run(
                command, cwd=workspace, capture_output=True, text=True,
                timeout=int(os.getenv("RESPONDER_TIMEOUT_SECONDS", "600")), check=False,
            )
            if completed.returncode != 0:
                _save_status(directory, "failed", error=f"Agent exited with {completed.returncode}")
                return
            _save_status(directory, "completed", response=json.loads(response_path.read_text(encoding="utf-8")))
        except Exception as exc:
            _save_status(directory, "failed", error=f"{type(exc).__name__}: {exc}")


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/alerts", status_code=202)
def alert(payload: dict[str, Any], tasks: BackgroundTasks) -> dict[str, str]:
    primary = _primary_alert(payload)
    directory = INCIDENTS / _incident_id()
    directory.mkdir(parents=True)
    _save_status(directory, "accepted")
    tasks.add_task(_run, payload, directory, primary)
    return {"incident_id": directory.name, "status": "accepted"}


@app.get("/incidents/{incident_id}")
def status(incident_id: str) -> dict[str, Any]:
    if not incident_id.startswith("INC-") or not incident_id.replace("-", "").isalnum():
        raise HTTPException(400, "Invalid incident ID")
    target = INCIDENTS / incident_id / "status.json"
    if not target.is_file():
        raise HTTPException(404, "Incident not found")
    return json.loads(target.read_text(encoding="utf-8"))

