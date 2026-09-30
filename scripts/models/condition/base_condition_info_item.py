from __future__ import annotations

from typing import Literal, Dict, List

from pydantic import Field, ConfigDict, BaseModel

from scripts.models.common.age import Age
from scripts.models.common.herb import Herb
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition
from scripts.models.common.scar import Scar
from scripts.models.condition.progression import ProgressionDict


class BaseConditionInfoSchemaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    severity: Literal["major", "minor", "severe"] = Field(
        description="Severity of the condition. For permanent conditions, major and severe conditions can cause the cat to retire early. For temporary conditions, major and minors conditions will prevent the cat from working."
    )
    mortality: Dict[Age, float] = Field(
        description="Percent chance for this condition to kill the cat. Can be left empty if the condition is not fatal."
    )
    immune_system_effect: float = Field(
        description="Effect on the percent chance that this cat will be infected by a different condition. This float will be added to the percent chance, thus increasing the cat's likely-hood to contract an infectious condition."
    )
    progression: Dict[Illness | Injury | PermCondition, ProgressionDict] = Field(
        description="The conditions that this condition can progress into (i.e. be replaced by). Can be left empty if the condition has no progressions."
    )
    risks: Dict[Illness | Injury | PermCondition, float] = Field(
        description="Extra conditions that can be gained while the cat has this condition. Float is the percentage chance to apply this condition."
    )
    treatment_strength: Dict[Literal["1", "2", "3"], List[Herb]] = Field(
        description="Lists of herbs that can be used for treatment of this condition. The 1, 2, 3 keys correspond to the strength of the herbs. Can be left empty if no herbs can be used to treat this condition."
    )
    possible_scars: List[Scar]
