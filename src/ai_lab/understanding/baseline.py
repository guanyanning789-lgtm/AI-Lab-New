from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .models import (
    AutonomyMode,
    ContextPack,
    IntentContract,
    Reversibility,
    RiskLevel,
    SuccessCriterion,
)


def context_from_eval(*, session_id: str, utterance: str, raw: Mapping[str, Any]) -> ContextPack:
    active_goal = raw.get("active_goal") or {}
    active_goal_id = active_goal.get("id") if isinstance(active_goal, Mapping) else None
    project_state = tuple(f"{k}={v}" for k, v in raw.items())
    preferences = tuple(str(item) for item in raw.get("preferences", ()) or ())
    hard_constraints = tuple(str(item) for item in raw.get("hard_constraints", ()) or ())
    return ContextPack(
        session_id=session_id,
        utterance=utterance,
        active_goal_id=active_goal_id,
        preferences=preferences,
        hard_constraints=hard_constraints,
        project_state=project_state,
    )


_FILE_WRITE_PATTERN = re.compile(
    r"(?:把|將)\s*(?:工作區(?:的)?\s*|workspace[\\/]?)?([\w.\-/]+)\s*(?:內容)?(?:改成|修改為|設為)\s*[\"'「『]?(.+?)[\"'」』]?\s*[。.!！]?$",
    re.IGNORECASE,
)


class BaselineInterpreter:
    """Deterministic baseline that makes obvious personal requests scoreable."""

    def interpret(self, *, context: ContextPack) -> IntentContract:
        text = context.utterance.strip()
        state = "\n".join(context.project_state)

        goal = "unknown_goal"
        target: tuple[str, ...] = ()
        missing: tuple[str, ...] = ()
        confidence = 0.60
        inferred = "resolve the user's current request from available context"
        outcome = "produce the requested result"
        autonomy = AutonomyMode.ADVISE
        verification_method = "scenario_specific_check"

        file_write = _FILE_WRITE_PATTERN.search(text)
        if file_write:
            file_name = file_write.group(1).strip()
            desired_text = file_write.group(2).strip()
            goal = "modify_text_file"
            target = (file_name,)
            confidence = 0.98
            inferred = "modify the requested text file inside the configured workspace"
            outcome = desired_text
            autonomy = AutonomyMode.EXECUTE
            verification_method = "read_back_exact_match"
        elif (text == "繼續" or text.startswith("繼續") or text.startswith("你繼續")) and context.active_goal_id:
            goal = "resume_active_goal"
            target = (context.active_goal_id,)
            confidence = 0.97
            inferred = "resume the saved active goal without repeating setup"
            outcome = f"resume {context.active_goal_id} from its saved state"
            autonomy = AutonomyMode.EXECUTE
        elif "上一版" in text and ("current_artifact=" in state or "previous_artifact=" in state):
            goal = "revise_current_artifact_using_previous_version"
            confidence = 0.93
            inferred = "use the previous artifact as the preferred reference and revise the current one"
            outcome = "revise the current artifact while preserving prior preferences"
            autonomy = AutonomyMode.EXECUTE
        elif ("專業一點" in text or "專業點" in text) and "quality_rubric_available=True" in state:
            goal = "improve_active_artifact_quality"
            confidence = 0.92
            inferred = "improve quality using the artifact-specific rubric rather than decoration"
            outcome = "produce a measurably higher-quality active artifact"
            autonomy = AutonomyMode.EXECUTE
        elif "今天我最應該做什麼" in text or "今天只做最重要" in text:
            goal = "select_single_highest_priority_goal"
            confidence = 0.94
            inferred = "choose one priority using current commitments, projects and deadlines"
            outcome = "return one highest-priority goal for today"
            autonomy = AutonomyMode.ADVISE
        elif ("失敗測試" in text or ("測試" in text and "修" in text)) and "active_repository=" in state:
            goal = "repair_failed_tests"
            confidence = 0.96
            inferred = "repair the failing tests in the active repository and verify before reporting success"
            outcome = "all targeted failed tests pass with verification evidence"
            autonomy = AutonomyMode.EXECUTE
        elif (
            "修好這個項目" in text
            or "修這個項目" in text
            or "把這個項目修好" in text
        ) and "active_repository=None" in state:
            goal = "repair_project"
            confidence = 0.84
            inferred = "repair a project, but the repository identity is unresolved"
            outcome = "repair the intended repository"
            missing = ("你指的是 repo-a 還是 repo-b？",)
            autonomy = AutonomyMode.EXECUTE
        elif ("下次繼續" in text or "先到這" in text or "先到這裡" in text) and context.active_goal_id:
            goal = "pause_and_checkpoint"
            target = (context.active_goal_id,)
            confidence = 0.98
            inferred = "pause execution and persist the exact current state for later resumption"
            outcome = "active goal is safely checkpointed and no further execution occurs"
            autonomy = AutonomyMode.EXECUTE
        elif "圖片" in text and "current_image_reference=" in state:
            goal = "revise_visual_artifact_from_reference"
            confidence = 0.95
            inferred = "use the referenced image as visual evidence and change only the requested typography"
            outcome = "revise the visual artifact to match the reference with smaller text"
            autonomy = AutonomyMode.EXECUTE
        elif "這個" in text and "active_artifact=" in state:
            goal = "revise_current_artifact"
            confidence = 0.86
            inferred = "apply the requested change to the active artifact without changing unrelated parts"
            outcome = "revise only the requested aspect of the active artifact"
            autonomy = AutonomyMode.EXECUTE

        evidence_ids = tuple(item.id for item in context.evidence)
        return IntentContract(
            literal_request=context.utterance,
            primary_goal=goal,
            inferred_need=inferred,
            desired_outcome=outcome,
            target_scope=target,
            constraints=context.hard_constraints,
            preferences=context.preferences,
            success_criteria=(
                SuccessCriterion(
                    id="expected-outcome",
                    description=outcome,
                    verification_method=verification_method,
                ),
            ),
            missing_information=missing,
            risk_level=RiskLevel.LOW,
            reversibility=Reversibility.REVERSIBLE,
            autonomy_mode=autonomy,
            confidence=confidence,
            evidence_ids=evidence_ids,
        )
