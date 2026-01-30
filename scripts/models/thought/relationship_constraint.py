from __future__ import annotations

from enum import Enum


class RelationshipConstraint(Enum):
    siblings = "siblings"
    not_siblings = "not_siblings"
    littermates = "littermates"
    not_littermates = "not_littermates"
    mates = "mates"
    mates_with_pl = "mates_with_pl"
    not_mates = "not_mates"
    parent_child = "parent/child"
    not_parent = "not_parent"
    child_parent = "child/parent"
    not_child = "not_child"
    mentor_app = "mentor/app"
    not_mentor = "not_mentor"
    app_mentor = "app/mentor"
    not_app = "not_app"
    strangers = "strangers"
