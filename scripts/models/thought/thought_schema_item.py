from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field

from scripts.cat.enums import CatAge
from scripts.models.common.all_trait import AllTrait
from scripts.models.common.backstory import Backstory
from scripts.models.thought.biome_enum import BiomeEnum
from scripts.models.thought.camp_enum import CampEnum
from scripts.models.thought.has_injuries import HasInjuries
from scripts.models.thought.perm_conditions import PermConditions
from scripts.models.thought.random_living_status import RandomLivingStatus
from scripts.models.thought.random_outside_status import RandomOutsideStatus
from scripts.models.thought.relationship_constraint_enum import (
    RelationshipConstraintEnum,
)
from scripts.models.thought.season_enum import SeasonEnum
from scripts.models.common.skill import Skill
from scripts.models.thought.status_any import StatusAny


class ThoughtSchemaItem(BaseModel):
    id: str = Field(
        ...,
        description="Separates the thoughts into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    biome: Optional[List[BiomeEnum]] = Field(
        None,
        description="Constrains the thought to only occur if a player chooses a specific biome.",
    )
    season: Optional[List[SeasonEnum]] = Field(
        None,
        description="Constrains the thought to only occur once the Clan is in a specific season.",
    )
    camp: Optional[List[CampEnum]] = Field(
        None,
        description="Constrains the thought to only occur if a specific camp type is chosen.",
    )
    thoughts: List[str] = Field(
        ..., description="List of the text that will be displayed in-game as thoughts."
    )
    has_injuries: Optional[HasInjuries] = Field(
        None,
        description='Constrains the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain condition (either illness or injury). Can also use "any" to allow the thought to occur if the cat has any illness or injury.',
    )
    perm_conditions: Optional[PermConditions] = Field(
        None,
        description='Constrains the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain permanent condition. Can also use "any" to allow the thought to occur if the cat has any permanent condition.',
    )
    relationship_constraint: Optional[List[RelationshipConstraintEnum]] = Field(
        None,
        description="Constrains the thought to only occur if m_c and r_c fulfill the tag requirements.",
    )
    main_backstory_constraint: Optional[List[Backstory]] = Field(
        None,
        description="Constrains the thought to only occur if m_c has a certain backstory.",
    )
    random_backstory_constraint: Optional[List[Backstory]] = Field(
        None,
        description="Constrains the thought to only occur if r_c has a certain backstory.",
    )
    main_status_constraint: Optional[List[StatusAny]] = Field(
        None,
        description="Constrains the thought to only happen if m_c is in a certain role.",
    )
    random_status_constraint: Optional[List[StatusAny]] = Field(
        None,
        description="Constrains the thought to only happen if r_c is in a certain role.",
    )
    main_age_constraint: Optional[List[CatAge]] = Field(
        None,
        description="Constrains the thought to only happen if m_c is within a certain age group.",
    )
    random_age_constraint: Optional[List[CatAge]] = Field(
        None,
        description="Constrains the thought to only happen if r_c is within a certain age group.",
    )
    main_trait_constraint: Optional[List[AllTrait]] = Field(
        None,
        description="Constrains the thought to only happen if m_c has a specific trait.",
    )
    random_trait_constraint: Optional[List[AllTrait]] = Field(
        None,
        description="Constrains the thought to only happen if r_c has a specific trait.",
    )
    main_skill_constraint: Optional[List[Skill]] = Field(
        None,
        description="Constrains the thought to only happen if m_c has a specific skill.",
    )
    random_skill_constraint: Optional[List[Skill]] = Field(
        None,
        description="Constrains the thought to only happen if r_c has a specific skill.",
    )
    random_living_status: Optional[List[RandomLivingStatus]] = Field(
        None, description="Constrains the thought if r_c has a specific place of death."
    )
    random_outside_status: Optional[List[RandomOutsideStatus]] = Field(
        None, description="Constrains the thought if r_c has a specific outside role."
    )
