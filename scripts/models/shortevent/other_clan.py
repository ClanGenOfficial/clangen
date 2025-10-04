from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field

from scripts.models.shortevent.other_clan_rep_enum import OtherClanRepEnum


class OtherClan(BaseModel):
    current_rep: Optional[List[OtherClanRepEnum]] = Field(
        None,
        description="The reputation the Clan must have in order for this event to be possible.",
    )
    changed: Optional[int] = Field(
        None,
        description="How the reputation of the Clan changes as a result of this event",
    )
