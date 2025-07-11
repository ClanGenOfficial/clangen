"""
Functions related to today's current date.
"""

import datetime
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Tuple, Union, List

from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get

# fixing year to 2000 so we can use date comparison functions.
# 2000 is used because it is a leap year.
_today = datetime.date.today().replace(year=2000)


@dataclass
class DateInfo:
    """
    Class keeping track of information about a specific date.
    start_date and end_date are INCLUSIVE RANGES.

    start_date: datetime.date representing start date.
    end_date: datetime.date representing end date.
    patrol_tag: Patrol tag for patrols exclusive to this date.
    """

    def __init__(
        self,
        patrol_tag: str,
        start_date: Tuple[int],
        end_date: Union[Tuple[int], None] = None,
    ):
        """
        start_date: Start date in the form of (mm, dd)
        end_date: End date in the form of (mm, dd)
                  or None if start_date = end_date
        patrol_tag: Patrol tag for patrols exclusive to this date.
        """
        self.start_date = datetime.date(2000, start_date[0], start_date[1])
        self.patrol_tag = patrol_tag
        if end_date:
            self.end_date = datetime.date(2000, end_date[0], end_date[1])
        else:
            self.end_date = self.start_date

    def in_range(self, date: datetime.date) -> bool:
        """
        Returns True if date is in the range of start_date and end_date.
        False otherwise.
        """
        return self.start_date <= date <= self.end_date


class SpecialDate(Enum):
    """
    Enum keeping track of registered 'special dates'.
    """

    APRIL_FOOLS = auto()
    HALLOWEEN = auto()
    NEW_YEARS = auto()


# Maps SpecialDate enums to actual DateInfo classes.
_date_map: Dict[SpecialDate, DateInfo] = {
    SpecialDate.APRIL_FOOLS: DateInfo("april_fools", (4, 1)),
    SpecialDate.HALLOWEEN: DateInfo("halloween", (10, 21), (11, 7)),
    SpecialDate.NEW_YEARS: DateInfo("new_years", (1, 1)),
}


def is_today(date: SpecialDate) -> bool:
    """
    Checks if today is a specified 'special date'.

    Only returns True if "special_dates" setting is True.
    """
    if not game_setting_get("special_dates"):
        return False
    if constants.CONFIG["fun"].get("always_halloween", False):
        return True

    d = _date_map.get(date, None)
    return d and d.in_range(_today)


def get_special_date() -> Union[DateInfo, None]:
    """
    If today is a 'special date', return the DateInfo.
    Only returns succeeds if "special_dates" setting is True.

    Otherwise, return None.
    """
    if not game_setting_get("special_dates"):
        return None
    if constants.CONFIG["fun"].get("always_halloween", False):
        return _date_map[SpecialDate.HALLOWEEN]

    for _, date in _date_map.items():
        if date.in_range(_today):
            return date
    return None


def contains_special_date_tag(lst: List[str]) -> bool:
    """
    Returns True if lst contains a special date tag. False otherwise.
    """
    for tag in lst:
        for _, date in _date_map.items():
            if date.patrol_tag == tag:
                return True
    return False
