from __future__ import annotations

import json
import os
from pathlib import Path

from ai_lab.understanding.baseline import context_from_eval
from ai_lab.understanding.llm import OpenAIAgentsInterpreter
from ai_lab.understanding.policy import ClarificationPolicy


CORPUS = Path("evals/understanding_cases.jsonl")
RESULTS = Path("evals/cloud_acceptance_results.jsonl")
SAMPLE_IDS = {
    "resume-active-goal",
    "negative-feedback-current-artifact",
    "quality-operationalization",
    "one-priority-today",
    "coding-e2e",
    "ambiguous-multiple-repos",
    "stop-and-checkpoint",
    "visual-reference",
    "current-artifact-small-change",
}


def _load_sample() -> list[dict[str, object]]:
    cases = [
        json.loads(line)
        for line in CORPUS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [case for case in cases if case["id"] in SAMPLE_IDS]


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required; no cloud acceptance evidence was written.")

    interpreter = OpenAIAgentsInterpreter()
    policy = ClarificationPolicy()
    rows: list[dict[str, object]] = []
    passed = 0

    for case in _load_sample():
        context = context_from_eval(
            session_id=f'cloud-{case["id"]}',
            utterance=str(case["utterance"]),
            raw=case["context"],
        )
        contract = interpreter.interpret(context=context)
        decision = policy.decide(contract)
        expected = case["expected"]

        goal_ok = contract.primary_goal == expected["primary_goal"]
        clarification = expected["clarification"]
        decision_ok = (
            decision.action.value in {"proceed", "proceed_with_assumptions", "preview"}
            if clarification == "none"
            else decision.action.value == clarification
        )
        ok = goal_ok and decision_ok
        passed += int(ok)
        rows.append(
            {
                "id": case["id"],
                "passed": ok,
                "expected_goal": expected["primary_goal"],
                "actual_goal": contract.primary_goal,
                "expected_clarification": clarification,
                "actual_decision": decision.action.value,
                "confidence": contract.confidence,
            }
        )
        print(f'{case["id"]}: {"PASS" if ok else "FAIL"}')

    total = len(rows)
    score = passed / total if total else 0.0
    print(f"Cloud understanding acceptance: {passed}/{total} ({score:.0%})")

    if score < 0.80:
        raise SystemExit("Cloud acceptance below 80%; evidence file was not written.")

    RESULTS.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    print(f"Acceptance evidence written to {RESULTS}")


if __name__ == "__main__":
    main()
