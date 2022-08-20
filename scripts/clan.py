import json
from .cats import *
from .text import *
from .relationship import *
from sys import exit
import os

class Clan(object):
    leader_lives = 9
    clan_cats = []
    starclan_cats = []
    seasons = ['Newleaf', 'Newleaf', 'Newleaf', 'Greenleaf', 'Greenleaf', 'Greenleaf', 'Leaf-fall', 'Leaf-fall',
               'Leaf-fall', 'Leaf-bare', 'Leaf-bare', 'Leaf-bare', ]
    layout_1 = {'leader den': ('center', 100), 'medicine den': (100, 230), 'nursery': (-100, 230),
                'clearing': ('center', 300), 'apprentice den': (100, 450), 'warrior den': (-100, 450),
                'elder den': ('center', 500),
                'leader place': [('center', 120), (screen_x / 2 - 50, 170), (screen_x / 2, 170)],
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
    places_vacant = {'leader': [False, False, False],
                     'medicine': [False, False, False, False, False],
                     'nursery': [False, False, False, False, False, False, False, False, False, False, False],
                     'clearing': [False, False, False, False, False, False, False],
                     'apprentice': [False, False, False, False, False, False],
                     'warrior': [False, False, False, False, False, False, False, False],
                     'elder': [False, False, False, False, False]}

    age = 0
    current_season = 'Newleaf'
    all_clans = []

    def __init__(self, name="", leader=None, deputy=None, medicine_cat=None):
        if name != "":
            self.clan_cats = []
            self.starclan_cats = []
            self.all_clans = []
            self.name = name
            self.leader = leader
            if self.leader != None:
                self.leader.status_change('leader')
                self.clan_cats.append(self.leader)
            self.leader_predecessors = 0
            self.deputy = deputy
            if deputy is not None:
                self.deputy.status_change('deputy')
                self.clan_cats.append(self.deputy)
            self.deputy_predecessors = 0
            self.medicine_cat = medicine_cat
            if self.medicine_cat != None:
                self.medicine_cat.status_change('medicine cat')
                self.clan_cats.append(self.medicine_cat)
            self.med_cat_predecessors = 0
            self.age = 0
            self.current_season = 'Newleaf'
            self.instructor = None  # This is the first cat in starclan, to "guide" the other dead cats there.

    def create_clan(self):
        """ This function is only called once a new clan is created in the 'clan created' screen, not every time
        the program starts"""
        for current_cat_id in game.switches['members']:
            cat = game.choose_cats[current_cat_id]
            if (self.leader is not None and cat.ID != self.leader.ID) and\
                (self.deputy is not None and cat.ID != self.deputy.ID) and\
                (self.medicine_cat is not None and cat.ID != self.medicine_cat.ID):
                self.clan_cats.append(cat)

        self.instructor = Cat(status=choice(["warrior", "elder"]))
        self.instructor.dead = True
        self.instructor.update_sprite()
        self.add_to_starclan(self.instructor)


        # first create all relationships
        for cat in self.clan_cats:
            cat.thoughts()
            cat.create_relationships()
        # second link all relationships, after all are created
        for cat in self.clan_cats:
            cat.link_relationships()
        # third create interaction / thoughts (testing)
        for cat in self.clan_cats:     
            cat.create_interaction()
            cat.thoughts()

        self.save_clan()

    def add_cat(self, cat):  # cat is a 'Cat' object
        """ Adds cat into the list of clan cats."""
        self.clan_cats.append(cat)
        return

    def add_to_starclan(self, cat):  # Same as add_cat
        """ Places the dead cat into starclan and removes them from the list of cats in the clan."""
        self.clan_cats = list(filter(lambda iterate_cat: iterate_cat.ID != cat.ID, self.clan_cats))
        self.starclan_cats.append(cat)

    def remove_cat(self, ID):  # ID is cat.ID
        """This function is for completely removing the cat from the game, it's not meant for a cat that's
        simply dead."""
        self.clan_cats = list(filter(lambda iterate_cat: iterate_cat.ID != ID, self.clan_cats))

    def new_leader(self, leader):
        if leader:
            self.leader = leader
            self.leader.status_change('leader')
            self.leader_predecessors += 1
        game.switches['new_leader'] = None

    def new_deputy(self, deputy):
        if deputy:
            self.deputy = deputy
            self.deputy.status_change('deputy')
            self.deputy_predecessors += 1

    def new_medicine_cat(self, medicine_cat):
        if medicine_cat:
            self.medicine_cat = medicine_cat
            self.medicine_cat.status_change('medicine cat')
            self.med_cat_predecessors += 1

    def switch_clans(self):
        list_data = game.switches['switch_clan'] + "\n"
        for i in range(len(game.switches['clan_list'])):
            if game.switches['clan_list'][i] != game.switches['switch_clan']:
                list_data = list_data + game.switches['clan_list'][i] + "\n"
        game.cur_events_list.clear()
        with open('saves/clanlist.txt', 'w') as write_file:
            write_file.write(list_data)

        pygame.display.quit()
        pygame.quit()
        exit()

    def save_clan(self):
        """Save clan and then the cats."""
        directory = 'saves/' + self.name
        if not os.path.exists(directory):
            os.makedirs(directory)

        data = {
            "name": self.name,
            "age": self.age,
            "leader_id": self.leader.ID if self.leader is not None else None,
            "leader_live": self.leader_lives,
            "leader_predecessors": self.leader_predecessors,
            "deputy_id": self.deputy.ID if self.deputy is not None else None,
            "deputy_predecessors": self.deputy_predecessors,
            "medicine_id": self.medicine_cat.ID if self.medicine_cat is not None else None,
            "med_cat_predecessors": self.med_cat_predecessors,
            "instructor_id": self.instructor.ID if self.instructor is not None else None,
        }

        # save data
        with open('saves/' + self.name + '/clan.json', 'w') as write_file:
            json_string = json.dumps(data)
            write_file.write(json_string)

        #save
        list_data = self.name + "\n"
        for i in range(len(game.switches['clan_list'])):
            if game.switches['clan_list'][i] != self.name:
                list_data = list_data + game.switches['clan_list'][i] + "\n"

        with open('saves/clanlist.txt', 'w') as write_file:
            write_file.write(list_data)

        # save cats
        self.save_cats()

    def load_clan(self):
        """Checking the type of storage in order to subsequently select the appropriate loading function."""
        directory = 'saves/' + game.switches['clan_list'][0]
        if not os.path.exists(directory):
            self.old_load()
        else:
            self.new_load()

    def new_load(self):
        """New loading function for more readability."""
        if game.switches['clan_list'][0].strip() == '':
            return
        clanname = game.switches['clan_list'][0]
        clan_data = {}
        with open('saves/' + clanname + '/clan.json', 'r') as read_file:
            clan_data = json.loads(read_file.read())
        cat_data = self.load_cats_new()

        leader_relevant = list(filter(lambda inter_cat: inter_cat.ID == clan_data["leader_id"], cat_data))
        leader = None
        if len(leader_relevant) > 0:
            leader = leader_relevant[0]

        deputy_relevant = list(filter(lambda inter_cat: inter_cat.ID == clan_data["deputy_id"], cat_data))
        deputy = None
        if len(deputy_relevant) > 0:
            deputy = deputy_relevant[0]
        
        med_relevant = list(filter(lambda inter_cat: inter_cat.ID == clan_data["medicine_id"], cat_data))
        medicine = None
        if len(med_relevant) > 0:
            medicine = med_relevant[0]

        instructor_relevant = list(filter(lambda inter_cat: inter_cat.ID == clan_data["instructor_id"], cat_data))
        instructor = None
        if len(instructor_relevant) == 1:
            instructor = instructor_relevant[0]

        game.clan = Clan(name=clan_data["name"], leader=leader, deputy=deputy, medicine_cat=medicine)
        game.clan.clan_cats = list(filter(lambda cat: not cat.dead, cat_data))
        game.clan.starclan_cats = list(filter(lambda cat: cat.dead, cat_data))
        game.clan.age = clan_data["age"]
        game.clan.current_season = self.seasons[game.clan.age % 12]
        game.clan.instructor = instructor
        game.clan.leader_lives = clan_data["leader_live"]
        game.clan.leader_predecessors = clan_data["leader_predecessors"]
        game.clan.deputy_predecessors = clan_data["deputy_predecessors"]
        game.clan.med_cat_predecessors = clan_data["med_cat_predecessors"]

        for cat in game.clan.clan_cats:
            cat.create_relationships()
            # Update the apprentice
            if len(cat.apprentice) > 0:
                new_apprentices = []
                for cat_id in cat.apprentice:
                    relevant_list = list(filter(lambda cat: cat.ID == cat_id, game.clan.clan_cats))
                    if len(relevant_list) > 0:
                        # if the cat can't be found, drop the cat_id
                        new_apprentices.append(relevant_list[0])
                cat.apprentice = new_apprentices
            # Update the apprentice
            if len(cat.former_apprentices) > 0:
                new_apprentices = []
                for cat_id in cat.former_apprentices:
                    relevant_list = list(filter(lambda cat: cat.ID == cat_id, game.clan.clan_cats))
                    if len(relevant_list) > 0:
                        # if the cat can't be found, drop the cat_id
                        new_apprentices.append(relevant_list[0])
                cat.former_apprentices = new_apprentices

    def old_load(self):
        """Loading function for old saving form to transform into new form when saved."""
        if game.switches['clan_list'][0].strip() == '':
            return
        with open('saves/' + game.switches['clan_list'][0] + 'clan.txt', 'r') as read_file:
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

        all_cats = self.load_cats_old()

        if leader_info[0] == '':
            leader_info[0] = None
        leader_relevant = list(filter(lambda inter_cat: inter_cat.ID == leader_info[0], all_cats))
        leader = None
        if len(leader_relevant) == 1:
            leader = leader_relevant[0]

        if deputy_info[0] == '':
            deputy_info[0] = None
        deputy_relevant = list(filter(lambda inter_cat: inter_cat.ID == deputy_info[0], all_cats))
        deputy = None
        if len(deputy_relevant) == 1:
            deputy = deputy_relevant[0]
        
        if med_cat_info[0] == '':
            med_cat_info[0] = None
        med_relevant = list(filter(lambda inter_cat: inter_cat.ID == med_cat_info[0], all_cats))
        medicine = None
        if len(med_relevant) == 1:
            medicine = med_relevant[0]

        game.clan = Clan(general[0], leader, deputy, medicine)

        game.clan.age = int(general[1])
        game.clan.current_season = game.clan.seasons[game.clan.age % 12]
        game.clan.leader_lives, game.clan.leader_predecessors = int(leader_info[1]), int(leader_info[2])

        if len(deputy_info) > 1:
            game.clan.deputy_predecessors = int(deputy_info[1])
        game.clan.med_cat_predecessors = int(med_cat_info[1])
        
        instructor = None
        if len(sections) > 4:
            if instructor_info == '':
                instructor_info = None
            instructor_relevant = list(filter(lambda inter_cat: inter_cat.ID == instructor_info, all_cats))
            if len(instructor_relevant) == 1:
                instructor = instructor_relevant[0]
                game.clan.instructor = instructor
        else:
            game.clan.instructor = Cat(status=choice(["warrior", "warrior", "elder"]))
            game.clan.instructor.update_sprite()
            game.clan.instructor.dead = True
            game.clan.add_cat(game.clan.instructor)
        if other_clans and other_clans[0]:
            for other_clan in other_clans:
                other_clan_info = other_clan.split(';')
                game.clan.all_clans.append(OtherClan(other_clan_info[0], other_clan_info[1], other_clan_info[2]))

        else:
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
        
        game.clan.clan_cats = list(filter(lambda cat: not cat.dead, all_cats))
        game.clan.starclan_cats = list(filter(lambda cat: cat.dead, all_cats))
        if instructor not in game.clan.starclan_cats:
            game.clan.starclan_cats.append(instructor)

        for cat in game.clan.clan_cats:
            cat.create_relationships()
            # Update the apprentice
            if len(cat.apprentice) > 0:
                new_apprentices = []
                for cat_id in cat.apprentice:
                    relevant_list = list(filter(lambda cat: cat.ID == cat_id, game.clan.clan_cats))
                    if len(relevant_list) > 0:
                        # if the cat can't be found, drop the cat_id
                        new_apprentices.append(relevant_list[0])
                cat.apprentice = new_apprentices
            # Update the apprentice
            if len(cat.former_apprentices) > 0:
                new_apprentices = []
                for cat_id in cat.former_apprentices:
                    relevant_list = list(filter(lambda cat: cat.ID == cat_id, game.clan.clan_cats))
                    if len(relevant_list) > 0:
                        # if the cat can't be found, drop the cat_id
                        new_apprentices.append(relevant_list[0])
                cat.former_apprentices = new_apprentices
            
        for cat in game.clan.clan_cats:
            cat.link_relationships()

        for cat in game.clan.clan_cats:     
            cat.create_interaction()
        
    def save_cats(self):
        directory = 'saves/' + self.name
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        all_cats = self.clan_cats + self.starclan_cats

        # transform all cats and saves them
        clan_cats = []
        for cat in all_cats:
            form_app = []
            for apprentice in cat.former_apprentices:
                if type(apprentice) is str:
                    get_relevant = list(filter(lambda cat: cat.ID == apprentice, all_cats))
                    if len(get_relevant) > 0:
                        form_app.append(get_relevant[0])
            cat.former_apprentices = form_app
            cat_data = {
                "ID": cat.ID,
                "name_prefix": cat.name.prefix,
                "name_suffix": cat.name.suffix,
                "gender": cat.gender,
                "role": cat.status,
                "age": cat.age,
                "trait": cat.trait,
                "parent1_id": cat.parent1.ID if cat.parent1 else None,
                "parent2_id": cat.parent2.ID if cat.parent2 else None,
                "mentor_id": cat.mentor.ID if cat.mentor else None,
                "pelt_name": cat.pelt.name,
                "pelt_color": cat.pelt.colour,
                "pelt_white": cat.pelt.white,
                "pelt_length": cat.pelt.length,
                "spirit_kitten": cat.age_sprites['kitten'],
                "spirit_adolescent": cat.age_sprites['adolescent'],
                "spirit_adult": cat.age_sprites['adult'],
                "spirit_elder": cat.age_sprites['elder'],
                "eye_colour": cat.eye_colour,
                "reverse": cat.reverse,
                "white_patches": cat.white_patches,
                "pattern": cat.pattern,
                "skin": cat.skin,
                "skill": cat.skill,
                "spec": cat.specialty,
                "moons": cat.moons,
                "mate_id": cat.mate.ID if cat.mate else None,
                "dead": cat.dead,
                "spirit_dead": cat.age_sprites['dead'],
                "scar2": cat.specialty2,
                "experience": cat.experience,
                "dead_for_moons": cat.dead_for,
                "apprentice": [appr.ID for appr in cat.apprentice],
                "former_apprentices" :[appr.ID for appr in cat.former_apprentices]
            }
            clan_cats.append(cat_data)
            
            # save relationships for each cat
            relationship_dir = directory + '/relationships' 
            if not os.path.exists(relationship_dir):
                os.makedirs(relationship_dir)
            
            rel = []
            for r in cat.relationships:
                r_data = {
                    "cat_from_id": r.cat_from.ID,
                    "cat_to_id": r.cat_to.ID,
                    "mates": r.mates,
                    "family": r.family,
                    "romantic_love": r.romantic_love,
                    "like": r.like,
                    "dislike": r.dislike,
                    "admiration": r.admiration,
                    "comfortable": r.comfortable,
                    "jealousy": r.jealousy,
                    "trust": r.trust 
                }
                rel.append(r_data)

            with open(relationship_dir + '/' + cat.ID + '_relations.json', 'w') as rel_file:
                json_string = json.dumps(rel)
                rel_file.write(json_string)

        with open('saves/' + self.name + '/clan_cats.json', 'w') as write_file:
            json_string = json.dumps(clan_cats)
            write_file.write(json_string)

    def load_cats_new(self):
        """ """
        all_cats = []
        clanname = game.switches['clan_list'][0]
        with open('saves/' + clanname + '/clan_cats.json', 'r') as read_file:
            cat_data = json.loads(read_file.read())

        # create new cat objects
        for cat in cat_data:
            new_pelt = choose_pelt(cat["gender"], cat["pelt_color"], cat["pelt_white"], cat["pelt_name"], cat["pelt_length"], True)
            new_cat = Cat(prefix=cat["name_prefix"], gender=cat["gender"], status=cat["role"],
                              parent1=None, parent2=None, moons=cat["moons"], pelt=new_pelt,
                              eye_colour=cat["eye_colour"], suffix=cat["name_suffix"], ID=cat["ID"])
            new_cat.age = cat["age"]
            new_cat.trait = cat["trait"]
            new_cat.mentor = cat["mentor_id"]
            new_cat.mate = cat["mate_id"]
            new_cat.parent1 = cat["parent1_id"]
            new_cat.parent2 = cat["parent2_id"]
            new_cat.apprentice = cat["apprentice"]
            new_cat.former_apprentices = cat["former_apprentices"]
            new_cat.age_sprites['kitten'] = cat["spirit_kitten"]
            new_cat.age_sprites['adolescent'] = cat["spirit_adolescent"]
            new_cat.age_sprites['adult'] = cat["spirit_adult"]
            new_cat.age_sprites['elder'] = cat["spirit_elder"]
            new_cat.eye_colour = cat["eye_colour"]
            new_cat.reverse = cat["reverse"]
            new_cat.white_patches = cat["white_patches"]
            new_cat.pattern = cat["pattern"]
            new_cat.skin = cat["skin"]
            new_cat.skill = cat["skill"]
            new_cat.specialty = cat["spec"]
            new_cat.moons = cat["moons"]
            new_cat.dead = cat["dead"]
            new_cat.age_sprites['dead'] = cat["spirit_dead"]
            new_cat.specialty2 = cat["scar2"]
            new_cat.experience = cat["experience"]
            new_cat.dead_for = cat["dead_for_moons"]
            all_cats.append(new_cat)

        # replace cat ids with cat objects and creat relationships
        for cat in all_cats:
            mate_relevant = list(filter(lambda inter_cat: inter_cat.ID == cat.mate, all_cats))
            cat.mate = None
            if len(mate_relevant) == 1:
                cat.mate = mate_relevant[0]
        
            parten1_relevant = list(filter(lambda inter_cat: inter_cat.ID == cat.parent1, all_cats))
            cat.parent1 = None
            if len(parten1_relevant) == 1:
                cat.parent1 = parten1_relevant[0]

            parten2_relevant = list(filter(lambda inter_cat: inter_cat.ID == cat.parent2, all_cats))
            cat.parent2 = None
            if len(parten2_relevant) == 1:
                cat.parent2 = parten2_relevant[0]

            mentor_relevant = list(filter(lambda inter_cat: inter_cat.ID == cat.mentor, all_cats))
            cat.mentor = None
            if len(mentor_relevant) == 1:
                cat.mentor = mentor_relevant[0]
            
            # creat relationships if cat 
            with open('saves/' + clanname + '/relationships/' + cat.ID + '_relations.json', 'r') as read_file:
                rel_data = json.loads(read_file.read())
                relationships = []
                for rel in rel_data:
                    relevant_cat_list = list(filter(lambda inter_cat: inter_cat.ID == rel['cat_to_id'], all_cats))
                    if len(relevant_cat_list) > 0:
                        cat_to = relevant_cat_list[0]
                        new_rel = Relationship(cat_from=cat,cat_to=cat_to,
                                                mates=rel['mates'],family=rel['family'],
                                                romantic_love=rel['romantic_love'],
                                                like=rel['like'], dislike=rel['dislike'],
                                                admiration=rel['admiration'],
                                                comfortable=rel['comfortable'],
                                                jealousy=rel['jealousy'],trust=rel['trust'])
                        relationships.append(new_rel)
                cat.relationships = relationships
            cat.update_sprite()
        
        return all_cats

    def load_cats_old(self):
        """ """
        if game.switches['clan_list'][0].strip() == '':
            cat_data = ''
        else:
            if os.path.exists('saves/' + game.switches['clan_list'][0] + 'cats.csv'):
                with open('saves/' + game.switches['clan_list'][0] + 'cats.csv', 'r') as read_file:
                    cat_data = read_file.read()
            else:
                with open('saves/' + game.switches['clan_list'][0] + 'cats.txt', 'r') as read_file:
                    cat_data = read_file.read()

        if len(cat_data) > 0:
            cat_data = cat_data.replace('\t', ',')
            all_cats = []
            for i in cat_data.split('\n'):
                # CAT: ID(0) - prefix:suffix(1) - gender(2) - status(3) - age(4) - trait(5) - parent1(6) - parent2(7)
                #  - mentor(8)
                # PELT: pelt(9) - colour(10) - white(11) - length(12)
                # SPRITE: kitten(13) - apprentice(14) - warrior(15) - elder(16) - eye colour(17) - reverse(18)
                # - white patches(19) - pattern(20) - skin(21) - skill(22) - NONE(23) - spec(24) - moons(25) - mate(26)
                # dead(27) - SPRITE:dead(28)
                if i.strip() != '':
                    attr = i.split(',')
                    for x in range(len(attr)):
                        attr[x] = attr[x].strip()
                        if attr[x] in ['None', 'None ']:
                            attr[x] = None
                        elif attr[x].upper() == 'TRUE':
                            attr[x] = True
                        elif attr[x].upper() == 'FALSE':
                            attr[x] = False

                    game.switches['error_message'] = 'There was an error loading cat # ' + str(attr[0])

                    the_pelt = choose_pelt(attr[2], attr[10], attr[11], attr[9], attr[12], True)
                    the_cat = Cat(ID=attr[0], prefix=attr[1].split(':')[0], suffix=attr[1].split(':')[1], gender=attr[2], status=attr[3], pelt=the_pelt, parent1=attr[6],
                                  parent2=attr[7], eye_colour=attr[17])
                    the_cat.age, the_cat.mentor = attr[4], attr[8]
                    the_cat.age_sprites['kitten'], the_cat.age_sprites['adolescent'] = int(attr[13]), int(attr[14])
                    the_cat.age_sprites['adult'], the_cat.age_sprites['elder'] = int(attr[15]), int(attr[16])
                    the_cat.age_sprites['young adult'], the_cat.age_sprites['senior adult'] = int(attr[15]), int(attr[15])
                    the_cat.reverse, the_cat.white_patches, the_cat.pattern = attr[18], attr[19], attr[20]
                    the_cat.trait, the_cat.skin, the_cat.specialty = attr[5], attr[21], attr[24]

                    if len(attr) > 29:
                        the_cat.specialty2 = attr[29]
                    else:
                        the_cat.specialty2 = None

                    if len(attr) > 30:
                        the_cat.experience = int(attr[30])
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        the_cat.experience_level = experiencelevels[math.floor(int(the_cat.experience) / 10)]

                    else:
                        the_cat.experience = 0

                    if len(attr) > 25:
                        # Attributes that are to be added after the update
                        the_cat.moons = int(attr[25])
                        if len(attr) >= 27:
                            # assigning mate to cat, if any
                            the_cat.mate = attr[26]
                        if len(attr) >= 28:
                            # Is the cat dead
                            the_cat.dead = attr[27]
                            the_cat.age_sprites['dead'] = attr[28]
                    if len(attr) > 31:
                        the_cat.dead_for = int(attr[31])
                    the_cat.skill = attr[22]

                    if len(attr) > 32 and attr[32] is not None:
                        the_cat.apprentice = attr[32].split(';')
                    if len(attr) > 33 and attr[33] is not None:
                        the_cat.former_apprentices = attr[33].split(';')
                    
                    all_cats.append(the_cat)

            game.switches['error_message'] = 'There was an error loading this clan\'s mentors/apprentices'

            for cat in all_cats:
                # Load the parents
                if cat.parent1 != None and cat.parent1 != "":
                    relevant_cat_list = list(filter(lambda iterate_cat: iterate_cat.ID == cat.parent1, all_cats))
                    if len(relevant_cat_list) > 0:
                        cat.parent1 = relevant_cat_list[0]
                    else:
                        cat.parent1 = None
                else:
                    cat.parent1 = None
                
                if cat.parent2 != None and cat.parent2 != "":
                    relevant_cat_list = list(filter(lambda iterate_cat: iterate_cat.ID == cat.parent2, all_cats))
                    if len(relevant_cat_list) > 0:
                        cat.parent2 = relevant_cat_list[0]
                    else:
                        cat.parent2 = None
                else:
                    cat.parent2 = None
                
                # Load the mate
                if cat.mate != None and cat.mate != "":
                    relevant_cat_list = list(filter(lambda iterate_cat: iterate_cat.ID == cat.mate, all_cats))
                    if len(relevant_cat_list) > 0:
                        cat.mate = relevant_cat_list[0]
                    else:
                        cat.mate = None
                else:
                    cat.mate = None

                # Load the mate
                if cat.mentor != None and cat.mentor != "":
                    relevant_cat_list = list(filter(lambda iterate_cat: iterate_cat.ID == cat.mentor, all_cats))
                    if len(relevant_cat_list) > 0:
                        cat.mentor = relevant_cat_list[0]
                    else:
                        cat.mentor = None
                else:
                    cat.mentor = None

                cat.update_sprite()

            game.switches['error_message'] = ''
        return all_cats


class OtherClan(object):
    def __init__(self, name='', relations=0, temperament=''):
        self.name = name or choice(names.normal_prefixes)
        self.relations = relations or randint(10, 15)
        self.temperament = temperament or choice(['bloodthirsty', 'righteous', 'strict', 'kind', 'calm', 'progressive', 'faithful', 'thoughtful', 'compassionate', 'logical', 'brave', 'altruistic', 'distant', 'competitive'])

    def __repr__(self):
        return f"{self.name}Clan"


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
clan_class.remove_cat(example_cat.ID)
