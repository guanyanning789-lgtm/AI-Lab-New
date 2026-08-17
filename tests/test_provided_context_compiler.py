from ai_lab.understanding.context import ProvidedContextCompiler


def test_compiler_preserves_active_goal_preferences_constraints_and_evidence() -> None:
    compiler = ProvidedContextCompiler(
        provider=lambda session_id: {
            "active_goal": {"id": "goal-42", "status": "repairing"},
            "active_repository": "repo-a",
            "preferences": ["prefer concise progress updates"],
            "hard_constraints": ["do not modify files outside repo-a"],
        }
    )

    context = compiler.compile(session_id="session-1", utterance="繼續")

    assert context.active_goal_id == "goal-42"
    assert context.preferences == ("prefer concise progress updates",)
    assert context.hard_constraints == ("do not modify files outside repo-a",)
    assert any("active_repository=repo-a" == item for item in context.project_state)
    assert context.evidence
    assert all(item.source_type == "provided_context" for item in context.evidence)
    assert all(item.confidence == 1.0 for item in context.evidence)


def test_compiler_does_not_turn_preferences_into_project_state() -> None:
    compiler = ProvidedContextCompiler(
        provider=lambda session_id: {
            "preferences": ["black and white UI"],
            "hard_constraints": ["no destructive actions"],
        }
    )

    context = compiler.compile(session_id="session-2", utterance="這個")

    assert context.project_state == ()
    assert context.preferences == ("black and white UI",)
    assert context.hard_constraints == ("no destructive actions",)
