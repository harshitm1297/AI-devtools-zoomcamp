from __future__ import annotations

import base64
import binascii
import hashlib
import json
import time
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.trace import Status, StatusCode

from .agent import GroundingError, GuardianAgent
from .ai import AIService
from .config import Settings
from .db import Database
from .embeddings import EmbeddingService, purchase_text
from .models import (
    Assessment,
    EvidencePurchase,
    FeedbackInput,
    FeedbackResult,
    Purchase,
    ReceiptConfirmation,
    ReceiptExtraction,
    ReceiptUpload,
)
from .telemetry import configure_telemetry


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
settings = Settings.from_env()
embedding_service = EmbeddingService(settings.ai_mode, settings.openai_api_key, settings.embedding_model)
ai_service = AIService(
    settings.ai_mode,
    settings.openai_api_key,
    settings.vision_model,
    settings.explanation_model,
    settings.ollama_base_url,
    settings.ollama_model,
)
database = Database(settings.database_path, embedding_service)
agent = GuardianAgent(database, ai_service, settings.anomaly_multiplier)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.initialize()
    yield


app = FastAPI(
    title="Guardian Angel API",
    version="0.1.0",
    description="Explainable receipt-based spending-risk assessment.",
    lifespan=lifespan,
)
telemetry = configure_telemetry(app)
app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")


def _decode_image(data_url: str) -> tuple[bytes, str]:
    try:
        header, encoded = data_url.split(",", 1)
    except ValueError as exc:
        raise HTTPException(422, "Image must be a base64 data URL") from exc
    supported = {"data:image/png;base64": "image/png", "data:image/jpeg;base64": "image/jpeg"}
    media_type = supported.get(header.lower())
    if not media_type:
        raise HTTPException(415, "Only PNG and JPEG receipts are supported")
    try:
        image = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(422, "Image data is not valid base64") from exc
    if not image or len(image) > settings.max_image_bytes:
        raise HTTPException(413, "Receipt image must be between 1 byte and 5 MB")
    return image, media_type


def _public_purchase(row: dict) -> Purchase:
    return Purchase(
        id=row["id"], merchant=row["merchant"], category=row["category"],
        purchase_date=date.fromisoformat(row["purchase_date"]), currency=row["currency"],
        amount=row["amount"], source=row["source"],
    )


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/healthz", tags=["operations"])
def health() -> dict[str, str]:
    with database.connect() as db:
        db.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/version", tags=["operations"])
def version() -> dict[str, str | bool]:
    import os
    return {
        "version": os.getenv("APP_VERSION", "dev"),
        "ai_mode": settings.ai_mode,
        "live_receipt_extraction": settings.ai_mode in {"ollama", "openai"},
    }


@app.get("/api/purchases", response_model=list[Purchase], tags=["purchases"])
def list_purchases(limit: int = 20) -> list[Purchase]:
    safe_limit = min(max(limit, 1), 100)
    rows = database.fetchall(
        "SELECT * FROM purchases ORDER BY purchase_date DESC, id DESC LIMIT ?", (safe_limit,)
    )
    return [_public_purchase(row) for row in rows]


@app.post("/api/receipts/extract", response_model=ReceiptExtraction, tags=["receipts"])
def extract_receipt(upload: ReceiptUpload) -> ReceiptExtraction:
    image, media_type = _decode_image(upload.image_data_url)
    if settings.ai_mode == "demo" and not upload.is_demo:
        raise HTTPException(
            503,
            "Uploaded receipt extraction is unavailable in demo mode. "
            "Set AI_MODE=ollama for free local extraction, or use the generated demo receipt.",
        )
    with telemetry.tracer.start_as_current_span("receipt.extract") as span:
        try:
            fields = ai_service.extract_receipt(image, media_type)
            receipt_id = f"receipt-{uuid4()}"
            database.execute(
                "INSERT INTO receipts VALUES (?, ?, ?, 'pending', ?)",
                (
                    receipt_id,
                    hashlib.sha256(image).hexdigest(),
                    fields.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            telemetry.extraction_counter.add(1, {"outcome": "success", "mode": settings.ai_mode})
            telemetry.logger.info("receipt_extraction_succeeded", extra={"mode": settings.ai_mode})
            return ReceiptExtraction(receipt_id=receipt_id, mode=settings.ai_mode, **fields.model_dump())
        except HTTPException:
            raise
        except Exception as exc:
            telemetry.extraction_counter.add(1, {"outcome": "error", "mode": settings.ai_mode})
            telemetry.logger.exception("receipt_extraction_failed", extra={"error.type": type(exc).__name__})
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, "receipt extraction failed"))
            raise HTTPException(502, "Receipt extraction is temporarily unavailable") from exc


@app.post("/api/receipts/{receipt_id}/confirm", response_model=Purchase, status_code=201, tags=["receipts"])
def confirm_receipt(receipt_id: str, confirmation: ReceiptConfirmation) -> Purchase:
    receipt = database.fetchone("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
    if receipt is None:
        raise HTTPException(404, "Receipt not found")
    if receipt["status"] != "pending":
        raise HTTPException(409, "Receipt has already been confirmed")
    purchase_id = f"purchase-{uuid4()}"
    embedding = embedding_service.embed(
        purchase_text(confirmation.merchant, confirmation.category, confirmation.currency)
    )
    now = datetime.now(timezone.utc).isoformat()
    with database.connect() as db:
        db.execute(
            """INSERT INTO purchases
               (id, receipt_id, merchant, category, purchase_date, currency, amount,
                embedding_json, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'receipt', ?)""",
            (
                purchase_id, receipt_id, confirmation.merchant, confirmation.category,
                confirmation.purchase_date.isoformat(), confirmation.currency, confirmation.total,
                json.dumps(embedding), now,
            ),
        )
        db.execute("UPDATE receipts SET status = 'confirmed' WHERE id = ?", (receipt_id,))
    return Purchase(
        id=purchase_id, merchant=confirmation.merchant, purchase_date=confirmation.purchase_date,
        currency=confirmation.currency, amount=confirmation.total,
        category=confirmation.category, source="receipt",
    )


@app.post("/api/purchases/{purchase_id}/assess", response_model=Assessment, status_code=201, tags=["assessments"])
def assess_purchase(purchase_id: str) -> Assessment:
    started = time.perf_counter()
    with telemetry.tracer.start_as_current_span("purchase.assess") as span:
        try:
            result = agent.assess(purchase_id)
            assessment_id = f"assessment-{uuid4()}"
            evidence_ids = [item["id"] for item in result.evidence]
            now = datetime.now(timezone.utc).isoformat()
            if settings.ai_mode == "ollama":
                model_name = settings.ollama_model
            elif settings.ai_mode == "openai":
                model_name = settings.explanation_model
            else:
                model_name = "deterministic-demo"
            database.execute(
                "INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    assessment_id, purchase_id, result.assessment, result.explanation,
                    result.suggested_action, json.dumps(evidence_ids), result.median_amount,
                    result.threshold_amount, model_name, now,
                ),
            )
            telemetry.assessment_counter.add(1, {"outcome": "success", "assessment": result.assessment})
            telemetry.logger.info(
                "purchase_assessment_succeeded",
                extra={"assessment.outcome": result.assessment, "evidence.count": len(result.evidence)},
            )
            evidence = [
                EvidencePurchase(
                    id=item["id"], merchant=item["merchant"],
                    purchase_date=date.fromisoformat(item["purchase_date"]),
                    currency=item["currency"], amount=item["amount"], category=item["category"],
                    similarity=round(item["similarity"], 4),
                )
                for item in result.evidence
            ]
            return Assessment(
                id=assessment_id, purchase_id=purchase_id, assessment=result.assessment,
                explanation=result.explanation, suggested_action=result.suggested_action,
                evidence=evidence, median_amount=result.median_amount,
                threshold_amount=result.threshold_amount, model_name=model_name,
            )
        except KeyError as exc:
            raise HTTPException(404, "Purchase not found") from exc
        except GroundingError as exc:
            telemetry.grounding_failures.add(1, {"outcome": "rejected"})
            telemetry.assessment_counter.add(1, {"outcome": "error", "assessment": "unknown"})
            span.record_exception(exc)
            raise HTTPException(502, "The generated explanation failed grounding validation") from exc
        except HTTPException:
            raise
        except Exception as exc:
            telemetry.assessment_counter.add(1, {"outcome": "error", "assessment": "unknown"})
            telemetry.logger.exception("purchase_assessment_failed", extra={"error.type": type(exc).__name__})
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, "assessment failed"))
            raise HTTPException(502, "Assessment is temporarily unavailable") from exc
        finally:
            telemetry.assessment_duration.record(
                time.perf_counter() - started,
                {"http.route": "/api/purchases/{purchase_id}/assess"},
            )


@app.get("/api/assessments/{assessment_id}", response_model=Assessment, tags=["assessments"])
def get_assessment(assessment_id: str) -> Assessment:
    row = database.fetchone("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
    if row is None:
        raise HTTPException(404, "Assessment not found")
    evidence_rows = []
    for evidence_id in json.loads(row["evidence_ids_json"]):
        evidence = database.fetchone("SELECT * FROM purchases WHERE id = ?", (evidence_id,))
        if evidence:
            evidence_rows.append(
                EvidencePurchase(
                    id=evidence["id"], merchant=evidence["merchant"],
                    purchase_date=date.fromisoformat(evidence["purchase_date"]),
                    currency=evidence["currency"], amount=evidence["amount"],
                    category=evidence["category"], similarity=0.0,
                )
            )
    return Assessment(
        id=row["id"], purchase_id=row["purchase_id"], assessment=row["assessment"],
        explanation=row["explanation"], suggested_action=row["suggested_action"],
        evidence=evidence_rows, median_amount=row["median_amount"],
        threshold_amount=row["threshold_amount"], model_name=row["model_name"],
    )


@app.post("/api/assessments/{assessment_id}/feedback", response_model=FeedbackResult, tags=["assessments"])
def submit_feedback(assessment_id: str, feedback: FeedbackInput) -> FeedbackResult:
    if database.fetchone("SELECT id FROM assessments WHERE id = ?", (assessment_id,)) is None:
        raise HTTPException(404, "Assessment not found")
    existing = database.fetchone("SELECT id FROM feedback WHERE assessment_id = ?", (assessment_id,))
    if existing:
        database.execute(
            "UPDATE feedback SET helpful = ?, created_at = ? WHERE assessment_id = ?",
            (int(feedback.helpful), datetime.now(timezone.utc).isoformat(), assessment_id),
        )
    else:
        database.execute(
            "INSERT INTO feedback VALUES (?, ?, ?, ?)",
            (
                f"feedback-{uuid4()}", assessment_id, int(feedback.helpful),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    return FeedbackResult(assessment_id=assessment_id, helpful=feedback.helpful)
