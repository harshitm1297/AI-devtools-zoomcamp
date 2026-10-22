from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from .models import ReceiptFields


def _output_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]
    raise ValueError("Model response did not contain output text")


@dataclass(frozen=True)
class Explanation:
    explanation: str
    suggested_action: str
    evidence_ids: list[str]


class AIService:
    def __init__(
        self,
        mode: str,
        api_key: str | None,
        vision_model: str,
        explanation_model: str,
        ollama_base_url: str = "http://127.0.0.1:11434",
        ollama_model: str = "gemma3:4b",
    ) -> None:
        self.mode = mode
        self.api_key = api_key
        self.vision_model = vision_model
        self.explanation_model = explanation_model
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model

    def extract_receipt(self, image_bytes: bytes, media_type: str) -> ReceiptFields:
        if self.mode == "demo":
            return ReceiptFields(
                merchant="Northstar Market",
                purchase_date=date(2026, 4, 12),
                currency="EUR",
                total=78.40,
                category="groceries",
            )
        schema = ReceiptFields.model_json_schema()
        prompt = (
            "Read the visible receipt carefully and extract exactly five fields. "
            "Use the merchant name printed in the receipt header; the transaction "
            "date (not a card-expiry date); the three-letter ISO-4217 currency; and "
            "the final amount actually paid. For total, prefer labels such as TOTAL, "
            "GRAND TOTAL, AMOUNT DUE, or CARD PAYMENT, and do not use subtotal, tax, "
            "tip, change, savings, or an individual line item. Categorize the merchant "
            "as groceries, dining, transport, shopping, entertainment, or other. "
            "Do not include card numbers, customer data, or facts not visible in the image."
        )
        if self.mode == "ollama":
            content = self._ollama_chat(
                prompt=f"{prompt}\nReturn JSON matching this schema: {json.dumps(schema)}",
                schema=schema,
                image_bytes=image_bytes,
            )
            return ReceiptFields.model_validate_json(content)

        image_url = f"data:{media_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        payload = self._response(
            model=self.vision_model,
            input_value=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                        {"type": "input_image", "image_url": image_url, "detail": "high"},
                    ],
                }
            ],
            schema_name="receipt_fields",
            schema=schema,
        )
        return ReceiptFields.model_validate_json(_output_text(payload))

    def explain(
        self,
        assessment: str,
        amount: float,
        median_amount: float | None,
        threshold_amount: float | None,
        evidence: list[dict[str, Any]],
    ) -> Explanation:
        evidence_ids = [str(item["id"]) for item in evidence]
        if self.mode == "demo":
            if assessment == "insufficient_history":
                explanation = "There are not yet enough comparable purchases for a reliable assessment."
                action = "Review the receipt manually and add more history before relying on this signal."
            elif assessment == "unusual":
                percent = round(((amount / float(median_amount)) - 1) * 100)
                explanation = f"This purchase is {percent}% above the €{median_amount:.2f} median of the retrieved examples."
                action = "Check the receipt and confirm whether the higher total was expected."
            else:
                explanation = f"This purchase is within the expected range; the comparison median is €{median_amount:.2f}."
                action = "No action is needed unless you do not recognize the purchase."
            return Explanation(explanation, action, evidence_ids)

        schema = {
            "type": "object",
            "properties": {
                "explanation": {"type": "string"},
                "suggested_action": {"type": "string"},
                "evidence_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["explanation", "suggested_action", "evidence_ids"],
            "additionalProperties": False,
        }
        compact_evidence = [
            {"id": item["id"], "amount": item["amount"], "category": item["category"]}
            for item in evidence
        ]
        prompt = {
            "assessment": assessment,
            "amount": amount,
            "median_amount": median_amount,
            "threshold_amount": threshold_amount,
            "retrieved_evidence": compact_evidence,
            "instruction": (
                "Explain this deterministic assessment in two short sentences. Cite only IDs from "
                "retrieved_evidence. Do not give financial advice or claim fraud."
            ),
        }
        if self.mode == "ollama":
            value = json.loads(
                self._ollama_chat(
                    prompt=f"{json.dumps(prompt)}\nReturn JSON matching this schema: {json.dumps(schema)}",
                    schema=schema,
                )
            )
            return Explanation(
                explanation=value["explanation"],
                suggested_action=value["suggested_action"],
                evidence_ids=value["evidence_ids"],
            )
        payload = self._response(
            model=self.explanation_model,
            input_value=json.dumps(prompt),
            schema_name="spending_explanation",
            schema=schema,
        )
        value = json.loads(_output_text(payload))
        return Explanation(
            explanation=value["explanation"],
            suggested_action=value["suggested_action"],
            evidence_ids=value["evidence_ids"],
        )

    def _ollama_chat(
        self,
        prompt: str,
        schema: dict[str, Any],
        image_bytes: bytes | None = None,
    ) -> str:
        message: dict[str, Any] = {"role": "user", "content": prompt}
        if image_bytes is not None:
            message["images"] = [base64.b64encode(image_bytes).decode("ascii")]
        response = httpx.post(
            f"{self.ollama_base_url}/api/chat",
            json={
                "model": self.ollama_model,
                "messages": [message],
                "format": schema,
                "options": {"temperature": 0},
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        content = response.json().get("message", {}).get("content")
        if not isinstance(content, str):
            raise ValueError("Ollama response did not contain message content")
        return content

    def _response(self, model: str, input_value: Any, schema_name: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model,
                "input": input_value,
                "store": False,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": schema,
                    }
                },
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

