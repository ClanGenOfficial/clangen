from enum import Enum
from typing import Union, Annotated

from pydantic import StringConstraints, RootModel


class GatherCatEnum(Enum):
    m_c = "m_c"
    r_c = "r_c"
    p_l = "p_l"
    s_c = "s_c"
    app1 = "app1"
    app2 = "app2"
    app3 = "app3"
    app4 = "app4"
    app5 = "app5"
    app6 = "app6"
    clan = "clan"
    some_clan = "some_clan"
    patrol = "patrol"
    multi = "multi"
    high_lawful = "high_lawful"
    low_lawful = "low_lawful"
    high_social = "high_social"
    low_social = "low_social"
    high_stable = "high_stable"
    low_stable = "low_stable"
    high_aggress = "high_aggress"
    low_aggress = "low_aggress"


class GatherCat(RootModel):
    root: Union[
        GatherCatEnum, Annotated[str, StringConstraints(pattern=r"^n_c:[0-9]+$")]
    ]
