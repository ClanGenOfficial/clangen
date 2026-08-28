from typing import Union, List, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.excluded_illness import ExcludedIllness
from scripts.models.common.excluded_injury import ExcludedInjury
from scripts.models.common.excluded_perm_condition import ExcludedPermCondition
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition


class HealthDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    working: Union[bool, MISSING] = Field(
        MISSING,
        description="By default, this is always set to true. if set to false, the cat can't be a working cat (aka, they are currently disabled by a condition of some kind)",
    )
    condition: Union[
        List[
            Union[
                Injury,
                Illness,
                PermCondition,
                ExcludedInjury,
                ExcludedIllness,
                ExcludedPermCondition,
                Literal["any"],
            ]
        ],
        MISSING,
    ] = Field(
        MISSING,
        description='A list of conditions that the cat must have at least one of. if any condition is allowed, use "any"',
    )
    must_be_congenital: Union[bool, MISSING] = Field(
        MISSING,
        description="By default, this is always set to false. if set to true, the cat must have been born with a permanent condition listed in the condition",
    )
    must_be_acquired: Union[bool, MISSING] = Field(
        MISSING,
        description="By default, this is always set to false. if set to true, the cat must have acquired a permanent condition listed in condition later in life",
    )
