# pylint: disable=line-too-long
"""
Functions related to today's current date.
"""  # pylint: enable=line-too-long


import datetime
from enum import Enum

# ---------------------------------------------------------------------------- #
#                                Fun Date Stuff                                #
# ---------------------------------------------------------------------------- #

class SpecialDate(Enum):
    """
    Enum keeping track of registered 'special dates'. Format is (mm, dd).
    """
    APRIL_FOOLS = (4, 1)
    HALLOWEEN = (10, 31)
    NEW_YEARS = (1, 1)

def is_today(date: SpecialDate) -> bool:
    """
    Checks if today is a specified 'special date'.
    """
    today = datetime.date.today()
    return (today.month, today.day) == date.value

def get_special_date() -> SpecialDate:
    """
    If today is a 'special date', return the SpecialDate. 

    Otherwise, return None.
    """
    today = datetime.date.today()
    for date in SpecialDate:
        if (today.month, today.day) == date.value:
            return date
    return None
