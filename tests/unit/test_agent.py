from pathlib import Path

import pytest

from backend.app.agent import GroundingError, GuardianAgent
from backend.app.ai import Explanation
from backend.app.db import Database
from backend.app.embeddings import EmbeddingService


class UngroundedAI:
    def explain(self, *_args, **_kwargs):
        return Explanation("Unsupported claim", "Do nothing", ["invented-id"])


def test_agent_rejects_evidence_that_was_not_retrieved(tmp_path: Path) -> None:
    database = Database(tmp_path / "test.db", EmbeddingService("demo", None, "unused"))
    database.initialize()
    agent = GuardianAgent(database, UngroundedAI())
    with pytest.raises(GroundingError):
        agent.assess("seed-001")

