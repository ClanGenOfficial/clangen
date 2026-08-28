from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.future_event import FutureEvent
from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.location import Location
from scripts.models.common.season import Season
from scripts.models.common.tag import Tag
from scripts.models.common.temperament import Temperament
from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent
from scripts.models.text_pool_event.condition import Condition
from scripts.models.text_pool_event.death import Death
from scripts.models.text_pool_event.join import Join
from scripts.models.text_pool_event.supply import Supply
from scripts.models.text_pool_event.gain_accessory import GainAccessory
from scripts.models.text_pool_event.relationship_change_dict import RelationshipChange
from scripts.models.text_pool_event.relationship_constraint_dict import (
    RelationshipConstraint,
)
from scripts.models.transition.involved_cats import InvolvedCatsTransitionEvent


class TransitionSchemaItem(BaseTextPoolEvent):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(
        ...,
        description="Separates the events into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    frequency: int = Field(
        ...,
        description="Controls how common an event is. 4 is the most common, 1 is the least.",
        json_schema_extra={
            "default": 4
        },  # Necessary so that JSON Schema still shows a default without making the field optional
    )
    involved_cats: InvolvedCatsTransitionEvent | MISSING = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    new_gender: List[
        Literal["trans male", "trans female", "nonbinary"]
    ] | MISSING = Field(
        MISSING, description="Determines what gender the primary cat is becoming."
    )
