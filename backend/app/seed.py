from __future__ import annotations

from datetime import date, timedelta


MERCHANTS = {
    "groceries": [("Northstar Market", 36.0), ("Green Basket", 28.0), ("Daily Foods", 42.0)],
    "dining": [("Cedar Cafe", 17.0), ("Noodle House", 24.0), ("Harbor Kitchen", 31.0)],
    "transport": [("City Transit", 8.0), ("QuickCab", 19.0), ("Rail Europe", 34.0)],
    "shopping": [("Corner Goods", 45.0), ("Studio Supply", 62.0), ("Everyday Store", 29.0)],
    "entertainment": [("Cinema Square", 15.0), ("Sound Hall", 39.0), ("Game Corner", 26.0)],
}


def synthetic_purchases() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = date(2026, 1, 5)
    counter = 1
    for category, merchants in MERCHANTS.items():
        for merchant_index, (merchant, baseline) in enumerate(merchants):
            for occurrence in range(5):
                variation = ((occurrence % 3) - 1) * 0.08
                rows.append(
                    {
                        "id": f"seed-{counter:03d}",
                        "merchant": merchant,
                        "category": category,
                        "purchase_date": (start + timedelta(days=counter * 3 + merchant_index)).isoformat(),
                        "currency": "EUR",
                        "amount": round(baseline * (1 + variation), 2),
                    }
                )
                counter += 1
    return rows

