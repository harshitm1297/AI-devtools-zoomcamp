from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Any, Literal


@dataclass(frozen=True)
class RiskResult:
    assessment: Literal["typical", "unusual", "insufficient_history"]
    median_amount: float | None
    threshold_amount: float | None


def calculate_risk(amount: float, evidence: list[dict[str, Any]], multiplier: float = 1.5) -> RiskResult:
    if len(evidence) < 3:
        return RiskResult("insufficient_history", None, None)
    baseline = round(float(median(float(item["amount"]) for item in evidence)), 2)
    threshold = round(baseline * multiplier, 2)
    return RiskResult("unusual" if amount > threshold else "typical", baseline, threshold)

