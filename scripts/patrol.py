#!/usr/bin/env python3
# -*- coding: ascii -*-
import random
from random import choice, randint, choices

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.clan import HERBS
from scripts.utility import (
    add_siblings_to_cat,
    add_children_to_cat,
    event_text_adjust,
    change_clan_relations,
    change_clan_reputation,
    change_relationship_values,
    )
from scripts.game_structure.game_essentials import game
from scripts.cat.names import names
from scripts.cat.cats import Cat, cat_class, ILLNESSES, INJURIES, PERMANENT
from scripts.cat.pelts import collars, scars1, scars2, scars3
from scripts.cat_relations.relationship import Relationship
from scripts.clan_resources.freshkill import ADDITIONAL_PREY, PREY_REQUIREMENT, HUNTER_EXP_BONUS, HUNTER_BONUS, FRESHKILL_ACTIVE
from scripts.clan import Clan

# ---------------------------------------------------------------------------- #
#                              PATROL CLASS START                              #
# ---------------------------------------------------------------------------- #
"""
When adding new patrols, use \n to add a paragraph break in the text
"""


class Patrol():

    def __init__(self):
        self.results_text = []
        self.patrol_event = None
        self.patrol_leader = None
        self.patrol_cats = []
        self.patrol_names = []
        self.patrol_apprentices = []
        self.possible_patrol_leaders = []
        self.patrol_leader_name = None
        self.patrol_skills = []
        self.patrol_statuses = []
        self.patrol_traits = []
        self.patrol_total_experience = 0
        self.success = False
        self.final_success = ""
        self.final_fail = ""
        self.antagonize = ""
        self.antagonize_fail = ""
        self.patrol_random_cat = None
        self.patrol_other_cats = []
        self.patrol_fail_stat_cat = None
        self.patrol_win_stat_cat = None
        self.app1_name = None
        self.app2_name = None
        self.app3_name = None
        self.app4_name = None
        self.app5_name = None
        self.app6_name = None
        self.other_clan = None
        self.experience_levels = []

    def add_patrol_cats(self, patrol_cats: list, clan: Clan) -> None:
        """Add the list of cats to the patrol class and handles to set all needed values.

            Parameters
            ----------
            patrol_cats : list
                list of cats which are on the patrol
            
            clan: Clan
                the clan class of the game, this parameter is needed to make tests possible

            Returns
            ----------
        """
        self.patrol_cats.clear()
        self.patrol_names.clear()
        self.possible_patrol_leaders.clear()
        self.patrol_skills.clear()
        self.patrol_statuses.clear()
        self.patrol_traits.clear()
        self.patrol_apprentices.clear()
        self.patrol_total_experience = 0
        self.experience_levels.clear()
        self.patrol_other_cats.clear()

        for cat in patrol_cats:
            self.patrol_cats.append(cat)
            self.patrol_names.append(str(cat.name))
            if cat.status != 'apprentice':
                self.possible_patrol_leaders.append(cat)
            self.patrol_skills.append(cat.skill)
            self.patrol_statuses.append(cat.status)
            self.patrol_traits.append(cat.trait)
            self.patrol_total_experience += cat.experience
            self.experience_levels.append(cat.experience_level)
            if cat.status == 'apprentice' or cat.status == 'medicine cat apprentice':
                self.patrol_apprentices.append(cat)
            game.patrolled.append(cat)

        # sets medcat as leader if they're in the patrol
        if "medicine cat" in self.patrol_statuses:
            med_index = self.patrol_statuses.index("medicine cat")
            self.patrol_leader = self.patrol_cats[med_index]
        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warrior from being treated as medicine cats in medicine cat patrols.
        elif "medicine cat apprentice" in self.patrol_statuses:
            med_index = self.patrol_statuses.index("medicine cat apprentice")
            self.patrol_leader = self.patrol_cats[med_index]
        # sets leader as patrol leader
        elif clan.leader and clan.leader in self.patrol_cats:
            self.patrol_leader = clan.leader
        else:
            if self.possible_patrol_leaders:
                self.patrol_leader = choice(self.possible_patrol_leaders)
            elif not self.possible_patrol_leaders:
                self.patrol_leader = choice(self.patrol_cats)
        self.patrol_leader_name = str(self.patrol_leader.name)

        self.patrol_random_cat = choice(self.patrol_cats)

        # big check for p_l and r_c not being the same cat if we can help it
        if len(self.patrol_cats) >= 2:
            for c in range(len(self.patrol_cats)):
                if self.patrol_leader == self.patrol_random_cat:
                    self.patrol_random_cat = self.patrol_cats[c]
                else:
                    break

        # adds the other cats to an other cat list just in case
        if len(self.patrol_cats) >= 3:
            for cat in self.patrol_cats:
                if cat != self.patrol_leader and cat != self.patrol_random_cat:
                    self.patrol_other_cats.append(cat)

        # grabbing the apprentices' names
        if len(self.patrol_apprentices) != 0:
            if len(self.patrol_apprentices) == 1:
                self.app1_name = str(self.patrol_apprentices[0].name)
            elif len(self.patrol_apprentices) == 2:
                self.app1_name = str(self.patrol_apprentices[0].name)
                self.app2_name = str(self.patrol_apprentices[1].name)
            elif len(self.patrol_apprentices) == 3:
                self.app1_name = str(self.patrol_apprentices[0].name)
                self.app2_name = str(self.patrol_apprentices[1].name)
                self.app3_name = str(self.patrol_apprentices[2].name)
            elif len(self.patrol_apprentices) == 4:
                self.app1_name = str(self.patrol_apprentices[0].name)
                self.app2_name = str(self.patrol_apprentices[1].name)
                self.app3_name = str(self.patrol_apprentices[2].name)
                self.app4_name = str(self.patrol_apprentices[3].name)
            elif len(self.patrol_apprentices) == 5:
                self.app1_name = str(self.patrol_apprentices[0].name)
                self.app2_name = str(self.patrol_apprentices[1].name)
                self.app3_name = str(self.patrol_apprentices[2].name)
                self.app4_name = str(self.patrol_apprentices[3].name)
                self.app5_name = str(self.patrol_apprentices[4].name)
            elif len(self.patrol_apprentices) == 6:
                self.app1_name = str(self.patrol_apprentices[0].name)
                self.app2_name = str(self.patrol_apprentices[1].name)
                self.app3_name = str(self.patrol_apprentices[2].name)
                self.app4_name = str(self.patrol_apprentices[3].name)
                self.app5_name = str(self.patrol_apprentices[4].name)
                self.app6_name = str(self.patrol_apprentices[5].name)

        if clan.all_clans and len(clan.all_clans) > 0:
            self.other_clan = choice(clan.all_clans)
        else:
            self.other_clan = None

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
        clan_relations = int(other_clan.relations)
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
        if clan_size > 20:
            small_clan = False
        else:
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

        # other clan patrols
        if other_clan_chance == 1:
            if clan_neutral:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN))
            elif clan_allies:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN_ALLIES))
            elif clan_hostile:
                possible_patrols.extend(self.generate_patrol_events(self.OTHER_CLAN_HOSTILE))

        final_patrols, final_romance_patrols = self.filter_patrols(possible_patrols, biome, patrol_size, current_season, patrol_type)
        if patrol_type == 'hunting':
            final_patrols = self.balance_hunting(final_patrols)
        final_patrols = self.filter_relationship(final_patrols)
        final_romance_patrols = self.filter_relationship(final_romance_patrols)

        return final_patrols, final_romance_patrols

    def filter_patrols(self, possible_patrols, biome, patrol_size, current_season, patrol_type):
        filtered_patrols = []
        romantic_patrols = []
        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        for patrol in possible_patrols:
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

            # making sure related cats don't accidentally go on romantic patrols together
            '''if "romantic" in patrol.tags:
                if ("rel_two_apps" and "two_apprentices") in patrol.tags and len(self.patrol_apprentices) >= 2:
                    if not self.patrol_apprentices[0].is_potential_mate(self.patrol_apprentices[1],
                                                                        for_love_interest=True):
                        continue
                else:
                    if not self.patrol_random_cat.is_potential_mate(self.patrol_leader, for_patrol=True):
                        continue'''
        return filtered_patrols, romantic_patrols

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

    def filter_relationship(self, possible_patrols: list):
        """Filter the incoming patrol list according to the relationship constraints, if there are constraints.

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

        for patrol in possible_patrols:
            # if there are no constraints, add the patrol to the filtered list
            if len(patrol.relationship_constraint) == 0:
                filtered_patrols.append(patrol)
                continue

            # filtering - relationship status
            # check if all are siblings
            if "siblings" in patrol.relationship_constraint:
                test_cat = self.patrol_cats[0]
                testing_cats = [cat for cat in self.patrol_cats if cat.ID != test_cat.ID]

                siblings = [inter_cat for inter_cat in testing_cats if test_cat.is_sibling(inter_cat)]
                if len(siblings) + 1 != len(self.patrol_cats):
                    continue

            # check if the cats are mates
            if "mates" in patrol.relationship_constraint:
                # it should be exactly two cats for a "mate" patrol
                if len(self.patrol_cats) != 2:
                    continue
                else:
                    cat1 = self.patrol_cats[0]
                    cat2 = self.patrol_cats[1]
                    # if one of the cat has no mate, not add this patrol
                    if not cat1.mate or not cat2.mate:
                        continue
                    elif cat1.mate != cat2.ID or cat2.mate != cat1.ID:
                        continue

            # check if the cats are in a parent/child relationship
            if "parent/child" in patrol.relationship_constraint:
                # it should be exactly two cats for a "parent/child" patrol
                if len(self.patrol_cats) != 2:
                    continue
                # when there are two cats in the patrol, p_l and r_c are different cats per default
                if not self.patrol_leader.is_parent(self.patrol_random_cat):
                    continue

            # check if the cats are in a child/parent relationship
            if "child/parent" in patrol.relationship_constraint:
                # it should be exactly two cats for a "child/parent" patrol
                if len(self.patrol_cats) != 2:
                    continue
                # when there are two cats in the patrol, p_l and r_c are different cats per default
                if not self.patrol_random_cat.is_parent(self.patrol_leader):
                    continue

            # filtering - relationship values
            # when there will be more relationship values or other tags, this should be updated
            value_types = ["romantic", "platonic", "dislike", "comfortable", "jealousy", "trust"]
            break_loop = False
            for v_type in value_types:
                # first get all tags for the current value type
                tags = [constraint for constraint in patrol.relationship_constraint if v_type in constraint]

                # there is not such a tag for the current value type, check the next one
                if len(tags) == 0:
                    continue

                # there should be only one value constraint for each value type
                elif len(tags) > 1:
                    patrol_id = patrol.patrol_id
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
                        rel_above_threshold = list(
                            filter(lambda rel: rel.romantic_love >= threshold, relevant_relationships))
                    elif v_type == "platonic":
                        rel_above_threshold = list(
                            filter(lambda rel: rel.platonic_like >= threshold, relevant_relationships))
                    elif v_type == "dislike":
                        rel_above_threshold = list(filter(lambda rel: rel.dislike >= threshold, relevant_relationships))
                    elif v_type == "comfortable":
                        rel_above_threshold = list(
                            filter(lambda rel: rel.comfortable >= threshold, relevant_relationships))
                    elif v_type == "jealousy":
                        rel_above_threshold = list(
                            filter(lambda rel: rel.jealousy >= threshold, relevant_relationships))
                    elif v_type == "trust":
                        rel_above_threshold = list(filter(lambda rel: rel.trust >= threshold, relevant_relationships))

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
                continue

            filtered_patrols.append(patrol)

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
                min_cats=patrol["min_cats"],
                max_cats=patrol["max_cats"],
                win_skills=patrol["win_skills"] if "win_skills" in patrol else [],
                win_trait=patrol["win_trait"] if "win_trait" in patrol else [],
                fail_skills=patrol["fail_skills"] if "fail_skills" in patrol else [],
                fail_trait=patrol["fail_trait"] if "fail_trait" in patrol else [],
                antagonize_text=patrol["antagonize_text"] if "antagonize_text" in patrol else None,
                antagonize_fail_text=patrol["antagonize_fail_text"] if "antagonize_fail_text" in patrol else None,
                history_text=patrol["history_text"] if "history_text" in patrol else [],
                relationship_constraint=patrol["relationship_constraint"] if "relationship_constraint" in patrol else []
            )

            all_patrol_events.append(patrol_event)

        return all_patrol_events

    def calculate_success(self, antagonize=False):
        if self.patrol_event is None:
            return

        antagonize = antagonize
        success_text = self.patrol_event.success_text
        fail_text = self.patrol_event.fail_text

        gm_modifier = game.config["patrol_generation"][f"{game.clan.game_mode}_difficulty_modifier"]

        # if patrol contains cats with autowin skill, chance of success is high. otherwise it will calculate the
        # chance by adding the patrol event's chance of success plus the patrol's total exp
        success_chance = self.patrol_event.chance_of_success + int(
            self.patrol_total_experience / (2 * gm_modifier))

        print('starting chance:', self.patrol_event.chance_of_success)
        print('updated chance according to exp: ', success_chance)
        for kitty in self.patrol_cats:
            if kitty.skill in self.patrol_event.win_skills:
                success_chance += game.config["patrol_generation"]["win_stat_cat_modifier"]
                if ("great" or "very") in kitty.skill:
                    success_chance += game.config["patrol_generation"]["better_stat_modifier"]
                elif ("fantastic" or "excellent" or "extremely") in kitty.skill:
                    success_chance += game.config["patrol_generation"]["best_stat_modifier"]
            if kitty.trait in self.patrol_event.win_trait:
                success_chance += game.config["patrol_generation"]["win_stat_cat_modifier"]
            if kitty.skill in self.patrol_event.fail_skills:
                success_chance += game.config["patrol_generation"]["fail_stat_cat_modifier"]
            if self.patrol_event.fail_trait and kitty.trait in self.patrol_event.fail_trait:
                success_chance += game.config["patrol_generation"]["fail_stat_cat_modifier"]

            print(kitty.name, 'updated chance to', success_chance)
        print('ending chance', success_chance)


        c = randint(0, 100)
        outcome = int(random.getrandbits(4))

        # denotes if they get the common "basic" outcome or the rare "basic" outcome
        rare = False
        common = False
        if outcome >= 11:
            rare = True
        else:
            common = True

        # ---------------------------------------------------------------------------- #
        #                                   SUCCESS                                    #
        # ---------------------------------------------------------------------------- #

        if c < success_chance:
            self.success = True
            self.patrol_fail_stat_cat = None

            # default is outcome 0
            outcome = 0
            if self.patrol_win_stat_cat:
                if self.patrol_event.win_trait:
                    if self.patrol_win_stat_cat.trait in self.patrol_event.win_trait:
                        outcome = 3
                if self.patrol_event.win_skills:
                    if self.patrol_win_stat_cat.skill in self.patrol_event.win_skills:
                        outcome = 2
            else:
                if rare and len(success_text) >= 2:
                    if success_text[1]:
                        outcome = 1

            # this is specifically for new cat events that can come with kits
            litter_choice = False
            if self.patrol_event.tags is not None:
                if "kits" in self.patrol_event.tags:
                    litter_choice = choice([True, False])
                    if litter_choice:
                        outcome = 1
                    else:
                        outcome = 0

            self.handle_exp_gain()

            if not antagonize:
                self.add_new_cats(litter_choice=litter_choice)
            if self.patrol_event.tags is not None:
                if "other_clan" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_clan_relations(difference=int(-2), antagonize=True, outcome=outcome)
                    else:
                        self.handle_clan_relations(difference=int(1), antagonize=False, outcome=outcome)
                elif "new_cat" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_reputation(-10)
                    else:
                        self.handle_reputation(10)

            self.handle_mentor_app_pairing()
            self.handle_relationships()

            if game.clan.game_mode != 'classic' and not antagonize:
                self.handle_herbs(outcome)

            try:
                self.final_success = self.patrol_event.success_text[outcome]
            except IndexError:
                self.final_success = self.patrol_event.success_text[0]

            if antagonize:
                self.antagonize = self.patrol_event.antagonize_text

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
            else:
                unscathed = False

            outcome = 0  # unscathed and common outcome, the default failure

            # first we check for a fail stat outcome
            if self.patrol_fail_stat_cat:
                # safe, just failed
                if unscathed and len(fail_text) >= 2:
                    if fail_text[1]:
                        outcome = 1
                # injured
                elif not unscathed and common and len(fail_text) >= 5:
                    if fail_text[4]:
                        outcome = 4
                # dead
                elif not unscathed and rare and len(fail_text) >= 6:
                    if fail_text[5]:
                        outcome = 5

            # if no fail stat cat or outcomes, then onto the injured/dead outcomes
            if not outcome and not unscathed:
                # injured
                if common and len(fail_text) > 4:
                    if fail_text[3]:
                        outcome = 3
                # if the leader is present and a cat /would/ die, then the leader sacrifices themselves
                elif rare and len(fail_text) >= 7 and self.patrol_leader == game.clan.leader:
                    if fail_text[6]:
                        outcome = 6
                # dead
                elif rare and len(fail_text) >= 3:
                    if fail_text[2]:
                        outcome = 2

            # if /still/ no outcome is picked then double check that an outcome 0 is available,
            # if it isn't, then try to injure and then kill the cat
            if not outcome and not fail_text[0]:
                # attempt death outcome
                if fail_text[2]:
                    outcome = 2
                # attempt injure outcome
                elif fail_text[3]:
                    outcome = 3

            if outcome == 2:
                self.handle_deaths_and_gone(self.patrol_random_cat)
            elif outcome == 4:
                self.handle_deaths_and_gone(self.patrol_fail_stat_cat)
            elif outcome == 6:
                self.handle_deaths_and_gone(self.patrol_leader)
            elif outcome == 3 or outcome == 5:
                if game.clan.game_mode == 'classic':
                    self.handle_scars(outcome)
                else:
                    self.handle_conditions(outcome)
            if self.patrol_event.tags is not None:
                if "other_clan" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_clan_relations(difference=int(-1), antagonize=True, outcome=outcome)
                    else:
                        self.handle_clan_relations(difference=int(-1), antagonize=False, outcome=outcome)
                elif "new_cat" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_reputation(-5)
                    else:
                        self.handle_reputation(0)
            self.handle_mentor_app_pairing()
            self.handle_relationships()
            self.final_fail = self.patrol_event.fail_text[outcome]
            if antagonize:
                self.antagonize_fail = self.patrol_event.antagonize_fail_text

        if not antagonize and game.clan.game_mode != "classic":
            self.handle_prey(outcome)

        print('Patrol Succeeded?', self.success, ', Outcome Index:', outcome)

    def results(self):
        text = "<br>".join(self.results_text)
        self.results_text.clear()
        return text

    def add_new_cats(self, litter_choice):
        tags = self.patrol_event.tags
        if "new_cat" in tags:
            if "new_cat_kit" in tags:  # new kit
                backstory_choice = choice(['abandoned2', 'abandoned1', 'abandoned3'])
                created_cats = self.create_new_cat(loner=False, loner_name=False, kittypet=choice([True, False]),
                                                   kit=True, backstory=backstory_choice)
                new_cat = created_cats[0]

            elif "new_cat_adult" in tags:
                if "kittypet" in self.patrol_event.patrol_id:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True, kit=False,
                                                       litter=False,
                                                       relevant_cat=None,
                                                       backstory=choice(['kittypet1', 'kittypet2', 'kittypet3',
                                                                         'refugee3', 'tragedy_survivor3']))
                    new_cat = created_cats[0]
                    # add litter if the kits text is rolled
                    if litter_choice == True:
                        new_backstory = 'outsider_roots2'
                        created_cats.extend(self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory,
                                                                litter=True, relevant_cat=new_cat))
                else:  # new loner
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor', 'refugee2', 'tragedy_survivor4',
                                            'refugee4', 'tragedy_survivor2'])
                    created_cats = self.create_new_cat(loner=True, kittypet=False, backstory=new_backstory)
                    new_cat = created_cats[0]
                    # add litter if the kits text is rolled
                    if litter_choice == True:
                        new_backstory = 'outsider_roots2'
                        created_cats.extend(self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory,
                                                                litter=True, relevant_cat=new_cat))

            elif "new_cat_med" in tags:  # new med cat
                new_backstory = choice(['medicine_cat', 'disgraced', 'loner1', 'loner2',
                                        'wandering_healer1', 'wandering_healer2'])
                created_cats = self.create_new_cat(loner=True, loner_name=True, kittypet=False, kit=False, litter=False,
                                                   med=True,
                                                   backstory=new_backstory)
                new_cat = created_cats[0]
                new_cat.skill = choice(['good healer', 'great healer', 'fantastic healer'])
                # add litter if the kits text is rolled
                if litter_choice == True:
                    new_backstory = 'outsider_roots2'
                    created_cats.extend(self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory,
                                                            litter=True, relevant_cat=new_cat))
            elif "new_cat_queen" in tags:
                created_cats = []
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet is True:
                    new_backstory = choice(['kittypet1', 'kittypet2', 'kittypet3',
                                            'refugee3', 'tragedy_survivor3'])
                    created_cats.extend(self.create_new_cat(loner=False, loner_name=True, kittypet=True, queen=True,
                                                            backstory=new_backstory))
                    new_cat = created_cats[0]
                    new_cat.thought = "Feels relieved that they've found a safe place to stay"
                    if game.clan.game_mode != 'classic':
                        new_cat.get_injured("recovering from birth")
                else:
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor', 'refugee2', 'tragedy_survivor4',
                                            'refugee4', 'tragedy_survivor2'])
                    created_cats.extend(self.create_new_cat(loner=True, loner_name=True, kittypet=False, queen=True,
                                                            backstory=new_backstory))
                    new_cat = created_cats[0]
                    new_cat.thought = "Feels relieved that they've found a safe place to stay"
                    if game.clan.game_mode != 'classic':
                        new_cat.get_injured("recovering from birth")
                if "new_cat_kits" in tags:
                    if "new_cat_newborn" in tags:
                        new_backstory = 'outsider_roots2'
                        created_cats.extend(self.create_new_cat(loner=False, loner_name=True, backstory=new_backstory,
                                                                litter=True, relevant_cat=new_cat, age='newborn'))
                    else:
                        new_backstory = 'outsider_roots2'
                        created_cats.extend(self.create_new_cat(loner=False, loner_name=True, backstory=new_backstory,
                                                                litter=True, relevant_cat=new_cat))

            elif "new_cat_kits" in tags:  # new kits
                created_cats = []
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet is True:
                    new_backstory = choice(['kittypet1', 'kittypet2', 'kittypet3',
                                            'refugee3', 'tragedy_survivor3'])
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True, queen=True,
                                                            backstory=new_backstory)
                    new_cat = created_cats[0]
                    new_cat.outside = True
                    new_cat.dead = True
                    new_cat.name.suffix = ""
                    new_cat.thought = "Is glad that their kits are safe"
                else:
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor', 'refugee2', 'tragedy_survivor4',
                                            'refugee4', 'tragedy_survivor2'])
                    created_cats = self.create_new_cat(loner=True, loner_name=True, kittypet=False, queen=True,
                                                            backstory=new_backstory)
                    new_cat = created_cats[0]
                    new_cat.outside = True
                    new_cat.dead = True
                    new_cat.name.suffix = ""
                    new_cat.thought = "Is glad that their kits are safe"
                if "new_cat_newborn" in tags:
                    created_cats.extend(
                        self.create_new_cat(loner=False, loner_name=True, backstory=choice(['orphaned', 'orphaned2']),
                                            litter=True, age='newborn', relevant_cat=new_cat))
                else:
                    created_cats.extend(
                        self.create_new_cat(loner=False, loner_name=True, backstory=choice(['orphaned', 'orphaned2']),
                                            litter=True, relevant_cat=new_cat))

            elif "new_cat_apprentice" in tags:
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True,
                                                       age='young',
                                                       backstory=choice(['kittypet1', 'kittypet2', 'kittypet3',
                                                                         'refugee3', 'tragedy_survivor3']))
                    new_cat = created_cats[0]
                else:
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2', 'refugee',
                                            'tragedy_survivor', 'refugee2', 'tragedy_survivor4',
                                            'refugee4', 'tragedy_survivor2'])
                    created_cats = self.create_new_cat(loner=True, loner_name=True, kittypet=False,
                                                       backstory=new_backstory,
                                                       age='young')
                    new_cat = created_cats[0]
                    new_cat.update_mentor()

            elif "new_cat_elder" in tags:
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True, age='old',
                                                       backstory=choice(['kittypet1', 'kittypet2']))
                    new_cat = created_cats[0]
                else:  # new loner
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor'])
                    created_cats = self.create_new_cat(loner=True, kittypet=False, backstory=new_backstory, age='old')
                    new_cat = created_cats[0]

            else:
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet is True:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True,
                                                       backstory=choice(['kittypet1', 'kittypet2', 'kittypet3',
                                                                         'refugee3', 'tragedy_survivor3']))
                    new_cat = created_cats[0]
                else:  # new loner
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor', 'refugee2', 'tragedy_survivor4',
                                            'refugee4', 'tragedy_survivor2'])
                    created_cats = self.create_new_cat(loner=True, kittypet=False, backstory=new_backstory)
                    new_cat = created_cats[0]
            # now we hurt the kitty
            if "new_cat_injury" in tags and game.clan.game_mode != 'classic':
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
            for cat in created_cats:
                if not cat.outside:
                    self.results_text.append(f"{cat.name} has joined the Clan.")

    def create_new_cat(self,
                       loner=False,
                       loner_name=False,  # loner name actually means kittypet name
                       kittypet=False,
                       kit=False,
                       litter=False,
                       med=False,
                       queen=False,
                       age=None,
                       relevant_cat=None,
                       backstory=None,
                       other_clan=None) -> list:
        """This function creates cats based on the given values and returns a list."""
        name = None
        skill = None
        accessory = None
        status = "kitten"
        backstory = backstory
        other_clan = other_clan
        tags = self.patrol_event.tags
        gender = None
        if "new_cat_tom" in tags:
            gender = 'male'
        if "new_cat_female" in tags:
            gender = 'female'

        if not litter and not kit:
            if age == 'young':
                age = randint(6, 11)
            elif age == 'old':
                age = randint(100, 150)
            else:
                age = randint(22, 99)

        if queen:
            if game.settings['no gendered breeding']:
                gender = gender
            else:
                gender = 'female'
            if age < 16:
                age = 16

        if litter or kit:
            if age == 'newborn':
                age = 0
            else:
                age = randint(0, 5)

        kp_name_chance = (1, 5)

        if (loner or kittypet) and not kit and not litter:
            if loner_name:
                if loner and kp_name_chance != 1:
                    name = choice(names.normal_prefixes)
                else:
                    name = choice(names.loner_names)
            if age >= 12:
                status = "warrior"
            else:
                status = "apprentice"
        if kittypet:
            if choice([1, 2]) == 1:
                accessory = choice(collars)
        if med:
            status = "medicine cat"

        amount = choice([1, 1, 2, 2, 2, 3]) if litter else 1
        created_cats = []
        suffix_choice = choice([True, False]) # if the cat gets a suffix or not
        if suffix_choice:
            suffix_ = None
        else:
            suffix_ = ""

        if kit or litter or age == 'young': # babies will always get a suffix bc they don't know any better
            suffix_ = None
        
        for number in range(amount):
            new_cat = None
            if loner_name:
                new_cat = Cat(moons=age, prefix=name, suffix=suffix_, status=status,
                              gender=gender if gender is not None else choice(['female', 'male']),
                              backstory=backstory)
            else:
                new_cat = Cat(moons=age, status=status, suffix=suffix_,
                              gender=gender if gender is not None else choice(['female', 'male']), backstory=backstory)
            if skill:
                new_cat.skill = skill
            if accessory:
                new_cat.accessory = accessory

            if (kit or litter) and relevant_cat and relevant_cat.ID in Cat.all_cats:
                new_cat.parent1 = relevant_cat.ID
                if relevant_cat.mate:
                    new_cat.parent2 = relevant_cat.mate

            # create and update relationships
            for the_cat in new_cat.all_cats.values():
                if the_cat.dead or the_cat.outside:
                    continue
                the_cat.relationships[new_cat.ID] = Relationship(the_cat, new_cat)
                new_cat.relationships[the_cat.ID] = Relationship(new_cat, the_cat)
            new_cat.thought = 'Is looking around the camp with wonder'
            created_cats.append(new_cat)

        for new_cat in created_cats:
            add_siblings_to_cat(new_cat, cat_class)
            add_children_to_cat(new_cat, cat_class)
            game.clan.add_cat(new_cat)

        return created_cats

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

    def handle_exp_gain(self):
        gm_modifier = 1
        base_exp = 0
        if "max" in self.experience_levels:
            max_boost = 10
        else:
            max_boost = 0
        patrol_exp = self.patrol_event.exp
        if game.clan.game_mode == 'classic':
            gm_modifier = gm_modifier
        elif game.clan.game_mode == 'expanded':
            gm_modifier = 3
        elif game.clan.game_mode == 'cruel season':
            gm_modifier = 6
        lvl_modifier = 1  # this makes exp gain slower after the cat reaches average
        for cat in self.patrol_cats:
            gained_exp = ((patrol_exp + base_exp + max_boost) / len(self.patrol_cats)) / gm_modifier
            if cat.experience_level == "average":
                lvl_modifier = 1.25
            if cat.experience_level == "high":
                lvl_modifier = 1.75
            if cat.experience_level == "master":
                lvl_modifier = 2
            final_exp = gained_exp / lvl_modifier
            cat.experience = cat.experience + final_exp

    def handle_deaths_and_gone(self, cat):
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
            if len(self.patrol_event.history_text) >= 2 and cat.status != 'leader':
                cat.died_by.append(event_text_adjust(Cat, f'{self.patrol_event.history_text[1]}', cat, cat))
                self.results_text.append(f"{cat.name} died.")
            elif len(self.patrol_event.history_text) >= 2 and cat.status == 'leader':
                cat.died_by.append(event_text_adjust(Cat, f'{self.patrol_event.history_text[2]}', cat, cat))
            elif cat.status != 'leader':
                cat.died_by.append(f'This cat died while patrolling.')
                self.results_text.append(f"{cat.name} died.")
            else:
                cat.died_by.append(f'died while patrolling')

            cat.die(body)

            if len(patrol.patrol_cats) > 1:
                for cat in patrol.patrol_cats:
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
                if len(self.patrol_event.history_text) >= 2 and cat.status != 'leader':
                    self.results_text.append(f"{cat.name} died.")
                    cat.died_by.append(event_text_adjust(Cat, f'{self.patrol_event.history_text[1]}', cat, cat))
                elif len(self.patrol_event.history_text) >= 2 and cat.status == 'leader':
                    cat.died_by.append(event_text_adjust(Cat, f'{self.patrol_event.history_text[2]}', cat, cat))
                elif cat.status != 'leader':
                    self.results_text.append(f"{cat.name} died.")
                    cat.died_by.append(f'This cat died while patrolling.')
                else:
                    cat.died_by.append(f'died while patrolling')
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
                if len(self.patrol_event.history_text) >= 2 and cat.status != 'leader':
                    cat.died_by.append(
                        event_text_adjust(Cat, f'{self.patrol_event.history_text[1]}', cat,
                                          cat))
                elif len(self.patrol_event.history_text) >= 2 and self.patrol_cats[d].status == 'leader':
                    cat.died_by.append(
                        event_text_adjust(Cat, f'{self.patrol_event.history_text[2]}', cat,
                                          cat))
                elif cat.status != 'leader':
                    cat.died_by.append(f'This cat died while patrolling.')
                else:
                    cat.died_by.append(f'died while patrolling')
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
            "beak_bite": ["beak bite", "torn ear", "scrapes"]
        }

        possible_conditions = []
        cat = None
        lethal = True

        # get the cat to injure
        if outcome == 3:
            if "apprentice" in patrol.patrol_event.tags:
                cat = self.patrol_apprentices[0]
            else:
                cat = self.patrol_random_cat

        elif outcome == 5:
            cat = self.patrol_fail_stat_cat

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

            if "poison_clan" in self.patrol_event.tags:
                cat.get_injured("poisoned")
                self.living_cats = []
                for x in range(len(Cat.all_cats.values())):
                    the_cat = list(Cat.all_cats.values())[x]
                    if not the_cat.dead and not the_cat.outside:
                        self.living_cats.append(the_cat)
                cats_to_poison = random.choices(self.living_cats, k=choice([2, 3, 4]))
                for cat in cats_to_poison:
                    cat.get_injured('poisoned')
                    self.results_text.append(f"{cat.name} got: poisoned")

            # now we hurt the kitty
            if "injure_all" in self.patrol_event.tags:
                for cat in self.patrol_cats:
                    if len(possible_conditions) > 0:
                        new_condition = choice(possible_conditions)
                        self.results_text.append(f"{cat.name} got: {new_condition}")
                        if new_condition in INJURIES:
                            cat.get_injured(new_condition, lethal=lethal)
                        elif new_condition in ILLNESSES:
                            cat.get_ill(new_condition, lethal=lethal)
                        elif new_condition in PERMANENT:
                            cat.get_permanent_condition(new_condition)
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

    def handle_scars(self, outcome):
        if self.patrol_event.tags is not None:
            print('getting scar')
            if "scar" in self.patrol_event.tags:
                if outcome == 3:
                    cat = self.patrol_random_cat
                elif outcome == 5:
                    cat = self.patrol_fail_stat_cat
                else:
                    return
                if len(self.patrol_random_cat.scars) < 4:
                    for tag in self.patrol_event.tags:
                        print(tag)
                        if tag in scars1 + scars2 + scars3:
                            print('gave scar')
                            cat.scars.append(tag)
                            self.results_text.append(f"{cat.name} got a scar.")
                    if len(self.patrol_event.history_text) >= 1:
                        adjust_text = self.patrol_event.history_text[0]
                        adjust_text = adjust_text.replace("r_c", str(cat.name))
                        self.patrol_random_cat.scar_event.append(
                            f'{adjust_text}')
                    else:
                        self.patrol_random_cat.death_event.append(f'This cat gained a scar while patrolling.')

    def handle_herbs(self, outcome):
        herbs_gotten = []
        no_herbs_tags = ["no_herbs0", "no_herbs1", "no_herbs2", "no_herbs3"]
        many_herbs_tags = ["many_herbs0", "many_herbs1", "many_herbs2", "many_herbs3"]
        patrol_size_modifier = int(len(self.patrol_cats) * .5)

        for x in range(len(no_herbs_tags)):
            if f"no_herbs{x}" in patrol.patrol_event.tags and outcome == x:
                return

        large_amount = None
        for x in range(len(many_herbs_tags)):
            if f"many_herbs{x}" in patrol.patrol_event.tags and outcome == x:
                large_amount = 4

        if "random_herbs" in patrol.patrol_event.tags:
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

        elif "herb" in patrol.patrol_event.tags:
            for tag in patrol.patrol_event.tags:
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

    def handle_prey(self, outcome_nr):
        """Handle the amount of prey which was caught and add it to the fresh-kill pile of the clan."""
        if not "hunting" in patrol.patrol_event.tags:
            return

        if not FRESHKILL_ACTIVE:
            return

        basic_amount = PREY_REQUIREMENT["warrior"]
        if game.clan.game_mode == 'expanded':
            basic_amount += ADDITIONAL_PREY
        prey_types = {
            "small_prey" : basic_amount , 
            "medium_prey" : basic_amount*2, 
            "large_prey" : basic_amount*3, 
            "huge_prey" : basic_amount*4
        }

        if not self.success and "hunting" in patrol.patrol_event.tags:
            cancel_tags = ["no_fail_prey", "poison_clan", "death", "disaster", "multi_deaths", "no_body",
                           "cruel_season", "gone", "multi_gone", "disaster_gone"]
            relevant_patrol_tags = [tag for tag in patrol.patrol_event.tags if tag in cancel_tags]
            if len(relevant_patrol_tags) == 0:
                amount = int(PREY_REQUIREMENT["warrior"] * len(self.patrol_cats) / 1.5)
                if "fantastic hunter" in self.patrol_skills:
                    amount = int(amount * (HUNTER_BONUS["fantastic hunter"] / 10 + 1))
                elif "great hunter" in self.patrol_skills:
                    amount = int(amount * (HUNTER_BONUS["great hunter"] / 10 + 1))
                elif "good hunter" in self.patrol_skills:
                    amount = int(amount * (HUNTER_BONUS["good hunter"] / 10 + 1))
                print(f" -- FRESHKILL: added {amount} fail-prey")
                game.clan.freshkill_pile.add_freshkill(amount)
                if len(patrol.patrol_cats) == 1:
                    self.results_text.append(f"{self.patrol_leader_name} still manages to bring home some amount of prey.")
                else:
                    self.results_text.append(f"The patrol still manages to bring home some amount of prey.")
            return

        prey_amount_per_cat = 0
        total_amount = 0

        # check what kind of prey type this succeeded patrol event has
        prey_size = None
        for prey_type, amount in prey_types.items():
            current_tag = prey_type + str(outcome_nr)
            if not outcome_nr:
                current_tag = prey_type + '0'
            prey_size = prey_type.split('_')[0]
            if current_tag in patrol.patrol_event.tags or prey_type in patrol.patrol_event.tags:
                prey_amount_per_cat = amount
                break

        for cat in self.patrol_cats:
            total_amount += prey_amount_per_cat
            # add bonus of certain skills
            if cat.skill in Cat.skill_groups["hunt"]:
                total_amount += HUNTER_EXP_BONUS[cat.experience_level] * HUNTER_BONUS[cat.skill]

        # add additional bonus of certain skills
        if "fantastic hunter" in self.patrol_skills:
            total_amount = int(total_amount * (HUNTER_BONUS["fantastic hunter"] / 10 + 1))
        elif "great hunter" in self.patrol_skills:
            total_amount = int(total_amount * (HUNTER_BONUS["great hunter"] / 10 + 1))
        elif "good hunter" in self.patrol_skills:
            total_amount = int(total_amount * (HUNTER_BONUS["good hunter"] / 10 + 1))

        if game.clan.game_mode != "classic":
            game.clan.freshkill_pile.add_freshkill(total_amount)
            if total_amount > 0:
                if len(patrol.patrol_cats) == 1:
                    self.results_text.append(f"{patrol.patrol_leader_name} brings back a {prey_size} amount of prey.")
                else:
                    self.results_text.append(f"Each cat brings back a {prey_size} amount of prey.")

    def handle_clan_relations(self, difference, antagonize, outcome):
        """
        relations with other clans
        """
        if "other_clan" in self.patrol_event.tags:
            other_clan = patrol.other_clan
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
            self.results_text.append(f"Relations with {other_clan} have {insert}.")

    def handle_mentor_app_pairing(self):
        for cat in self.patrol_cats:
            if Cat.fetch_cat(cat.mentor) in self.patrol_cats:
                cat.patrol_with_mentor += 1

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
        all_cats = list(filter(lambda c: not c.dead and not c.outside, Cat.all_cats.values()))
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
        other_cat_ids = [cat.ID for cat in self.patrol_other_cats]

        if "clan_to_p_l" in self.patrol_event.tags:
            # whole clan gains relationship towards p_l
            cats_to = [p_l_id]
            cats_from = all_cats

        elif "clan_to_r_c" in self.patrol_event.tags:
            if self.patrol_fail_stat_cat or self.patrol_win_stat_cat:
                # whole clan gains relationship towards s_c
                cats_to = [s_c_id]
                cats_from = all_cats
            else:
                cats_to = [r_c_id]
                cats_from = all_cats

        elif "clan to patrol" in self.patrol_event.tags:
            # whole clan gains relationship towards patrol, the cats IN the patrol do not gain this relationship value
            cats_to = cat_ids
            cats_from = all_cats

        elif "patrol_to_r_c" in self.patrol_event.tags:
            if self.patrol_fail_stat_cat or self.patrol_win_stat_cat:
                cats_to = [s_c_id]
                cats_from = self.patrol_cats
            else:
                # whole clan gains relationship towards r_c
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


class PatrolEvent():

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
                 relationship_constraint=None):
        self.patrol_id = patrol_id
        self.biome = biome or "Any"
        self.season = season or "Any"
        self.tags = tags
        self.intro_text = intro_text
        self.decline_text = decline_text
        self.chance_of_success = chance_of_success  # out of 100
        self.exp = exp
        self.win_skills = win_skills
        self.win_trait = win_trait
        self.fail_skills = fail_skills
        self.fail_trait = fail_trait
        self.min_cats = min_cats
        self.max_cats = max_cats
        self.antagonize_text = antagonize_text
        self.antagonize_fail_text = antagonize_fail_text

        # if someone needs a empty list, don't make it as a default parameter
        # otherwise all instances of this class will use the same list

        if success_text:
            self.success_text = success_text
        else:
            self.success_text = []

        if fail_text:
            self.fail_text = fail_text
        else:
            self.fail_text = []

        if history_text:
            self.history_text = history_text
        else:
            history_text = []

        if relationship_constraint:
            self.relationship_constraint = relationship_constraint
        else:
            self.relationship_constraint = []


# ---------------------------------------------------------------------------- #
#                              GENERAL INFORMATION                             #
# ---------------------------------------------------------------------------- #

"""
    hunting patrols - "hunting", "small_prey", "medium_prey", "large_prey", "huge_prey"

    training patrols - "training",

    border patrols - "border", "other_clan", "reputation",

    med patrols - "med_cat", "herb", "random_herbs", "many_herbs#"
            
    new cat tags - ("kittypet" in the patrol ID will make the cat a kittypet no matter what)                                                              
    "new_cat", "new_cat_med", "new_cat_queen", "new_cat_female", "new_cat_tom", "new_cat_neutered",
    "new_cat_elder", "new_cat_majorinjury", "new_cat_kit", "new_cat_kits", "new_cat_newborn",
    "new_cat_apprentice", "new_cat_adult",

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
-- success/fail outcomes -- 
    Success[0] is the most common
    Success[1] is slightly rarer
    Success[2] is if win skill is applicable
    Success[3] is if win trait is applicable

    Fail text[0] is unscathed fail 1
    Fail text[1] is unscathed 2, fail skill or fail traits
    Fail text[2] is death
    Fail text[3] is scar/injury
    Fail text[4] is death for s_c
    fail text[5] is scar/injury for s_c
    fail text[6] is alt leader death

    History text[0] is scar text
    History text[1] is death text for normal cats
    History text[2] is death text for leaders
        
-- PATROL ABBREVIATIONS --
    Clan name - c_n
    Other clan name - o_c_n
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
        patrol, and also works with "two_apprentices" (or any of the higher numbered apprentice specifers) and "apprentice".

        "warrior" is used to specify that the patrol should only trigger with at least 1 warrior in it. 
        "no_app" is for when no apps should be on the patrol

    - RELATIONSHIP TAGS -
        I think all of these can be used together. the tag for which relationships are increased should ALSO be used
        # whole clan gains relationship towards p_l - "clan_to_p_l"
        # whole clan gains relationship towards s_c - "clan_to_r_c" (triggers to be s_c if s_c is present)
        # whole clan gains relationship towards r_c - "clan_to_r_c"
        # patrol gains relationship towards p_l - "patrol_to_p_l"
        # patrol gains relationship towards s_c - "patrol_to_r_c" (triggers to be s_c if s_c is present)
        # patrol gains relationship towards r_c - "patrol_to_r_c"
        # "p_l_to_r_c" is for specifically pl and rc gaining relationship with EACH OTHER
        # two apps gain relationship towards each other - "rel_two_apps"
        # whole clan gains relationship towards patrol - "clan_to_patrol"
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
        
        "sacrificial" is for fail outcomes where a cat valiantly sacrifices themselves for the clan 
        (such as the single cat big dog patrol) this will give the tagged for group ("clan_to_r_c", "patrol_to_r_c", ect) 
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

patrol = Patrol()
