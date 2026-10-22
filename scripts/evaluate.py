from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.risk import calculate_risk  # noqa: E402


def main() -> int:
    cases = json.loads((ROOT / "data" / "evaluation-cases.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        evidence = [{"amount": amount} for amount in case["history"]]
        actual = calculate_risk(case["amount"], evidence).assessment
        marker = "PASS" if actual == case["expected"] else "FAIL"
        print(f"{marker} {case['id']}: expected={case['expected']} actual={actual}")
        if marker == "FAIL":
            failures.append(case["id"])
    print(f"{len(cases) - len(failures)}/{len(cases)} deterministic cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
