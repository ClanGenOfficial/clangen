from typing import List, Union, Literal

from pydantic import Field
from pydantic_core import MISSING

from scripts.models.relationship_group_event.cat_enums import GroupEventCatEnum
from scripts.models.text_pool_event.relationship_change_dict import RelationshipChange


class GroupEventRelationshipChange(RelationshipChange):
    cats_from: List[GroupEventCatEnum] = Field(
        ...,
        description='The cat\'s whose relationship values are being edited. You are changing how the "cats_from" feels.',
    )
    cats_to: List[GroupEventCatEnum] = Field(
        ...,
        description='The target of the relationship. You are changing how "cats_from" feels about "cats_to".',
    )
    log: Union[dict[Literal["cats_from", "cats_to"], str], MISSING] = MISSING
