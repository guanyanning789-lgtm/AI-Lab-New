from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_lab.understanding.models import ClarificationAction, IntentContract


@dataclass(frozen=True)
class ExecutionEvidence:
    target: str
    expected_text: str
    observed_text: str
    verified: bool


@dataclass(frozen=True)
class ExecutionResult:
    contract: IntentContract
    changed: bool
    evidence: ExecutionEvidence


class SafeTextFileExecutor:
    """Minimal reversible side-effect executor for today's vertical acceptance slice.

    Raw user text is never accepted here. The executor only accepts a validated
    IntentContract plus explicit structured task data supplied by the caller.
    The target must stay inside the configured workspace.
    """

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def execute_write_text(
        self,
        *,
        contract: IntentContract,
        relative_path: str,
        text: str,
    ) -> ExecutionResult:
        if contract.autonomy_mode.value != "execute":
            raise PermissionError("intent contract does not authorize execution")

        target = (self.workspace / relative_path).resolve()
        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise PermissionError("target escapes configured workspace") from exc

        target.parent.mkdir(parents=True, exist_ok=True)
        before = target.read_text(encoding="utf-8") if target.exists() else None
        target.write_text(text, encoding="utf-8")
        observed = target.read_text(encoding="utf-8")
        verified = observed == text

        return ExecutionResult(
            contract=contract,
            changed=before != observed,
            evidence=ExecutionEvidence(
                target=str(target),
                expected_text=text,
                observed_text=observed,
                verified=verified,
            ),
        )


def assert_proceedable(action: ClarificationAction) -> None:
    if action not in {
        ClarificationAction.PROCEED,
        ClarificationAction.PROCEED_WITH_ASSUMPTIONS,
    }:
        raise PermissionError(f"policy decision does not permit execution: {action}")
