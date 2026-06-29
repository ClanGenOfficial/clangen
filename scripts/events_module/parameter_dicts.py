from typing import TypedDict, NotRequired, Literal


class StandingDict(TypedDict):
    group: list[str]
    currently: list[str]
    past: list[str]


class StatDict(TypedDict, total=False):
    skill: list[str]
    trait: list[str]
    must_have_both: bool


class HealthDict(TypedDict, total=False):
    working: bool
    condition: list[str]
    must_be_congenital: bool
    must_be_acquired: bool


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


class RelationshipChangeDict(TypedDict):
    cats_from: list[str]
    cats_to: list[str]
    mutual: bool
    values: list[str]
    amount: int


class RequiredReputationDict(TypedDict, total=False):
    other_clan: Literal["ally", "neutral", "enemy"]
    outsider: Literal["welcoming", "neutral", "hostile"]


class ReputationChangesDict(TypedDict, total=False):
    other_clan: int
    outsider: int


class DeathDict(TypedDict):
    cats: list[str]
    history: str


class InjuryDict(TypedDict):
    cats: list[str]
    injury: list[str]
    scar_pool_override: NotRequired[list[str]]
    scar_history: NotRequired[str]
    death_history: NotRequired[str]


class LostDict(TypedDict):
    cats: list[str]


class SupplyDict(TypedDict):
    type: str
    trigger: Literal["always", "excess", "full", "adequate", "low"]
    adjust: Literal[
        "reduce_eighth",
        "reduce_quarter",
        "reduce_half",
        "reduce_full",
        "increase_tiny",
        "increase_small",
        "increase_medium",
        "increase_large",
        "increase_huge"
    ]
