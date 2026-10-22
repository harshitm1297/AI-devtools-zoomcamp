from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "probable OpenAI secret": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "probable payment-card number": re.compile(r"(?<!\d)(?:\d[ -]?){15,16}(?!\d)"),
}


def main() -> int:
    findings: list[str] = []
    for folder in (ROOT / "backend", ROOT / "frontend", ROOT / "tests"):
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".js", ".html", ".css", ".json"}:
                continue
            text = path.read_text(encoding="utf-8")
            for label, pattern in PATTERNS.items():
                if pattern.search(text):
                    findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        print("Privacy guard failed:\n" + "\n".join(findings))
        return 1
    print("Privacy guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
