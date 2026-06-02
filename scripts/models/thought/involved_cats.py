from typing import Union

from pydantic import BaseModel
from pydantic_core import MISSING

from scripts.models.thought.cat_dict import CatDict


class InvolvedCats(BaseModel):
    m_c: Union[CatDict, MISSING] = MISSING
    r_c: Union[CatDict, MISSING] = MISSING
