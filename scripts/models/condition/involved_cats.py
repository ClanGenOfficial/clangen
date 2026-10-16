from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.text_pool_event.cat_dict import CatDict


class InvolvedCatsConditionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    m_c: CatDict | MISSING = MISSING
    multi_cat: CatDict | MISSING = MISSING
    r_c0: CatDict | MISSING = MISSING
    r_c1: CatDict | MISSING = MISSING
    r_c2: CatDict | MISSING = MISSING
    r_c3: CatDict | MISSING = MISSING
    r_c4: CatDict | MISSING = MISSING
    r_c5: CatDict | MISSING = MISSING
