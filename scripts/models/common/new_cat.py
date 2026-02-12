from enum import Enum
from typing import List, Union, Annotated

from pydantic import StringConstraints, RootModel


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
            Annotated[str, StringConstraints(pattern=r"^status:(.+)$")],
            Annotated[str, StringConstraints(pattern=r"^age:(.+)$")],
            Annotated[str, StringConstraints(pattern=r"^backstory:(.+)$")],
            Annotated[str, StringConstraints(pattern=r"^parent:([,0-9]+)$")],
            Annotated[str, StringConstraints(pattern=r"^adoptive:([_,0-9a-zA-Z]+)$")],
            Annotated[str, StringConstraints(pattern=r"^mate:([_,0-9a-zA-Z]+)$")],
        ]
    ]
