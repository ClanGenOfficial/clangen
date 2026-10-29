from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.group import Group
from scripts.models.common.standing import Standing


class StandingDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group: Union[List[Group]] = Field(
        ...,
        description="the group we are checking the cat's standing with. you can utilize exclusionary tags. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to qualify against one of the groups. You should not try to tag no_group",
    )
    currently: Union[List[Standing], MISSING] = Field(
        MISSING,
        description="the standing the cat should currently possess with this group. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to have one of the standings",
    )
    past: Union[List[Standing], MISSING] = Field(
        MISSING,
        description="standings the cat used to have with this group. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to have had one of the standings",
    )
