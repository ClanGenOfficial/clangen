#!/usr/bin/env python3
# -*- coding: ascii -*-
from random import choice, randint, choices
from math import floor

from scripts.clan import HERBS
from scripts.game_structure.game_essentials import *
from scripts.cat.names import *
from scripts.cat.cats import *
from scripts.cat.pelts import *
from scripts.clan_resources.freshkill import PREY_REQUIREMENT, HUNTER_EXP_BONUS, HUNTER_BONUS

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
        self.patrol_stat_cat = None
        self.app1_name = None
        self.app2_name = None
        self.app3_name = None
        self.app4_name = None
        self.app5_name = None
        self.app6_name = None
        self.other_clan = None
        self.experience_levels = []

    def add_patrol_cats(self, patrol_cats):
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
        # sets leader as patrol leader
        elif game.clan.leader in self.patrol_cats:
            self.patrol_leader = game.clan.leader
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

        self.other_clan = choice(game.clan.all_clans)

    def get_possible_patrols(self, current_season, biome, all_clans, patrol_type,
                             game_setting_disaster=game.settings['disasters']):
        # ---------------------------------------------------------------------------- #
        #                                LOAD RESOURCES                                #
        # ---------------------------------------------------------------------------- #
        biome = biome.lower()
        season = current_season.lower()
        resource_dir = "resources/dicts/patrols/"
        biome_dir = f"{biome}/"
        h = "hunting/"
        t = "training/"
        b = "border/"
        m = "med/"
        leaf = f"{season}"

        # HUNTING #
        HUNTING_SZN = None
        with open(f"{resource_dir}{biome_dir}{h}{leaf}.json", 'r', encoding='ascii') as read_file:
            HUNTING_SZN = ujson.loads(read_file.read())
        HUNTING = None
        with open(f"{resource_dir}{biome_dir}{h}any.json", 'r', encoding='ascii') as read_file:
            HUNTING = ujson.loads(read_file.read())
        # BORDER #
        BORDER_SZN = None
        with open(f"{resource_dir}{biome_dir}{b}{leaf}.json", 'r', encoding='ascii') as read_file:
            BORDER_SZN = ujson.loads(read_file.read())
        BORDER = None
        with open(f"{resource_dir}{biome_dir}{b}any.json", 'r', encoding='ascii') as read_file:
            BORDER = ujson.loads(read_file.read())
        # TRAINING #
        TRAINING_SZN = None
        with open(f"{resource_dir}{biome_dir}{t}{leaf}.json", 'r', encoding='ascii') as read_file:
            TRAINING_SZN = ujson.loads(read_file.read())
        TRAINING = None
        with open(f"{resource_dir}{biome_dir}{t}any.json", 'r', encoding='ascii') as read_file:
            TRAINING = ujson.loads(read_file.read())
        # MED #
        MEDCAT_SZN = None
        with open(f"{resource_dir}{biome_dir}{m}{leaf}.json", 'r', encoding='ascii') as read_file:
            MEDCAT_SZN = ujson.loads(read_file.read())
        MEDCAT = None
        with open(f"{resource_dir}{biome_dir}{m}any.json", 'r', encoding='ascii') as read_file:
            MEDCAT = ujson.loads(read_file.read())
        # NEW CAT #
        NEW_CAT = None
        with open(f"{resource_dir}new_cat.json", 'r', encoding='ascii') as read_file:
            NEW_CAT = ujson.loads(read_file.read())
        NEW_CAT_HOSTILE = None
        with open(f"{resource_dir}new_cat_hostile.json", 'r', encoding='ascii') as read_file:
            NEW_CAT_HOSTILE = ujson.loads(read_file.read())
        NEW_CAT_WELCOMING = None
        with open(f"{resource_dir}new_cat_welcoming.json", 'r', encoding='ascii') as read_file:
            NEW_CAT_WELCOMING = ujson.loads(read_file.read())
        # OTHER CLAN #
        OTHER_CLAN = None
        with open(f"{resource_dir}other_clan.json", 'r', encoding='ascii') as read_file:
            OTHER_CLAN = ujson.loads(read_file.read())
        OTHER_CLAN_ALLIES = None
        with open(f"{resource_dir}other_clan_allies.json", 'r', encoding='ascii') as read_file:
            OTHER_CLAN_ALLIES = ujson.loads(read_file.read())
        OTHER_CLAN_HOSTILE = None
        with open(f"{resource_dir}other_clan_hostile.json", 'r', encoding='ascii') as read_file:
            OTHER_CLAN_HOSTILE = ujson.loads(read_file.read())

        DISASTER = None
        with open(f"{resource_dir}disaster.json", 'r', encoding='ascii') as read_file:
            DISASTER = ujson.loads(read_file.read())

        possible_patrols = []
        final_patrols = []
        patrol_size = len(self.patrol_cats)
        reputation = game.clan.reputation
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

        possible_patrols.extend(self.generate_patrol_events(HUNTING))
        possible_patrols.extend(self.generate_patrol_events(HUNTING_SZN))
        possible_patrols.extend(self.generate_patrol_events(BORDER))
        possible_patrols.extend(self.generate_patrol_events(BORDER_SZN))
        possible_patrols.extend(self.generate_patrol_events(TRAINING))
        possible_patrols.extend(self.generate_patrol_events(TRAINING_SZN))
        possible_patrols.extend(self.generate_patrol_events(MEDCAT))
        possible_patrols.extend(self.generate_patrol_events(MEDCAT_SZN))

        if game_setting_disaster:
            dis_chance = int(random.getrandbits(3)) # disaster patrol chance
            if dis_chance == 1:
                possible_patrols.extend(self.generate_patrol_events(DISASTER))

        # new cat patrols
        if chance == 1:
            if welcoming_rep:
                possible_patrols.extend(self.generate_patrol_events(NEW_CAT_WELCOMING))
            elif neutral_rep:
                possible_patrols.extend(self.generate_patrol_events(NEW_CAT))
            elif hostile_rep:
                possible_patrols.extend(self.generate_patrol_events(NEW_CAT_HOSTILE))

        # other clan patrols
        if other_clan_chance == 1:
            if clan_neutral:
                possible_patrols.extend(self.generate_patrol_events(OTHER_CLAN))
            elif clan_allies:
                possible_patrols.extend(self.generate_patrol_events(OTHER_CLAN_ALLIES))
            elif clan_hostile:
                possible_patrols.extend(self.generate_patrol_events(OTHER_CLAN_HOSTILE))

        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        for patrol in possible_patrols:

            # correct button check
            if 'general' not in patrol.tags and patrol_type != 'general':
                if 'hunting' not in patrol.tags and patrol_type == 'hunting':
                    continue
                elif 'border' not in patrol.tags and patrol_type == 'border':
                    continue
                elif 'training' not in patrol.tags and patrol_type == 'training':
                    continue
                elif 'med_cat' not in patrol.tags and patrol_type == 'med':
                    continue

            if patrol_size < patrol.min_cats:
                continue
            if patrol_size > patrol.max_cats:
                continue

            # makes sure that an apprentice is present if the apprentice tag is
            if "apprentice" in patrol.tags:
                if "apprentice" not in self.patrol_statuses and "medicine cat apprentice" not in self.patrol_statuses:
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
                med = ["medicine cat", "medicine cat apprentice"]
                if not any(status in self.patrol_statuses for status in med):
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

            # making sure related cats don't accidentally go on romantic patrols together
            if "romantic" in patrol.tags:
                if ("rel_two_apps" and "two_apprentices") in patrol.tags and len(self.patrol_apprentices) >= 2:
                    if not self.patrol_apprentices[0].is_potential_mate(self.patrol_apprentices[1],
                                                                        for_love_interest=True):
                        continue
                else:
                    if not self.patrol_random_cat.is_potential_mate(self.patrol_leader, for_patrol=True):
                        continue
            final_patrols.append(patrol)
        for event in final_patrols:
        return final_patrols

    def generate_patrol_events(self, patrol_dict):
        all_patrol_events = []
        for patrol in patrol_dict:
            patrol_event = PatrolEvent(
                patrol_id=patrol["patrol_id"],
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
                antagonize_text=patrol["antagonize_text"],
                antagonize_fail_text=patrol["antagonize_fail_text"],
                history_text=patrol["history_text"] if "history_text" in patrol else [])

            all_patrol_events.append(patrol_event)

        return all_patrol_events

    def calculate_success(self, antagonize=False):
        if self.patrol_event is None:
            return
        antagonize = antagonize
        success_text = self.patrol_event.success_text
        fail_text = self.patrol_event.fail_text
        gm_modifier = 1
        if game.clan.game_mode == "classic":
            gm_modifier = 1
        elif game.clan.game_mode == "expanded":
            gm_modifier = 2
        elif game.clan.game_mode == "cruel season":
            gm_modifier = 3
        # initially setting stat_cat
        if self.patrol_event.win_skills is not None and self.patrol_event.win_trait is not None:
            if cat_class.skill in self.patrol_event.win_skills or cat_class.trait in self.patrol_event.win_trait:
                self.patrol_stat_cat = cat_class
        # if patrol contains cats with autowin skill, chance of success is high
        # otherwise it will calculate the chance by adding the patrolevent's chance of success plus the patrol's total exp
        chance = self.patrol_event.chance_of_success + int(
            self.patrol_total_experience / (2 * gm_modifier))
        if self.patrol_event.win_skills is not None:
            if set(self.patrol_skills).isdisjoint(
                    self.patrol_event.win_skills):
                chance = chance + 50
                if self.patrol_stat_cat is not None:
                    if "excellent" in self.patrol_stat_cat.skill:
                        chance = chance + 10
                    elif "fantastic" in self.patrol_stat_cat.skill:
                        chance = chance + 20
        if self.patrol_event.win_trait is not None:
            if set(self.patrol_traits).isdisjoint(
                    self.patrol_event.win_trait):
                chance = chance + 50

        # resetting stat_cat to fails
        if self.patrol_event.fail_trait is not None:
            if set(self.patrol_traits).isdisjoint(
                    self.patrol_event.fail_trait):
                chance = chance - 50

        c = randint(0, 100)
        outcome = int(random.getrandbits(4))
        
        # ---------------------------------------------------------------------------- #
        #                                   SUCCESS                                    #
        # ---------------------------------------------------------------------------- #
        """
        n = the outcome chosen
        rare and common denote the outcome chance
        """
        rare = False
        common = False
        if outcome >= 11:
            rare = True
        else:
            common = True

        if c < chance:
            self.success = True
            # this adds the stat cat (if there is one)
            if self.patrol_stat_cat is not None:
                if self.patrol_stat_cat.trait in self.patrol_event.win_trait:
                    outcome = 3
                elif self.patrol_stat_cat.skill in self.patrol_event.win_skills:
                    outcome = 2
            else:
                if rare and len(success_text) >= 2 and success_text[1] is not None:
                    outcome = 1
                else:
                    if success_text[0] is not None:
                        outcome = 0
                    else:
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
                        self.handle_clan_relations(difference=int(-2))
                    else:
                        self.handle_clan_relations(difference=int(1))
                elif "new_cat" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_reputation(-10)
                    else:
                        self.handle_reputation(10)
            self.handle_mentor_app_pairing()
            self.handle_relationships()
            if game.clan.game_mode != 'classic' and not antagonize:
                self.handle_herbs(outcome)
            self.final_success = self.patrol_event.success_text[outcome]
            if antagonize:
                self.antagonize = self.patrol_event.antagonize_text

        # ---------------------------------------------------------------------------- #
        #                                   FAILURE                                    #
        # ---------------------------------------------------------------------------- #
        else:
            self.success = False

            # unscathed or not
            unscathed = False
            u = int(random.getrandbits(4))
            if u >= 10:
                unscathed = True
            else:
                unscathed = False

            # pick stat cat
            if self.patrol_event.fail_skills is not None and self.patrol_event.fail_trait is not None:
                for cat in self.patrol_cats:
                    if cat.skill in self.patrol_event.fail_skills or cat.trait in self.patrol_event.fail_trait:
                        self.patrol_stat_cat = cat

            outcome = 0
            if self.patrol_stat_cat is not None and len(fail_text) > 1:
                if rare and unscathed and fail_text[1] is not None:
                    outcome = 1
                elif common and not unscathed and len(fail_text) > 5 and fail_text[5] is not None:
                    outcome = 5
                elif rare and not unscathed and len(fail_text) > 4 and fail_text[4] is not None:
                    outcome = 4
                elif fail_text[1] is None:
                    outcome = 5
                elif fail_text[5] is None:
                    outcome = 1
                else:
                    outcome = 4
            elif len(fail_text) >= 7 and fail_text[6] is not None and self.patrol_leader == game.clan.leader:
                if not unscathed:
                    outcome = 6
            elif common and len(fail_text) >= 4 and fail_text[3] is not None:
                outcome = 3
            elif rare and len(fail_text) >= 3 and fail_text[2] is not None:
                outcome = 2
            elif fail_text[0] is None:
                if len(fail_text) >= 4 and fail_text[3] is not None:
                    outcome = 3
                elif len(fail_text) >= 3 and fail_text[2] is not None:
                    outcome = 2
            elif rare and len(fail_text) >= 7 and fail_text[6] is not None and self.patrol_leader == game.clan.leader:
                outcome = 6

            if outcome == 2:
                self.handle_deaths(self.patrol_random_cat)
            elif outcome == 4:
                self.handle_deaths(self.patrol_stat_cat)
            elif outcome == 6:
                self.handle_deaths(self.patrol_leader)
            elif outcome == 3 or outcome == 5:
                if game.clan.game_mode == 'classic':
                    self.handle_scars(outcome)
                else:
                    self.handle_conditions(outcome)
            if self.patrol_event.tags is not None:
                if "other_clan" in self.patrol_event.tags:
                    if antagonize:
                        self.handle_clan_relations(difference=int(-1))
                    else:
                        self.handle_clan_relations(difference=int(-1))
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

        if not antagonize:
            self.handle_prey(outcome)


    def results(self):
        text = "<br>".join(self.results_text)
        self.results_text.clear()
        return text

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

    def handle_deaths(self, cat):
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
            if len(self.patrol_event.fail_text) > 4 and self.final_fail == self.patrol_event.fail_text[4]:
                self.results_text.append(f"{self.patrol_stat_cat.name} died.")
                self.patrol_stat_cat.die(body)
            else:
                self.results_text.append(f"{self.patrol_random_cat.name} has been lost.")
                self.patrol_random_cat.gone()
                self.patrol_random_cat.grief(body=False)

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
            cat = self.patrol_random_cat
        elif outcome == 5:
            cat = self.patrol_stat_cat

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
            if "scar" in self.patrol_event.tags:
                cat = None
                if outcome == 3:
                    cat = self.patrol_random_cat
                elif outcome == 5:
                    cat = self.patrol_stat_cat
                if len(self.patrol_random_cat.scars) < 4:
                    self.patrol_random_cat.scars.append(choice(
                        [choice(scars1)]))
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

        for x in range(len(no_herbs_tags)):
            if f"no_herbs{x}" in patrol.patrol_event.tags and outcome == x:
                return

        for x in range(len(many_herbs_tags)):
            large_amount = None
            if f"many_herbs{x}" in patrol.patrol_event.tags and outcome == x:
                large_amount = 5

        if "random_herbs" in patrol.patrol_event.tags:
            number_of_herb_types = choices([1, 2, 3], [5, 3, 1], k=1)
            herbs_picked = choices(HERBS, k=number_of_herb_types[0])
            for herb in herbs_picked:
                herbs_gotten.append(str(herb).replace('_', ' '))
                if not large_amount:
                    amount_gotten = choices([1, 2, 3], [1, 3, 2], k=1)
                    if herb in game.clan.herbs.keys():
                        game.clan.herbs[herb] += amount_gotten[0] * len(patrol.patrol_cats)
                    else:
                        game.clan.herbs.update({herb: amount_gotten[0] * len(patrol.patrol_cats)})
                else:
                    if herb in game.clan.herbs.keys():
                        game.clan.herbs[herb] += large_amount * len(patrol.patrol_cats)
                    else:
                        game.clan.herbs.update({herb: large_amount})
        elif "herb" in patrol.patrol_event.tags:
            for tag in patrol.patrol_event.tags:
                if tag in HERBS:
                    herbs_gotten.append(str(tag).replace('_', ' '))
                    if not large_amount:
                        amount_gotten = choices([1, 2, 3], [1, 3, 2], k=1)
                        if tag in game.clan.herbs.keys():
                            game.clan.herbs[tag] += amount_gotten[0] * len(patrol.patrol_cats)
                        else:
                            game.clan.herbs.update({tag: amount_gotten[0] * len(patrol.patrol_cats)})
                    else:
                        if tag in game.clan.herbs.keys():
                            game.clan.herbs[tag] += large_amount * len(patrol.patrol_cats)
                        else:
                            game.clan.herbs.update({tag: large_amount * len(patrol.patrol_cats)})
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
        """Handle the amount of prey which was caught and add it to the freshkill pile of the clan."""
        prey_types = {
            "small_prey" : PREY_REQUIREMENT["warrior"], 
            "medium_prey" : PREY_REQUIREMENT["warrior"]*2 , 
            "large_prey" : PREY_REQUIREMENT["warrior"]*3, 
            "huge_prey" : PREY_REQUIREMENT["warrior"]*4
        }

        if not self.success and "hunting" in patrol.patrol_event.tags:
            cancel_tags = ["no_fail_prey", "poison_clan", "death", "disaster", "multi_deaths", "no_body", "cruel_season", "gone", "multi_gone", "disaster_gone"]
            relevant_patrol_tags = [tag for tag in patrol.patrol_event.tags if tag in cancel_tags]
            if len(relevant_patrol_tags) == 0:
                amount = int(PREY_REQUIREMENT["warrior"] * len(self.patrol_cats) / 2)
                game.clan.freshkill_pile.add_freshkill(amount)
                self.results_text.append(f"The patrol still manages to catch some amount of prey.")
            return

        prey_amount_per_cat = 0
        total_amount = 0

        # check what kind of prey type this succeeded patrol event has
        prey_size = None
        for prey_type, amount in prey_types.items():
            current_tag = prey_type + str(outcome_nr)
            prey_size = prey_type.split('_')[0]
            if current_tag in patrol.patrol_event.tags or prey_type in patrol.patrol_event.tags:
                prey_amount_per_cat = amount
                break

        for cat in self.patrol_cats:
            total_amount += prey_amount_per_cat
            # add bonus of certain traits
            if cat.trait in Cat.skill_groups["hunt"]:
                total_amount += HUNTER_EXP_BONUS[cat.experience_level] * HUNTER_BONUS[cat.trait]

        # add additional bonus of certain traits
        if "fantastic_hunter" in self.patrol_skills:
            total_amount = total_amount * (HUNTER_BONUS["fantastic_hunter"] / 10)
        elif "great_hunter" in self.patrol_skills:
            total_amount = total_amount * (HUNTER_BONUS["great_hunter"] / 10)
        elif "good_hunter" in self.patrol_skills:
            total_amount = total_amount * (HUNTER_BONUS["good_hunter"] / 10)

        if game.clan.game_mode != "classic":
            game.clan.freshkill_pile.add_freshkill(total_amount)
            if total_amount > 0:
                self.results_text.append(f"Each cat catches a {prey_size} amount of prey.")

    def handle_clan_relations(self, difference):
        """
        relations with other clans
        """
        if "other_clan" in self.patrol_event.tags:
            other_clan = patrol.other_clan
            change_clan_relations(other_clan, difference)
            if difference > 0 and self.patrol_event.patrol_id != "gen_bord_otherclan3":
                insert = "improved"
            else:
                insert = "worsened"
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
        sc_rc = []
        if self.patrol_stat_cat is not None:
            s_c_id = self.patrol_stat_cat.ID
            sc_rc = [self.patrol_stat_cat, self.patrol_random_cat]
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

        elif "clan_to_r_c" in self.patrol_event.tags and self.patrol_stat_cat is not None:
            # whole clan gains relationship towards s_c
            cats_to = [s_c_id]
            cats_from = all_cats

        elif "patrol_to_r_c" in self.patrol_event.tags:
            # whole clan gains relationship towards r_c
            cats_to = [r_c_id]
            cats_from = self.patrol_cats

        elif "patrol_to_p_l" in self.patrol_event.tags:
            # patrol gains relationship towards p_l
            cats_to = [p_l_id]
            cats_from = self.patrol_cats

        elif "patrol_to_r_c" in self.patrol_event.tags and self.patrol_stat_cat is not None:
            # patrol gains relationship towards s_c
            cats_to = [s_c_id]
            cats_from = self.patrol_cats

        elif "patrol_to_r_c" in self.patrol_event.tags:
            # patrol gains relationship towards r_c
            cats_to = [r_c_id]
            cats_from = self.patrol_cats

        elif "rel_two_apps" in self.patrol_event.tags:
            # two apps gain relationship towards each other
            cats_to = app_ids
            cats_from = self.patrol_apprentices

        elif "clan to patrol" in self.patrol_event.tags:
            # whole clan gains relationship towards patrol, the cats IN the patrol do not gain this relationship value
            cats_to = cat_ids
            cats_from = all_cats

        elif "p_l_to_r_c" in self.patrol_event.tags:
            # p_l gains relationship with r_c and vice versa
            cats_to = pl_rc_ids
            cats_from = pl_rc

        elif "s_c to r_c" in self.patrol_event.tags:
            # s_c gains relationship with r_c and vice versa
            cats_to = sc_rc_ids
            cats_from = sc_rc

        elif "rel_patrol" in self.patrol_event.tags:
            # whole patrol gains relationship with each other
            cats_to = cat_ids
            cats_from = self.patrol_cats

        else:
            # whole patrol gains relationship with each other
            # same as last one, just makes this happen if no other rel tags are added
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

    def add_new_cats(self, litter_choice):
        tags = self.patrol_event.tags
        litter_choice = litter_choice
        if "new_cat" in tags:
            if "new_cat_majorinjury" in tags and game.clan.game_mode != 'classic':
                major_injury = True
            else:
                major_injury = False
            if "new_cat_kit" in tags:  # new kit
                backstory_choice = choice(['abandoned2', 'abandoned1', 'abandoned3'])
                if backstory_choice == 'abandoned2':
                    kittypet = True
                else:
                    kittypet = False
                created_cats = self.create_new_cat(loner=False, loner_name=False, kittypet=kittypet,
                                                   kit=True, backstory=backstory_choice)
                new_cat = created_cats[0]

            elif "new_cat_adult" in tags:
                if "kittypet" in self.patrol_event.patrol_id:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True, kit=False,
                                                       litter=False,
                                                       relevant_cat=None,
                                                       backstory=choice(['kittypet1', 'kittypet2']))
                    new_cat = created_cats[0]
                    # add litter if the kits text is rolled
                    if litter_choice:
                        new_backstory = 'outsider_roots2'
                        created_cats.extend(self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory,
                                                           litter=True, relevant_cat=new_cat))
                    if major_injury:
                        new_cat.get_injured("broken bone")
                else:  # new loner
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor'])
                    created_cats = self.create_new_cat(loner=True, kittypet=False, backstory=new_backstory)
                    new_cat = created_cats[0]
                    # add litter if the kits text is rolled
                    if litter_choice:
                        new_backstory = 'outsider_roots2'
                        created_cats.extend(self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory,
                                                           litter=True, relevant_cat=new_cat))
                    if major_injury:
                        new_cat.get_injured("broken bone")

            elif "new_cat_med" in tags:  # new med cat
                new_backstory = choice(['medicine_cat', 'disgraced', 'loner1', 'loner2'])
                created_cats = self.create_new_cat(loner=True, loner_name=True, kittypet=False, kit=False, litter=False,
                                                   med=True,
                                                   backstory=new_backstory)
                new_cat = created_cats[0]
                new_cat.skill = choice(['good healer', 'great healer', 'fantastic healer'])
                # add litter if the kits text is rolled
                if litter_choice:
                    new_backstory = 'outsider_roots2'
                    created_cats.extend(self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory,
                                                       litter=True, relevant_cat=new_cat))
            elif "new_cat_queen" in tags:
                created_cats = []
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet is True:
                    new_backstory = choice(['kittypet1', 'kittypet2'])
                    created_cats.extend(self.create_new_cat(loner=False, loner_name=True, kittypet=True, queen=True,
                                                       backstory=new_backstory))
                    new_cat = created_cats[0]
                    if game.clan.game_mode != 'classic':
                        new_cat.get_injured("recovering from birth")
                else:
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor'])
                    created_cats.extend(self.create_new_cat(loner=True, loner_name=True, kittypet=False, queen=True,
                                                       backstory=new_backstory))
                    new_cat = created_cats[0]
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
                    new_backstory = choice(['kittypet1', 'kittypet2'])
                    created_cats.extend(self.create_new_cat(loner=False, loner_name=True, kittypet=True, queen=True,
                                                       backstory=new_backstory))
                    new_cat = created_cats[0]
                    new_cat.outside = True
                    new_cat.dead = True
                else:
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor'])
                    created_cats.extend(self.create_new_cat(loner=True, loner_name=True, kittypet=False, queen=True,
                                                       backstory=new_backstory))
                    new_cat = created_cats[0]
                    new_cat.outside = True
                    new_cat.dead = True
                    new_cat.thought = "Is so very grateful that their kits survived"
                if "new_cat_newborn" in tags:
                    created_cats.extend(self.create_new_cat(loner=False, loner_name=True, backstory='orphaned',
                                                       litter=True, age='newborn', relevant_cat=new_cat))
                else:
                    created_cats.extend(self.create_new_cat(loner=False, loner_name=True, backstory='orphaned',
                                                       litter=True, relevant_cat=new_cat))

            elif "new_cat_apprentice" in tags:
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True,
                                                       age='young', backstory=choice(['kittypet1', 'kittypet2']))
                    new_cat = created_cats[0]
                    if major_injury:
                        new_cat.get_injured("broken bone")
                else:
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2', 'refugee',
                                            'tragedy_survivor'])
                    created_cats = self.create_new_cat(loner=True, loner_name=True, kittypet=False,
                                                       backstory=new_backstory,
                                                       age='young')
                    new_cat = created_cats[0]
                    if major_injury:
                        new_cat.get_injured("broken bone")
                    new_cat.update_mentor()

            elif "new_cat_elder" in tags:
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True, age='old',
                                                       backstory=choice(['kittypet1', 'kittypet2']))
                    new_cat = created_cats[0]
                    if major_injury:
                        new_cat.get_injured("broken bone")
                else:  # new loner
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor'])
                    created_cats = self.create_new_cat(loner=True, kittypet=False, backstory=new_backstory, age='old')
                    new_cat = created_cats[0]
                    if major_injury:
                        new_cat.get_injured("broken bone")

            else:
                kittypet = choice([True, False])
                if "kittypet" in self.patrol_event.patrol_id:
                    kittypet = True
                if kittypet is True:  # new kittypet
                    created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True,
                                                       backstory=choice(['kittypet1', 'kittypet2']))
                    new_cat = created_cats[0]
                    if major_injury:
                        new_cat.get_injured("broken bone")
                else:  # new loner
                    new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                            'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                            'tragedy_survivor'])
                    created_cats = self.create_new_cat(loner=True, kittypet=False, backstory=new_backstory)
                    new_cat = created_cats[0]
                    if major_injury:
                        new_cat.get_injured("broken bone")
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
                       other_clan=None):
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
                age = randint(12, 99)

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
        a = randint(0, 1)
        for number in range(amount):
            new_cat = None
            if loner_name and a == 1:
                new_cat = Cat(moons=age, prefix=name, status=status,
                              gender=gender if gender is not None else choice(['female', 'male']),
                              backstory=backstory)
            elif loner_name:
                new_cat = Cat(moons=age, prefix=name, suffix=None, status=status,
                              gender=gender if gender is not None else choice(['female', 'male']),
                              backstory=backstory)
            else:
                new_cat = Cat(moons=age, status=status,
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
                 success_text=[],
                 fail_text=[],
                 win_skills=None,
                 win_trait=None,
                 fail_skills=None,
                 fail_trait=None,
                 min_cats=1,
                 max_cats=6,
                 antagonize_text="",
                 antagonize_fail_text="",
                 history_text=[]):
        self.patrol_id = patrol_id
        self.biome = biome or "Any"
        self.season = season or "Any"
        self.tags = tags
        self.intro_text = intro_text
        self.success_text = success_text
        self.fail_text = fail_text
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
        self.history_text = history_text

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

        TAG INFO:
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
        

        HERB TAGGING:
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
