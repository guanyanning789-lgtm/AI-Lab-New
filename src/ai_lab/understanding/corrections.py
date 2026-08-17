from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class CorrectionRecorder:
    """Append user feedback as durable JSONL candidates for future evals.

    M1 does not silently mutate the canonical eval corpus. Corrections are first
    captured with the original utterance, context and model prediction so they
    can be reviewed and promoted into regression tests deliberately.
    """

    path: Path

    def record(
        self,
        *,
        utterance: str,
        raw_context: Mapping[str, Any],
        predicted_goal: str,
        predicted_outcome: str,
        rating: str,
        correction: str,
    ) -> None:
        if rating not in {"m", "n"}:
            raise ValueError("only partial or incorrect interpretations should be recorded")
        if not correction.strip():
            raise ValueError("correction cannot be empty")

        payload = {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "utterance": utterance,
            "context": dict(raw_context),
            "prediction": {
                "primary_goal": predicted_goal,
                "desired_outcome": predicted_outcome,
            },
            "rating": rating,
            "user_correction": correction.strip(),
            "status": "candidate",
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
