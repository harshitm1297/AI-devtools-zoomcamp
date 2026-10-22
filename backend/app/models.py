from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


Category = Literal["groceries", "dining", "transport", "shopping", "entertainment", "other"]


class ReceiptFields(BaseModel):
    merchant: str = Field(min_length=1, max_length=100)
    purchase_date: date
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    total: float = Field(gt=0, le=100_000)
    category: Category

    @field_validator("merchant")
    @classmethod
    def normalize_merchant(cls, value: str) -> str:
        return " ".join(value.split())


class ReceiptUpload(BaseModel):
    image_data_url: str = Field(min_length=30)
    is_demo: bool = False


class ReceiptExtraction(ReceiptFields):
    receipt_id: str
    mode: Literal["demo", "ollama", "openai"]
    requires_confirmation: bool = True


class ReceiptConfirmation(ReceiptFields):
    pass


class Purchase(BaseModel):
    id: str
    merchant: str
    purchase_date: date
    currency: str
    amount: float
    category: Category
    source: Literal["seed", "receipt"]


class EvidencePurchase(BaseModel):
    id: str
    merchant: str
    purchase_date: date
    currency: str
    amount: float
    category: Category
    similarity: float


class Assessment(BaseModel):
    id: str
    purchase_id: str
    assessment: Literal["typical", "unusual", "insufficient_history"]
    explanation: str
    suggested_action: str
    evidence: list[EvidencePurchase]
    median_amount: float | None
    threshold_amount: float | None
    model_name: str


class FeedbackInput(BaseModel):
    helpful: bool


class FeedbackResult(BaseModel):
    assessment_id: str
    helpful: bool

