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


class MentorApprenticeDict(TypedDict, total=False):
    current: bool
    former: bool


class NameCheckDict(TypedDict):
    has_suffix: bool


class InvolvedCatDict(TypedDict, total=False):
    prior_abbreviation: list[str]
    can_create_new_cat: CanCreateNewCatDict
    status: list[str]
    past_status: list[str]
    age: list[str]
    gender: Literal["male", "female", "can_birth"]
    group: list[str]
    standing: StandingDict
    stat: StatDict
    current_exp: list[str]
    health: HealthDict
    backstory: list[str]
    has_mentor: MentorApprenticeDict
    has_apprentice: MentorApprenticeDict
    name: NameCheckDict


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
    log: dict[str, str]


class RequiredReputationDict(TypedDict, total=False):
    other_clan: list[Literal["ally", "neutral", "hostile"]]
    outsider: list[Literal["welcoming", "neutral", "hostile"]]


class ReputationChangesDict(TypedDict, total=False):
    other_clan: int
    outsider: int


class DeathDict(TypedDict):
    cats: list[str]
    body: NotRequired[bool]
    history: str
    no_results: NotRequired[bool]


class ConditionDict(TypedDict):
    cats: list[str]
    condition: list[str]
    no_results: NotRequired[bool]
    non_lethal: NotRequired[bool]
    scar_pool_override: NotRequired[list[str]]
    scar_history: NotRequired[str]
    death_history: NotRequired[str]


class LostDict(TypedDict):
    cats: list[str]
    # i know this feels unnecessary as a dict, but i'd like it to follow the structure of the other cat "consequences" (death/injury)
    # and eventually i think we should be dictating a history snippet for when cats get lost


class JoinDict(TypedDict):
    cats: list[str]
    change_name: NotRequired[bool]
    new_status: NotRequired[list[str]]


class SupplyDict(TypedDict):
    type: str
    trigger: NotRequired[Literal["always", "excess", "full", "adequate", "low"]]
    adjust: Literal[
        "increase_tiny",
        "increase_small",
        "increase_medium",
        "increase_large",
        "increase_huge",
    ]


class FutureEventDict(TypedDict):
    event_type: str
    pool: dict
    moon_delay: tuple[int, int]
    involved_cats: dict
