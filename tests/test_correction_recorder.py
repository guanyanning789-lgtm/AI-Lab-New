from __future__ import annotations

import json

import pytest

from ai_lab.understanding.corrections import CorrectionRecorder


def test_partial_or_wrong_understanding_is_recorded_as_eval_candidate(tmp_path) -> None:
    path = tmp_path / "corrections.jsonl"
    recorder = CorrectionRecorder(path)

    recorder.record(
        utterance="這個不對，還是上一版好一點",
        raw_context={"current_artifact": "v3", "previous_artifact": "v2"},
        predicted_goal="revise_current_artifact",
        predicted_outcome="change the current artifact",
        rating="n",
        correction="我要以 v2 為基準修改 v3，不是重新設計。",
    )

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    assert records[0]["utterance"] == "這個不對，還是上一版好一點"
    assert records[0]["rating"] == "n"
    assert records[0]["status"] == "candidate"
    assert records[0]["prediction"]["primary_goal"] == "revise_current_artifact"
    assert "v2" in records[0]["user_correction"]


def test_good_rating_is_not_allowed_into_correction_queue(tmp_path) -> None:
    recorder = CorrectionRecorder(tmp_path / "corrections.jsonl")

    with pytest.raises(ValueError, match="only partial or incorrect"):
        recorder.record(
            utterance="繼續",
            raw_context={},
            predicted_goal="resume_active_goal",
            predicted_outcome="resume",
            rating="y",
            correction="already correct",
        )
