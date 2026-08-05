from typing import Union, List, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.age import Age
from scripts.models.common.backstory import Backstory
from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.group import Group
from scripts.models.text_pool_event.can_create_new_cat import CanCreateNewCat
from scripts.models.text_pool_event.health_dict import HealthDict
from scripts.models.text_pool_event.standing_dict import StandingDict
from scripts.models.text_pool_event.stat_dict import StatDict
from scripts.models.text_pool_event.status_any import StatusAny


class CatDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prior_abbreviation: Union[List[Union[GatherCat, Literal["any"]]], MISSING] = MISSING
    can_create_new_cat: Union[CanCreateNewCat, MISSING] = MISSING
    status: Union[List[StatusAny], MISSING] = MISSING
    past_status: Union[List[StatusAny], MISSING] = MISSING
    age: Union[List[Age], MISSING] = MISSING
    gender: Union[Literal["male", "female", "can_birth"], MISSING] = MISSING
    group: Union[List[Group], MISSING] = Field(MISSING, description="")
    standing: Union[StandingDict, MISSING] = Field(
        MISSING,
        description="Constrains the event to only happen if the cat matches with the dictated group standings. A group standing is the relationship between a cat and a group, for example: if they are an exile or lost",
    )
    stat: Union[StatDict, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat holds specific skills or traits. You can utilize exclusionary tags",
    )
    health: Union[HealthDict, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat's health matches the constraints",
    )
    backstory: Union[List[Backstory], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat has a listed backstory. To find what each backstory describes, you can find more by going to resources/lang/en/cat/backstories.en.json. You can utilize exclusionary tags",
    )
    has_mentor: Union[bool, MISSING] = Field(
        MISSING,
        description="Set True if the cat must be mentored. This does not require the mentor to be present on the patrol",
    )
