from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.text_pool_event.cat_dict import CatDict


class InvolvedCatsCeremonyEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    m_c: Union[CatDict, MISSING] = MISSING
    past_deputy: Union[CatDict, MISSING] = MISSING
    r_c0: Union[CatDict, MISSING] = MISSING
    r_c1: Union[CatDict, MISSING] = MISSING
    r_c2: Union[CatDict, MISSING] = MISSING
    r_c3: Union[CatDict, MISSING] = MISSING
    r_c4: Union[CatDict, MISSING] = MISSING
    r_c5: Union[CatDict, MISSING] = MISSING
    n_c0: Union[CatDict, MISSING] = MISSING
    n_c1: Union[CatDict, MISSING] = MISSING
    n_c2: Union[CatDict, MISSING] = MISSING
    n_c3: Union[CatDict, MISSING] = MISSING
    n_c4: Union[CatDict, MISSING] = MISSING
    n_c5: Union[CatDict, MISSING] = MISSING
