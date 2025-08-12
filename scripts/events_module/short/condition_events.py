import random
from copy import deepcopy
from typing import Dict, List

import i18n
import ujson

from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge, CatRank
from scripts.cat.history import History
from scripts.clan_package.settings import get_clan_setting
from scripts.clan_resources.freshkill import (
    FRESHKILL_ACTIVE,
    MAL_PERCENTAGE,
    STARV_PERCENTAGE,
)
from scripts.conditions import (
    medicine_cats_can_cover_clan,
    get_amount_cat_for_one_medic,
)
from scripts.event_class import Single_Event
from scripts.events_module.short.handle_short_events import handle_short_events
from scripts.events_module.short.scar_events import Scar_Events
from scripts.game_structure import constants
from scripts.game_structure.game.switches import (
    Switch,
    switch_get_value,
    switch_set_value,
    switch_append_list_value,
)
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import (
    event_text_adjust,
    find_alive_cats_with_rank,
    get_leader_life_notice,
)


# ---------------------------------------------------------------------------- #
#                             Condition Event Class                            #
# ---------------------------------------------------------------------------- #


class Condition_Events:
    """All events with a connection to conditions."""

    resource_directory = "resources/dicts/conditions/"
    current_loaded_lang = None

    with open(
        f"{resource_directory}illnesses.json", "r", encoding="utf-8"
    ) as read_file:
        ILLNESSES = ujson.loads(read_file.read())

    with open(f"{resource_directory}injuries.json", "r", encoding="utf-8") as read_file:
        INJURIES = ujson.loads(read_file.read())

    with open(
        "resources/dicts/conditions/permanent_conditions.json", "r", encoding="utf-8"
    ) as read_file:
        PERMANENT = ujson.loads(read_file.read())
    # ---------------------------------------------------------------------------- #
    #                                    CHANCE                                    #
    # ---------------------------------------------------------------------------- #

    with open(
        "resources/dicts/conditions/illnesses_seasons.json", "r", encoding="utf-8"
    ) as read_file:
        ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

    # ---------------------------------------------------------------------------- #
    #                                   STRINGS                                    #
    # ---------------------------------------------------------------------------- #

    PERM_CONDITION_RISK_STRINGS: Dict[str, Dict[str, List[str]]] = {}
    ILLNESS_RISK_STRINGS: Dict[str, Dict[str, List[str]]] = {}
    INJURY_RISK_STRINGS: Dict[str, Dict[str, List[str]]] = {}
    CONGENITAL_CONDITION_GOT_STRINGS: Dict[str, List[str]] = {}
    PERMANENT_CONDITION_GOT_STRINGS: Dict[str, List[str]] = {}
    ILLNESS_GOT_STRINGS: Dict[str, List[str]] = {}
    ILLNESS_HEALED_STRINGS: Dict[str, List[str]] = {}
    INJURY_HEALED_STRINGS: Dict[str, List[str]] = {}
    INJURY_DEATH_STRINGS: Dict[str, List[str]] = {}
    ILLNESS_DEATH_STRINGS: Dict[str, List[str]] = {}

    @classmethod
    def rebuild_strings(cls):
        if cls.current_loaded_lang == i18n.config.get("locale"):
            return

        resources = [
            (
                "PERM_CONDITION_RISK_STRINGS",
                "risk_strings/permanent_condition_risk_strings.json",
            ),
            ("ILLNESS_RISK_STRINGS", "risk_strings/illness_risk_strings.json"),
            ("INJURY_RISK_STRINGS", "risk_strings/injuries_risk_strings.json"),
            (
                "CONGENITAL_CONDITION_GOT_STRINGS",
                "condition_got_strings/gain_congenital_condition_strings.json",
            ),
            (
                "PERMANENT_CONDITION_GOT_STRINGS",
                "condition_got_strings/gain_permanent_condition_strings.json",
            ),
            ("ILLNESS_GOT_STRINGS", "condition_got_strings/gain_illness_strings.json"),
            (
                "ILLNESS_HEALED_STRINGS",
                "healed_and_death_strings/illness_healed_strings.json",
            ),
            (
                "INJURY_HEALED_STRINGS",
                "healed_and_death_strings/injury_healed_strings.json",
            ),
            (
                "INJURY_DEATH_STRINGS",
                "healed_and_death_strings/injury_death_strings.json",
            ),
            (
                "ILLNESS_DEATH_STRINGS",
                "healed_and_death_strings/illness_death_strings.json",
            ),
        ]

        for class_property, file in resources:
            setattr(cls, class_property, load_lang_resource(f"conditions/{file}"))

        cls.current_loaded_lang = i18n.config.get("locale")

    @staticmethod
    def handle_nutrient(cat: Cat, nutrition_info: dict) -> None:
        """
        Handles gaining conditions or death for cats with low nutrient.
        This function should only be called if the game is in 'expanded' or 'cruel season' mode.

        Starvation and malnutrtion must be handled separately from other illnesses due to their distinct death triggers.

            Parameters
            ----------
            cat : Cat
                the cat which has to be checked and updated
            nutrition_info : dict
                dictionary of all nutrition information (can be found in the freshkill pile)
        """
        if not FRESHKILL_ACTIVE:
            return

        if cat.ID not in nutrition_info.keys():
            print(
                f"WARNING: Could not find cat with ID {cat.ID}({cat.name}) in the nutrition information."
            )
            return

        # get all events for a certain rank of a cat
        cat_nutrition = nutrition_info[cat.ID]

        event = None
        illness = None
        heal = False

        Condition_Events.rebuild_strings()

        # handle death first, if percentage is 0 or lower, the cat will die
        if cat_nutrition.percentage <= 0:
            text = ""
            if cat.status.is_leader:
                game.clan.leader_lives -= 1
                # kill and retrieve leader life text
                text = get_leader_life_notice()

            possible_string_list = Condition_Events.ILLNESS_DEATH_STRINGS["starving"]
            event = random.choice(possible_string_list) + " " + text
            # first event in string lists is always appropriate for history formatting
            history_event = possible_string_list[0]

            event = event_text_adjust(Cat, event.strip(), main_cat=cat)

            if cat.status.is_leader:
                history_event = history_event.replace("m_c ", "").replace(".", "")
                cat.history.add_death(
                    condition="starving", death_text=history_event.strip()
                )
            else:
                cat.history.add_death(condition="starving", death_text=history_event)

            cat.die()

            # if the cat is the leader and isn't full dead
            # make them malnourished and refill nutrition slightly
            if cat.status.is_leader and game.clan.leader_lives > 0:
                mal_score = (
                    nutrition_info[cat.ID].max_score / 100 * (MAL_PERCENTAGE + 1)
                )
                nutrition_info[cat.ID].current_score = round(mal_score, 2)
                cat.get_ill("malnourished")

            types = ["birth_death"]
            game.cur_events_list.append(
                Single_Event(event, types, cat_dict={"m_c": cat})
            )
            return

        # heal cat if percentage is high enough and cat is ill
        if (
            cat_nutrition.percentage > MAL_PERCENTAGE
            and cat.is_ill()
            and "malnourished" in cat.illnesses
        ):
            illness = "malnourished"
            event = random.choice(
                Condition_Events.ILLNESS_HEALED_STRINGS["malnourished"]
            )
            heal = True

        # heal cat if percentage is high enough and cat is ill
        elif (
            cat_nutrition.percentage > STARV_PERCENTAGE
            and cat.is_ill()
            and "starving" in cat.illnesses
        ):
            if cat_nutrition.percentage < MAL_PERCENTAGE:
                if "malnourished" not in cat.illnesses:
                    cat.get_ill("malnourished")
                illness = "starving"
                heal = True
            else:
                illness = "starving"
                heal = True

        elif MAL_PERCENTAGE >= cat_nutrition.percentage > STARV_PERCENTAGE:
            # because of the smaller 'nutrition buffer', kitten and elder should get the starving condition.
            if cat.status.rank in (CatRank.KITTEN, CatRank.ELDER):
                illness = "starving"
            else:
                illness = "malnourished"

        elif cat_nutrition.percentage <= STARV_PERCENTAGE:
            illness = "starving"

        # handle the gaining/healing illness
        if heal:
            event = random.choice(Condition_Events.ILLNESS_HEALED_STRINGS[illness])
            cat.illnesses.pop(illness)
        elif not heal and illness:
            event = random.choice(Condition_Events.ILLNESS_GOT_STRINGS[illness])
            cat.get_ill(illness)

        if event:
            event_text = event_text_adjust(Cat, event, main_cat=cat)
            types = ["health"]
            game.cur_events_list.append(
                Single_Event(event_text, types, cat_dict={"m_c": cat})
            )

    @staticmethod
    def handle_illnesses(cat, season=None):
        """
        This function handles the illnesses overall by randomly making cat ill (or not).
        It will return a bool to indicate if the cat is dead.
        """
        # return immediately if they're already dead
        triggered = False
        if cat.dead:
            if cat.dead:
                triggered = True
            return triggered

        event_string = None

        if cat.is_ill():
            event_string = Condition_Events.handle_already_ill(cat)
        else:
            # ---------------------------------------------------------------------------- #
            #                              make cats sick                                  #
            # ---------------------------------------------------------------------------- #
            random_number = int(
                random.random()
                * game.get_config_value(
                    "condition_related", f"{game.clan.game_mode}_illness_chance"
                )
            )
            if (
                not cat.dead
                and not cat.is_ill()
                and random_number <= 10
                and not event_string
            ):
                # CLAN FOCUS!
                if get_clan_setting("rest and recover"):
                    stopping_chance = constants.CONFIG["focus"]["rest and recover"][
                        "illness_prevent"
                    ]
                    if not int(random.random() * stopping_chance):
                        return triggered

                season_dict = Condition_Events.ILLNESSES_SEASON_LIST[season]
                possible_illnesses = []

                # pick up possible illnesses from the season dict
                for illness_name in season_dict:
                    possible_illnesses += [illness_name] * season_dict[illness_name]

                # pick a random illness from those possible
                random_index = int(random.random() * len(possible_illnesses))
                chosen_illness = possible_illnesses[random_index]
                # if a non-kitten got kittencough, switch it to whitecough instead
                if chosen_illness == "kittencough" and not cat.status.rank.is_baby():
                    chosen_illness = "whitecough"
                # make em sick
                cat.get_ill(chosen_illness)

                # create event text
                if i18n.config.get("locale") == "en" and chosen_illness in (
                    "running nose",
                    "stomachache",
                ):
                    illness = f"a {chosen_illness}"

                # try to translate the illness
                illness = i18n.t(f"conditions.illnesses.{chosen_illness}")

                illness.replace("conditions.illnesses.", "")

                event_string = i18n.t(
                    "defaults.illness_get_event",
                    illness=illness,
                )

                event_string = event_text_adjust(Cat, text=event_string, main_cat=cat)

        # if an event happened, then add event to cur_event_list and save death if it happened.
        if event_string:
            types = ["health"]
            if cat.dead:
                types.append("birth_death")
            game.cur_events_list.append(
                Single_Event(event_string, types, cat.ID, cat_dict={"m_c": cat})
            )

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.dead:
            triggered = True
        else:
            triggered = False

        return triggered

    @staticmethod
    def handle_injuries(cat, random_cat=None):
        """
        This function handles injuries overall by randomly injuring cat (or not).
        Returns: boolean - if an event was triggered
        """
        triggered = False
        random_number = int(
            random.random()
            * game.get_config_value(
                "condition_related", f"{game.clan.game_mode}_injury_chance"
            )
        )

        if cat.dead:
            triggered = True
            return triggered

        if (
            constants.CONFIG["event_generation"]["debug_type_override"] == "injury"
            and random_cat
        ):
            handle_short_events.handle_event(
                event_type="health",
                main_cat=cat,
                random_cat=random_cat,
                freshkill_pile=game.clan.freshkill_pile,
            )

        # handle if the current cat is already injured
        if cat.is_injured():
            for injury in cat.injuries:
                if injury == "pregnant" and cat.ID not in game.clan.pregnancy_data:
                    print(
                        f"INFO: deleted pregnancy condition of {cat.ID} due no pregnancy data in the clan."
                    )
                    del cat.injuries[injury]
                    return triggered
                elif injury == "pregnant":
                    return triggered
            triggered = Condition_Events.handle_already_injured(cat)
        else:
            # EVENTS
            if (
                not triggered
                and cat.personality.trait
                in (
                    "adventurous",
                    "bold",
                    "daring",
                    "confident",
                    "ambitious",
                    "bloodthirsty",
                    "fierce",
                    "strict",
                    "troublesome",
                    "vengeful",
                    "impulsive",
                )
                and random_number <= 15
            ):
                triggered = True
            elif not triggered and random_number <= 5:
                triggered = True

            if triggered:
                # CLAN FOCUS!
                if get_clan_setting("rest and recover"):
                    stopping_chance = constants.CONFIG["focus"]["rest and recover"][
                        "injury_prevent"
                    ]
                    if not int(random.random() * stopping_chance):
                        return False

                handle_short_events.handle_event(
                    event_type="health",
                    main_cat=cat,
                    random_cat=random_cat,
                    freshkill_pile=game.clan.freshkill_pile,
                )

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.status.rank != CatRank.LEADER:
            # only checks for non-leaders, as leaders will not be dead if they are just losing a life
            if cat.dead:
                triggered = True
            else:
                triggered = False

        return triggered

    @staticmethod
    def handle_permanent_conditions(
        cat, condition=None, injury_name=None, scar=None, born_with=False
    ):
        """
        this function handles overall the permanent conditions of a cat.
        returns boolean if event was triggered
        """

        # dict of possible physical conditions that can be acquired from relevant scars
        scar_to_condition = {
            "THREE": ["one bad eye", "failing eyesight"],
            "FOUR": ["weak leg"],
            "LEFTEAR": ["partial hearing loss"],
            "RIGHTEAR": ["partial hearing loss"],
            "NOLEFTEAR": ["partial hearing loss"],
            "NORIGHTEAR": ["partial hearing loss"],
            "NOEAR": ["partial hearing loss", "deaf"],
            "NOPAW": ["lost a leg"],
            "NOTAIL": ["lost their tail"],
            "HALFTAIL": ["lost their tail"],
            "BRIGHTHEART": ["one bad eye"],
            "LEFTBLIND": ["one bad eye", "failing eyesight"],
            "RIGHTBLIND": ["one bad eye", "failing eyesight"],
            "BOTHBLIND": ["failing eyesight", "blind"],
            "MANLEG": ["weak leg", "twisted leg"],
            "RATBITE": ["weak leg"],
            "LEGBITE": ["weak leg"],
            "TOETRAP": ["weak leg"],
            "HINDLEG": ["weak leg"],
        }

        scarless_conditions = (
            "weak leg",
            "paralyzed",
            "raspy lungs",
            "wasting disease",
            "blind",
            "failing eyesight",
            "one bad eye",
            "partial hearing loss",
            "deaf",
            "constant joint pain",
            "constantly dizzy",
            "recurring shock",
            "lasting grief",
            "persistent headaches",
        )

        got_condition = False
        perm_condition = None
        possible_conditions = []

        if injury_name is not None:
            if scar is not None and scar in scar_to_condition:
                possible_conditions = scar_to_condition.get(scar)
                perm_condition = random.choice(possible_conditions)
            elif scar is None:
                try:
                    if Condition_Events.INJURIES[injury_name] is not None:
                        conditions = Condition_Events.INJURIES[injury_name][
                            "cause_permanent"
                        ]
                        for x in conditions:
                            if x in scarless_conditions:
                                possible_conditions.append(x)
                        if len(possible_conditions) > 0 and not int(
                            random.random()
                            * constants.CONFIG["condition_related"][
                                "permanent_condition_chance"
                            ]
                        ):
                            perm_condition = random.choice(possible_conditions)
                        else:
                            return perm_condition
                except KeyError:
                    print(
                        f"WARNING: {injury_name} couldn't be found in injury dict! no permanent condition is possible."
                    )
                    return perm_condition
            else:
                print(
                    f"WARNING: {scar} for {injury_name} is either None or is not in scar_to_condition dict. This is "
                    f"not necessarily a bug.  Only report if you feel the scar should have "
                    f"resulted in a permanent condition."
                )

        elif condition is not None:
            perm_condition = condition

        if perm_condition is not None:
            got_condition = cat.get_permanent_condition(perm_condition, born_with)

        if got_condition is True:
            return perm_condition

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def handle_already_ill(cat):
        starting_life_count = game.clan.leader_lives
        cat.healed_condition = False
        event_list = []
        illness_progression = {
            "running nose": "whitecough",
            "kittencough": "whitecough",
            "whitecough": "greencough",
            "greencough": "yellowcough",
            "yellowcough": "redcough",
            "an infected wound": "a festering wound",
            "heat exhaustion": "heat stroke",
            "stomachache": "diarrhea",
            "grief stricken": "lasting grief",
        }
        Condition_Events.rebuild_strings()
        # ---------------------------------------------------------------------------- #
        #                         handle currently sick cats                           #
        # ---------------------------------------------------------------------------- #

        # making a copy, so we can iterate through copy and modify the real dict at the same time
        illnesses = deepcopy(cat.illnesses)
        for illness in illnesses:
            if illness in switch_get_value(Switch.skip_conditions):
                continue

            # moon skip to try and kill or heal cat
            skipped = cat.moon_skip_illness(illness)

            # if event trigger was true, events should be skipped for this illness
            if skipped is True:
                continue

            # death event text and break bc any other illnesses no longer matter
            if cat.dead or (
                cat.status.is_leader and starting_life_count != game.clan.leader_lives
            ):
                try:
                    possible_string_list = Condition_Events.ILLNESS_DEATH_STRINGS[
                        illness
                    ]
                    event = random.choice(possible_string_list)
                    # first event in string lists is always appropriate for history formatting
                    history_event = possible_string_list[0]
                except KeyError:
                    print(
                        f"WARNING: {illness} does not have an injury death string, placeholder used."
                    )
                    event = i18n.t("defaults.illness_death_event")
                    history_event = (
                        i18n.t("defaults.illness_death_history")
                        if cat.status.rank != CatRank.LEADER
                        else i18n.t("defaults.illness_death_history_leader")
                    )

                event = event_text_adjust(Cat, event, main_cat=cat)

                if cat.status.is_leader:
                    event = event + " " + get_leader_life_notice()
                    history_event = history_event.replace("m_c ", "").replace(".", "")
                    cat.history.add_death(
                        condition=illness, death_text=history_event.strip()
                    )
                else:
                    cat.history.add_death(condition=illness, death_text=history_event)

                # clear event list to get rid of any healed or risk event texts from other illnesses
                event_list.clear()
                event_list.append(event)
                game.herb_events_list.append(event)
                break

            # if the leader died, then break before handling other illnesses cus they'll be fully healed or dead-dead
            if cat.status.is_leader and starting_life_count != game.clan.leader_lives:
                break

            # heal the cat
            elif cat.healed_condition is True:
                cat.history.remove_possible_history(illness)
                switch_append_list_value(Switch.skip_conditions, illness)
                # gather potential event strings for healed illness
                possible_string_list = Condition_Events.ILLNESS_HEALED_STRINGS[illness]

                # choose event string
                random_index = int(random.random() * len(possible_string_list))
                event = possible_string_list[random_index]
                event = event_text_adjust(Cat, event, main_cat=cat)
                event_list.append(event)
                game.herb_events_list.append(event)

                cat.illnesses.pop(illness)
                # make sure complications get reset if infection or fester were healed
                if illness in ("an infected wound", "a festering wound"):
                    for injury in cat.injuries:
                        keys = cat.injuries[injury].keys()
                        if "complication" in keys:
                            cat.injuries[injury]["complication"] = None
                    for condition in cat.permanent_condition:
                        keys = cat.permanent_condition[condition].keys()
                        if "complication" in keys:
                            cat.permanent_condition[condition]["complication"] = None
                cat.healed_condition = False

                # move to next illness, the cat can't get a risk from an illness that has healed
                continue

            Condition_Events.give_risks(
                cat, event_list, illness, illness_progression, illnesses, cat.illnesses
            )

        # joining event list into one event string
        event_string = None
        if len(event_list) > 0:
            event_string = " ".join(event_list)
        return event_string

    @staticmethod
    def handle_already_injured(cat):
        """
        This function handles, when the cat is already injured
        Returns: True if an event was triggered, False if nothing happened
        """
        Condition_Events.rebuild_strings()

        triggered = False
        event_list = []

        injury_progression = {"poisoned": "redcough", "shock": "lingering shock"}

        # need to hold this number so that we can check if the leader has died
        starting_life_count = game.clan.leader_lives

        injuries = deepcopy(cat.injuries)
        for injury in injuries:
            if injury in switch_get_value(Switch.skip_conditions):
                continue

            skipped = cat.moon_skip_injury(injury)
            if skipped:
                continue

            if cat.dead or (
                cat.status.is_leader and starting_life_count != game.clan.leader_lives
            ):
                triggered = True

                try:
                    possible_string_list = Condition_Events.INJURY_DEATH_STRINGS[injury]
                    event = random.choice(possible_string_list)

                    # first string in the list is always appropriate for history text
                    history_text = possible_string_list[0]
                except KeyError:
                    print(
                        f"WARNING: {injury} does not have an injury death string, placeholder used"
                    )

                    event = i18n.t("defaults.injury_death_event")
                    history_text = (
                        i18n.t("defaults.injury_death_history")
                        if cat.status.rank != CatRank.LEADER
                        else i18n.t("injury_death_history_leader")
                    )

                event = event_text_adjust(Cat, event, main_cat=cat)

                if cat.status.is_leader:
                    event = event + " " + get_leader_life_notice()
                    history_text = history_text.replace("m_c", " ").replace(".", "")
                    cat.history.add_death(
                        condition=injury, death_text=history_text.strip()
                    )

                else:
                    cat.history.add_death(condition=injury, death_text=history_text)

                # clear event list first to make sure any heal or risk events from other injuries are not shown
                event_list.clear()
                event_list.append(event)
                game.herb_events_list.append(event)
                break

            elif cat.healed_condition is True:
                switch_append_list_value(Switch.skip_conditions, injury)
                triggered = True

                # Try to give a scar, and get the event text to be displayed
                event, scar_given = Scar_Events.handle_scars(cat, injury)
                # If a scar was not given, we need to grab a separate healed event
                if not scar_given:
                    try:
                        event = random.choice(
                            Condition_Events.INJURY_HEALED_STRINGS[injury]
                        )
                    except KeyError:
                        print(
                            f"WARNING: {injury} couldn't be found in the healed strings dict! "
                            f"placeholder string was used."
                        )
                        # try to translate the string
                        new_injury = i18n.t(f"conditions.injuries.{injury}")
                        new_injury.replace("conditions.injuries.", "")

                        event = i18n.t(
                            "defaults.injury_healed_event", injury=new_injury
                        )

                event = event_text_adjust(Cat, event, main_cat=cat)

                game.herb_events_list.append(event)

                cat.history.remove_possible_history(injury)
                cat.injuries.pop(injury)
                cat.healed_condition = False

                # try to give a permanent condition based on healed injury and new scar if any
                condition_got = Condition_Events.handle_permanent_conditions(
                    cat, injury_name=injury, scar=scar_given
                )

                if condition_got is not None:
                    # gather potential event strings for gotten condition

                    try:
                        possible_string_list = (
                            Condition_Events.PERMANENT_CONDITION_GOT_STRINGS[injury][
                                condition_got
                            ]
                        )
                    except KeyError:
                        print(
                            f"WARNING: No entry in gain_permanent_condition_strings for injury '{injury}' causing "
                            f"condition '{condition_got}'. Using default."
                        )

                        # try to translate the injury & condition
                        translated_injury = i18n.t(f"conditions.injury.{injury}")
                        translated_injury.replace("conditions.injury.", "")

                        translated_condition = i18n.t(
                            f"conditions.permanent_conditions.{condition_got}"
                        )
                        translated_condition.replace(
                            "conditions.permanent_conditions.", ""
                        )

                        possible_string_list = [
                            i18n.t(
                                "defaults.permanent_condition_from_injury_event",
                                injury=translated_injury,
                                condition=translated_condition,
                            )
                        ]
                        del translated_condition, translated_injury
                    # choose event string and ensure Clan's med cat number aligns with event text
                    random_index = random.randrange(0, len(possible_string_list))

                    med_list = find_alive_cats_with_rank(
                        Cat,
                        [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE],
                        working=True,
                    )
                    # If the cat is a med cat, don't consider them as one for the event.

                    if cat in med_list:
                        med_list.remove(cat)

                    # Choose med cat, if you can
                    if med_list:
                        med_cat = random.choice(med_list)
                    else:
                        med_cat = None

                    if (
                        not med_cat
                        and random_index < 2
                        and len(possible_string_list) >= 3
                    ):
                        random_index = 2

                    event = possible_string_list[random_index]
                    event = event_text_adjust(
                        Cat, event, main_cat=cat, random_cat=med_cat
                    )  # adjust the text

                if event is not None:
                    event_list.append(event)
                continue

            Condition_Events.give_risks(
                cat, event_list, injury, injury_progression, injuries, cat.injuries
            )

        if len(event_list) > 0:
            event_string = " ".join(event_list)
        else:
            event_string = None

        if event_string:
            types = ["health"]
            if cat.dead:
                types.append("birth_death")
            game.cur_events_list.append(Single_Event(event_string, types, cat.ID))

        return triggered

    @staticmethod
    def handle_already_disabled(cat):
        """
        this function handles what happens if the cat already has a permanent condition.
        Returns: boolean (if something happened) and the event_string
        """
        triggered = False
        event_types = ["health"]

        event_list = []

        Condition_Events.rebuild_strings()

        condition_progression = {
            "one bad eye": "failing eyesight",
            "failing eyesight": "blind",
            "partial hearing loss": "deaf",
        }

        cat_dict = {"m_c": cat}

        conditions = deepcopy(cat.permanent_condition)
        for condition in conditions:
            # checking if the cat has a congenital condition to reveal and handling duration and death
            prev_lives = game.clan.leader_lives
            state = cat.moon_skip_permanent_condition(condition)

            # if cat is dead, break
            if cat.dead or game.clan.leader_lives < prev_lives:
                triggered = True
                event_types.append("birth_death")
                translated_condition = i18n.t(
                    f"conditions.permanent_conditions.{condition}"
                )
                event = i18n.t(
                    "defaults.complications_death_event", condition=translated_condition
                )
                if cat.status.is_leader and game.clan.leader_lives >= 1:
                    event = i18n.t(
                        "defaults.complications_death_event_leader",
                        condition=translated_condition,
                    )
                event_list.append(event)

                if cat.status.rank != CatRank.LEADER:
                    cat.history.add_death(
                        death_text=i18n.t("defaults.complications_death_history"),
                        condition=translated_condition,
                    )
                else:
                    cat.history.add_death(
                        death_text=i18n.t("defaults.complications_death_history"),
                        condition=translated_condition,
                    )

                game.herb_events_list.append(event)
                break

            # skipping for whatever reason
            if state == "skip":
                continue

            # revealing perm condition
            if state == "reveal":
                # gather potential event strings for gotten risk
                possible_string_list = (
                    Condition_Events.CONGENITAL_CONDITION_GOT_STRINGS[condition]
                )

                # choose event string and ensure Clan's med cat number aligns with event text
                random_index = int(random.random() * len(possible_string_list))
                med_list = find_alive_cats_with_rank(
                    Cat,
                    [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE],
                    working=True,
                    sort=True,
                )
                med_cat = None
                has_parents = False
                if cat.parent1 is not None and cat.parent2 is not None:
                    # Check if the parent is in Cat.all_cats. If not, they are faded are dead.

                    # If they have a med parent, this will be flicked to True in the next couple lines.
                    med_parent = False
                    if cat.parent1 in Cat.all_cats:
                        parent1_dead = Cat.all_cats[cat.parent1].dead
                        if Cat.all_cats[cat.parent1].status.rank.is_any_medicine_rank():
                            med_parent = True
                    else:
                        parent1_dead = True

                    if cat.parent2 in Cat.all_cats:
                        parent2_dead = Cat.all_cats[cat.parent2].dead
                        if Cat.all_cats[cat.parent2].status.rank.is_any_medicine_rank():
                            med_parent = True
                    else:
                        parent2_dead = True

                    if not parent1_dead or not parent2_dead and not med_parent:
                        has_parents = True

                if len(med_list) == 0 or not has_parents:
                    if random_index == 0:
                        random_index = 1
                    else:
                        med_cat = None
                else:
                    med_cat = random.choice(med_list)
                    if med_cat == cat:
                        random_index = 1
                        med_cat = None
                event = possible_string_list[random_index]
                event = event_text_adjust(
                    Cat, event, main_cat=cat, random_cat=med_cat
                )  # adjust the text
                event_list.append(event)
                if med_cat:
                    cat_dict["r_c"] = med_cat
                continue

            # give risks
            Condition_Events.give_risks(
                cat,
                event_list,
                condition,
                condition_progression,
                conditions,
                cat.permanent_condition,
            )

        Condition_Events.determine_retirement(cat, triggered)

        if len(event_list) > 0:
            event_string = " ".join(event_list)
            game.cur_events_list.append(
                Single_Event(event_string, event_types, [cat.ID], cat_dict=cat_dict)
            )
        return

    @staticmethod
    def determine_retirement(cat, triggered):
        if get_clan_setting("retirement") or cat.no_retire:
            return

        if (
            not triggered
            and not cat.dead
            and cat.status.rank in (CatRank.APPRENTICE, CatRank.WARRIOR)
        ):
            for condition in cat.permanent_condition:
                if cat.permanent_condition[condition]["severity"] not in (
                    "major",
                    "severe",
                ):
                    continue

                if cat.permanent_condition[condition]["severity"] == "severe":
                    # Higher chances for "severe". These are meant to be nearly 100% without
                    # being 100%
                    retire_chances = {
                        CatAge.NEWBORN: 0,
                        CatAge.KITTEN: 0,
                        CatAge.ADOLESCENT: 50,  # This is high so instances where a cat retires the same moon they become an apprentice is rare
                        CatAge.YOUNG_ADULT: 10,
                        CatAge.ADULT: 5,
                        CatAge.SENIOR_ADULT: 5,
                        CatAge.SENIOR: 5,
                    }
                else:
                    retire_chances = {
                        CatAge.NEWBORN: 0,
                        CatAge.KITTEN: 0,
                        CatAge.ADOLESCENT: 100,
                        CatAge.YOUNG_ADULT: 80,
                        CatAge.ADULT: 70,
                        CatAge.SENIOR_ADULT: 50,
                        CatAge.SENIOR: 10,
                    }

                chance = int(retire_chances.get(cat.age))
                if not int(random.random() * chance):
                    retire_involved = [cat.ID]
                    cat_dict = {"m_c": cat}
                    if cat.age == CatAge.ADOLESCENT:
                        event = i18n.t(
                            "hardcoded.condition_retire_adolescent", name=cat.name
                        )
                    elif game.clan.leader is not None:
                        if (
                            game.clan.leader.status.alive_in_player_clan
                            and cat.moons < 120
                        ):
                            retire_involved.append(game.clan.leader.ID)
                            event = i18n.t("hardcoded.condition_retire_normal")
                        else:
                            event = i18n.t("hardcoded.condition_retire_no_leader")
                    else:
                        event = i18n.t("hardcoded.condition_retire_no_leader")

                    if cat.age == CatAge.ADOLESCENT:
                        event += i18n.t(
                            "hardcoded.condition_retire_adolescent_ceremony",
                            clan=game.clan.displayname,
                            newname=cat.name.prefix + cat.name.suffix,
                        )

                    cat.retire_cat()
                    # Don't add this to the condition event list: instead make it its own event, a ceremony.
                    game.cur_events_list.append(
                        Single_Event(
                            event_text_adjust(Cat, event, main_cat=cat),
                            "ceremony",
                            retire_involved,
                            cat_dict=cat_dict,
                        )
                    )

    @staticmethod
    def give_risks(cat, event_list, condition, progression, conditions, dictionary):
        Condition_Events.rebuild_strings()

        event_triggered = False
        if dictionary == cat.permanent_condition:
            event_triggered = True
        for risk in conditions[condition]["risks"]:
            if risk["name"] in (cat.injuries or cat.illnesses):
                continue
            if (
                risk["name"] == "an infected wound"
                and "a festering wound" in cat.illnesses
            ):
                continue

            # adjust chance of risk gain if Clan has enough meds
            chance = risk["chance"]
            if medicine_cats_can_cover_clan(
                Cat.all_cats.values(), get_amount_cat_for_one_medic(game.clan)
            ):
                chance += 10  # lower risk if enough meds
            if game.clan.medicine_cat is None and chance != 0:
                chance = int(
                    chance * 0.75
                )  # higher risk if no meds and risk chance wasn't 0
                if chance <= 0:  # ensure that chance is never 0
                    chance = 1

            # if we hit the chance, then give the risk if the cat does not already have the risk
            if (
                chance != 0
                and not int(random.random() * chance)
                and risk["name"] not in dictionary
            ):
                # check if the new risk is a previous stage of a current illness
                skip = False
                if risk["name"] in progression:
                    if progression[risk["name"]] in dictionary:
                        skip = True
                # if it is, then break instead of giving the risk
                if skip is True:
                    break

                new_condition_name = risk["name"]

                # lower risk of getting it again if not a perm condition
                if dictionary != cat.permanent_condition:
                    saved_condition = dictionary[condition]["risks"]
                    for old_risk in saved_condition:
                        if old_risk["name"] == risk["name"]:
                            if new_condition_name in [
                                "an infected wound",
                                "a festering wound",
                            ]:
                                # if it's infection or festering, we're removing the chance completely
                                # this is both to prevent annoying infection loops
                                # and bc the illness/injury difference causes problems
                                old_risk["chance"] = 0
                            else:
                                old_risk["chance"] = risk["chance"] + 10

                med_cat = None
                removed_condition = False
                try:
                    # gather potential event strings for gotten condition
                    if dictionary == cat.illnesses:
                        possible_string_list = Condition_Events.ILLNESS_RISK_STRINGS[
                            condition
                        ][new_condition_name]
                    elif dictionary == cat.injuries:
                        possible_string_list = Condition_Events.INJURY_RISK_STRINGS[
                            condition
                        ][new_condition_name]
                    else:
                        possible_string_list = (
                            Condition_Events.PERM_CONDITION_RISK_STRINGS[condition][
                                new_condition_name
                            ]
                        )

                    # if it is a progressive condition, then remove the old condition and keep the new one
                    if (
                        condition in progression
                        and new_condition_name == progression.get(condition)
                    ):
                        removed_condition = True
                        dictionary.pop(condition)

                    # choose event string and ensure Clan's med cat number aligns with event text
                    random_index = int(random.random() * len(possible_string_list))
                    med_list = find_alive_cats_with_rank(
                        Cat,
                        [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE],
                        working=True,
                        sort=True,
                    )
                    if len(med_list) == 0:
                        if random_index == 0:
                            random_index = 1
                        else:
                            med_cat = None
                    else:
                        med_cat = random.choice(med_list)
                        if med_cat == cat:
                            random_index = 1
                    event = possible_string_list[random_index]
                except KeyError:
                    print(
                        f"WARNING: {condition} couldn't be found in the risk strings! placeholder string was used"
                    )
                    event = i18n.t(
                        "conditions.permanent_conditions.unknown_condition_risk_given"
                    )

                event = event_text_adjust(
                    Cat, event, main_cat=cat, random_cat=med_cat
                )  # adjust the text

                event_list.append(event)

                # we add the condition to this game switch, this is so we can ensure it's skipped over for this moon
                switch_append_list_value(Switch.skip_conditions, new_condition_name)
                # here we give the new condition
                if new_condition_name in Condition_Events.INJURIES:
                    cat.get_injured(new_condition_name, event_triggered=event_triggered)
                    break
                elif new_condition_name in Condition_Events.ILLNESSES:
                    cat.get_ill(new_condition_name, event_triggered=event_triggered)
                    if dictionary == cat.illnesses or removed_condition:
                        break
                    keys = dictionary[condition].keys()
                    complication = None
                    if new_condition_name == "an infected wound":
                        complication = "infected"
                    elif new_condition_name == "a festering wound":
                        complication = "festering"
                    if complication is not None:
                        if "complication" in keys:
                            dictionary[condition]["complication"] = complication
                        else:
                            dictionary[condition].update({"complication": complication})
                    break
                elif new_condition_name in Condition_Events.PERMANENT:
                    cat.get_permanent_condition(
                        new_condition_name, event_triggered=event_triggered
                    )
                    break

                # break out of risk giving loop cus we don't want to give multiple risks for one condition
                break


Condition_Events.rebuild_strings()
