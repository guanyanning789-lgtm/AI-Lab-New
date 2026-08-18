from pathlib import Path

from ai_lab.runtime.vertical_slice import SafeTextFileExecutor, assert_proceedable
from ai_lab.understanding.entrypoint import understand_utterance


def test_one_sentence_becomes_verified_real_change(tmp_path: Path) -> None:
    result = understand_utterance(
        session_id="acceptance",
        utterance="把驗收文件改成 DONE",
        raw_context={"active_artifact": "acceptance.txt"},
    )

    assert result.contract.primary_goal == "revise_current_artifact"
    assert result.contract.autonomy_mode.value == "execute"
    assert_proceedable(result.decision.action)

    execution = SafeTextFileExecutor(tmp_path).execute_write_text(
        contract=result.contract,
        relative_path="acceptance.txt",
        text="DONE",
    )

    assert execution.changed is True
    assert (tmp_path / "acceptance.txt").read_text(encoding="utf-8") == "DONE"
    assert execution.evidence.verified is True
    assert execution.evidence.observed_text == execution.evidence.expected_text


def test_executor_rejects_path_escape(tmp_path: Path) -> None:
    result = understand_utterance(
        session_id="acceptance",
        utterance="把這個改成 DONE",
        raw_context={"active_artifact": "acceptance.txt"},
    )
    assert_proceedable(result.decision.action)

    executor = SafeTextFileExecutor(tmp_path)
    try:
        executor.execute_write_text(
            contract=result.contract,
            relative_path="../escape.txt",
            text="DONE",
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("workspace escape must be rejected")
