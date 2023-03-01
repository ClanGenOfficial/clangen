import random
from random import choice, randint
import os

import pygame

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.game_structure.game_essentials import game
from scripts.utility import update_sprite
from scripts.cat.cats import Cat, cat_class
from scripts.cat.names import names
from scripts.clan_resources.freshkill import Freshkill_Pile, Nutrition

# try:
#    from scripts.world import World, save_map, load_map
#    map_available = True
# except:
#    map_available = False
map_available = False
from sys import exit


class Clan():
    BIOME_TYPES = ["Forest", "Plains", "Mountainous", "Beach"]

    CAT_TYPES = [
        "kitten",
        "apprentice",
        "warrior",
        "medicine",
        "deputy",
        "leader",
        "elder",
        "mediator",
        "general",
    ]

    leader_lives = 0
    clan_cats = []
    starclan_cats = []
    seasons = [
        'Newleaf',
        'Newleaf',
        'Newleaf',
        'Greenleaf',
        'Greenleaf',
        'Greenleaf',
        'Leaf-fall',
        'Leaf-fall',
        'Leaf-fall',
        'Leaf-bare',
        'Leaf-bare',
        'Leaf-bare',
    ]
    layout_1 = {
        'leader den': (688, 188),
        'medicine den': (160, 400),
        'nursery': (1240, 400),
        'clearing': (720, 589),
        'apprentice den': (164, 860),
        'warrior den': (1180, 860),
        'elder den': (696, 980),
        'leader place': [(750, 240), (700, 340),
                         (800, 340)],
        'medicine place': [(140, 500), (240, 500), (340, 500), (200, 600),
                           (300, 600)],
        'nursery place': [(1100, 600), (1200, 500), (1300, 500), (1070, 600),
                          (1970, 600), (1270, 600), (1370, 600), (1060, 700),
                          (1160, 700), (1260, 700), (1360, 700)],
        'clearing place': [(750, 640), (600, 740), (700, 740), (800, 740),
                           (600, 840), (700, 840), (800, 840)],
        'apprentice place': [(140, 940), (240, 940), (340, 970), (200, 1040),
                             (300, 1040), (400, 1040)],
        'warrior place': [(1400, 940), (1100, 980), (1200, 940), (1300, 980),
                          (1400, 1040), (1100, 1080), (1200, 1040), (1300, 1080)],
        'elder place': [(840, 1140), (700, 1040), (800, 1040), (640, 1140),
                        (740, 1140)]
    }

    cur_layout = layout_1

    layout_2 = {
        'leader den': (688, 188),
        'medicine den': (160, 400),
        'nursery': (1240, 400),
        'clearing': (720, 589),
        'apprentice den': (164, 860),
        'warrior den': (1180, 860),
        'elder den': (696, 980),
        'leader place': [(1200, 80),
                         (720, 230),
                         (700, 320),
                         (800, 310)],
        'medicine place': [(300, 550),
                           (200, 530), (400, 530),
                           (200, 670),
                           (400, 630),
                           (330, 450)],
        'nursery place': [(1040, 350),
                          (1240, 420),
                          (1100, 500), (1200, 500), (1300, 500),
                          (1070, 600), (1170, 600), (1270, 600),
                          (1160, 700), (1300, 700)],
        'clearing place': [(500, 400),
                           (750, 640), (500, 650),
                           (600, 450), (710, 460), (820, 420),
                           (370, 720), (900, 720),
                           (600, 740), (700, 740), (800, 740),
                           (700, 840), (800, 840),
                           (900, 900)],
        'apprentice place': [(400, 840),
                             (140, 940), (240, 940), (340, 940),
                             (300, 1040), (400, 1040),
                             (350, 1140)],
        'warrior place': [(1400, 940), (1200, 940),
                          (1100, 980), (1300, 980),
                          (1400, 1040), (1200, 1040),
                          (1100, 1080), (1300, 1080)],
        'elder place': [(560, 910),
                        (700, 1040), (800, 1040),
                        (640, 1140), (740, 1140), (840, 1140)]
    }
    places_vacant = {
        'leader': [False, False, False],
        'medicine': [False, False, False, False, False],
        'nursery': [
            False, False, False, False, False, False, False, False, False,
            False, False
        ],
        'clearing': [False, False, False, False, False, False, False],
        'apprentice': [False, False, False, False, False, False],
        'warrior': [False, False, False, False, False, False, False, False],
        'elder': [False, False, False, False, False]
    }

    age = 0
    current_season = 'Newleaf'
    all_clans = []

    def __init__(self,
                 name="",
                 leader=None,
                 deputy=None,
                 medicine_cat=None,
                 biome='Forest',
                 world_seed=6616,
                 camp_site=(20, 22),
                 camp_bg=None,
                 game_mode='classic',
                 starting_members=[]):
        if name != "":
            self.name = name
            self.leader = leader
            if self.leader:
                self.leader.status_change('leader')
                self.clan_cats.append(self.leader.ID)
            self.leader_lives = 9
            self.leader_predecessors = 0
            self.deputy = deputy
            if deputy is not None:
                self.deputy.status_change('deputy')
                self.clan_cats.append(self.deputy.ID)
            self.deputy_predecessors = 0
            self.medicine_cat = medicine_cat
            self.med_cat_list = []
            self.med_cat_predecessors = 0
            if medicine_cat is not None:
                self.clan_cats.append(self.medicine_cat.ID)
                self.med_cat_list.append(self.medicine_cat.ID)
                if medicine_cat.status != 'medicine cat':
                    Cat.all_cats[medicine_cat.ID].status_change('medicine cat')
            self.med_cat_number = len(self.med_cat_list)  # Must do this after the medicine cat is added to the list.
            self.herbs = {}
            self.age = 0
            self.current_season = 'Newleaf'
            self.instructor = None  # This is the first cat in starclan, to "guide" the other dead cats there.
            self.biome = biome
            self.world_seed = world_seed
            self.camp_site = camp_site
            self.camp_bg = camp_bg
            self.game_mode = game_mode
            self.pregnancy_data = {}
            self.reputation = 80
            self.starting_members = starting_members
            if game_mode in ['expanded', 'cruel season']:
                self.freshkill_pile = Freshkill_Pile()
            else:
                self.freshkill_pile = None
            if self.biome == 'Forest' and self.camp_bg == 'camp3':
                self.cur_layout = self.layout_2

            self.faded_ids = []  # Stores ID's of faded cats, to ensure these IDs aren't reused.

            """
            Reputation is for loners/kittypets/outsiders in general that wish to join the clan. 
            it's a range from 1-100, with 30-70 being neutral, 71-100 being "welcoming",
            and 1-29 being "hostile". if you're hostile to outsiders, they will VERY RARELY show up.
            """

    def create_clan(self):
        """ This function is only called once a new clan is created in the 'clan created' screen, not every time
        the program starts"""
        self.instructor = Cat(status=choice(["warrior", "elder"]))
        self.instructor.dead = True
        update_sprite(self.instructor)
        self.add_cat(self.instructor)
        self.all_clans = []
        other_clans = []

        key_copy = tuple(Cat.all_cats.keys())
        for i in key_copy:  # Going through all currently existing cats
            # cat_class is a Cat-object
            not_found = True
            for x in self.starting_members:
                if Cat.all_cats[i] == x:
                    self.add_cat(Cat.all_cats[i])
                    not_found = False
            if Cat.all_cats[i] != self.leader and Cat.all_cats[i] != \
                    self.medicine_cat and Cat.all_cats[i] != \
                    self.deputy and Cat.all_cats[i] != \
                    self.instructor \
                    and not_found:
                Cat.all_cats[i].example = True
                self.remove_cat(Cat.all_cats[i].ID)

        # give thoughts,actions and relationships to cats
        for cat_id in Cat.all_cats:
            Cat.all_cats.get(cat_id).create_all_relationships()
            Cat.all_cats.get(cat_id).backstory = 'clan_founder'
            if Cat.all_cats.get(cat_id).status == 'apprentice':
                Cat.all_cats.get(cat_id).status_change('apprentice')
            Cat.all_cats.get(cat_id).thoughts()

        game.save_cats()
        number_other_clans = randint(3, 5)
        for _ in range(number_other_clans):
            self.all_clans.append(OtherClan())
        self.save_clan()
        game.save_clanlist(self.name)
        game.switches['clan_list'] = game.read_clans()
        # if map_available:
        #    save_map(game.map_info, game.clan.name)

        # CHECK IF CAMP BG IS SET -fail-safe in case it gets set to None-
        if game.switches['camp_bg'] is None:
            random_camp_options = ['camp1', 'camp2']
            random_camp = choice(random_camp_options)
            game.switches['camp_bg'] = random_camp
        if game.switches['camp_bg'] == 'camp3' and game.clan.biome == 'Forest':
            self.cur_layout = self.layout_2

        # if no game mode chosen, set to Classic
        if game.switches['game_mode'] is None:
            game.switches['game_mode'] = 'classic'
        if game.switches['game_mode'] == 'cruel_season':
            game.settings['disasters'] = True

    def add_cat(self, cat):  # cat is a 'Cat' object
        """ Adds cat into the list of clan cats"""
        if cat.ID in Cat.all_cats.keys(
        ) and cat.ID not in self.clan_cats:
            self.clan_cats.append(cat.ID)

    def add_to_starclan(self, cat):  # Same as add_cat
        """ Places the dead cat into starclan. It should not be removed from the list of cats in the clan"""
        if cat.ID in Cat.all_cats.keys(
        ) and cat.dead and cat.ID not in self.starclan_cats:
            # The dead-value must be set to True before the cat can go to starclan
            self.starclan_cats.append(cat.ID)
            if cat.ID in self.med_cat_list:
                self.med_cat_list.remove(cat.ID)
                self.med_cat_predecessors += 1

    def add_to_clan(self, cat):
        if cat.ID in Cat.all_cats.keys(
        ) and not cat.outside and cat.ID in Cat.outside_cats.keys():
            # The outside-value must be set to True before the cat can go to cotc
            self.clan_cats.append(cat.ID)
            Cat.outside_cats.pop(cat.ID)
            cat.clan = str(game.clan.name)

    def add_to_outside(self, cat):  # same as add_cat
        """ Places the gone cat into cotc. It should not be removed from the list of cats in the clan"""
        if cat.ID in Cat.all_cats.keys(
        ) and cat.outside and cat.ID not in Cat.outside_cats.keys():
            # The outside-value must be set to True before the cat can go to cotc
            Cat.outside_cats.update({cat.ID: cat})
            if cat.status != 'leader':  # takes away the suffix unless the cat used to be leader
                cat.suffix = ''

    def add_to_darkforest(self, cat):  # Same as add_cat
        """ Places the dead cat into the dark forest. It should not be removed from the list of cats in the clan"""
        if cat.ID in Cat.all_cats.keys(
        ) and cat.dead and cat.df is False:
            cat.df = True
            cat.thought = "Is distraught after being sent to the Place of No Stars"
            if cat in self.starclan_cats:
                self.starclan_cats.remove(cat.ID)
            if cat.ID in self.med_cat_list:
                self.med_cat_list.remove(cat.ID)
                self.med_cat_predecessors += 1
            update_sprite(Cat.all_cats[str(cat)])
            # The dead-value must be set to True before the cat can go to starclan

    def remove_cat(self, ID):  # ID is cat.ID
        """This function is for completely removing the cat from the game, it's not meant for a cat that's
        simply dead"""

        if Cat.all_cats[ID] in Cat.all_cats_list:
            Cat.all_cats_list.remove(Cat.all_cats[ID])

        if ID in Cat.all_cats.keys():
            Cat.all_cats.pop(ID)
            if ID in self.clan_cats:
                self.clan_cats.remove(ID)
            if ID in self.starclan_cats:
                self.starclan_cats.remove(ID)

    def __repr__(self):
        if self.name is not None:
            return f'{self.name}: led by {self.leader.name} with {self.medicine_cat.name} as med. cat'

        else:
            return 'No clan'

    def new_leader(self, leader):
        if leader:
            self.leader = leader
            Cat.all_cats[leader.ID].status_change('leader')
            self.leader_predecessors += 1
            self.leader_lives = 9
        game.switches['new_leader'] = None

    def new_deputy(self, deputy):
        if deputy:
            self.deputy = deputy
            Cat.all_cats[deputy.ID].status_change('deputy')
            self.deputy_predecessors += 1

    def new_medicine_cat(self, medicine_cat):
        if medicine_cat:
            if medicine_cat.status != 'medicine cat':
                Cat.all_cats[medicine_cat.ID].status_change('medicine cat')
            if medicine_cat.ID not in self.med_cat_list:
                self.med_cat_list.append(medicine_cat.ID)
            medicine_cat = self.med_cat_list[0]
            self.medicine_cat = Cat.all_cats[medicine_cat]
            self.med_cat_number = len(self.med_cat_list)

    def remove_med_cat(self, medicine_cat):
        # Removes a med cat. Use when retiring, or switching to warrior
        if medicine_cat:
            if medicine_cat.ID in game.clan.med_cat_list:
                game.clan.med_cat_list.remove(medicine_cat.ID)
                game.clan.med_cat_number = len(game.clan.med_cat_list)
            if self.medicine_cat:
                if medicine_cat.ID == self.medicine_cat.ID:
                    if game.clan.med_cat_list:
                        game.clan.medicine_cat = Cat.fetch_cat(game.clan.med_cat_list[0])
                        game.clan.med_cat_number = len(game.clan.med_cat_list)
                    else:
                        game.clan.medicine_cat = None

    def switch_clans(self, clan):
        game.save_clanlist(clan)
        game.cur_events_list.clear()

        # game.rpc.close()
        pygame.display.quit()
        pygame.quit()
        exit()

    def save_clan(self):

        clan_data = {
            "clanname": self.name,
            "clanage": self.age,
            "biome": self.biome,
            "camp_bg": self.camp_bg,
            "worldseed": self.world_seed,
            "camp_site_1": self.camp_site[0],
            "camp_site_2": self.camp_site[1],
            "gamemode": self.game_mode,
            "instructor": self.instructor.ID,
            "reputation": self.reputation,
            "mediated": game.mediated
        }

        # LEADER DATA
        if self.leader:
            clan_data["leader"] = self.leader.ID
            clan_data["leader_lives"] = self.leader_lives
        else:
            clan_data["leader"] = None

        clan_data["leader_predecessors"] = self.leader_predecessors

        # DEPUTY DATA
        if self.deputy:
            clan_data["deputy"] = self.deputy.ID
        else:
            clan_data["deputy"] = None

        clan_data["deputy_predecessors"] = self.deputy_predecessors

        # MED CAT DATA
        if self.medicine_cat:
            clan_data["med_cat"] = self.medicine_cat.ID
        else:
            clan_data["med_cat"] = None
        clan_data["med_cat_number"] = self.med_cat_number
        clan_data["med_cat_predecessors"] = self.med_cat_predecessors

        # LIST OF CLAN CATS
        clan_data['clan_cats'] = ",".join([str(i) for i in self.clan_cats])

        clan_data["faded_cats"] = ",".join([str(i) for i in self.faded_ids])

        # Patrolled cats
        clan_data["patrolled_cats"] = [str(i) for i in game.patrolled]

        # OTHER CLANS
        # Clan Names
        clan_data["other_clans_names"] = ",".join([str(i.name) for i in self.all_clans])
        clan_data["other_clans_relations"] = ",".join([str(i.relations) for i in self.all_clans])
        clan_data["other_clan_temperament"] = ",".join([str(i.temperament) for i in self.all_clans])

        self.save_herbs(game.clan)
        if game.clan.game_mode in ['expanded', 'cruel season']:
            self.save_freshkill_pile(game.clan)

        with open(f'saves/{self.name}clan.json', 'w') as write_file:
            json_string = ujson.dumps(clan_data, indent=4)
            write_file.write(json_string)

        list_data = self.name + "\n"
        for i in range(len(game.switches['clan_list'])):
            if game.switches['clan_list'][i] != self.name:
                list_data = list_data + game.switches['clan_list'][i] + "\n"
        with open('saves/clanlist.txt', 'w') as write_file:
            write_file.write(list_data)

    def load_clan(self):
        if os.path.exists('saves/' + game.switches['clan_list'][0] + 'clan.json'):
            self.load_clan_json()
        elif os.path.exists('saves/' + game.switches['clan_list'][0] + 'clan.txt'):
            self.load_clan_txt()
        else:
            game.switches['error_message'] = "There was an error loading the clan.txt"
        pass

    def load_clan_txt(self):
        other_clans = []
        if game.switches['clan_list'] == '':
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return
        if game.switches['clan_list'][0].strip() == '':
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return
        game.switches['error_message'] = "There was an error loading the clan.txt"
        with open('saves/' + game.switches['clan_list'][0] + 'clan.txt',
                  'r') as read_file:
            clan_data = read_file.read()
        clan_data = clan_data.replace('\t', ',')
        sections = clan_data.split('\n')
        if len(sections) == 7:
            general = sections[0].split(',')
            leader_info = sections[1].split(',')
            deputy_info = sections[2].split(',')
            med_cat_info = sections[3].split(',')
            instructor_info = sections[4]
            members = sections[5].split(',')
            other_clans = sections[6].split(',')
        elif len(sections) == 6:
            general = sections[0].split(',')
            leader_info = sections[1].split(',')
            deputy_info = sections[2].split(',')
            med_cat_info = sections[3].split(',')
            instructor_info = sections[4]
            members = sections[5].split(',')
            other_clans = []
        else:
            general = sections[0].split(',')
            leader_info = sections[1].split(',')
            deputy_info = 0, 0
            med_cat_info = sections[2].split(',')
            instructor_info = sections[3]
            members = sections[4].split(',')
            other_clans = []
        if len(general) == 9:
            if general[3] == 'None':
                general[3] = 'camp1'
            elif general[4] == 'None':
                general[4] = 0
            elif general[7] == 'None':
                general[7] = 'classic'
            elif general[8] == 'None':
                general[8] = 50
            game.clan = Clan(general[0],
                             Cat.all_cats[leader_info[0]],
                             Cat.all_cats.get(deputy_info[0], None),
                             Cat.all_cats.get(med_cat_info[0], None),
                             biome=general[2],
                             camp_bg=general[3],
                             world_seed=int(general[4]),
                             camp_site=(int(general[5]),
                                        int(general[6])),
                             game_mode=general[7]
                             )
            game.clan.reputation = general[8]
        elif len(general) == 8:
            if general[3] == 'None':
                general[3] = 'camp1'
            elif general[4] == 'None':
                general[4] = 0
            elif general[7] == 'None':
                general[7] = 'classic'
            game.clan = Clan(general[0],
                             Cat.all_cats[leader_info[0]],
                             Cat.all_cats.get(deputy_info[0], None),
                             Cat.all_cats.get(med_cat_info[0], None),
                             biome=general[2],
                             camp_bg=general[3],
                             world_seed=int(general[4]),
                             camp_site=(int(general[5]),
                                        int(general[6])),
                             game_mode=general[7],
                             )
        elif len(general) == 7:
            if general[4] == 'None':
                general[4] = 0
            elif general[3] == 'None':
                general[3] = 'camp1'
            game.clan = Clan(general[0],
                             Cat.all_cats[leader_info[0]],
                             Cat.all_cats.get(deputy_info[0], None),
                             Cat.all_cats.get(med_cat_info[0], None),
                             biome=general[2],
                             camp_bg=general[3],
                             world_seed=int(general[4]),
                             camp_site=(int(general[5]),
                                        int(general[6])),
                             )
        elif len(general) == 3:
            game.clan = Clan(general[0], Cat.all_cats[leader_info[0]],
                             Cat.all_cats.get(deputy_info[0], None),
                             Cat.all_cats.get(med_cat_info[0], None),
                             general[2])
        else:
            game.clan = Clan(general[0], Cat.all_cats[leader_info[0]],
                             Cat.all_cats.get(deputy_info[0], None),
                             Cat.all_cats.get(med_cat_info[0], None))
        game.clan.age = int(general[1])
        game.clan.current_season = game.clan.seasons[game.clan.age % 12]
        game.clan.leader_lives, game.clan.leader_predecessors = int(
            leader_info[1]), int(leader_info[2])

        if len(deputy_info) > 1:
            game.clan.deputy_predecessors = int(deputy_info[1])
        if len(med_cat_info) > 1:
            game.clan.med_cat_predecessors = int(med_cat_info[1])
        if len(med_cat_info) > 2:
            game.clan.med_cat_number = int(med_cat_info[2])
        if len(sections) > 4:
            if instructor_info in Cat.all_cats.keys():
                game.clan.instructor = Cat.all_cats[instructor_info]
                game.clan.add_cat(game.clan.instructor)
        else:
            game.clan.instructor = Cat(
                status=choice(["warrior", "warrior", "elder"]))
            update_sprite(game.clan.instructor)
            game.clan.instructor.dead = True
            game.clan.add_cat(game.clan.instructor)
        if other_clans != [""]:
            for other_clan in other_clans:
                other_clan_info = other_clan.split(';')
                self.all_clans.append(
                    OtherClan(other_clan_info[0], int(other_clan_info[1]), other_clan_info[2]))

        else:
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())

        for cat in members:
            if cat in Cat.all_cats.keys():
                game.clan.add_cat(Cat.all_cats[cat])
                game.clan.add_to_starclan(Cat.all_cats[cat])
            else:
                print('WARNING: Cat not found:', cat)
        self.load_pregnancy(game.clan)
        game.switches['error_message'] = ''

    def load_clan_json(self):
        other_clans = []
        if game.switches['clan_list'] == '':
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return
        if game.switches['clan_list'][0].strip() == '':
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return

        game.switches['error_message'] = "There was an error loading the clan.json"
        with open('saves/' + game.switches['clan_list'][0] + 'clan.json',
                  'r') as read_file:
            clan_data = ujson.loads(read_file.read())

        if clan_data["leader"]:
            leader = Cat.all_cats[clan_data["leader"]]
            leader_lives = clan_data["leader_lives"]
        else:
            leader = None
            leader_lives = 0

        if clan_data["deputy"]:
            deputy = Cat.all_cats[clan_data["deputy"]]
        else:
            deputy = None

        if clan_data["med_cat"]:
            med_cat = Cat.all_cats[clan_data["med_cat"]]
        else:
            med_cat = None

        game.clan = Clan(clan_data["clanname"],
                         leader,
                         deputy,
                         med_cat,
                         biome=clan_data["biome"],
                         camp_bg=clan_data["camp_bg"],
                         camp_site=(int(clan_data["camp_site_1"]), int(clan_data["camp_site_2"])),
                         game_mode=clan_data["gamemode"])

        game.clan.reputation = int(clan_data["reputation"])

        game.clan.age = clan_data["clanage"]
        game.clan.current_season = game.clan.seasons[game.clan.age % 12]
        game.clan.leader_lives = leader_lives
        game.clan.leader_predecessors = clan_data["leader_predecessors"]

        game.clan.deputy_predecessors = clan_data["deputy_predecessors"]
        game.clan.med_cat_predecessors = clan_data["med_cat_predecessors"]
        game.clan.med_cat_number = clan_data["med_cat_number"]

        # Instructor Info
        if clan_data["instructor"] in Cat.all_cats.keys():
            game.clan.instructor = Cat.all_cats[clan_data["instructor"]]
            game.clan.add_cat(game.clan.instructor)
        else:
            game.clan.instructor = Cat(
                status=choice(["warrior", "warrior", "elder"]))
            update_sprite(game.clan.instructor)
            game.clan.instructor.dead = True
            game.clan.add_cat(game.clan.instructor)

        for name, relation, temper in zip(clan_data["other_clans_names"].split(","),
                                          clan_data["other_clans_relations"].split(","),
                                          clan_data["other_clan_temperament"].split(",")):
            game.clan.all_clans.append(OtherClan(name, int(relation), temper))

        for cat in clan_data["clan_cats"].split(","):
            if cat in Cat.all_cats.keys():
                game.clan.add_cat(Cat.all_cats[cat])
                game.clan.add_to_starclan(Cat.all_cats[cat])
            else:
                print('WARNING: Cat not found:', cat)

        if "faded_cats" in clan_data:
            if clan_data["faded_cats"].strip():  # Check for empty string
                for cat in clan_data["faded_cats"].split(","):
                    game.clan.faded_ids.append(cat)

        # Patrolled cats
        if "patrolled_cats" in clan_data:
            for cat in clan_data["patrolled_cats"]:
                if cat in Cat.all_cats:
                    game.patrolled.append(Cat.all_cats[cat])

        # Mediated flag
        if "mediated" in clan_data:
            if type(clan_data["mediated"]) != list:
                game.mediated = []
            else:
                game.mediated = clan_data["mediated"]

        self.load_pregnancy(game.clan)
        self.load_herbs(game.clan)
        if game.clan.game_mode in ['expanded', 'cruel season']:
            self.load_freshkill_pile(game.clan)
        game.switches['error_message'] = ''

    def load_herbs(self, clan):
        if not game.clan.name:
            return
        file_path = f"saves/{game.clan.name}/herbs.json"
        if os.path.exists(file_path):
            with open(file_path,
                      'r') as read_file:
                clan.herbs = ujson.loads(read_file.read())

        else:
            # generate a random set of herbs since the clan didn't have any saved
            herbs = {}
            random_herbs = random.choices(HERBS, k=random.randrange(3, 8))
            for herb in random_herbs:
                herbs.update({herb: random.randint(1, 3)})
            with open(file_path, 'w') as rel_file:
                json_string = ujson.dumps(herbs, indent=4)
                rel_file.write(json_string)
            clan.herbs = herbs

    def save_herbs(self, clan):
        if not game.clan.name:
            return
        file_path = f"saves/{game.clan.name}/herbs.json"
        try:
            with open(file_path, 'w') as file:
                json_string = ujson.dumps(clan.herbs, indent=4)
                file.write(json_string)
        except:
            print(f"ERROR: Saving the herb data didn't work.")

    def load_pregnancy(self, clan):
        if not game.clan.name:
            return
        file_path = f"saves/{game.clan.name}/pregnancy.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as read_file:
                clan.pregnancy_data = ujson.load(read_file)
        else:
            clan.pregnancy_data = {}

    def save_pregnancy(self, clan):
        if not game.clan.name:
            return
        file_path = f"saves/{game.clan.name}/pregnancy.json"
        try:
            with open(file_path, 'w') as file:
                json_string = ujson.dumps(clan.pregnancy_data, indent=4)
                file.write(json_string)
        except:
            print(f"ERROR: Saving the pregnancy data didn't work.")

    def load_freshkill_pile(self, clan):
        if not game.clan.name or clan.game_mode == 'classic':
            return

        file_path = f"saves/{game.clan.name}/freshkill_pile.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as read_file:
                    pile = ujson.load(read_file)
                    clan.freshkill_pile = Freshkill_Pile(pile)

                file_path = f"saves/{game.clan.name}/nutrition_info.json"
                if os.path.exists(file_path) and clan.freshkill_pile:
                    with open(file_path, 'r') as read_file:
                        nutritions = ujson.load(read_file)
                        for k, nutr in nutritions.items():
                            nutrition = Nutrition()
                            nutrition.max_score = nutr['max_score']
                            nutrition.current_score = nutr['current_score']
                            clan.freshkill_pile.nutrition_info[k] = nutrition
            else:
                clan.freshkill_pile = Freshkill_Pile()
        except:
            clan.freshkill_pile = Freshkill_Pile()

    def save_freshkill_pile(self, clan):
        if clan.game_mode == "classic" or not clan.freshkill_pile:
            return

        try:
            with open(f"saves/{game.clan.name}/freshkill_pile.json", 'w') as rel_file:
                json_string = ujson.dumps(clan.freshkill_pile.pile, indent=4)
                rel_file.write(json_string)
        except:
            print(f"ERROR: Saving the freshkill pile didn't work.")

        try:
            with open(f"saves/{game.clan.name}/nutrition_info.json", 'w') as rel_file:
                data = {}
                for k, nutr in clan.freshkill_pile.nutrition_info.items():
                    data[k] = {
                        "max_score": nutr.max_score,
                        "current_score": nutr.current_score,
                        "percentage": nutr.percentage,
                    }
                json_string = ujson.dumps(data, indent=4)
                rel_file.write(json_string)
        except:
            print(f"ERROR: Saving nutrition information of the freshkill pile didn't work.")


class OtherClan():

    def __init__(self, name='', relations=0, temperament=''):
        temperament_list = [
            'cunning', 'wary', 'logical', 'proud', 'stoic',
            'mellow', 'bloodthirsty', 'amiable', 'gracious'
        ]
        self.name = name or choice(names.normal_prefixes)
        self.relations = relations or randint(8, 12)
        self.temperament = temperament or choice(temperament_list)
        if self.temperament not in temperament_list:
            self.temperament = choice(temperament_list)

    def __repr__(self):
        return f"{self.name}Clan"


class StarClan():
    forgotten_stages = {
        0: [0, 100],
        10: [101, 200],
        30: [201, 300],
        60: [301, 400],
        90: [401, 500],
        100: [501, 502]
    }  # Tells how faded the cat will be in starclan by months spent
    dead_cats = {}

    def __init__(self):
        self.instructor = None

    def fade(self, cat):
        white = pygame.Surface((50, 50))
        fade_level = 0
        if cat.dead:
            for f in self.forgotten_stages.keys():
                if cat.dead_for in range(self.forgotten_stages[f][0],
                                         self.forgotten_stages[f][1]):
                    fade_level = f
        white.fill((255, 255, 255, fade_level))
        return white


clan_class = Clan()
clan_class.remove_cat(cat_class.ID)

HERBS = None
with open(f"resources/dicts/herbs.json", 'r') as read_file:
    HERBS = ujson.loads(read_file.read())
