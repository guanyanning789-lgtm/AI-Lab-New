from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .task import TaskSpec


@dataclass(frozen=True)
class VerificationResult:
    target: str
    expected_text: str
    observed_text: str | None
    exists: bool
    content_matches: bool
    change_confirmed: bool
    after_hash: str | None
    verified: bool


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class IndependentVerifier:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def verify(self, *, task: TaskSpec, before_hash: str | None) -> VerificationResult:
        target = (self.workspace / task.relative_path).resolve()
        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise PermissionError("verification target escapes configured workspace") from exc

        if not target.exists():
            return VerificationResult(
                target=str(target),
                expected_text=task.verification.expected_text,
                observed_text=None,
                exists=False,
                content_matches=False,
                change_confirmed=False,
                after_hash=None,
                verified=False,
            )

        observed = target.read_text(encoding="utf-8")
        after_hash = sha256_text(observed)
        content_matches = observed == task.verification.expected_text
        change_confirmed = before_hash != after_hash
        return VerificationResult(
            target=str(target),
            expected_text=task.verification.expected_text,
            observed_text=observed,
            exists=True,
            content_matches=content_matches,
            change_confirmed=change_confirmed,
            after_hash=after_hash,
            verified=content_matches and change_confirmed,
        )
