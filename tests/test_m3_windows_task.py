from unittest.mock import patch

import pytest

from ai_lab.runtime.approval import execute_approved, prepare_execution
from ai_lab.runtime.windows_task import WindowsActionResult


def test_natural_language_youtube_request_generates_windows_plan() -> None:
    prepared = prepare_execution(utterance="打開 YouTube 網頁版")
    assert prepared.plan.executor == "Windows Agent"
    assert prepared.plan.target == "https://www.youtube.com/"
    assert prepared.action_kind == "open_youtube"
    assert any("YouTube" in step for step in prepared.plan.steps)


def test_youtube_plan_requires_approval(tmp_path) -> None:
    prepared = prepare_execution(utterance="幫我打開youtube")
    with pytest.raises(PermissionError):
        execute_approved(prepared=prepared, approved_plan_id="wrong", root=tmp_path)


@patch("ai_lab.runtime.approval.execute_open_youtube")
def test_approved_youtube_plan_dispatches_windows_agent(mock_execute, tmp_path) -> None:
    mock_execute.return_value = WindowsActionResult(
        changed=True,
        target="https://www.youtube.com/",
        verified=True,
        detail="browser_process_count=1",
    )
    prepared = prepare_execution(utterance="打開 YouTube 網頁版")
    receipt = execute_approved(
        prepared=prepared,
        approved_plan_id=prepared.plan.plan_id,
        root=tmp_path,
    )
    assert receipt.verified is True
    assert receipt.final_status == "verified_complete"
    mock_execute.assert_called_once_with()
