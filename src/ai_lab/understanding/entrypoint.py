from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .baseline import BaselineInterpreter, context_from_eval
from .llm import OpenAIAgentsInterpreter
from .models import ContextPack, UnderstandingResult
from .service import IntentInterpreter, UnderstandingService


@dataclass(frozen=True)
class MappingContextCompiler:
    """Compile a ContextPack from one utterance plus externally supplied state.

    M1 keeps context injection explicit: callers decide what state is available,
    while the understanding service owns interpretation, validation and policy.
    Persistent retrieval is introduced later in M2.
    """

    raw_context: Mapping[str, Any]

    def compile(self, *, session_id: str, utterance: str) -> ContextPack:
        return context_from_eval(
            session_id=session_id,
            utterance=utterance,
            raw=self.raw_context,
        )


def select_interpreter(*, prefer_cloud: bool = True) -> IntentInterpreter:
    """Select the best currently available interpreter without hiding fallback."""
    if prefer_cloud and os.getenv("OPENAI_API_KEY"):
        return OpenAIAgentsInterpreter()
    return BaselineInterpreter()


def understand_utterance(
    *,
    session_id: str,
    utterance: str,
    raw_context: Mapping[str, Any] | None = None,
    interpreter: IntentInterpreter | None = None,
) -> UnderstandingResult:
    """Canonical M1 entrypoint: language -> context -> contract -> policy decision."""
    service = UnderstandingService(
        context_compiler=MappingContextCompiler(raw_context or {}),
        interpreter=interpreter or select_interpreter(),
    )
    return service.understand(session_id=session_id, utterance=utterance)
