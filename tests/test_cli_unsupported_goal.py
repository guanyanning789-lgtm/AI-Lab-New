from __future__ import annotations

import sys

from ai_lab import __main__ as cli


def test_unsupported_goal_is_reported_without_traceback(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["ai_lab", "檢查我的磁盤，最大的占比"])

    result = cli.main()
    output = capsys.readouterr().out

    assert result == 3
    assert "目前還不能為這個任務生成可執行計劃" in output
    assert "沒有執行任何修改" in output
    assert "Traceback" not in output
