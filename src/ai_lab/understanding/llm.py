from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol

from .models import ContextPack, IntentContract


SYSTEM_INSTRUCTIONS = """You are the semantic understanding layer of a personal AI OS.
Your only job is to infer the user's real intent from the supplied ContextPack.

Rules:
- Preserve literal_request exactly as the user's utterance.
- Ground claims in supplied context; do not invent history, preferences, files, people, or projects.
- Distinguish explicit user statements from assumptions.
- Prefer the smallest useful interpretation that satisfies the request.
- If one missing fact materially changes the result, put it in missing_information.
- Convert vague quality words into concrete desired outcomes and success criteria when context supports it.
- Do not grant yourself permission for risky or irreversible actions.
- Return only a valid IntentContract.
"""


class StructuredIntentModel(Protocol):
    def interpret(self, *, context: ContextPack) -> IntentContract: ...


@dataclass(frozen=True)
class OpenAIAgentsInterpreter:
    """Structured semantic interpreter using the OpenAI Agents SDK.

    The dependency is imported lazily so the core package and deterministic
    baseline remain usable without cloud dependencies or credentials.
    """

    model: str = "gpt-5.6"

    def interpret(self, *, context: ContextPack) -> IntentContract:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for OpenAIAgentsInterpreter")

        try:
            from agents import Agent, Runner
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise RuntimeError(
                "Install the optional cloud dependency with: pip install -e '.[cloud]'"
            ) from exc

        agent = Agent(
            name="AI Lab Understanding Kernel",
            instructions=SYSTEM_INSTRUCTIONS,
            model=self.model,
            output_type=IntentContract,
        )
        payload = json.dumps(context.model_dump(mode="json"), ensure_ascii=False, indent=2)
        result = Runner.run_sync(
            agent,
            "Interpret this ContextPack into the most faithful IntentContract:\n" + payload,
        )
        output = result.final_output
        if not isinstance(output, IntentContract):
            raise TypeError("structured model did not return IntentContract")
        return output
