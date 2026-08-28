from typing import List, Union, Literal

from pydantic import Field
from pydantic_core import MISSING

from scripts.models.relationship_pair_event.cat_enums import PairEventCatEnum
from scripts.models.text_pool_event.relationship_change_dict import RelationshipChange


class PairEventRelationshipChange(RelationshipChange):
    cats_from: List[PairEventCatEnum] = Field(
        ...,
        description='The cat\'s whose relationship values are being edited. You are changing how the "cats_from" feels.',
    )
    cats_to: List[PairEventCatEnum] = Field(
        ...,
        description='The target of the relationship. You are changing how "cats_from" feels about "cats_to".',
    )
    log: Union[dict[Literal["cats_from", "cats_to"], str], MISSING] = MISSING
