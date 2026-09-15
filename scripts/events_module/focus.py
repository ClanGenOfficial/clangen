from random import random, choice, choices, randint

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.cat.microservices.conditions import get_injured, get_ill
from scripts.clan_package.cotc import change_clan_reputation, change_clan_relations
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.clan_package.settings import get_clan_setting
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.text_adjust import adjust_list_text
from scripts.game_structure import game
from scripts.game_structure.constants import HERBS

disable_random: bool = False


def handle_focus():
    """
    Checks the current focus setting and handles all immediate affects.
    """
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
    # handle warrior
    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )

    warrior_amount = len(healthy_warriors) * get_config(
        f"focus.hunting.{CatRank.WARRIOR}"
    )

    # handle apprentices
    healthy_apprentices = find_alive_cats_with_rank(
        Cat, ranks=[CatRank.APPRENTICE], working=True
    )

    app_amount = len(healthy_apprentices) * get_config(
        f"focus.hunting.{CatRank.APPRENTICE}"
    )

    # finish
    total_amount = warrior_amount + app_amount
    game.clan.freshkill_pile.add_freshkill(total_amount)
    focus_text = i18n.t("focus.focus_prey", count=total_amount)
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

    return game.clan.herb_supply.handle_focus(healthy_meds, healthy_warriors)


def _threaten_outsiders() -> str:
    """
    Lowers relations with outsiders
    """
    amount = get_config("focus.outsiders.reputation")
    change_clan_reputation(-amount)
    return i18n.t("focus.threaten_outsiders")


def _seek_outsiders() -> str:
    """
    Increases relations with outsiders
    """
    amount = get_config("focus.outsiders.reputation")
    change_clan_reputation(amount)
    return i18n.t("focus.seek_outsiders")


def _sabotage_clans() -> str:
    """
    Lowers relationships with target clans
    """
    amount = get_config("focus.other_clans.relation")
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
    amount = get_config("focus.other_clans.relation")
    for name in game.clan.clans_in_focus:
        clan = [clan for clan in game.clan.all_other_clans if clan.name == name][0]
        change_clan_relations(clan, amount)
    return i18n.t("focus.aid_clans", clan=adjust_list_text(game.clan.clans_in_focus))


def _raid_clans() -> str:
    """
    Lowers relations with target clans and steals herbs/prey from them, can injure cats as a result
    """
    info_dict = get_config("focus.raid_other_clans")

    injured_cats = []

    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )

    prey_recovered = 0
    for _c in healthy_warriors:
        if disable_random:
            prey_recovered += 1
        else:
            prey_recovered += choices(
                info_dict["prey_amounts"], info_dict["prey_weights"]
            )[0]

    # HANDLE HERBS
    herb_amount_to_gain = 0
    for _c in healthy_warriors:
        if disable_random:
            herb_amount_to_gain += 1
        else:
            herb_amount_to_gain += choices(
                info_dict["herb_amounts"], info_dict["herb_weights"]
            )[0]

    gathered_herbs = {}
    while herb_amount_to_gain:
        amount = randint(1, herb_amount_to_gain)
        gathered_herbs[choice(list(HERBS.keys()))] = amount
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
    else:
        herbs_recovered = []

    # HANDLE INJURIES
    injury_chance = info_dict["injury_chance"] - (
        len(game.clan.clans_in_focus * info_dict["chance_increase_per_clan"])
    )

    for cat in healthy_warriors:
        if not int(random() * max(2, injury_chance)) or disable_random:
            injury_dict = info_dict["injuries"]
            chosen_injury = choices(
                list(injury_dict.keys()), list(injury_dict.values())
            )[0]
            get_injured(cat, chosen_injury)
            injured_cats.append(cat.ID)

    for name in game.clan.clans_in_focus:
        clan = [clan for clan in game.clan.all_other_clans if clan.name == name][0]
        amount = get_config("focus.raid_other_clans.relation")
        change_clan_relations(clan, amount)

    text = []
    if prey_recovered:
        prey_text = i18n.t("focus.raid_prey", count=prey_recovered)
        game.clan.freshkill_pile.add_freshkill(prey_recovered)

        game.freshkill_event_list.append(prey_text)
        text.append(prey_text)
    if herbs_recovered:
        text.append(i18n.t("focus.raid_herb", herbs=herbs_recovered))

    text.append(
        i18n.t("focus.raid_relations", clan=adjust_list_text(game.clan.clans_in_focus))
    )

    if injured_cats:
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
    involved_cats = {"injured": [], "sick": []}

    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )
    prey_recovered = len(healthy_warriors) * info_dict["prey_warrior"]

    healthy_meds = list(
        filter(
            lambda c: c.status.rank == CatRank.MEDICINE_CAT
            and c.status.alive_in_player_clan
            and not c.not_working(),
            Cat.all_cats.values(),
        )
    )

    injury_chance_warrior = info_dict["injury_chance_warrior"]
    injury_chance_medicine_cat = info_dict["injury_chance_medicine_cat"]
    illness_chance = info_dict["illness_chance"]

    for cat in healthy_warriors + healthy_meds:
        if cat in healthy_warriors:
            injury_chance = injury_chance_warrior
        else:
            injury_chance = injury_chance_medicine_cat

        if not int(random() * injury_chance) or disable_random:
            injury_dict = info_dict["injuries"]
            chosen_injury = choices(
                list(injury_dict.keys()), list(injury_dict.values())
            )[0]
            get_injured(cat, chosen_injury)
            involved_cats["injured"].append(cat.ID)
        elif not int(random() * illness_chance) or disable_random:
            illness_dict = info_dict["illnesses"]
            chosen_illness = choices(
                list(illness_dict.keys()), list(illness_dict.values())
            )[0]
            get_ill(cat, chosen_illness)
            involved_cats["sick"].append(cat.ID)

    text = []
    if healthy_meds:
        herb_focus_text = game.clan.herb_supply.handle_focus(healthy_meds)
        text.append(herb_focus_text)
    if prey_recovered:
        prey_text = i18n.t("focus.focus_prey", count=prey_recovered)
        game.clan.freshkill_pile.add_freshkill(prey_recovered)

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
