from typing import List

from pydantic import Field

from scripts.models.relationship_pair_event.cat_enums import PairEventCatEnum
from scripts.models.text_pool_event.relationship_constraint_dict import (
    RelationshipConstraint,
)


class PairEventRelationshipConstraint(RelationshipConstraint):
    cats_from: List[PairEventCatEnum] = Field(
        ...,
        description="The cat from whom the relationship originates.",
    )
    cats_to: List[PairEventCatEnum] = Field(
        ...,
        description="The target of the relationship.",
    )
