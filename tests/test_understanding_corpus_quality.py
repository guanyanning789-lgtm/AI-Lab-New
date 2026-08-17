from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


CORPUS_PATH = Path("evals/understanding_cases.jsonl")


def _load_cases() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_understanding_corpus_has_at_least_50_unique_cases() -> None:
    cases = _load_cases()
    ids = [str(case["id"]) for case in cases]

    assert len(cases) >= 50
    assert len(ids) == len(set(ids)), "eval case ids must be unique"


def test_understanding_corpus_covers_multiple_real_intent_families() -> None:
    cases = _load_cases()
    goals = Counter(str(case["expected"]["primary_goal"]) for case in cases)

    required = {
        "resume_active_goal",
        "revise_current_artifact_using_previous_version",
        "improve_active_artifact_quality",
        "select_single_highest_priority_goal",
        "repair_failed_tests",
        "repair_project",
        "pause_and_checkpoint",
        "revise_visual_artifact_from_reference",
        "revise_current_artifact",
    }

    assert required.issubset(goals)
    assert all(goals[goal] >= 2 for goal in required)


def test_every_case_has_a_verifiable_expected_decision() -> None:
    for case in _load_cases():
        expected = case["expected"]
        assert expected.get("primary_goal")
        assert expected.get("clarification") in {"none", "ask_one_question"}
