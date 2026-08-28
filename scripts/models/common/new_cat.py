from enum import Enum
from typing import List, Union, Annotated
import re

from pydantic import AfterValidator, StringConstraints, RootModel

from scripts.models.common.backstory import Backstory
from scripts.models.common.status import Status


def validate_nc_backstories(value: str) -> str:
    backstories = [b.value for b in Backstory if not b.value.startswith("-")]
    _, backstory_str = value.split(":")

    chosen_backstories = re.split(r", ?", backstory_str)
    for chosen_backstory in chosen_backstories:
        if chosen_backstory.strip() not in backstories:
            raise ValueError(f"Backstory {chosen_backstory} in {value} is invalid!")
    return value


def validate_nc_status(value: str) -> str:
    statuses = [
        s.value
        for s in Status
        if not s.value.startswith("-") or s.value not in ("leader", "deputy")
    ]
    _, status_str = value.split(":")

    if status_str not in statuses:
        raise ValueError(f"Status {status_str} in {value} is invalid!")
    return value


def validate_nc_age(value: str) -> str:
    ages = [
        "newborn",
        "kitten",
        "adolescent",
        "young adult",
        "adult",
        "senior adult",
        "senior",
        "mate",
        "has_kits",
    ]
    _, age_str = value.split(":")

    if age_str not in ages:
        raise ValueError(f"Age {age_str} in {value} is invalid!")
    return value


class NewCatTag(Enum):
    male = "male"
    female = "female"
    can_birth = "can_birth"
    new_name = "new_name"
    old_name = "old_name"
    kittypet = "kittypet"
    loner = "loner"
    rogue = "rogue"
    clancat = "clancat"
    former_clancat = "former clancat"
    meeting = "meeting"
    exists = "exists"
    unknown = "unknown"
    litter = "litter"
    dead = "dead"


class NewCat(RootModel):
    root: List[
        Union[
            NewCatTag,
            Annotated[
                str,
                StringConstraints(pattern=r"^status:(.+)$"),
                AfterValidator(validate_nc_status),
            ],
            Annotated[
                str,
                StringConstraints(pattern=r"^age:(.+)$"),
                AfterValidator(validate_nc_age),
            ],
            Annotated[
                str,
                StringConstraints(pattern=r"^backstory:(.+)$"),
                AfterValidator(validate_nc_backstories),
            ],
            Annotated[str, StringConstraints(pattern=r"^parent:([,0-9]+)$")],
            Annotated[str, StringConstraints(pattern=r"^adoptive:([_,0-9a-zA-Z]+)$")],
            Annotated[str, StringConstraints(pattern=r"^mate:([_,0-9a-zA-Z]+)$")],
        ]
    ]
