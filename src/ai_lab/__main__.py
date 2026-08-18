from __future__ import annotations

import argparse
from pathlib import Path

from .runtime.approval import execute_approved, prepare_execution


def _print_plan(prepared) -> None:
    plan = prepared.plan
    print("\nAI LAB")
    print(f"\n你想做什麼？\n{plan.utterance}\n")
    print("AI Lab 執行計劃\n")
    for index, step in enumerate(plan.steps, start=1):
        print(f"{index}. {step}")
    print(f"\n執行器：{plan.executor}")
    print(f"風險：{plan.risk}")
    print(f"目標：{plan.target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Lab OS approval-gated runner")
    parser.add_argument("utterance", nargs="?", help="one natural-language request")
    parser.add_argument(
        "--approve",
        action="store_true",
        help="approve the generated plan non-interactively",
    )
    args = parser.parse_args()

    utterance = args.utterance or input("你想做什麼？\n> ").strip()
    if not utterance:
        print("沒有收到任務。")
        return 2

    try:
        prepared = prepare_execution(utterance=utterance)
    except ValueError as exc:
        if "unsupported goal for vertical slice" in str(exc):
            print("\nAI Lab 目前還不能為這個任務生成可執行計劃。")
            print("沒有執行任何修改。")
            print("目前這個里程碑只支援：自然語言修改 workspace 內的文字文件。")
            return 3
        raise

    _print_plan(prepared)

    approved = args.approve
    if not approved:
        answer = input("\n輸入『執行』批准此計劃，其他輸入都會取消：\n> ").strip()
        approved = answer == "執行"

    if not approved:
        print("\n已取消。沒有執行任何修改。")
        return 0

    receipt = execute_approved(
        prepared=prepared,
        approved_plan_id=prepared.plan.plan_id,
        root=Path.cwd(),
    )

    print("\n執行結果")
    print(f"修改完成：{'YES' if receipt.changed else 'NO'}")
    print(f"獨立驗證：{'PASS' if receipt.verified else 'FAIL'}")
    print(f"最終狀態：{receipt.final_status}")
    print(f"目標：{receipt.target}")
    return 0 if receipt.final_status == "verified_complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
