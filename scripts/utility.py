# pylint: disable=line-too-long
"""

TODO: Docs


"""  # pylint: enable=line-too-long

import logging
import os
import re
import traceback
from math import floor
from random import choice, randint, sample
from sys import exit as sys_exit
from typing import List, TYPE_CHECKING, Type

import i18n
import pygame
import ujson
from pygame_gui.core import ObjectID

from scripts.cat import pronouns
from scripts.cat.pronouns import get_pronouns, determine_plural_pronouns
from scripts.cat_relations.enums import RelType
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure.game.settings import game_settings_save, game_setting_get
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.localization import (
    load_lang_resource,
    get_lang_config,
)
from scripts.ui.scale import ui_scale_dimensions

logger = logging.getLogger(__name__)
from scripts.game_structure import image_cache, localization, constants
from scripts.cat.enums import (
    CatAge,
    CatRank,
    CatGroup,
)
from scripts.cat.sprites import sprites
from scripts.game_structure import game
import scripts.game_structure.screen_settings  # must be done like this to get updates when we change screen size etc

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


# ---------------------------------------------------------------------------- #
#                               Getting Cats                                   #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                          Handling Outside Factors                            #
# ---------------------------------------------------------------------------- #


def get_current_season():
    """
    function to handle the math for finding the Clan's current season
    :return: the Clan's current season
    """

    if constants.CONFIG["lock_season"]:
        game.clan.current_season = game.clan.starting_season
        return game.clan.starting_season

    modifiers = {"Newleaf": 0, "Greenleaf": 3, "Leaf-fall": 6, "Leaf-bare": 9}
    index = game.clan.age % 12 + modifiers[game.clan.starting_season]

    if index > 11:
        index = index - 12

    game.clan.current_season = constants.SEASON_CALENDAR[index]

    return game.clan.current_season


# ---------------------------------------------------------------------------- #
#                             Cat Relationships                                #
# ---------------------------------------------------------------------------- #


# todo: kill this function. with fire.
def get_num_of_cats_with_relation_amount_towards(cat, amount, all_cats):
    """
    Looks how many cats have the certain value
    :param cat: cat in question
    :param amount: amount of relationship value which has to be reached
    :param all_cats: list of cats which has to be checked
    """

    # collect all true or false if the value is reached for the cat or not
    # later count or sum can be used to get the amount of cats
    # this will be handled like this, because it is easier / shorter to check

    relation_dict = {v: [] for v in [*RelType]}

    for inter_cat in all_cats:
        if cat.ID in inter_cat.relationships:
            relation = inter_cat.relationships[cat.ID]
        else:
            continue

        for value in [*RelType]:
            if amount > 0:
                relation_dict[value].append(
                    relation.get_amount_of_type(value) >= amount
                )
            elif amount < 0:
                relation_dict[value].append(
                    relation.get_amount_of_type(value) <= amount
                )

    return_dict = {v: sum(relation_dict[v]) for v in [*RelType]}

    return return_dict


# ---------------------------------------------------------------------------- #
#                               Text Adjust                                    #
# ---------------------------------------------------------------------------- #


def get_leader_life_notice() -> str:
    """
    Returns a string specifying how many lives the leader has left or notifying of the leader's full death
    """
    if game.clan.instructor.status.group == CatGroup.DARK_FOREST:
        return i18n.t("cat.history.leader_lives_left_df", count=game.clan.leader_lives)
    return i18n.t("cat.history.leader_lives_left_sc", count=game.clan.leader_lives)


def pronoun_repl(m, cat_pronouns_dict, raise_exception=False):
    """
    Helper function for add_pronouns.
    :param m: Snippet to pronounify
    :param cat_pronouns_dict: Cats to pronounify
    :param raise_exception: If True, will raise an exception if a mistake is found. Necessary for tests!
    :return: Appropriate pronoun/verb/adjective
    :raises KeyError: if cat doesn't have requested pronoun
    :raises IndexError: if cat doesn't have requested pronoun
    """

    # Add protection about the "insert" sometimes used
    if m.group(0) == "{insert}":
        return m.group(0)

    inner_details = m.group(1).split("/")
    out = None

    try:
        if inner_details[1].upper() == "PLURAL":
            inner_details.pop(1)  # remove plural tag so it can be processed as normal
            catlist = []
            for cat in inner_details[1].split("+"):
                try:
                    catlist.append(cat_pronouns_dict[cat][1])
                except KeyError as e:
                    print(f"Missing pronouns for {cat}")
                    if raise_exception:
                        raise e
                    continue
            d = determine_plural_pronouns(catlist)
        else:
            try:
                d = cat_pronouns_dict[inner_details[1]][1]
            except KeyError as e:
                if raise_exception:
                    raise e

                if inner_details[0].upper() == "ADJ":
                    # find the default - this is a semi-expected behaviour for the adj tag as it may be called when
                    # there is no relevant cat
                    return inner_details[localization.get_default_adj()]
                else:
                    logger.warning(
                        f"Could not get pronouns for {inner_details[1]}. Using default."
                    )
                    print(
                        f"Could not get pronouns for {inner_details[1]}. Using default."
                    )
                    d = choice(pronouns.get_new_pronouns("default"))

        if inner_details[0].upper() == "PRONOUN":
            out = d[inner_details[2]]
        elif inner_details[0].upper() == "VERB":
            out = inner_details[d["conju"] + 1]
        elif inner_details[0].upper() == "ADJ":
            out = inner_details[(d["gender"] + 2) if "gender" in d else 2]

        if out is not None:
            if inner_details[-1] == "CAP":
                out = out.capitalize()
            return out

        if raise_exception:
            raise KeyError(
                f"Pronoun tag: {m.group(1)} is not properly"
                "indicated as a PRONOUN or VERB tag."
            )

        print("Failed to find pronoun:", m.group(1))
        return "error1"
    except (KeyError, IndexError) as e:
        if raise_exception:
            raise

        logger.exception("Failed to find pronoun: " + m.group(1))
        print("Failed to find pronoun:", m.group(1))
        return "error2"


def name_repl(m, cat_dict):
    """Name replacement"""
    return cat_dict[m.group(0)][0]


def process_text(text, cat_dict, raise_exception=False):
    """Add the correct name and pronouns into a string."""
    adjust_text = re.sub(
        r"(?<!%)\{(.*?)}", lambda x: pronoun_repl(x, cat_dict, raise_exception), text
    )

    name_patterns = [r"(?<!\{)" + re.escape(l) + r"(?!\})" for l in cat_dict]
    adjust_text = re.sub(
        "|".join(name_patterns), lambda x: name_repl(x, cat_dict), adjust_text
    )
    return adjust_text


def adjust_list_text(list_of_items: List) -> str:
    """
    returns the list in correct grammar format (i.e. item1, item2, item3 and item4)
    this works with any number of items
    :param list_of_items: the list of items you want converted
    :return: the new string
    """

    if not isinstance(list_of_items, list):
        logger.warning("non-list object was passed to adjust_list_text")
        list_of_items = list(list_of_items)

    if len(list_of_items) == 0:
        item1 = ""
        item2 = ""
    elif len(list_of_items) == 1:
        item1 = list_of_items[0]
        item2 = ""
    elif len(list_of_items) == 2:
        item1 = list_of_items[0]
        item2 = list_of_items[1]
    else:
        item1 = ", ".join(list_of_items[:-1])
        if get_lang_config().get("oxford_comma"):
            item1 += ","
        item2 = list_of_items[-1]

    return i18n.t("utility.items", count=len(list_of_items), item1=item1, item2=item2)


def adjust_prey_abbr(patrol_text):
    """
    checks for prey abbreviations and returns adjusted text
    """
    global PREY_LISTS
    if langs["prey"] != i18n.config.get("locale"):
        langs["prey"] = i18n.config.get("locale")
        PREY_LISTS = load_lang_resource("patrols/prey_text_replacements.json")

    for abbr in PREY_LISTS["abbreviations"]:
        if abbr in patrol_text:
            chosen_list = PREY_LISTS["abbreviations"].get(abbr)
            chosen_list = PREY_LISTS[chosen_list]
            prey = choice(chosen_list)
            patrol_text = patrol_text.replace(abbr, prey)

    return patrol_text


def get_special_snippet_list(
    chosen_list, amount, sense_groups=None, return_string=True
):
    """
    function to grab items from various lists in snippet_collections.json
    list options are:
    -prophecy_list - sense_groups = sight, sound, smell, emotional, touch
    -omen_list - sense_groups = sight, sound, smell, emotional, touch
    -clair_list  - sense_groups = sound, smell, emotional, touch, taste
    -dream_list (this list doesn't have sense_groups)
    -story_list (this list doesn't have sense_groups)
    :param chosen_list: pick which list you want to grab from
    :param amount: the amount of items you want the returned list to contain
    :param sense_groups: list which senses you want the snippets to correspond with:
     "touch", "sight", "emotional", "sound", "smell" are the options. Default is None, if left as this then all senses
     will be included (if the list doesn't have sense categories, then leave as None)
    :param return_string: if True then the function will format the snippet list with appropriate commas and 'ands'.
    This will work with any number of items. If set to True, then the function will return a string instead of a list.
    (i.e. ["hate", "fear", "dread"] becomes "hate, fear, and dread") - Default is True
    :return: a list of the chosen items from chosen_list or a formatted string if format is True
    """
    biome = (
        game.clan.biome if not game.clan.override_biome else game.clan.override_biome
    ).casefold()
    global SNIPPETS
    if langs["snippet"] != i18n.config.get("locale"):
        langs["snippet"] = i18n.config.get("locale")
        SNIPPETS = load_lang_resource("snippet_collections.json")

    # these lists don't get sense specific snippets, so is handled first
    if chosen_list in ["dream_list", "story_list"]:
        if (
            chosen_list == "story_list"
        ):  # story list has some biome specific things to collect
            snippets = SNIPPETS[chosen_list]["general"]
            snippets.extend(SNIPPETS[chosen_list][biome])
        elif (
            chosen_list == "clair_list"
        ):  # the clair list also pulls from the dream list
            snippets = SNIPPETS[chosen_list]
            snippets.extend(SNIPPETS["dream_list"])
        else:  # the dream list just gets the one
            snippets = SNIPPETS[chosen_list]

    else:
        # if no sense groups were specified, use all of them
        if not sense_groups:
            if chosen_list == "clair_list":
                sense_groups = ["taste", "sound", "smell", "emotional", "touch"]
            else:
                sense_groups = ["sight", "sound", "smell", "emotional", "touch"]

        # find the correct lists and compile them
        snippets = []
        for sense in sense_groups:
            snippet_group = SNIPPETS[chosen_list][sense]
            snippets.extend(snippet_group["general"])
            snippets.extend(snippet_group[biome])

    # now choose a unique snippet from each snip list
    unique_snippets = []
    for snip_list in snippets:
        unique_snippets.append(choice(snip_list))

    # pick out our final snippets
    final_snippets = sample(unique_snippets, k=amount)

    if return_string:
        text = adjust_list_text(final_snippets)
        return text
    else:
        return final_snippets


def find_special_list_types(text):
    """
    purely to identify which senses are being called for by a snippet abbreviation
    returns adjusted text, sense list, list type, and cat_tag
    """
    senses = []
    list_text = None
    words = text.split(" ")
    for bit in words:
        if "_list" in bit:
            list_text = bit
            # just getting rid of pesky punctuation
            list_text = list_text.replace(".", "")
            list_text = list_text.replace(",", "")
            break

    if not list_text:
        return text, None, None, None

    parts_of_tag = list_text.split("/")

    try:
        cat_tag = parts_of_tag[1]
    except IndexError:
        cat_tag = None

    if "omen_list" in list_text:
        list_type = "omen_list"
    elif "prophecy_list" in list_text:
        list_type = "prophecy_list"
    elif "dream_list" in list_text:
        list_type = "dream_list"
    elif "clair_list" in list_text:
        list_type = "clair_list"
    elif "story_list" in list_text:
        list_type = "story_list"
    else:
        logger.error("WARNING: no list type found for %s", list_text)
        return text, None, None, None

    if "_sight" in list_text:
        senses.append("sight")
    if "_sound" in list_text:
        senses.append("sound")
    if "_smell" in list_text:
        senses.append("smell")
    if "_emotional" in list_text:
        senses.append("emotional")
    if "_touch" in list_text:
        senses.append("touch")
    if "_taste" in list_text:
        senses.append("taste")

    text = text.replace(list_text, list_type)

    return text, senses, list_type, cat_tag


def history_text_adjust(text, other_clan_name, clan, other_cat_rc=None):
    """
    we want to handle history text on its own because it needs to preserve the pronoun tags and cat abbreviations.
    this is so that future pronoun changes or name changes will continue to be reflected in history
    """
    vowels = ["A", "E", "I", "O", "U"]

    if "o_c_n" in text:
        pos = 0
        for x in range(text.count("o_c_n")):
            if "o_c_n" in text:
                for y in vowels:
                    if str(other_clan_name).startswith(y):
                        modify = text.split()
                        if "o_c_n" in modify:
                            pos = modify.index("o_c_n")
                        if "o_c_n's" in modify:
                            pos = modify.index("o_c_n's")
                        if "o_c_n." in modify:
                            pos = modify.index("o_c_n.")
                        if modify[pos - 1] == "a":
                            modify.remove("a")
                            modify.insert(pos - 1, "an")
                        text = " ".join(modify)
                        break

        text = text.replace("o_c_n", str(other_clan_name))

    if "c_n" in text:
        text = text.replace("c_n", clan.displayname + "Clan")
    if "r_c" in text and other_cat_rc:
        text = selective_replace(text, "r_c", str(other_cat_rc.name))
    return text


def selective_replace(text, pattern, replacement):
    i = 0
    while i < len(text):
        index = text.find(pattern, i)
        if index == -1:
            break
        start_brace = text.rfind("{", 0, index)
        end_brace = text.find("}", index)
        if start_brace != -1 and end_brace != -1 and start_brace < index < end_brace:
            i = index + len(pattern)
        else:
            text = text[:index] + replacement + text[index + len(pattern) :]
            i = index + len(replacement)

    return text


def ongoing_event_text_adjust(Cat, text, clan=None, other_clan_name=None):
    """
    This function is for adjusting the text of ongoing events
    :param Cat: the cat class
    :param text: the text to be adjusted
    :param clan: the name of the clan
    :param other_clan_name: the other Clan's name if another Clan is involved
    """
    cat_dict = {}
    if "lead_name" in text:
        kitty = Cat.fetch_cat(game.clan.leader)
        cat_dict["lead_name"] = (str(kitty.name), choice(kitty.pronouns))
    if "dep_name" in text:
        kitty = Cat.fetch_cat(game.clan.deputy)
        cat_dict["dep_name"] = (str(kitty.name), choice(kitty.pronouns))
    if "med_name" in text:
        kitty = choice(
            find_alive_cats_with_rank(Cat, [CatRank.MEDICINE_CAT], working=True)
        )
        cat_dict["med_name"] = (str(kitty.name), choice(kitty.pronouns))

    if cat_dict:
        text = process_text(text, cat_dict)

    if other_clan_name:
        text = text.replace("o_c_n", other_clan_name)
    if clan:
        clan_name = str(clan.displayname)
    else:
        if game.clan is None:
            # todo can this be Switch.clan_name ?
            clan_name = switch_get_value(Switch.clan_list)[0]
        else:
            clan_name = str(game.clan.displayname)

    text = text.replace("c_n", clan_name + "Clan")

    return text


def event_text_adjust(
    Cat: Type["Cat"],
    text,
    *,
    patrol_leader=None,
    main_cat=None,
    random_cat=None,
    stat_cat=None,
    victim_cat=None,
    patrol_cats: list = None,
    patrol_apprentices: list = None,
    new_cats: list = None,
    multi_cats: list = None,
    clan=None,
    other_clan=None,
    chosen_herb: str = None,
):
    """
    handles finding abbreviations in the text and replacing them appropriately, returns the adjusted text
    :param Cat Cat: always pass the Cat class
    :param str text: the text being adjusted
    :param Cat patrol_leader: Cat object for patrol_leader (p_l), if present
    :param Cat main_cat: Cat object for main_cat (m_c), if present
    :param Cat random_cat: Cat object for random_cat (r_c), if present
    :param Cat stat_cat: Cat object for stat_cat (s_c), if present
    :param Cat victim_cat: Cat object for victim_cat (mur_c), if present
    :param list[Cat] patrol_cats: List of Cat objects for cats in patrol, if present
    :param list[Cat] patrol_apprentices: List of Cat objects for patrol_apprentices (app#), if present
    :param list[Cat] new_cats: List of Cat objects for new_cats (n_c:index), if present
    :param list[Cat] multi_cats: List of Cat objects for multi_cat (multi_cat), if present
    :param Clan clan: pass game.clan
    :param OtherClan other_clan: OtherClan object for other_clan (o_c_n), if present
    :param str chosen_herb: string of chosen_herb (chosen_herb), if present
    """
    vowels = ["A", "E", "I", "O", "U"]
    if not patrol_apprentices:
        patrol_apprentices = []
    if not new_cats:
        new_cats = []

    if not text:
        text = "This should not appear, report as a bug please! Tried to adjust the text, but no text was provided."
        print("WARNING: Tried to adjust text, but no text was provided.")

    # this check is really just here to catch odd bug edge-cases from old saves, specifically in death history
    # otherwise we should really *never* have lists being passed as the text
    if isinstance(text, list):
        text = text[0]

    replace_dict = {}

    # special lists - this needs to happen first for pronoun tag reasons
    text, senses, list_type, cat_tag = find_special_list_types(text)
    if list_type:
        sign_list = get_special_snippet_list(
            list_type, amount=randint(1, 3), sense_groups=senses
        )
        text = text.replace(list_type, str(sign_list))
        if cat_tag:
            text = text.replace("cat_tag", cat_tag)

    # main_cat
    if "m_c" in text:
        if main_cat:
            replace_dict["m_c"] = (str(main_cat.name), choice(main_cat.pronouns))

    # patrol_lead
    if "p_l" in text:
        if patrol_leader:
            replace_dict["p_l"] = (
                str(patrol_leader.name),
                choice(patrol_leader.pronouns),
            )

    # random_cat
    if "r_c" in text:
        if random_cat:
            replace_dict["r_c"] = (str(random_cat.name), get_pronouns(random_cat))

    # stat cat
    if "s_c" in text:
        if stat_cat:
            replace_dict["s_c"] = (str(stat_cat.name), get_pronouns(stat_cat))

    # other_cats
    if patrol_cats:
        other_cats = [
            i
            for i in patrol_cats
            if i not in [patrol_leader, random_cat, patrol_apprentices]
        ]
        other_cat_abbr = ["o_c1", "o_c2", "o_c3", "o_c4"]
        for i, abbr in enumerate(other_cat_abbr):
            if abbr not in text:
                continue
            if len(other_cats) > i:
                replace_dict[abbr] = (
                    str(other_cats[i].name),
                    choice(other_cats[i].pronouns),
                )

    # patrol_apprentices
    app_abbr = ["app1", "app2", "app3", "app4", "app5", "app6"]
    for i, abbr in enumerate(app_abbr):
        if abbr not in text:
            continue
        if len(patrol_apprentices) > i:
            replace_dict[abbr] = (
                str(patrol_apprentices[i].name),
                choice(patrol_apprentices[i].pronouns),
            )

    # new_cats (include pre version)
    if "n_c" in text:
        for i, cat_list in enumerate(new_cats):
            if len(new_cats) > 1:
                pronoun = pronouns.get_new_pronouns("default plural")[0]
            else:
                pronoun = choice(cat_list[0].pronouns)

            replace_dict[f"n_c:{i}"] = (str(cat_list[0].name), pronoun)
            replace_dict[f"n_c_pre:{i}"] = (str(cat_list[0].name.prefix), pronoun)

    # mur_c (murdered cat for reveals)
    if "mur_c" in text:
        replace_dict["mur_c"] = (str(victim_cat.name), get_pronouns(victim_cat))

    # lead_name
    if "lead_name" in text:
        leader = Cat.fetch_cat(game.clan.leader)
        replace_dict["lead_name"] = (str(leader.name), choice(leader.pronouns))

    # dep_name
    if "dep_name" in text:
        deputy = Cat.fetch_cat(game.clan.deputy)
        replace_dict["dep_name"] = (str(deputy.name), choice(deputy.pronouns))

    # med_name
    if "med_name" in text:
        med = choice(
            find_alive_cats_with_rank(Cat, [CatRank.MEDICINE_CAT], working=True)
        )
        replace_dict["med_name"] = (str(med.name), choice(med.pronouns))

    # assign all names and pronouns
    if replace_dict:
        text = process_text(text, replace_dict)

    # multi_cat
    if "multi_cat" in text:
        name_list = []
        for _cat in multi_cats:
            name_list.append(str(_cat.name))
        list_text = adjust_list_text(name_list)
        text = text.replace("multi_cat", list_text)

    # other_clan_name
    if "o_c_n" in text and other_clan:
        other_clan_name = other_clan.name
        pos = 0
        for x in range(text.count("o_c_n")):
            if "o_c_n" in text:
                for y in vowels:
                    if str(other_clan_name).startswith(y):
                        modify = text.split()
                        if "o_c_n" in modify:
                            pos = modify.index("o_c_n")
                        if "o_c_n's" in modify:
                            pos = modify.index("o_c_n's")
                        if "o_c_n." in modify:
                            pos = modify.index("o_c_n.")
                        if modify[pos - 1] == "a":
                            modify.remove("a")
                            modify.insert(pos - 1, "an")
                        text = " ".join(modify)
                        break

        text = text.replace("o_c_n", str(other_clan_name) + "Clan")

    # clan_name
    if "c_n" in text:
        try:
            clan_name = clan.displayname
        except AttributeError:
            # todo can this be Switch.clan_name ?
            clan_name = switch_get_value(Switch.clan_list)[0]

        pos = 0
        for x in range(text.count("c_n")):
            if "c_n" in text:
                for y in vowels:
                    if str(clan_name).startswith(y):
                        modify = text.split()
                        if "c_n" in modify:
                            pos = modify.index("c_n")
                        if "c_n's" in modify:
                            pos = modify.index("c_n's")
                        if "c_n." in modify:
                            pos = modify.index("c_n.")
                        if modify[pos - 1] == "a":
                            modify.remove("a")
                            modify.insert(pos - 1, "an")
                        text = " ".join(modify)
                        break

        text = text.replace("c_n", str(clan_name) + "Clan")

    # prey lists
    text = adjust_prey_abbr(text)

    # acc_plural (only works for main_cat's acc)
    if main_cat:
        if "acc_plural" in text:
            text = text.replace(
                "acc_plural",
                i18n.t(f"cat.accessories.{main_cat.pelt.accessory[-1]}", count=2),
            )

        # acc_singular (only works for main_cat's acc)
        if "acc_singular" in text:
            accessory_name = main_cat.pelt.accessory[-1]
            if sprites.COLLAR_DATA["palette_map"]:
                potential_collar = "".join(
                    [x for x in accessory_name if not x.islower()]
                ).strip("_")
                for style in main_cat.pelt.collar_styles:
                    if style == potential_collar:
                        accessory_name = potential_collar
                        break
            text = text.replace(
                "acc_singular",
                i18n.t(f"cat.accessories.{accessory_name}", count=1),
            )

        if "given_herb" in text:
            text = text.replace(
                "given_herb", i18n.t(f"conditions.herbs.{chosen_herb}", count=2)
            )

    return text


def leader_ceremony_text_adjust(
    Cat,
    text,
    leader,
    life_giver=None,
    virtue=None,
    extra_lives=None,
):
    """
    used to adjust the text for leader ceremonies
    """
    replace_dict = {
        "m_c_star": (str(leader.name.prefix + "star"), choice(leader.pronouns)),
        "m_c": (str(leader.name.prefix + leader.name.suffix), choice(leader.pronouns)),
    }

    if life_giver:
        replace_dict["r_c"] = (
            str(Cat.fetch_cat(life_giver).name),
            choice(Cat.fetch_cat(life_giver).pronouns),
        )

    text = process_text(text, replace_dict)

    if virtue:
        virtue = process_text(virtue, replace_dict)
        text = text.replace("[virtue]", virtue)

    if extra_lives:
        text = text.replace("[life_num]", str(extra_lives))

    text = text.replace("c_n", str(game.clan.displayname) + "Clan")

    return text


def ceremony_text_adjust(
    Cat,
    text,
    cat,
    old_name=None,
    dead_mentor=None,
    mentor=None,
    previous_alive_mentor=None,
    random_honor=None,
    living_parents=(),
    dead_parents=(),
):
    clanname = str(game.clan.displayname + "Clan")

    random_honor = random_honor
    random_living_parent = None
    random_dead_parent = None

    adjust_text = text

    cat_dict = {
        "m_c": (
            (str(cat.name), choice(cat.pronouns)) if cat else ("cat_placeholder", None)
        ),
        "(mentor)": (
            (str(mentor.name), choice(mentor.pronouns))
            if mentor
            else ("mentor_placeholder", None)
        ),
        "(deadmentor)": (
            (str(dead_mentor.name), get_pronouns(dead_mentor))
            if dead_mentor
            else ("dead_mentor_name", None)
        ),
        "(previous_mentor)": (
            (str(previous_alive_mentor.name), choice(previous_alive_mentor.pronouns))
            if previous_alive_mentor
            else ("previous_mentor_name", None)
        ),
        "l_n": (
            (str(game.clan.leader.name), choice(game.clan.leader.pronouns))
            if game.clan.leader
            else ("leader_name", None)
        ),
        "c_n": (clanname, None),
    }

    if old_name:
        cat_dict["(old_name)"] = (old_name, None)

    if random_honor:
        cat_dict["r_h"] = (random_honor, None)

    if "p1" in adjust_text and "p2" in adjust_text and len(living_parents) >= 2:
        cat_dict["p1"] = (
            str(living_parents[0].name),
            choice(living_parents[0].pronouns),
        )
        cat_dict["p2"] = (
            str(living_parents[1].name),
            choice(living_parents[1].pronouns),
        )
    elif living_parents:
        random_living_parent = choice(living_parents)
        cat_dict["p1"] = (
            str(random_living_parent.name),
            choice(random_living_parent.pronouns),
        )
        cat_dict["p2"] = (
            str(random_living_parent.name),
            choice(random_living_parent.pronouns),
        )

    if (
        "dead_par1" in adjust_text
        and "dead_par2" in adjust_text
        and len(dead_parents) >= 2
    ):
        cat_dict["dead_par1"] = (
            str(dead_parents[0].name),
            get_pronouns(dead_parents[0]),
        )
        cat_dict["dead_par2"] = (
            str(dead_parents[1].name),
            get_pronouns(dead_parents[1]),
        )
    elif dead_parents:
        random_dead_parent = choice(dead_parents)
        cat_dict["dead_par1"] = (
            str(random_dead_parent.name),
            get_pronouns(random_dead_parent),
        )
        cat_dict["dead_par2"] = (
            str(random_dead_parent.name),
            get_pronouns(random_dead_parent),
        )

    adjust_text = process_text(adjust_text, cat_dict)

    return adjust_text, random_living_parent, random_dead_parent


def shorten_text_to_fit(
    name, length_limit, font_size=None, font_type="resources/fonts/NotoSans-Medium.ttf"
):
    length_limit = length_limit * scripts.game_structure.screen_settings.screen_scale
    if font_size is None:
        font_size = 15
    font_size = floor(font_size * scripts.game_structure.screen_settings.screen_scale)

    if font_type == "clangen":
        font_type = "resources/fonts/clangen.ttf"
    # Create the font object
    font = pygame.font.Font(font_type, font_size)

    # Add dynamic name lengths by checking the actual width of the text
    total_width = 0
    short_name = ""
    ellipsis_width = font.size("...")[0]
    for index, character in enumerate(name):
        char_width = font.size(character)[0]

        # Check if the current character is the last one and its width is less than or equal to ellipsis_width
        if index == len(name) - 1 and char_width <= ellipsis_width:
            short_name += character
        else:
            total_width += char_width
            if total_width + ellipsis_width > length_limit:
                break
            short_name += character

    # If the name was truncated, add "..."
    if len(short_name) < len(name):
        short_name += "..."

    return short_name


# ---------------------------------------------------------------------------- #
#                                    Sprites                                   #
# ---------------------------------------------------------------------------- #


def update_sprite(cat):
    # First, check if the cat is faded.
    if cat.faded:
        # Don't update the sprite if the cat is faded.
        return

    # apply
    cat.sprite = generate_sprite(cat)
    # update class dictionary
    cat.all_cats[cat.ID] = cat


def update_mask(cat):
    if cat.faded or cat.dead:
        # should never need a mask since they can't appear on the Clan screen
        cat.sprite_mask = None
        return

    val = pygame.mask.from_surface(
        pygame.transform.scale(cat.sprite, ui_scale_dimensions((50, 50))), threshold=250
    )

    inflated_mask = pygame.Mask(
        (
            val.get_size()[0] + 10,
            val.get_size()[1] + 10,
        )
    )
    inflated_mask.draw(val, (5, 5))
    for _ in range(3):
        outline = inflated_mask.outline()
        for point in outline:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    try:
                        inflated_mask.set_at((point[0] + dx, point[1] + dy), 1)
                    except IndexError:
                        continue
    cat.sprite_mask = inflated_mask


def clan_symbol_sprite(clan, return_string=False, force_light=False):
    """
    returns the clan symbol for the given clan_name, if no symbol exists then random symbol is chosen
    :param clan: the clan object
    :param return_string: default False, set True if the sprite name string is required rather than the sprite image
    :param force_light: Set true if you want this sprite to override the dark/light mode changes with the light sprite
    """
    if not clan.chosen_symbol:
        possible_sprites = []
        for sprite in sprites.clan_symbols:
            name = sprite.strip("1234567890")
            if f"symbol{clan.name.upper()}" == name:
                possible_sprites.append(sprite)
        if possible_sprites:
            clan.chosen_symbol = choice(possible_sprites)
        else:
            # give random symbol if no matching symbol exists
            print(
                f"WARNING: attempted to return symbol, but there's no clan symbol for {clan.name.upper()}. "
                f"Random chosen."
            )
            clan.chosen_symbol = choice(sprites.clan_symbols)

    if return_string:
        return clan.chosen_symbol
    else:
        return sprites.get_symbol(clan.chosen_symbol, force_light=force_light)


def generate_sprite(
    cat,
    life_state=None,
    scars_hidden=False,
    acc_hidden=False,
    always_living=False,
    disable_sick_sprite=False,
) -> pygame.Surface:
    """
    Generates the sprite for a cat, with optional arguments that will override certain things.

    :param life_state: sets the age life_stage of the cat, overriding the one set by its age. Set to string.
    :param scars_hidden: If True, doesn't display the cat's scars. If False, display cat scars.
    :param acc_hidden: If True, hide the accessory. If false, show the accessory.
    :param always_living: If True, always show the cat with living lineart
    :param disable_sick_sprite: If true, never use the not_working lineart.
                    If false, use the cat.not_working() to determine the no_working art.
    """
    sprite_poses = sprites.POSE_DATA["poses"]

    if life_state is not None:
        age = life_state
    else:
        age = cat.age

    if always_living:
        dead = False
    else:
        dead = cat.dead

    # setting the cat_sprite (bc this makes things much easier)

    # sick sprites
    if (
        not disable_sick_sprite
        and cat.not_working()
        and age != CatAge.NEWBORN
        and constants.CONFIG["cat_sprites"]["sick_sprites"]
    ):
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            cat_sprite = sprite_poses["sick_young0"]
        else:
            cat_sprite = sprite_poses["sick_adult0"]

    # paralyzed sprites
    elif cat.pelt.paralyzed and age != CatAge.NEWBORN:
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            cat_sprite = sprite_poses["para_young0"]
        else:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites["para_adult"]]

    # default sprites
    else:
        if constants.CONFIG["fun"]["all_cats_are_newborn"]:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites["newborn"]]
        else:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites[age]]

    new_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    # generating the sprite
    try:
        if cat.pelt.name not in ["Tortie", "Calico"]:
            new_sprite.blit(
                sprites.sprites[
                    cat.pelt.get_sprites_name() + cat.pelt.colour + cat_sprite
                ],
                (0, 0),
            )
        else:
            # Base Coat
            sprite_name = f"colours_{cat.pelt.tortie_base}{cat.pelt.colour}{cat_sprite}"
            new_sprite.blit(
                sprites.sprites[sprite_name],
                (0, 0),
            )

            # Create the patch image
            if cat.pelt.tortie_pattern == "Single":
                tortie_pattern = "SingleColour"
            else:
                tortie_pattern = cat.pelt.tortie_pattern

            sprite_name = (
                f"colours_{tortie_pattern}{cat.pelt.tortie_colour}{cat_sprite}"
            )
            patches = sprites.sprites[sprite_name].copy()
            sprite_name = f"{sprites.TORTIE_DATA['spritesheet']}{cat.pelt.tortie_marking}{cat_sprite}"
            patches.blit(
                sprites.sprites[sprite_name],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            # Add patches onto cat.
            new_sprite.blit(patches, (0, 0))

        # TINTS
        if (
            cat.pelt.tint is not None
            and cat.pelt.tint in sprites.cat_tints["tint_colours"]
        ):
            # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
            # entire surface. To get around this, we first blit the tint onto a white background to dull it,
            # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        if (
            cat.pelt.tint is not None
            and cat.pelt.tint in sprites.cat_tints["dilute_tint_colours"]
        ):
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # draw white patches
        if cat.pelt.white_patches is not None:
            sprite_name = f"{sprites.WHITE_DATA['spritesheet']}{cat.pelt.white_patches}{cat_sprite}"
            white_patches = sprites.sprites[sprite_name].copy()

            # Apply tint to white patches.
            if (
                cat.pelt.white_patches_tint is not None
                and cat.pelt.white_patches_tint
                in sprites.white_patches_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(
                    tuple(
                        sprites.white_patches_tints["tint_colours"][
                            cat.pelt.white_patches_tint
                        ]
                    )
                )
                white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            new_sprite.blit(white_patches, (0, 0))

        # draw vit & points

        if cat.pelt.points:
            sprite_name = (
                f"{sprites.WHITE_DATA['spritesheet']}{cat.pelt.points}{cat_sprite}"
            )

            points = sprites.sprites[sprite_name].copy()
            if (
                cat.pelt.white_patches_tint is not None
                and cat.pelt.white_patches_tint
                in sprites.white_patches_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(
                    tuple(
                        sprites.white_patches_tints["tint_colours"][
                            cat.pelt.white_patches_tint
                        ]
                    )
                )
                points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            new_sprite.blit(points, (0, 0))

        if cat.pelt.vitiligo:
            sprite_name = (
                f"{sprites.WHITE_DATA['spritesheet']}{cat.pelt.vitiligo}{cat_sprite}"
            )

            new_sprite.blit(
                sprites.sprites[sprite_name],
                (0, 0),
            )

        # draw eyes & scars1
        sprite_name = (
            f"{sprites.EYE_DATA['spritesheet'][0]}{cat.pelt.eye_colour}{cat_sprite}"
        )
        eyes = sprites.sprites[sprite_name].copy()
        if cat.pelt.eye_colour2 != None:
            sprite_name = f"{sprites.EYE_DATA['spritesheet'][1]}{cat.pelt.eye_colour2}{cat_sprite}"
            eyes.blit(
                sprites.sprites[sprite_name],
                (0, 0),
            )
        new_sprite.blit(eyes, (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.general_scars:
                    sprite_name = (
                        f"{sprites.SCAR_DATA['spritesheet']}{scar}{cat_sprite}"
                    )
                    new_sprite.blit(
                        sprites.sprites[sprite_name],
                        (0, 0),
                    )

        # setting the lineart color to override on accessories & missing bits
        lineart_color = (
            pygame.Color(
                constants.CONFIG["cat_sprites"]["lineart_color_sc"]
                if cat.status.group == CatGroup.STARCLAN
                else constants.CONFIG["cat_sprites"]["lineart_color_df"]
            )
            if cat.status.group != CatGroup.UNKNOWN_RESIDENCE
            else None
        )

        gradient_surface = (
            sprites.sprites["line_ur_gradient" + cat_sprite]
            if dead and cat.status.group == CatGroup.UNKNOWN_RESIDENCE
            else None
        )

        def _recolor_lineart(
            sprite, color=None, source: pygame.Surface = None
        ) -> pygame.Surface:
            """
            Helper function to set the appropriate lineart color for the living status of the cat
            :param sprite: lineart to recolor
            :param color: color to apply to all pixels
            :param source: source surface of same size as sprite to use instead of color
            :return:
            """
            if not dead:
                return sprite

            if color is None and source is None:
                raise ValueError(
                    "Must provide either `color` or `source` for _recolor_lineart"
                )

            out = sprite.copy()
            if color:
                pixel_array = pygame.PixelArray(out)
                pixel_array.replace((0, 0, 0), color, distance=0)
                del pixel_array
                return out

            width, height = sprite.get_size()
            for x in range(width):
                for y in range(height):
                    if sprite.get_at((x, y)) == pygame.Color(0, 0, 0):
                        color = source.get_at((x, y))
                        sprite.set_at((x, y), color)
            return out

        # draw line art
        if game_setting_get("shaders") and not dead:
            new_sprite.blit(
                sprites.sprites["shader_mask" + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGB_MULT,
            )
            new_sprite.blit(sprites.sprites["shader_lighting" + cat_sprite], (0, 0))

        if not dead:
            new_sprite.blit(sprites.sprites["lineart" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
            new_sprite.blit(sprites.sprites["lineart_ur" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.DARK_FOREST:
            new_sprite.blit(sprites.sprites["lineart_df" + cat_sprite], (0, 0))
        elif dead:
            new_sprite.blit(sprites.sprites["lineart_sc" + cat_sprite], (0, 0))
        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        sprite_name = f"{sprites.SKIN_DATA['spritesheet']}{cat.pelt.skin}{cat_sprite}"
        new_sprite.blit(
            sprites.sprites[sprite_name],
            (0, 0),
        )

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.missing_part_scars:
                    sprite_name = f"{sprites.SCAR_MISSING_PART_DATA['spritesheet']}{scar}{cat_sprite}"
                    new_sprite.blit(
                        _recolor_lineart(
                            sprites.sprites[sprite_name],
                            lineart_color,
                            gradient_surface,
                        ),
                        (0, 0),
                        special_flags=blendmode,
                    )

        # draw accessories
        from scripts.cat.pelts import Pelt

        if not acc_hidden and cat.pelt.accessory:
            cat_accessories = cat.pelt.accessory
            categories = [
                "collar_accessories",
                "tail_accessories",
                "body_accessories",
                "head_accessories",
            ]
            for category in categories:
                for accessory in cat_accessories:
                    if accessory in getattr(Pelt, category):
                        if accessory in cat.pelt.plant_accessories:
                            sprite_name = f"{sprites.PLANT_DATA['spritesheet']}{accessory}{cat_sprite}"
                            new_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )
                        elif accessory in cat.pelt.wild_accessories:
                            sprite_name = f"{sprites.WILD_DATA['spritesheet']}{accessory}{cat_sprite}"
                            new_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )
                        elif accessory in cat.pelt.collar_accessories:
                            sprite_name = f"{sprites.COLLAR_DATA['spritesheet']}{accessory}{cat_sprite}"
                            new_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )

        # Apply fading fog
        if (
            cat.pelt.opacity <= 97
            and not cat.prevent_fading
            and get_clan_setting("fading")
            and dead
        ):
            stage = "0"
            if 80 >= cat.pelt.opacity > 45:
                # Stage 1
                stage = "1"
            elif cat.pelt.opacity <= 45:
                # Stage 2
                stage = "2"

            new_sprite.blit(
                sprites.sprites["fademask" + stage + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            if cat.status.group == CatGroup.STARCLAN:
                temp = sprites.sprites["fadestarclan" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
                temp = sprites.sprites["fadeur" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites["fadedf" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        # ok! we have the sprite! now, do some layer things if the cat's already dead
        if dead:
            temp_sprite = pygame.Surface(
                (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
            )

            if cat.status.group == CatGroup.STARCLAN:
                # no underlay

                # cat sprite
                temp_sprite.blit(new_sprite, (0, 0))

                # overlay
                temp_sprite.blit(
                    sprites.sprites["line_sc_overlay" + cat_sprite],
                    (0, 0),
                )
            elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
                # underlay
                temp_sprite.blit(
                    sprites.sprites["line_ur_overlay" + cat_sprite],
                    (0, 0),
                )

                # cat sprite
                temp_sprite.blit(new_sprite, (0, 0))

                # overlay
                temp_sprite.blit(
                    sprites.sprites["line_ur_overlay" + cat_sprite],
                    (0, 0),
                )
            elif cat.status.group == CatGroup.DARK_FOREST:
                # no underlay

                # cat sprite
                temp_sprite.blit(new_sprite, (0, 0))

                # no overlay

            new_sprite = temp_sprite

        # reverse, if assigned so
        if cat.pelt.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

    except (TypeError, KeyError):
        traceback.print_exc()
        logger.exception("Failed to load sprite")

        # Placeholder image
        new_sprite = image_cache.load_image(
            f"sprites/error_placeholder.png"
        ).convert_alpha()

    return new_sprite


# ---------------------------------------------------------------------------- #
#                                     OTHER                                    #
# ---------------------------------------------------------------------------- #


def chunks(L, n):
    return [L[x : x + n] for x in range(0, len(L), n)]


def clamp(value: float, minimum_value: float, maximum_value: float) -> float:
    """
    Takes a value and returns it constrained to a certain range
    :param value: The input value
    :param minimum_value: Lower bound
    :param maximum_value: Upper bound
    :return: Clamped float.
    """
    if value < minimum_value:
        return minimum_value
    elif value > maximum_value:
        return maximum_value
    return value


def is_iterable(y):
    try:
        0 in y
    except TypeError:
        return False


def get_text_box_theme(theme_name=None):
    """Updates the name of the theme based on dark or light mode"""
    if game_setting_get("dark mode"):
        return ObjectID("#dark", theme_name)
    else:
        return theme_name


def quit_game(savesettings=False, clearevents=False):
    """
    Quits the game, avoids a bunch of repeated lines
    """
    if savesettings:
        game_settings_save(None)
    if clearevents:
        game.cur_events_list.clear()
    game.rpc.close_rpc.set()
    game.rpc.update_rpc.set()
    pygame.display.quit()
    pygame.quit()
    if game.rpc.is_alive():
        game.rpc.join(1)
    sys_exit()


resource_directory = "resources/dicts/conditions/"
with open(
    os.path.normpath(f"{resource_directory}illnesses.json"), "r", encoding="utf-8"
) as read_file:
    ILLNESSES = ujson.loads(read_file.read())

with open(
    os.path.normpath(f"{resource_directory}injuries.json"), "r", encoding="utf-8"
) as read_file:
    INJURIES = ujson.loads(read_file.read())

with open(
    os.path.normpath(f"{resource_directory}permanent_conditions.json"),
    "r",
    encoding="utf-8",
) as read_file:
    PERMANENT = ujson.loads(read_file.read())

langs = {"snippet": None, "prey": None}

SNIPPETS = None
PREY_LISTS = None

with open(
    os.path.normpath("resources/dicts/backstories.json"), "r", encoding="utf-8"
) as read_file:
    BACKSTORIES = ujson.loads(read_file.read())
