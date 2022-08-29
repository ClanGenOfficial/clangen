from random import choice, randint
from math import ceil, floor
from .events import events_class
from .game_essentials import *
from .names import *
from .cats import *
from .pelts import *


class Patrol(object):

    def __init__(self):
        self.patrol_event = None
        self.patrol_leader = None
        self.patrol_cats = []
        self.patrol_skills = []
        self.patrol_statuses = []
        self.patrol_traits = []
        self.patrol_total_experience = 0
        self.success = False
        self.patrol_random_cat = None
        self.patrol_stat_cat = None
        self.experience_levels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']

    def add_patrol_cats(self):
        self.patrol_cats.clear()
        self.patrol_skills.clear()
        self.patrol_statuses.clear()
        self.patrol_traits.clear()
        self.patrol_total_experience = 0
        for cat in game.switches['current_patrol']:
            self.patrol_cats.append(cat)
            self.patrol_skills.append(cat.skill)
            self.patrol_statuses.append(cat.status)
            self.patrol_traits.append(cat.trait)
            self.patrol_total_experience += cat.experience
        self.patrol_leader = choice(self.patrol_cats)

    def add_possible_patrols(self):
        possible_patrols = []
        # general hunting patrols
        possible_patrols.extend([
            PatrolEvent(1, 'Your patrol comes across a mouse', 'Your patrol catches the mouse!', 'Your patrol narrowly misses the mouse', 'Your patrol ignores the mouse', 60, 10,
                        win_skills=['good hunter', 'great hunter', 'fantastic hunter']),
            PatrolEvent(2, 'Your patrol comes across a large rat', 'Your patrol catches the rat! More freshkill!',
                        'Your patrol misses the rat, and the patrol\'s confidence is shaken', 'Your patrol ignores the rat', 50, 10,
                        win_skills=['great hunter', 'fantastic hunter']),
            PatrolEvent(3, 'Your patrol comes across a large hare', 'Your patrol catches the hare!', 'Your patrol narrowly misses the hare', 'Your patrol ignores the hare', 40, 20,
                        win_skills=['fantastic hunter']),
            PatrolEvent(4, 'Your patrol comes across a bird', 'Your patrol catches the bird before it flies away!', 'Your patrol narrowly misses the bird',
                        'Your patrol ignores the bird', 50, 10, win_skills=['great hunter', 'fantastic hunter']),
            PatrolEvent(5, 'Your patrol comes across a squirrel', 'Your patrol catches the squirrel!', 'Your patrol narrowly misses the squirrel',
                        'Your patrol ignores the squirrel', 50, 10, win_skills=['good hunter', 'great hunter', 'fantastic hunter']),
            PatrolEvent(6, 'Your patrol sees the shadow of a fish in a river', 'r_c hooks the fish out of the water! More freshkill!',
                        'Your patrol accidentally scares the fish away', 'Your patrol ignores the fish', 50, 10, win_skills=['great hunter', 'fantastic hunter'])])

        # general boring patrols
        possible_patrols.extend([
            PatrolEvent(100, 'Your patrol doesn\'t find anything useful', 'It was still a fun outing!', 'How did you fail this??', 'Your patrol decides to head home early', 100,
                        10), PatrolEvent(101, 'The patrol finds a nice spot to sun themselves', 'The sunlight feels great and the cats have a pleasant patrol',
                                         'The patrol doesn\'t get much done because of that', 'They decide to stay focused instead', 80, 10)])
        if game.clan.current_season == 'Newleaf':
            print('a')
        elif game.clan.current_season == 'Greenleaf':
            print('a')
        elif game.clan.current_season == 'Leaf-fall':
            print('a')
        elif game.clan.current_season == 'Leaf-bare':
            print('a')

        # conversation patrols
        if len(self.patrol_cats) > 1:
            possible_patrols.extend([
                PatrolEvent(200, 'Your patrol doesn\'t find anything useful', 'It was still a fun outing!', 'How did you fail this??', 'Your patrol decides to head home', 100, 10),
                PatrolEvent(201, 'The patrol finds a nice spot to sun themselves', 'The sunlight feels great and the cats have a successful patrol',
                            'The patrol doesn\'t get much done because of that', 'They decide to stay focused instead', 80, 10)])

        # fighting patrols
        possible_patrols.extend([PatrolEvent(300, 'Your patrol catches the scent of a fox', 'Your patrol finds the fox and drives it away',
                                             'Your patrol fails to drive away to fox, but luckily no cat was injured', 'Your patrol decides not to pursue the fox', 40, 20,
                                             win_skills=['good fighter', 'great fighter', 'excellent fighter']),
                                 PatrolEvent(301, 'Your patrol comes catches the scent of a fox', 'Your patrol drives away the fox and her cubs',
                                             'The mother fox fights to defend her cubs, and r_c is injured in the attack', 'Your patrol decides not to pursue the dog', 30, 30,
                                             win_skills=['excellent fighter']),
                                 PatrolEvent(302, 'Your patrol comes across a large dog', 'Your patrol valiantly drives away the dog',
                                             'The dog is driven away, but not before injuring r_c', 'Your patrol decides not to pursue the dog', 40, 20,
                                             win_skills=['excellent fighter']),
                                 PatrolEvent(303, 'Your patrol comes across a small dog', 'Your patrol drives away the dog', 'The dog\'s barking scares away prey',
                                             'The patrol decides not to pursue the dog', 20, 60, win_skills=['good fighter', 'great fighter', 'excellent fighter']),
                                 PatrolEvent(304, 'r_c alerts the rest of the patrol that there is a rogue near the clan border',
                                             'Your patrol chases the rogue off of the territory', 'The rogue leaves, but not before giving r_c a scar',
                                             'Your patrol decides not to confront the rogue', 50, 20, win_skills=['great fighter', 'excellent fighter']),
                                 PatrolEvent(305, 'A gang of rogues confronts your patrol', 'Your patrol drives away the rogues',
                                             'The rogues are bloodthirsty and kill r_c before they leave', 'The patrol sprints back to camp', 40, 20,
                                             win_skills=['excellent fighter']),
                                 PatrolEvent(306, 'There is a badger den up ahead', 'Your patrol chases the badger off of the territory',
                                             'The badger is angered when the patrol nears its den and badly injures r_c', 'The patrol avoids the badger den', 40, 20,
                                             win_skills=['excellent fighter']),
                                 PatrolEvent(307, 'There is a badger den up ahead', 'Your patrol chases the badger off of the territory',
                                             'The badger is furious when the patrol nears its den and kills r_c', 'The patrol avoids the badger den', 50, 20,
                                             win_skills=['excellent fighter']), PatrolEvent(308, 'While on patrol, r_c notices some suspicious pawprints in the ground',
                                                                                            'The pawprints lead to a trespassing rogue and the patrol drives them off of the '
                                                                                            'territory', 'It turns out they were r_c\'s own pawprints... How embarrassing',
                                                                                            'They decide not to investigate', 60, 20,
                                                                                            win_skills=['good fighter', 'great fighter', 'excellent fighter']),
                                 PatrolEvent(309, 'While on patrol, r_c notices some suspicious pawprints in the ground',
                                             'The pawprints lead to a trespassing rogue and the patrol drives them off of the '
                                             'territory', 'It turns out they were r_c\'s own pawprints... How embarrassing', 'They decide not to investigate', 60, 20,
                                             win_skills=['good fighter', 'great fighter', 'excellent fighter']), ])

        # single cat patrol

        # new cat patrols (not kit)

        # new kit patrols

        # status specific patrols

        # season specific patrols

        # trait specific patrols

        # biome specific patrols

        # deadly patrols

        self.patrol_event = choice(possible_patrols)

    def calculate_success(self):
        if self.patrol_event is not None:
            # if patrol contains cats with autowin skill, chance of success is 100
            # otherwise it will calculate the chance by adding the patrolevent's chance of success plus the patrol's total exp
            chance = self.patrol_event.chance_of_success + int(self.patrol_total_experience / 10) if set(self.patrol_skills).isdisjoint(self.patrol_event.win_skills) else 100
            if randint(0, 100) < chance:
                self.success = True
                self.handle_exp_gain()

    def handle_exp_gain(self):
        if self.success:
            for cat in self.patrol_cats:
                cat.experience += self.patrol_event.exp


class PatrolEvent(object):
    def __init__(self, patrol_id, intro_text, success_text, fail_text, decline_text, chance_of_success, exp, other_clan=None, win_skills=None):
        if other_clan is None:
            other_clan = {}
        if win_skills is None:
            win_skills = []
        self.patrol_id = patrol_id
        self.intro_text = intro_text
        self.success_text = success_text
        self.fail_text = fail_text
        self.decline_text = decline_text
        self.chance_of_success = chance_of_success  # out of 100
        self.exp = exp
        self.other_clan = other_clan
        self.win_skills = win_skills


patrol = Patrol()
