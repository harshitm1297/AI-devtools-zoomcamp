from __future__ import annotations

import json
import os
import urllib.parse
from pathlib import Path
from typing import Any

import httpx


def _get_json(url: str) -> Any:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Operational evidence URL must use HTTP or HTTPS")
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {"unavailable": type(exc).__name__}


def collect(payload: dict[str, Any], incident_dir: Path) -> None:
    """Collect only allowlisted, non-customer operational evidence."""

    app_url = os.getenv("GUARDIAN_APP_URL", "http://127.0.0.1:8000")
    prometheus = os.getenv("PROMETHEUS_URL", "http://127.0.0.1:9090")
    loki = os.getenv("LOKI_URL", "http://127.0.0.1:3100")
    incident_dir.mkdir(parents=True, exist_ok=True)
    safe_alert = {
        "status": payload.get("status"),
        "alerts": [
            {
                "status": alert.get("status"),
                "labels": alert.get("labels", {}),
                "annotations": alert.get("annotations", {}),
                "startsAt": alert.get("startsAt"),
            }
            for alert in payload.get("alerts", [])[:5]
            if isinstance(alert, dict)
        ],
    }
    (incident_dir / "alert.json").write_text(json.dumps(safe_alert, indent=2), encoding="utf-8")
    (incident_dir / "health.json").write_text(
        json.dumps(_get_json(f"{app_url}/healthz"), indent=2), encoding="utf-8"
    )
    (incident_dir / "version.json").write_text(
        json.dumps(_get_json(f"{app_url}/version"), indent=2), encoding="utf-8"
    )
    query = 'sum(increase(guardian_angel_assessments_total{outcome="error"}[5m]))'
    metrics_url = f"{prometheus}/api/v1/query?{urllib.parse.urlencode({'query': query})}"
    (incident_dir / "metrics.json").write_text(
        json.dumps(_get_json(metrics_url), indent=2), encoding="utf-8"
    )
    log_query = '{service_name="guardian-angel"} |= "assessment"'
    logs_url = f"{loki}/loki/api/v1/query_range?{urllib.parse.urlencode({'query': log_query, 'limit': 100})}"
    (incident_dir / "logs.json").write_text(
        json.dumps(_get_json(logs_url), indent=2), encoding="utf-8"
    )

