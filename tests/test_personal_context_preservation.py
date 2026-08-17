from ai_lab.understanding.baseline import BaselineInterpreter
from ai_lab.understanding.context import ProvidedContextCompiler
from ai_lab.understanding.service import UnderstandingService


def test_personal_preferences_and_constraints_survive_understanding() -> None:
    def provider(_session_id: str) -> dict[str, object]:
        return {
            "active_artifact": "screen-layout",
            "preferences": ["minimal changes", "black and white"],
            "hard_constraints": ["do not alter unrelated layout"],
        }

    service = UnderstandingService(
        context_compiler=ProvidedContextCompiler(provider=provider),
        interpreter=BaselineInterpreter(),
    )

    result = service.understand(
        session_id="personal-context-1",
        utterance="這個字太大了，小一點，其他別動",
    )

    assert result.contract.primary_goal == "revise_current_artifact"
    assert result.contract.preferences == ("minimal changes", "black and white")
    assert result.contract.constraints == ("do not alter unrelated layout",)
    assert result.contract.evidence_ids
    assert set(result.contract.evidence_ids) == {
        item.id for item in result.context.evidence
    }
