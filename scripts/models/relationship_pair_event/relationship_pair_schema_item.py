from __future__ import annotations

from typing import List, Union

from pydantic import ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.relationship_pair_event.involved_cats import InvolvedCatsPairEvent
from scripts.models.relationship_pair_event.relationship_change_dict import (
    PairEventRelationshipChange,
)
from scripts.models.relationship_pair_event.relationship_constraint_dict import (
    PairEventRelationshipConstraint,
)
from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent


class RelationshipPairEventSchemaItem(BaseTextPoolEvent):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(
        ...,
        description="Separates the events into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    involved_cats: Union[InvolvedCatsPairEvent, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    relationship_constraint: Union[
        List[PairEventRelationshipConstraint], MISSING
    ] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
    relationship_changes: Union[List[PairEventRelationshipChange], MISSING] = Field(
        MISSING,
        description="Used to change specific relationships between the cats",
    )
