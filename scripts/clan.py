from .cats import *
from .text import *
from sys import exit


class Clan(object):
    leader_lives = 9
    clan_cats = []

    # Starclan
    starclan_cats = []
    seasons = ['Newleaf','Newleaf','Newleaf','Greenleaf','Greenleaf','Greenleaf','Leaf-fall','Leaf-fall','Leaf-fall','Leaf-bare','Leaf-bare','Leaf-bare',]

    layout_1 = {'leader den': ('center', 100), 'medicine den': (100, 230), 'nursery': (-100, 230),
                'clearing': ('center', 300), 'apprentice den': (100, 450), 'warrior den': (-100, 450),
                'elder den': ('center', 500),
                'leader place': [('center', 120), (screen_x/2-50, 170), (screen_x/2, 170)],
                'medicine place': [(70, 250), (120, 250), (170, 250), (100, 300), (150, 300)],
                'nursery place': [(-100, 250), (-150, 250), (-200, 250), (-70, 300), (-120, 300), (-170, 300),
                                  (-220, 300), (-70, 350), (-120, 350), (-170, 350), (-220, 350)],
                'clearing place': [('center', 320), (300, 370), (350, 370), (400, 370), (300, 420), (350, 420),
                                   (400, 420)],
                'apprentice place': [(70, 470), (120, 470), (170, 470), (100, 520), (150, 520), (200, 520)],
                'warrior place': [(-50, 470), (-100, 490), (-150, 470), (-200, 490), (-50, 520), (-100, 540),
                                  (-150, 520), (-200, 540)],
                'elder place': [(300, 520), (350, 520), (400, 520), (320, 570), (370, 570)]}

    cur_layout = layout_1
    places_vacant = {'leader': [False, False, False], 'medicine': [False, False, False, False, False],
                     'nursery': [False, False, False, False, False, False, False, False, False, False, False],
                     'clearing': [False, False, False, False, False, False, False],
                     'apprentice': [False, False, False, False, False, False],
                     'warrior': [False, False, False, False, False, False, False, False],
                     'elder': [False, False, False, False, False]}

    age = 0
    season = 'Newleaf'

    def __init__(self, name=None, leader=None, medicine_cat=None):
        if name is not None:
            self.name = name

            self.leader = leader
            self.leader.status_change('leader')
            self.leader_predecessors = 0
            self.deputy = 0
            self.clan_cats.append(self.leader.ID)

            self.medicine_cat = medicine_cat
            self.medicine_cat.status_change('medicine cat')
            self.med_cat_predecessors = 0
            self.clan_cats.append(self.medicine_cat.ID)

            self.age = 0
            self.season = 'Newleaf'

            # Starclan
            self.instructor = None  # This is the first cat in starclan, to "guide" the other dead cats there..
            # And help the player. It is a cat object
        else:
            self.name = None

    def create_clan(self):
        """ This function is only called once a new clan is created in the 'clan created' screen, not every time
        the program starts"""
        self.instructor = Cat(status=choice(["warrior", "warrior", "elder", "apprentice"]))
        self.instructor.update_sprite()
        self.instructor.dead = True
        self.add_cat(self.instructor)

        key_copy = tuple(cat_class.all_cats.keys()) 
        #for i in cat_class.all_cats.values():  # Going through all currently existing cats
        for i in key_copy:  # Going through all currently existing cats
            # cat_class is a Cat -object
            not_found = True
            for x in game.switches['members']:
                if cat_class.all_cats[i] == game.choose_cats[x]:
                    self.add_cat(cat_class.all_cats[i])
                    not_found = False
            if cat_class.all_cats[i] != game.choose_cats[game.switches['leader']] and cat_class.all_cats[i] != game.choose_cats[game.switches['medicine_cat']]\
                    and not_found:
                cat_class.all_cats[i].example = True
                self.remove_cat(cat_class.all_cats[i].ID)
                
        cat_class.save_cats()
        self.save_clan()

        # give thoughts/actions to cats
        cat_class.thoughts()

    def add_cat(self, cat):  # cat is a 'Cat' object
        """ Adds cat into the list of clan cats"""
        if cat.ID in cat_class.all_cats.keys() and cat.ID not in self.clan_cats:
            self.clan_cats.append(cat.ID)

    def add_to_starclan(self, cat):  # Same as add_cat
        """ Places the dead cat into starclan. It should not be removed from the list of cats in the clan"""
        if cat.ID in cat_class.all_cats.keys() and cat.dead and cat.ID not in self.starclan_cats:
            # The dead-value must be set to True before the cat can go to starclan
            self.starclan_cats.append(cat.ID)

    def remove_cat(self, ID):  # ID is cat.ID
        """This function is for completely removing the cat from the game, it's not meant for a cat that's
        simply dead"""
        if ID in cat_class.all_cats.keys():
            cat_class.all_cats.pop(ID)
            if ID in self.clan_cats:
                self.clan_cats.remove(ID)

    def __repr__(self):
        if self.name is not None:
            return self.name + ': led by ' + str(self.leader.name) + ' with ' + str(
                self.medicine_cat.name) + ' as med. cat'
        else:
            return 'No clan'

    def new_leader(self,leader):
        if leader:
            self.leader=leader
            cat_class.all_cats[leader.ID].status_change('leader')
            self.leader_predecessors+=1 
            game.clan.deputy=0
        game.switches['new_leader'] = None

    def switch_clans(self):
        list_data = game.switches['switch_clan'] + "\n"
        for i in range(len(game.switches['clan_list'])):
            if game.switches['clan_list'][i]!=game.switches['switch_clan']:
                list_data = list_data + game.switches['clan_list'][i] + "\n"
            
        with open('saves/clanlist.txt', 'w') as write_file:
            write_file.write(list_data)

        pygame.display.quit()
        pygame.quit()
        exit()

       # with open('saves/clanlist.txt', 'r') as read_file:
        #    clan_list = read_file.read()
        #    if_clans = len(clan_list)
       # if if_clans > 0:
        #    game.switches['clan_list'] = clan_list.split('\n')
        #cat_class.load_cats()
        #self.load_clan()

    def save_clan(self):
        # clan name - clan age
        data = self.name + ',' + str(self.age) + '\n'

        # leader ID - leader lives - number of leader predecessors
        data = data + self.leader.ID + ',' + str(self.leader_lives) + ',' + str(self.leader_predecessors) + ',' + str(self.deputy) + '\n'

        # med. cat ID - number of med. cat predecessors
        data = data + self.medicine_cat.ID + ',' + str(self.med_cat_predecessors) + '\n'

        # Instructor
        data = data + self.instructor.ID + '\n'

        # other members
        for a in range(len(self.clan_cats)):
            if a != len(self.clan_cats) - 1:
                if self.clan_cats[a] in cat_class.all_cats.keys():
                    data = data + self.clan_cats[a] + ','
            else:
                data = data + self.clan_cats[a]

        # save data
        with open('saves/' + self.name + 'clan.txt', 'w') as write_file:
            write_file.write(data)

        list_data = self.name + "\n"
        for i in range(len(game.switches['clan_list'])):
            if game.switches['clan_list'][i]!=self.name:
                list_data = list_data + game.switches['clan_list'][i] + "\n"
            
        with open('saves/clanlist.txt', 'w') as write_file:
            write_file.write(list_data)


    def load_clan(self):
        if game.switches['clan_list'][0].strip() == '':
            clan_data=''
        else:
            with open('saves/' + game.switches['clan_list'][0] + 'clan.txt', 'r') as read_file:
                clan_data = read_file.read()

            clan_data= clan_data.replace('\t',',')
            sections = clan_data.split('\n')

            general = sections[0].split(',')  # clan name(0) - clan age(1)
            leader_info = sections[1].split(',')  # leader ID(0) - leader lives(1) - leader predecessors(2) - deputy ID(3)
            med_cat_info = sections[2].split(',')  # med cat ID(0) - med cat predecessors(2)
            if len(sections) > 4:
                instructor_info = sections[3]  # instructor ID
                members = sections[4].split(',')  # rest of the members in order
            else:
                instructor_info = None
                members = sections[3].split(',')  # rest of the members in order

            game.clan = Clan(general[0], cat_class.all_cats[leader_info[0]], cat_class.all_cats[med_cat_info[0]])
            game.clan.age = int(general[1])
            game.clan.season=game.clan.seasons[game.clan.age%12]
            game.clan.leader_lives, game.clan.leader_predecessors = int(leader_info[1]), int(leader_info[2])
            if len(leader_info)>3:
                if int(leader_info[3])>0:
                    game.clan.deputy=cat_class.all_cats[leader_info[3]]
                else:
                   game.clan.deputy=0 
            else:
                game.clan.deputy=0
            game.clan.med_cat_predecessors = int(med_cat_info[1])

            # instructor
            if len(sections) > 4:
                if instructor_info in cat_class.all_cats.keys():
                    # Instructor exists
                    game.clan.instructor = cat_class.all_cats[instructor_info]
                    game.clan.add_cat(game.clan.instructor)  # This is to make sure the instructor isn't removed
                else:
                    # For whatever reason... instructor doesn't exist
                    game.clan.instructor = Cat(status=choice(["warrior", "warrior", "elder", "apprentice"]))
                    game.clan.instructor.update_sprite()
                    game.clan.instructor.dead = True
                    game.clan.add_cat(game.clan.instructor)  # This is to make sure the instructor isn't removed
            else:
                # instructor doesn't exist because the version converted is too old
                game.clan.instructor = Cat(status=choice(["warrior", "warrior", "elder", "apprentice"]))
                game.clan.instructor.update_sprite()
                game.clan.instructor.dead = True
                game.clan.add_cat(game.clan.instructor)  # This is to make sure the instructor isn't removed

            for x in members:
                if x in cat_class.all_cats.keys():
                    game.clan.add_cat(cat_class.all_cats[x])
                    game.clan.add_to_starclan(cat_class.all_cats[x])  # Cat is only added to starclan if dead-value is True
                else:
                    print('cat not found:', x)


class StarClan(object):
    forgotten_stages = {0: [0, 100], 10: [101, 200], 30: [201, 300], 60: [301, 400],
                        90: [401, 500], 100: [501, 502]}  # Tells how faded the cat will be in starclan by months spent
    dead_cats = {}

    def __init__(self):
        self.instructor = None

    def fade(self, cat):
        white = pygame.Surface((50, 50))
        fade_level = 0
        if cat.dead:
            for f in self.forgotten_stages.keys():
                if cat.dead_for in range(self.forgotten_stages[f][0], self.forgotten_stages[f][1]):
                    fade_level = f
        white.fill((255, 255, 255, fade_level))
        return white


clan_class = Clan()

# remove non-existent cats
clan_class.remove_cat(cat_class.ID)
clan_class.remove_cat(example_cat.ID)

