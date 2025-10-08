from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.common.new_cat import NewCat
from scripts.models.common.season import Season
from scripts.models.shortevent.event_subtype import EventSubtype
from scripts.models.shortevent.history_text import HistoryText
from scripts.models.shortevent.injury_item import InjuryItem
from scripts.models.shortevent.mc import MC
from scripts.models.shortevent.other_clan import OtherClan
from scripts.models.shortevent.outsider import Outsider
from scripts.models.shortevent.rc import RC
from scripts.models.shortevent.supply import Supply
from scripts.models.shortevent.tag import Tag


class ShortEventSchemaItem(BaseModel):
    event_id: Union[str, MISSING] = Field(
        MISSING, description="Unique string used to identify the event."
    )
    location: Union[List[str], MISSING] = Field(
        MISSING, description="Controls the biome and camp the event appears in."
    )
    season: Union[List[Season], MISSING] = Field(
        MISSING, description="List of seasons in which the event may occur."
    )
    sub_type: Union[List[EventSubtype], MISSING] = Field(
        MISSING, description="List of sub_types for this event."
    )
    tags: Union[
        List[Tag],
        MISSING,
    ] = Field(MISSING, description="Used for some filtering purposes")
    frequency: Union[int, MISSING] = Field(
        MISSING,
        description="Controls how common an event is. 4 == Common, 3 == Uncommon, 2 == Rare, 3 == Very Rare. Consider this in the terms of 'If an event of this type happened every moon for 10 moons, on how many of those moons should this sort of event appear?'",
    )
    event_text: Union[str, MISSING] = Field(
        MISSING,
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
    injury: Union[List[InjuryItem], MISSING] = MISSING
    history_text: Union[HistoryText, MISSING] = MISSING
    outsider: Union[Outsider, MISSING] = Field(
        MISSING,
        description="Dictates what reputation the clan is required to have with outsiders as well as how that reputation changes due to the event.",
    )
    other_clan: Union[OtherClan, MISSING] = Field(
        MISSING,
        description="Dictates what reputation the clan is required to have with the other clan as well as how that reputation changes due to the event.",
    )
    supplies: Union[List[Supply], MISSING] = MISSING
