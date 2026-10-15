from enum import Enum, auto
from random import random

from scripts.cat.conditions.permanent_condition import PermanentCondition
from scripts.cat.conditions.temporary_condition import TemporaryCondition
from scripts.config import get_config
from scripts.game_structure import game


class ConditionState(Enum):
    REVEALED = auto()
    SKIPPED = auto()
    CONTINUING = auto()
    FATAL = auto()
    HEALED = auto()


def update_permanent_condition_state(condition: PermanentCondition) -> ConditionState:
    """
    Checks the status of given permanent condition, updates it's state, and returns the new state
    """
    if condition.omit_moonskip:
        return ConditionState.SKIPPED

    # handling congenital countdown
    if condition.is_congenital:
        if condition.moons_until_discovery >= 0:
            condition.moons_until_discovery -= 1

            if condition.moons_until_discovery == -1:
                condition.moon_gained = game.clan.age if game.clan else 0
                return ConditionState.REVEALED
            else:
                return ConditionState.SKIPPED

    mortality = _progress_mortality(condition)
    if mortality == ConditionState.FATAL:
        return ConditionState.FATAL

    return ConditionState.CONTINUING


def update_temporary_condition_state(condition: TemporaryCondition):
    """
    Checks the status of given temporary condition, updates it's state, and returns the new state
    """
    if condition.omit_moonskip:
        return ConditionState.SKIPPED

    mortality = _progress_mortality(condition)
    if mortality == ConditionState.FATAL:
        return ConditionState.FATAL

    recovery_buff = get_config("focus.rest_and_recover.moons_earlier_healed")

    condition.duration -= 1 + recovery_buff

    if condition.duration <= 0:
        if condition.current_complication:
            condition.duration = 1
            return ConditionState.CONTINUING
        else:
            return ConditionState.HEALED
    else:
        return ConditionState.CONTINUING


def _progress_mortality(condition) -> ConditionState:
    """
    Checks the conditions mortality state
    """
    if condition.mortality and random() <= condition.mortality:
        # actual death is handled later by event outcomes
        return ConditionState.FATAL

    return ConditionState.CONTINUING
