from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING
from scripts.models.common.biome import Biome
from scripts.models.common.min_max_status import MinMaxStatusDictKey
from scripts.models.common.relationship_status import RelationshipStatus
from scripts.models.common.season import Season
from scripts.models.common.skill import Skill
from scripts.models.patrol.outcome import Outcome
from scripts.models.patrol.patrol_tag import PatrolTag
from scripts.models.patrol.patrol_type import PatrolType


class PatrolSchemaItem(BaseModel):
    patrol_id: str = Field(
        ..., description="Unique string used to identify the patrol."
    )
    biome: List[Union[Biome, Literal["any"]]] = Field(
        ..., description="Controls the biome(s) the patrol appears in"
    )
    season: List[Season] = Field(
        ..., description="Controls the season(s) the patrol appears in."
    )
    types: List[PatrolType] = Field(..., description="Controls the type of patrol.")
    tags: List[PatrolTag] = Field(
        ...,
        description="Tags are used for some filtering purposes, and some odd-and-ends. Tags never affect outcome.",
    )
    patrol_art: Optional[str] = Field(
        ...,
        description="The name of displayed patrol art file, without any file extension (no .png).",
    )
    patrol_art_clean: Optional[str] = Field(
        None,
        description='If patrol_art contains gore, this line can hold a clean version. The existence of a non-empty string in this parameter marks the patrol art in "patrol_art" as explicit.',
    )
    min_cats: int = Field(
        ..., description="Minimum total number of cats for this patrol."
    )
    max_cats: int = Field(
        ..., description="Maximum total number of cats for this patrol"
    )
    min_max_status: Union[Dict[MinMaxStatusDictKey, Tuple[int, int]], MISSING] = Field(
        MISSING,
        description="Allows specification of the minimum and maximum number of specific types of cats that are allowed on the patrol.",
    )
    frequency: int = Field(
        ...,
        description="Controls how common a patrol is. 4 is the most common, 1 is the least.",
        json_schema_extra={
            "default": 4
        },  # Necessary so that JSON Schema still shows a default without making the field optional
    )
    chance_of_success: int = Field(
        ...,
        description="Controls chance to succeed. Higher number is higher chance to succeed.",
    )
    relationship_status: Union[List[RelationshipStatus], MISSING] = Field(
        MISSING,
        description="Dictates what relationships m_c must have towards r_c. Do not use this section if there is no r_c in the event.",
    )
    pl_skill_constraint: Union[List[Skill], MISSING] = Field(
        MISSING,
        description="Only allow this patrol if the patrol leader (p_l) meets at least one of these skill requirements.",
    )
    intro_text: str = Field(
        ..., description="The text that displays when the patrol first starts."
    )
    decline_text: str = Field(
        ...,
        description="The text that displays if the patrol is declined (do not proceed)",
    )
    success_outcomes: List[Outcome]
    fail_outcomes: List[Outcome]
    antag_success_outcomes: Union[List[Outcome], MISSING] = MISSING
    antag_fail_outcomes: List[Outcome] = MISSING
