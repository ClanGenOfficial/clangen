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
    deputy_buff = 0
    buffs = get_config("focus.hunting.buff")
    for skill, tier in game.clan.deputy.skills.get_all().items():
        skill = skill.name
        if skill not in buffs.keys():
            continue
        if buffs[skill]["tier"] > tier:
            continue

        if "biome" in buffs[skill]:
            if game.clan.biome.casefold() in buffs[skill]["biome"]:
                deputy_buff = buffs[skill]["prey_increase"]
        else:
            deputy_buff = buffs[skill]["prey_increase"]

    # handle warrior
    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )

    prey_amount = 0
    season = game.clan.current_season.casefold()
    warrior_prey = get_config(f"focus.hunting.warrior.{season}.prey_amounts")
    warrior_weights = get_config(f"focus.hunting.warrior.{season}.prey_weights")
    for _c in healthy_warriors:
        if disable_random:
            prey_amount += warrior_prey[1] + deputy_buff
        else:
            prey_amount += choices(warrior_prey, warrior_weights)[0] + deputy_buff

    # handle apprentices
    healthy_apprentices = find_alive_cats_with_rank(
        Cat, ranks=[CatRank.APPRENTICE], working=True
    )

    app_prey = get_config(f"focus.hunting.apprentice.{season}.prey_amounts")
    app_weights = get_config(f"focus.hunting.apprentice.{season}.prey_weights")
    for _c in healthy_apprentices:
        if disable_random:
            prey_amount += app_prey[1] + deputy_buff
        else:
            prey_amount += choices(app_prey, app_weights)[0] + deputy_buff

    # finish
    game.clan.freshkill_pile.add_freshkill(prey_amount)
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

    return game.clan.herb_supply.handle_focus(
        healthy_meds, healthy_warriors, gather_max_increase, quantity_increase
    )


def _threaten_outsiders() -> str:
    """
    Lowers relations with outsiders
    """
    amount = get_config("focus.threaten_outsiders.reputation")

    buffs = get_config("focus.threaten_outsiders.buff")

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
    amount = get_config("focus.seek_outsiders.reputation")

    buffs = get_config("focus.seek_outsiders.buff")

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
    amount = get_config("focus.sabotage_other_clans.relation")

    buffs = get_config("focus.sabotage_other_clans.buff")

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

    buffs = get_config("focus.raid_other_clans.buff")

    injury_modifier = 0
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

    injured_cats = []

    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )

    prey_recovered = 0
    for _c in healthy_warriors:
        if disable_random:
            prey_recovered += 1 + supply_amount_buff
        else:
            prey_recovered += (
                choices(info_dict["prey_amounts"], info_dict["prey_weights"])[0]
                + supply_amount_buff
            )

    # HANDLE HERBS
    herb_amount_to_gain = 0
    for _c in healthy_warriors:
        if disable_random:
            herb_amount_to_gain += 1 + supply_amount_buff
        else:
            herb_amount_to_gain += (
                choices(info_dict["herb_amounts"], info_dict["herb_weights"])[0]
                + supply_amount_buff
            )

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
    injury_chance = (
        round(
            info_dict["injury_chance"]
            - (len(game.clan.clans_in_focus * info_dict["chance_increase_per_clan"]))
        )
        * injury_modifier
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

    buffs = get_config("focus.hoarding.buff")
    condition_modifier = 0
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

    prey_recovered = 0
    healthy_warriors = find_alive_cats_with_rank(
        Cat,
        ranks=[CatRank.WARRIOR, CatRank.DEPUTY, CatRank.LEADER],
        working=True,
    )
    season = game.clan.current_season.casefold()
    warrior_prey = get_config(f"focus.hunting.warrior.{season}.prey_amounts")
    warrior_weights = get_config(f"focus.hunting.warrior.{season}.prey_weights")
    for _c in healthy_warriors:
        if disable_random:
            prey_recovered += warrior_prey[1] + prey_increase
        else:
            prey_recovered += choices(warrior_prey, warrior_weights)[0] + prey_increase

    # handle apprentices
    healthy_apprentices = find_alive_cats_with_rank(
        Cat, ranks=[CatRank.APPRENTICE], working=True
    )

    app_prey = get_config(f"focus.hunting.apprentice.{season}.prey_amounts")
    app_weights = get_config(f"focus.hunting.apprentice.{season}.prey_weights")
    for _c in healthy_apprentices:
        if disable_random:
            prey_recovered += app_prey[1] + prey_increase
        else:
            prey_recovered += choices(app_prey, app_weights)[0] + prey_increase
    healthy_meds = list(
        filter(
            lambda c: c.status.rank == CatRank.MEDICINE_CAT
            and c.status.alive_in_player_clan
            and not c.not_working(),
            Cat.all_cats.values(),
        )
    )

    injury_chance_warrior = info_dict["injury_chance_warrior"] * condition_modifier
    injury_chance_medicine_cat = (
        info_dict["injury_chance_medicine_cat"] * condition_modifier
    )
    illness_chance = info_dict["illness_chance"] * condition_modifier

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
        herb_focus_text = game.clan.herb_supply.handle_focus(
            healthy_meds, healthy_warriors, max_buff=gather_max_increase
        )
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
