import json

from backend.app.ai import AIService


class StubResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


def test_ollama_receipt_extraction_sends_image_and_schema(monkeypatch) -> None:
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return StubResponse(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "merchant": "Corner Shop",
                            "purchase_date": "2026-10-20",
                            "currency": "EUR",
                            "total": 12.5,
                            "category": "groceries",
                        }
                    )
                }
            }
        )

    monkeypatch.setattr("backend.app.ai.httpx.post", fake_post)
    service = AIService(
        "ollama",
        None,
        "unused-openai-vision",
        "unused-openai-explanation",
        "http://127.0.0.1:11434",
        "gemma3:4b",
    )

    fields = service.extract_receipt(b"fake-image-bytes", "image/png")

    assert fields.merchant == "Corner Shop"
    assert fields.total == 12.5
    assert captured["url"] == "http://127.0.0.1:11434/api/chat"
    assert captured["json"]["model"] == "gemma3:4b"
    assert captured["json"]["stream"] is False
    assert captured["json"]["options"]["temperature"] == 0
    assert captured["json"]["messages"][0]["images"]
    assert captured["json"]["format"]["required"] == [
        "merchant",
        "purchase_date",
        "currency",
        "total",
        "category",
    ]
