from __future__ import annotations

from typing import List, Union

from pydantic import ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.relationship_group_event.involved_cats import InvolvedCatsGroupEvent
from scripts.models.relationship_group_event.relationship_change_dict import (
    GroupEventRelationshipChange,
)
from scripts.models.relationship_group_event.relationship_constraint_dict import (
    GroupEventRelationshipConstraint,
)
from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent


class RelationshipGroupEventSchemaItem(BaseTextPoolEvent):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(
        ...,
        description="Separates the events into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    involved_cats: Union[InvolvedCatsGroupEvent, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    relationship_constraint: Union[
        List[GroupEventRelationshipConstraint], MISSING
    ] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
    relationship_changes: Union[List[GroupEventRelationshipChange], MISSING] = Field(
        MISSING,
        description="Used to change specific relationships between the cats",
    )
