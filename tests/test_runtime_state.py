import pytest

from ai_lab.runtime import GoalRunState, InvalidStateTransition, ensure_transition


def test_happy_path_transitions_are_allowed() -> None:
    path = (
        GoalRunState.RECEIVED,
        GoalRunState.CONTEXTUALIZING,
        GoalRunState.UNDERSTANDING,
        GoalRunState.READY,
        GoalRunState.PLANNING,
        GoalRunState.EXECUTING,
        GoalRunState.VERIFYING,
        GoalRunState.COMPLETED,
    )
    for current, target in zip(path, path[1:]):
        ensure_transition(current, target)


def test_completed_run_cannot_restart_silently() -> None:
    with pytest.raises(InvalidStateTransition):
        ensure_transition(GoalRunState.COMPLETED, GoalRunState.EXECUTING)
