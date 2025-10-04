from __future__ import annotations

from typing import Union

from pydantic import RootModel

from scripts.models.common.status import Status


class StatusAny(RootModel):
    root: Union[Status, str]
