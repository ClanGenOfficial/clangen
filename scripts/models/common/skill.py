from enum import Enum
from typing import Annotated

from pydantic import AfterValidator, StringConstraints, RootModel


class Skills(Enum):
    TEACHER = "TEACHER"
    HUNTER = "HUNTER"
    FIGHTER = "FIGHTER"
    RUNNER = "RUNNER"
    CLIMBER = "CLIMBER"
    SWIMMER = "SWIMMER"
    SPEAKER = "SPEAKER"
    MEDIATOR = "MEDIATOR"
    CLEVER = "CLEVER"
    INSIGHTFUL = "INSIGHTFUL"
    SENSE = "SENSE"
    KIT = "KIT"
    STORY = "STORY"
    LORE = "LORE"
    CAMP = "CAMP"
    HEALER = "HEALER"
    STAR = "STAR"
    DARK = "DARK"
    OMEN = "OMEN"
    DREAM = "DREAM"
    CLAIRVOYANT = "CLAIRVOYANT"
    PROPHET = "PROPHET"
    GHOST = "GHOST"

    # these ones are NOT real skills! DO NOT USE THEM!!
    # they're just here so that the tests don't error out.
    # we can search/replace them in the json files when backstory constraints are added
    # once that happens, remove them from here.
    ROGUE = "ROGUE"
    LONER = "LONER"
    KITTYPET = "KITTYPET"


def validate_skill(value: str) -> str:
    skills = []
    for s in Skills:
        skills.append(s.value)
        skills.append(f"-{s.value}")

    skill, _ = value.split(",")
    if skill not in skills:
        raise ValueError(f"Skill {skill} in {value} isn't a valid skill!")
    return value


class Skill(RootModel):
    root: Annotated[
        str,
        StringConstraints(pattern=r"^-?[A-Z]+,\s*[0-4]$"),
        AfterValidator(validate_skill),
    ]
