from __future__ import annotations

from typing import List, Union

from pydantic import ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent
from scripts.models.thought.relationship_constraint_dict import (
    ThoughtRelationshipConstraint,
)
from scripts.thoughts.text_pool_event.involved_cats import InvolvedCats


class ThoughtSchemaItem(BaseTextPoolEvent):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(
        ...,
        description="Separates the thoughts into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    involved_cats: Union[InvolvedCats, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    relationship_constraint: Union[
        List[ThoughtRelationshipConstraint], MISSING
    ] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
