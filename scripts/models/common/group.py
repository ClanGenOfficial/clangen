from enum import Enum
from typing import Annotated, Union

from pydantic import RootModel, StringConstraints, AfterValidator

from scripts.models.common.cat import validate_cat_abbr


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


class Group(RootModel):
    root: Union[
        GroupEnum,
        Annotated[
            str,
            StringConstraints(pattern=r"^match:(.+)$"),
            AfterValidator(validate_cat_abbr),
        ],
    ]
