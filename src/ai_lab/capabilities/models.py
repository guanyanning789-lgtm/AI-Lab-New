from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SideEffectLevel(str, Enum):
    NONE = "none"
    REVERSIBLE_WRITE = "reversible_write"
    EXTERNAL_EFFECT = "external_effect"
    IRREVERSIBLE = "irreversible"


class CapabilityManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    input_schema_ref: str = Field(min_length=1)
    output_schema_ref: str = Field(min_length=1)
    required_permissions: tuple[str, ...] = ()
    side_effect_level: SideEffectLevel = SideEffectLevel.NONE
    verifier: str = Field(min_length=1)
    rollback_supported: bool = False
