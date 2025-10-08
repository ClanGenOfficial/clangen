from __future__ import annotations

from typing import Union, Literal

from pydantic import RootModel

from scripts.models.common.perm_condition import PermCondition


class PermConditionAny(RootModel):
    root: Union[PermCondition, Literal["any"]]
