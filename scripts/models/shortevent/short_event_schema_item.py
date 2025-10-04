from __future__ import annotations

from typing import Optional, List, Union, Annotated

from pydantic import BaseModel, Field, StringConstraints

from scripts.models.common.season import SeasonEnum
from scripts.models.shortevent.history_text import HistoryText
from scripts.models.shortevent.injury_item import InjuryItem
from scripts.models.shortevent.mc import MC
from scripts.models.common.new_cat import NewCat
from scripts.models.shortevent.other_clan import OtherClan
from scripts.models.shortevent.outsider import Outsider
from scripts.models.shortevent.rc import RC
from scripts.models.shortevent.event_sub_type_enum import EventSubTypeEnum
from scripts.models.shortevent.supply import Supply
from scripts.models.shortevent.tags import Tags


class ShortEventSchemaItem(BaseModel):
    event_id: Optional[str] = Field(
        None, description="Unique string used to identify the event."
    )
    location: Optional[List[str]] = Field(
        None, description="Controls the biome and camp the event appears in."
    )
    season: Optional[List[SeasonEnum]] = Field(
        None, description="List of seasons in which the event may occur."
    )
    sub_type: Optional[List[EventSubTypeEnum]] = Field(
        None, description="List of sub_types for this event."
    )
    tags: Optional[
        List[Union[Tags, Annotated[str, StringConstraints(pattern=r"^clan:(.+)$")]]]
    ] = Field(None, description="Used for some filtering purposes")
    frequency: Optional[int] = Field(
        None,
        description="Controls how common an event is. 4 == Common, 3 == Uncommon, 2 == Rare, 3 == Very Rare. Consider this in the terms of 'If an event of this type happened every moon for 10 moons, on how many of those moons should this sort of event appear?'",
    )
    event_text: Optional[str] = Field(
        None,
        description="Text that appears within the event list when the event occurs.",
    )
    new_accessory: Optional[List[str]] = Field(
        None,
        description="If the event gives a new accessory, list possible new accessories here (one will be chosen from the list)",
    )
    m_c: Optional[MC] = Field(
        None,
        description="Specifies the requirements for the main cat (m_c) of the event.",
    )
    r_c: Optional[RC] = Field(
        None,
        description="Specifies the requirements for the random cat (r_c) of the event.",
    )
    new_cat: Optional[List[NewCat]] = Field(None, description="Adds a new cat.")
    injury: Optional[List[InjuryItem]] = None
    history_text: Optional[HistoryText] = None
    outsider: Optional[Outsider] = Field(
        None,
        description="Dictates what reputation the clan is required to have with outsiders as well as how that reputation changes due to the event.",
    )
    other_clan: Optional[OtherClan] = Field(
        None,
        description="Dictates what reputation the clan is required to have with the other clan as well as how that reputation changes due to the event.",
    )
    supplies: Optional[List[Supply]] = None
