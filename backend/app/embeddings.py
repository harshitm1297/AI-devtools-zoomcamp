from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence

import httpx


TOKEN_RE = re.compile(r"[a-z0-9]+")


def purchase_text(merchant: str, category: str, currency: str) -> str:
    return f"{merchant.lower()} {category.lower()} purchase paid in {currency.upper()}"


def hash_embedding(text: str, dimensions: int = 64) -> list[float]:
    """Return a deterministic local embedding suitable for the small demo corpus."""

    vector = [0.0] * dimensions
    for token in TOKEN_RE.findall(text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


class EmbeddingService:
    def __init__(self, mode: str, api_key: str | None, model: str) -> None:
        self.mode = mode
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if self.mode != "openai":
            return [hash_embedding(text) for text in texts]
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": texts, "encoding_format": "float"},
            timeout=30,
        )
        response.raise_for_status()
        data = sorted(response.json()["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in data]

