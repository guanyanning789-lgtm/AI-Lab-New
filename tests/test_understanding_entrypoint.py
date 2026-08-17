from ai_lab.understanding.baseline import BaselineInterpreter
from ai_lab.understanding.entrypoint import understand_utterance
from ai_lab.understanding.models import ClarificationAction


def test_resume_request_flows_through_canonical_entrypoint() -> None:
    result = understand_utterance(
        session_id="s1",
        utterance="繼續",
        raw_context={"active_goal": {"id": "goal-ai-lab"}},
        interpreter=BaselineInterpreter(),
    )

    assert result.context.active_goal_id == "goal-ai-lab"
    assert result.contract.literal_request == "繼續"
    assert result.contract.primary_goal == "resume_active_goal"
    assert result.contract.target_scope == ("goal-ai-lab",)
    assert result.decision.action in {
        ClarificationAction.PROCEED,
        ClarificationAction.PROCEED_WITH_ASSUMPTIONS,
    }


def test_ambiguous_project_request_surfaces_one_question() -> None:
    result = understand_utterance(
        session_id="s2",
        utterance="修好這個項目",
        raw_context={"active_repository": None},
        interpreter=BaselineInterpreter(),
    )

    assert result.contract.primary_goal == "repair_project"
    assert result.contract.missing_information
    assert result.decision.action == ClarificationAction.ASK_ONE_QUESTION
    assert result.decision.question


def test_empty_utterance_is_rejected_at_service_boundary() -> None:
    try:
        understand_utterance(
            session_id="s3",
            utterance="   ",
            raw_context={},
            interpreter=BaselineInterpreter(),
        )
    except ValueError as exc:
        assert "utterance cannot be empty" in str(exc)
    else:
        raise AssertionError("empty utterance should be rejected")
