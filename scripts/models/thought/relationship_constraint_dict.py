from typing import List

from pydantic import Field

from scripts.models.text_pool_event.relationship_constraint_dict import (
    RelationshipConstraint,
)
from scripts.models.thought.cat_enums import ThoughtCatEnum


class ThoughtRelationshipConstraint(RelationshipConstraint):
    cats_from: List[ThoughtCatEnum] = Field(
        ...,
        description="The cat from whom the relationship originates.",
    )
    cats_to: List[ThoughtCatEnum] = Field(
        ...,
        description="The target of the relationship.",
    )
