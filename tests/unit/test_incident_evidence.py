from __future__ import annotations

import sys
from pathlib import Path


INCIDENT_RESPONSE = Path(__file__).resolve().parents[2] / "incident-response"
sys.path.insert(0, str(INCIDENT_RESPONSE))

from collect_evidence import _get_json  # noqa: E402


def test_evidence_collector_rejects_non_http_urls(monkeypatch) -> None:
    called = False

    def unexpected_get(*_args, **_kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr("collect_evidence.httpx.get", unexpected_get)

    assert _get_json("file:///private/data") == {"unavailable": "ValueError"}
    assert called is False
