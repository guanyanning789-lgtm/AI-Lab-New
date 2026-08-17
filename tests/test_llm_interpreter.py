import os

import pytest

from ai_lab.understanding.llm import OpenAIAgentsInterpreter
from ai_lab.understanding.models import ContextPack


def test_llm_interpreter_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    interpreter = OpenAIAgentsInterpreter()
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        interpreter.interpret(
            context=ContextPack(session_id="s1", utterance="繼續")
        )


def test_default_model_name_is_explicit() -> None:
    assert OpenAIAgentsInterpreter().model == "gpt-5.6"
