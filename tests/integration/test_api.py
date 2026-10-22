import base64
import importlib
import re
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute


PNG_1X1 = base64.b64encode(
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
).decode("ascii")


def build_app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "guardian-test.db"))
    monkeypatch.setenv("AI_MODE", "demo")
    monkeypatch.setenv("OTEL_EXPORTER_MODE", "none")
    import backend.app.main as main
    importlib.reload(main)
    main.database.initialize()
    return main


def test_complete_receipt_assessment_and_feedback_flow(monkeypatch, tmp_path) -> None:
    main = build_app(monkeypatch, tmp_path)
    extraction = main.extract_receipt(
        main.ReceiptUpload(image_data_url=f"data:image/png;base64,{PNG_1X1}", is_demo=True)
    )
    assert extraction.requires_confirmation is True

    purchase = main.confirm_receipt(
        extraction.receipt_id,
        main.ReceiptConfirmation(
            merchant=extraction.merchant,
            purchase_date=extraction.purchase_date,
            currency=extraction.currency,
            total=extraction.total,
            category=extraction.category,
        ),
    )
    assessment = main.assess_purchase(purchase.id)
    assert assessment.assessment == "unusual"
    assert len(assessment.evidence) == 5
    assert assessment.threshold_amount < purchase.amount

    feedback = main.submit_feedback(assessment.id, main.FeedbackInput(helpful=True))
    assert feedback.helpful is True


def test_rejects_unsupported_image(monkeypatch, tmp_path) -> None:
    main = build_app(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc:
        main.extract_receipt(
            main.ReceiptUpload(image_data_url="data:image/gif;base64,R0lGODlhAQABAIAAAAUEBA==")
        )
    assert exc.value.status_code == 415


def test_does_not_fake_extraction_for_uploaded_receipt_in_demo_mode(monkeypatch, tmp_path) -> None:
    main = build_app(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc:
        main.extract_receipt(
            main.ReceiptUpload(image_data_url=f"data:image/png;base64,{PNG_1X1}")
        )
    assert exc.value.status_code == 503
    assert "AI_MODE=ollama" in exc.value.detail
    assert main.database.fetchone("SELECT id FROM receipts LIMIT 1") is None


def test_confirmation_is_idempotency_guarded(monkeypatch, tmp_path) -> None:
    main = build_app(monkeypatch, tmp_path)
    extracted = main.extract_receipt(
        main.ReceiptUpload(image_data_url=f"data:image/png;base64,{PNG_1X1}", is_demo=True)
    )
    payload = main.ReceiptConfirmation(
        merchant=extracted.merchant,
        purchase_date=extracted.purchase_date,
        currency="EUR",
        total=78.4,
        category="groceries",
    )
    main.confirm_receipt(extracted.receipt_id, payload)
    with pytest.raises(HTTPException) as exc:
        main.confirm_receipt(extracted.receipt_id, payload)
    assert exc.value.status_code == 409


def test_openapi_contract_documents_every_public_api_path(monkeypatch, tmp_path) -> None:
    main = build_app(monkeypatch, tmp_path)
    contract = (Path(__file__).resolve().parents[2] / "openapi.yaml").read_text(encoding="utf-8")
    documented = set(re.findall(r"^  (/[^:]+):$", contract, flags=re.MULTILINE))
    runtime = {
        route.path
        for route in main.app.routes
        if isinstance(route, APIRoute) and route.include_in_schema
    }
    assert documented == runtime
