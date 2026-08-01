from typing import TypedDict, NotRequired, Literal


class StandingDict(TypedDict):
    group: list[str]
    currently: NotRequired[list[str]]
    past: NotRequired[list[str]]


class StatDict(TypedDict, total=False):
    skill: list[str]
    trait: list[str]
    must_have_both: bool


class HealthDict(TypedDict, total=False):
    working: bool
    condition: list[str]
    must_be_congenital: bool
    must_be_acquired: bool


class CanCreateNewCatDict(TypedDict, total=False):
    become_litter: bool
    assign_blood_parent: list[str]
    assign_adoptive_parent: list[str]
    assign_mate: list[str]


class InvolvedCatDict(TypedDict, total=False):
    can_create_new_cat: CanCreateNewCatDict
    status: list[str]
    past_status: list[str]
    age: list[str]
    gender: Literal["male", "female", "can_birth"]
    group: list[str]
    standing: StandingDict
    stat: StatDict
    health: HealthDict
    backstory: list[str]


class RelationshipConstraintDict(TypedDict):
    cats_from: list[str]
    cats_to: list[str]
    mutual: bool
    constraints: list[str]


class RelationshipChangeDict(TypedDict):
    cats_from: list[str]
    cats_to: list[str]
    mutual: bool
    values: list[str]
    amount: int
