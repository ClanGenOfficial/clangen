from __future__ import annotations

from typing import Dict, List, Tuple, Union

from pydantic import Field
from pydantic_core import MISSING

from scripts.models.common.min_max_status import MinMaxStatusDictKey
from scripts.models.common.temperament import Temperament
from scripts.models.patrol.involved_cats import InvolvedCatsPatrolEvent
from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent


class Outcome(BaseTextPoolEvent):
    frequency: int = Field(
        ...,
        description="Controls how common an outcome is. 4 is the most common, 1 is the least.",
        json_schema_extra={
            "default": 4
        },  # Necessary so that JSON Schema still shows a default without making the field optional
    )
    outcome_art: Union[str, MISSING] = Field(
        MISSING,
        description="The name of displayed patrol art file, without any file extension (no .png).",
    )
    outcome_art_clean: Union[str, MISSING] = Field(
        MISSING,
        description='If patrol_art contains gore, this line can hold a clean version. The existence of a non-empty string in this parameter marks the patrol art in "patrol_art" as explicit.',
    )
    involved_cats: Union[InvolvedCatsPatrolEvent, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    required_cat_types: Union[
        Dict[MinMaxStatusDictKey, Tuple[int, int]], MISSING
    ] = Field(
        MISSING,
        description="Allows specification of the minimum and maximum number of specific types of cats that are allowed on the patrol.",
    )
    patrol_temperament: Union[List[Temperament], MISSING] = Field(
        MISSING,
        description="Constrains the outcome to only occur if the patrol has one of these temperaments.",
    )
    exp_gained: int = Field(
        ...,
        description="The amount of exp cats receive (sorta). The exact amount also depends on the number of cats and current EXP levels, but in general, a higher number here means more exp. If exp is 0, no exp will be given",
    )
