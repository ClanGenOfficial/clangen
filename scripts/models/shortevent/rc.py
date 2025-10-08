from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.cat.enums import CatAge
from scripts.models.common.all_trait import AllTrait
from scripts.models.common.backstory import Backstory
from scripts.models.shortevent.rc_relationship_status import RcRelationshipStatus
from scripts.models.common.skill import Skill
from scripts.models.common.status import Status


class RC(BaseModel):
    age: List[CatAge | Literal["any"]] | MISSING = Field(
        MISSING,
        description='List of ages r_c can be. If they can be anything, use "any".',
    )
    status: List[Status | Literal["any"]] | MISSING = Field(
        MISSING,
        description='List of statuses r_c can be. If they can be anything, use "any".',
    )
    relationship_status: List[RcRelationshipStatus] | MISSING = Field(
        MISSING, description="Dictates what relationships r_c must have towards m_c."
    )
    skill: List[Skill | Literal["any"]] | MISSING = Field(
        MISSING,
        description='r_c must possess at least one skill from this list. If they can be anything, use "any".',
    )
    not_skill: List[Skill] | MISSING = Field(
        MISSING, description="r_c cannot possess any of the skills on this list."
    )
    trait: List[AllTrait | Literal["any"]] | MISSING = Field(
        MISSING,
        description='r_c must possess at least one trait from this list. If they can be anything, use "any".',
    )
    not_trait: List[AllTrait] | MISSING = Field(
        MISSING, description="r_c cannot possess any of the traits on this list."
    )
    backstory: List[Backstory] | MISSING = Field(
        MISSING, description="r_c must possess a backstory from this list."
    )
    dies: bool | MISSING = Field(
        MISSING, description="r_c will die due to this event. Default is False."
    )
