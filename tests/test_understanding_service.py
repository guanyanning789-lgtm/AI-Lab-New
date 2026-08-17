from ai_lab.understanding.models import (
    AutonomyMode,
    ContextPack,
    IntentContract,
    Reversibility,
    RiskLevel,
    SuccessCriterion,
)
from ai_lab.understanding.service import UnderstandingService


class FakeContextCompiler:
    def compile(self, *, session_id: str, utterance: str) -> ContextPack:
        return ContextPack(
            session_id=session_id,
            utterance=utterance,
            active_goal_id="goal-123",
            project_state=("one active coding task",),
        )


class FakeInterpreter:
    def interpret(self, *, context: ContextPack) -> IntentContract:
        assert context.active_goal_id == "goal-123"
        return IntentContract(
            literal_request=context.utterance,
            primary_goal="resume_active_goal",
            inferred_need="continue without setup repetition",
            desired_outcome="resume goal-123",
            success_criteria=(
                SuccessCriterion(
                    id="resumed",
                    description="goal-123 enters planning or execution",
                    verification_method="state_check",
                ),
            ),
            risk_level=RiskLevel.LOW,
            reversibility=Reversibility.REVERSIBLE,
            autonomy_mode=AutonomyMode.EXECUTE,
            confidence=0.93,
        )


def test_service_compiles_context_before_interpreting() -> None:
    service = UnderstandingService(
        context_compiler=FakeContextCompiler(),
        interpreter=FakeInterpreter(),
    )
    result = service.understand(session_id="session-1", utterance="繼續")
    assert result.context.active_goal_id == "goal-123"
    assert result.contract.primary_goal == "resume_active_goal"
    assert result.decision.action.value == "proceed"


class InventedEvidenceInterpreter(FakeInterpreter):
    def interpret(self, *, context: ContextPack) -> IntentContract:
        base = super().interpret(context=context)
        return base.model_copy(update={"evidence_ids": ("evidence-that-does-not-exist",)})


def test_service_rejects_invented_evidence() -> None:
    service = UnderstandingService(
        context_compiler=FakeContextCompiler(),
        interpreter=InventedEvidenceInterpreter(),
    )
    try:
        service.understand(session_id="session-1", utterance="繼續")
    except ValueError as exc:
        assert "unknown evidence" in str(exc)
    else:
        raise AssertionError("invented evidence must not be accepted")
