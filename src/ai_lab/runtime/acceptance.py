from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_lab.understanding.entrypoint import understand_utterance

from .task import CompletionReceipt
from .task_compiler import compile_task
from .verifier import IndependentVerifier
from .vertical_slice import SafeTextFileExecutor, assert_proceedable


def run_vertical_acceptance(*, utterance: str, root: Path) -> tuple[CompletionReceipt, Path]:
    understanding = understand_utterance(
        session_id=f"acceptance-{uuid4().hex[:8]}",
        utterance=utterance,
    )
    assert_proceedable(understanding.decision.action)
    task = compile_task(understanding.contract)

    workspace = (root / "workspace").resolve()
    execution = SafeTextFileExecutor(workspace).execute(
        contract=understanding.contract,
        task=task,
    )
    verification = IndependentVerifier(workspace).verify(
        task=task,
        before_hash=execution.before_hash,
    )

    receipt = CompletionReceipt(
        utterance=utterance,
        task=task,
        policy_action=understanding.decision.action.value,
        changed=execution.changed,
        target=execution.target,
        before_text=execution.before_text,
        after_text=execution.after_text,
        before_hash=execution.before_hash,
        after_hash=execution.after_hash,
        verified=verification.verified,
        final_status="verified_complete" if verification.verified else "verification_failed",
    )
    receipt_path = _save_receipt(root=root, receipt=receipt)
    return receipt, receipt_path


def _save_receipt(*, root: Path, receipt: CompletionReceipt) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    run_dir = root / ".ai-lab" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "receipt.json"
    payload = asdict(receipt)
    payload["task"]["action"] = receipt.task.action.value
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
