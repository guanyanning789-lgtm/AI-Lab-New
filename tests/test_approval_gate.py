from pathlib import Path

import pytest

from ai_lab.runtime.approval import execute_approved, prepare_execution
from ai_lab.understanding.entrypoint import understand_utterance


def test_baseline_recognizes_workspace_prefixed_file_write() -> None:
    result = understand_utterance(
        session_id="approval-regression",
        utterance="把 workspace/demo.txt 改成 hello",
    )

    assert result.contract.primary_goal == "modify_text_file"
    assert result.contract.target_scope == ("demo.txt",)
    assert result.contract.desired_outcome == "hello"


def test_prepare_execution_has_no_side_effect(tmp_path: Path) -> None:
    prepared = prepare_execution(utterance="把 workspace/demo.txt 改成 hello")

    assert prepared.plan.plan_id
    assert prepared.plan.steps
    assert prepared.plan.risk in {"low", "medium", "high", "critical"}
    assert not (tmp_path / "workspace" / "demo.txt").exists()


def test_execution_requires_exact_plan_approval(tmp_path: Path) -> None:
    prepared = prepare_execution(utterance="把 workspace/demo.txt 改成 hello")

    with pytest.raises(PermissionError, match="explicitly approved"):
        execute_approved(
            prepared=prepared,
            approved_plan_id="wrong-plan-id",
            root=tmp_path,
        )

    assert not (tmp_path / "workspace" / "demo.txt").exists()


def test_approved_plan_executes_and_verifies(tmp_path: Path) -> None:
    prepared = prepare_execution(utterance="把 workspace/demo.txt 改成 hello")

    receipt = execute_approved(
        prepared=prepared,
        approved_plan_id=prepared.plan.plan_id,
        root=tmp_path,
    )

    assert receipt.verified is True
    assert receipt.final_status == "verified_complete"
