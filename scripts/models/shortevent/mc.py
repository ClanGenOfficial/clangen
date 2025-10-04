from __future__ import annotations

from typing import Optional, List, Union

from pydantic import BaseModel, Field

from scripts.cat.enums import CatAge
from scripts.models.common.all_trait import AllTrait
from scripts.models.common.backstory import Backstory
from scripts.models.common.relationship_status import (
    RelationshipStatus as McRelationshipStatus,
)
from scripts.models.common.skill import Skill
from scripts.models.common.status import Status


class MC(BaseModel):
    age: Optional[List[Union[CatAge, str]]] = Field(
        None, description='List of ages m_c can be. If they can be anything, use "any".'
    )
    status: Optional[List[Union[Status, str]]] = Field(
        None,
        description='List of statuses m_c can be. If they can be anything, use "any".',
    )
    relationship_status: Optional[List[McRelationshipStatus]] = Field(
        None,
        description="Dictates what relationships m_c must have towards r_c. Do not use this section if there is no r_c in the event.",
    )
    skill: Optional[List[Union[Skill, str]]] = Field(
        None,
        description='m_c must possess at least one skill from this list. If they can be anything, use "any".',
    )
    not_skill: Optional[List[Skill]] = Field(
        None, description="m_c cannot possess any of the skills on this list."
    )
    trait: Optional[List[Union[AllTrait, str]]] = Field(
        None,
        description='m_c must possess at least one trait from this list. If they can be anything, use "any".',
    )
    not_trait: Optional[List[AllTrait]] = Field(
        None, description="m_c cannot possess any of the traits on this list."
    )
    backstory: Optional[List[Backstory]] = Field(
        None, description="m_c must possess a backstory from this list."
    )
    dies: Optional[bool] = Field(
        False, description="m_c will die due to this event. Default is False."
    )
