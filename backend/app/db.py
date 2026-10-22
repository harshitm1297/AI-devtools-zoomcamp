from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .embeddings import EmbeddingService, cosine_similarity, purchase_text
from .seed import synthetic_purchases


class Database:
    def __init__(self, path: Path, embeddings: EmbeddingService) -> None:
        self.path = path
        self.embeddings = embeddings

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY,
                    image_sha256 TEXT NOT NULL,
                    extracted_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS purchases (
                    id TEXT PRIMARY KEY,
                    receipt_id TEXT REFERENCES receipts(id),
                    merchant TEXT NOT NULL,
                    category TEXT NOT NULL,
                    purchase_date TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    amount REAL NOT NULL,
                    embedding_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS assessments (
                    id TEXT PRIMARY KEY,
                    purchase_id TEXT NOT NULL REFERENCES purchases(id),
                    assessment TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    suggested_action TEXT NOT NULL,
                    evidence_ids_json TEXT NOT NULL,
                    median_amount REAL,
                    threshold_amount REAL,
                    model_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    assessment_id TEXT NOT NULL UNIQUE REFERENCES assessments(id),
                    helpful INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            count = db.execute("SELECT COUNT(*) FROM purchases WHERE source = 'seed'").fetchone()[0]
            if count == 0:
                self._insert_seed_rows(db, synthetic_purchases())

    def _insert_seed_rows(self, db: sqlite3.Connection, rows: Iterable[dict[str, object]]) -> None:
        rows = list(rows)
        now = datetime.now(timezone.utc).isoformat()
        texts = [
            purchase_text(str(row["merchant"]), str(row["category"]), str(row["currency"]))
            for row in rows
        ]
        for row, embedding in zip(rows, self.embeddings.embed_many(texts), strict=True):
            db.execute(
                """INSERT INTO purchases
                   (id, receipt_id, merchant, category, purchase_date, currency, amount,
                    embedding_json, source, created_at)
                   VALUES (?, NULL, ?, ?, ?, ?, ?, ?, 'seed', ?)""",
                (
                    row["id"], row["merchant"], row["category"], row["purchase_date"],
                    row["currency"], row["amount"], json.dumps(embedding), now,
                ),
            )

    def execute(self, sql: str, parameters: tuple[Any, ...] = ()) -> None:
        with self.connect() as db:
            db.execute(sql, parameters)

    def fetchone(self, sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute(sql, parameters).fetchone()
        return dict(row) if row else None

    def fetchall(self, sql: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(sql, parameters).fetchall()
        return [dict(row) for row in rows]

    def similar_purchases(self, purchase: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
        candidates = self.fetchall(
            "SELECT * FROM purchases WHERE currency = ? AND id != ?",
            (purchase["currency"], purchase["id"]),
        )
        target = json.loads(purchase["embedding_json"])
        for candidate in candidates:
            candidate["similarity"] = cosine_similarity(target, json.loads(candidate["embedding_json"]))
        candidates.sort(key=lambda row: (row["similarity"], row["purchase_date"]), reverse=True)
        return candidates[:limit]

