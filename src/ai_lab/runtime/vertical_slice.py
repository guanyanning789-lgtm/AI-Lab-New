from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_lab.understanding.models import ClarificationAction, IntentContract

from .task import TaskAction, TaskSpec
from .verifier import sha256_text


@dataclass(frozen=True)
class ExecutionResult:
    contract: IntentContract
    changed: bool
    target: str
    before_text: str | None
    after_text: str
    before_hash: str | None
    after_hash: str


class SafeTextFileExecutor:
    """Execute validated structured tasks inside one configured workspace."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def execute(self, *, contract: IntentContract, task: TaskSpec) -> ExecutionResult:
        if contract.autonomy_mode.value != "execute":
            raise PermissionError("intent contract does not authorize execution")
        if task.action is not TaskAction.WRITE_TEXT:
            raise ValueError(f"unsupported action: {task.action}")

        target = (self.workspace / task.relative_path).resolve()
        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise PermissionError("target escapes configured workspace") from exc

        target.parent.mkdir(parents=True, exist_ok=True)
        before = target.read_text(encoding="utf-8") if target.exists() else None
        before_hash = sha256_text(before) if before is not None else None
        target.write_text(task.text, encoding="utf-8")
        after = target.read_text(encoding="utf-8")
        after_hash = sha256_text(after)

        return ExecutionResult(
            contract=contract,
            changed=before_hash != after_hash,
            target=str(target),
            before_text=before,
            after_text=after,
            before_hash=before_hash,
            after_hash=after_hash,
        )


def assert_proceedable(action: ClarificationAction) -> None:
    if action not in {
        ClarificationAction.PROCEED,
        ClarificationAction.PROCEED_WITH_ASSUMPTIONS,
    }:
        raise PermissionError(f"policy decision does not permit execution: {action}")
