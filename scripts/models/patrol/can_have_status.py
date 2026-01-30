from __future__ import annotations

from enum import Enum


class CanHaveStat(Enum):
    p_l = "p_l"
    r_c = "r_c"
    app1 = "app1"
    app2 = "app2"
    not_pl = "not_pl"
    not_rc = "not_rc"
    not_pl_rc = "not_pl_rc"
    any = "any"
    adult = "adult"
    app = "app"
    healer = "healer"
