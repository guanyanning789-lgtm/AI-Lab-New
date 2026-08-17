from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from .models import ContextPack, EvidenceRef


ContextProvider = Callable[[str], Mapping[str, Any]]


def _summary(value: Any) -> str:
    if isinstance(value, Mapping):
        parts = [f"{key}={value[key]}" for key in sorted(value)]
        return ", ".join(parts)
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value)
    return str(value)


@dataclass(frozen=True)
class ProvidedContextCompiler:
    """Compile trusted session/project context into a grounded ContextPack.

    M1 deliberately starts with context supplied by deterministic providers.
    Persistent retrieval and ranking belong to later M1/M2 work; this compiler
    gives the understanding layer one production-shaped entrypoint now.
    """

    provider: ContextProvider

    def compile(self, *, session_id: str, utterance: str) -> ContextPack:
        raw = dict(self.provider(session_id))
        active_goal = raw.get("active_goal")
        active_goal_id: str | None = None
        if isinstance(active_goal, Mapping):
            value = active_goal.get("id")
            if value is not None:
                active_goal_id = str(value)

        preferences = tuple(str(item) for item in raw.get("preferences", ()) or ())
        hard_constraints = tuple(
            str(item) for item in raw.get("hard_constraints", ()) or ()
        )

        project_items = []
        evidence = []
        observed_at = datetime.now(timezone.utc)
        for index, (key, value) in enumerate(sorted(raw.items()), start=1):
            if key in {"preferences", "hard_constraints"}:
                continue
            rendered = _summary(value)
            project_items.append(f"{key}={rendered}")
            evidence.append(
                EvidenceRef(
                    id=f"ctx-{index}-{key}",
                    source_type="provided_context",
                    source_id=f"{session_id}:{key}",
                    summary=f"{key}: {rendered}",
                    confidence=1.0,
                    observed_at=observed_at,
                )
            )

        return ContextPack(
            session_id=session_id,
            utterance=utterance,
            active_goal_id=active_goal_id,
            preferences=preferences,
            hard_constraints=hard_constraints,
            project_state=tuple(project_items),
            evidence=tuple(evidence),
        )
