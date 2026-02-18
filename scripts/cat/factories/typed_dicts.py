from typing import TypedDict, Optional, List, Dict


class GenderDict(TypedDict, total=False):
    sex: str
    genderalign: str
    pronouns: Optional[Dict]


class MentorshipDict(TypedDict):
    mentor: Optional[str]
    former_mentor: List[str]
    patrol_with_mentor: int
    apprentice: List[str]
    former_apprentices: List[str]


class CatTogglesDict(TypedDict):
    no_kits: bool
    no_mates: bool
    no_retire: bool
    prevent_fading: bool
    favourite: bool


class MateshipDict(TypedDict):
    mate: List[str]
    previous_mates: List[str]


class InheritanceDict(TypedDict):
    parent1: Optional[str]
    parent2: Optional[str]
    adoptive_parents: List[str]
    faded_offspring: List[str]
    mate: List[str]
    previous_mates: List[str]


class AfterlifeAffinityDict(TypedDict):
    starclan: int
    dark_forest: int
