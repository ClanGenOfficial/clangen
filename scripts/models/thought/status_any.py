from __future__ import annotations

from typing import Union, Literal

from pydantic import RootModel

from scripts.models.common.status import Status


class StatusAny(RootModel):
    root: Union[Status, Literal["any"]]
