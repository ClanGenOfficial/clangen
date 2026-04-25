from __future__ import annotations

from enum import Enum
from typing import List, Union, Literal, Tuple

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING
from scripts.models.common.age import Age
from scripts.models.common.all_trait import AllTrait
from scripts.models.common.skill import Skill
from scripts.models.common.status import Status

from scripts.models.shortevent.event_subtype import EventSubtype
from scripts.models.shortevent.cat import Cat
from scripts.models.shortevent.gender import GenderEnum


class EventType(Enum):
    death = "death"
    injury = "injury"
    new_cat = "new_cat"
    misc = "misc"


class FutureEventPool(BaseModel):
    subtype: Union[List[EventSubtype], MISSING] = Field(
        MISSING,
        description="Events to be added to the pool will contain all subtypes specified.",
    )
    event_id: Union[List[str], MISSING] = Field(
        MISSING,
        description="Only events with the specified event_ids will be added to the pool.",
    )
    excluded_event_id: Union[List[str], MISSING] = Field(
        MISSING,
        description="All events with the specified event_ids will be removed from the pool.",
    )


class FutureCat(BaseModel):
    age: Union[List[Union[Age, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='List of ages the cat can be. If they can be anything, use "any".',
    )
    status: Union[List[Union[Status, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='List of statuses the cat can be. If they can be anything, use "any".',
    )
    skill: Union[List[Union[Skill, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='The cat must possess at least one skill from this list. If they can be anything, use "any".',
    )
    trait: Union[List[Union[AllTrait, Literal["any"]]], MISSING] = Field(
        MISSING,
        description='The cat must possess at least one trait from this list. If they can be anything, use "any".',
    )
    gender: Union[List[GenderEnum], MISSING] = Field(
        MISSING, description="The cat will have this gender."
    )


class FutureEventInvolvedCats(BaseModel):
    model_config = ConfigDict(extra="forbid")
    m_c: Union[FutureCat, Cat, MISSING] = Field(
        MISSING,
        title="Main Cat",
        description="m_c in the future event. Can either be a cat in the current event or constraints for a newly chosen cat.",
    )
    mur_c: Union[FutureCat, Cat, MISSING] = Field(
        MISSING,
        title="Murdered Cat",
        description="The murdered cat in the future event. Can either be a cat in the current event or constraints for a newly chosen cat.",
    )
    r_c: Union[FutureCat, Cat, MISSING] = Field(
        MISSING,
        title="Random Cat",
        description="r_c in the future event. Can either be a cat in the current event or constraints for a newly chosen cat.",
    )


class FutureEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: EventType = Field(
        description="Specify which ShortEvent type the future event will be."
    )
    moon_delay: Tuple[int, int] = Field(
        description="How many moons must pass before the first event appears (inclusive). The first value is the smallest possible delay and the second value is the largest."
    )
    pool: FutureEventPool = Field(
        description="Pool of events to be chosen from. Only one event from the pool will be chosen."
    )
    involved_cats: FutureEventInvolvedCats = Field(
        description="Specifies which cats can fill the roles within the future event."
    )
