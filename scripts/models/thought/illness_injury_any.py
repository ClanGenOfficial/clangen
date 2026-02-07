from __future__ import annotations

from typing import Union, Literal

from pydantic import RootModel

from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury


class IllnessInjuryAny(RootModel):
    root: Union[Illness, Injury, Literal["any"]]
