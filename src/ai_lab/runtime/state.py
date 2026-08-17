from __future__ import annotations

from enum import Enum


class GoalRunState(str, Enum):
    RECEIVED = "received"
    CONTEXTUALIZING = "contextualizing"
    UNDERSTANDING = "understanding"
    WAITING_FOR_USER = "waiting_for_user"
    READY = "ready"
    PLANNING = "planning"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    REPAIRING = "repairing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


_ALLOWED: dict[GoalRunState, frozenset[GoalRunState]] = {
    GoalRunState.RECEIVED: frozenset({GoalRunState.CONTEXTUALIZING, GoalRunState.CANCELLED}),
    GoalRunState.CONTEXTUALIZING: frozenset(
        {GoalRunState.UNDERSTANDING, GoalRunState.FAILED, GoalRunState.CANCELLED}
    ),
    GoalRunState.UNDERSTANDING: frozenset(
        {
            GoalRunState.WAITING_FOR_USER,
            GoalRunState.READY,
            GoalRunState.FAILED,
            GoalRunState.CANCELLED,
        }
    ),
    GoalRunState.WAITING_FOR_USER: frozenset(
        {GoalRunState.CONTEXTUALIZING, GoalRunState.CANCELLED}
    ),
    GoalRunState.READY: frozenset({GoalRunState.PLANNING, GoalRunState.CANCELLED}),
    GoalRunState.PLANNING: frozenset(
        {
            GoalRunState.WAITING_FOR_APPROVAL,
            GoalRunState.EXECUTING,
            GoalRunState.FAILED,
            GoalRunState.CANCELLED,
        }
    ),
    GoalRunState.WAITING_FOR_APPROVAL: frozenset(
        {GoalRunState.EXECUTING, GoalRunState.CANCELLED}
    ),
    GoalRunState.EXECUTING: frozenset(
        {
            GoalRunState.VERIFYING,
            GoalRunState.REPAIRING,
            GoalRunState.REPLANNING,
            GoalRunState.FAILED,
            GoalRunState.CANCELLED,
        }
    ),
    GoalRunState.VERIFYING: frozenset(
        {
            GoalRunState.COMPLETED,
            GoalRunState.PARTIAL,
            GoalRunState.REPAIRING,
            GoalRunState.REPLANNING,
            GoalRunState.FAILED,
            GoalRunState.CANCELLED,
        }
    ),
    GoalRunState.REPAIRING: frozenset(
        {GoalRunState.EXECUTING, GoalRunState.REPLANNING, GoalRunState.FAILED}
    ),
    GoalRunState.REPLANNING: frozenset(
        {GoalRunState.PLANNING, GoalRunState.FAILED, GoalRunState.CANCELLED}
    ),
    GoalRunState.COMPLETED: frozenset(),
    GoalRunState.PARTIAL: frozenset(),
    GoalRunState.FAILED: frozenset(),
    GoalRunState.CANCELLED: frozenset(),
}


class InvalidStateTransition(ValueError):
    pass


def ensure_transition(current: GoalRunState, target: GoalRunState) -> None:
    if target not in _ALLOWED[current]:
        raise InvalidStateTransition(f"invalid GoalRun transition: {current.value} -> {target.value}")
