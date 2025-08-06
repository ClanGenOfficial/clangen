#!/usr/bin/env python3
# -*- coding: ascii -*-
import logging
import random
from copy import deepcopy
from itertools import repeat
from os.path import exists as path_exists
from random import choice, randint, choices
from typing import List, Tuple, Optional, Union

import pygame

from scripts.cat.cats import Cat
from scripts.cat_relations.enums import RelType
from scripts.cat.enums import CatAge, CatRank
from scripts.clan import Clan
from scripts.clan_package.settings import get_clan_setting
from scripts.events_module.event_filters import event_for_tags
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.patrol.patrol_outcome import PatrolOutcome
from scripts.game_structure import localization, constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import (
    get_personality_compatibility,
    check_relationship_value,
    process_text,
    adjust_prey_abbr,
    find_special_list_types,
    filter_relationship_type,
    get_special_snippet_list,
    adjust_list_text,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                              PATROL CLASS START                              #
# ---------------------------------------------------------------------------- #
"""
When adding new patrols, use \n to add a paragraph break in the text
"""


class Patrol:
    used_patrols = []

    def __init__(self):
        self.patrol_event: Optional[PatrolEvent] = None

        self.patrol_leader = None
        self.random_cat = None
        self.patrol_cats = []
        self.patrol_apprentices = []
        self.other_clan = None
        self.intro_text = ""

        self.patrol_statuses = {}
        self.patrol_status_list = []

        # Holds new cats for easy access
        self.new_cats: List[List[Cat]] = []

        # False if no debug patrol set, value if one is set
        self.debug_patrol: Union[bool, str] = False

        # the patrols
        self.HUNTING_SZN = None
        self.HUNTING = None
        self.TRAINING_SZN = None
        self.TRAINING = None
        self.BORDER_SZN = None
        self.BORDER = None
        self.MEDCAT_SZN = None
        self.MEDCAT = None
        self.NEW_CAT = None
        self.NEW_CAT_HOSTILE = None
        self.NEW_CAT_WELCOMING = None
        self.OTHER_CLAN = None
        self.OTHER_CLAN_HOSTILE = None
        self.OTHER_CLAN_ALLIES = None
        self.HUNTING_GEN = None
        self.BORDER_GEN = None
        self.TRAINING_GEN = None
        self.MEDCAT_GEN = None
        self.DISASTER = None

    def setup_patrol(self, patrol_cats: List[Cat], patrol_type: str) -> str:
        # Add cats

        print("PATROL START ---------------------------------------------------")

        self.add_patrol_cats(patrol_cats, game.clan)

        self.debug_patrol = (
            constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
            if constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
            else False
        )

        final_patrols, final_romance_patrols = self.get_possible_patrols(
            str(game.clan.current_season).casefold(),
            str(
                game.clan.biome
                if not game.clan.override_biome
                else game.clan.override_biome
            ).casefold(),
            str(game.clan.camp_bg).casefold(),
            patrol_type,
            get_clan_setting("disasters"),
        )

        print(
            f"Total Number of Possible Patrols | normal: {len(final_patrols)}, romantic: {len(final_romance_patrols)} "
        )

        if final_patrols:
            normal_event_choice = choices(
                final_patrols, weights=[x.weight for x in final_patrols]
            )[0]
        else:
            print("ERROR: NO POSSIBLE NORMAL PATROLS FOUND for: ", self.patrol_statuses)
            raise RuntimeError

        romantic_event_choice = None
        if final_romance_patrols:
            romantic_event_choice = choices(
                final_romance_patrols, [x.weight for x in final_romance_patrols]
            )[0]

        if romantic_event_choice and Patrol.decide_if_romantic(
            romantic_event_choice,
            self.patrol_leader,
            self.random_cat,
            self.patrol_apprentices,
        ):
            print("did the romance")
            self.patrol_event = romantic_event_choice
        else:
            self.patrol_event = normal_event_choice

        Patrol.used_patrols.append(self.patrol_event.patrol_id)

        return self.process_text(self.patrol_event.intro_text, None)

    def proceed_patrol(self, path: str = "proceed") -> Tuple[str, str, Optional[str]]:
        """Proceed the patrol to the next step.
        path can be: "proceed", "antag", or "decline" """

        if path == "decline":
            if self.patrol_event:
                print(
                    f"PATROL ID: {self.patrol_event.patrol_id} | SUCCESS: N/A (did not proceed)"
                )
                return self.process_text(self.patrol_event.decline_text, None), "", None
            else:
                return "Error - no event chosen", "", None

        return self.determine_outcome(antagonize=(path == "antag"))

    def add_patrol_cats(self, patrol_cats: List[Cat], clan: Clan) -> None:
        """Add the list of cats to the patrol class and handles to set all needed values.

        Parameters
        ----------
        patrol_cats : list
            list of cats which are on the patrol

        clan: Clan
            the Clan class of the game, this parameter is needed to make tests possible

        Returns
        ----------
        """
        for cat in patrol_cats:
            self.patrol_cats.append(cat)

            if cat.status.rank.is_any_apprentice_rank():
                self.patrol_apprentices.append(cat)

            self.patrol_status_list.append(cat.status.rank)

            if cat.status.rank in self.patrol_statuses:
                self.patrol_statuses[cat.status.rank] += 1
            else:
                self.patrol_statuses[cat.status.rank] = 1

            # Combined patrol_statuses categories
            if cat.status.rank.is_any_medicine_rank():
                if "healer cats" in self.patrol_statuses:
                    self.patrol_statuses["healer cats"] += 1
                else:
                    self.patrol_statuses["healer cats"] = 1

            if cat.status.rank.is_any_apprentice_rank():
                if "all apprentices" in self.patrol_statuses:
                    self.patrol_statuses["all apprentices"] += 1
                else:
                    self.patrol_statuses["all apprentices"] = 1

            if (
                cat.status.rank.is_any_adult_warrior_like_rank()
                and cat.age != CatAge.ADOLESCENT
            ):
                if "normal adult" in self.patrol_statuses:
                    self.patrol_statuses["normal adult"] += 1
                else:
                    self.patrol_statuses["normal adult"] = 1

            game.patrolled.append(cat.ID)

        # PATROL LEADER AND RANDOM CAT CAN NOT CHANGE AFTER SET-UP

        # DETERMINE PATROL LEADER
        # sets medcat as leader if they're in the patrol
        if CatRank.MEDICINE_CAT in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.MEDICINE_CAT)
            self.patrol_leader = self.patrol_cats[index]
        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warrior from being treated as medicine cats in medicine cat patrols.
        elif CatRank.MEDICINE_APPRENTICE in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.MEDICINE_APPRENTICE)
            self.patrol_leader = self.patrol_cats[index]
            # then we just make sure that this app will also be app1
            self.patrol_apprentices.remove(self.patrol_leader)
            self.patrol_apprentices = [self.patrol_leader] + self.patrol_apprentices
        # sets leader as patrol leader
        elif CatRank.LEADER in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.LEADER)
            self.patrol_leader = self.patrol_cats[index]
        elif CatRank.DEPUTY in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.DEPUTY)
            self.patrol_leader = self.patrol_cats[index]
        else:
            # Get the oldest cat
            possible_leader = [
                i
                for i in self.patrol_cats
                if not i.status.rank.is_any_apprentice_rank()
            ]
            if possible_leader:
                # Flip a coin to pick the most experience, or oldest.
                if randint(0, 1):
                    possible_leader.sort(key=lambda x: x.moons)
                else:
                    possible_leader.sort(key=lambda x: x.experience)
                self.patrol_leader = possible_leader[-1]
            else:
                self.patrol_leader = choice(self.patrol_cats)

        if clan.all_clans and len(clan.all_clans) > 0:
            self.other_clan = choice(clan.all_clans)
        else:
            self.other_clan = None

        # DETERMINE RANDOM CAT
        # Find random cat
        if len(patrol_cats) > 1:
            self.random_cat = choice(
                [i for i in patrol_cats if i != self.patrol_leader]
            )
        else:
            self.random_cat = choice(patrol_cats)

        print("Patrol Leader:", str(self.patrol_leader.name))
        print("Random Cat:", str(self.random_cat.name))

    def get_possible_patrols(
        self,
        current_season: str,
        biome: str,
        camp: str,
        patrol_type: str,
        game_setting_disaster=None,
    ) -> Tuple[List[PatrolEvent]]:
        # ---------------------------------------------------------------------------- #
        #                                LOAD RESOURCES                                #
        # ---------------------------------------------------------------------------- #
        biome = biome.lower()
        camp = camp.lower()
        game_setting_disaster = (
            game_setting_disaster
            if game_setting_disaster is not None
            else get_clan_setting("disasters")
        )
        season = current_season.lower()
        leaf = f"{season}"
        biome_dir = f"{biome}/"
        self.update_resources(biome_dir, leaf)

        possible_patrols = []
        # This is for debugging purposes, load-in *ALL* the possible patrols when debug_override_patrol_stat_requirements is true. (May require longer loading time)
        if constants.CONFIG["patrol_generation"][
            "debug_override_patrol_stat_requirements"
        ]:
            leaves = ["greenleaf", "leaf-bare", "leaf-fall", "newleaf", "any"]
            for biome in constants.BIOME_TYPES:
                for leaf in leaves:
                    biome_dir = f"{biome.lower()}/"
                    self.update_resources(biome_dir, leaf)
                    possible_patrols.extend(self.generate_patrol_events(self.HUNTING))
                    possible_patrols.extend(
                        self.generate_patrol_events(self.HUNTING_SZN)
                    )
                    possible_patrols.extend(self.generate_patrol_events(self.BORDER))
                    possible_patrols.extend(
                        self.generate_patrol_events(self.BORDER_SZN)
                    )
                    possible_patrols.extend(self.generate_patrol_events(self.TRAINING))
                    possible_patrols.extend(
                        self.generate_patrol_events(self.TRAINING_SZN)
                    )
                    possible_patrols.extend(self.generate_patrol_events(self.MEDCAT))
                    possible_patrols.extend(
                        self.generate_patrol_events(self.MEDCAT_SZN)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.HUNTING_GEN)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.BORDER_GEN)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.TRAINING_GEN)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.MEDCAT_GEN)
                    )
                    possible_patrols.extend(self.generate_patrol_events(self.DISASTER))
                    possible_patrols.extend(self.generate_patrol_events(self.NEW_CAT))
                    possible_patrols.extend(
                        self.generate_patrol_events(self.NEW_CAT_WELCOMING)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.NEW_CAT_HOSTILE)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.OTHER_CLAN)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.OTHER_CLAN_ALLIES)
                    )
                    possible_patrols.extend(
                        self.generate_patrol_events(self.OTHER_CLAN_HOSTILE)
                    )

        # this next one is needed for Classic specifically
        patrol_type = (
            "med"
            if [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE]
            in self.patrol_status_list
            else patrol_type
        )
        patrol_size = len(self.patrol_cats)
        reputation = game.clan.reputation  # reputation with outsiders
        other_clan = self.other_clan
        clan_relations = int(other_clan.relations) if other_clan else 0
        hostile_rep = False
        neutral_rep = False
        welcoming_rep = False
        clan_neutral = False
        clan_hostile = False
        clan_allies = False
        clan_size = int(len(game.clan.clan_cats))
        chance = 0
        # assigning other_clan relations
        if clan_relations > 17:
            clan_allies = True
        elif clan_relations < 7:
            clan_hostile = True
        elif 7 <= clan_relations <= 17:
            clan_neutral = True
        # this is just for separating them a bit from the other patrols, it means they can always happen
        other_clan_chance = 1
        # chance for each kind of loner event to occur
        small_clan = False
        if not other_clan:
            other_clan_chance = 0
        if clan_size < 20:
            small_clan = True
        regular_chance = int(random.getrandbits(2))
        hostile_chance = int(random.getrandbits(5))
        welcoming_chance = int(random.getrandbits(1))
        if 1 <= int(reputation) <= 30:
            hostile_rep = True
            if small_clan:
                chance = welcoming_chance
            else:
                chance = hostile_chance
        elif 31 <= int(reputation) <= 70:
            neutral_rep = True
            if small_clan:
                chance = welcoming_chance
            else:
                chance = regular_chance
        elif int(reputation) >= 71:
            welcoming_rep = True
            chance = welcoming_chance

        possible_patrols.extend(self.generate_patrol_events(self.HUNTING))
        possible_patrols.extend(self.generate_patrol_events(self.HUNTING_SZN))
        possible_patrols.extend(self.generate_patrol_events(self.BORDER))
        possible_patrols.extend(self.generate_patrol_events(self.BORDER_SZN))
        possible_patrols.extend(self.generate_patrol_events(self.TRAINING))
        possible_patrols.extend(self.generate_patrol_events(self.TRAINING_SZN))
        possible_patrols.extend(self.generate_patrol_events(self.MEDCAT))
        possible_patrols.extend(self.generate_patrol_events(self.MEDCAT_SZN))
        possible_patrols.extend(self.generate_patrol_events(self.HUNTING_GEN))
        possible_patrols.extend(self.generate_patrol_events(self.BORDER_GEN))
        possible_patrols.extend(self.generate_patrol_events(self.TRAINING_GEN))
        possible_patrols.extend(self.generate_patrol_events(self.MEDCAT_GEN))

        if game_setting_disaster:
            dis_chance = int(random.getrandbits(3))  # disaster patrol chance
            if dis_chance == 1:
                possible_patrols.extend(self.generate_patrol_events(self.DISASTER))

        # new cat patrols
        if chance == 1:
            if welcoming_rep:
                possible_patrols.extend(
                    self.generate_patrol_events(self.NEW_CAT_WELCOMING)
                )
            elif neutral_rep:
                possible_patrols.extend(self.generate_patrol_events(self.NEW_CAT))
            elif hostile_rep:
                possible_patrols.extend(
                    self.generate_patrol_events(self.NEW_CAT_HOSTILE)
                )

        # other Clan patrols
        if other_clan_chance == 1:
            if clan_neutral:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN))
            elif clan_allies:
                possible_patrols.extend(
                    self.generate_patrol_events(self.OTHER_CLAN_ALLIES)
                )
            elif clan_hostile:
                possible_patrols.extend(
                    self.generate_patrol_events(self.OTHER_CLAN_HOSTILE)
                )
        patrol_ids = [patrol.patrol_id for patrol in possible_patrols]
        if self.debug_patrol and self.debug_patrol not in patrol_ids:
            print(
                "DEBUG: requested patrol not present (check spelling/mismatched season, biome, patrol type, new cat flag, other clan relations, disaster setting)"
            )

        final_patrols, final_romance_patrols = self.get_filtered_patrols(
            possible_patrols, biome, camp, current_season, patrol_type
        )

        # This is a debug option, this allows you to remove any constraints of a patrol regarding location, session, biomes, etc.
        if constants.CONFIG["patrol_generation"][
            "debug_override_patrol_stat_requirements"
        ]:
            final_patrols = final_romance_patrols = possible_patrols
            # Logging
            print(
                "All patrol filters regarding location, session, etc. have been removed."
            )

        # This is a debug option. If the patrol_id set in "debug_ensure_patrol" is possible,
        # make it the *only* possible patrol
        if self.debug_patrol:
            for _pat in final_patrols:
                if _pat.patrol_id == self.debug_patrol:
                    patrol_type = choice(_pat.types) if _pat.types != [] else "general"
                    final_patrols = final_romance_patrols = [_pat]
                    print(
                        f"debug_ensure_patrol_id: "
                        f'"{constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]}" '
                        f"is a possible {patrol_type} patrol, and was set as the only "
                        f"{patrol_type} patrol option"
                    )
                    break
            else:
                print(
                    f"debug_ensure_patrol_id: "
                    f'"{constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]}" '
                    f"is not found. Check output for reason."
                )
        return final_patrols, final_romance_patrols

    def _check_constraints(self, patrol: PatrolEvent) -> bool:
        if not filter_relationship_type(
            group=self.patrol_cats,
            filter_types=patrol.relationship_constraints,
            event_id=patrol.patrol_id,
            patrol_leader=self.patrol_leader,
        ):
            if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                print(
                    "DEBUG: requested patrol does not meet constraints (relationship type)"
                )
            return False

        if (
            patrol.pl_skill_constraints
            and not self.patrol_leader.skills.check_skill_requirement_list(
                patrol.pl_skill_constraints
            )
        ):
            if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                print("DEBUG: requested patrol does not meet constraints (pl_skill)")
            return False

        if (
            patrol.pl_trait_constraints
            and self.patrol_leader.personality.trait not in patrol.pl_trait_constraints
        ):
            if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                print("DEBUG: requested patrol does not meet constraints (pl_trait)")
            return False

        return True

    @staticmethod
    def decide_if_romantic(
        romantic_event, patrol_leader, random_cat, patrol_apprentices: list
    ) -> bool:
        # if no romance was available or the patrol lead and random cat aren't potential mates then use the normal event

        if not romantic_event:
            print("No romantic event")
            return False

        if "rom_two_apps" in romantic_event.tags:
            if len(patrol_apprentices) < 2:
                print("somehow, there are not enough apprentices for romantic patrol")
                return False
            love1 = patrol_apprentices[0]
            love2 = patrol_apprentices[1]
        else:
            love1 = patrol_leader
            love2 = random_cat

        if (
            not love1.is_potential_mate(love2, for_love_interest=True)
            and love1.ID not in love2.mate
        ):
            print("not a potential mate or current mate")
            return False

        print("attempted romance between:", love1.name, love2.name)
        chance_of_romance_patrol = constants.CONFIG["patrol_generation"][
            "chance_of_romance_patrol"
        ]

        if (
            get_personality_compatibility(love1, love2) is True
            or love1.ID in love2.mate
        ):
            chance_of_romance_patrol -= 10
        else:
            chance_of_romance_patrol += 10

        values = [*RelType]
        for val in values:
            value_check = check_relationship_value(love1, love2, val)
            if value_check < 0:
                chance_of_romance_patrol -= 1
            elif value_check > 0:
                chance_of_romance_patrol += 2

        if chance_of_romance_patrol <= 0:
            chance_of_romance_patrol = 1
        print("final romance chance:", chance_of_romance_patrol)
        return not int(random.random() * chance_of_romance_patrol)

    def _filter_patrols(
        self,
        possible_patrols: List[PatrolEvent],
        biome: str,
        camp: str,
        current_season: str,
        patrol_type: str,
    ):
        filtered_patrols = []
        romantic_patrols = []
        # This make sure general only gets hunting, border, or training patrols
        # chose fix type will make it not depending on the content amount
        if patrol_type == "general":
            patrol_type = random.choice(["hunting", "border", "training"])

        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        for patrol in possible_patrols:
            if not self._check_constraints(patrol):
                continue

            # Don't check for repeat patrols if ensure_patrol_id is being used.
            if (
                constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"] == ""
                and patrol.patrol_id in self.used_patrols
            ):
                continue

            if not (patrol.min_cats <= len(self.patrol_cats) <= patrol.max_cats):
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print(
                        "DEBUG: requested patrol does not meet constraints (min or max cats range)"
                    )
                continue

            flag = False
            for sta, num in patrol.min_max_status.items():
                if len(num) != 2:
                    print(f"Issue with status limits: {patrol.patrol_id}")
                    continue

                if not (num[0] <= self.patrol_statuses.get(sta, -1) <= num[1]):
                    flag = True
                    break
            if flag:
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print(
                        "DEBUG: requested patrol does not meet constraints (min max status)"
                    )
                continue

            if not event_for_tags(patrol.tags, Cat):
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print("DEBUG: requested patrol does not meet constraints (tags)")
                continue

            if biome not in patrol.biome and "any" not in patrol.biome:
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print("DEBUG: requested patrol does not meet constraints (biome)")
                continue
            if camp not in patrol.camp and "any" not in patrol.camp:
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print("DEBUG: requested patrol does not meet constraints (camp)")
                continue
            if current_season not in patrol.season and "any" not in patrol.season:
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print("DEBUG: requested patrol does not meet constraints (season)")
                continue

            if "hunting" not in patrol.types and patrol_type == "hunting":
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print(
                        "DEBUG: requested patrol does not meet constraints (patrol type)"
                    )
                continue
            elif "border" not in patrol.types and patrol_type == "border":
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print(
                        "DEBUG: requested patrol does not meet constraints (patrol type)"
                    )
                continue
            elif "training" not in patrol.types and patrol_type == "training":
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print(
                        "DEBUG: requested patrol does not meet constraints (patrol type)"
                    )
                continue
            elif "herb_gathering" not in patrol.types and patrol_type == "med":
                if self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                    print(
                        "DEBUG: requested patrol does not meet constraints (patrol type)"
                    )
                continue

            if "romance" in patrol.tags:
                romantic_patrols.append(patrol)
            else:
                filtered_patrols.append(patrol)

        # make sure the hunting patrols are balanced
        if patrol_type == "hunting":
            filtered_patrols = self.balance_hunting(filtered_patrols)

        return filtered_patrols, romantic_patrols

    def get_filtered_patrols(
        self, possible_patrols, biome, camp, current_season, patrol_type
    ):
        filtered_patrols, romantic_patrols = self._filter_patrols(
            possible_patrols, biome, camp, current_season, patrol_type
        )

        if patrol_type == "herb_gathering":
            target_herbs = game.clan.herb_supply.sorted_by_need
            herb_filtered_patrols = []
            herb_romance_patrols = []

            i = 0
            while not herb_filtered_patrols and i <= len(target_herbs):
                i += 1
                herb_filtered_patrols = [
                    patrol
                    for patrol in filtered_patrols
                    if target_herbs[i] in patrol.herbs_given
                    or "random_herbs" in patrol.herbs_given
                ]
                herb_romance_patrols = [
                    patrol
                    for patrol in romantic_patrols
                    if target_herbs[i] in patrol.herbs_given
                    or "random_herbs" in patrol.herbs_given
                ]

            if herb_filtered_patrols:
                filtered_patrols = herb_filtered_patrols
                romantic_patrols = herb_romance_patrols

                if self.debug_patrol and self.debug_patrol not in [
                    patrol.patrol_id for patrol in filtered_patrols + romantic_patrols
                ]:
                    print(
                        "DEBUG: requested patrol removed during herb filtering (not target herb)"
                    )

        if not filtered_patrols:
            print(
                "No normal patrols possible. Repeating filter with used patrols cleared."
            )
            self.used_patrols.clear()
            print("used patrols cleared", self.used_patrols)
            filtered_patrols, romantic_patrols = self._filter_patrols(
                possible_patrols, biome, camp, current_season, patrol_type
            )

            if not filtered_patrols:
                raise Exception(
                    "No matching patrols found! This may be a localization issue."
                )

        return filtered_patrols, romantic_patrols

    def generate_patrol_events(self, patrol_dict):
        all_patrol_events = []
        for patrol in patrol_dict:
            patrol_event = PatrolEvent(
                patrol_id=patrol.get("patrol_id"),
                biome=patrol.get("biome"),
                camp=patrol.get("camp"),
                season=patrol.get("season"),
                tags=patrol.get("tags"),
                weight=patrol.get("weight", 20),
                types=patrol.get("types"),
                intro_text=patrol.get("intro_text"),
                patrol_art=patrol.get("patrol_art"),
                patrol_art_clean=patrol.get("patrol_art_clean"),
                success_outcomes=PatrolOutcome.generate_from_info(
                    patrol.get("success_outcomes")
                ),
                fail_outcomes=PatrolOutcome.generate_from_info(
                    patrol.get("fail_outcomes"), success=False
                ),
                decline_text=patrol.get("decline_text"),
                chance_of_success=patrol.get("chance_of_success"),
                min_cats=patrol.get("min_cats", 1),
                max_cats=patrol.get("max_cats", 6),
                min_max_status=patrol.get("min_max_status"),
                antag_success_outcomes=PatrolOutcome.generate_from_info(
                    patrol.get("antag_success_outcomes"), antagonize=True
                ),
                antag_fail_outcomes=PatrolOutcome.generate_from_info(
                    patrol.get("antag_fail_outcomes"), success=False, antagonize=True
                ),
                relationship_constraints=patrol.get("relationship_constraint"),
                pl_skill_constraints=patrol.get("pl_skill_constraint"),
                pl_trait_constraints=patrol.get("pl_trait_constraints"),
            )

            all_patrol_events.append(patrol_event)

        return all_patrol_events

    def determine_outcome(self, antagonize=False) -> Tuple[str, str, Optional[str]]:
        if self.patrol_event is None:
            raise Exception("No patrol event supplied")

        # First Step - Filter outcomes and pick a fail and success outcome
        success_outcomes = (
            self.patrol_event.antag_success_outcomes
            if antagonize
            else self.patrol_event.success_outcomes
        )
        fail_outcomes = (
            self.patrol_event.antag_fail_outcomes
            if antagonize
            else self.patrol_event.fail_outcomes
        )

        # Filter the outcomes. Do this only once - this is also where stat cats are determined
        success_outcomes = PatrolOutcome.prepare_allowed_outcomes(
            success_outcomes, self
        )
        fail_outcomes = PatrolOutcome.prepare_allowed_outcomes(fail_outcomes, self)

        # Choose a success and fail outcome
        chosen_success = choices(
            success_outcomes, weights=[x.weight for x in success_outcomes]
        )[0]
        chosen_failure = choices(
            fail_outcomes, weights=[x.weight for x in fail_outcomes]
        )[0]

        final_event, success = self.calculate_success(chosen_success, chosen_failure)

        print(f"PATROL ID: {self.patrol_event.patrol_id} | SUCCESS: {success}")

        # Run the chosen outcome
        return final_event.execute_outcome(self)

    def calculate_success(
        self, success_outcome: PatrolOutcome, fail_outcome: PatrolOutcome
    ) -> Tuple[PatrolOutcome, bool]:
        """Returns both the chosen event, and a boolean that's True if success, and False is fail."""

        patrol_size = len(self.patrol_cats)
        total_exp = sum([x.experience for x in self.patrol_cats])
        gm_modifier = constants.CONFIG["patrol_generation"][
            f"{game.clan.game_mode}_difficulty_modifier"
        ]

        exp_adustment = (
            (1 + 0.10 * patrol_size) * total_exp / (patrol_size * gm_modifier * 2)
        )

        success_chance = self.patrol_event.chance_of_success + int(exp_adustment)
        success_chance = min(success_chance, 90)

        # Now, apply success and fail skill
        print(
            "starting chance:",
            self.patrol_event.chance_of_success,
            "| EX_updated chance:",
            success_chance,
        )
        skill_updates = ""

        # Skill and trait stuff
        for kitty in self.patrol_cats:
            hits = kitty.skills.check_skill_requirement_list(success_outcome.stat_skill)
            success_chance += (
                hits * constants.CONFIG["patrol_generation"]["win_stat_cat_modifier"]
            )

            hits = kitty.skills.check_skill_requirement_list(fail_outcome.stat_skill)
            success_chance -= (
                hits * constants.CONFIG["patrol_generation"]["fail_stat_cat_modifier"]
            )

            if kitty.personality.trait in success_outcome.stat_trait:
                success_chance += constants.CONFIG["patrol_generation"][
                    "win_stat_cat_modifier"
                ]

            if kitty.personality.trait in fail_outcome.stat_trait:
                success_chance += constants.CONFIG["patrol_generation"][
                    "fail_stat_cat_modifier"
                ]

            skill_updates += f"{kitty.name} updated chance to {success_chance} | "

        if success_chance >= 120:
            success_chance = 115
            skill_updates += "success chance over 120, updated to 115"

        print(skill_updates)

        success = int(random.random() * 120) < success_chance

        # This is a debug option, this will forcefully change the outcome of a patrol
        if isinstance(
            constants.CONFIG["patrol_generation"]["debug_ensure_patrol_outcome"], bool
        ):
            success = constants.CONFIG["patrol_generation"][
                "debug_ensure_patrol_outcome"
            ]
            # Logging
            print(
                f"The outcome of {self.patrol_event.patrol_id} was altered to {success}"
            )

        return (success_outcome if success else fail_outcome, success)

    def update_resources(self, biome_dir, leaf):
        resources = [
            ("HUNTING_SZN", f"{biome_dir}hunting/{leaf}.json"),
            ("HUNTING", f"{biome_dir}hunting/any.json"),
            ("BORDER_SZN", f"{biome_dir}border/{leaf}.json"),
            ("BORDER", f"{biome_dir}border/any.json"),
            ("TRAINING_SZN", f"{biome_dir}training/{leaf}.json"),
            ("TRAINING", f"{biome_dir}training/any.json"),
            ("MEDCAT_SZN", f"{biome_dir}med/{leaf}.json"),
            ("MEDCAT", f"{biome_dir}med/any.json"),
            ("NEW_CAT", "new_cat.json"),
            ("NEW_CAT_HOSTILE", "new_cat_hostile.json"),
            ("NEW_CAT_WELCOMING", "new_cat_welcoming.json"),
            ("OTHER_CLAN", "other_clan.json"),
            ("OTHER_CLAN_HOSTILE", "other_clan_hostile.json"),
            ("OTHER_CLAN_ALLIES", "other_clan_allies.json"),
            ("HUNTING_GEN", "general/hunting.json"),
            ("BORDER_GEN", "general/border.json"),
            ("MEDCAT_GEN", "general/medcat.json"),
            ("TRAINING_GEN", "general/training.json"),
            ("DISASTER", "disaster.json"),
        ]
        for patrol_property, location in resources:
            try:
                setattr(
                    self, patrol_property, load_lang_resource(f"patrols/{location}")
                )
            except:
                raise Exception("Something went wrong loading patrols!")

    def balance_hunting(self, possible_patrols: list):
        """Filter the incoming hunting patrol list to balance the different kinds of hunting patrols.
        With this filtering, there should be more prey possible patrols.

            Parameters
            ----------
            possible_patrols : list
                list of patrols which should be filtered

            Returns
            ----------
            filtered_patrols : list
                list of patrols which is filtered
        """
        filtered_patrols = []

        # get first what kind of prey size which will be chosen
        biome = (
            game.clan.biome
            if not game.clan.override_biome
            else game.clan.override_biome
        )
        season = game.clan.current_season
        possible_prey_size = []
        idx = 0
        prey_size = ["very_small", "small", "medium", "large", "huge"]
        for amount in PATROL_BALANCE[biome][season]:
            possible_prey_size.extend(repeat(prey_size[idx], amount))
            idx += 1
        chosen_prey_size = choice(possible_prey_size)
        print(f"chosen filter prey size: {chosen_prey_size}")

        # filter all possible patrol depending on the needed prey size
        for patrol in possible_patrols:
            for adaption, needed_weight in PATROL_WEIGHT_ADAPTION.items():
                if needed_weight[0] <= patrol.weight < needed_weight[1]:
                    # get the amount of class sizes which can be increased
                    increment = int(adaption.split("_")[0])
                    new_idx = prey_size.index(chosen_prey_size) + increment
                    # check that the increment does not lead to a overflow
                    new_idx = (
                        new_idx if new_idx < len(prey_size) else len(prey_size) - 1
                    )
                    chosen_prey_size = deepcopy(prey_size[new_idx])

            # now count the outcomes + prey size
            prey_types = {}
            for outcome in patrol.success_outcomes:
                # ignore skill or trait outcomes
                if outcome.stat_trait or outcome.stat_skill:
                    continue
                if outcome.prey:
                    if outcome.prey[0] in prey_types:
                        prey_types[outcome.prey[0]] += 1
                    else:
                        prey_types[outcome.prey[0]] = 1

            # get the prey size with the most outcomes
            most_prey_size = ""
            max_occurrences = 0
            for size, amount in prey_types.items():
                if amount >= max_occurrences and most_prey_size != chosen_prey_size:
                    most_prey_size = size

            if chosen_prey_size == most_prey_size:
                filtered_patrols.append(patrol)
            elif self.debug_patrol and self.debug_patrol == patrol.patrol_id:
                print(
                    "DEBUG: requested patrol does not meet constraints (failed prey balancing)"
                )
        # if the filtering results in an empty list, don't filter and return whole possible patrols
        if len(filtered_patrols) <= 0:
            print(
                "---- WARNING ---- filtering to balance out the hunting, didn't work."
            )
            filtered_patrols = possible_patrols
        return filtered_patrols

    def get_patrol_art(self) -> pygame.Surface:
        """Return's patrol art surface"""
        if not self.patrol_event or not isinstance(self.patrol_event.patrol_art, str):
            return pygame.Surface((600, 600), flags=pygame.SRCALPHA)

        root_dir = "resources/images/patrol_art/"

        if game_setting_get("gore") and self.patrol_event.patrol_art_clean:
            file_name = self.patrol_event.patrol_art_clean
        else:
            file_name = self.patrol_event.patrol_art

        if not isinstance(file_name, str) or not path_exists(
            f"{root_dir}{file_name}.png"
        ):
            if "herb_gathering" in self.patrol_event.types:
                file_name = "med"
            elif "hunting" in self.patrol_event.types:
                file_name = "hunt"
            elif "border" in self.patrol_event.types:
                file_name = "bord"
            else:
                file_name = "train"

            file_name = f"{file_name}_general_intro"

        return pygame.image.load(f"{root_dir}{file_name}.png")

    def process_text(self, text, stat_cat: Optional[Cat]) -> str:
        """Processes text"""

        vowels = ["A", "E", "I", "O", "U"]
        if not text:
            text = "This should not appear, report as a bug please!"

        replace_dict = {
            "p_l": (str(self.patrol_leader.name), choice(self.patrol_leader.pronouns)),
            "r_c": (
                str(self.random_cat.name),
                choice(self.random_cat.pronouns),
            ),
        }

        text, senses, list_type, cat_tag = find_special_list_types(text)
        if list_type:
            sign_list = get_special_snippet_list(
                list_type, amount=randint(1, 3), sense_groups=senses
            )
            text = text.replace(list_type, str(sign_list))
            if cat_tag:
                text = text.replace("cat_tag", cat_tag)

        other_cats = [
            i
            for i in self.patrol_cats
            if i not in [self.patrol_leader, self.random_cat]
        ]
        if len(other_cats) >= 1:
            replace_dict["o_c1"] = (
                str(other_cats[0].name),
                choice(other_cats[0].pronouns),
            )
        if len(other_cats) >= 2:
            replace_dict["o_c2"] = (
                str(other_cats[1].name),
                choice(other_cats[1].pronouns),
            )
        if len(other_cats) >= 3:
            replace_dict["o_c3"] = (
                str(other_cats[2].name),
                choice(other_cats[2].pronouns),
            )
        if len(other_cats) == 4:
            replace_dict["o_c4"] = (
                str(other_cats[3].name),
                choice(other_cats[3].pronouns),
            )

        # New Cats
        for i, new_cats in enumerate(self.new_cats):
            if len(new_cats) == 1:
                names = str(new_cats[0].name)
                pronoun = choice(new_cats[0].pronouns)
            else:
                names = adjust_list_text([str(cat.name) for cat in new_cats])
                pronoun = localization.get_new_pronouns("default plural")

            replace_dict[f"n_c:{i}"] = (names, pronoun)

        if len(self.patrol_apprentices) > 0:
            replace_dict["app1"] = (
                str(self.patrol_apprentices[0].name),
                choice(self.patrol_apprentices[0].pronouns),
            )
        if len(self.patrol_apprentices) > 1:
            replace_dict["app2"] = (
                str(self.patrol_apprentices[1].name),
                choice(self.patrol_apprentices[1].pronouns),
            )
        if len(self.patrol_apprentices) > 2:
            replace_dict["app3"] = (
                str(self.patrol_apprentices[2].name),
                choice(self.patrol_apprentices[2].pronouns),
            )
        if len(self.patrol_apprentices) > 3:
            replace_dict["app4"] = (
                str(self.patrol_apprentices[3].name),
                choice(self.patrol_apprentices[3].pronouns),
            )
        if len(self.patrol_apprentices) > 4:
            replace_dict["app5"] = (
                str(self.patrol_apprentices[4].name),
                choice(self.patrol_apprentices[4].pronouns),
            )
        if len(self.patrol_apprentices) > 5:
            replace_dict["app6"] = (
                str(self.patrol_apprentices[5].name),
                choice(self.patrol_apprentices[5].pronouns),
            )

        if stat_cat:
            replace_dict["s_c"] = (str(stat_cat.name), choice(stat_cat.pronouns))

        text = process_text(text, replace_dict)
        text = adjust_prey_abbr(text)

        other_clan_name = self.other_clan.name
        s = 0
        for x in range(text.count("o_c_n")):
            if "o_c_n" in text:
                for y in vowels:
                    if str(other_clan_name).startswith(y):
                        modify = text.split()
                        pos = 0
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

        clan_name = game.clan.displayname
        s = 0
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

        text = text.replace("c_n", str(game.clan.displayname) + "Clan")

        # TODO: check if this can be handled in event_text_adjust
        return text


# ---------------------------------------------------------------------------- #
#                               PATROL CLASS END                               #
# ---------------------------------------------------------------------------- #

PATROL_WEIGHT_ADAPTION = game.prey_config["patrol_weight_adaption"]
PATROL_BALANCE = game.prey_config["patrol_balance"]

# ---------------------------------------------------------------------------- #
#                              GENERAL INFORMATION                             #
# ---------------------------------------------------------------------------- #

"""
More Documentation: https://docs.google.com/document/d/1Vuyclyd40mjG7PFXtl0852DlkcxIiyi_uIWxyi41sbI/edit?usp=sharing


Patrol Template.
This is a good starting point for writing your own patrols. 

{
    "patrol_id": "some_unique_id",
    "biome": [],
    "season": [],
    "types": [],
    "tags": [],
    "patrol_art": null,
    "patrol_art_clean": null,
    "min_cats": 1,
    "max_cats": 6,
    "min_max_status": {
        "apprentice": [0, 6],
        "medicine cat apprentice": [0, 6],
        "medicine cat": [0, 6],
        "deputy": [0, 6]
        "warrior": [0, 6],
        "leader": [0, 6],
        "healer cats": [0, 6],
        "normal_adult": [1, 6],
        "all apprentices": [1, 6]
    }
    "weight": 20,
    "chance_of_success": 50,
    "relationship_constraint": [],
    "pl_skill_constraint": [],
    "intro_text": "The patrol heads out.",
    "decline_text": "And they head right back!",
    "success_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
            
        },
    ],
    "fail_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
            
        },
    ],

    "antag_success_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
            
        },
    ],

    "antag_fail_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
            
        },
    ],

}



----------------------------------------------------------------------------------------

Outcome Block Template.
This is a good starting point for writing your own outcomes.
{
    "text": "The raw displayed outcome text.",
    "exp": 0,
    "weight": 20,
    "stat_skill": [],
    "stat_trait": [],
    "can_have_stat": [],
    "lost_cats": [],
    "dead_cats": [],
    "outsider_rep": null,
    "other_clan_rep": null,
    "injury": [
        {
            "cats": [],
            "injuries": [],
            "scars": [],
            "no_results": false
        },
        {
            "cats": [],
            "injuries": [],
            "scars": [],
            "no_results": false
        }
    ]
    "history_text": {
        "reg_death": "m_c died while on a patrol.",
        "leader_death": "died on patrol",
        "scar": "m_c was scarred on patrol",
    }
    "relationships": [
        {
            "cats_to": [],
            "cats_from": [],
            "mutual": false
            "values": [],
            "amount": 5
        },	
        {
            "cats_to": [],
            "cats_from": [],
            "mutual": false
            "values": [],
            "amount": 5
        }
    ],
    "new_cat" [
        [],
        []
    ],

}

"""
