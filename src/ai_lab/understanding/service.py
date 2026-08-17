from __future__ import annotations

from typing import Protocol

from .models import ContextPack, IntentContract, UnderstandingResult
from .policy import AuthorizationContext, ClarificationPolicy


class ContextCompiler(Protocol):
    def compile(self, *, session_id: str, utterance: str) -> ContextPack: ...


class IntentInterpreter(Protocol):
    def interpret(self, *, context: ContextPack) -> IntentContract: ...


def _validate_grounding(*, context: ContextPack, contract: IntentContract) -> None:
    """Reject contracts that rewrite the request or invent supporting evidence."""
    if contract.literal_request != context.utterance:
        raise ValueError("intent contract must preserve the exact user utterance")

    available = {item.id for item in context.evidence}
    referenced = set(contract.evidence_ids)
    for assumption in contract.assumptions:
        referenced.update(assumption.evidence_ids)

    unknown = sorted(referenced - available)
    if unknown:
        raise ValueError(f"intent contract references unknown evidence ids: {unknown}")


class UnderstandingService:
    """Orchestrate context compilation, structured interpretation and policy."""

    def __init__(
        self,
        *,
        context_compiler: ContextCompiler,
        interpreter: IntentInterpreter,
        policy: ClarificationPolicy | None = None,
    ) -> None:
        self._context_compiler = context_compiler
        self._interpreter = interpreter
        self._policy = policy or ClarificationPolicy()

    def understand(
        self,
        *,
        session_id: str,
        utterance: str,
        authorization: AuthorizationContext | None = None,
    ) -> UnderstandingResult:
        if not utterance.strip():
            raise ValueError("utterance cannot be empty")

        context = self._context_compiler.compile(
            session_id=session_id,
            utterance=utterance,
        )
        contract = self._interpreter.interpret(context=context)
        _validate_grounding(context=context, contract=contract)
        decision = self._policy.decide(contract, authorization=authorization)
        return UnderstandingResult(
            context=context,
            contract=contract,
            decision=decision,
        )
