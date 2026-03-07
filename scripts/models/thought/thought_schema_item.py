from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.common.age import Age
from scripts.models.common.all_trait import AllTrait
from scripts.models.common.backstory import Backstory
from scripts.models.common.biome import Biome
from scripts.models.common.relationship_status import RelationshipStatus
from scripts.models.common.skill import Skill
from scripts.models.thought.camp import Camp
from scripts.models.thought.has_injuries import HasInjuries
from scripts.models.thought.perm_conditions import PermConditions
from scripts.models.thought.random_living_status import RandomLivingStatus
from scripts.models.thought.random_outside_status import RandomOutsideStatus
from scripts.models.thought.relationship_constraint import (
    RelationshipConstraint,
)
from scripts.models.thought.season import Season
from scripts.models.thought.status_any import StatusAny


class ThoughtSchemaItem(BaseModel):
    id: str = Field(
        ...,
        description="Separates the thoughts into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    biome: Union[List[Biome], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only occur if a player chooses a specific biome.",
    )
    season: Union[List[Season], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only occur once the Clan is in a specific season.",
    )
    camp: Union[List[Camp], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only occur if a specific camp type is chosen.",
    )
    thoughts: List[str] = Field(
        ..., description="List of the text that will be displayed in-game as thoughts."
    )
    has_injuries: Union[HasInjuries, MISSING] = Field(
        MISSING,
        description='Constrains the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain condition (either illness or injury). Can also use "any" to allow the thought to occur if the cat has any illness or injury.',
    )
    perm_conditions: Union[PermConditions, MISSING] = Field(
        MISSING,
        description='Constrains the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain permanent condition. Can also use "any" to allow the thought to occur if the cat has any permanent condition.',
    )
    relationship_status: Union[List[RelationshipStatus], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only occur if m_c and r_c fulfill the tag requirements.",
    )
    main_backstory_constraint: Union[List[Backstory], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only occur if m_c has a certain backstory.",
    )
    random_backstory_constraint: Union[List[Backstory], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only occur if r_c has a certain backstory.",
    )
    main_status_constraint: Union[List[StatusAny], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if m_c is in a certain role.",
    )
    random_status_constraint: Union[List[StatusAny], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if r_c is in a certain role.",
    )
    main_status_history: Union[List[StatusAny], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if m_c had a certain role, but no longer does.",
    )
    random_status_history: Union[List[StatusAny], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if r_c had a certain role, but no longer does.",
    )
    main_age_constraint: Union[List[Age], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if m_c is within a certain age group.",
    )
    random_age_constraint: Union[List[Age], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if r_c is within a certain age group.",
    )
    main_trait_constraint: Union[List[AllTrait], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if m_c has a specific trait.",
    )
    random_trait_constraint: Union[List[AllTrait], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if r_c has a specific trait.",
    )
    main_skill_constraint: Union[List[Skill], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if m_c has a specific skill.",
    )
    random_skill_constraint: Union[List[Skill], MISSING] = Field(
        MISSING,
        description="Constrains the thought to only happen if r_c has a specific skill.",
    )
    random_living_status: Union[List[RandomLivingStatus], MISSING] = Field(
        MISSING,
        description="Constrains the thought if r_c has a specific place of death.",
    )
    random_outside_status: Union[List[RandomOutsideStatus], MISSING] = Field(
        MISSING,
        description="Constrains the thought if r_c has a specific outside role.",
    )
