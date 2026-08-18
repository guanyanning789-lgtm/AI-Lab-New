from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from ai_lab.understanding.entrypoint import understand_utterance
from ai_lab.understanding.models import UnderstandingResult

from .acceptance import _save_receipt
from .task import CompletionReceipt, TaskSpec
from .task_compiler import compile_task
from .verifier import IndependentVerifier
from .vertical_slice import SafeTextFileExecutor, assert_proceedable


@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    utterance: str
    steps: tuple[str, ...]
    executor: str
    risk: str
    target: str


@dataclass(frozen=True)
class PreparedExecution:
    plan: ExecutionPlan
    understanding: UnderstandingResult
    task: TaskSpec


def prepare_execution(*, utterance: str) -> PreparedExecution:
    """Understand and compile a request without performing side effects."""
    understanding = understand_utterance(
        session_id=f"approval-{uuid4().hex[:8]}",
        utterance=utterance,
    )
    assert_proceedable(understanding.decision.action)
    task = compile_task(understanding.contract)
    plan = ExecutionPlan(
        plan_id=uuid4().hex,
        utterance=utterance,
        steps=(
            "Inspect the requested target and current state",
            "Compile the natural-language request into an executable task",
            "Execute the approved change",
            "Verify the result independently",
            "Report the verified outcome",
        ),
        executor="AI Lab runtime",
        risk=understanding.contract.risk_level.value,
        target=task.relative_path,
    )
    return PreparedExecution(plan=plan, understanding=understanding, task=task)


def execute_approved(*, prepared: PreparedExecution, approved_plan_id: str, root: Path) -> CompletionReceipt:
    """Execute only when the caller explicitly approves the exact prepared plan."""
    if approved_plan_id != prepared.plan.plan_id:
        raise PermissionError("execution blocked: plan has not been explicitly approved")

    workspace = (root / "workspace").resolve()
    execution = SafeTextFileExecutor(workspace).execute(
        contract=prepared.understanding.contract,
        task=prepared.task,
    )
    verification = IndependentVerifier(workspace).verify(
        task=prepared.task,
        before_hash=execution.before_hash,
    )
    receipt = CompletionReceipt(
        utterance=prepared.plan.utterance,
        task=prepared.task,
        policy_action=prepared.understanding.decision.action.value,
        changed=execution.changed,
        target=execution.target,
        before_text=execution.before_text,
        after_text=execution.after_text,
        before_hash=execution.before_hash,
        after_hash=execution.after_hash,
        verified=verification.verified,
        final_status="verified_complete" if verification.verified else "verification_failed",
    )
    _save_receipt(root=root, receipt=receipt)
    return receipt
