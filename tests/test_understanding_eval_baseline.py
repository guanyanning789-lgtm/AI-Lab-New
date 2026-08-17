import json
from pathlib import Path

import pytest

from ai_lab.understanding.baseline import BaselineInterpreter, context_from_eval
from ai_lab.understanding.policy import ClarificationPolicy


CASES = [
    json.loads(line)
    for line in Path("evals/understanding_cases.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_personal_understanding_baseline(case: dict) -> None:
    context = context_from_eval(
        session_id=f'eval-{case["id"]}',
        utterance=case["utterance"],
        raw=case["context"],
    )
    contract = BaselineInterpreter().interpret(context=context)
    decision = ClarificationPolicy().decide(contract)

    assert contract.primary_goal == case["expected"]["primary_goal"]
    expected_clarification = case["expected"]["clarification"]
    if expected_clarification == "none":
        assert decision.action.value in {"proceed", "proceed_with_assumptions", "preview"}
    else:
        assert decision.action.value == expected_clarification
