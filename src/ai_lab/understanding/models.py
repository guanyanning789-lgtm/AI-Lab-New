from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Reversibility(str, Enum):
    REVERSIBLE = "reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"


class AutonomyMode(str, Enum):
    ADVISE = "advise"
    PREVIEW = "preview"
    EXECUTE = "execute"


class ClarificationAction(str, Enum):
    PROCEED = "proceed"
    PROCEED_WITH_ASSUMPTIONS = "proceed_with_assumptions"
    PREVIEW = "preview"
    ASK_ONE_QUESTION = "ask_one_question"
    REQUIRE_APPROVAL = "require_approval"


class EvidenceRef(StrictModel):
    id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    observed_at: datetime | None = None
    sensitivity: str = "normal"


class ContextConflict(StrictModel):
    topic: str = Field(min_length=1)
    evidence_ids: tuple[str, ...] = Field(min_length=2)
    summary: str = Field(min_length=1)


class ContextPack(StrictModel):
    session_id: str = Field(min_length=1)
    utterance: str = Field(min_length=1)
    conversation_summary: str = ""
    active_goal_id: str | None = None
    preferences: tuple[str, ...] = ()
    hard_constraints: tuple[str, ...] = ()
    project_state: tuple[str, ...] = ()
    relevant_memories: tuple[str, ...] = ()
    evidence: tuple[EvidenceRef, ...] = ()
    conflicts: tuple[ContextConflict, ...] = ()

    @model_validator(mode="after")
    def evidence_ids_are_unique(self) -> ContextPack:
        ids = [item.id for item in self.evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence ids must be unique")
        return self


class Assumption(StrictModel):
    statement: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    impact_if_wrong: RiskLevel = RiskLevel.LOW
    evidence_ids: tuple[str, ...] = ()


class SuccessCriterion(StrictModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    verification_method: str = Field(min_length=1)
    required: bool = True


class IntentContract(StrictModel):
    literal_request: str = Field(min_length=1)
    primary_goal: str = Field(min_length=1)
    inferred_need: str = Field(min_length=1)
    why_now: str = ""
    desired_outcome: str = Field(min_length=1)
    target_scope: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    preferences: tuple[str, ...] = ()
    non_goals: tuple[str, ...] = ()
    success_criteria: tuple[SuccessCriterion, ...] = Field(min_length=1)
    assumptions: tuple[Assumption, ...] = ()
    missing_information: tuple[str, ...] = ()
    risk_level: RiskLevel = RiskLevel.LOW
    reversibility: Reversibility = Reversibility.REVERSIBLE
    autonomy_mode: AutonomyMode = AutonomyMode.ADVISE
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def criterion_ids_are_unique(self) -> IntentContract:
        ids = [item.id for item in self.success_criteria]
        if len(ids) != len(set(ids)):
            raise ValueError("success criterion ids must be unique")
        return self


class ClarificationDecision(StrictModel):
    action: ClarificationAction
    reason: str = Field(min_length=1)
    question: str | None = None
    assumptions_to_surface: tuple[str, ...] = ()

    @model_validator(mode="after")
    def question_matches_action(self) -> ClarificationDecision:
        asks = self.action in {
            ClarificationAction.ASK_ONE_QUESTION,
            ClarificationAction.REQUIRE_APPROVAL,
        }
        if asks and not self.question:
            raise ValueError("a question is required for this action")
        if not asks and self.question is not None:
            raise ValueError("question must be empty when no user input is required")
        return self


class UnderstandingResult(StrictModel):
    context: ContextPack
    contract: IntentContract
    decision: ClarificationDecision
