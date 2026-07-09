from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.text_pool_event.cat_dict import CatDict


class InvolvedCatsPairEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    m_c: Union[CatDict, MISSING] = MISSING
    r_c: Union[CatDict, MISSING] = MISSING
