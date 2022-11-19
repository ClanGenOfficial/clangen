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
            game.patrolled.append(cat)
        if self.possible_patrol_leaders:
            self.patrol_leader = choice(self.possible_patrol_leaders)
        elif not self.possible_patrol_leaders:
            self.patrol_leader = choice(self.patrol_cats)
        if len(self.patrol_cats) >= 2:
            self.patrol_random_cat = choice(self.patrol_cats)
            for cat in self.patrol_cats:
                if self.patrol_random_cat == self.patrol_leader:
                    self.patrol_random_cat = choice(self.patrol_cats)
                else:
                    break
        else:
            self.patrol_random_cat = choice(self.patrol_cats)
        if len(self.patrol_cats) >= 3:
            for cat in self.patrol_cats:
                if cat != self.patrol_leader and cat != self.patrol_random_cat:
                    self.patrol_other_cats.append(cat)
        if self.patrol_leader is not None:
            pl_index = self.patrol_cats.index(self.patrol_leader)
            patrol_leader_name = str(self.patrol_names[pl_index])
            self.patrol_leader_name = str(patrol_leader_name)

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

        # general hunting patrols
        possible_patrols.extend(self.generate_patrol_events(HUNTING))

        # general/misc patrols
        possible_patrols.extend(self.generate_patrol_events(GENERAL))

        # deadly patrols
        if game_setting_disaster:
            possible_patrols.extend(self.generate_patrol_events(DISASTER))

        # fighting patrols
        possible_patrols.extend(self.generate_patrol_events(FIGHTING))

        # training patrols
        possible_patrols.extend(self.generate_patrol_events(TRAINING))

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
            if patrol.tags is not None:
                if "apprentice" in patrol.tags:
                    if "apprentice" not in self.patrol_statuses:
                        apprentice = False
                    else:
                        apprentice = True
                else:
                    apprentice = True

            if game.clan.game_mode != 'classic':
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
                # elif patrol_type == 'med' and ["med", "general"] in patrol.tags:
                #    correct_button
                else:
                    correct_button = False
                if max_good and min_good and correct_season and correct_biome and apprentice and correct_button:
                    final_patrols.append(patrol)
            else:
                if max_good and min_good and correct_season and correct_biome and apprentice:
                    final_patrols.append(patrol)
        
        return final_patrols
        

        if self.patrol_random_cat is not None and self.patrol_random_cat.status == 'apprentice' and len(
                self.patrol_cats) > 1:
            possible_patrols.extend([
                PatrolEvent(
                    150,
                    'The patrol wants to hold a training session for r_c',
                    'r_c becomes more confident in their abilities after the training session',
                    'r_c is nervous and doesn\'t perform well',
                    'They decide to focus on the patrol instead',
                    50,
                    10),
                PatrolEvent(
                    116,
                    'While helping gathering herbs, r_c stumbles upon a bush of red berries',
                    'The patrol tells r_c to stay away from the deathberries just in time',
                    'r_c chews some of the deathberries and dies',
                    'r_c decides not to touch the berries',
                    50,
                    10,
                    win_skills=['very smart', 'extremely smart']),
                PatrolEvent(
                    117,
                    'While helping gathering herbs, r_c stumbles upon a bush of red berries',
                    'Yum! r_c recognizes them as strawberries and shares the tasty treat with the patrol',
                    'The patrol scolds r_c for wasting time munching on berries',
                    'r_c decides not to touch the berries',
                    50,
                    10,
                    win_skills=['very smart', 'extremely smart']),
            ])

        # conversation patrols
        if len(self.patrol_cats) == 2 and self.patrol_leader != self.patrol_random_cat:
            # general relationship patrols
            if len(self.patrol_cats) == 2:
                possible_patrols.extend([
                    PatrolEvent(
                        1000,
                        'p_l playfully asks r_c to race',
                        'r_c accepts and wins, grinning mischieviously',
                        'r_c loses and gets annoyed',
                        'r_c politely declines',
                        50,
                        10),
                    PatrolEvent(
                        1001,
                        'p_l asks r_c if they can tell them a secret',
                        'p_l feels a huge weight lift from their shoulders as they tell their secret to r_c',
                        'r_c dismisses it rudely, leaving p_l heartbroken',
                        'r_c politely declines',
                        60,
                        10),
                    PatrolEvent(
                        1002,
                        'r_c has failed yet another hunting attempt and is feeling embarrassed',
                        'p_l gently instructs them what they could do better, and r_c catches a big squirrel!',
                        'p_l tries to tell them what they did wrong but r_c takes offense and stalks off',
                        'p_l says nothing',
                        60,
                        20),
                    PatrolEvent(
                        1004,
                        'p_l considers joking around with r_c to lighten up the mood',
                        'p_l makes r_c laugh the entire patrol',
                        'r_c scolds p_l for their lack of focus',
                        'p_l decides to stay quiet',
                        50,
                        10),
                    PatrolEvent(
                        1005,
                        'p_l points out an interesting cloud to r_c',
                        'r_c and p_l spend hours watching the sky together',
                        'r_c chides p_l for their childishness',
                        'p_l changes the subject',
                        50,
                        10),
                    PatrolEvent(
                        1006,
                        'r_c is thrilled that they were assigned to patrol with p_l today',
                        'The two spend the whole patrol chatting and laughing',
                        'Unfortunately, p_l doesn\'t seem to feel the same',
                        'Still, their duties to the clan come first',
                        50,
                        10),
                    PatrolEvent(
                        1007,
                        'p_l notices that r_c isn\'t acting like their usual self',
                        'r_c opens up to p_l over something that has been bothering them',
                        'r_c snaps at p_l to mind their own business',
                        'p_l decides not to interfere',
                        50,
                        10)
                ])

                if current_season == 'Leaf-bare':
                    possible_patrols.extend([
                        PatrolEvent(
                            1003,
                            'p_l notices r_c shivering',
                            'p_l asks r_c if they want to walk closer for warmth',
                            'r_c says that they\'re fine',
                            'p_l decides not to mention it',
                            60,
                            20)
                    ])

                # romantic patrols for two cats
                if self.patrol_leader.is_potential_mate(self.patrol_random_cat, for_love_interest=True):
                    possible_patrols.extend([
                        PatrolEvent(
                            1010,
                            'p_l casually brushes against r_c\'s flank',
                            'p_l and r_c enter camp together, tails entwined',
                            'r_c jerks away suddenly and almost trips',
                            'p_l immediately apologizes for doing so',
                            50,
                            10),
                        PatrolEvent(
                            1011,
                            'p_l thinks this might be the perfect chance to tell r_c how they feel',
                            'r_c listens intently, smiling a bit by the end of p_l\'s confession',
                            'r_c cuts them off, saying that they don\'t feel the same way',
                            'p_l\'s nerves seem to get the best of them and they say nothing',
                            50,
                            10),

                        PatrolEvent(
                            1012,
                            'p_l asks r_c if they can talk on the patrol',
                            'r_c agrees. p_l and r_c end up talking until the sun starts to set',
                            'r_c agrees, but it\'s awkward and the rest of the patrol lasts way too long',
                            'p_l changes their mind',
                            50,
                            10),
                        PatrolEvent(
                            1013,
                            'p_l notices how pretty r_c looks with the sun on their pelt',
                            'p_l shares the compliment with r_c, who thanks them',
                            'r_c tells p_l to keep their eyes off of them',
                            'p_l decides to keep their feelings silent',
                            50,
                            10),
                        PatrolEvent(
                            1014,
                            'p_l notices r_c staring at them',
                            'p_l feels their heart flutter',
                            'p_l snaps at r_c to knock it off',
                            'p_l ignores r_c',
                            50,
                            10),
                        PatrolEvent(
                            1015,
                            'p_l thinks r_c\'s eyes are beautiful',
                            'p_l tells r_c and they love the compliment',
                            'p_l tells r_c and they feel awkward, ignoring p_l for the rest of the patrol',
                            'p_l shakes their head and focuses on the patrol',
                            50,
                            10)
                    ])
                    if current_season == 'Newleaf':
                        possible_patrols.extend([
                            PatrolEvent(
                                1012,
                                'p_l brings a flower to r_c, saying it matches their eyes',
                                'r_c smiles and takes the flower',
                                'r_c goes to take the flower and sneezes. The flower goes flying',
                                'p_l drops the flower on the way over! Oh well',
                                50,
                                10),
                        ])
                elif self.patrol_random_cat.status == 'apprentice':
                    possible_patrols.extend([
                        PatrolEvent(
                            1020,
                            'p_l asks r_c how their training is going',
                            'r_c happily tells p_l all about the fighting move they just learned',
                            'r_c answers curtly, having been subjected to cleaning the elders\'s den recently',
                            'r_c doesn\'t hear the question and p_l changes the subject',
                            50,
                            10),
                        PatrolEvent(
                            1021,
                            'p_l asks r_c if they would like to go to the training grounds to practice',
                            'The practice goes well and the apprentice learns a lot!',
                            'The apprentice can\'t seem to focus today',
                            'r_c declines the offer',
                            50,
                            10),
                        PatrolEvent(
                            1023,
                            'r_c doesn\'t feel totally comfortable around p_l just yet',
                            'p_l cracks a joke to make r_c feel more at ease',
                            'r_c forces themself to spend time with p_l but it doesn\'t help',
                            'r_c stays away from p_l',
                            50,
                            10)
                    ])
                if current_season == 'Leaf-fall':
                    possible_patrols.extend([
                        PatrolEvent(
                            1022,
                            'Leaf-fall gives new opportunities to train!',
                            'r_c pays close attention to how p_l stalks prey while walking on leaves and manages to catch a bird!',
                            'r_c can\'t seem to replicate p_l and scares off all the prey',
                            'p_l decides to hunt with r_c in an area with less leaves',
                            50,
                            10)

                    ])

                else:
                    possible_patrols.extend([
                        PatrolEvent(
                            200,
                            'Your patrol doesn\'t find anything useful',
                            'It was still a fun outing!',
                            'How did you fail this??',
                            'Your patrol decides to head home',
                            100,
                            10),
                        PatrolEvent(
                            201,
                            'The patrol finds a nice spot to sun themselves',
                            'The sunlight feels great and the cats have a successful patrol',
                            'The patrol doesn\'t get much done because of that',
                            'They decide to stay focused instead',
                            80,
                            10),
                        PatrolEvent(
                            204,
                            'Your patrol has a disagreement and look to p_l to settle the dispute',
                            'p_l manages to skillfully smooth over any disagreement',
                            'p_l stutters; they don\'t think they are fit to lead the patrol',
                            'Your patrol decides to head home',
                            50,
                            10,
                            win_skills=['great speaker', 'excellent speaker']),
                        PatrolEvent(
                            205,
                            'r_c admits that they had a vision from StarClan last night',
                            'The patrol talks them through the vision as they hunt',
                            'No one can make sense of the vision',
                            'The patrol doesn\'t talk about the vision',
                            50,
                            10,
                            win_skills=['strong connection to starclan']),
                        PatrolEvent(
                            202,
                            'The patrol quickly devolves into ghost stories and everyone is on edge',
                            'Despite the tense mood, the patrol is successful',
                            'A branch snaps and the whole patrol runs back to camp',
                            'p_l quickly silences any talk about ghosts',
                            50,
                            10),
                        PatrolEvent(
                            203, 'r_c is tempted to eat the prey they just caught',
                            'They eat the prey without anyone noticing',
                            'The patrol notices r_c eating the prey and reports them back at camp',
                            'r_c decides against breaking the warrior code',
                            50,
                            10),
                        PatrolEvent(
                            103,
                            'p_l suggests this might be a good chance for the cats to practice teamwork',
                            'Everyone has a nice practice session and their connection to their Clanmates grows stronger',
                            'Unfortunately, no one steps up to teach',
                            'They decide to focus on the patrol instead',
                            50,
                            10,
                            win_skills=['good teacher', 'great teacher', 'fantastic teacher']),
                        PatrolEvent(
                            104,
                            'p_l suggests this might be a good chance for the cats to practice new hunting techniques',
                            'Everyone has a nice practice session and their hunting skills grow stronger',
                            'Unfortunately, no one steps up to teach',
                            'They decide to focus on the patrol instead',
                            50,
                            10,
                            win_skills=['good teacher', 'great teacher', 'fantastic teacher']),
                        PatrolEvent(
                            105,
                            'p_l suggests this might be a good chance for the cats to practice new fighting techniques',
                            'Everyone has a nice practice session and their fighting skills grow stronger',
                            'Unfortunately, no one steps up to teach',
                            'They decide to focus on the patrol instead',
                            50,
                            10,
                            win_skills=['good teacher', 'great teacher', 'fantastic teacher'])
                    ])

                # if self.patrol_random_cat.status == 'warrior' or self.patrol_random_cat.status == 'apprentice':
                #     possible_patrols.extend([
                #         PatrolEvent(
                #             250,
                #             'r_c admits that they have been training in the dark forest',
                #             'The patrol manages to convince r_c to stop',
                #             'The patrol isn\'t able to convince r_c to stop and a few nights later they are found dead in their nest',
                #             'The patrol decides not to advise r_c what they should do',
                #             50,
                #             10,
                #             win_skills=[
                #                 'great speaker', 'excellent speaker',
                #                 'strong connection to starclan'
                #             ]),
                #         PatrolEvent(
                #             251,
                #             'r_c admits that they have been training in the dark forest',
                #             'The patrol manages to convince r_c to stop',
                #             'The patrol isn\'t able to convince r_c to stop and a few nights later they wake up injured in their nest',
                #             'The patrol decides not to advise r_c what they should do',
                #             50,
                #             10,
                #             win_skills=[
                #                 'great speaker', 'excellent speaker',
                #                 'strong connection to starclan'
                #             ])
                #     ])

                if self.patrol_random_cat.status == 'deputy':
                    possible_patrols.extend([
                        PatrolEvent(
                            260,
                            'r_c admits that they don\'t think that they are a good deputy',
                            'The patrol tells r_c that the Clan wouldn\'t be the same without them, and r_c feels a sense of relief',
                            'The patrol secretly agrees with r_c',
                            'The patrol doesn\'t say anything about r_c\'s statement',
                            50,
                            10,
                            win_skills=['great speaker', 'excellent speaker']),
                        PatrolEvent(
                            251,
                            'The patrol starts to doubt r_c\'s ability as the Clan\'s deputy',
                            'r_c performs well on the patrol and all doubt is quelled',
                            'The patrol performs poorly and they blame r_c',
                            'The patrol decides to keep their thoughts to themselves',
                            50,
                            10)
                    ])
                # trait specific patrols
                if self.patrol_random_cat.trait == 'strange':
                    possible_patrols.extend([
                        PatrolEvent(
                            600,
                            'r_c tells the patrol to roll in a patch of garlic to diguise their scent while hunting',
                            'The plan works and their hunt goes well',
                            'The patrol finds no prey and blame r_c; it seems like all the prey was scared off because of their stench!',
                            'The patrol ignores r_c\'s odd instructions',
                            50,
                            10)
                    ])
                elif self.patrol_random_cat.trait == 'bloodthirsty':
                    possible_patrols.extend([
                        PatrolEvent(
                            605,
                            'r_c deliberately provokes a border patrol skirmish',
                            'The other cats in the patrol keep r_c from fighting and no one is hurt',
                            'r_c is injured by the enemy patrol',
                            'r_c decides to back down by themselves',
                            50,
                            10,
                            win_skills=['great speaker', 'fantastic speaker'])
                    ])

        if self.patrol_random_cat.skill == 'formerly a loner':
            possible_patrols.extend([
                PatrolEvent(
                    510,
                    'r_c finds an old friend of their\'s from when they were a loner',
                    'r_c invites their friend to join the Clan',
                    'r_c and their friend reminisce about old times',
                    'r_c says farewell to their friend and rejoins the patrol', 40, 10)
            ])

        if self.patrol_random_cat.status == 'formerly a kittypet':
            possible_patrols.extend([
                PatrolEvent(
                    520,
                    'r_c finds an old friend of their\'s from when they were a kittypet',
                    'r_c invites their friend to join the Clan',
                    'r_c and their friend reminisce about old times',
                    'r_c says farewell to their friend and rejoins the patrol', 40, 10)
            ])

            return possible_patrols

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
        # if patrol contains cats with autowin skill, chance of success is high
        # otherwise it will calculate the chance by adding the patrolevent's chance of success plus the patrol's total exp
        chance = self.patrol_event.chance_of_success + int(
            self.patrol_total_experience / 10)
        if self.patrol_event.patrol_id != 100:
            chance = min(chance, 80)
        if self.patrol_event.win_skills is not None:
            if set(self.patrol_skills).isdisjoint(
                    self.patrol_event.win_skills):
                chance = 90
        if self.patrol_event.win_trait is not None:
            if set(self.patrol_traits).isdisjoint(
                    self.patrol_event.win_trait):
                chance = 90
        if self.patrol_event.fail_skills is not None:
            if set(self.patrol_skills).isdisjoint(
                    self.patrol_event.fail_skills):
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
                    n = 0
            self.handle_exp_gain()
            self.add_new_cats()
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
                if fail_text[1] is not None:
                    n = 1
            elif outcome <= 10 and len(fail_text) > 3 and fail_text[3] is not None:
                n = 3
            elif outcome >= 11 and len(fail_text) > 2 and fail_text[2] is not None:
                n = 2
            elif fail_text[0] is None:
                if fail_text[3] is not None:
                    n = 3
                elif fail_text[1] is not None:
                    n = 1
            else:
                n = 0
            if n == 2:
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
        if game.switches['game_mode'] == 'classic':
            gm_modifier = gm_modifier
        elif game.switches['game_mode'] == 'extended':
            gm_modifier = 3
        elif game.switches['game_mode'] == 'cruel_season':
            gm_modifier = 6
        if self.success:
            for cat in self.patrol_cats:
                print("EXP Before: " + str(cat.experience))
                gained_exp = ((patrol_exp + base_exp) / len(self.patrol_cats)) / gm_modifier
                cat.experience = int(cat.experience + gained_exp)
                print("After: " + str(cat.experience))

    def handle_deaths(self):
        if self.patrol_random_cat.status == 'leader':
            if "gone" in self.patrol_event.tags:
                game.clan.leader_lives -= 9  # taken by twolegs, fall into ravine
            else:
                game.clan.leader_lives -= 1
        self.patrol_random_cat.die()
        if len(self.patrol_event.history_text) >= 2:
            self.patrol_random_cat.death_event.append(f'{self.patrol_event.history_text[1]}')
        else:
            self.patrol_random_cat.death_event.append(f'This cat died while patrolling.')

        if "disaster" in self.patrol_event.tags:
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
            romantic_love = 10
        if "platonic" in self.patrol_event.tags:
            platonic_like = 10
        if "dislike" in self.patrol_event.tags:
            dislike = 5
        if "respect" in self.patrol_event.tags:
            admiration = 10
        if "comfort" in self.patrol_event.tags:
            comfortable = 5
        if "jealous" in self.patrol_event.tags:
            jealousy = 5
        if "trust" in self.patrol_event.tags:
            trust = 10

        # affect the relationship
        cat_ids = [cat.ID for cat in self.patrol_cats]
        for cat in self.patrol_cats:
            relationships = list(
                filter(lambda rel: rel.cat_to.ID in cat_ids,
                       list(cat.relationships.values())))
            for rel in relationships:
                if self.success:
                    rel.romantic_love += romantic_love
                    rel.platonic_like += platonic_like
                    rel.dislike -= dislike
                    rel.admiration += admiration
                    rel.comfortable += comfortable
                    rel.jealousy -= jealousy
                    rel.trust += trust
                elif not self.success:
                    rel.romantic_love -= romantic_love
                    rel.platonic_like -= platonic_like
                    rel.dislike += dislike
                    rel.admiration -= admiration
                    rel.comfortable -= comfortable
                    rel.jealousy += jealousy
                    rel.trust -= trust

    def add_new_cats(self):
        if "new_cat" in self.patrol_event.tags:
            if self.patrol_event.patrol_id == "gen_gen_newkit1":  # new kit
                kit = Cat(status='kitten', moons=0)
                # create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = Cat.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat)
                game.clan.add_cat(kit)
                new_backstory = choice(['abandoned1', 'abandoned2', 'abandoned3'])
                kit.backstory = new_backstory
                kit.thought = 'Is looking around the camp with wonder'
                if kit.backstory in ['abandoned2']:
                    if randint(0, 2) == 0:  # chance to add collar
                        kit.accessory = choice(collars)

            if self.patrol_event.patrol_id in ["gen_gen_newcat1", "gen_gen_newcat3", "gen_gen_lonerchase1"]:  # new loner
                new_status = choice([
                    'apprentice', 'warrior', 'warrior', 'warrior', 'warrior',
                    'elder'
                ])
                new_backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2',
                                        'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee',
                                        'tragedy_survivor'])
                kit = Cat(status=new_status)
                if (kit.status == 'elder'):
                    kit.moons = randint(120, 150)
                # create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = Cat.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat)
                game.clan.add_cat(kit)
                kit.backstory = new_backstory
                kit.thought = 'Is looking around the camp with wonder'
                if randint(0, 5) == 0:  # chance to keep name
                    kit.name.prefix = choice(names.loner_names)
                    kit.name.suffix = ''
                elif randint(0, 3) == 0:  # chance to have kittypet name prefix + suffix
                    kit.name.prefix = choice(names.loner_names)
                    kit.name.suffix = choice(names.normal_suffixes)
                # add kits to the added cats if the second success text is rolled
                if len(self.patrol_event.success_text) >= 2:
                    if self.final_success == self.patrol_event.success_text[1]:
                        num_kits = choice([2, 2, 2, 2, 3, 4])
                        for _ in range(num_kits):
                            kit2 = Cat(status='kitten', moons=0)
                            kit2.backstory = 'outsider_roots2'
                            kit2.parent1 = kit.ID
                            kit2.thought = 'Is looking around the camp with wonder'
                            # create and update relationships
                            for cat_id in game.clan.clan_cats:
                                the_cat = Cat.all_cats.get(cat_id)
                                if the_cat.dead or the_cat.exiled:
                                    continue
                                if the_cat.ID in [kit2.parent1, kit2.parent2]:
                                    the_cat.relationships[kit2.ID] = Relationship(the_cat, kit2, False, True)
                                    kit2.relationships[the_cat.ID] = Relationship(kit2, the_cat, False, True)
                                else:
                                    the_cat.relationships[kit2.ID] = Relationship(the_cat, kit2)
                                    kit2.relationships[the_cat.ID] = Relationship(kit2, the_cat)
                            game.clan.add_cat(kit2)

            elif self.patrol_event.patrol_id in ["gen_gen_newcat2", "gen_gen_newcat3"]:  # new kittypet
                new_status = choice([
                    'apprentice', 'warrior', 'warrior', 'warrior', 'warrior',
                    'elder'
                ])
                kit = Cat(status=new_status)
                # create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = Cat.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat)
                game.clan.add_cat(kit)
                new_backstory = choice(['kittypet1', 'kittypet2'])
                kit.backstory = new_backstory
                kit.thought = 'Is looking around the camp with wonder'
                if (kit.status == 'elder'):
                    kit.moons = randint(120, 150)
                if randint(0, 2) == 0:  # chance to add collar
                    kit.accessory = choice(collars)
                if randint(0, 5) == 0:  # chance to keep name
                    kit.name.prefix = choice(names.loner_names)
                    kit.name.suffix = ''
                elif randint(0, 3) == 0:
                    kit.name.prefix = choice(names.loner_names)
                    kit.name.suffix = choice(names.normal_suffixes)
                if self.final_success == self.patrol_event.success_text[1]:
                    num_kits = choice([2, 2, 2, 2, 3, 4])
                    for _ in range(num_kits):
                        kit2 = Cat(status='kitten', moons=0)
                        kit2.backstory = 'outsider_roots2'
                        kit2.parent1 = kit.ID
                        kit2.thought = 'Is looking around the camp with wonder'
                        # create and update relationships
                        for cat_id in game.clan.clan_cats:
                            the_cat = Cat.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if the_cat.ID in [kit2.parent1, kit2.parent2]:
                                the_cat.relationships[kit2.ID] = Relationship(the_cat, kit2, False, True)
                                kit2.relationships[the_cat.ID] = Relationship(kit2, the_cat, False, True)
                            else:
                                the_cat.relationships[kit2.ID] = Relationship(the_cat, kit2)
                                kit2.relationships[the_cat.ID] = Relationship(kit2, the_cat)
                        game.clan.add_cat(kit2)

            elif self.patrol_event.patrol_id == "gen_gen_newmed1":  # new med cat
                new_status = 'medicine cat'
                kit = Cat(status=new_status)
                # create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat)
                game.clan.add_cat(kit)
                add_siblings_to_cat(kit, cat_class)
                add_children_to_cat(kit, cat_class)
                new_backstory = choice(['medicine_cat', 'disgraced', 'loner1', 'loner2'])
                kit.backstory = new_backstory
                kit.skill = choice(['good healer', 'great healer', 'fantastic healer'])
                kit.thought = 'Is looking around the camp with wonder'
                if randint(0, 5) == 0 and kit.backstory not in ['medicine_cat', 'disgraced']:  # chance to keep name
                    # kit.name.prefix = choice(names.loner_names)
                    kit.name.suffix = ''
                elif randint(0, 3) == 0 and kit.backstory not in ['medicine_cat', 'disgraced']:
                    kit.name.prefix = choice(names.loner_names)
                    kit.name.suffix = choice(names.normal_suffixes)

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
            fail text [1] is unscathed 2, fail skill or fail traits
            fail text [2] is death
            fail text [3] is scar"""

        tags = [
            'hunting', 'other_clan', 'fighting', 'death', 'scar', 'new_cat', 'npc',
            'retirement', 'injury', 'illness', 'romantic', 'platonic', 'comfort', 'respect', 'trust',
            'dislike', 'jealousy', 'med_cat', 'training', 'apprentice', 'border', 'reputation', 'leader',
            'herbs', 'gone', 'disaster', 'multiple_deaths', 'general'
        ]


patrol = Patrol()

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/patrols/"

GENERAL = None
with open(f"{resource_directory}general.json", 'r') as read_file:
    GENERAL = ujson.loads(read_file.read())

HUNTING = None
with open(f"{resource_directory}hunting.json", 'r') as read_file:
    HUNTING = ujson.loads(read_file.read())

FIGHTING = None
with open(f"{resource_directory}fighting.json", 'r') as read_file:
    FIGHTING = ujson.loads(read_file.read())

TRAINING = None
with open(f"{resource_directory}training.json", 'r') as read_file:
    TRAINING = ujson.loads(read_file.read())

NEW_CAT = None
with open(f"{resource_directory}new_cat.json", 'r') as read_file:
    NEW_CAT = ujson.loads(read_file.read())

NEW_CAT_HOSTILE = None
with open(f"{resource_directory}new_cat_hostile.json", 'r') as read_file:
    NEW_CAT_HOSTILE = ujson.loads(read_file.read())

NEW_CAT_WELCOMING = None
with open(f"{resource_directory}new_cat_welcoming.json", 'r') as read_file:
    NEW_CAT_WELCOMING = ujson.loads(read_file.read())

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

