from backend.app.risk import calculate_risk


def evidence(*amounts: float) -> list[dict[str, float]]:
    return [{"amount": amount} for amount in amounts]


def test_amount_above_one_and_a_half_times_median_is_unusual() -> None:
    result = calculate_risk(50.0, evidence(28.0, 30.0, 32.0), multiplier=1.5)
    assert result.assessment == "unusual"
    assert result.median_amount == 30.0
    assert result.threshold_amount == 45.0


def test_amount_at_threshold_is_typical() -> None:
    result = calculate_risk(45.0, evidence(28.0, 30.0, 32.0), multiplier=1.5)
    assert result.assessment == "typical"


def test_less_than_three_examples_is_insufficient() -> None:
    result = calculate_risk(100.0, evidence(10.0, 20.0))
    assert result.assessment == "insufficient_history"
    assert result.median_amount is None

