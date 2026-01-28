"""
Aggregation schema for all common models.
This file imports all common models for schema generation purposes.
"""

from pydantic import BaseModel

from scripts.models.common.all_trait import AllTrait
from scripts.models.common.backstory import Backstory
from scripts.models.common.gather_cat import GatherCat, GatherCatEnum
from scripts.models.common.herb import Herb
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.kit_trait import KitTrait
from scripts.models.common.new_cat import NewCat, NewCatTag
from scripts.models.common.perm_condition import PermCondition
from scripts.models.common.relationship_status import RelationshipStatus
from scripts.models.common.scar import Scar
from scripts.models.common.season import Season
from scripts.models.common.skill import Skill
from scripts.models.common.status import Status
from scripts.models.common.trait import Trait


class CommonSchema(BaseModel):
    """Helper model to generate $defs for all common types."""

    all_trait: AllTrait
    backstory: Backstory
    gather_cat: GatherCat
    gather_cat_enum: GatherCatEnum
    herb: Herb
    illness: Illness
    injury: Injury
    kit_trait: KitTrait
    new_cat: NewCat
    new_cat_tag: NewCatTag
    perm_condition: PermCondition
    relationship_status: RelationshipStatus
    scar: Scar
    season_enum: Season
    skill: Skill
    status: Status
    trait: Trait
