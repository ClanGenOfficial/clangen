from random import random, choice, choices, randint

import i18n

from scripts.cat.cats import Cat
from scripts.cat.conditions.gain_conditions import gain_temporary_condition
from scripts.cat.enums import CatRank
from scripts.clan_package.cotc import change_clan_reputation, change_clan_relations
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.clan_package.settings import get_clan_setting
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.text_adjust import adjust_list_text
from scripts.game_structure import game
from scripts.game_structure.constants import HERBS


def handle_focus():
    """
    Checks the current focus setting and handles all immediate affects.
    """
    if not game.clan.deputy or not game.clan.deputy.status.alive_in_player_clan:
        return
    if get_clan_setting("business_as_usual"):
        return
    elif get_clan_setting("rest_and_recover"):
        focus_text = _rest_and_recover()
    elif get_clan_setting("hunting"):
        focus_text = _hunting()
    elif get_clan_setting("herb_gathering"):
        focus_text = _herb_gathering()
    elif get_clan_setting("threaten_outsiders"):
        focus_text = _threaten_outsiders()
    elif get_clan_setting("seek_outsiders"):
        focus_text = _seek_outsiders()
    elif get_clan_setting("sabotage_other_clans"):
        focus_text = _sabotage_clans()
    elif get_clan_setting("aid_other_clans"):
        focus_text = _aid_clans()
    elif get_clan_setting("raid_other_clans"):
        focus_text = _raid_clans()
    elif get_clan_setting("hoarding"):
        focus_text = _hoarding()
    else:
        focus_text = i18n.t("focus.default")

    game.cur_events_list.insert(0, EventInformation(focus_text, ["misc"]))


def _rest_and_recover() -> str:
    """
    Creates rest and recover text. All of this focus's impacts are added in other areas of the code.
    """
    return i18n.t("focus.rest_and_recover")


def _hunting() -> str:
    """
    Gathers additional prey
    """
    prey_increase = 0
    injury_modifier = 1
    info_dict = get_config("focus.hunting")
    buffs = info_dict["buff"]
    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        if (
            "biome" in buffs[skill]
            and game.clan.biome.casefold() not in buffs[skill]["biome"]
        ):
            continue

        if "injury_modifier" in buffs[skill]:
            injury_modifier = buffs[skill]["injury_modifier"]
        elif "prey_increase" in buffs[skill]:
            prey_increase = buffs[skill]["prey_increase"]

    used_cats, prey_amount = _cats_gather_prey(prey_increase)

    # HANDLE INJURIES
    injury_chance = round(info_dict["injury_chance"]) * injury_modifier
    injury_dict = info_dict["injuries"]

    involved_cats = _give_conditions(
        used_cats, injury_chance=injury_chance, injury_dict=injury_dict
    )

    # finish
    injured_cats = involved_cats["injured"]
    if injured_cats:
        game.cur_events_list.insert(
            0,
            EventInformation(
                i18n.t("focus.prey_injury", count=len(injured_cats)),
                ["health"],
                injured_cats,
            ),
        )

    focus_text = i18n.t("focus.focus_prey", count=prey_amount)
    game.freshkill_event_list.append(focus_text)

    return focus_text


def _herb_gathering() -> str:
    """
    Gathers additional herbs
    """
    # get medicine cats
    healthy_meds = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE],
        working=True,
    )
    # get warriors to help
    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )

    # no warriors? then who can even help gather...
    if not healthy_warriors:
        return i18n.t("focus.focus_herbs", count=0)

    buffs = get_config("focus.herb_gathering.buff")
    quantity_increase = 0
    gather_max_increase = 0
    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        if "quantity_increase" in buffs[skill]:
            quantity_increase = buffs[skill]["quantity_increase"]
        if "gather_max_increase" in buffs[skill]:
            gather_max_increase = buffs[skill]["gather_max_increase"]

    return _meds_gather_herbs(
        healthy_meds, healthy_warriors, gather_max_increase, quantity_increase
    )


def _threaten_outsiders() -> str:
    """
    Lowers relations with outsiders
    """
    info_dict = get_config("focus.threaten_outsiders")
    amount = info_dict["reputation"]

    buffs = info_dict["buff"]

    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        amount = round(amount * buffs[skill]["reputation_modifier"])

    change_clan_reputation(amount)
    return i18n.t("focus.threaten_outsiders")


def _seek_outsiders() -> str:
    """
    Increases relations with outsiders
    """
    info_dict = get_config("focus.seek_outsiders")
    amount = info_dict["reputation"]

    buffs = info_dict["buff"]

    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        amount = round(amount * buffs[skill]["reputation_modifier"])

    change_clan_reputation(amount)
    return i18n.t("focus.seek_outsiders")


def _sabotage_clans() -> str:
    """
    Lowers relationships with target clans
    """
    info_dict = get_config("focus.sabotage_other_clans")
    amount = info_dict["relation"]

    buffs = info_dict["buff"]

    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        amount = round(amount * buffs[skill]["relation_modifier"])

    for name in game.clan.clans_in_focus:
        clan = [clan for clan in game.clan.all_other_clans if clan.name == name][0]
        change_clan_relations(clan, -amount)
    return i18n.t(
        "focus.sabotage_clans", clan=adjust_list_text(game.clan.clans_in_focus)
    )


def _aid_clans() -> str:
    """
    Increases relations with target clans
    """
    amount = get_config("focus.aid_other_clans.relation")

    buffs = get_config("focus.aid_other_clans.buff")

    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        amount = round(amount * buffs[skill]["relation_modifier"])

    for name in game.clan.clans_in_focus:
        clan = [clan for clan in game.clan.all_other_clans if clan.name == name][0]
        change_clan_relations(clan, amount)
    return i18n.t("focus.aid_clans", clan=adjust_list_text(game.clan.clans_in_focus))


def _raid_clans() -> str:
    """
    Lowers relations with target clans and steals herbs/prey from them, can injure cats as a result
    """
    info_dict = get_config("focus.raid_other_clans")

    buffs = info_dict["buff"]

    injury_modifier = 1
    supply_amount_buff = 0
    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        if "injury_chance_modifier" in buffs[skill]:
            injury_modifier = buffs[skill]["injury_chance_modifier"]
        if "supply_amount_buff" in buffs[skill]:
            supply_amount_buff = buffs[skill]["supply_amount_buff"]

    used_cats = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )

    prey_recovered = 0
    prey_amounts = info_dict["prey_amounts"]
    prey_weights = info_dict["prey_weights"]
    for _c in used_cats:
        prey_recovered += choices(prey_amounts, prey_weights)[0] + supply_amount_buff

    # HANDLE HERBS
    herb_amount_to_gain = 0
    herb_amounts = info_dict["herb_amounts"]
    herb_weights = info_dict["herb_weights"]
    for _c in used_cats:
        herb_amount_to_gain += (
            choices(herb_amounts, herb_weights)[0] + supply_amount_buff
        )

    gathered_herbs = {}
    while herb_amount_to_gain:
        amount = randint(1, herb_amount_to_gain)
        chosen_herb = choice(list(HERBS.keys()))
        if chosen_herb not in gathered_herbs:
            gathered_herbs[chosen_herb] = amount
        else:
            gathered_herbs[chosen_herb] += amount
        herb_amount_to_gain -= amount

    if gathered_herbs:
        (
            list_of_herb_strs,
            found_herbs,
        ) = game.clan.herb_supply.handle_found_herbs_outcomes(gathered_herbs)
        # remove dupes
        herbs_recovered = list(set(found_herbs))
        # get display strings for herbs
        herb_strs = []
        for herb in herbs_recovered:
            herb_strs.append(game.clan.herb_supply.herb[herb].plural_display)

        herbs_recovered = adjust_list_text(herb_strs)
        game.herb_events_list.append(
            i18n.t("focus.raid_herb_log", herbs=herbs_recovered)
        )

        herbs_recovered = 0
        for _h in found_herbs:
            herbs_recovered += found_herbs[_h]
    else:
        herbs_recovered = []

    # HANDLE INJURIES
    injury_chance = max(
        1,
        round(
            info_dict["injury_chance"]
            - (len(game.clan.clans_in_focus * info_dict["chance_increase_per_clan"]))
            * injury_modifier
        ),
    )
    injury_dict = info_dict["injuries"]

    involved_cats = _give_conditions(
        used_cats, injury_chance=injury_chance, injury_dict=injury_dict
    )

    for name in game.clan.clans_in_focus:
        clan = [clan for clan in game.clan.all_other_clans if clan.name == name][0]
        amount = info_dict["relation"]
        change_clan_relations(clan, amount)

    text = []
    if prey_recovered:
        prey_text = i18n.t("focus.raid_prey", count=prey_recovered)
        game.clan.freshkill_pile.add_freshkill(prey_recovered)

        game.freshkill_event_list.append(prey_text)
        text.append(prey_text)
    if herbs_recovered:
        text.append(i18n.t("focus.raid_herb", count=herbs_recovered))

    text.append(
        i18n.t("focus.raid_relations", clan=adjust_list_text(game.clan.clans_in_focus))
    )

    if involved_cats:
        injured_cats = involved_cats["injured"]
        game.cur_events_list.insert(
            0,
            EventInformation(
                i18n.t("focus.raid_injury", count=len(injured_cats)),
                ["health"],
                injured_cats,
            ),
        )

    return " ".join(text)


def _hoarding():
    """
    Gathers additional prey and herbs while also applying conditions to cats.
    """
    info_dict = get_config("focus.hoarding")

    buffs = info_dict["buff"]
    condition_modifier = 1
    gather_max_increase = 0
    prey_increase = 0
    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        if "condition_chance_modifier" in buffs[skill]:
            condition_modifier = buffs[skill]["condition_chance_modifier"]
        if "gather_max_increase" in buffs[skill]:
            gather_max_increase = buffs[skill]["gather_max_increase"]
        if "prey_increase" in buffs[skill]:
            prey_increase = buffs[skill]["prey_increase"]

    used_cats, prey_recovered = _cats_gather_prey(prey_increase)

    healthy_meds = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.MEDICINE_CAT],
        working=True,
    )

    injury_chance = info_dict["injury_chance_warrior"] * condition_modifier
    illness_chance = info_dict["illness_chance"] * condition_modifier
    injury_dict = info_dict["injuries"]
    illness_dict = info_dict["illnesses"]

    involved_cats = _give_conditions(
        used_cats,
        illness_chance=illness_chance,
        illness_dict=illness_dict,
        injury_chance=injury_chance,
        injury_dict=injury_dict,
    )

    text = []
    if healthy_meds:
        herb_focus_text = _meds_gather_herbs(
            healthy_meds, used_cats, max_buff=gather_max_increase
        )
        text.append(herb_focus_text)
    if prey_recovered:
        prey_text = i18n.t("focus.focus_prey", count=prey_recovered)

        game.freshkill_event_list.append(prey_text)
        text.append(prey_text)

    if involved_cats["injured"]:
        game.cur_events_list.insert(
            0,
            EventInformation(
                i18n.t("focus.hoarding_injury", count=len(involved_cats["injured"])),
                ["health"],
                involved_cats["injured"],
            ),
        )
    if involved_cats["sick"]:
        game.cur_events_list.insert(
            0,
            EventInformation(
                i18n.t("focus.hoarding_illness", count=len(involved_cats["sick"])),
                ["health"],
                involved_cats["sick"],
            ),
        )

    return " ".join(text)


def _give_conditions(
    used_cats: list,
    illness_chance: int = 0,
    illness_dict: dict = None,
    injury_chance: int = 0,
    injury_dict: dict = None,
) -> dict:
    involved_cats = {
        "sick": [],
        "injured": [],
    }

    for cat in used_cats:
        if injury_chance:
            if not int(random() * injury_chance):
                chosen_injury = choices(
                    list(injury_dict.keys()), list(injury_dict.values())
                )[0]
                gain_temporary_condition(cat, chosen_injury)
                involved_cats["injured"].append(cat.ID)
        if illness_chance:
            if not int(random() * illness_chance):
                chosen_illness = choices(
                    list(illness_dict.keys()), list(illness_dict.values())
                )[0]
                gain_temporary_condition(
                    cat,
                    chosen_illness,
                )
                involved_cats["sick"].append(cat.ID)

    return involved_cats


def _cats_gather_prey(prey_increase: int = 0):
    prey_recovered = 0
    season = game.clan.current_season.casefold()
    info_dict = get_config("focus.hunting")

    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )
    warrior_prey = info_dict["warrior"][season]["prey_amounts"]
    warrior_weights = info_dict["warrior"][season]["prey_weights"]
    for _c in healthy_warriors:
        prey_recovered += choices(warrior_prey, warrior_weights)[0] + prey_increase

    # handle apprentices
    healthy_apprentices = find_alive_cats_with_rank(
        Cat, ranks=[CatRank.APPRENTICE], working=True
    )
    app_prey = info_dict["apprentice"][season]["prey_amounts"]
    app_weights = info_dict["apprentice"][season]["prey_weights"]
    for _c in healthy_apprentices:
        prey_recovered += choices(app_prey, app_weights)[0] + prey_increase

    game.clan.freshkill_pile.add_freshkill(prey_recovered)

    return healthy_warriors + healthy_apprentices, prey_recovered


def _meds_gather_herbs(
    med_cats: list,
    assistants: list = None,
    max_buff: int = 0,
    quantity_buff: int = 0,
):
    """
    Handles sending med cats to gather extra herbs in accordance to Clan focus
    :param med_cats: a list of medicine cat objects,
    :param assistants: a list of any non-meddies who are assisting the search for herbs
    :param max_buff: Buff to the maximum that can be gathered per assistant
    :param quantity_buff: Buff to the multiplier for quantity
    """

    # get herbs found
    herb_list = []
    info_dict = get_config("focus.herb_gathering")
    quantity_allowed = round(
        len(assistants) * (info_dict["assistant_gather_max"] + max_buff)
    )
    for med in med_cats:
        if not quantity_allowed:
            break
        # each med can also hold some herbs
        quantity_allowed += info_dict["med_gather_max"]
        list_of_herb_strs, found_herbs = game.clan.herb_supply.get_found_herbs(
            med,
            general_amount_bonus=True,
            specific_quantity_bonus=2 + quantity_buff,
            specific_quantity_allowed=quantity_allowed,
        )
        herb_list.extend(found_herbs)
        for h in found_herbs:
            quantity_allowed -= found_herbs[h]

    # remove dupes
    herb_list = list(set(herb_list))
    # get display strings for herbs
    herb_strs = []
    for herb in herb_list:
        herb_strs.append(game.clan.herb_supply.herb[herb].plural_display)

    herb_list = adjust_list_text(herb_strs)

    # finish
    focus_text = i18n.t("focus.focus_herbs", herbs=herb_list, count=len(herb_list))

    if herb_list:
        game.herb_events_list.append(i18n.t("screens.med_den.focus", herbs=herb_list))

    return focus_text
