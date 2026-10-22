from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    ai_mode: str
    openai_api_key: str | None
    ollama_base_url: str
    ollama_model: str
    vision_model: str
    explanation_model: str
    embedding_model: str
    max_image_bytes: int
    anomaly_multiplier: float

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("AI_MODE", "demo").lower()
        if mode not in {"demo", "ollama", "openai"}:
            raise ValueError("AI_MODE must be 'demo', 'ollama', or 'openai'")
        key = os.getenv("OPENAI_API_KEY")
        if mode == "openai" and not key:
            raise ValueError("OPENAI_API_KEY is required when AI_MODE=openai")
        return cls(
            database_path=Path(os.getenv("DATABASE_PATH", "data/guardian_angel.db")),
            ai_mode=mode,
            openai_api_key=key,
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
            vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-6-astra"),
            explanation_model=os.getenv("OPENAI_EXPLANATION_MODEL", "gpt-6-astra"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            max_image_bytes=int(os.getenv("MAX_IMAGE_BYTES", str(5 * 1024 * 1024))),
            anomaly_multiplier=float(os.getenv("ANOMALY_MULTIPLIER", "1.5")),
        )

