from typing import TypedDict, Optional, List, Dict, Literal

from scripts.cat.enums import CatSocial, CatRank, CatAge


class AfterlifeAffinityDict(TypedDict):
    starclan: int
    dark_forest: int


class CatTogglesDict(TypedDict):
    no_kits: bool
    no_mates: bool
    no_retire: bool
    prevent_fading: bool
    favourite: bool


class GenderDict(TypedDict, total=False):
    sex: Literal["male", "female"]
    genderalign: str
    pronouns: Optional[Dict]


class InheritanceDict(TypedDict):
    parent1: Optional[str]
    parent2: Optional[str]
    adoptive_parents: List[str]
    faded_offspring: List[str]
    mate: List[str]
    previous_mates: List[str]


class MentorshipDict(TypedDict):
    mentor: Optional[str]
    former_mentor: List[str]
    patrol_with_mentor: int
    apprentice: List[str]
    former_apprentices: List[str]


class StatusDict(TypedDict, total=False):
    """
    Dict containing:

    "group_history": list[dict],
    "standing_history": list[dict],
    "social": CatSocial,
    "group": CatGroup
    "rank": CatRank
    "age": CatAge

    Dict does not need to contain all keys. However, if you have no group history, then you must include a rank or age
    """

    group_history: Optional[List[Dict]]
    standing_history: Optional[List[Dict]]
    social: Optional[CatSocial]
    group_ID: Optional[str]
    rank: Optional[CatRank]
    age: Optional[CatAge]
