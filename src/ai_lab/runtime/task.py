from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskAction(str, Enum):
    WRITE_TEXT = "text_file.write"


@dataclass(frozen=True)
class VerificationSpec:
    method: str
    expected_text: str


@dataclass(frozen=True)
class TaskSpec:
    action: TaskAction
    relative_path: str
    text: str
    verification: VerificationSpec


@dataclass(frozen=True)
class CompletionReceipt:
    utterance: str
    task: TaskSpec
    policy_action: str
    changed: bool
    target: str
    before_text: str | None
    after_text: str
    before_hash: str | None
    after_hash: str
    verified: bool
    final_status: str
