from __future__ import annotations

from typing import Annotated, List, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pydantic_core import MISSING

from scripts.models.common.biome import Biome
from scripts.models.common.new_cat import NewCat
from scripts.models.common.season import Season
from scripts.models.shortevent.event_subtype import EventSubtype
from scripts.models.shortevent.gender import NewGenderEnum
from scripts.models.shortevent.history_text import HistoryText
from scripts.models.shortevent.injury_item import InjuryItem
from scripts.models.shortevent.location import Location
from scripts.models.shortevent.mc import MC
from scripts.models.shortevent.other_clan import OtherClan
from scripts.models.shortevent.outsider import Outsider
from scripts.models.shortevent.rc import RC
from scripts.models.shortevent.supply import Supply
from scripts.models.shortevent.tag import Tag
from scripts.models.shortevent.cat import Cat
from scripts.models.common.relationship import Relationship
from scripts.models.common.future_event import FutureEvent


class ShortEventSchemaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(..., description="Unique string used to identify the event.")
    location: Location = Field(
        ..., description="Controls the biome and camp the event appears in."
    )
    season: List[Season] = Field(
        ..., description="List of seasons in which the event may occur."
    )
    sub_type: Union[List[EventSubtype], MISSING] = Field(
        MISSING, description="List of sub_types for this event."
    )
    tags: Union[
        List[Tag],
        MISSING,
    ] = Field(MISSING, description="Used for some filtering purposes")
    frequency: int = Field(
        ...,
        description="Controls how common an event is. 4 == Common, 3 == Uncommon, 2 == Rare, 3 == Very Rare. Consider this in the terms of 'If an event of this type happened every moon for 10 moons, on how many of those moons should this sort of event appear?'",
    )
    event_text: str = Field(
        ...,
        description="Text that appears within the event list when the event occurs.",
    )
    new_accessory: Union[List[str], MISSING] = Field(
        MISSING,
        description="If the event gives a new accessory, list possible new accessories here (one will be chosen from the list)",
    )
    m_c: Union[MC, MISSING] = Field(
        MISSING,
        description="Specifies the requirements for the main cat (m_c) of the event.",
    )
    r_c: Union[RC, MISSING] = Field(
        MISSING,
        description="Specifies the requirements for the random cat (r_c) of the event.",
    )
    new_cat: Union[List[NewCat], MISSING] = Field(
        MISSING, description="Adds a new cat."
    )
    injury: Union[List[InjuryItem], MISSING] = Field(
        MISSING, description="Indicates which cats get injured, and how."
    )
    history: Union[List[HistoryText], MISSING] = Field(
        MISSING, description="Controls the history-text for scars and death."
    )
    relationships: Union[List[Relationship], MISSING] = Field(
        MISSING, description="Indicates effect on cat relationships."
    )
    exclude_involved: Union[List[Cat], MISSING] = Field(
        MISSING,
        description='Excludes certain cats from showing up in the "involved cats" list of the event, meaning their button will not be present on the events screen.',
    )
    new_gender: Union[List[NewGenderEnum], MISSING] = Field(
        MISSING,
        description="New gender for cats who are transitioning.",
    )
    future_event: Union[List[FutureEvent], MISSING] = Field(
        MISSING, description="Schedules another event to happen in the future."
    )
    outsider: Union[Outsider, MISSING] = Field(
        MISSING,
        description="Dictates what reputation the clan is required to have with outsiders as well as how that reputation changes due to the event.",
    )
    other_clan: Union[OtherClan, MISSING] = Field(
        MISSING,
        description="Dictates what reputation the clan is required to have with the other clan as well as how that reputation changes due to the event.",
    )
    supplies: Union[List[Supply], MISSING] = Field(
        MISSING,
        description="Dictates how this event changes the various supply pools of the clan.",
    )
