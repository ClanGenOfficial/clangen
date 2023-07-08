#!/usr/bin/env python3
# -*- coding: ascii -*-
import random
from random import choice, randint, choices

import ujson
import pygame

from scripts.cat.history import History
from scripts.clan import HERBS, Clan
from scripts.utility import (
    event_text_adjust,
    change_clan_relations,
    change_clan_reputation,
    change_relationship_values, create_new_cat,
    create_outside_cat,
    get_personality_compatibility,
    check_relationship_value
)
from scripts.game_structure.game_essentials import game
from itertools import combinations
from scripts.cat.names import names
from scripts.cat.skills import SkillPath
from scripts.cat.cats import Cat, ILLNESSES, INJURIES, PERMANENT, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan_resources.freshkill import ADDITIONAL_PREY, PREY_REQUIREMENT, HUNTER_EXP_BONUS, HUNTER_BONUS, \
    FRESHKILL_ACTIVE
from os.path import exists as file_exists

# ---------------------------------------------------------------------------- #
#                              PATROL CLASS START                              #
# ---------------------------------------------------------------------------- #
"""
When adding new patrols, use \n to add a paragraph break in the text
"""


class Patrol():
    used_patrols = []
    EXPLICIT_PATROL_ART = None
    with open(f"resources/dicts/patrols/explicit_patrol_art.json", 'r') as read_file:
        EXPLICIT_PATROL_ART = ujson.loads(read_file.read())
    
    def __init__(self):
        
        self.patrol_event = None
        self.patrol_art = None
        
        self.patrol_done = False
        
        self.patrol_leader = None
        self.patrol_random_cat = None
        self.patrol_fail_stat_cat = None
        self.patrol_win_stat_cat = None
        self.patrol_cats = []
        self.patrol_apprentices = []
        self.other_clan = None
        self.intro_text = ""

        self.patrol_skills = []
        self.patrol_hidden_skills = []
        self.patrol_statuses = []
        self.patrol_traits = []
        self.patrol_total_experience = 0
        self.experience_levels = []

        # Keep track of outcome
        self.success = None
        self.antagonize = None
        self.outcome_text = ""
        self.results_text = []
    
    def setup_patrol(self, patrol_cats:list, patrol_type):
        # Add cats
        self.add_patrol_cats(patrol_cats, game.clan)
        final_patrols, final_romance_patrols = self.get_possible_patrols(
            str(game.clan.current_season).casefold(),
            str(game.clan.biome).casefold(),
            game.clan.all_clans,
            patrol_type,
            game.settings.get('disasters')
        )
        
        if final_patrols:
            normal_event_choice = choice(final_patrols) 
        else:
            print("ERROR: NO POSSIBLE NORMAL PATROLS FOUND for: ", self.patrol_statuses)
            raise RuntimeError
        if final_romance_patrols:
            romantic_event_choice = choice(final_romance_patrols) 
        else:
            romantic_event_choice = None
        
        if romantic_event_choice and Patrol.decide_if_romantic(romantic_event_choice, 
                                                               self.patrol_leader, 
                                                               self.patrol_random_cat, 
                                                               self.patrol_apprentices):
            print("did the romance")
            self.patrol_event = romantic_event_choice
        else:
            self.patrol_event = normal_event_choice
            
        self.get_stat_cats()
        Patrol.used_patrols.append(self.patrol_event.patrol_id)
        self.intro_text = self.patrol_event.intro_text
        self.get_patrol_art()
        
        return self.patrol_event.intro_text

    def proceed_patrol(self, path:str="proceed"):
        """Proceed the patrol to the next step. 
            path can be: "proceed", "antag", or "decline" """
        
        if path == "decline":
            if self.patrol_event:
                return self.patrol_event.decline_text
            else:
                return "Error - no event chosen"
        
        self.patrol_done = True
        self.calculate_success(antagonize=(path == "antag"))
        
        return self.outcome_text
        
    def add_patrol_cats(self, patrol_cats: list, clan: Clan) -> None:
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
            
            #Grab all the skills
            if cat.skills.primary:
                self.patrol_skills.append(cat.skills.primary)
            if cat.skills.secondary:
                self.patrol_skills.append(cat.skills.secondary)
            
            
            if cat.skills.hidden:
                self.patrol_hidden_skills.append(cat.skills.hidden.skill)
            
            self.experience_levels.append(cat.experience_level)
            
            self.patrol_statuses.append(cat.status)
            self.patrol_traits.append(cat.personality.trait)
            self.patrol_total_experience += cat.experience


            if cat.status == 'apprentice' or cat.status == 'medicine cat apprentice':
                self.patrol_apprentices.append(cat)
            
            game.patrolled.append(cat.ID)


        #PATROL LEADER AND RANDOM CAT CAN NOT CHANGE AFTER SET-UP

        # DETERMINE PATROL LEADER
        # sets medcat as leader if they're in the patrol
        if "medicine cat" in self.patrol_statuses:
            med_index = self.patrol_statuses.index("medicine cat")
            self.patrol_leader = self.patrol_cats[med_index]
        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warrior from being treated as medicine cats in medicine cat patrols.
        elif "medicine cat apprentice" in self.patrol_statuses:
            med_index = self.patrol_statuses.index("medicine cat apprentice")
            self.patrol_leader = self.patrol_cats[med_index]
            # then we just make sure that this app will also be app1
            self.patrol_apprentices.remove(self.patrol_leader)
            self.patrol_apprentices = [self.patrol_leader] + self.patrol_apprentices
        # sets leader as patrol leader
        elif clan.leader and clan.leader in self.patrol_cats:
            self.patrol_leader = clan.leader
        elif clan.deputy and clan.deputy in self.patrol_cats:
            self.patrol_leader = clan.deputy
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
            possible_random_cats = [i for i in patrol_cats if i != self.patrol_leader]
            self.patrol_random_cat = choice(possible_random_cats)
        else:
            possible_random_cats = [i for i in patrol_cats]
            self.patrol_random_cat = choice(possible_random_cats)

    def get_possible_patrols(self, current_season, biome, all_clans, patrol_type,
                             game_setting_disaster=game.settings['disasters']):
        # ---------------------------------------------------------------------------- #
        #                                LOAD RESOURCES                                #
        # ---------------------------------------------------------------------------- #
        biome = biome.lower()
        season = current_season.lower()
        biome_dir = f"{biome}/"
        leaf = f"{season}"
        self.update_resources(biome_dir, leaf)

        possible_patrols = []
        # this next one is needed for Classic specifically
        patrol_type = "med" if ['medicine cat', 'medicine cat apprentice'] in self.patrol_statuses else patrol_type
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

        final_patrols, final_romance_patrols = self.filter_patrols(possible_patrols, biome, patrol_size, current_season,
                                                                   patrol_type)

        return final_patrols, final_romance_patrols

    def check_constraints(self, patrol):
        if "relationship" in patrol.constraints:
            if not self.filter_relationship(patrol):
                return False
  
        if "skill" in patrol.constraints:
            if not self.patrol_leader.skills.check_skill_requirement_list(patrol.constraints["skill"]):
                return False
        
        if "trait" in patrol.constraints:
            if self.patrol_leader.personality.trait not in patrol.constraints["trait"]:
                return False
            
        return True

    def filter_relationship(self, patrol):
        """
        Filter the incoming patrol list according to the relationship constraints, if there are constraints.

        """

        # filtering - relationship status
        # check if all are siblings
        if "siblings" in patrol.constraints["relationship"]:
            test_cat = self.patrol_cats[0]
            testing_cats = [cat for cat in self.patrol_cats if cat.ID != test_cat.ID]

            siblings = [test_cat.is_sibling(inter_cat) for inter_cat in testing_cats]
            if not all(siblings):
                return False
            
        # check if the cats are mates
        if "mates" in patrol.constraints["relationship"]:
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
        if "parent/child" in patrol.constraints["relationship"]:
            # it should be exactly two cats for a "parent/child" patrol
            if len(self.patrol_cats) != 2:
                return False
            # when there are two cats in the patrol, p_l and r_c are different cats per default
            if not self.patrol_leader.is_parent(self.patrol_random_cat):
                return False

        # check if the cats are in a child/parent relationship
        if "child/parent" in patrol.constraints["relationship"]:
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
            tags = [constraint for constraint in patrol.constraints["relationship"] if v_type in constraint]

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

    def _allowed_stat_cat(self, kitty):
        """Helper functions that deals with filtering
        for conflicts with r_c and s_c"""

        if len(self.patrol_cats) == 1:
            # When you have a one cat patrol, no
            # no filtering for random_cat and patrol_leader
            # random cat and patrol leader will be the 
            # same, and stat cat can also be the same cat
            return True

        if len(self.patrol_cats) == 2:
            # For a 2 cat patrol, the only restriction is
            # that s_c can't be r_c. s_c only allowed to be the 
            # same cat as the p_l. This
            # can be overridden by the "rc_has_stat"
            # tag, which forces s_c to be r_c instead. 
            if "rc_has_stat" in self.patrol_event.tags:
                return True if kitty == self.patrol_random_cat else False

            return True if kitty == self.patrol_leader else False

        # normal, 3+ cat p_l and r_c 
        # filtering, where stat cat must be
        # different from s_c and random cat
        new_possible_cats = []
        if "rc_has_stat" in self.patrol_event.tags:
            # If "rc_has_stat" is provided, the s_c must be r_c. If they
            # are not, return False 
            return True if kitty == self.patrol_random_cat else False

        if "pl_has_stat" in self.patrol_event.tags:
            # if "pl_has_stat" is provided, the s_c must be p_l
            return True if kitty == self.patrol_leader else False

        # Otherwise, can't be random cat or patrol_leader
        if kitty == self.patrol_random_cat:
            return False
        if kitty == self.patrol_leader:
            return False

        return True


    def get_stat_cats(self):
        """sets patrol.patrol_fail_stat_cat and patrol.patrol_win_stat_cat"""
        
        possible_stat_cats = []
        for kitty in self.patrol_cats:
            if "app_stat" in self.patrol_event.tags \
                    and kitty.status not in ['apprentice', "medicine cat apprentice"]:
                continue
            
            if "adult_stat" in self.patrol_event.tags and kitty.status in ['apprentice', "medicine cat apprentice"]:
                continue
            
            if "app1_has_stat" in self.patrol_event.tags and self.patrol_apprentices and kitty != self.patrol_apprentices[0]:
                continue
            
            if not self._allowed_stat_cat(kitty):
                continue
            
            possible_stat_cats.append(kitty)

        print('POSSIBLE STAT CATS',  [str(i.name) for i in possible_stat_cats])

        #WIN STAT CAT
        win_stat_cats = []
        if self.patrol_event.win_skills:
            for kitty in possible_stat_cats:
                if kitty.skills.check_skill_requirement_list(self.patrol_event.win_skills):
                    win_stat_cats.append(kitty)
                        
        if self.patrol_event.win_trait:
            for kitty in possible_stat_cats:
                if kitty.personality.trait in self.patrol_event.win_trait:
                    win_stat_cats.append(kitty)
        
        #FAIL STAT CAT
        fail_stat_cats = []    
        if self.patrol_event.fail_skills:
            for kitty in possible_stat_cats:
                if kitty.skills.check_skill_requirement_list(self.patrol_event.fail_skills):
                    fail_stat_cats.append(kitty)
    
        if self.patrol_event.fail_trait:
            for kitty in possible_stat_cats:
                if kitty.personality.trait in self.patrol_event.fail_trait:
                    fail_stat_cats.append(kitty)
                
                        
        if not (win_stat_cats or fail_stat_cats):
            print("no cats with win/fail attributes")
            return
        
        print('PATROL WIN STAT', win_stat_cats)
        print('PATROL FAIL STAT', fail_stat_cats)
        
        # Check if patrol_stat cat is 
        if fail_stat_cats:
            self.patrol_fail_stat_cat = choice(fail_stat_cats)
        
        if win_stat_cats:
            self.patrol_win_stat_cat = choice(win_stat_cats)
        
        print('has stat cats', 
              "FAIL",
              str(self.patrol_fail_stat_cat.name) if self.patrol_fail_stat_cat else None,
              "WIN",
              str(self.patrol_win_stat_cat.name) if self.patrol_win_stat_cat else None)
        
        return
        
    @staticmethod
    def decide_if_romantic(romantic_event, patrol_leader, random_cat, patrol_apprentices:list) -> bool:
         # if no romance was available or the patrol lead and random cat aren't potential mates then use the normal event

        if not romantic_event:
            print("No romantic event")
            return False
        
        if "rel_two_apps" in romantic_event.tags:
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

    def filter_patrols(self, possible_patrols, biome, patrol_size, current_season, patrol_type):
        filtered_patrols = []
        romantic_patrols = []
        self.filter_count = 0

        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        for patrol in possible_patrols:
            if not self.check_constraints(patrol):
                continue
            if patrol.patrol_id in self.used_patrols:
                continue

            if patrol_size < patrol.min_cats:
                continue
            if patrol_size > patrol.max_cats:
                continue
            if patrol.biome not in [biome, "Any"]:
                continue
            if patrol.season not in [current_season, "Any"]:
                continue

            #  correct button check
            if patrol_type == "general":
                if not set(patrol.tags).intersection({"hunting", "border", "training"}):
                    # This make sure general only gets hunting, border, or training patrols.
                    continue
            else:
                if 'hunting' not in patrol.tags and patrol_type == 'hunting':
                    continue
                elif 'border' not in patrol.tags and patrol_type == 'border':
                    continue
                elif 'training' not in patrol.tags and patrol_type == 'training':
                    continue
                elif 'herb_gathering' not in patrol.tags and patrol_type == 'med':
                    continue

            if patrol_size < patrol.min_cats:
                continue
            if patrol_size > patrol.max_cats:
                continue

            # makes sure that an apprentice is present if the apprentice tag is
            if "apprentice" in patrol.tags:
                if patrol_type != 'med':
                    if "apprentice" not in self.patrol_statuses:
                        continue
                else:
                    if "medicine cat apprentice" not in self.patrol_statuses:
                        continue
                    if "warrior_app" in patrol.tags and "apprentice" not in self.patrol_statuses:
                        continue

            # makes sure that the deputy is present if the deputy tag is
            if "deputy" in patrol.tags:
                if "deputy" not in self.patrol_statuses:
                    continue
                else:
                    st_index = self.patrol_statuses.index("deputy")
                    self.patrol_random_cat = self.patrol_cats[st_index]

            # makes sure the leader is present when the leader tag is
            if "leader" in patrol.tags:
                if "leader" not in self.patrol_statuses:
                    continue

            # makes sure at least one warrior is present
            if "warrior" in patrol.tags:
                warrior = ["warrior", "deputy", "leader"]
                if not any(status in self.patrol_statuses for status in warrior):
                    continue

            # makes sure there's a med in a med patrol
            if "med_cat" in patrol.tags:
                if "medicine cat" not in self.patrol_statuses:
                    continue

            # makes sure no apps are present if they're not supposed to be
            # mostly for romance patrols between warriors/dumb stuff that they wouldn't involve apprentices in
            if "no_app" in patrol.tags:
                if "apprentice" in self.patrol_statuses or "medicine cat apprentice" in self.patrol_statuses:
                    continue

            # makes sure no warriors/warrior apps are present. for med patrols
            if "med_only" in patrol.tags:
                non_med = ["leader", "deputy", "warrior", "apprentice"]
                if any(status in self.patrol_statuses for status in non_med):
                    continue

            # makes sure the leader isn't present if they're not supposed to be
            if "no_leader" in patrol.tags:
                if "leader" in self.patrol_statuses:
                    continue

            # cruel season tag check
            if "cruel_season" in patrol.tags:
                if game.clan.game_mode != 'cruel_season':
                    continue

            # one apprentice check
            if "one_apprentice" in patrol.tags:
                if len(self.patrol_apprentices) < 1 or len(self.patrol_apprentices) > 1:
                    continue

            # two apprentices check
            if "two_apprentices" in patrol.tags:
                if len(self.patrol_apprentices) < 2 or len(self.patrol_apprentices) > 2:
                    continue

            # three apprentices check
            if "three_apprentices" in patrol.tags:
                if len(self.patrol_apprentices) < 3 or len(self.patrol_apprentices) > 3:
                    continue

            # four apprentices check
            if "four_apprentices" in patrol.tags:
                if len(self.patrol_apprentices) < 4 or len(self.patrol_apprentices) > 4:
                    continue

            # five apprentices check
            if "five_apprentices" in patrol.tags:
                if len(self.patrol_apprentices) < 5 or len(self.patrol_apprentices) > 5:
                    continue

            # six apprentices check
            if "six_apprentices" in patrol.tags:
                if len(self.patrol_apprentices) < 6 or len(self.patrol_apprentices) > 6:
                    continue

            if "romantic" in patrol.tags:
                romantic_patrols.append(patrol)
            else:
                filtered_patrols.append(patrol)

        if patrol_type == 'hunting':
            filtered_patrols = self.balance_hunting(filtered_patrols)

        if not filtered_patrols:
            if self.filter_count == 1:
                # error message will print from patrol_screens.py once this is returned
                return filtered_patrols, romantic_patrols
            self.filter_count += 1
            self.used_patrols.clear()
            print('used patrols cleared', self.used_patrols)
            filtered_patrols, romantic_patrols = self.repeat_filter(possible_patrols, biome, patrol_size,
                                                                    current_season, patrol_type)
        else:
            # reset this when we succeed in finding a patrol
            self.filter_count = 0
        return filtered_patrols, romantic_patrols

    def repeat_filter(self, possible_patrols, biome, patrol_size, current_season, patrol_type):
        print('repeating filter')
        filtered_patrols, romantic_patrols = self.filter_patrols(possible_patrols, biome, patrol_size, current_season,
                                                                 patrol_type)
        return filtered_patrols, romantic_patrols

    def get_patrol_art(self):
        """
        grabs art for the patrol based on the patrol_id
        -first checks for image file with exact patrol_id
        -then checks for image file with the patrol_id minus any numbers
        -then checks for image file with the patrol_id minus any numbers and with 'gen' replacing biome indicator
        -if none of those are available, then uses placeholder patrol type image
        if you are adding art and the art has gore or blood, add its exact patrol id to the explicit_patrol_art.json
        """
        path = "resources/images/patrol_art/"

        # if gore isn't allowed then placeholder is shown instead
        gore_allowed = game.settings["gore"]
        placeholder_needed = False
        if not gore_allowed and self.patrol_event.patrol_id in Patrol.EXPLICIT_PATROL_ART:
            placeholder_needed = True

        image_name = self.patrol_event.patrol_id

        if not placeholder_needed:
        
            # looking for exact patrol ID
            if file_exists(f"{path}{image_name}.png"):
                self.patrol_art = pygame.image.load(
                            f"{path}{image_name}.png").convert_alpha()
                return

            # looking for patrol ID without numbers
            image_name = ''.join([i for i in image_name if not i.isdigit()])
            if file_exists(f"{path}{image_name}.png"):
                self.patrol_art = pygame.image.load(
                            f"{path}{image_name}.png").convert_alpha()
                return

            # looking for patrol ID with biome indicator replaced with 'gen'
            # if that isn't found then patrol type placeholder will be used
        
            image_name = ''.join([i for i in image_name if not i.isdigit()])
            image_name = image_name.replace("fst_", "gen_")
            image_name = image_name.replace("mtn_", "gen_")
            image_name = image_name.replace("pln_", "gen_")
            image_name = image_name.replace("bch_", "gen_")
            if file_exists(f"{path}{image_name}.png"):
                self.patrol_art = pygame.image.load(
                            f"{path}{image_name}.png").convert_alpha()
                return
    
        image_name = 'train'
        if self.patrol_event.patrol_id.find('med') != -1:
            image_name = 'med'
        elif self.patrol_event.patrol_id.find('hunt') != -1:
            image_name = 'hunt'
        elif self.patrol_event.patrol_id.find('train') != -1:
            image_name = 'train'
        elif self.patrol_event.patrol_id.find('bord') != -1:
            image_name = 'bord'
        try:
            self.patrol_art = pygame.image.load(
                        f"resources/images/patrol_art/{image_name}_general_intro.png").convert_alpha()
        except Exception:
            self.patrol_art = pygame.Surface((10, 10))
            print('ERROR: could not display patrol image')

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

    def generate_patrol_events(self, patrol_dict):
        all_patrol_events = []
        for patrol in patrol_dict:
            patrol_event = PatrolEvent(
                patrol_id=patrol["patrol_id"],
                biome=patrol["biome"],
                season=patrol["season"],
                tags=patrol["tags"],
                intro_text=patrol["intro_text"],
                success_text=patrol["success_text"],
                fail_text=patrol["fail_text"],
                decline_text=patrol["decline_text"],
                chance_of_success=patrol["chance_of_success"],
                exp=patrol["exp"],
                min_cats=patrol["min_cats"] if "min_cats" in patrol else 1,
                max_cats=patrol["max_cats"] if "max_cats" in patrol else 6,
                win_skills=patrol["win_skills"] if "win_skills" in patrol else [],
                win_trait=patrol["win_trait"] if "win_trait" in patrol else [],
                fail_skills=patrol["fail_skills"] if "fail_skills" in patrol else [],
                fail_trait=patrol["fail_trait"] if "fail_trait" in patrol else [],
                antagonize_text=patrol["antagonize_text"] if "antagonize_text" in patrol else None,
                antagonize_fail_text=patrol["antagonize_fail_text"] if "antagonize_fail_text" in patrol else None,
                history_text=patrol["history_text"] if "history_text" in patrol else [],
                constraints=patrol["constraints"] if "constraints" in patrol else {},
                other_clan=patrol["other_clan"] if "other_clan" in patrol else None
            )

            all_patrol_events.append(patrol_event)

        return all_patrol_events

    def calculate_success(self, antagonize=False):
        if self.patrol_event is None:
            return

        print("patrol tags: ", self.patrol_event.tags)

        antagonize = antagonize
        success_text = self.patrol_event.success_text
        fail_text = self.patrol_event.fail_text

        gm_modifier = game.config["patrol_generation"][f"{game.clan.game_mode}_difficulty_modifier"]

        # if patrol contains cats with autowin skill, chance of success is high. otherwise it will calculate the
        # chance by adding the patrol event's chance of success plus the patrol's total exp
        success_adjust = (1 + 0.10 * len(self.patrol_cats)) * self.patrol_total_experience / (
                len(self.patrol_cats) * gm_modifier * 2)
        success_chance = self.patrol_event.chance_of_success + int(success_adjust)

        # Auto-wins based on EXP are sorta lame. Often makes it impossible for large patrols with experienced cats to fail patrols at all. 
        # EXP alone can only bring success chance up to 85. However, skills/traits can bring it up above that. 
        success_chance = min(success_chance, 90)

        print('starting chance:', self.patrol_event.chance_of_success, "| EX_updated chance:", success_chance)
        skill_updates = ""
        
        
        # Skill and trait stuff
        for kitty in self.patrol_cats:
            hits = kitty.skills.check_skill_requirement_list(self.patrol_event.win_skills)
            success_chance += hits * game.config["patrol_generation"]["win_stat_cat_modifier"] 
            
            hits = kitty.skills.check_skill_requirement_list(self.patrol_event.fail_skills)
            success_chance -= hits * game.config["patrol_generation"]["fail_stat_cat_modifier"]
            
    
            if self.patrol_event.win_trait and kitty.personality.trait in self.patrol_event.win_trait:
                success_chance += game.config["patrol_generation"]["win_stat_cat_modifier"]
                
            if self.patrol_event.fail_trait and kitty.personality.trait in self.patrol_event.fail_trait:
                success_chance += game.config["patrol_generation"]["fail_stat_cat_modifier"]

            skill_updates += f"{kitty.name} updated chance to {success_chance} | "
        
        if success_chance >= 120:
            success_chance = 115
            skill_updates += "success chance over 120, updated to 115"
        
        print(skill_updates)
        
        c = int(random.random() * 120)
        outcome = int(random.getrandbits(4))
        print('ending chance', success_chance, 'vs.', c)

        # denotes if they get the common "basic" outcome or the rare "basic" outcome
        rare = False
        common = False
        if outcome >= 11:
            rare = True
            print('TRY FOR RARE OUTCOME')
        else:
            common = True
            print("TRY FOR COMMON OUTCOME")

        # ---------------------------------------------------------------------------- #
        #                                   SUCCESS                                    #
        # ---------------------------------------------------------------------------- #

        if c < success_chance:
            self.success = True
            self.patrol_fail_stat_cat = None

            # default is outcome 0
            outcome = "unscathed_common"
            if self.patrol_win_stat_cat:
                if self.patrol_event.win_trait:
                    if self.patrol_win_stat_cat.personality.trait in self.patrol_event.win_trait and success_text.get("stat_trait"):
                        outcome = "stat_trait"
                    else:
                        outcome = "stat_skill"
            else:
                if rare and success_text.get("unscathed_rare"):
                    outcome = "unscathed_rare"

            if not antagonize:
                self.add_new_cats(outcome, self.success)
            if self.patrol_event.tags is not None:
                if "other_clan" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_clan_relations(difference=int(-2), antagonize=True, outcome=outcome)
                    else:
                        self.handle_clan_relations(difference=int(1), antagonize=False, outcome=outcome)
                if any("new_cat" in ptrltag for ptrltag in self.patrol_event.tags):
                    if antagonize:
                        self.handle_reputation(-20)
                    else:
                        self.handle_reputation(10)

            self.handle_mentor_app_pairing()
            self.handle_relationships()

            if game.clan.game_mode != 'classic' and not antagonize:
                self.handle_herbs(outcome)

            try:
                self.outcome_text = self.patrol_event.success_text[outcome]
            except KeyError:
                self.outcome_text = self.patrol_event.success_text["unscathed_common"]

            if antagonize:
                self.outcome_text = self.patrol_event.antagonize_text

        # ---------------------------------------------------------------------------- #
        #                                   FAILURE                                    #
        # ---------------------------------------------------------------------------- #
        else:
            self.success = False
            self.patrol_win_stat_cat = None

            # unscathed or not
            u = int(random.getrandbits(4))
            if u >= 10:
                unscathed = True
                print("Unscathed true")
            else:
                unscathed = False
                print("Unscathed false")

            outcome = "unscathed_common"  # unscathed and common outcome, the default failure

            # first we check for a fail stat outcome
            if self.patrol_fail_stat_cat is not None:
                print("Fail stat cat")
                # safe, just failed
                if unscathed and fail_text.get("unscathed_stat"):
                    outcome = "unscathed_stat"
                # injured
                elif not unscathed and common and fail_text.get("stat_injury"):
                    outcome = "stat_injury"
                # dead
                elif not unscathed and rare and fail_text.get("stat_death"):
                    outcome = "stat_death"

            # if no fail stat cat or outcomes, then onto the injured/dead outcomes
            if not unscathed:
                # injured
                if common and fail_text.get("injury"):
                    outcome = "injury"
                # if the leader is present and a cat /would/ die, then the leader sacrifices themselves
                elif rare and fail_text.get("leader_death") and self.patrol_leader == game.clan.leader:
                    outcome = "leader_death"
                # dead
                elif rare and fail_text.get("death"):
                    outcome = "death"

            # if /still/ no outcome is picked then double check that an outcome 0 is available,
            # if it isn't, then try to injure and then kill the cat
            if not fail_text.get("unscathed_common"):
                # attempt death outcome
                if fail_text.get("death"):
                    outcome = "death"
                # attempt injure outcome
                elif fail_text.get("injury"):
                    outcome = "injury"

            if not antagonize or antagonize and "antag_death" in self.patrol_event.tags:
                if "death" in outcome:
                    self.handle_deaths_and_gone(outcome)
                elif outcome == "injury" or outcome == "stat_injury":
                    if game.clan.game_mode == 'classic':
                        self.handle_scars(outcome)
                    else:
                        self.handle_conditions(outcome)
            if not antagonize and "meeting" in self.patrol_event.tags:
                self.add_new_cats(outcome, self.success)
            if self.patrol_event.tags is not None:
                if "other_clan" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_clan_relations(difference=int(-1), antagonize=True, outcome=outcome)
                    else:
                        self.handle_clan_relations(difference=int(-1), antagonize=False, outcome=outcome)
                elif any("new_cat" in ptrltag for ptrltag in self.patrol_event.tags):
                    if antagonize:
                        self.handle_reputation(-10)
                    else:
                        self.handle_reputation(0)
            self.handle_mentor_app_pairing()
            self.handle_relationships()
            
            if antagonize:
                self.outcome_text = self.patrol_event.antagonize_fail_text
            else:
                self.outcome_text = self.patrol_event.fail_text[outcome]

        print("PATROL ID:", self.patrol_event.patrol_id)
        self.handle_exp_gain(self.success)
        if not antagonize and game.clan.game_mode != "classic":
            self.handle_prey(outcome)

        print('Patrol Succeeded?', self.success, ', Outcome Index:', outcome)

    def results(self):
        text = "<br>".join(self.results_text)
        self.results_text.clear()
        return text

    def add_new_cats(self, outcome, success):
        """
        handles new_cat tags and passing info to the create_new_cats function
        :param outcome: the outcome index
        :param success: success bool
        """
        tags = self.patrol_event.tags

        if self.success:
            # converting outcomes
            outcomes = {
                "unscathed_common": 0,
                "unscathed_rare": 1,
                "stat_skill": 2,
                "stat_trait": 3,
            }
            outcome_number = outcomes[outcome]
            outcome = outcome_number

            # check for ignore outcome tag
            if f"no_new_cat{outcome}" in tags:
                return

        # find the new cat tag and split to get attributes - else return if no tag found
        attribute_list = []
        for tag in tags:
            # print(tag)
            if "new_cat" in tag and "no_new_cat" not in tag and "new_cat_injury" not in tag:
                attribute_list = tag.split("_")
                print('found tag, attributes:', attribute_list)
                break
        if not attribute_list:
            return

        print('new cat creation started')

        # setting the defaults
        new_name = choice([True, False])
        kit_backstory = None
        if "_tom" in tags:
            gender = 'male'
        elif "_female" in tags:
            gender = 'female'
        else:
            gender = None
        kit = False
        litter = False
        status = None
        age = None
        kit_age = 0
        thought = 'Is looking around the camp with wonder'
        alive = True
        outside = False

        # figure out what type of cat they are and set default backstories.json - this can be overwritten if need be
        loner = False
        kittypet = False
        other_clan = None

        if "kittypet" in attribute_list:
            cat_type = "kittypet"
        elif "loner" in attribute_list:
            cat_type = "loner"
        elif "clancat" in attribute_list:
            cat_type = "former_clancat"
        elif "rogue" in attribute_list:
            cat_type = "rogue"
        else:
            cat_type = choice(['kittypet', 'loner', 'former_clancat'])

        if cat_type == 'kittypet':
            kittypet = True
            new_name = choice([True, False])
            chosen_backstory = BACKSTORIES["backstory_categories"]["kittypet_backstories"]
            if "medcat" in attribute_list:
                status = 'medicine cat'
                chosen_backstory = ["wandering_healer1", "wandering_healer2"]
            if not success:
                outsider = create_outside_cat(Cat, "kittypet", backstory=choice(chosen_backstory))
                self.results_text.append(f"The Clan has met {outsider}.")
                return
        elif cat_type == 'loner':
            loner = True
            new_name = choice([True, False])
            chosen_backstory = BACKSTORIES["backstory_categories"]["loner_backstories"]
            if "medcat" in attribute_list:
                status = 'medicine cat'
                chosen_backstory = ["wandering_healer1", "wandering_healer2"]
            if not success:
                outsider = create_outside_cat(Cat, "loner", backstory=choice(chosen_backstory))
                self.results_text.append(f"The Clan has met {outsider}.")
                return
        elif cat_type == 'rogue':
            loner = True
            new_name = choice([True, False])
            chosen_backstory = BACKSTORIES["backstory_categories"]["rogue_backstories"]
            if "medcat" in attribute_list:
                status = 'medicine cat'
                chosen_backstory = ["wandering_healer1", "wandering_healer2"]
            if not success:
                outsider = create_outside_cat(Cat, "rogue", backstory=choice(chosen_backstory))
                self.results_text.append(f"The Clan has met {outsider}.")
                return
        elif cat_type == 'clancat':
            other_clan = self.other_clan
            new_name = False
            chosen_backstory = BACKSTORIES["backstory_categories"]["former_clancat_backstories"]
            if "medcat" in attribute_list:
                status = 'medicine cat'
                chosen_backstory = ["medicine_cat", "disgraced1"]
            if not success:
                outsider = create_outside_cat(Cat, "former Clancat", backstory=choice(chosen_backstory))
                self.results_text.append(f"The Clan has met {outsider}.")
                return
        else:
            other_clan = self.other_clan
            chosen_backstory = BACKSTORIES["backstory_categories"]["former_clancat_backstories"]
            # failsafe in case self.other_clan is None for some reason
            if "medcat" in attribute_list:
                status = 'medicine cat'
                chosen_backstory = ["medicine_cat", "disgraced1"]
            if not other_clan:
                loner = True
                new_name = choice([True, False])
                chosen_backstory = BACKSTORIES["backstory_categories"]["rogue_backstories"]
                if "medcat" in attribute_list:
                    chosen_backstory = ["medicine_cat", "disgraced1"]
                if not success:
                    outsider = create_outside_cat(Cat, loner, backstory=choice(chosen_backstory))
                    self.results_text.append(f"The Clan has met {outsider}.")
                    return
            else:
                if not success:
                    outsider = create_outside_cat(Cat, "former Clancat", backstory=choice(chosen_backstory))
                    self.results_text.append(f"The Clan has met {outsider}.")
                    return

        # handing out ranks
        if "kitten" in attribute_list:
            kit = True
            age = randint(1, 5)
            status = "kitten"
            chosen_kit_backstory = ['abandoned2', 'abandoned1', 'abandoned3']
        elif "apprentice" in attribute_list:
            status = "apprentice"
        elif "warrior" in attribute_list:
            status = "warrior"
        elif "medcat" in attribute_list:
            status = 'medicine cat'
        elif "elder" in attribute_list:
            status = "elder"

        # handing out ages
        if "newborn" in attribute_list:
            age = 0
            status = 'newborn'
        elif "adolescent" in attribute_list:
            age = randint(6, 11)
        elif "youngadult" in attribute_list:
            age = randint(12, 47)
        elif "adult" in attribute_list:
            age = randint(48, 95)
        elif "senioradult" in attribute_list:
            age = randint(96, 119)
        elif "elder" in attribute_list:
            age = randint(120, 300)
        elif not status:
            age = randint(12, 115)

        # hand out genders
        if "male" in attribute_list:
            gender = 'male'
        elif 'female' in attribute_list:
            gender = 'female'

        # hand out death and outside
        if "dead" in attribute_list:
            if loner:
                status = choice(['rogue', 'loner'])
            elif kittypet:
                status = 'kittypet'
            elif other_clan:
                status = 'former Clancat'
            alive = False
            thought = "Is glad that their kits are safe"

        if "outside" in attribute_list:
            outside = True

        # give a litter if the outcome calls for it
        kit_thought = 'Is looking around the camp with wonder'
        if f"litter{outcome}" in attribute_list:
            print('litter outcome checking')
            if not game.settings["same sex birth"]:
                gender = 'female'
            litter = True
            age = randint(23, 100)
            # make sure kittens get correct backstory
            if "dead" in attribute_list:
                print('parent is dead')
                chosen_kit_backstory = ['orphaned1', 'orphaned2']
            else:
                print('parent is alive')
                chosen_kit_backstory = ['outsider_roots2', 'outsider_roots2']
            # make sure kittens get right age
            if "litternewborn" in attribute_list:
                print('litter is newborn')
                kit_age = 0
                kit_thought = "Mewls quietly for milk"
            else:
                print('litter is not newborn')
                kit_age = randint(1, 5)

            # giving specified backstories.json if any were specified
            possible_backstories = []
            for backstory in BACKSTORIES["backstories"]:
                if f'{backstory}{outcome}' in attribute_list:
                    possible_backstories.append(backstory)

            if possible_backstories:
                kit_backstory = possible_backstories
            else:
                kit_backstory = chosen_kit_backstory

            backstory = chosen_backstory
        else:
            # giving specified backstories.json if any were specified
            possible_backstories = []
            for backstory in BACKSTORIES["backstories"]:
                if backstory in attribute_list:
                    possible_backstories.append(backstory)

            if possible_backstories:
                backstory = possible_backstories
            elif kit:
                backstory = ['abandoned2', 'abandoned1', 'abandoned3']
                # if none of these tags are present, then it uses the chosen_backstory from before
            else:
                backstory = chosen_backstory

        # we create a single cat
        created_cats = create_new_cat(Cat,
                                      Relationship,
                                      new_name=new_name,
                                      loner=loner,
                                      kittypet=kittypet,
                                      kit=kit,
                                      litter=False,
                                      other_clan=other_clan,
                                      backstory=backstory,
                                      status=status,
                                      age=age,
                                      gender=gender,
                                      thought=thought,
                                      alive=alive,
                                      outside=outside
                                      )
        if not alive:
            self.results_text.append(f"{created_cats[0].name}'s ghost now wanders.")
            game.clan.add_to_unknown(created_cats[0])

        # now we hurt the kitty
        if "new_cat_injury" in tags and game.clan.game_mode != 'classic':
            new_cat = created_cats[0]
            possible_conditions = []
            condition_lists = {
                "nc_blunt_force_injury": ["broken bone", "broken back", "head damage", "broken jaw"],
                "nc_sickness": ["greencough", "redcough", "whitecough", "yellowcough"],
                "nc_battle_injury": ["claw-wound", "mangled leg", "mangled tail", "torn pelt", "bite-wound"],
                "nc_hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
                "nc_cold_injury": ["shivering", "frostbite"]
            }
            for tag in self.patrol_event.tags:
                tag = tag.replace("nc_", "")
                if tag in INJURIES:
                    possible_conditions.append(tag)
                    continue
                elif tag in ILLNESSES:
                    possible_conditions.append(tag)
                    continue
                elif tag in PERMANENT:
                    possible_conditions.append(tag)
                    continue

            for y in condition_lists:
                if y in self.patrol_event.tags:
                    possible_conditions.extend(condition_lists[y])
                    continue
            if len(possible_conditions) > 0:
                new_condition = choice(possible_conditions)
                if new_condition in INJURIES:
                    new_cat.get_injured(new_condition)
                elif new_condition in ILLNESSES:
                    new_cat.get_ill(new_condition)
                elif new_condition in PERMANENT:
                    new_cat.get_permanent_condition(new_condition)

        # we create any needed litters
        if litter:
            created_cats.extend(create_new_cat(Cat,
                                               Relationship,
                                               new_name=new_name,
                                               loner=loner,
                                               kittypet=kittypet,
                                               kit=False,  # this is for singular kits, litters need this to be false
                                               litter=True,
                                               other_clan=other_clan,
                                               backstory=kit_backstory,
                                               status=None,
                                               age=kit_age,
                                               gender=None,
                                               thought=kit_thought,
                                               alive=True,
                                               outside=False
                                               ))
            # giving the mother the necessary condition
            if game.clan.game_mode != 'classic' and kit_age <= 2 and not created_cats[0].dead:
                if not game.settings["same sex birth"]:
                    if created_cats[0].gender == 'female':
                        created_cats[0].get_injured("recovering from birth")
                else:
                    created_cats[0].get_injured("recovering from birth")

            # make sure the kits are given to the parent and are given relationships with each other
            if len(created_cats) > 1:
                for new_cat in created_cats[1:]:
                    # adding parent and siblings
                    new_cat.parent1 = created_cats[0].ID

                    # creating relationships
                    new_cat.create_one_relationship(created_cats[0])
                    kit_to_parent = game.config["new_cat"]["parent_buff"]["kit_to_parent"]
                    change_relationship_values(
                        cats_to=[created_cats[0].ID],
                        cats_from=[new_cat],
                        romantic_love=kit_to_parent["romantic"],
                        platonic_like=kit_to_parent["platonic"],
                        dislike=kit_to_parent["dislike"],
                        admiration=kit_to_parent["admiration"],
                        comfortable=kit_to_parent["comfortable"],
                        jealousy=kit_to_parent["jealousy"],
                        trust=kit_to_parent["trust"]
                    )

                    # give relationships for siblings
                    for sibling in new_cat.get_siblings():
                        sibling = Cat.fetch_cat(sibling)
                        sibling.create_one_relationship(new_cat)
                        new_cat.create_one_relationship(sibling)
                        cat1_to_cat2 = game.config["new_cat"]["sib_buff"]["cat1_to_cat2"]
                        cat2_to_cat1 = game.config["new_cat"]["sib_buff"]["cat2_to_cat1"]
                        change_relationship_values(
                            cats_to=[sibling.ID],
                            cats_from=[new_cat],
                            romantic_love=cat1_to_cat2["romantic"],
                            platonic_like=cat1_to_cat2["platonic"],
                            dislike=cat1_to_cat2["dislike"],
                            admiration=cat1_to_cat2["admiration"],
                            comfortable=cat1_to_cat2["comfortable"],
                            jealousy=cat1_to_cat2["jealousy"],
                            trust=cat1_to_cat2["trust"]
                        )
                        change_relationship_values(
                            cats_to=[new_cat.ID],
                            cats_from=[sibling],
                            romantic_love=cat2_to_cat1["romantic"],
                            platonic_like=cat2_to_cat1["platonic"],
                            dislike=cat2_to_cat1["dislike"],
                            admiration=cat2_to_cat1["admiration"],
                            comfortable=cat2_to_cat1["comfortable"],
                            jealousy=cat2_to_cat1["jealousy"],
                            trust=cat2_to_cat1["trust"]
                        )

                    # if the parent is dead, don't make their relationship to the kits cus it ain't saved anyway
                    if not created_cats[0].dead:
                        created_cats[0].create_one_relationship(new_cat)
                        parent_to_kit = game.config["new_cat"]["parent_buff"]["parent_to_kit"]
                        change_relationship_values(
                            cats_to=[new_cat.ID],
                            cats_from=[created_cats[0]],
                            romantic_love=parent_to_kit["romantic"],
                            platonic_like=parent_to_kit["platonic"],
                            dislike=parent_to_kit["dislike"],
                            admiration=parent_to_kit["admiration"],
                            comfortable=parent_to_kit["comfortable"],
                            jealousy=parent_to_kit["jealousy"],
                            trust=parent_to_kit["trust"]
                        )

        # now have the new cats form relationships with the patrol cats and 
        # update inheritance
        for new_cat in created_cats:
            if new_cat.outside:
                continue
            if new_cat.dead:
                continue
            for patrol_cat in self.patrol_cats:
                patrol_cat.create_one_relationship(new_cat)
                new_cat.create_one_relationship(patrol_cat)
                
            self.results_text.append(f"{new_cat.name} has joined the Clan.")
            
            # update inheritance!
            new_cat.create_inheritance_new_cat()
            
            
            # for each cat increase the relationship towards all patrolling cats
            new_to_clan_cat = game.config["new_cat"]["rel_buff"]["new_to_clan_cat"]
            clan_cat_to_new = game.config["new_cat"]["rel_buff"]["clan_cat_to_new"]
            change_relationship_values(
                cats_to=[cat.ID for cat in self.patrol_cats],
                cats_from=[new_cat],
                romantic_love=new_to_clan_cat["romantic"],
                platonic_like=new_to_clan_cat["platonic"],
                dislike=new_to_clan_cat["dislike"],
                admiration=new_to_clan_cat["admiration"],
                comfortable=new_to_clan_cat["comfortable"],
                jealousy=new_to_clan_cat["jealousy"],
                trust=new_to_clan_cat["trust"]
            )
            change_relationship_values(
                cats_to=[new_cat.ID],
                cats_from=self.patrol_cats,
                romantic_love=clan_cat_to_new["romantic"],
                platonic_like=clan_cat_to_new["platonic"],
                dislike=clan_cat_to_new["dislike"],
                admiration=clan_cat_to_new["admiration"],
                comfortable=clan_cat_to_new["comfortable"],
                jealousy=clan_cat_to_new["jealousy"],
                trust=clan_cat_to_new["trust"]
            )

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

    # ---------------------------------------------------------------------------- #
    #                                   Handlers                                   #
    # ---------------------------------------------------------------------------- #

    def handle_exp_gain(self, success: bool):

        if game.clan.game_mode == 'classic':
            gm_modifier = 1
        elif game.clan.game_mode == 'expanded':
            gm_modifier = 3
        elif game.clan.game_mode == 'cruel season':
            gm_modifier = 6
        else:
            gm_modifier = 1

        if success:
            base_exp = 0
            if "master" in self.experience_levels:
                max_boost = 10
            else:
                max_boost = 0
            patrol_exp = 2 * self.patrol_event.exp
            gained_exp = (patrol_exp + base_exp + max_boost)
            gained_exp = max(gained_exp * (1 - 0.1 * len(self.patrol_cats)) / gm_modifier, 1)
        else:
            gained_exp = 0

        # Apprentice exp, does not depend on success
        if game.clan.game_mode != "classic" and (
                "apprentice" in self.patrol_statuses or "medicine cat apprentice" in self.patrol_statuses):
            app_exp = max(random.randint(1, 7) * (1 - 0.1 * len(self.patrol_cats)), 1)
        else:
            app_exp = 0

        if gained_exp or app_exp:
            for cat in self.patrol_cats:
                if cat.status in ["apprentice", "medicine cat apprentice"]:
                    cat.experience = cat.experience + app_exp
                else:
                    cat.experience = cat.experience + gained_exp

    def handle_deaths_and_gone(self, outcome):
        ''' handles death and abduction/lost events '''
        # find the new cat tag and split to get attributes - else return if no tag found
        attribute_list = []
        tags = self.patrol_event.tags
        for tag in tags:
            # print(tag)
            if "death" in tag or "gone" in tag:
                attribute_list = tag.split("_")
                print(attribute_list)
                break
        if attribute_list and len(attribute_list) == 1:
            if "stat" in outcome:
                cat = self.patrol_fail_stat_cat
            elif "leader" in outcome:
                cat = self.patrol_leader
            else:
                cat = self.patrol_random_cat
        else:
            if "app1" in attribute_list:
                cat = self.patrol_apprentices[0]
        if "no_body" in self.patrol_event.tags:
            body = False
        else:
            body = True
        if "death" in self.patrol_event.tags:
            if cat.status == 'leader':
                if 'all_lives' in self.patrol_event.tags:
                    game.clan.leader_lives -= 10
                    self.results_text.append(f"{cat.name} lost all their lives.")
                elif "some_lives" in self.patrol_event.tags:
                    if game.clan.leader_lives > 2:
                        current_lives = int(game.clan.leader_lives)
                        game.clan.leader_lives -= random.randrange(1, current_lives - 1)
                        self.results_text.append(f"{cat.name} lost some of their lives.")
                    else:
                        game.clan.leader_lives -= 1
                        self.results_text.append(f"{cat.name} lost one life.")
                else:
                    game.clan.leader_lives -= 1
                    self.results_text.append(f"{cat.name} lost one life.")
            else:
                self.results_text.append(f"{cat.name} died.")

            self.handle_history(cat, death=True)
            cat.die(body)

            if game.game_mode != "classic" and len(self.patrol_cats) > 1:
                for cat in self.patrol_cats:
                    if not cat.dead:
                        cat.get_injured("shock", lethal=False)

        elif "disaster" in self.patrol_event.tags:
            for cat in self.patrol_cats:
                cat.experience += self.patrol_event.exp
                cat.experience = min(cat.experience, 80)
                if cat.status == 'leader':
                    if 'all_lives' in self.patrol_event.tags:
                        game.clan.leader_lives -= 10
                        self.results_text.append(f"{cat.name} lost all their lives.")
                    elif "some_lives" in self.patrol_event.tags:
                        if game.clan.leader_lives > 2:
                            current_lives = int(game.clan.leader_lives)
                            game.clan.leader_lives -= random.randrange(1, current_lives - 1)
                            self.results_text.append(f"{cat.name} lost some of their lives.")
                        else:
                            self.results_text.append(f"{cat.name} lost one life.")
                            game.clan.leader_lives -= 1
                    else:
                        self.results_text.append(f"{cat.name} lost all their lives.")
                        game.clan.leader_lives -= 10
                else:
                    self.results_text.append(f"{cat.name} died.")

                self.handle_history(cat, death=True)
                cat.die(body)

        elif "multi_deaths" in self.patrol_event.tags:
            cats_dying = choice([2, 3])
            if cats_dying >= len(self.patrol_cats):
                cats_dying = int(len(self.patrol_cats) - 1)
            for d in range(0, cats_dying):
                cat = self.patrol_cats[d]
                if self.patrol_cats[d].status == 'leader':
                    if 'all_lives' in self.patrol_event.tags:
                        game.clan.leader_lives -= 10
                        self.results_text.append(f"{cat.name} lost all their lives.")
                    elif "some_lives" in self.patrol_event.tags:
                        if game.clan.leader_lives > 2:
                            current_lives = int(game.clan.leader_lives)
                            game.clan.leader_lives -= random.randrange(1, current_lives - 1)
                            self.results_text.append(f"{cat.name} lost some of their lives.")
                        else:
                            self.results_text.append(f"{cat.name} lost one life.")
                            game.clan.leader_lives -= 1
                    else:
                        self.results_text.append(f"{cat.name} lost all their lives.")
                        game.clan.leader_lives -= 10
                else:
                    self.results_text.append(f"{cat.name} died.")
                self.handle_history(cat, death=True)
                cat.die()

        # cats disappearing on patrol is also handled under this def for simplicity's sake
        elif "gone" in self.patrol_event.tags:
            self.results_text.append(f"{cat.name} has been lost.")
            cat.gone()
            cat.grief(body=False)

        elif "disaster_gone" in self.patrol_event.tags:
            for cat in self.patrol_cats:
                self.results_text.append(f"{cat.name} has been lost.")
                cat.experience += self.patrol_event.exp
                cat.experience = min(cat.experience, 80)
                cat.gone()
                cat.grief(body=False)

        elif "multi_gone" in self.patrol_event.tags:
            cats_gone = choice([2, 3])
            if cats_gone >= len(self.patrol_cats):
                cats_gone = int(len(self.patrol_cats) - 1)
            for g in range(0, cats_gone):
                self.results_text.append(f"{self.patrol_cats[g].name} has been lost.")
                self.patrol_cats[g].gone()
                self.patrol_cats[g].grief(body=False)

    def handle_conditions(self, outcome):

        condition_lists = {
            "battle_injury": ["claw-wound", "mangled leg", "mangled tail", "torn pelt", "cat bite"],
            "minor_injury": ["sprain", "sore", "bruises", "scrapes"],
            "blunt_force_injury": ["broken bone", "broken back", "head damage", "broken jaw"],
            "hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
            "cold_injury": ["shivering", "frostbite"],
            "big_bite_injury": ["bite-wound", "broken bone", "torn pelt", "mangled leg", "mangled tail"],
            "small_bite_injury": ["bite-wound", "torn ear", "torn pelt", "scrapes"],
            "beak_bite": ["beak bite", "torn ear", "scrapes"],
            "rat_bite": ["rat bite", "torn ear", "torn pelt"]
        }

        possible_conditions = []
        cat = None
        lethal = True

        # get the cat to injure
        if "stat" in outcome:
            cat = self.patrol_fail_stat_cat
        else:
            if "apprentice" in self.patrol_event.tags:
                cat = self.patrol_apprentices[0]
            else:
                cat = self.patrol_random_cat

        if self.patrol_event.tags:
            # here we check if a specific condition has been tagged for, excluding shock, and add it to possible
            # conditions list

            if "injury" in self.patrol_event.tags:
                for tag in self.patrol_event.tags:
                    if tag in INJURIES:
                        possible_conditions.append(tag)
                        continue
                    elif tag in ILLNESSES:
                        possible_conditions.append(tag)
                        continue
                    elif tag in PERMANENT:
                        possible_conditions.append(tag)
                        continue
            # next we check if a list (y) has been tagged for and add that list to possible conditions
            for y in condition_lists:
                if y in self.patrol_event.tags:
                    possible_conditions.extend(condition_lists[y])
                    continue

            # check for lethality
            if "non_lethal" in self.patrol_event.tags:
                lethal = False

            # poisons cats
            if "poison_clan" in self.patrol_event.tags:
                self.living_cats = []
                for x in range(len(Cat.all_cats.values())):
                    the_cat = list(Cat.all_cats.values())[x]
                    if not the_cat.dead and not the_cat.outside:
                        self.living_cats.append(the_cat)

                cats_to_poison = random.sample(self.living_cats, k=min(len(self.living_cats), choice([2, 3, 4])))
                for poisoned in cats_to_poison:
                    poisoned.get_injured('poisoned')
                    self.handle_history(cat, 'poisoned', possible=True, death=True)
                    if f"{poisoned.name} got: poisoned" not in self.results_text:
                        self.results_text.append(f"{poisoned.name} got: poisoned")

            # now we hurt the kitty
            if "injure_all" in self.patrol_event.tags:
                for cat in self.patrol_cats:
                    if len(possible_conditions) > 0:
                        new_condition = choice(possible_conditions)
                        if f"{cat.name} got: {new_condition}" not in self.results_text:
                            self.results_text.append(f"{cat.name} got: {new_condition}")
                        if new_condition in INJURIES:
                            cat.get_injured(new_condition, lethal=lethal)
                        elif new_condition in ILLNESSES:
                            cat.get_ill(new_condition, lethal=lethal)
                        elif new_condition in PERMANENT:
                            cat.get_permanent_condition(new_condition)
                        self.handle_history(cat, new_condition, possible=True, scar=True, death=True)
            else:
                if len(possible_conditions) > 0:
                    new_condition = choice(possible_conditions)
                    self.results_text.append(f"{cat.name} got: {new_condition}")
                    if new_condition in INJURIES:
                        cat.get_injured(new_condition, lethal=lethal)
                    elif new_condition in ILLNESSES:
                        cat.get_ill(new_condition, lethal=lethal)
                    elif new_condition in PERMANENT:
                        cat.get_permanent_condition(new_condition)
                    self.handle_history(cat, new_condition, possible=True, scar=True, death=True)

    def handle_scars(self, outcome):
        if self.patrol_event.tags is not None:
            print('getting scar')
            if "scar" in self.patrol_event.tags:
                if "stat" not in outcome:
                    cat = self.patrol_random_cat
                elif "stat" in outcome:
                    cat = self.patrol_fail_stat_cat
                else:
                    return
                if len(self.patrol_random_cat.pelt.scars) < 4:
                    for tag in self.patrol_event.tags:
                        print(tag)
                        if tag in Pelt.scars1 + Pelt.scars2 + Pelt.scars3:
                            print('gave scar')
                            cat.pelt.scars.append(tag)
                            self.results_text.append(f"{cat.name} got a scar.")
                    self.handle_history(cat, scar=True)

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

    def handle_herbs(self, outcome):
        herbs_gotten = []
        no_herbs_tags = ["no_herbs0", "no_herbs1", "no_herbs2", "no_herbs3"]
        many_herbs_tags = ["many_herbs0", "many_herbs1", "many_herbs2", "many_herbs3"]
        patrol_size_modifier = int(len(self.patrol_cats) * .5)

        # converting outcomes
        outcomes = {
            "unscathed_common": 0,
            "unscathed_rare": 1,
            "stat_skill": 2,
            "stat_trait": 3
        }
        outcome_number = outcomes[outcome]
        outcome = outcome_number
        
        if f"no_herbs{outcome}" in self.patrol_event.tags:
            return

        large_amount = None
        if f"many_herbs{outcome}" in self.patrol_event.tags:
            large_amount = 4

        if "random_herbs" in self.patrol_event.tags:
            number_of_herb_types = choices([1, 2, 3], [6, 5, 1], k=1)
            herbs_picked = random.sample(HERBS, k=number_of_herb_types[0])
            for herb in herbs_picked:
                herbs_gotten.append(str(herb).replace('_', ' '))
                if not large_amount:
                    amount_gotten = choices([1, 2, 3], [2, 3, 1], k=1)[0]
                else:
                    amount_gotten = large_amount

                # Apply patrol size modifier
                amount_gotten = int(amount_gotten * patrol_size_modifier)
                if amount_gotten < 1:
                    amount_gotten = 1

                if herb in game.clan.herbs.keys():
                    game.clan.herbs[herb] += amount_gotten
                else:
                    game.clan.herbs.update({herb: amount_gotten})

        elif "herb" in self.patrol_event.tags:
            for tag in self.patrol_event.tags:
                if tag in HERBS:
                    herbs_gotten.append(str(tag).replace('_', ' '))
                    if not large_amount:
                        amount_gotten = choices([1, 2, 3], [2, 3, 1], k=1)[0]
                    else:
                        amount_gotten = large_amount

                    # Apply patrol size modifier
                    amount_gotten = int(amount_gotten * patrol_size_modifier)
                    if amount_gotten < 1:
                        amount_gotten = 1

                    if tag in game.clan.herbs.keys():
                        game.clan.herbs[tag] += amount_gotten
                    else:
                        game.clan.herbs.update({tag: amount_gotten})

        if herbs_gotten:
            if len(herbs_gotten) == 1 and herbs_gotten[0] != 'cobwebs':
                insert = f"{herbs_gotten[0]} was"
            elif len(herbs_gotten) == 1 and herbs_gotten[0] == 'cobwebs':
                insert = f"{herbs_gotten[0]} were"
            elif len(herbs_gotten) == 2:
                if str(herbs_gotten[0]) == str(herbs_gotten[1]):
                    insert = f"{herbs_gotten[0]} was"
                else:
                    insert = f"{herbs_gotten[0]} and {herbs_gotten[1]} were"
            else:
                insert = f"{', '.join(herbs_gotten[:-1])}, and {herbs_gotten[-1]} were"
            game.herb_events_list.append(f"{insert.capitalize()} gathered on a patrol.")
            self.results_text.append(f"{insert.capitalize()} gathered during this patrol.")

    def handle_prey(self, outcome_key):
        """Handle the amount of prey which was caught and add it to the fresh-kill pile of the clan."""
        if not "hunting" in self.patrol_event.tags:
            return

        if not FRESHKILL_ACTIVE:
            return

        basic_amount = PREY_REQUIREMENT["warrior"]
        if game.clan.game_mode == 'expanded':
            basic_amount += ADDITIONAL_PREY
        prey_types = {
            "small_prey": basic_amount,
            "medium_prey": basic_amount * 1.5,
            "large_prey": basic_amount * 2,
            "huge_prey": basic_amount * 3
        }

        if not self.success and "hunting" in self.patrol_event.tags:
            cancel_tags = ["no_fail_prey", "poison_clan", "death", "disaster", "multi_deaths", "no_body",
                           "cruel_season", "gone", "multi_gone", "disaster_gone"]
            relevant_patrol_tags = [tag for tag in self.patrol_event.tags if tag in cancel_tags]
            if len(relevant_patrol_tags) == 0:
                amount = int(PREY_REQUIREMENT["warrior"] * len(self.patrol_cats) / 1.5)
                for cat in self.patrol_cats:
                    if cat.skills.primary.path == SkillPath.HUNTER and cat.skills.primary.tier > 0:
                        amount += int((HUNTER_EXP_BONUS[cat.experience_level] * HUNTER_BONUS[str(cat.skills.primary.tier)]) / 10 + 1)
                    elif cat.skills.secondary and cat.skills.secondary.path == SkillPath.HUNTER and cat.skills.secondary.tier > 0:
                        amount += int((HUNTER_EXP_BONUS[cat.experience_level] * HUNTER_BONUS[str(cat.skills.secondary.tier)]) / 10 + 1)
                game.clan.freshkill_pile.add_freshkill(int(amount))
                if FRESHKILL_ACTIVE:
                    print(f" -- FRESHKILL: added {amount} fail-prey")
                if len(self.patrol_cats) == 1:
                    self.results_text.append(
                        f"{self.patrol_leader.name} still manages to bring home some amount of prey.")
                else:
                    self.results_text.append(f"The patrol still manages to bring home some amount of prey.")
            return

        prey_amount_per_cat = 0
        total_amount = 0

        # after the patrol format changed, the tag's have to be adapted
        number_translation = {}
        idx = 0
        for k in self.patrol_event.success_text.keys():
            number_translation[k] = idx
            idx += 1

        # check what kind of prey type this succeeded patrol event has
        amount_text = None
        for prey_type, amount in prey_types.items():
            current_tag = prey_type
            if outcome_key in number_translation:
                current_tag = current_tag + str(number_translation[outcome_key])
            amount_text = prey_type.split('_')[0]
            if current_tag in self.patrol_event.tags or prey_type in self.patrol_event.tags:
                prey_amount_per_cat = amount
                break
        if FRESHKILL_ACTIVE:
            print(" -- FRESHKILL: amount per cat ", prey_amount_per_cat)

        for cat in self.patrol_cats:
            total_amount += prey_amount_per_cat
            # add bonus of certain skills
            if cat.skills.primary.path == SkillPath.HUNTER and cat.skills.primary.tier > 0:
                total_amount += HUNTER_EXP_BONUS[cat.experience_level] * HUNTER_BONUS[str(cat.skills.primary.tier)]
            elif cat.skills.secondary and cat.skills.secondary.path == SkillPath.HUNTER and cat.skills.secondary.tier > 0:
                total_amount += HUNTER_EXP_BONUS[cat.experience_level] * HUNTER_BONUS[str(cat.skills.secondary.tier)]
        if game.clan.game_mode != "classic":
            if FRESHKILL_ACTIVE:
                print(f" -- FRESHKILL: added {total_amount} prey")
            game.clan.freshkill_pile.add_freshkill(total_amount)
            if total_amount > 0:
                amount_text = "medium"
                if total_amount < game.clan.freshkill_pile.amount_food_needed() / 2:
                    amount_text = "small"
                elif total_amount < game.clan.freshkill_pile.amount_food_needed():
                    amount_text = "decent"
                elif total_amount >= game.clan.freshkill_pile.amount_food_needed() * 2:
                    amount_text = "huge"
                elif total_amount >= game.clan.freshkill_pile.amount_food_needed() * 1.5:
                    amount_text = "large"
                elif total_amount >= game.clan.freshkill_pile.amount_food_needed():
                    amount_text = "good"

                if len(self.patrol_cats) == 1:
                    self.results_text.append(f"{self.patrol_leader.name} brings back a {amount_text} amount of prey.")
                else:
                    self.results_text.append(f"The patrol brings back a {amount_text} amount of prey.")

    def handle_clan_relations(self, difference, antagonize, outcome):
        """
        relations with other clans
        """
        if "other_clan" in self.patrol_event.tags:
            other_clan = self.other_clan
            if "otherclan_nochangefail" in self.patrol_event.tags and not self.success:
                difference = 0
            elif "otherclan_nochangesuccess" in self.patrol_event.tags and self.success and not antagonize:
                difference = 0
            elif "otherclan_antag_nochangefail" in self.patrol_event.tags and antagonize and not self.success:
                difference = 0

            if f"success_reldown{outcome}" in self.patrol_event.tags:
                difference = -1
                insert = "worsened"
            elif difference > 0 and self.patrol_event.patrol_id != "gen_bord_otherclan3":
                insert = "improved"
            elif difference == 0:
                insert = "remained neutral"
            else:
                insert = "worsened"
            change_clan_relations(other_clan, difference)
            #print(f"Relations with {other_clan} have {insert} {difference}.")
            self.results_text.append(f"Relations with {other_clan} have {insert}.")

    def handle_mentor_app_pairing(self):
        for cat in self.patrol_cats:
            if Cat.fetch_cat(cat.mentor) in self.patrol_cats:
                cat.patrol_with_mentor += 1
                affect_personality = cat.personality.mentor_influence(Cat.fetch_cat(cat.mentor))
                affect_skills = cat.skills.mentor_influence(Cat.fetch_cat(cat.mentor))
                if affect_personality:
                    History.add_facet_mentor_influence(cat, affect_personality[0], affect_personality[1], affect_personality[2])
                    print(str(cat.name), affect_personality)
                if affect_skills:
                    History.add_skill_mentor_influence(cat, affect_skills[0], affect_skills[1], affect_skills[2])
                    print(str(cat.name), affect_skills)

    def handle_reputation(self, difference):
        """
        reputation with outsiders
        """
        if "no_change_fail_rep" in self.patrol_event.tags and not self.success:
            difference = 0
        change_clan_reputation(difference)
        if difference > 0:
            insert = "improved"
        elif difference == 0:
            insert = "remained neutral"
        else:
            insert = "worsened"
        #print("REP: " + int(game.clan.reputation))
        self.results_text.append(f"Your Clan's reputation towards Outsiders has {insert}.")

    def handle_relationships(self):
        n = 5
        if "big_change" in self.patrol_event.tags:
            n = 10

        romantic_love = 0
        platonic_like = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0

        if self.success:
            if "no_change_success" in self.patrol_event.tags:
                n = 0

            if "romantic" in self.patrol_event.tags:
                romantic_love = n
            if "platonic" in self.patrol_event.tags:
                platonic_like = n
            if "dislike" in self.patrol_event.tags:
                dislike = -n
            if "pos_dislike" in self.patrol_event.tags:
                dislike = n
            if "respect" in self.patrol_event.tags:
                admiration = n
            if "comfort" in self.patrol_event.tags:
                comfortable = n
            if "jealous" in self.patrol_event.tags:
                jealousy = -n
            if "pos_jealous" in self.patrol_event.tags:
                jealousy = n
            if "trust" in self.patrol_event.tags:
                trust = n

        elif "sacrificial" in self.patrol_event.tags:  # for when a cat risks themselves valiantly and still fails
            admiration = 15
            trust = 15

        elif not self.success and "pos_fail" not in self.patrol_event.tags:
            if "no_change_fail" in self.patrol_event.tags:
                n = 0

            if "romantic" in self.patrol_event.tags:
                romantic_love = -n
            if "platonic" in self.patrol_event.tags:
                platonic_like = -n
            if "dislike" in self.patrol_event.tags:
                dislike = n
            if "pos_dislike" in self.patrol_event.tags:
                dislike = -n
            if "disrespect" in self.patrol_event.tags:
                admiration = -n
            if "comfort" in self.patrol_event.tags:
                comfortable = -n
            if "jealous" in self.patrol_event.tags:
                jealousy = n
            if "pos_jealous" in self.patrol_event.tags:
                jealousy = -n
            if "distrust" in self.patrol_event.tags:
                trust = -n

        # collect the needed IDs and lists
        all_cats = [i for i in Cat.all_cats.values() if not (i.dead or i.outside)]
        cat_ids = [cat.ID for cat in self.patrol_cats]
        r_c_id = self.patrol_random_cat.ID
        s_c_id = None
        sc_rc_ids = None
        sc_rc = []
        if self.patrol_win_stat_cat:
            s_c_id = self.patrol_win_stat_cat.ID
            sc_rc = [self.patrol_win_stat_cat, self.patrol_random_cat]
            sc_rc_ids = [s_c_id, r_c_id]
        elif self.patrol_fail_stat_cat:
            s_c_id = self.patrol_fail_stat_cat.ID
            sc_rc = [self.patrol_fail_stat_cat, self.patrol_random_cat]
            sc_rc_ids = [s_c_id, r_c_id]
        p_l_id = self.patrol_leader.ID
        app_ids = [cat.ID for cat in self.patrol_apprentices]
        pl_rc = [self.patrol_leader, self.patrol_random_cat]
        pl_rc_ids = [p_l_id, r_c_id]

        if "clan_to_p_l" in self.patrol_event.tags:
            # whole Clan gains relationship towards p_l
            cats_to = [p_l_id]
            cats_from = all_cats

        elif "clan_to_r_c" in self.patrol_event.tags:
            if self.patrol_fail_stat_cat or self.patrol_win_stat_cat:
                # whole Clan gains relationship towards s_c
                cats_to = [s_c_id]
                cats_from = all_cats
            else:
                cats_to = [r_c_id]
                cats_from = all_cats

        elif "clan to patrol" in self.patrol_event.tags:
            # whole Clan gains relationship towards patrol, the cats IN the patrol do not gain this relationship value
            cats_to = cat_ids
            cats_from = all_cats

        elif "patrol_to_r_c" in self.patrol_event.tags:
            if self.patrol_fail_stat_cat or self.patrol_win_stat_cat:
                cats_to = [s_c_id]
                cats_from = self.patrol_cats
            else:
                # whole Clan gains relationship towards r_c
                cats_to = [r_c_id]
                cats_from = self.patrol_cats

        elif "patrol_to_p_l" in self.patrol_event.tags:
            # patrol gains relationship towards p_l
            cats_to = [p_l_id]
            cats_from = self.patrol_cats

        elif "rel_patrol" in self.patrol_event.tags:
            # whole patrol gains relationship with each other
            cats_to = cat_ids
            cats_from = self.patrol_cats

        elif "rel_two_apps" in self.patrol_event.tags:
            # two apps gain relationship towards each other
            cats_to = app_ids
            cats_from = self.patrol_apprentices

        elif "p_l_to_r_c" in self.patrol_event.tags:
            # p_l gains relationship with r_c and vice versa
            cats_to = pl_rc_ids
            cats_from = pl_rc

        elif "s_c_to_r_c" in self.patrol_event.tags:
            # s_c gains relationship with r_c and vice versa
            cats_to = sc_rc_ids
            cats_from = sc_rc

        else:
            # whole patrol gains relationship with each other  just makes this happen if no other rel tags are added
            cats_to = cat_ids
            cats_from = self.patrol_cats

        # now change the values
        change_relationship_values(
            cats_to,
            cats_from,
            romantic_love,
            platonic_like,
            dislike,
            admiration,
            comfortable,
            jealousy,
            trust
        )


# ---------------------------------------------------------------------------- #
#                               PATROL CLASS END                               #
# ---------------------------------------------------------------------------- #


class PatrolEvent:

    def __init__(self,
                 patrol_id,
                 biome="Any",
                 season="Any",
                 tags=None,
                 intro_text="",
                 decline_text="",
                 chance_of_success=0,
                 exp=0,
                 success_text=None,
                 fail_text=None,
                 win_skills=None,
                 win_trait=None,
                 fail_skills=None,
                 fail_trait=None,
                 min_cats=1,
                 max_cats=6,
                 antagonize_text="",
                 antagonize_fail_text="",
                 history_text=None,
                 constraints=None,
                 other_clan=None):
        self.patrol_id = patrol_id
        self.biome = biome or "Any"
        self.season = season or "Any"
        self.tags = tags
        self.intro_text = intro_text
        self.success_text = success_text if success_text else []
        self.fail_text = fail_text if fail_text else []
        self.decline_text = decline_text
        self.history_text = history_text if history_text else []
        self.chance_of_success = chance_of_success  # out of 100
        self.exp = exp
        self.win_skills = win_skills if win_skills else []
        self.win_trait = win_trait if win_trait else []
        self.fail_skills = fail_skills if fail_skills else []
        self.fail_trait = fail_trait if fail_trait else []
        self.min_cats = min_cats
        self.max_cats = max_cats
        self.antagonize_text = antagonize_text
        self.antagonize_fail_text = antagonize_fail_text
        self.other_clan = other_clan
        self.constraints = constraints if constraints else {}


# ---------------------------------------------------------------------------- #
#                              GENERAL INFORMATION                             #
# ---------------------------------------------------------------------------- #

"""
    hunting patrols - "hunting", "small_prey", "medium_prey", "large_prey", "huge_prey"

    training patrols - "training",

    border patrols - "border", "other_clan", "reputation",

    med patrols - "med_cat", "herb", "random_herbs", "many_herbs#"

    un-used for now - "npc", "gone_cat"
            
    death and gone tags -
    "death", "disaster", "multi_deaths", "no_body", "cruel_season", "gone", "multi_gone", "disaster_gone",

    relationship tags - 
    "romantic", "platonic", "comfort", "respect", "trust", "dislike", "pos_dislike", "jealous", "pos_jealous", "distrust", "disrespect",
    "apprentice", "two_apprentices", "three_apprentices", "warrior", "no_app", "med_only", "no_leader",
    "no_deputy", "leader", "deputy",

    "clan_to_p_l", "clan_to_r_c", "patrol_to_p_l", "patrol_to_r_c",
    "rel_two_apps", "p_l_to_r_c", "s_c_to_r_c", "clan_to_patrol", "rel_patrol",
    "sacrificial", "pos_fail", "no_change_fail", "no_change_success", "big_change",
    "all_lives", "some_lives"

    relationship constraint - 
    "siblings", "mates", "parent/child", "child/parent",
    "romantic_NUMBER", "platonic_NUMBER", "dislike_NUMBER", "comfortable_NUMBER", "jealousy_NUMBER", "trust_NUMBER"

"""

# ! Patrol Notes
"""
-- success outcomes -- 
    "unscathed_common": 
    "unscathed_rare":
    "stat_skill": 
    "stat_trait":

-- fail outcomes -- 
    "unscathed_common": 
    "unscathed_stat": 
    "death": 
    "injury": 
    "stat_death": 
    "stat_injury": 
    "leader_death":

-- history text -- 
    History text[0] is scar text
    History text[1] is death text for normal cats
    History text[2] is death text for leaders
        
-- PATROL ABBREVIATIONS --
    Clan name - c_n
    Other Clan name - o_c_n
    Random cat - r_c
    Patrol leader - p_l
    Stat Cat - s_c (this is the cat with relevant skills/traits for the situation)
    Apprentice 1 - app1
    Apprentice 2 - app2
    Apprentice 3 - app3 
    Apprentice 4 - app4 
    Apprentice 5 - app5 
    Apprentice 6 - app6 
    Random cat 2 - r_c2
    Random cat 3 - r_c3
    Random cat 4 - r_c4
    Random cat 5 - r_c5

-- PATROL ID GUIDELINES --
    ID format: biome_type_descriptor 
        
    biomes:
    Forest - fst
    Plains - pln
    Mountainous - mtn
    Beach - bch
    Wetlands - wtlnd
    Desert - dst
    If no specific biome - gen
    If it needs multiple biomes, but not all biomes, then create dupe patrols in relevant biomes with appropriate 
    patrol IDs
        
    types:
    Hunting - hunt
    Border - bord
    Training - train
    Med Cat - med
    If no specific type, pick one bc they gotta be categorized somewhere.  Make dupes in each type if you feel like 
    they all apply or some apply.

    descriptors:
    Descriptors should be one word and a number, starting at 1 and incrementing up (i.e. mtn_hunt_mouse1 then 
    mtn_hunt_mouse2 for another patrol involving a mouse. If you then make a new patrol that is not mouse 
    related, choose a different descriptor word and start over again at 1) try to keep descriptor words unique from 
    other descriptors being used to make identification and sorting easier. 

-- RELATIONSHIP CONSTRAINT:
    This is an optional constraint, if you use this, all cats in the patrol has to have these relation.
    If there are multiple 'tags', all 'tags' will be be used for the filtering.

    general:
    "sibling", "mates"
    "parent/child" -> patrol leader is parent, random cat is child
    "child/parent" -> patrol leader is child, random cat is parent

    'thresholds':
    for a 'threshold' tag, you only have to add the value type and then a number.
    !ALL! relationship values of each cat to each other has to have these values or higher
    "romantic_NUMBER",
    "platonic_NUMBER",
    "dislike_NUMBER",
    "comfortable_NUMBER",
    "jealousy_NUMBER",
    "trust_NUMBER"

    NUMBER has to be replaced with a number -> e.g. "romantic_10"


-- TAG INFO: --
    You can ONLY have one of these:
    "death" (r_c dies), "disaster" (all die), "multi_deaths" (2-4 cats die)
    If you have more than one, it takes the first one in this order.
    same for: "gone" (r_c leaves the clan), "disaster_gone" (all leave the clan), "multi_gone" (2-4 cats leave the clan)

    #!FOR INJURIES, SEE CONDITIONS LIST FOR TAGGING
    Tag all injury patrols that should give a scar with "scar" to ensure that classic mode will still scar the cat.
    If you'd like a patrol to have an injury from one of the injury pools, tag with the pool name
    -- Possible Pools --
        "battle_injury": ["claw-wound", "bite-wound", "mangled leg", "mangled tail", "torn pelt"],
        "minor_injury": ["sprain", "sore", "bruises", "scrapes"],
        "blunt_force_injury": ["broken bone", "paralyzed", "head damage", "broken jaw"],
        "hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
        "cold_injury": ["shivering", "frostbite"],
        "big_bite_injury": ["bite-wound", "broken bone", "torn pelt", "mangled leg", "mangled tail"],
        "small_bite_injury": ["bite-wound", "torn ear", "torn pelt", "scrapes"]
        "beak_bite": ["beak bite", "torn ear", "scrapes"]
    If you want to specify a certain condition, tag both with "injury" and the condition
    If you want to injure all the cats in the patrol, tag with "injure_all"
    This will work with any condition whether they are an illness, injury, or perm condition
    If you want to ensure that a cat cannot die from the condition, tag with "non_lethal"
    Keep in mind that minor injuries are already non lethal by default and permanent conditions will not be affected by this tag.
    These tags will stack! So you could tag a patrol as "blunt_force_injury", "injury", "water in their lungs" to give all the 
    conditions from blunt_force_injury AND water in their lungs as possible conditions for that patrol. 
    Keep in mind that the "non_lethal" tag will apply to ALL the conditions for that patrol.
    Right now, nonlethal shock is auto applied to all cats present when another cat dies. This may change in the future.

    ! To tag injuries/illnesses on cats joining, you MUST use "new_cat_injury"
    You can choose from these:
        "nc_blunt_force_injury": ["broken bone", "broken back", "head damage", "broken jaw"],
        "nc_sickness": ["greencough", "redcough", "whitecough", "yellowcough"],
        "nc_battle_injury": ["claw-wound", "mangled leg", "mangled tail", "torn pelt", "bite-wound"],
        "nc_hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
        "nc_cold_injury": ["shivering", "frostbite"]

    or you can tag a specific injury like this: "nc_broken back"

    - HERB TAGGING: -
        herbs are given on successes only
        "random_herbs" <give a random assortment of herbs
        
        "herbs" < use to mark that this patrol gives a specific herb, use in conjunction with a herb tag. 
        
        Herb tags:
        reference herbs.json, you can use any herb name listed there
        
        "many_herbs#" < to cause the patrol to give a large number of herbs automatically. Numbering starts at 0. 
        Replace the # with the outcome number (i.e. if you want success[2] - which is the skill success - to give lots of herbs, then 
        use "many_herbs2")
        
        "no_herbs#" < to cause the patrol to give no herbs on a certain outcome, while still giving herbs on other 
        outcomes. Numbering starts at 0. Replace the # with the outcome number (i.e. if you want success[2] - which is the skill 
        success - to give no herbs, then use "no_herbs2")

    - TO SPECIFY -
        "one_apprentice" is for patrols with one apprentice in them. It works with the "apprentice" tag. 
        "two_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "three_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "four_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "five_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "six_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 

        "rel_two_apps" is for patrols with relationship changes between app1 and app2 that don't affect the rest of the 
        patrol, and also works with "two_apprentices" (or any of the higher numbered apprentice specifiers) and "apprentice".

        "warrior" is used to specify that the patrol should only trigger with at least 1 warrior in it. 
        "no_app" is for when no apps should be on the patrol

    - RELATIONSHIP TAGS -
        I think all of these can be used together. the tag for which relationships are increased should ALSO be used
        # whole Clan gains relationship towards p_l - "clan_to_p_l"
        # whole Clan gains relationship towards s_c - "clan_to_r_c" (triggers to be s_c if s_c is present)
        # whole Clan gains relationship towards r_c - "clan_to_r_c"
        # patrol gains relationship towards p_l - "patrol_to_p_l"
        # patrol gains relationship towards s_c - "patrol_to_r_c" (triggers to be s_c if s_c is present)
        # patrol gains relationship towards r_c - "patrol_to_r_c"
        # "p_l_to_r_c" is for specifically pl and rc gaining relationship with EACH OTHER
        # two apps gain relationship towards each other - "rel_two_apps"
        # whole Clan gains relationship towards patrol - "clan_to_patrol"
        # whole patrol gains relationship with each other - "rel_patrol" 
        (also default, so if you don't add any other tags, it goes to this. If you want this outcome, 
        you don't need to add any tags, this is just if you need to add one of the other tags)
        
        "romantic" < change romantic value
        "platonic" < change platonic value
        "comfort" < change comfort value
        "respect" < change admiration/respect value
        "trust" < change trust value
        "dislike" < change dislike value (decrease on success, increase on fail)
        "pos_dislike" < change dislike value (increase on success, decrease on fail)
        "jealous" < change jealousy value (decrease on success, increase on fail)
        "pos_jealous" < change jealous value (increase on success, decrease on fail)
        "distrust" < always decrease trust
        "disrespect" < always decrease respect
        
        ^^^ On a success, the above tagged values will increase (or if values are dislike and jealousy, 
        they will decrease).  On a fail, the tagged values will decrease (or if values are dislike and jealousy, they will increase)
        
        "sacrificial" is for fail outcomes where a cat valiantly sacrifices themselves for the Clan 
        (such as the single cat big dog patrol) this will give the tagged for group ("clan_to_r_c", "patrol_to_r_c", etc) 
        a big boost to respect and trust in that cat even though they failed (if the cat survives lol) Other tagged for values 
        will be disregarded for these fail outcomes.
        "pos_fail" is for if you want the tagged relationship values to still be positive on a failure, rather than negative.
        
        "big_change" is for if you want the values to increment by a larger number.  This will make all tagged relationship values change by 10 instead of 5
        
        "no_change_fail" to set all relationship value changes to 0 on fail outcomes
        "no_change_success" to set all relationship value changes to 0 on success outcomes

        "no_change_fail_rep" is for when rep should not change when a new_cat patrol fails

    - PREY TAGS -
        If there is no tag, there will be no prey if the hunt is successful
        There are 4 tag types "small_prey", "medium_prey", "large_prey" and "huge_prey". 
        If you want to differentiate between the success texts how much prey each success will get, you have to use the tag and then add the index of the sentence you want the prey to
        E.g. 3 successful outcome texts -> "small_prey0", "medium_prey1", "medium_prey2"

        There will be auto prey for failed hunts to stop the auto, following tags do not allow auto prey:
        > "no_fail_prey"
        + all disaster tags ("death", "disaster", "multi_deaths", "no_body", "cruel_season", "gone", "multi_gone", "disaster_gone")
        + "poison_clan"

        We want a mix of medium_prey and large_prey under normal conditions.


-- WHEN WRIING --   
        Event text should be kept to 350 characters at the maximum to keep it easily readable and concise.
        History text needs to be written in past tense.
        o_c_n and c_n should use "a" not "an" in front of them

"""
