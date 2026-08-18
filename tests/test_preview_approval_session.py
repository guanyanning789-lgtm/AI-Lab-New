from pathlib import Path

from ai_lab.runtime.approval import PreviewApprovalSession


def test_request_only_previews_and_does_not_modify(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "acceptance.txt"
    target.write_text("BEFORE", encoding="utf-8")

    session = PreviewApprovalSession(tmp_path)
    reply = session.submit("把工作區的 acceptance.txt 內容改成 DONE。")

    assert reply.kind == "plan"
    assert "目前尚未執行任何修改" in reply.message
    assert "workspace/acceptance.txt" in reply.message
    assert "DONE" in reply.message
    assert target.read_text(encoding="utf-8") == "BEFORE"
    assert session.pending is not None


def test_execute_runs_exact_pending_plan_and_verifies(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "acceptance.txt"
    target.write_text("BEFORE", encoding="utf-8")

    session = PreviewApprovalSession(tmp_path)
    plan_reply = session.submit("把工作區的 acceptance.txt 內容改成 DONE。")
    assert plan_reply.kind == "plan"
    pending_id = session.pending.plan_id if session.pending else None

    reply = session.submit("執行")

    assert pending_id is not None
    assert reply.kind == "completed"
    assert reply.receipt is not None
    assert reply.receipt.task.relative_path == "acceptance.txt"
    assert reply.receipt.task.text == "DONE"
    assert reply.receipt.changed is True
    assert reply.receipt.verified is True
    assert reply.receipt.final_status == "verified_complete"
    assert target.read_text(encoding="utf-8") == "DONE"
    assert session.pending is None


def test_execute_without_pending_plan_is_rejected(tmp_path: Path) -> None:
    session = PreviewApprovalSession(tmp_path)

    reply = session.submit("執行")

    assert reply.kind == "error"
    assert "沒有等待執行的計劃" in reply.message


def test_new_request_replaces_pending_plan_without_executing_old_one(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "acceptance.txt"
    target.write_text("BEFORE", encoding="utf-8")

    session = PreviewApprovalSession(tmp_path)
    first = session.submit("把工作區的 acceptance.txt 內容改成 OLD。")
    first_id = session.pending.plan_id if session.pending else None
    second = session.submit("把工作區的 acceptance.txt 內容改成 NEW。")
    second_id = session.pending.plan_id if session.pending else None

    assert first.kind == "plan"
    assert second.kind == "plan"
    assert first_id != second_id
    assert target.read_text(encoding="utf-8") == "BEFORE"

    completed = session.submit("執行")
    assert completed.kind == "completed"
    assert target.read_text(encoding="utf-8") == "NEW"


def test_cancel_discards_pending_plan(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "acceptance.txt"
    target.write_text("BEFORE", encoding="utf-8")

    session = PreviewApprovalSession(tmp_path)
    session.submit("把工作區的 acceptance.txt 內容改成 DONE。")
    reply = session.submit("取消")

    assert reply.kind == "cancelled"
    assert session.pending is None
    assert target.read_text(encoding="utf-8") == "BEFORE"
