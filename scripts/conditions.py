# pylint: disable=line-too-long
"""

TODO: Docs


"""
from random import randrange, choice, random, randint

import i18n

from scripts.cat.cats import Cat
from scripts.cat.constants import ILLNESSES, INJURIES, PERMANENT
from scripts.cat.enums import CatRank
from scripts.cat.pelts import Pelt

# pylint: enable=line-too-long

from scripts.cat.skills import SkillPath
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.event_class import Single_Event
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
        potential_scars=None,
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
        self.potential_scars = potential_scars

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


def get_ill(cat, illness_name, event_triggered=False, lethal=True, severity="default"):
    """Add an illness to this cat.

    :param cat: the cat to be made ill
    :param illness_name: name of the illness (str)
    :param event_triggered: Whether to have this illness skip `moon_skip_illness` for 1 moon, default `False` (bool)
    :param lethal: Allow lethality, default `True` (bool)
    :param severity: Override severity, default `'default'` (str, accepted values `'minor'`, `'major'`, `'severe'`)
    """
    if cat.dead:
        return
    if illness_name not in ILLNESSES:
        print(f"WARNING: {illness_name} is not in the illnesses collection.")
        return
    if illness_name == "kittencough" and cat.status.rank != CatRank.KITTEN:
        return

    illness = ILLNESSES[illness_name]
    mortality = illness["mortality"][cat.age.value]
    med_mortality = illness["medicine_mortality"][cat.age.value]
    illness_severity = illness["severity"] if severity == "default" else severity
    duration = illness["duration"]
    med_duration = illness["medicine_duration"]

    amount_per_med = get_amount_cat_for_one_medic(game.clan)

    if medicine_cats_can_cover_clan(Cat.all_cats.values(), amount_per_med):
        duration = med_duration
    if severity != "minor":
        duration += randrange(-1, 1)
    if duration == 0:
        duration = 1

    if lethal is False:
        mortality = 0

    new_illness = Illness(
        name=illness_name,
        severity=illness_severity,
        mortality=mortality,
        infectiousness=illness["infectiousness"],
        duration=duration,
        medicine_duration=illness["medicine_duration"],
        medicine_mortality=med_mortality,
        risks=illness["risks"],
        event_triggered=event_triggered,
    )

    if new_illness.name not in cat.illnesses:
        cat.illnesses[new_illness.name] = {
            "severity": new_illness.severity,
            "mortality": new_illness.current_mortality,
            "infectiousness": new_illness.infectiousness,
            "duration": new_illness.duration,
            "moon_start": game.clan.age if game.clan else 0,
            "risks": new_illness.risks,
            "event_triggered": new_illness.new,
        }


def get_injured(
    self,
    name,
    event_triggered=False,
    lethal=True,
    potential_scars=None,
    severity="default",
):
    """Add an injury to this cat.

    :param name: The injury to add
    :type name: str
    :param event_triggered: Whether to process healing immediately, defaults to False
    :type event_triggered: bool, optional
    :param lethal: _description_, defaults to True
    :type lethal: bool, optional
    :param potential_scars: List of possible scars to get upon healing, defaults to None
    :type potential_scars: array, optional
    :param severity: _description_, defaults to 'default'
    :type severity: str, optional
    """
    if self.dead:
        return

    if name not in INJURIES:
        print(f"WARNING: {name} is not in the injuries collection.")
        return

    if name == "mangled tail" and "NOTAIL" in self.pelt.scars:
        return
    if name == "torn ear" and "NOEAR" in self.pelt.scars:
        return

    injury = INJURIES[name]
    mortality = injury["mortality"][self.age.value]
    duration = injury["duration"]
    med_duration = injury["medicine_duration"]

    injury_severity = injury["severity"] if severity == "default" else severity
    if medicine_cats_can_cover_clan(
        Cat.all_cats.values(), get_amount_cat_for_one_medic(game.clan)
    ):
        duration = med_duration
    if severity != "minor":
        duration += randrange(-1, 1)
    if duration == 0:
        duration = 1
    if lethal is False:
        mortality = 0

    new_injury = Injury(
        name=name,
        severity=injury_severity,
        duration=injury["duration"],
        medicine_duration=duration,
        mortality=mortality,
        risks=injury["risks"],
        illness_infectiousness=injury["illness_infectiousness"],
        also_got=injury["also_got"],
        cause_permanent=injury["cause_permanent"],
        event_triggered=event_triggered,
        potential_scars=potential_scars,
    )

    if new_injury.name not in self.injuries:
        self.injuries[new_injury.name] = {
            "severity": new_injury.severity,
            "mortality": new_injury.current_mortality,
            "duration": new_injury.duration,
            "moon_start": game.clan.age if game.clan else 0,
            "illness_infectiousness": new_injury.illness_infectiousness,
            "risks": new_injury.risks,
            "complication": None,
            "cause_permanent": new_injury.cause_permanent,
            "event_triggered": new_injury.new,
            "potential_scars": new_injury.potential_scars,
        }

    if (
        not Cat.disable_random
        and len(new_injury.also_got) > 0
        and not int(random() * 5)
    ):
        avoided = False
        if (
            "blood loss" in new_injury.also_got
            and len(
                find_alive_cats_with_rank(Cat, [CatRank.MEDICINE_CAT], working=True)
            )
            != 0
        ):
            clan_herbs = {
                herb
                for herb, clan_has_herb in game.clan.herb_supply.entire_supply.items()
                if clan_has_herb
            }
            needed_herbs = {"horsetail", "raspberry", "marigold", "cobwebs"}
            usable_herbs = list(needed_herbs.intersection(clan_herbs))

            if usable_herbs:
                # deplete the herb
                herb_used = choice(usable_herbs)
                game.clan.herb_supply.remove_herb(herb_used, -1)
                avoided = True
                text = i18n.t("screens.med_den.blood_loss", name=self.name)
                game.herb_events_list.append(text)

        if not avoided:
            self.also_got = True
            additional_injury = choice(new_injury.also_got)
            if additional_injury in INJURIES:
                get_injured(self, additional_injury, event_triggered=True)
            else:
                get_ill(self, additional_injury, event_triggered=True)
    else:
        self.also_got = False


def contact_with_ill_cat(cat, other_cat: Cat):
    """handles if one cat had contact with an ill cat"""

    infectious_illnesses = []
    if cat.is_ill() or other_cat is None or not other_cat.is_ill():
        return
    elif other_cat.is_ill():
        for illness in other_cat.illnesses:
            if other_cat.illnesses[illness]["infectiousness"] != 0:
                infectious_illnesses.append(illness)
        if len(infectious_illnesses) == 0:
            return

    for illness in infectious_illnesses:
        illness_name = illness
        rate = other_cat.illnesses[illness]["infectiousness"]
        if cat.is_injured():
            for y in cat.injuries:
                illness_infect = list(
                    filter(
                        lambda ill: ill["name"] == illness_name,
                        cat.injuries[y]["illness_infectiousness"],
                    )
                )
                if illness_infect is not None and len(illness_infect) > 0:
                    illness_infect = illness_infect[0]
                    rate -= illness_infect["lower_by"]

                # prevent rate lower 0 and print warning message
                if rate < 0:
                    print(
                        f"WARNING: injury {cat.injuries[y]['name']} has lowered \
                        chance of {illness_name} infection to {rate}"
                    )
                    rate = 1

        if not random() * rate:
            text = f"{cat.name} had contact with {other_cat.name} and now has {illness_name}."
            # game.health_events_list.append(text)
            game.cur_events_list.append(
                Single_Event(text, "health", cat_dict={"m_c": cat})
            )
            get_ill(cat, illness_name)


def add_congenital_condition(cat):
    possible_conditions = []

    for condition in PERMANENT:
        possible = PERMANENT[condition]
        if possible["congenital"] in ("always", "sometimes"):
            possible_conditions.append(condition)

    new_condition = choice(possible_conditions)

    if new_condition == "born without a leg":
        cat.pelt.scars = (*cat.pelt.scars, "NOPAW")
    elif new_condition == "born without a tail":
        cat.pelt.scars = (*cat.pelt.scars, "NOTAIL")

    get_permanent_condition(cat, new_condition, born_with=True)


def get_permanent_condition(cat, name, born_with=False, event_triggered=False):
    if cat.dead:
        return False
    if name not in PERMANENT:
        print(
            cat.name,
            f"WARNING: {name} is not in the permanent conditions collection.",
        )
        return False

    if "blind" in cat.permanent_condition and name == "failing eyesight":
        return False
    if "deaf" in cat.permanent_condition and name == "partial hearing loss":
        return False

    # remove accessories if need be
    if "NOTAIL" in cat.pelt.scars or "HALFTAIL" in cat.pelt.scars:
        cat.pelt.accessory = tuple(
            acc for acc in cat.pelt.accessory if acc not in Pelt.tail_accessories
        )

    if "NOPAW" in cat.pelt.scars:
        cat.pelt.accessory = tuple(
            acc for acc in cat.pelt.accessory if acc not in Pelt.paw_accessories
        )

    condition = PERMANENT[name]
    new_condition = False
    mortality = condition["mortality"][cat.age.value]

    if condition["congenital"] == "always":
        born_with = True
    moons_until = condition["moons_until"]
    if born_with and moons_until != 0:
        moons_until = randint(
            moons_until - 1, moons_until + 1
        )  # creating a range in which a condition can present
        moons_until = max(moons_until, 0)

    if born_with and not cat.status.rank.is_baby():
        moons_until = -2
    elif born_with is False:
        moons_until = 0

    if name == "paralyzed":
        cat.pelt.paralyzed = True

    new_perm_condition = PermanentCondition(
        name=name,
        severity=condition["severity"],
        congenital=condition["congenital"],
        moons_until=moons_until,
        mortality=mortality,
        risks=condition["risks"],
        illness_infectiousness=condition["illness_infectiousness"],
        event_triggered=event_triggered,
    )

    if new_perm_condition.name not in cat.permanent_condition:
        cat.permanent_condition[new_perm_condition.name] = {
            "severity": new_perm_condition.severity,
            "born_with": born_with,
            "moons_until": new_perm_condition.moons_until,
            "moon_start": game.clan.age if game.clan else 0,
            "mortality": new_perm_condition.current_mortality,
            "illness_infectiousness": new_perm_condition.illness_infectiousness,
            "risks": new_perm_condition.risks,
            "complication": None,
            "event_triggered": new_perm_condition.new,
        }
        new_condition = True
    return new_condition
