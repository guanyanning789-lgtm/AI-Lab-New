import json
from pathlib import Path

import pytest

from ai_lab.runtime.acceptance import run_vertical_acceptance
from ai_lab.runtime.task_compiler import compile_task
from ai_lab.runtime.vertical_slice import SafeTextFileExecutor, assert_proceedable
from ai_lab.understanding.entrypoint import understand_utterance


UTTERANCE = "把工作區的 acceptance.txt 內容改成 DONE。"


def test_one_sentence_creates_task_without_manual_task_parameters() -> None:
    result = understand_utterance(session_id="acceptance", utterance=UTTERANCE)

    assert result.contract.primary_goal == "modify_text_file"
    assert result.contract.target_scope == ("acceptance.txt",)
    assert result.contract.desired_outcome == "DONE"
    assert result.contract.autonomy_mode.value == "execute"
    assert_proceedable(result.decision.action)

    task = compile_task(result.contract)
    assert task.action.value == "text_file.write"
    assert task.relative_path == "acceptance.txt"
    assert task.text == "DONE"
    assert task.verification.method == "read_back_exact_match"


def test_one_sentence_becomes_verified_real_change_and_receipt(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "acceptance.txt"
    target.write_text("BEFORE", encoding="utf-8")

    receipt, receipt_path = run_vertical_acceptance(utterance=UTTERANCE, root=tmp_path)

    assert target.read_text(encoding="utf-8") == "DONE"
    assert receipt.changed is True
    assert receipt.before_text == "BEFORE"
    assert receipt.after_text == "DONE"
    assert receipt.verified is True
    assert receipt.final_status == "verified_complete"
    assert receipt.before_hash != receipt.after_hash
    assert receipt_path.exists()

    persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert persisted["utterance"] == UTTERANCE
    assert persisted["task"]["relative_path"] == "acceptance.txt"
    assert persisted["task"]["text"] == "DONE"
    assert persisted["verified"] is True
    assert persisted["final_status"] == "verified_complete"


def test_executor_rejects_path_escape(tmp_path: Path) -> None:
    result = understand_utterance(
        session_id="acceptance",
        utterance="把工作區的 ../escape.txt 內容改成 DONE。",
    )
    assert_proceedable(result.decision.action)
    task = compile_task(result.contract)

    with pytest.raises(PermissionError, match="escapes configured workspace"):
        SafeTextFileExecutor(tmp_path).execute(contract=result.contract, task=task)


def test_unchanged_file_cannot_claim_verified_change(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "acceptance.txt").write_text("DONE", encoding="utf-8")

    receipt, _ = run_vertical_acceptance(utterance=UTTERANCE, root=tmp_path)

    assert receipt.changed is False
    assert receipt.verified is False
    assert receipt.final_status == "verification_failed"
