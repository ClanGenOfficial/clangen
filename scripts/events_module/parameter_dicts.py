from typing import TypedDict, NotRequired


class StandingDict(TypedDict):
    group: list[str]
    currently: list[str]
    past: list[str]


class StatDict(TypedDict):
    skill: list[str]
    trait: list[str]
    must_have_both: bool


class HealthDict(TypedDict):
    working: bool
    condition: list[str]
    must_be_congenital: NotRequired[bool]
    must_be_acquired: NotRequired[bool]


class InvolvedCatDict(TypedDict):
    status: NotRequired[list[str]]
    past_status: NotRequired[list[str]]
    age: NotRequired[list[str]]
    group: NotRequired[list[str]]
    standing: NotRequired[StandingDict]
    stat: NotRequired[StatDict]
    health: NotRequired[HealthDict]
    backstory: NotRequired[list[str]]


class RelationshipConstraintDict(TypedDict):
    cats_from: list[str]
    cats_to: list[str]
    mutual: bool
    constraints: list[str]
