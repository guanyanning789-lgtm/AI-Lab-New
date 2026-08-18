from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from ai_lab.understanding.entrypoint import understand_utterance
from ai_lab.understanding.models import IntentContract

from .acceptance import _save_receipt
from .task import CompletionReceipt, TaskSpec
from .task_compiler import compile_task
from .verifier import IndependentVerifier
from .vertical_slice import SafeTextFileExecutor, assert_proceedable


@dataclass(frozen=True)
class PendingPlan:
    plan_id: str
    utterance: str
    contract: IntentContract
    task: TaskSpec

    def render(self) -> str:
        return (
            "執行計劃\n"
            f"計劃 ID：{self.plan_id}\n"
            f"1. 動作：{self.task.action.value}\n"
            f"2. 目標：workspace/{self.task.relative_path}\n"
            f"3. 修改為：{self.task.text}\n"
            f"4. 驗證：{self.task.verification.method}，預期 {self.task.verification.expected_text}\n\n"
            "目前尚未執行任何修改。\n"
            "如果確認，請輸入：執行"
        )


@dataclass(frozen=True)
class SessionReply:
    kind: str
    message: str
    receipt: CompletionReceipt | None = None
    receipt_path: Path | None = None


class PreviewApprovalSession:
    """Two-turn interaction: preview an exact task, then execute only on explicit approval."""

    APPROVE_WORDS = {"執行", "执行"}
    CANCEL_WORDS = {"取消", "不要執行", "不要执行"}

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.pending: PendingPlan | None = None

    def submit(self, text: str) -> SessionReply:
        normalized = text.strip()
        if not normalized:
            return SessionReply(kind="error", message="請輸入你的需求。")

        if normalized in self.CANCEL_WORDS:
            self.pending = None
            return SessionReply(kind="cancelled", message="已取消。沒有執行任何修改。")

        if normalized in self.APPROVE_WORDS:
            if self.pending is None:
                return SessionReply(kind="error", message="目前沒有等待執行的計劃。請先告訴我你要做什麼。")
            return self._execute_pending()

        understanding = understand_utterance(
            session_id=f"dialog-{uuid4().hex[:8]}",
            utterance=normalized,
        )
        assert_proceedable(understanding.decision.action)
        task = compile_task(understanding.contract)
        plan = PendingPlan(
            plan_id=uuid4().hex[:10],
            utterance=normalized,
            contract=understanding.contract,
            task=task,
        )
        self.pending = plan
        return SessionReply(kind="plan", message=plan.render())

    def _execute_pending(self) -> SessionReply:
        plan = self.pending
        if plan is None:
            raise RuntimeError("pending plan disappeared")

        workspace = (self.root / "workspace").resolve()
        execution = SafeTextFileExecutor(workspace).execute(
            contract=plan.contract,
            task=plan.task,
        )
        verification = IndependentVerifier(workspace).verify(
            task=plan.task,
            before_hash=execution.before_hash,
        )
        receipt = CompletionReceipt(
            utterance=plan.utterance,
            task=plan.task,
            policy_action="explicit_user_approval",
            changed=execution.changed,
            target=execution.target,
            before_text=execution.before_text,
            after_text=execution.after_text,
            before_hash=execution.before_hash,
            after_hash=execution.after_hash,
            verified=verification.verified,
            final_status="verified_complete" if verification.verified else "verification_failed",
        )
        receipt_path = _save_receipt(root=self.root, receipt=receipt)
        self.pending = None

        if receipt.verified:
            message = (
                "執行完成。\n"
                f"目標：workspace/{receipt.task.relative_path}\n"
                f"修改前：{receipt.before_text}\n"
                f"修改後：{receipt.after_text}\n"
                "驗證：PASS\n"
                f"回執：{receipt_path}"
            )
            return SessionReply(
                kind="completed",
                message=message,
                receipt=receipt,
                receipt_path=receipt_path,
            )

        return SessionReply(
            kind="failed",
            message="執行已完成，但獨立驗證失敗。系統不會宣稱任務完成。",
            receipt=receipt,
            receipt_path=receipt_path,
        )
