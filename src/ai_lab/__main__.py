from __future__ import annotations

import argparse
from pathlib import Path

from .runtime.acceptance import run_vertical_acceptance


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Lab OS vertical acceptance runner")
    parser.add_argument("utterance", help="one natural-language request")
    args = parser.parse_args()

    receipt, receipt_path = run_vertical_acceptance(
        utterance=args.utterance,
        root=Path.cwd(),
    )

    print(f"① ONE HUMAN SENTENCE ........ YES")
    print(f"② TASK CREATED .............. YES")
    print(f"   action: {receipt.task.action.value}")
    print(f"   target: workspace/{receipt.task.relative_path}")
    print(f"   desired content: {receipt.task.text}")
    print(f"③ REAL CHANGE COMPLETED ..... {'YES' if receipt.changed else 'NO'}")
    print(f"   before: {receipt.before_text}")
    print(f"   after:  {receipt.after_text}")
    print(f"④ INDEPENDENT VERIFICATION .. {'YES' if receipt.verified else 'NO'}")
    print(f"   expected: {receipt.task.verification.expected_text}")
    print(f"   observed: {receipt.after_text}")
    print(f"FINAL RESULT: {'PASS' if receipt.final_status == 'verified_complete' else 'FAIL'}")
    print(f"RECEIPT: {receipt_path}")
    return 0 if receipt.final_status == "verified_complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
