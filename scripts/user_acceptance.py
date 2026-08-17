from __future__ import annotations

import json
import os
from pathlib import Path

from ai_lab.understanding.baseline import BaselineInterpreter, context_from_eval
from ai_lab.understanding.llm import OpenAIAgentsInterpreter


def _load_context() -> dict[str, object]:
    path = Path("acceptance_context.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _score(label: str) -> int:
    return {"y": 2, "m": 1, "n": 0}[label]


def main() -> None:
    print("AI LAB — User Acceptance 01")
    print("直接用你平常的說法。輸入 /quit 結束。\n")

    raw_context = _load_context()
    use_llm = bool(os.getenv("OPENAI_API_KEY"))
    interpreter = OpenAIAgentsInterpreter() if use_llm else BaselineInterpreter()
    print("理解引擎：" + ("LLM structured interpreter" if use_llm else "baseline（未設 OPENAI_API_KEY）"))

    total = 0
    count = 0
    while True:
        utterance = input("\n你 > ").strip()
        if utterance == "/quit":
            break
        if not utterance:
            continue

        context = context_from_eval(
            session_id="user-acceptance-01",
            utterance=utterance,
            raw=raw_context,
        )
        contract = interpreter.interpret(context=context)

        print("\nAI Lab 理解")
        print(f"  真正目標：{contract.primary_goal}")
        print(f"  我認為你需要：{contract.inferred_need}")
        print(f"  想得到的結果：{contract.desired_outcome}")
        print(f"  信心：{contract.confidence:.0%}")
        if contract.assumptions:
            print("  推測：")
            for item in contract.assumptions:
                print(f"    - {item.statement} ({item.confidence:.0%})")
        if contract.missing_information:
            print("  尚缺：")
            for item in contract.missing_information:
                print(f"    - {item}")

        print("\n請你判斷：y=很對 / m=大概對 / n=不對")
        while True:
            label = input("評分 > ").strip().lower()
            if label in {"y", "m", "n"}:
                break
        score = _score(label)
        total += score
        count += 1
        print(f"目前：{total}/{count * 2}")

    if count:
        print(f"\n本次 Understanding 得分：{total}/{count * 2} ({total / (count * 2):.0%})")
    else:
        print("\n本次沒有評分。")


if __name__ == "__main__":
    main()
