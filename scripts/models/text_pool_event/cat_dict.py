from typing import Union, List, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.age import Age
from scripts.models.common.backstory import Backstory
from scripts.models.common.experience_levels import ExperienceLevels
from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.group import Group
from scripts.models.text_pool_event.mentor_apprentice_dict import MentorApprenticeDict
from scripts.models.text_pool_event.can_create_new_cat import CanCreateNewCat
from scripts.models.text_pool_event.health_dict import HealthDict
from scripts.models.text_pool_event.name_check_dict import NameCheckDict
from scripts.models.text_pool_event.standing_dict import StandingDict
from scripts.models.text_pool_event.stat_dict import StatDict
from scripts.models.text_pool_event.status_any import StatusAny


class CatDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prior_abbreviation: Union[List[Union[GatherCat, Literal["any"]]], MISSING] = Field(
        MISSING,
        description="Specifies s_c choices. Read the docs. It's too long for this.",
    )
    can_create_new_cat: Union[CanCreateNewCat, MISSING] = Field(
        MISSING,
        description="Add if the outsider/other_clan cat can be newly generated rather than having to utilize an existing cat. Can even be added as an empty dict to simply mark it as a new cat creation without any additional specifications",
    )
    status: Union[List[StatusAny], MISSING] = Field(
        MISSING,
        description='Constrains the event to only happen if the cat holds a certain role. You can utilize exclusionary tags. You can also remove the parameter to allow the event to occur for all roles except "newborns", who are only allowed if specifically tagged as such.',
    )
    past_status: Union[List[StatusAny], MISSING] = Field(
        MISSING,
        description="Constrains the event to only happen if the cat held a certain role in the past",
    )
    age: Union[List[Age], MISSING] = Field(
        MISSING,
        description='Constrains the event to only occur if the cat is within a certain age group. You can also remove the parameter to allow the event to occur for all ages except "newborns", who are only allowed if specifically tagged as such',
    )
    gender: Union[Literal["male", "female", "can_birth"], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat has a certain birth gender. can_birth will allow either female or male cats dependant upon the player's settings",
    )
    group: Union[List[Group], MISSING] = Field(
        MISSING,
        description="Constraints the thought to only happen if the cat is a member of a listed group or a member of no group. This should only be used to dictate what group a new cat is originally part of",
    )
    standing: Union[StandingDict, MISSING] = Field(
        MISSING,
        description="Constrains the event to only happen if the cat matches with the dictated group standings. A group standing is the relationship between a cat and a group, for example: if they are an exile or lost",
    )
    stat: Union[StatDict, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat holds specific skills or traits. You can utilize exclusionary tags",
    )
    current_exp: Union[list[ExperienceLevels], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat has a listed experience level",
    )
    health: Union[HealthDict, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat's health matches the constraints",
    )
    backstory: Union[List[Backstory], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the cat has a listed backstory. To find what each backstory describes, you can find more by going to resources/lang/en/cat/backstories.en.json. You can utilize exclusionary tags",
    )
    has_mentor: Union[MentorApprenticeDict, MISSING] = Field(
        MISSING,
        description="Set current mentor status",
    )
    has_apprentice: Union[MentorApprenticeDict, MISSING] = Field(
        MISSING,
        description="Set current apprentice status",
    )
    name: Union[NameCheckDict, MISSING] = Field(
        MISSING,
        description="Constrain per specific name states",
    )
