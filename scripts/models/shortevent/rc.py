from __future__ import annotations

from typing import List, Literal, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.common.age import Age
from scripts.models.common.all_trait import AllTrait
from scripts.models.common.backstory import Backstory
from scripts.models.common.skill import Skill
from scripts.models.common.status import Status
from scripts.models.shortevent.rc_relationship_status import RcRelationshipStatus


class RC(BaseModel):
    age: Union[List[Union[Age, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='List of ages r_c can be. If they can be anything, use "any".',
    )
    status: Union[List[Union[Status, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='List of statuses r_c can be. If they can be anything, use "any".',
    )
    relationship_status: Union[List[RcRelationshipStatus], MISSING] = Field(
        MISSING, description="Dictates what relationships r_c must have towards m_c."
    )
    skill: Union[List[Union[Skill, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='r_c must possess at least one skill from this list. If they can be anything, use "any".',
    )
    trait: Union[List[Union[AllTrait, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='r_c must possess at least one trait from this list. If they can be anything, use "any".',
    )
    backstory: Union[List[Backstory], MISSING] = Field(
        MISSING, description="r_c must possess a backstory from this list."
    )
    dies: Union[bool, MISSING] = Field(
        MISSING, description="r_c will die due to this event. Default is False."
    )
