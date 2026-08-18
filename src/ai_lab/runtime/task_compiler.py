from __future__ import annotations

from ai_lab.understanding.models import IntentContract

from .task import TaskAction, TaskSpec, VerificationSpec


def compile_task(contract: IntentContract) -> TaskSpec:
    if contract.primary_goal != "modify_text_file":
        raise ValueError(f"unsupported goal for vertical slice: {contract.primary_goal}")
    if not contract.target_scope:
        raise ValueError("intent contract is missing a target file")

    target = contract.target_scope[0]
    desired_text = contract.desired_outcome
    if not desired_text:
        raise ValueError("intent contract is missing desired file content")

    return TaskSpec(
        action=TaskAction.WRITE_TEXT,
        relative_path=target,
        text=desired_text,
        verification=VerificationSpec(
            method="read_back_exact_match",
            expected_text=desired_text,
        ),
    )
