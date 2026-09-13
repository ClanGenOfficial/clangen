from random import randrange, random, choice, randint

import i18n
from scripts.cat.constants import ILLNESSES, INJURIES, PERMANENT
from scripts.cat.enums import CatRank
from scripts.cat.pelts import Pelt
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.conditions import (
    get_amount_cat_for_one_medic,
    medicine_cats_can_cover_clan,
    Illness,
    Injury,
    PermanentCondition,
)
from scripts.events_module.event_information import EventInformation
from scripts.game_structure import game


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

    if medicine_cats_can_cover_clan(cat.all_cats.values(), amount_per_med):
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
    cat,
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
    if cat.dead:
        return

    if name not in INJURIES:
        print(f"WARNING: {name} is not in the injuries collection.")
        return

    if name == "mangled tail" and "NOTAIL" in cat.pelt.scars:
        return
    if name == "torn ear" and "NOEAR" in cat.pelt.scars:
        return

    injury = INJURIES[name]
    mortality = injury["mortality"][cat.age.value]
    duration = injury["duration"]
    med_duration = injury["medicine_duration"]

    injury_severity = injury["severity"] if severity == "default" else severity
    if medicine_cats_can_cover_clan(
        cat.all_cats.values(), get_amount_cat_for_one_medic(game.clan)
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

    if new_injury.name not in cat.injuries:
        cat.injuries[new_injury.name] = {
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
        not cat.disable_random
        and len(new_injury.also_got) > 0
        and not int(random() * 5)
    ):
        avoided = False
        if (
            "blood loss" in new_injury.also_got
            and len(
                find_alive_cats_with_rank(cat, [CatRank.MEDICINE_CAT], working=True)
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
                text = i18n.t("screens.med_den.blood_loss", name=cat.name)
                game.herb_events_list.append(text)

        if not avoided:
            cat.also_got = True
            additional_injury = choice(new_injury.also_got)
            if additional_injury in INJURIES:
                get_injured(cat, additional_injury, event_triggered=True)
            else:
                get_ill(cat, additional_injury, event_triggered=True)
    else:
        cat.also_got = False


def contact_with_ill_cat(cat, other_cat):
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
                EventInformation(text, ["health"], cat_dict={"m_c": cat})
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
