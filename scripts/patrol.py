from random import choice, randint
from math import floor

from scripts.game_structure.game_essentials import *
from scripts.cat.names import *
from scripts.cat.cats import *
from scripts.cat.pelts import *

# ---------------------------------------------------------------------------- #
#                              PATROL CLASS START                              #
# ---------------------------------------------------------------------------- #
"""
When adding new patrols, use \n to add a paragraph break in the text
"""


class Patrol():

    def __init__(self):
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
        self.other_clan = None
        self.experience_levels = [
            'very low', 'low', 'average', 'high', 'master', 'max'
        ]

    def add_patrol_cats(self):
        self.patrol_cats.clear()
        self.patrol_names.clear()
        self.possible_patrol_leaders.clear()
        self.patrol_skills.clear()
        self.patrol_statuses.clear()
        self.patrol_traits.clear()
        self.patrol_apprentices.clear()
        self.patrol_total_experience = 0
        self.patrol_other_cats.clear()
        for cat in game.switches['current_patrol']:
            self.patrol_cats.append(cat)
            self.patrol_names.append(str(cat.name))
            if cat.status != 'apprentice':
                self.possible_patrol_leaders.append(cat)
            self.patrol_skills.append(cat.skill)
            self.patrol_statuses.append(cat.status)
            self.patrol_traits.append(cat.trait)
            self.patrol_total_experience += cat.experience
            if cat.status == 'apprentice':
                    self.patrol_apprentices.append(cat)
            game.patrolled.append(cat)
        # sets leader as patrol leader
        if game.clan.leader in self.patrol_cats:
            self.patrol_leader = game.clan.leader
        # EXCEPT IF there's a medicine cat in the patrol, then medcat is leader
        elif game.clan.medicine_cat in self.patrol_cats:
            self.patrol_leader = game.clan.medicine_cat
        else:
            if self.possible_patrol_leaders:
                self.patrol_leader = choice(self.possible_patrol_leaders)
            elif not self.possible_patrol_leaders:
                self.patrol_leader = choice(self.patrol_cats)
        self.patrol_leader_name = str(self.patrol_leader.name)
        self.patrol_random_cat = choice(self.patrol_cats)
        if self.patrol_random_cat is None:
            choice(self.patrol_apprentices)
        if self.patrol_random_cat == self.patrol_leader:
            self.patrol_random_cat = choice(self.patrol_cats)

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

        self.other_clan = choice(game.clan.all_clans)
        print(self.patrol_total_experience)

    def add_cat(self, cat):
        """Add a new cat to the patrol"""
        self.patrol_cats.append(cat)
        self.patrol_names.append(str(cat.name))
        if cat.status != 'apprentice':
            self.possible_patrol_leaders.append(cat)
        self.patrol_skills.append(cat.skill)
        self.patrol_statuses.append(cat.status)
        self.patrol_traits.append(cat.trait)
        self.patrol_total_experience += cat.experience
        game.patrolled.append(cat)

    def get_possible_patrols(self, current_season, biome, all_clans, patrol_type,
                             game_setting_disaster=game.settings['disasters']):

        possible_patrols = []
        final_patrols = []
        patrol_type = patrol_type
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
        chance = 0
        # assigning other_clan relations
        if clan_relations > 17:
            clan_allies = True
        elif clan_relations < 7:
            clan_hostile = True
        elif clan_relations in range(7, 17):
            clan_neutral = True
        other_clan_chance = 1  # this is just for separating them a bit from the other patrols, it means they can always happen
        # chance for each kind of loner event to occur
        regular_chance = int(random.getrandbits(2))
        hostile_chance = int(random.getrandbits(5))
        welcoming_chance = int(random.getrandbits(1))
        if reputation in range(1, 30):
            hostile_rep = True
            chance = hostile_chance
        elif reputation in range(31, 70):
            neutral_rep = True
            chance = regular_chance
        elif reputation in range(71, 100):
            welcoming_rep = True
            chance = welcoming_chance

        # hunting patrols
        possible_patrols.extend(self.generate_patrol_events(HUNTING))
        possible_patrols.extend(self.generate_patrol_events(HUNTING_FST))
        possible_patrols.extend(self.generate_patrol_events(HUNTING_PLN))
        possible_patrols.extend(self.generate_patrol_events(HUNTING_MTN))
        possible_patrols.extend(self.generate_patrol_events(HUNTING_BCH))
        possible_patrols.extend(self.generate_patrol_events(HUNTING_WTLND))

        # general/misc patrols
        possible_patrols.extend(self.generate_patrol_events(GENERAL))

        # deadly patrols
        if game_setting_disaster:
            possible_patrols.extend(self.generate_patrol_events(DISASTER))

        # fighting patrols
        possible_patrols.extend(self.generate_patrol_events(BORDER))
        possible_patrols.extend(self.generate_patrol_events(BORDER_FST))
        possible_patrols.extend(self.generate_patrol_events(BORDER_PLN))
        possible_patrols.extend(self.generate_patrol_events(BORDER_MTN))
        possible_patrols.extend(self.generate_patrol_events(BORDER_BCH))

        # training patrols
        possible_patrols.extend(self.generate_patrol_events(TRAINING))
        possible_patrols.extend(self.generate_patrol_events(TRAINING_FST))
        possible_patrols.extend(self.generate_patrol_events(TRAINING_PLN))
        possible_patrols.extend(self.generate_patrol_events(TRAINING_MTN))
        possible_patrols.extend(self.generate_patrol_events(TRAINING_BCH))

        # med patrols
        possible_patrols.extend(self.generate_patrol_events(MEDCAT))

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
                

        # one last check
        two_apprentices = False
        status_a = False
        status_b = False
        status_c = False
        status_d = False
        no_app = False
        mode = False
        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        for patrol in possible_patrols:
            if patrol_size >= patrol.min_cats:
                min_good = True
            elif patrol_size < patrol.min_cats:
                min_good = False
            if patrol_size <= patrol.max_cats:
                max_good = True
            elif patrol_size > patrol.max_cats:
                max_good = False
            if patrol.biome == biome:
                correct_biome = True
            elif patrol.biome == "Any":
                correct_biome = True
            else:
                correct_biome = False
            if patrol.season == current_season:
                correct_season = True
            elif patrol.season == "Any":
                correct_season = True
            else:
                correct_season = False
            # makes sure that an apprentice is present if the apprentice tag is
            if "apprentice" in patrol.tags:
                if "apprentice" not in self.patrol_statuses:
                    status_a = False
                else:
                    status_a = True
            # sets it as true if the status tag is not in bc the check no longer applies
            else:
                status_a = True
            # makes sure that the deputy is present if the deputy tag is
            if "deputy" in patrol.tags:
                if "deputy" not in self.patrol_statuses:
                    status_b = False
                else:
                    status_b = True
                    st_index = self.patrol_statuses.index("deputy")
                    self.patrol_random_cat = self.patrol_cats[st_index]
            else:
                status_b = True
            # makes sure the leader is present when the leader tag is
            if "leader" in patrol.tags:
                if "leader" not in self.patrol_statuses:
                    status_c = False
                else:
                    status_c = True
            else:
                status_c = True

            # makes sure at least one warrior is present
            if "warrior" in patrol.tags:
                if ("warrior" or "deputy" or "leader") not in self.patrol_statuses:
                    status_d = False
                else:
                    status_d = True
            else:
                status_d = True

            # makes sure no apps are present if they're not supposed to be
            # mostly for romance patrols between warriors/dumb stuff that they wouldn't involve apprentices in
            if "no_app" in patrol.tags:
                if "apprentice" in self.patrol_statuses:
                    no_app = False
                else:
                    no_app = True
            else:
                no_app = True

            # cruel season tag check
            if "cruel_season" in patrol.tags:
                if game.clan.game_mode != 'cruel_season':
                    mode = False
                else:
                    mode = True
            else:
                mode = True

            # two apprentices check
            if "two_apprentices" in patrol.tags:
                if len(self.patrol_apprentices) >= 2:
                    two_apprentices = True
                else:
                    two_apprentices = False
            else:
                two_apprentices = True

            # correct button check
            if patrol_type == 'hunting' and "hunting" in patrol.tags:
                correct_button = True
            elif patrol_type == 'hunting' and "general" in patrol.tags:
                correct_button = True
            elif patrol_type == 'border' and "border" in patrol.tags:
                correct_button = True
            elif patrol_type == 'border' and "general" in patrol.tags:
                correct_button = True
            elif patrol_type == 'training' and "training" in patrol.tags:
                correct_button = True
            elif patrol_type == 'training' and "general" in patrol.tags:
                correct_button = True
            elif patrol_type == 'med' and "med_cat" in patrol.tags:
                correct_button = True
            else:
                correct_button = False


            # one last mode check for classic
            if game.clan.game_mode == 'classic':
                if max_good and min_good and correct_season and correct_biome and status_a and status_b and status_c\
                    and status_d and no_app and two_apprentices:
                    final_patrols.append(patrol)
            # this is for all patrols that aren't classic
            else:
                if max_good and min_good and correct_season and correct_biome and status_a and status_b and status_c\
                    and status_d and correct_button and no_app and two_apprentices and mode:
                        final_patrols.append(patrol)
        
        return final_patrols   

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
                antagonize_text=patrol["antagonize_text"],
                antagonize_fail_text=patrol["antagonize_fail_text"])

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
        elif game.clan.game_mode == "cruel_season":
            gm_modifier = 3
        # initially setting stat_cat
        if self.patrol_event.win_skills is not None and self.patrol_event.win_trait is not None:
                for cat in self.patrol_cats:
                    if cat.skill in self.patrol_event.win_skills or cat.trait in self.patrol_event.win_trait:
                        self.patrol_stat_cat = cat
        # if patrol contains cats with autowin skill, chance of success is high
        # otherwise it will calculate the chance by adding the patrolevent's chance of success plus the patrol's total exp
        chance = self.patrol_event.chance_of_success + int(
            self.patrol_total_experience / (10 * gm_modifier))
        if self.patrol_event.win_skills is not None:
            if set(self.patrol_skills).isdisjoint(
                    self.patrol_event.win_skills):
                chance = 60
                if self.patrol_stat_cat is not None:
                    if "excellent" in self.patrol_stat_cat.skill:
                        chance = 80
                    elif "fantastic" in self.patrol_stat_cat.skill:
                        chance = 90
        if self.patrol_event.win_trait is not None:
            if set(self.patrol_traits).isdisjoint(
                    self.patrol_event.win_trait):
                chance = 90

        # resetting stat_cat to fails
        if self.patrol_event.fail_skills is not None and self.patrol_event.faiil_trait is not None:
                for cat in self.patrol_cats:
                    if cat.skill in self.patrol_event.fail_skills or cat.trait in self.patrol_event.fail_trait:
                        self.patrol_stat_cat = cat
        if self.patrol_event.fail_skills is not None:
            if set(self.patrol_skills).isdisjoint(
                    self.patrol_event.fail_skills):
                chance = 20
                if self.patrol_stat_cat is not None:
                    if "bad" in self.patrol_stat_cat.skill:
                        chance = 15
                    elif "awful" in self.patrol_stat_cat.skill:
                        chance = 10
        if self.patrol_event.fail_trait is not None:
            if set(self.patrol_traits).isdisjoint(
                    self.patrol_event.fail_trait):
                chance = 10
        c = randint(20, 100)
        outcome = int(random.getrandbits(4))
        print("Outcome: " + str(outcome))
        print("Clan Rel. Before: " + str(patrol.other_clan.relations))
        print("Rep. Before: " + str(game.clan.reputation))
        if c < chance:
            self.success = True
            # this adds the stat cat (if there is one)
            if self.patrol_event.win_skills is not None and self.patrol_event.win_trait is not None:
                for cat in self.patrol_cats:
                    if cat.skill in self.patrol_event.win_skills or cat.trait in self.patrol_event.win_trait:
                        self.patrol_stat_cat = cat
            if self.patrol_stat_cat is not None:
                if self.patrol_stat_cat.trait in self.patrol_event.win_trait:
                    n = 3
                elif self.patrol_stat_cat.skill in self.patrol_event.win_skills:
                    n = 2
            else:
                if outcome >= 10 and len(success_text) >= 2 and success_text[1] is not None:
                    n = 1
                else:
                    if success_text[0] is not None:
                        n = 0
                    else:
                        n = 1
            # this is specifically for new cat events that can come with kits
            litter_choice = False
            if self.patrol_event.tags is not None:
                if "kits" in self.patrol_event.tags:
                    litter_choice = choice([True, False])
                    if litter_choice == True:
                        n = 1
                    else:
                        n = 0
            self.handle_exp_gain()
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
            self.final_success = self.patrol_event.success_text[n]
            if antagonize:
                self.antagonize = self.patrol_event.antagonize_text

            print(str(self.patrol_event.patrol_id))
            print("Min cats: " + str(self.patrol_event.min_cats) + " & Max cats: " + str(self.patrol_event.max_cats))
            if antagonize is False: print(str(self.final_success) + " #: " + str(n))
            if antagonize: print(str(self.patrol_event.antagonize_text))
            print(str(self.patrol_event.biome) + " vs " + str(game.clan.biome).lower())
            print("Clan Rel. After: " + str(patrol.other_clan.relations))
            print("Rep. After: " + str(game.clan.reputation))
        else:
            self.success = False
            if self.patrol_event.fail_skills is not None and self.patrol_event.fail_trait is not None:
                for cat in self.patrol_cats:
                    if cat.skill in self.patrol_event.fail_skills or cat.trait in self.patrol_event.fail_trait:
                        self.patrol_stat_cat = cat
            if self.patrol_stat_cat is not None and len(fail_text) > 1:
                if outcome >= 11 and fail_text[1] is not None:
                    n = 1
                elif outcome <= 10 and len(fail_text) > 4 and fail_text[4] is not None:
                    n = 4
                elif fail_text[1] is None:
                    n = 4
                elif fail_text[4] is None:
                    n = 1
            elif outcome <= 10 and len(fail_text) >= 4 and fail_text[3] is not None:
                n = 3
            elif outcome >= 11 and len(fail_text) >= 3 and fail_text[2] is not None:
                n = 2
            elif fail_text[0] is None:
                if len(fail_text) >= 4 and fail_text[3] is not None:
                    n = 3
                elif len(fail_text) >= 3 and fail_text[2] is not None:
                    n = 2
            else:
                n = 0
            if n == 2 or n == 4:
                self.handle_deaths()
            elif n == 3:
                self.handle_scars()
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
                elif "disaster" in self.patrol_event.tags:
                    self.handle_deaths()
            self.handle_mentor_app_pairing()
            self.handle_relationships()
            self.final_fail = self.patrol_event.fail_text[n]
            if antagonize:
                self.antagonize_fail = self.patrol_event.antagonize_fail_text

            print(str(self.patrol_event.patrol_id))
            print("Min cats: " + str(self.patrol_event.min_cats) + " and Max cats " + str(self.patrol_event.max_cats))
            if antagonize is False: print(str(self.final_fail) + " #: " + str(n))
            if antagonize: print(str(self.patrol_event.antagonize_fail_text))
            print(str(self.patrol_event.biome) + " vs " + str(game.clan.biome).lower())
            print("Clan Rel. After: " + str(patrol.other_clan.relations))
            print("Rep. After: " + str(game.clan.reputation))

    def handle_exp_gain(self):
        gm_modifier = 1
        base_exp = 10
        patrol_exp = self.patrol_event.exp
        if game.clan.game_mode == 'classic':
            gm_modifier = gm_modifier
        elif game.clan.game_mode == 'expanded':
            gm_modifier = 3
        elif game.clan.game_mode == 'cruel_season':
            gm_modifier = 6
        if self.success:
            for cat in self.patrol_cats:
                print("EXP Before: " + str(cat.experience))
                gained_exp = ((patrol_exp + base_exp) / len(self.patrol_cats)) / gm_modifier
                cat.experience = int(cat.experience + gained_exp)
                print("After: " + str(cat.experience))

    def handle_deaths(self):
        if "death" in self.patrol_event.tags:
            if self.patrol_random_cat.status == 'leader':
                game.clan.leader_lives = int(game.clan.leader_lives) - 1
            elif len(self.patrol_event.fail_text) > 4 and self.final_fail == self.patrol_event.fail_text[4]:
                self.patrol_stat_cat.die()
            else:
                self.patrol_random_cat.die()
            if len(self.patrol_event.history_text) >= 2:
                self.patrol_random_cat.death_event.append(f'{self.patrol_event.history_text[1]}')
            else:
                self.patrol_random_cat.death_event.append(f'This cat died while patrolling.')

        elif "disaster" in self.patrol_event.tags:
            for cat in self.patrol_cats:
                cat.experience += self.patrol_event.exp
                cat.experience = min(cat.experience, 80)
                if cat.status == 'leader':
                    game.clan.leader_lives -= 10
                if len(self.patrol_event.history_text) >= 2:
                    self.patrol_random_cat.death_event.append(f'{self.patrol_event.history_text[1]}')
                else:
                    self.patrol_random_cat.death_event.append(f'This cat died while patrolling.')
                cat.die()

        elif "multi_deaths" in self.patrol_event.tags:
            cats_dying = choice([2, 3, 4])
            if cats_dying > len(self.patrol_cats):
                cats_dying = int(len(self.patrol_cats) - 1)
            for d in range(0, cats_dying):
                self.patrol_cats[d].die()

        # cats disappearing on patrol is also handled under this def for simplicity's sake
        elif "gone" in self.patrol_event.tags:
            if len(self.patrol_event.fail_text) > 4 and self.final_fail == self.patrol_event.fail_text[4]:
                self.patrol_stat_cat.die()
            else:
                self.patrol_random_cat.gone()

        elif "disaster_gone" in self.patrol_event.tags:
            for cat in self.patrol_cats:
                cat.experience += self.patrol_event.exp
                cat.experience = min(cat.experience, 80)
                cat.gone()

        elif "multi_gone" in self.patrol_event.tags:
            cats_gone = choice([2, 3, 4])
            if cats_gone > len(self.patrol_cats):
                cats_gone = int(len(self.patrol_cats) - 1)
            for g in range(0, cats_gone):
                self.patrol_cats[g].gone()
                

    def handle_scars(self):
        if self.patrol_event.tags is not None:
            if "scar" in self.patrol_event.tags:
                if self.patrol_random_cat.specialty is None:
                    self.patrol_random_cat.specialty = choice(
                        [choice(scars1),
                         choice(scars2)])
                    if len(self.patrol_event.history_text) >= 1:
                        self.patrol_random_cat.scar_event.append(
                            f'{self.patrol_event.history_text[0]}')
                    else:
                        self.patrol_random_cat.death_event.append(f'This cat gained a scar while patrolling.')
                elif self.patrol_random_cat.specialty2 is None:
                    self.patrol_random_cat.specialty2 = choice(
                        [choice(scars1),
                         choice(scars2)])
                    if len(self.patrol_event.history_text) >= 1:
                        self.patrol_random_cat.scar_event.append(
                            f'{self.patrol_event.history_text[0]}')
                    else:
                        self.patrol_random_cat.death_event.append(f'This cat gained a scar while patrolling.')
        """elif self.patrol_event.patrol_id == 904:
            if self.patrol_random_cat.specialty is None:
                self.patrol_random_cat.specialty = "SNAKE"
                self.patrol_random_cat.scar_event.append(
                    f'{self.patrol_random_cat.name} gained a scar while on patrol.')
            elif self.patrol_random_cat.specialty2 is None:
                self.patrol_random_cat.specialty2 = "SNAKE"
                self.patrol_random_cat.scar_event.append(
                    f'{self.patrol_random_cat.name} gained a scar while on patrol.')"""

    def handle_retirements(self):
        if game.settings['retirement'] and self.patrol_random_cat.status != 'leader':
            self.patrol_random_cat.status_change('elder')
            self.patrol_random_cat.scar_event.append(
                f'{self.patrol_random_cat.name} retired after being hit by a monster.')
        else:
            self.patrol_random_cat.skill = choice(
                ['paralyzed', 'blind', 'missing a leg'])
            self.patrol_random_cat.scar_event.append(
                f'{self.patrol_random_cat.name} is hit by a car and is now {self.patrol_random_cat.skill}.')

    def handle_clan_relations(self, difference):
        other_clan = patrol.other_clan
        otherclan = game.clan.all_clans.index(other_clan)
        clan_relations = int(game.clan.all_clans[otherclan].relations)
        if "other_clan" in self.patrol_event.tags:
            if patrol.success:
                clan_relations += difference
            else:
                clan_relations += difference
        game.clan.all_clans[otherclan].relations = clan_relations

    def handle_mentor_app_pairing(self):
        for cat in self.patrol_cats:
            if cat.mentor in self.patrol_cats:
                cat.patrol_with_mentor += 1

    # reputation with outsiders
    def handle_reputation(self, difference):
        reputation = game.clan.reputation
        difference = int(difference)
        if patrol.success:
            reputation += difference
        else:
            reputation += difference
        game.clan.reputation = reputation

    def handle_relationships(self):
        romantic_love = 0
        platonic_like = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0

        # change the values
        if "romantic" in self.patrol_event.tags:
            romantic_love = 5
        if "platonic" in self.patrol_event.tags:
            platonic_like = 5
        if "dislike" in self.patrol_event.tags:
            dislike = 5
        if "respect" in self.patrol_event.tags:
            admiration = 5
        if "comfort" in self.patrol_event.tags:
            comfortable = 5
        if "jealous" in self.patrol_event.tags:
            jealousy = 5
        if "trust" in self.patrol_event.tags:
            trust = 5
        
        # this is just for prints, if it's still here later, just remove it
        changed = False
        if romantic_love == 0 and platonic_like == 0 and dislike == 0 and admiration == 0 and\
        comfortable == 0 and jealousy == 0 and trust == 0:
            changed = False
        else:
            changed = True

        # affect the relationship
        all_cats = list(filter(lambda c: not c.dead and not c.outside, Cat.all_cats.values()))
        cat_ids = [cat.ID for cat in self.patrol_cats]
        r_c_id = self.patrol_random_cat.ID
        if self.patrol_stat_cat is not None:
            s_c_id = self.patrol_stat_cat.ID
        p_l_id = self.patrol_leader.ID
        app_ids = [cat.ID for cat in self.patrol_apprentices]
        other_cat_ids = [cat.ID for cat in self.patrol_other_cats]

        if "clan_to_p_l" in self.patrol_event.tags:
            # whole clan gains relationship towards p_l
            for cat in all_cats:
                relationships = list(
                    filter(lambda rel: rel.rel.cat_to.ID == p_l_id,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == p_l_id:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Respect: -" + str(admiration) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy) +
                        " /Trust: -" + str(trust)) if changed else print("No relationship change")

        elif "clan_to_r_c" in self.patrol_event.tags and self.patrol_stat_cat is not None:
            # whole clan gains relationship towards s_c
            for cat in all_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID == s_c_id,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == s_c_id:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "clan_to_r_c" in self.patrol_event.tags:
        # whole clan gains relationship towards r_c
            for cat in all_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID == r_c_id,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == r_c_id:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "patrol_to_p_l" in self.patrol_event.tags:
            # patrol gains relationship towards p_l
            for cat in self.patrol_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID == p_l_id,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == p_l_id:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "patrol_to_r_c" in self.patrol_event.tags and self.patrol_stat_cat is not None:
        # patrol gains relationship towards s_c
            for cat in self.patrol_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID == s_c_id,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == s_c_id:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "patrol_to_r_c" in self.patrol_event.tags:
        # patrol gains relationship towards r_c
            for cat in self.patrol_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID == r_c_id,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == r_c_id:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.admiration -= admiration
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "relation_two_apps" in self.patrol_event.tags:
        # two apps gain relationship towards each other
            for cat in self.patrol_apprentices:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID in app_ids,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == rel.cat_to.ID:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "clan_to_patrol" in self.patrol_event.tags:
        # whole clan gains relationship towards patrol, but the cats IN the patrol do not gain this relationship value
            for cat in all_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID in cat_ids,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID in cat_ids:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        elif "rel_patrol" in self.patrol_event.tags:
            # whole patrol gains relationship with each other
            for cat in self.patrol_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID in cat_ids,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == rel.cat_to.ID:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

        else:
        # whole patrol gains relationship with each other / same as last one, makes this one happen if no other tags are added
            for cat in self.patrol_cats:
                relationships = list(
                    filter(lambda rel: rel.cat_to.ID in cat_ids,
                        list(cat.relationships.values())))
                for rel in relationships:
                    if cat.ID == rel.cat_to.ID:
                        continue
                    if self.success:
                        rel.romantic_love += romantic_love
                        rel.platonic_like += platonic_like
                        rel.dislike -= dislike
                        rel.admiration += admiration
                        rel.comfortable += comfortable
                        rel.jealousy -= jealousy
                        rel.trust += trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: +" + str(romantic_love) +
                        " /Platonic: +" + str(platonic_like) +
                        " /Dislike: -" + str(dislike) +
                        " /Respect: +" + str(admiration) +
                        " /Comfort: +" + str(comfortable) +
                        " /Jealousy: -" + str(jealousy) +
                        " /Trust: +" + str(trust)) if changed else print("No relationship change")
                    elif not self.success:
                        rel.romantic_love -= romantic_love
                        rel.platonic_like -= platonic_like
                        rel.dislike += dislike
                        rel.comfortable -= comfortable
                        rel.jealousy += jealousy
                        if "disrespect" in self.patrol_event.tags:
                            rel.admiration -= admiration
                        if "distrust" in self.patrol_event.tags:
                            rel.trust -= trust
                        print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                        "Romantic: -" + str(romantic_love) +
                        " /Platonic: -" + str(platonic_like) +
                        " /Dislike: +" + str(dislike) +
                        " /Comfort: -" + str(comfortable) +
                        " /Jealousy: +" + str(jealousy)) if changed else print("No relationship change")

    def add_new_cats(self, litter_choice):
        if "new_cat" in self.patrol_event.tags:
            if self.patrol_event.patrol_id == "gen_gen_newkit1":  # new kit
                backstory_choice = choice(['abandoned2', 'abandoned1', 'abandoned3'])
                created_cats = self.create_new_cat(loner=False, loner_name=False, kittypet=choice([True, False]), kit=True, backstory=backstory_choice)
                
            if self.patrol_event.patrol_id in ["gen_gen_newcat1", "gen_gen_newcat3", "gen_gen_lonerchase1"]:  # new loner
                new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                        'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                        'tragedy_survivor'])
                created_cats = self.create_new_cat(loner = True, kittypet=False, backstory=new_backstory)
                new_cat = created_cats[0]
                # add litter if the kits text is rolled
                if litter_choice == True:
                    new_backstory = 'outsider_roots2'
                    created_cats = self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory, litter=True, relevant_cat=new_cat)
                    if new_cat.moons < 12:
                        new_cat.moons = 16
                
            elif self.patrol_event.patrol_id in ["gen_gen_newcat2", "gen_gen_newcat3"]:  # new kittypet
                created_cats = self.create_new_cat(loner=False, loner_name=True, kittypet=True, kit=False, litter=False, relevant_cat=None,
                backstory=choice(['kittypet1', 'kittypet2']))
                new_cat = created_cats[0]
                # add litter if the kits text is rolled
                if litter_choice == True:
                    new_backstory = 'outsider_roots2'
                    created_cats = self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory, litter=True, relevant_cat=new_cat)
                    if new_cat.moons < 12:
                        new_cat.moons = 16
                
            elif self.patrol_event.patrol_id == "gen_gen_newmed1":  # new med cat
                new_backstory = choice(['medicine_cat', 'disgraced', 'loner1', 'loner2'])
                created_cats = self.create_new_cat(loner=True, loner_name=True, kittypet=False, kit=False, litter=False, med=True,
                backstory=new_backstory)
                new_cat = created_cats[0]
                new_cat.skill = choice(['good healer', 'great healer', 'fantastic healer'])
                # add litter if the kits text is rolled
                if litter_choice == True:
                    new_backstory = 'outsider_roots2'
                    created_cats = self.create_new_cat(loner=True, loner_name=True, backstory=new_backstory, litter=True, relevant_cat=new_cat)
                
    def create_new_cat(self,
                       loner=False,
                       loner_name=False,
                       kittypet=False,
                       kit=False,
                       litter=False,
                       med=False,
                       relevant_cat=None,
                       backstory=None,
                       other_clan=None):
        name = None
        skill = None
        accessory = None
        status = "kitten"
        backstory = backstory
        other_clan = other_clan

        age = randint(0, 5)
        kp_name_chance = (1, 5)
        if not litter and not kit:
            age = randint(6, 120)
        if med:
            age = randint(16, 120)

        if (loner or kittypet) and not kit and not litter:
            if loner_name:
                if loner and kp_name_chance == 1:
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
                new_cat = Cat(moons=age, prefix=name, status=status, gender=choice(['female', 'male']), backstory=backstory)
            elif loner_name:
                new_cat = Cat(moons=age, prefix=name, suffix=None, status=status, gender=choice(['female', 'male']), backstory=backstory)
            else:
                new_cat = Cat(moons=age, status=status, gender=choice(['female', 'male']), backstory=backstory)
            if skill:
                new_cat.skill = skill
            if accessory:
                new_cat.accessory = accessory

            if (kit or litter) and relevant_cat and relevant_cat.ID in Cat.all_cats:
                new_cat.parent1 = relevant_cat.ID
                if relevant_cat.mate:
                    new_cat.parent2 = relevant_cat.mate

            #create and update relationships
            for the_cat in new_cat.all_cats.values():
                if the_cat.dead or the_cat.exiled:
                    continue
                the_cat.relationships[new_cat.ID] = Relationship(the_cat, new_cat)
                new_cat.relationships[the_cat.ID] = Relationship(new_cat, the_cat)
            new_cat.thought = 'Is looking around the camp with wonder'
            created_cats.append(new_cat)
        
        for new_cat in created_cats:
            add_siblings_to_cat(new_cat,cat_class)
            add_children_to_cat(new_cat,cat_class)
            game.clan.add_cat(new_cat)

        return created_cats

    def check_territories(self):
        hunting_claim = str(game.clan.name) + 'Clan Hunting Grounds'
        self.hunting_grounds = []
        for y in range(44):
            for x in range(40):
                claim_type = game.map_info[(x, y)][3]
                if claim_type == hunting_claim:
                    self.hunting_claim_info[(x, y)] = game.map_info[(x, y)]
                    self.hunting_grounds.append((x, y))


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
                 other_clan=None,
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
        self.other_clan = patrol.other_clan
        self.win_skills = win_skills
        self.win_trait = win_trait
        self.fail_skills = fail_skills
        self.fail_trait = fail_trait
        self.min_cats = min_cats
        self.max_cats = max_cats
        self.antagonize_text = antagonize_text
        self.antagonize_fail_text = antagonize_fail_text
        self.history_text = history_text

        """ success [0] is the most common
            success [1] is slightly rarer
            success [2] is if win skill is applicable
            success [3] is if win trait is applicable

            fail text [0] is unscathed fail 1
            fail text [1] is unscathed 2 - fail skill or fail traits
            fail text [2] is death
            fail text [3] is scar"""

        tags = [
            "hunting", "other_clan", "fighting", "death", "scar", "new_cat", 
            "npc", "retirement", "injury", "illness", "romantic", "platonic", 
            "comfort", "respect", "trust", "dislike", "jealousy", "med_cat", 
            "training", "apprentice", "border", "reputation", "leader", "gone", 
            "multi_gone", "disaster_gone", "herbs", "deputy", "small_prey", "big_prey", 
            "disaster", "multi_deaths", "kits", "cruel_season", "two_apprentices", 
            "warrior", "no_app", "clan_to_p_l", "clan_to_r_c", "patrol_to_p_l", "patrol_to_r_c", 
            "rel_two_apps", "p_l_to_r_c", "clan_to_patrol", "rel_patrol", "distrust", "disrespect"

        ]

        """tag info:
        death tags: you can only have ONE death tag. if you have multiple, it picks the first one in this order:
        "death" (kills r_c) > "disaster" (kills whole patrol) > "multi_deaths" (kills 2-4 cats)
        
        relation_r_c also works for s_c"""


patrol = Patrol()

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/patrols/"
hunting_directory = "hunting/"
training_directory = "training/"
border_directory = "border/"
med_directory = "med/"

GENERAL = None
with open(f"{resource_directory}general.json", 'r') as read_file:
    GENERAL = ujson.loads(read_file.read())

# HUNTING #
HUNTING = None
with open(f"{resource_directory}{hunting_directory}hunting.json", 'r') as read_file:
    HUNTING = ujson.loads(read_file.read())

HUNTING_FST = None
with open(f"{resource_directory}{hunting_directory}hunting_forest.json", 'r') as read_file:
    HUNTING_FST = ujson.loads(read_file.read())

HUNTING_PLN = None
with open(f"{resource_directory}{hunting_directory}hunting_plains.json", 'r') as read_file:
    HUNTING_PLN = ujson.loads(read_file.read())

HUNTING_MTN = None
with open(f"{resource_directory}{hunting_directory}hunting_mountains.json", 'r') as read_file:
    HUNTING_MTN = ujson.loads(read_file.read())

HUNTING_BCH = None
with open(f"{resource_directory}{hunting_directory}hunting_beach.json", 'r') as read_file:
    HUNTING_BCH = ujson.loads(read_file.read())

HUNTING_WTLND = None
with open(f"{resource_directory}{hunting_directory}hunting_wetlands.json", 'r') as read_file:
    HUNTING_WTLND = ujson.loads(read_file.read())

# BORDER #
BORDER = None
with open(f"{resource_directory}{border_directory}border.json", 'r') as read_file:
    BORDER = ujson.loads(read_file.read())

BORDER_FST = None
with open(f"{resource_directory}{border_directory}border_forest.json", 'r') as read_file:
    BORDER_FST = ujson.loads(read_file.read())

BORDER_PLN = None
with open(f"{resource_directory}{border_directory}border_plains.json", 'r') as read_file:
    BORDER_PLN = ujson.loads(read_file.read())

BORDER_MTN = None
with open(f"{resource_directory}{border_directory}border_mountains.json", 'r') as read_file:
    BORDER_MTN = ujson.loads(read_file.read())

BORDER_BCH = None
with open(f"{resource_directory}{border_directory}border_beach.json", 'r') as read_file:
    BORDER_BCH = ujson.loads(read_file.read())

# TRAINING #
TRAINING = None
with open(f"{resource_directory}{training_directory}training.json", 'r') as read_file:
    TRAINING = ujson.loads(read_file.read())

TRAINING_FST = None
with open(f"{resource_directory}{training_directory}training_forest.json", 'r') as read_file:
    TRAINING_FST = ujson.loads(read_file.read())

TRAINING_PLN = None
with open(f"{resource_directory}{training_directory}training_plains.json", 'r') as read_file:
    TRAINING_PLN = ujson.loads(read_file.read())

TRAINING_MTN = None
with open(f"{resource_directory}{training_directory}training_mountains.json", 'r') as read_file:
    TRAINING_MTN = ujson.loads(read_file.read())

TRAINING_BCH = None
with open(f"{resource_directory}{training_directory}training_beach.json", 'r') as read_file:
    TRAINING_BCH = ujson.loads(read_file.read())

# MED CAT #

MEDCAT = None
with open(f"{resource_directory}{med_directory}medcat.json", 'r') as read_file:
    MEDCAT = ujson.loads(read_file.read())


# NEW CAT #
NEW_CAT = None
with open(f"{resource_directory}new_cat.json", 'r') as read_file:
    NEW_CAT = ujson.loads(read_file.read())

NEW_CAT_HOSTILE = None
with open(f"{resource_directory}new_cat_hostile.json", 'r') as read_file:
    NEW_CAT_HOSTILE = ujson.loads(read_file.read())

NEW_CAT_WELCOMING = None
with open(f"{resource_directory}new_cat_welcoming.json", 'r') as read_file:
    NEW_CAT_WELCOMING = ujson.loads(read_file.read())

# OTHER CLAN #
OTHER_CLAN = None
with open(f"{resource_directory}other_clan.json", 'r') as read_file:
    OTHER_CLAN = ujson.loads(read_file.read())

OTHER_CLAN_ALLIES = None
with open(f"{resource_directory}other_clan_allies.json", 'r') as read_file:
    OTHER_CLAN_ALLIES = ujson.loads(read_file.read())

OTHER_CLAN_HOSTILE = None
with open(f"{resource_directory}other_clan_hostile.json", 'r') as read_file:
    OTHER_CLAN_HOSTILE = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                            patrols with conditions                           #
# ---------------------------------------------------------------------------- #

DISASTER = None
with open(f"{resource_directory}disaster.json", 'r') as read_file:
    DISASTER = ujson.loads(read_file.read())

