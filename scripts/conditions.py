# pylint: disable=line-too-long
"""

TODO: Docs


"""
from scripts.cat.enums import CatRank

# pylint: enable=line-too-long

from scripts.cat.skills import SkillPath
from scripts.game_structure import game


def amount_clanmembers_covered(all_cats, amount_per_med) -> int:
    """
    number of clan members the meds can treat
    """

    medicine_cats = [
        i
        for i in all_cats
        if i.status.alive_in_player_clan
        and not i.not_working()
        and i.status.rank.is_any_medicine_rank()
    ]
    full_med = [i for i in medicine_cats if i.status.rank == CatRank.MEDICINE_CAT]
    apprentices = [
        i for i in medicine_cats if i.status.rank == CatRank.MEDICINE_APPRENTICE
    ]

    total_exp = 0
    for cat in medicine_cats:
        total_exp += cat.experience
    total_exp = total_exp * 0.003

    # Determine the total med number. Med cats with certain skill counts
    # as "more" of a med cat.  Only full medicine cat can have their skills have effect
    total_med_number = len(apprentices) / 2
    for cat in full_med:
        if cat.skills.meets_skill_requirement(SkillPath.HEALER, 3):
            total_med_number += 2
        elif cat.skills.meets_skill_requirement(SkillPath.HEALER, 2):
            total_med_number += 1.75
        elif cat.skills.meets_skill_requirement(SkillPath.HEALER, 1):
            total_med_number += 1.5
        else:
            total_med_number += 1

    adjust_med_number = total_med_number + total_exp

    return int(
        adjust_med_number * (amount_per_med + 1)
    )  # number of cats they can care for


def medicine_cats_can_cover_clan(all_cats, amount_per_med) -> bool:
    """
    whether the player has enough meds for the whole clan
    """
    relevant_cats = [c for c in all_cats if c.status.alive_in_player_clan]
    return amount_clanmembers_covered(all_cats, amount_per_med) >= len(relevant_cats)


def get_amount_cat_for_one_medic(clan):
    """Returns the amount of cats one medicine cat can treat"""
    amount = 10
    if clan and clan.game_mode == "cruel season":
        amount = 7
    if clan and clan.game_mode == "classic":
        # just hope nobody has clans with more than 1,000,000 cats in classic
        amount = 1000000
    return amount


# ---------------------------------------------------------------------------- #
#                                    Illness                                   #
# ---------------------------------------------------------------------------- #


class Illness:
    """
    TODO: DOCS
    """

    def __init__(
        self,
        name,
        severity,
        mortality,
        infectiousness,
        duration,
        medicine_duration,
        medicine_mortality,
        risks,
        herbs=None,
        event_triggered=False,
    ):
        self.name = name
        self.severity = severity
        self.mortality = int(mortality)
        self.infectiousness = int(infectiousness)
        self.duration = int(duration)
        self.medicine_duration = int(medicine_duration)
        self.medicine_mortality = int(medicine_mortality)
        self.risks = risks
        self.herbs = herbs if herbs else []
        self.new = event_triggered

        self.current_duration = duration
        self.current_mortality = mortality

        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medicine_cats_can_cover_clan(
            game.cat_class.all_cats.values(), amount_per_med
        ):
            self.current_duration = medicine_duration
            self.current_mortality = medicine_mortality

    @property
    def current_duration(self):
        """
        TODO: DOCS
        """
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        """
        TODO: DOCS
        """
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medicine_cats_can_cover_clan(
            game.cat_class.all_cats.values(), amount_per_med
        ):
            if value > self.medicine_duration:
                value = self.medicine_duration

        self._current_duration = value

    @property
    def current_mortality(self):
        """
        TODO: DOCS
        """
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        """
        TODO: DOCS
        """
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medicine_cats_can_cover_clan(
            game.cat_class.all_cats.values(), amount_per_med
        ):
            if value < self.medicine_mortality:
                value = self.medicine_mortality

        self._current_mortality = value


# ---------------------------------------------------------------------------- #
#                                   Injuries                                   #
# ---------------------------------------------------------------------------- #


class Injury:
    """
    TODO: DOCS
    """

    def __init__(
        self,
        name,
        severity,
        duration,
        medicine_duration,
        mortality,
        risks=None,
        illness_infectiousness=None,
        also_got=None,
        cause_permanent=None,
        herbs=None,
        event_triggered=False,
    ):
        self.name = name
        self.severity = severity
        self.duration = duration
        self.medicine_duration = medicine_duration
        self.mortality = mortality
        self.risks = risks
        self.illness_infectiousness = illness_infectiousness
        self.also_got = also_got
        self.cause_permanent = cause_permanent
        self.herbs = herbs if herbs else []
        self.new = event_triggered

        self.current_duration = duration
        self.current_mortality = mortality

        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medicine_cats_can_cover_clan(
            game.cat_class.all_cats.values(), amount_per_med
        ):
            self.current_duration = medicine_duration

    @property
    def current_duration(self):
        """
        TODO: DOCS
        """
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medicine_cats_can_cover_clan(
            game.cat_class.all_cats.values(), amount_per_med
        ):
            if value > self.medicine_duration:
                value = self.medicine_duration

        self._current_duration = value

    @property
    def current_mortality(self):
        """
        TODO: DOCS
        """
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        self._current_mortality = value


# ---------------------------------------------------------------------------- #
#                             Permanent Conditions                             #
# ---------------------------------------------------------------------------- #


class PermanentCondition:
    """
    TODO: DOCS
    """

    def __init__(
        self,
        name,
        severity,
        moons_until,
        congenital="never",
        mortality=0,
        risks=None,
        illness_infectiousness=None,
        herbs=None,
        event_triggered=False,
    ):
        self.name = name
        self.severity = severity
        self.congenital = congenital
        self.moons_until = moons_until
        self.mortality = mortality
        self.risks = risks
        self.illness_infectiousness = illness_infectiousness
        self.herbs = herbs if herbs else []
        self.new = event_triggered

        self.current_mortality = mortality

    # severity level determines retirement:
    # severe - auto retire, major - chance retire, minor - no retire
    # congenital determines if a cat can be born with it or not: never, sometimes, always

    # moons_until is used if you want a delay between when the cat
    # contracts the condition and when the cat presents that condition

    @property
    def current_mortality(self):
        """
        TODO: DOCS
        """
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        """
        TODO: DOCS
        """
        self._current_mortality = value
