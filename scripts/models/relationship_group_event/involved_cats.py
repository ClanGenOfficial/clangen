from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.text_pool_event.cat_dict import CatDict


class InvolvedCatsGroupEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    m_c: Union[CatDict, MISSING] = MISSING
    r_c: Union[CatDict, MISSING] = MISSING
    r_c1: Union[CatDict, MISSING] = MISSING
    r_c2: Union[CatDict, MISSING] = MISSING
    r_c3: Union[CatDict, MISSING] = MISSING
    r_c4: Union[CatDict, MISSING] = MISSING
    r_c5: Union[CatDict, MISSING] = MISSING
    r_c6: Union[CatDict, MISSING] = MISSING
    multi_cat: Union[CatDict, MISSING] = MISSING
