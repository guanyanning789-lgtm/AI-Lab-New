from ai_lab.understanding.baseline import BaselineInterpreter
from ai_lab.understanding.context import ProvidedContextCompiler
from ai_lab.understanding.models import ClarificationAction
from ai_lab.understanding.service import UnderstandingService


def test_resume_short_utterance_resolves_active_goal_without_question() -> None:
    compiler = ProvidedContextCompiler(
        provider=lambda session_id: {
            "active_goal": {
                "id": "goal-coding-17",
                "status": "repairing",
                "summary": "repair failing repository tests",
            },
            "active_repository": "repo-a",
        }
    )
    service = UnderstandingService(
        context_compiler=compiler,
        interpreter=BaselineInterpreter(),
    )

    result = service.understand(session_id="session-1", utterance="繼續")

    assert result.contract.primary_goal == "resume_active_goal"
    assert result.contract.target_scope == ("goal-coding-17",)
    assert result.contract.literal_request == "繼續"
    assert result.decision.action is ClarificationAction.PROCEED


def test_ambiguous_project_asks_exactly_one_high_value_question() -> None:
    compiler = ProvidedContextCompiler(
        provider=lambda session_id: {
            "active_repository": None,
            "recent_repositories": ["repo-a", "repo-b"],
            "dominant_candidate": None,
        }
    )
    service = UnderstandingService(
        context_compiler=compiler,
        interpreter=BaselineInterpreter(),
    )

    result = service.understand(session_id="session-2", utterance="修好這個項目")

    assert result.contract.primary_goal == "repair_project"
    assert result.decision.action is ClarificationAction.ASK_ONE_QUESTION
    assert result.decision.question is not None
    assert "repo-a" in result.decision.question
    assert "repo-b" in result.decision.question
