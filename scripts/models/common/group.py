from enum import Enum
from typing import Annotated, Union

from pydantic import RootModel, StringConstraints, AfterValidator

from scripts.models.common.cat import CatEnum


class GroupEnum(Enum):
    AFTERLIFE = "afterlife"
    PLAYER_CLAN = "player_clan"
    OTHER_CLAN = "other_clan"

    DARK_FOREST = "dark_forest"
    STARCLAN = "starclan"
    UNKNOWN_RESIDENCE = "unknown_residence"
    NO_GROUP = "no_group"

    NOT_AFTERLIFE = "-afterlife"
    NOT_PLAYER_CLAN = "-player_clan"
    NOT_OTHER_CLAN = "-other_clan"

    NOT_DARK_FOREST = "-dark_forest"
    NOT_STARCLAN = "-starclan"
    NOT_UNKNOWN_RESIDENCE = "-unknown_residence"
    NOT_NO_GROUP = "-no_group"


def validate_cat_abbr(value: str) -> str:
    abbrs = [r.value for r in CatEnum]
    _, abbr_str = value.split(":")
    if abbr_str not in abbrs:
        raise ValueError(
            f"Abbreviation {abbr_str} in {value} is not a valid abbreviation!"
        )
    return value


class Group(RootModel):
    root: Union[
        GroupEnum,
        Annotated[
            str,
            StringConstraints(pattern=r"^match:(.+)$"),
            AfterValidator(validate_cat_abbr),
        ],
    ]
