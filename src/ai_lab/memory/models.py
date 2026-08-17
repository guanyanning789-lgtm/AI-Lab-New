from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MemoryKind(str, Enum):
    PROFILE = "profile"
    PREFERENCE = "preference"
    PROJECT_STATE = "project_state"
    EPISODE = "episode"
    PROCEDURE = "procedure"
    CORRECTION = "correction"
    COMMITMENT = "commitment"


class MemoryStatus(str, Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


class SourceAuthority(str, Enum):
    USER_CONFIRMED = "user_confirmed"
    USER_STATED = "user_stated"
    SYSTEM_OBSERVED = "system_observed"
    MODEL_INFERRED = "model_inferred"


class MemoryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    kind: MemoryKind
    subject: str = Field(min_length=1)
    payload: dict[str, Any]
    source_event_id: str = Field(min_length=1)
    source_authority: SourceAuthority
    confidence: float = Field(ge=0.0, le=1.0)
    status: MemoryStatus = MemoryStatus.PROPOSED
    sensitivity: str = "normal"
    valid_from: datetime
    valid_to: datetime | None = None
    supersedes_id: str | None = None
