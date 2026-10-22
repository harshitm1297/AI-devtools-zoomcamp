from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ai import AIService
from .db import Database
from .risk import calculate_risk


class GroundingError(ValueError):
    pass


@dataclass(frozen=True)
class AgentResult:
    assessment: str
    explanation: str
    suggested_action: str
    evidence: list[dict[str, Any]]
    median_amount: float | None
    threshold_amount: float | None


class GuardianAgent:
    """A bounded read-only agent over three explicit finance-data tools."""

    def __init__(self, database: Database, ai: AIService, multiplier: float = 1.5) -> None:
        self.database = database
        self.ai = ai
        self.multiplier = multiplier

    def get_purchase(self, purchase_id: str) -> dict[str, Any] | None:
        return self.database.fetchone("SELECT * FROM purchases WHERE id = ?", (purchase_id,))

    def find_similar_purchases(self, purchase: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
        return self.database.similar_purchases(purchase, limit)

    def get_spending_statistics(self, purchase: dict[str, Any], evidence: list[dict[str, Any]]):
        return calculate_risk(float(purchase["amount"]), evidence, self.multiplier)

    def assess(self, purchase_id: str) -> AgentResult:
        purchase = self.get_purchase(purchase_id)
        if purchase is None:
            raise KeyError(purchase_id)
        evidence = self.find_similar_purchases(purchase)
        risk = self.get_spending_statistics(purchase, evidence)
        explanation = self.ai.explain(
            risk.assessment,
            float(purchase["amount"]),
            risk.median_amount,
            risk.threshold_amount,
            evidence,
        )
        allowed = {str(item["id"]) for item in evidence}
        cited = set(explanation.evidence_ids)
        if not cited.issubset(allowed):
            raise GroundingError("The explanation cited evidence that was not retrieved")
        selected = [item for item in evidence if str(item["id"]) in cited]
        return AgentResult(
            assessment=risk.assessment,
            explanation=explanation.explanation,
            suggested_action=explanation.suggested_action,
            evidence=selected,
            median_amount=risk.median_amount,
            threshold_amount=risk.threshold_amount,
        )
