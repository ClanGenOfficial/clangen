#!/usr/bin/env python3
# -*- coding: ascii -*-
import random
from random import choice, randint, choices
from typing import List, Tuple

import ujson
import pygame
from os.path import exists as path_exists

from scripts.cat.history import History
from scripts.clan import Clan
from scripts.utility import (
    get_personality_compatibility,
    check_relationship_value,
    process_text,
    adjust_prey_abbr,
    find_special_list_types,
    get_special_snippet_list
)
from scripts.game_structure.game_essentials import game
from itertools import combinations
from scripts.patrol.patrol_event import PatrolEvent
from scripts.patrol.patrol_outcome import PatrolOutcome
from scripts.cat.cats import Cat
from scripts.special_dates import get_special_date, contains_special_date_tag

# ---------------------------------------------------------------------------- #
#                              PATROL CLASS START                              #
# ---------------------------------------------------------------------------- #
"""
When adding new patrols, use \n to add a paragraph break in the text
"""


class Patrol():
    used_patrols = []
    
    def __init__(self):
        
        self.patrol_event: PatrolEvent = None
    
        self.patrol_leader = None
        self.patrol_random_cat = None
        self.patrol_cats = []
        self.patrol_apprentices = []
        self.other_clan = None
        self.intro_text = ""

        self.patrol_statuses = {}
        self.patrol_status_list = []
        
        # Holds new cats for easy access
        self.new_cats: List[List[Cat]] = []

    def setup_patrol(self, patrol_cats:List[Cat], patrol_type:str) -> str:
        # Add cats
        
        print("PATROL START ---------------------------------------------------")
        
        self.add_patrol_cats(patrol_cats, game.clan)
        
        final_patrols, final_romance_patrols = self.get_possible_patrols(
            str(game.clan.current_season).casefold(),
            str(game.clan.biome).casefold(),
            patrol_type,
            game.settings.get('disasters')
        )
        
        print(f'Total Number of Possible Patrols | normal: {len(final_patrols)}, romantic: {len(final_romance_patrols)} ')
        
        if final_patrols:
            normal_event_choice = choices(final_patrols, weights=[x.weight for x in final_patrols])[0]
        else:
            print("ERROR: NO POSSIBLE NORMAL PATROLS FOUND for: ", self.patrol_statuses)
            raise RuntimeError
        
        romantic_event_choice = None
        if final_romance_patrols:
            romantic_event_choice = choices(final_romance_patrols, [x.weight for x in final_romance_patrols])[0]
        
        if romantic_event_choice and Patrol.decide_if_romantic(romantic_event_choice, 
                                                               self.patrol_leader, 
                                                               self.patrol_random_cat, 
                                                               self.patrol_apprentices):
            print("did the romance")
            self.patrol_event = romantic_event_choice
        else:
            self.patrol_event = normal_event_choice
            
        Patrol.used_patrols.append(self.patrol_event.patrol_id)
        
        return self.process_text(self.patrol_event.intro_text, None)

    def proceed_patrol(self, path:str="proceed") -> Tuple[str]:
        """Proceed the patrol to the next step. 
            path can be: "proceed", "antag", or "decline" """
        
        if path == "decline":
            if self.patrol_event:
                return self.process_text(self.patrol_event.decline_text, None), ""
            else:
                return "Error - no event chosen", ""
        
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
            
            if cat.status == 'apprentice' or cat.status == 'medicine cat apprentice':
                self.patrol_apprentices.append(cat)
            
            self.patrol_status_list.append(cat.status)
            
            if cat.status in self.patrol_statuses:
                self.patrol_statuses[cat.status] += 1
            else:
                self.patrol_statuses[cat.status] = 1
            
            # Combined patrol_statuses catagories
            if cat.status in ("medicine cat", "medicine cat apprentice"):
                if "healer cats" in self.patrol_statuses:
                    self.patrol_statuses["healer cats"] += 1
                else:
                    self.patrol_statuses["healer cats"] = 1
            
            if cat.status in ("apprentice", "medicine cat apprentice"):
                if "all apprentices" in self.patrol_statuses:
                    self.patrol_statuses["all apprentices"] += 1
                else:
                    self.patrol_statuses["all apprentices"] = 1
                    
            if cat.status in ("warrior", "deputy", "leader"):
                if "normal adult" in self.patrol_statuses:
                    self.patrol_statuses["normal adult"] += 1
                else:
                    self.patrol_statuses["normal adult"] = 1
            
            game.patrolled.append(cat.ID)


        #PATROL LEADER AND RANDOM CAT CAN NOT CHANGE AFTER SET-UP

        # DETERMINE PATROL LEADER
        # sets medcat as leader if they're in the patrol
        if "medicine cat" in self.patrol_status_list:
            index = self.patrol_status_list.index("medicine cat")
            self.patrol_leader = self.patrol_cats[index]
        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warrior from being treated as medicine cats in medicine cat patrols.
        elif "medicine cat apprentice" in self.patrol_status_list:
            index = self.patrol_status_list.index("medicine cat apprentice")
            self.patrol_leader = self.patrol_cats[index]
            # then we just make sure that this app will also be app1
            self.patrol_apprentices.remove(self.patrol_leader)
            self.patrol_apprentices = [self.patrol_leader] + self.patrol_apprentices
        # sets leader as patrol leader
        elif "leader" in self.patrol_status_list:
            index = self.patrol_status_list.index("leader")
            self.patrol_leader = self.patrol_cats[index]
        elif "deputy" in self.patrol_status_list:
            index = self.patrol_status_list.index("deputy")
            self.patrol_leader = self.patrol_cats[index]
        else:
            # Get the oldest cat
            possible_leader = [i for i in self.patrol_cats if i.status not in 
                               ["medicine cat apprentice", "apprentice"]]
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
        #Find random cat
        if len(patrol_cats) > 1:
            self.patrol_random_cat = choice([i for i in patrol_cats if i != self.patrol_leader])
        else:
            self.patrol_random_cat = choice(patrol_cats)
            
        print("Patrol Leader:", str(self.patrol_leader.name))
        print("Random Cat:", str(self.patrol_random_cat.name))

    def get_possible_patrols(self, current_season:str, biome:str, patrol_type:str,
                             game_setting_disaster=None) -> Tuple[List[PatrolEvent]]:
        # ---------------------------------------------------------------------------- #
        #                                LOAD RESOURCES                                #
        # ---------------------------------------------------------------------------- #
        biome = biome.lower()
        game_setting_disaster = game_setting_disaster if game_setting_disaster is not None else \
                                game.clan.clan_settings['disasters']
        season = current_season.lower()
        biome_dir = f"{biome}/"
        leaf = f"{season}"
        self.update_resources(biome_dir, leaf)

        possible_patrols = []
        # this next one is needed for Classic specifically
        patrol_type = "med" if ['medicine cat', 'medicine cat apprentice'] in self.patrol_status_list else patrol_type
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
        other_clan_chance = 1  # this is just for separating them a bit from the other patrols, it means they can always happen
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
                possible_patrols.extend(self.generate_patrol_events(self.NEW_CAT_WELCOMING))
            elif neutral_rep:
                possible_patrols.extend(self.generate_patrol_events(self.NEW_CAT))
            elif hostile_rep:
                possible_patrols.extend(self.generate_patrol_events(self.NEW_CAT_HOSTILE))

        # other Clan patrols
        if other_clan_chance == 1:
            if clan_neutral:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN))
            elif clan_allies:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN_ALLIES))
            elif clan_hostile:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN_HOSTILE))

        final_patrols, final_romance_patrols = self. get_filtered_patrols(possible_patrols, biome, current_season,
                                                                          patrol_type)

        # This is a debug option. If the patrol_id set isn "debug_ensure_patrol" is possible, 
        # make it the *only* possible patrol
        if isinstance(game.config["patrol_generation"]["debug_ensure_patrol_id"], str):
            for _pat in final_patrols:
                if _pat.patrol_id == game.config["patrol_generation"]["debug_ensure_patrol_id"]:
                    final_patrols = [_pat]
                    print(f"debug_ensure_patrol_id: " 
                          f'"{game.config["patrol_generation"]["debug_ensure_patrol_id"]}" '
                           "is a possible normal patrol, and was set as the only "
                           "normal patrol option")
                    break
            else:
                print(f"debug_ensure_patrol_id: "
                      f'"{game.config["patrol_generation"]["debug_ensure_patrol_id"]}" '
                      "is not a possible normal patrol.")
            
            for _pat in final_romance_patrols:
                if _pat.patrol_id == game.config["patrol_generation"]["debug_ensure_patrol_id"]:
                    final_romance_patrols = [_pat]
                    print(f"debug_ensure_patrol_id: " 
                          f'"{game.config["patrol_generation"]["debug_ensure_patrol_id"]}" '
                           "is a possible romantic patrol, and was set as the only "
                           "romantic patrol option")
                    break
            else:
                print(f"debug_ensure_patrol_id: "
                      f'"{game.config["patrol_generation"]["debug_ensure_patrol_id"]}" '
                      "is not a possible romantic patrol.")
            
        return final_patrols, final_romance_patrols

    def _check_constraints(self, patrol: PatrolEvent) -> bool:
        if not self._filter_relationship(patrol):
            return False

        if patrol.pl_skill_constraints and not self.patrol_leader.skills.check_skill_requirement_list(patrol.pl_skill_constraints):
            return False
        
        if patrol.pl_trait_constraints and self.patrol_leader.personality.trait not in patrol.pl_trait_constraints:
            return False
            
        return True

    def _filter_relationship(self, patrol:PatrolEvent):
        """
        Filter the incoming patrol list according to the relationship constraints, if there are constraints.

        """

        # filtering - relationship status
        # check if all are siblings
        if "siblings" in patrol.relationship_constraints:
            test_cat = self.patrol_cats[0]
            testing_cats = [cat for cat in self.patrol_cats if cat.ID != test_cat.ID]

            siblings = [test_cat.is_sibling(inter_cat) for inter_cat in testing_cats]
            if not all(siblings):
                return False
            
        # check if the cats are mates
        if "mates" in patrol.relationship_constraints:
            # First test if there is more then one cat
            if len(self.patrol_cats) == 1:
                return False
            
            # Then if cats don't have the needed number of mates. 
            if not all(len(i.mate) >= (len(self.patrol_cats) - 1) for i in self.patrol_cats):
                return False
            
            # Now the expensive test. We have to see if everyone is mates with each other
            # Hopefully the cheaper tests mean this is only needed on small patrols. 
            for x in combinations(self.patrol_cats, 2):
                if x[0].ID not in x[1].mate:
                    return False
                

        # check if the cats are in a parent/child relationship
        if "parent/child" in patrol.relationship_constraints:
            # it should be exactly two cats for a "parent/child" patrol
            if len(self.patrol_cats) != 2:
                return False
            # when there are two cats in the patrol, p_l and r_c are different cats per default
            if not self.patrol_leader.is_parent(self.patrol_random_cat):
                return False

        # check if the cats are in a child/parent relationship
        if "child/parent" in patrol.relationship_constraints:
            # it should be exactly two cats for a "child/parent" patrol
            if len(self.patrol_cats) != 2:
                return False
            # when there are two cats in the patrol, p_l and r_c are different cats per default
            if not self.patrol_random_cat.is_parent(self.patrol_leader):
                return False

        # filtering - relationship values
        # when there will be more relationship values or other tags, this should be updated
        value_types = ["romantic", "platonic", "dislike", "comfortable", "jealousy", "trust"]
        break_loop = False
        for v_type in value_types:
            patrol_id = patrol.patrol_id
            # first get all tags for the current value type
            tags = [constraint for constraint in patrol.relationship_constraints if v_type in constraint]

            # there is not such a tag for the current value type, check the next one
            if len(tags) == 0:
                continue

            # there should be only one value constraint for each value type
            elif len(tags) > 1:
                print(f"ERROR: patrol {patrol_id} has multiple relationship constraints for the value {v_type}.")
                break_loop = True
                break

            threshold = 0
            # try to extract the value/threshold from the text
            try:
                threshold = int(tags[0].split('_')[1])
            except Exception as e:
                print(
                    f"ERROR: patrol {patrol_id} with the relationship constraint for the value {v_type} follows not the formatting guidelines.")
                break_loop = True
                break

            if threshold > 100:
                print(
                    f"ERROR: patrol {patrol_id} has a relationship constraints for the value {v_type}, which is higher than the max value of a relationship.")
                break_loop = True
                break

            if threshold <= 0:
                print(
                    f"ERROR: patrol {patrol_id} has a relationship constraints for the value {v_type}, which is lower than the min value of a relationship or 0.")
                break_loop = True
                break

            # each cat has to have relationships with this relationship value above the threshold
            fulfilled = True
            for inter_cat in self.patrol_cats:
                rel_above_threshold = []
                patrol_cats_ids = [cat.ID for cat in self.patrol_cats]
                relevant_relationships = list(
                    filter(lambda rel: rel.cat_to.ID in patrol_cats_ids and rel.cat_to.ID != inter_cat.ID,
                           list(inter_cat.relationships.values())
                           )
                )

                # get the relationships depending on the current value type + threshold
                if v_type == "romantic":
                    rel_above_threshold = [i for i in relevant_relationships if i.romantic_love >= threshold]
                elif v_type == "platonic":
                    rel_above_threshold = [i for i in relevant_relationships if i.platonic_like >= threshold]
                elif v_type == "dislike":
                    rel_above_threshold = [i for i in relevant_relationships if i.dislike >= threshold]
                elif v_type == "comfortable":
                    rel_above_threshold = [i for i in relevant_relationships if i.comfortable >= threshold]
                elif v_type == "jealousy":
                    rel_above_threshold = [i for i in relevant_relationships if i.jealousy >= threshold]
                elif v_type == "trust":
                    rel_above_threshold = [i for i in relevant_relationships if i.trust >= threshold]

                # if the lengths are not equal, one cat has not the relationship value which is needed to another cat of the patrol
                if len(rel_above_threshold) + 1 != len(self.patrol_cats):
                    fulfilled = False
                    break

            if not fulfilled:
                break_loop = True
                break

        # if break is used in the loop, the condition are not fulfilled
        # and this patrol should not be added to the filtered list
        if break_loop:
            return False

        return True

    @staticmethod
    def decide_if_romantic(romantic_event, patrol_leader, random_cat, patrol_apprentices:list) -> bool:
         # if no romance was available or the patrol lead and random cat aren't potential mates then use the normal event

        if not romantic_event:
            print("No romantic event")
            return False
        
        if "rom_two_apps" in romantic_event.tags:
            if len(patrol_apprentices) < 2:
                print('somehow, there are not enough apprentices for romantic patrol')
                return False
            love1 = patrol_apprentices[0]
            love2 = patrol_apprentices[1]
        else:
            love1 = patrol_leader
            love2 = random_cat
        
        if not love1.is_potential_mate(love2, for_love_interest=True) \
                and love1.ID not in love2.mate:
            print('not a potential mate or current mate')
            return False 
        

        print("attempted romance between:", love1.name, love2.name)
        chance_of_romance_patrol = game.config["patrol_generation"]["chance_of_romance_patrol"]

        if get_personality_compatibility(love1,
                                         love2) is True or love1.ID in love2.mate:
            chance_of_romance_patrol -= 10
        else:
            chance_of_romance_patrol += 10
        
        values = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
        for val in values:
            value_check = check_relationship_value(love1, love2, val)
            if val in ["romantic", "platonic", "admiration", "comfortable", "trust"] and value_check >= 20:
                chance_of_romance_patrol -= 1
            elif val in ["dislike", "jealousy"] and value_check >= 20:
                chance_of_romance_patrol += 2
        if chance_of_romance_patrol <= 0:
            chance_of_romance_patrol = 1
        print("final romance chance:", chance_of_romance_patrol)
        return not int(random.random() * chance_of_romance_patrol)

    def _filter_patrols(self, possible_patrols: List[PatrolEvent], biome:str, current_season:str, patrol_type:str):
        filtered_patrols = []
        romantic_patrols = []
        special_date = get_special_date()

        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        for patrol in possible_patrols:
            if not self._check_constraints(patrol):
                continue
            
            # Don't check for repeat patrols if ensure_patrol_id is being used. 
            if not isinstance(game.config["patrol_generation"]["debug_ensure_patrol_id"], str) and \
                    patrol.patrol_id in self.used_patrols:
                continue

            # filtering for dates
            if contains_special_date_tag(patrol.tags):
                if not special_date or special_date.patrol_tag not in patrol.tags:
                    continue

            if not (patrol.min_cats <= len(self.patrol_cats) <= patrol.max_cats):
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
                continue
            
            if biome not in patrol.biome and "Any" not in patrol.biome:
                continue
            if current_season not in patrol.season and "Any" not in patrol.season:
                continue

            #  correct button check
            if patrol_type == "general":
                if not set(patrol.types).intersection({"hunting", "border", "training"}):
                    # This make sure general only gets hunting, border, or training patrols.
                    continue
            else:
                if 'hunting' not in patrol.types and patrol_type == 'hunting':
                    continue
                elif 'border' not in patrol.types and patrol_type == 'border':
                    continue
                elif 'training' not in patrol.types and patrol_type == 'training':
                    continue
                elif 'herb_gathering' not in patrol.types and patrol_type == 'med':
                    continue

            # cruel season tag check
            if "cruel_season" in patrol.tags:
                if game.clan.game_mode != 'cruel_season':
                    continue

            if "romantic" in patrol.tags:
                romantic_patrols.append(patrol)
            else:
                filtered_patrols.append(patrol)

        # I'll get to that later, hahah TODO
        #if patrol_type == 'hunting':
        #    filtered_patrols = self.balance_hunting(filtered_patrols)

        return filtered_patrols, romantic_patrols

    def get_filtered_patrols(self, possible_patrols, biome, current_season, patrol_type):
        
        filtered_patrols, romantic_patrols = self._filter_patrols(possible_patrols, biome, current_season,
                                                                  patrol_type)
        
        if not filtered_patrols:
            print('No normal patrols possible. Repeating filter with used patrols cleared.')
            self.used_patrols.clear()
            print('used patrols cleared', self.used_patrols)
            filtered_patrols, romantic_patrols = self._filter_patrols(possible_patrols, biome,
                                                                      current_season, patrol_type)    
        
        return filtered_patrols, romantic_patrols

    def generate_patrol_events(self, patrol_dict):
        all_patrol_events = []
        for patrol in patrol_dict:
            patrol_event = PatrolEvent(
                patrol_id=patrol.get("patrol_id"),
                biome=patrol.get("biome"),
                season=patrol.get("season"),
                tags=patrol.get("tags"),
                types=patrol.get("types"),
                intro_text=patrol.get("intro_text"),
                patrol_art=patrol.get("patrol_art"),
                patrol_art_clean=patrol.get("patrol_art_clean"),
                success_outcomes=PatrolOutcome.generate_from_info(patrol.get("success_outcomes")),
                fail_outcomes=PatrolOutcome.generate_from_info(patrol.get("fail_outcomes"), success=False),
                decline_text=patrol.get("decline_text"),
                chance_of_success=patrol.get("chance_of_success"),
                min_cats=patrol.get("min_cats", 1),
                max_cats=patrol.get("max_cats", 6),
                min_max_status=patrol.get("min_max_status"),
                antag_success_outcomes=PatrolOutcome.generate_from_info(patrol.get("antag_success_outcomes"), antagonize=True),
                antag_fail_outcomes=PatrolOutcome.generate_from_info(patrol.get("antag_fail_outcomes"), success=False, 
                                                                     antagonize=True),
                relationship_constraints=patrol.get("relationship_constraint"),
                pl_skill_constraints=patrol.get("pl_skill_constraint"),
                pl_trait_constraints=patrol.get("pl_trait_constraints")
            )

            all_patrol_events.append(patrol_event)

        return all_patrol_events

    def determine_outcome(self, antagonize=False) -> Tuple[str]:
        
        if self.patrol_event is None:
            return
        
        # First Step - Filter outcomes and pick a fail and success outcome
        success_outcomes = self.patrol_event.antag_success_outcomes if antagonize else \
                           self.patrol_event.success_outcomes
        fail_outcomes = self.patrol_event.antag_fail_outcomes if antagonize else \
                        self.patrol_event.fail_outcomes
                        
        # Filter the outcomes. Do this only once - this is also where stat cats are determined
        success_outcomes = PatrolOutcome.prepare_allowed_outcomes(success_outcomes, self)
        fail_outcomes = PatrolOutcome.prepare_allowed_outcomes(fail_outcomes, self)
        
        # Choose a success and fail outcome
        chosen_success = choices(success_outcomes, weights=[x.weight for x in success_outcomes])[0]
        chosen_failure = choices(fail_outcomes, weights=[x.weight for x in fail_outcomes])[0]
        
        final_event, success = self.calculate_success(chosen_success, chosen_failure)
        
        print(f"PATROL ID: {self.patrol_event.patrol_id} | SUCCESS: {success}")        
        
        # Run the chosen outcome
        return final_event.execute_outcome(self)
        
    def calculate_success(self, success_outcome: PatrolOutcome, fail_outcome: PatrolOutcome) -> Tuple[PatrolOutcome, bool]:
        """Returns both the chosen event, and a boolian that's True if success, and False is fail."""
        
        patrol_size = len(self.patrol_cats)
        total_exp = sum([x.experience for x in self.patrol_cats])
        gm_modifier = game.config["patrol_generation"][f"{game.clan.game_mode}_difficulty_modifier"]
        
        exp_adustment = (1 + 0.10 * patrol_size) * total_exp / (
                patrol_size * gm_modifier * 2)
        
        success_chance = self.patrol_event.chance_of_success + int(exp_adustment)
        success_chance = min(success_chance, 90)
        
        # Now, apply success and fail skill 
        print('starting chance:', self.patrol_event.chance_of_success, "| EX_updated chance:", success_chance)
        skill_updates = ""
        
        # Skill and trait stuff
        for kitty in self.patrol_cats:
            hits = kitty.skills.check_skill_requirement_list(success_outcome.stat_skill)
            success_chance += hits * game.config["patrol_generation"]["win_stat_cat_modifier"] 
            
            hits = kitty.skills.check_skill_requirement_list(fail_outcome.stat_skill)
            success_chance -= hits * game.config["patrol_generation"]["fail_stat_cat_modifier"]
            
    
            if kitty.personality.trait in success_outcome.stat_trait:
                success_chance += game.config["patrol_generation"]["win_stat_cat_modifier"]
                
            if kitty.personality.trait in fail_outcome.stat_trait:
                success_chance += game.config["patrol_generation"]["fail_stat_cat_modifier"]

            skill_updates += f"{kitty.name} updated chance to {success_chance} | "
        
        if success_chance >= 120:
            success_chance = 115
            skill_updates += "success chance over 120, updated to 115"
        
        print(skill_updates)
        
        success = int(random.random() * 120) < success_chance
        return (success_outcome if success else fail_outcome, success)
        
    def update_resources(self, biome_dir, leaf):
        resource_dir = "resources/dicts/patrols/"
        # HUNTING #
        self.HUNTING_SZN = None
        with open(f"{resource_dir}{biome_dir}hunting/{leaf}.json", 'r', encoding='ascii') as read_file:
            self.HUNTING_SZN = ujson.loads(read_file.read())
        self.HUNTING = None
        with open(f"{resource_dir}{biome_dir}hunting/any.json", 'r', encoding='ascii') as read_file:
            self.HUNTING = ujson.loads(read_file.read())
        # BORDER #
        self.BORDER_SZN = None
        with open(f"{resource_dir}{biome_dir}border/{leaf}.json", 'r', encoding='ascii') as read_file:
            self.BORDER_SZN = ujson.loads(read_file.read())
        self.BORDER = None
        with open(f"{resource_dir}{biome_dir}border/any.json", 'r', encoding='ascii') as read_file:
            self.BORDER = ujson.loads(read_file.read())
        # TRAINING #
        self.TRAINING_SZN = None
        with open(f"{resource_dir}{biome_dir}training/{leaf}.json", 'r', encoding='ascii') as read_file:
            self.TRAINING_SZN = ujson.loads(read_file.read())
        self.TRAINING = None
        with open(f"{resource_dir}{biome_dir}training/any.json", 'r', encoding='ascii') as read_file:
            self.TRAINING = ujson.loads(read_file.read())
        # MED #
        self.MEDCAT_SZN = None
        with open(f"{resource_dir}{biome_dir}med/{leaf}.json", 'r', encoding='ascii') as read_file:
            self.MEDCAT_SZN = ujson.loads(read_file.read())
        self.MEDCAT = None
        with open(f"{resource_dir}{biome_dir}med/any.json", 'r', encoding='ascii') as read_file:
            self.MEDCAT = ujson.loads(read_file.read())
        # NEW CAT #
        self.NEW_CAT = None
        with open(f"{resource_dir}new_cat.json", 'r', encoding='ascii') as read_file:
            self.NEW_CAT = ujson.loads(read_file.read())
        self.NEW_CAT_HOSTILE = None
        with open(f"{resource_dir}new_cat_hostile.json", 'r', encoding='ascii') as read_file:
            self.NEW_CAT_HOSTILE = ujson.loads(read_file.read())
        self.NEW_CAT_WELCOMING = None
        with open(f"{resource_dir}new_cat_welcoming.json", 'r', encoding='ascii') as read_file:
            self.NEW_CAT_WELCOMING = ujson.loads(read_file.read())
        # OTHER CLAN #
        self.OTHER_CLAN = None
        with open(f"{resource_dir}other_clan.json", 'r', encoding='ascii') as read_file:
            self.OTHER_CLAN = ujson.loads(read_file.read())
        self.OTHER_CLAN_ALLIES = None
        with open(f"{resource_dir}other_clan_allies.json", 'r', encoding='ascii') as read_file:
            self.OTHER_CLAN_ALLIES = ujson.loads(read_file.read())
        self.OTHER_CLAN_HOSTILE = None
        with open(f"{resource_dir}other_clan_hostile.json", 'r', encoding='ascii') as read_file:
            self.OTHER_CLAN_HOSTILE = ujson.loads(read_file.read())
        self.DISASTER = None
        with open(f"{resource_dir}disaster.json", 'r', encoding='ascii') as read_file:
            self.DISASTER = ujson.loads(read_file.read())
        # sighing heavily as I add general patrols back in
        self.HUNTING_GEN = None
        with open(f"{resource_dir}general/hunting.json", 'r', encoding='ascii') as read_file:
            self.HUNTING_GEN = ujson.loads(read_file.read())
        self.BORDER_GEN = None
        with open(f"{resource_dir}general/border.json", 'r', encoding='ascii') as read_file:
            self.BORDER_GEN = ujson.loads(read_file.read())
        self.TRAINING_GEN = None
        with open(f"{resource_dir}general/training.json", 'r', encoding='ascii') as read_file:
            self.TRAINING_GEN = ujson.loads(read_file.read())
        self.MEDCAT_GEN = None
        with open(f"{resource_dir}general/medcat.json", 'r', encoding='ascii') as read_file:
            self.MEDCAT_GEN = ujson.loads(read_file.read())

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

        # get first what kind of hunting type which will be chosen
        patrol_type = ["fighting", "injury", "prey", "prey", "more_prey", "less_prey", "all"]
        needed_tags = []
        not_allowed_tag = None
        chosen_tag = choice(patrol_type)
        # add different tags which should be in the patrol
        if chosen_tag == "all":
            return possible_patrols
        if chosen_tag == "fighting":
            needed_tags.append("fighting")
            needed_tags.append("death")
        elif chosen_tag == "injury":
            needed_tags.append("injury")
            needed_tags.append("blunt_force_injury")
            needed_tags.append("big_bite_injury")
            needed_tags.append("small_bite_injury")
            needed_tags.append("minor_injury")
            needed_tags.append("cold_injury")
            needed_tags.append("hot_injury")
        elif chosen_tag in ["less_prey", "prey"]:
            if chosen_tag == "prey":
                not_allowed_tag = "death"
            prey_types = ["small_prey", "medium_prey", "large_prey", "huge_prey"]
            for prey_type in prey_types:
                if chosen_tag == "less_prey" and prey_type in ["large_prey", "huge_prey"]:
                    continue
                needed_tags.append(f"{prey_type}")
                if prey_type != "small_prey":
                    needed_tags.append(f"{prey_type}0")
                    needed_tags.append(f"{prey_type}1")
                    needed_tags.append(f"{prey_type}2")
                    needed_tags.append(f"{prey_type}3")
        elif chosen_tag == "more_prey":
            not_allowed_tag = "death"
            needed_tags.append("large_prey")
            needed_tags.append("huge_prey")
            needed_tags.append("huge_prey0")
            needed_tags.append("huge_prey1")
            needed_tags.append("huge_prey2")
            needed_tags.append("huge_prey3")

        # filter all possible patrol depending on the needed tags
        # one of the mentioned tags should be in the patrol tag
        for patrol in possible_patrols:
            for tag in needed_tags:
                if tag in patrol.tags:
                    # if there is a tag set, check if this tag is not in the current patrol
                    if not_allowed_tag and not_allowed_tag not in patrol.tags:
                        filtered_patrols.append(patrol)
                        break
                    # when there is no tag set, add the patrol
                    elif not not_allowed_tag:
                        filtered_patrols.append(patrol)
                        break

        # if the filtering results in an empty list, don't filter and return whole possible patrols
        if len(filtered_patrols) <= 0:
            print("WARNING: filtering to balance out the hunting, didn't work.")
            filtered_patrols = possible_patrols
        return filtered_patrols

    def get_patrol_art(self) -> pygame.Surface:
        """Return's patrol art surface """
        if not self.patrol_event or not isinstance(self.patrol_event.patrol_art, str):
            return pygame.Surface((600, 600), flags=pygame.SRCALPHA)
        
        root_dir = "resources/images/patrol_art/"
        
        if game.settings.get("gore") and self.patrol_event.patrol_art_clean:
            file_name = self.patrol_event.patrol_art_clean
        else:
            file_name = self.patrol_event.patrol_art
            
        
        if not isinstance(file_name, str) or not path_exists(f"{root_dir}{file_name}.png"):
            if "herb_gathering" in self.patrol_event.types:
                file_name = 'med'
            elif "hunting" in self.patrol_event.types:
                file_name = 'hunt'
            elif "border" in self.patrol_event.types:
                file_name = 'bord'
            else:
                file_name = 'train'
            
            file_name = f"{file_name}_general_intro"
            
        return pygame.image.load(f"{root_dir}{file_name}.png")
    
    def process_text(self, text, stat_cat:Cat) -> str:
        """Processes text """

        vowels = ['A', 'E', 'I', 'O', 'U']
        if not text:
            text = 'This should not appear, report as a bug please!'

        replace_dict = {
            "p_l": (str(self.patrol_leader.name), choice(self.patrol_leader.pronouns)),
            "r_c": (str(self.patrol_random_cat.name), choice(self.patrol_random_cat.pronouns)),
        }

        other_cats = [i for i in self.patrol_cats if i not in [self.patrol_leader, self.patrol_random_cat]]
        if len(other_cats) >= 1:
            replace_dict['o_c1'] = (str(other_cats[0].name),
                                    choice(other_cats[0].pronouns))
        if len(other_cats) >= 2:
            replace_dict['o_c2'] = (str(other_cats[1].name),
                                    choice(other_cats[1].pronouns))
        if len(other_cats) >= 3:
            replace_dict['o_c3'] = (str(other_cats[2].name),
                                    choice(other_cats[2].pronouns))
        if len(other_cats) == 4:
            replace_dict['o_c4'] = (str(other_cats[3].name),
                                    choice(other_cats[3].pronouns))

        # New Cats
        for i, new_cats in enumerate(self.new_cats):
            if len(new_cats) == 1:
                names = str(new_cats[0].name)
                pronoun = choice(new_cats[0].pronouns)
            elif len(new_cats) == 1:
                names = f"{new_cats[0].name} and {new_cats[1].name}"
                pronoun = Cat.default_pronouns[0] # They/them for muliple cats
            else:
                names = ", ".join([str(x.name) for x in new_cats[:-1]]) +  f", and {new_cats[1].name}"
                pronoun = Cat.default_pronouns[0] # They/them for muliple cats
            
            replace_dict[f"n_c:{i}"] = (names, pronoun)
        
        if len(self.patrol_apprentices) > 0:
            replace_dict["app1"] = (str(self.patrol_apprentices[0].name), choice(self.patrol_apprentices[0].pronouns))
        if len(self.patrol_apprentices) > 1:
            replace_dict["app2"] = (str(self.patrol_apprentices[1].name), choice(self.patrol_apprentices[1].pronouns))
        if len(self.patrol_apprentices) > 2:
            replace_dict["app3"] = (str(self.patrol_apprentices[2].name), choice(self.patrol_apprentices[2].pronouns))
        if len(self.patrol_apprentices) > 3:
            replace_dict["app4"] = (str(self.patrol_apprentices[3].name), choice(self.patrol_apprentices[3].pronouns))
        if len(self.patrol_apprentices) > 4:
            replace_dict["app5"] = (str(self.patrol_apprentices[4].name), choice(self.patrol_apprentices[4].pronouns))
        if len(self.patrol_apprentices) > 5:
            replace_dict["app6"] = (str(self.patrol_apprentices[5].name), choice(self.patrol_apprentices[5].pronouns))

        if stat_cat:
            replace_dict['s_c'] = (str(stat_cat.name),
                                choice(stat_cat.pronouns))

        text = process_text(text, replace_dict)
        text = adjust_prey_abbr(text)

        other_clan_name = self.other_clan.name
        s = 0
        for x in range(text.count('o_c_n')):
            if 'o_c_n' in text:
                for y in vowels:
                    if str(other_clan_name).startswith(y):
                        modify = text.split()
                        pos = 0
                        if 'o_c_n' in modify:
                            pos = modify.index('o_c_n')
                        if "o_c_n's" in modify:
                            pos = modify.index("o_c_n's")
                        if 'o_c_n.' in modify:
                            pos = modify.index('o_c_n.')
                        if modify[pos - 1] == 'a':
                            modify.remove('a')
                            modify.insert(pos - 1, 'an')
                        text = " ".join(modify)
                        break

        text = text.replace('o_c_n', str(other_clan_name) + 'Clan')

        clan_name = game.clan.name
        s = 0
        pos = 0
        for x in range(text.count('c_n')):
            if 'c_n' in text:
                for y in vowels:
                    if str(clan_name).startswith(y):
                        modify = text.split()
                        if 'c_n' in modify:
                            pos = modify.index('c_n')
                        if "c_n's" in modify:
                            pos = modify.index("c_n's")
                        if 'c_n.' in modify:
                            pos = modify.index('c_n.')
                        if modify[pos - 1] == 'a':
                            modify.remove('a')
                            modify.insert(pos - 1, 'an')
                        text = " ".join(modify)
                        break

        text = text.replace('c_n', str(game.clan.name) + 'Clan')

        # Prey lists for forest random prey patrols
        fst_tinyprey_singlular = ['shrew', 'robin', 'vole', 'dormouse', 'blackbird',
                                'wood mouse', 'lizard', 'tiny grass snake', 'finch', 'sparrow',
                                'small bird', 'young rat', 'young hedgehog', 'big beetle', 'woodrat',
                                'white-footed mouse', 'golden mouse', 'young squirrel', 'chipmunk', ]
        text = text.replace('f_tp_s', str(fst_tinyprey_singlular))

        fst_tinyprey_plural = ['mice', 'mice', 'mice', 'shrews', 'robins', 'voles', 'mice', 'blackbirds',
                            'mice', 'mice', 'lizards', 'small birds', 'small birds', 'sparrows',
                            'sleepy dormice', 'chipmunks', 'woodrats', ]
        text = text.replace('f_tp_p', str(fst_tinyprey_plural))

        fst_midprey_singlular = ['plump shrew', 'woodpecker', 'mole', 'fat dormouse', 'blackbird',
                                'field vole', 'big lizard', 'grass snake', 'half-grown rabbit', 'hedgehog',
                                'red squirrel', 'gray squirrel', 'rat', 'flying squirrel', 'kingfisher', ]
        text = text.replace('f_mp_s', str(fst_midprey_singlular))

        fst_midprey_plural = ['plump shrews', 'woodpeckers', 'moles', 'blackbirds',
                            'field voles', 'big lizards', 'grass snakes', 'half-grown rabbits', 'hedgehogs',
                            'red squirrels', 'gray squirrels', 'rats', ]
        text = text.replace('f_mp_p', str(fst_midprey_plural))

        text, senses, list_type = find_special_list_types(text)
        if list_type:
            sign_list = get_special_snippet_list(list_type, amount=randint(1, 3), sense_groups=senses)
            text = text.replace(list_type, str(sign_list))

        return text
    # ---------------------------------------------------------------------------- #
    #                                   Handlers                                   #
    # ---------------------------------------------------------------------------- #

    def handle_history(self, cat, condition=None, possible=False, scar=False, death=False):
        """
        this handles the scar and death history of the cat
        :param cat: the cat gaining the history
        :param condition: if the history is related to a condition, include its name here
        :param possible: if you want the history added to the possible scar/death then set this to True, defaults to False
        :param scar: if you want the scar history added set this to True, default is False
        :param death: if you want the death history added set this to True, default is False
        """
        if not self.patrol_event.history_text:
            print(
                f"WARNING: No history found for {self.patrol_event.patrol_id}, it may not need one but double check please!")
        if scar and "scar" in self.patrol_event.history_text:
            adjust_text = self.patrol_event.history_text['scar']
            adjust_text = adjust_text.replace("r_c", str(cat.name))
            adjust_text = adjust_text.replace("o_c_n", str(self.other_clan.name))
            if possible:
                History.add_possible_history(cat, condition=condition, scar_text=adjust_text)
            else:
                History.add_scar(cat, adjust_text)
        if death:
            if cat.status == 'leader':
                if "lead_death" in self.patrol_event.history_text:
                    adjust_text = self.patrol_event.history_text['lead_death']
                    adjust_text = adjust_text.replace("r_c", str(cat.name))
                    adjust_text = adjust_text.replace("o_c_n", str(self.other_clan.name))
                    if possible:
                        History.add_possible_history(cat, condition=condition, death_text=adjust_text)
                    else:
                        History.add_death(cat, adjust_text)
            else:
                if "reg_death" in self.patrol_event.history_text:
                    adjust_text = self.patrol_event.history_text['reg_death']
                    adjust_text = adjust_text.replace("r_c", str(cat.name))
                    adjust_text = adjust_text.replace("o_c_n", str(self.other_clan.name))
                    if possible:
                        History.add_possible_history(cat, condition=condition, death_text=adjust_text)
                    else:
                        History.add_death(cat, adjust_text)



# ---------------------------------------------------------------------------- #
#                               PATROL CLASS END                               #
# ---------------------------------------------------------------------------- #



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