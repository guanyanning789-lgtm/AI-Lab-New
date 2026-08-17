from ai_lab.understanding.models import (
    Assumption,
    AutonomyMode,
    ClarificationAction,
    IntentContract,
    Reversibility,
    RiskLevel,
    SuccessCriterion,
)
from ai_lab.understanding.policy import AuthorizationContext, ClarificationPolicy


def contract(**overrides: object) -> IntentContract:
    values: dict[str, object] = {
        "literal_request": "繼續",
        "primary_goal": "resume_active_goal",
        "inferred_need": "continue without repeating setup",
        "desired_outcome": "resume the most relevant active task",
        "success_criteria": (
            SuccessCriterion(
                id="active-run-resumed",
                description="the correct active GoalRun is resumed",
                verification_method="state_check",
            ),
        ),
        "risk_level": RiskLevel.LOW,
        "reversibility": Reversibility.REVERSIBLE,
        "autonomy_mode": AutonomyMode.EXECUTE,
        "confidence": 0.90,
    }
    values.update(overrides)
    return IntentContract(**values)


def test_clear_reversible_intent_proceeds() -> None:
    decision = ClarificationPolicy().decide(contract())
    assert decision.action is ClarificationAction.PROCEED


def test_low_impact_ambiguity_does_not_force_a_question() -> None:
    decision = ClarificationPolicy().decide(
        contract(
            confidence=0.70,
            assumptions=(
                Assumption(
                    statement="the most recent active project is the intended target",
                    confidence=0.70,
                    impact_if_wrong=RiskLevel.LOW,
                ),
            ),
        )
    )
    assert decision.action is ClarificationAction.PROCEED_WITH_ASSUMPTIONS


def test_missing_critical_information_asks_exactly_one_question() -> None:
    decision = ClarificationPolicy().decide(
        contract(missing_information=("哪一個 repository 是目標", "預期截止時間"))
    )
    assert decision.action is ClarificationAction.ASK_ONE_QUESTION
    assert decision.question is not None
    assert "repository" in decision.question


def test_irreversible_action_requires_approval() -> None:
    target = contract(
        primary_goal="delete_files",
        risk_level=RiskLevel.HIGH,
        reversibility=Reversibility.IRREVERSIBLE,
    )
    decision = ClarificationPolicy().decide(target)
    assert decision.action is ClarificationAction.REQUIRE_APPROVAL

    approved = ClarificationPolicy().decide(
        target,
        authorization=AuthorizationContext(irreversible_action_approved=True),
    )
    assert approved.action is ClarificationAction.PROCEED


def test_uncertain_high_impact_assumption_requires_confirmation() -> None:
    decision = ClarificationPolicy().decide(
        contract(
            assumptions=(
                Assumption(
                    statement="the user wants the public repository overwritten",
                    confidence=0.72,
                    impact_if_wrong=RiskLevel.HIGH,
                ),
            ),
        )
    )
    assert decision.action is ClarificationAction.ASK_ONE_QUESTION
