from random import choice, randint
import math
import os.path
import ujson

from .pelts import *
from .names import *
from .sprites import *
from .thoughts import *
from .appearance_utility import *
from scripts.conditions import Illness, Injury

from scripts.utility import *
from scripts.game_structure.game_essentials import *
from scripts.cat_relations.relationship import *


class Cat():
    used_screen = screen
    traits = [
        'adventurous', 'altruistic', 'ambitious', 'bloodthirsty', 'bold',
        'calm', 'careful', 'charismatic', 'childish', 'cold', 'compassionate',
        'confident', 'daring', 'empathetic', 'faithful', 'fierce', 'insecure',
        'lonesome', 'loving', 'loyal', 'nervous', 'patient', 'playful',
        'responsible', 'righteous', 'shameless', 'sneaky', 'strange', 'strict',
        'thoughtful', 'troublesome', 'vengeful', 'wise'
    ]
    kit_traits = [
        'attention-seeker', 'bossy', 'bouncy', 'bullying', 'charming',
        'daring', 'daydreamer', 'impulsive', 'inquisitive', 'insecure',
        'nervous', 'noisy', 'polite', 'quiet', 'sweet', 'troublesome'
    ]
    personality_groups = {
        'Outgoing': ['adventurous', 'bold', 'charismatic', 'childish', 'confident', 'daring',
                        'playful', 'righteous', 'attention-seeker', 'bouncy', 'charming', 'noisy'],
        'Benevolent': ['altruistic', 'compassionate', 'empathetic', 'faithful', 'loving',
                        'patient', 'responsible', 'thoughtful', 'wise', 'inquisitive',
                        'polite', 'sweet'],
        'Abrasive': ['ambitious', 'bloodthirsty', 'cold', 'fierce', 'shameless', 'strict',
                        'troublesome', 'vengeful', 'bossy', 'bullying', 'impulsive'],
        'Reserved': ['calm', 'careful', 'insecure', 'lonesome', 'loyal', 'nervous', 'sneaky',
                        'strange', 'daydreamer', 'quiet'],
        }
    ages = [
        'kitten', 'adolescent', 'young adult', 'adult', 'senior adult',
        'elder', 'dead'
    ]
    age_moons = {
        'kitten': [0, 5],
        'adolescent': [6, 11],
        'young adult': [12, 47],
        'adult': [48, 95],
        'senior adult': [96, 119],
        'elder': [120, 300]
    }
    gender_tags = {'female': 'F', 'male': 'M'}
    skills = [
        'good hunter', 'great hunter', 'fantastic hunter', 'smart',
        'very smart', 'extremely smart', 'good fighter', 'great fighter',
        'excellent fighter', 'good speaker', 'great speaker',
        'excellent speaker', 'strong connection to StarClan', 'good teacher',
        'great teacher', 'fantastic teacher'
    ]
    med_skills = [
        'good healer', 'great healer', 'fantastic healer', 'omen sight',
        'dream walker', 'strong connection to StarClan', 'lore keeper',
        'good teacher', 'great teacher', 'fantastic teacher', 'keen eye',
        'smart', 'very smart', 'extremely smart', 'good mediator',
        'great mediator', 'excellent mediator', 'clairvoyant', 'prophet'
    ]
    elder_skills = [
        'good storyteller', 'great storyteller', 'fantastic storyteller',
        'smart tactician', 'valuable tactician','valuable insight',
        'good mediator', 'great mediator', 'excellent mediator',
        'good teacher', 'great teacher', 'fantastic teacher',
        'strong connection to StarClan', 'smart', 'very smart', 'extremely smart',
        'good kitsitter', 'great kitsitter', 'excellent kitsitter', 'camp keeper', 'den builder',
    ]
    backstories = [
        'clanborn', 'half-clan1', 'half-clan2', 'outsider_roots1', 'outsider_roots2', 
        'loner1', 'loner2', 'kittypet1', 'kittypet2', 'rogue1', 'rogue2', 'abandoned1',
        'abandoned2', 'abandoned3', 'medicine_cat', 'otherclan', 'otherclan2', 'ostracized_warrior', 'disgraced', 
        'retired_leader', 'refugee', 'tragedy_survivor'
    ]

    all_cats = {}  # ID: object
    other_cats = {}  # cats outside the clan

    def __init__(self,
                 prefix=None,
                 gender=None,
                 status="kitten",
                 backstory="clanborn",
                 parent1=None,
                 parent2=None,
                 pelt=None,
                 eye_colour=None,
                 suffix=None,
                 ID=None,
                 moons=None,
                 example=False):
        self.gender = gender
        self.status = status
        self.backstory = backstory
        self.age = None
        self.skill = None
        self.trait = None
        self.parent1 = parent1
        self.parent2 = parent2
        self.pelt = pelt
        self.eye_colour = eye_colour
        self.mentor = None
        self.former_mentor = []
        self.apprentice = []
        self.former_apprentices = []
        self.relationships = []
        self.mate = None
        self.placement = None
        self.example = example
        self.dead = False
        self.died_by = None  # once the cat dies, tell the cause
        self.dead_for = 0  # moons
        self.thought = ''
        self.genderalign = None
        self.tortiebase = None
        self.pattern = None
        self.tortiepattern = None
        self.tortiecolour = None
        self.white_patches = None
        self.accessory = None
        self.birth_cooldown = 0
        self.siblings = []
        self.children = []
        self.illness = None
        self.injury = None

        # setting ID
        if ID is None:
            potential_ID = str(randint(10000, 9999999))
            while potential_ID in self.all_cats:
                potential_ID = str(randint(10000, 9999999))
            self.ID = potential_ID
        else:
            self.ID = ID

        # age and status
        if status is None and moons is None:
            self.age = choice(self.ages)
        elif moons is not None:
            for key_age in self.age_moons.keys():
                if moons in range(self.age_moons[key_age][0], self.age_moons[key_age][1]+1):
                    self.age = key_age
                    self.moons = moons
        else:
            if status in ['kitten', 'elder']:
                self.age = status
            elif status == 'apprentice':
                self.age = 'adolescent'
            elif status == 'medicine cat apprentice':
                self.age = 'adolescent'
            else:
                self.age = choice(['young adult', 'adult', 'adult', 'senior adult'])
            self.moons = random.randint(self.age_moons[self.age][0], self.age_moons[self.age][1])

        # personality trait and skill
        if self.trait is None:
            if self.status != 'kitten':
                self.trait = choice(self.traits)
            else:
                self.trait = choice(self.kit_traits)

        if self.skill is None:
            if self.moons <= 11:
                self.skill = '???'
            elif self.status == 'warrior':
                self.skill = choice(self.skills)
            elif self.moons >= 120 and self.status != 'leader' and self.status != 'medicine cat':
                self.skill = choice(self.elder_skills)
            elif self.status == 'medicine cat':
                self.skill = choice(self.med_skills)
            else:
                self.skill = choice(self.skills)

        # backstory
        if self.backstory == None:
            if self.skill == 'formerly a loner':
                backstory = choice(['loner1', 'loner2', 'rogue1', 'rogue2'])
                self.backstory = backstory
            elif self.skill == 'formerly a kittypet':
                backstory = choice(['kittypet1', 'kittypet2'])
                self.backstory = backstory
            else:
                self.backstory = 'clanborn'
        else:
            self.backstory = self.backstory

        # sex
        if self.gender is None:
            self.gender = choice(["female", "male"])
        self.g_tag = self.gender_tags[self.gender]

        #trans cat chances
        trans_chance = randint(0, 50)
        nb_chance = randint(0, 75)
        if self.gender == "female" and not self.age == 'kitten':
            if trans_chance == 1:
                self.genderalign = "trans male"
            elif nb_chance == 1:
                self.genderalign = "nonbinary"
            else:
                self.genderalign = self.gender
        if self.gender == "male" and not self.age == 'kitten':
            if trans_chance == 1:
                self.genderalign = "trans female"
            elif nb_chance == 1:
                self.genderalign = "nonbinary"
            else:
                self.genderalign = self.gender

        # NAME
        if self.pelt is not None:
            self.name = Name(status, prefix, suffix, self.pelt.colour,
                             self.eye_colour, self.pelt.name)
        else:
            self.name = Name(status, prefix, suffix, eyes=self.eye_colour)

        # APPEARANCE
        init_eyes(self)
        init_pelt(self)
        init_sprite(self)
        init_scars(self)
        init_accessories(self)
        init_white_patches(self)
        init_pattern(self)

        self.paralyzed = False
        self.no_kits = False
        self.exiled = False
        if self.genderalign is None:
            self.genderalign = self.gender

        # Sprite sizes
        self.sprite = None
        self.big_sprite = None
        self.large_sprite = None

        # experience and current patrol status
        self.in_camp = 1
        if self.age in ['kitten']:
            self.experience = 0
        elif self.age in ['adolescent']:
            self.experience = randint(0, 19)
        elif self.age in ['young adult']:
            self.experience = randint(10, 40)
        elif self.age in ['adult']:
            self.experience = randint(20, 50)
        elif self.age in ['senior adult']:
            self.experience = randint(30, 60)
        elif self.age in ['elder']:
            self.experience = randint(40, 70)
        else:
            self.experience = 0

        self.paralyzed = False
        self.no_kits = False
        self.exiled = False
        if self.genderalign is None:
            self.genderalign = self.gender

        # SAVE CAT INTO ALL_CATS DICTIONARY IN CATS-CLASS
        self.all_cats[self.ID] = self

    def __repr__(self):
        return self.ID

    def is_alive(self):
        return not self.dead

    def die(self):
        if self.status == 'leader' and game.clan.leader_lives > 0:
            return
        elif self.status == 'leader' and game.clan.leader_lives <= 0:
            self.dead = True
            game.clan.leader_lives = 0
        else:
            self.dead = True

        if self.mate is not None:
            self.mate = None
            if type(self.mate) == str:
                mate = Cat.all_cats.get(self.mate)
                mate.mate = None
            elif type(self.mate) == Cat:
                self.mate.mate = None

        for app in self.apprentice.copy():
            app.update_mentor()
        self.update_mentor()
        game.clan.add_to_starclan(self)

    def status_change(self, new_status):
        self.status = new_status
        self.name.status = new_status
        # revealing of traits and skills
        self.update_traits(self.status)
        # updates mentors
        if self.status == 'apprentice':
            self.update_mentor()
        elif self.status == 'medicine cat apprentice':
            self.update_med_mentor()
        # updates skill
        if self.status == 'warrior':
            self.skill = choice(self.skills)
            self.update_mentor()
        elif self.status == 'medicine cat':
            self.skill = choice(self.med_skills)
            self.update_med_mentor()
        else:
            self.skill = self.skill
        if self.status == 'elder':
            self.skill = choice(self.elder_skills)

        # update class dictionary
        self.all_cats[self.ID] = self

    def update_traits(self, new_status):
        if new_status == 'apprentice' or new_status == 'medicine cat apprentice':
            chance = randint(0, 5)  # chance for cat to gain trait that matches their previous trait's personality group
            if chance == 0:
                self.trait = choice(self.traits)
                print(self.name, 'NEW TRAIT TYPE: Random - CHANCE', chance)
            else:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        chosen_trait = choice(possible_trait)
                        if chosen_trait in self.kit_traits:
                            self.trait = choice(self.traits)
                            print(self.name, 'trait type chosen was kit trait -', self.trait,
                                  'chosen randomly instead')
                        else:
                            self.trait = chosen_trait
                            print(self.name, 'TRAIT TYPE:', x, 'NEW TRAIT PICKED:', chosen_trait, 'CHANCE:', chance)
        if new_status == 'warrior' or new_status == 'medicine cat':
            chance = randint(0, 5)  # chance for cat to gain new trait or keep old
            if chance == 0:
                self.trait = choice(self.traits)
                print(self.name, 'NEW TRAIT TYPE: Random - CHANCE', chance)
            elif chance == 1 or chance == 2:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        chosen_trait = choice(possible_trait)
                        if chosen_trait in self.kit_traits:
                            self.trait = choice(self.traits)
                            print(self.name, 'trait type chosen was kit trait -', self.trait,
                                  'chosen randomly instead')
                        else:
                            self.trait = chosen_trait
                            print(self.name, 'TRAIT TYPE:', x, 'NEW TRAIT PICKED:', chosen_trait, 'CHANCE:', chance)
            else:
                print(self.name, 'NEW TRAIT TYPE: No change', chance)

        if new_status == 'elder':
            chance = randint(0, 7)  # chance for cat to gain new trait or keep old
            if chance == 0:
                self.trait = choice(self.traits)
                print(self.name, 'NEW TRAIT TYPE: Random - CHANCE', chance)
            elif chance == 1:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        chosen_trait = choice(possible_trait)
                        if chosen_trait in self.kit_traits:
                            self.trait = choice(self.traits)
                            print(self.name, 'trait type chosen was kit trait -', self.trait,
                                  'chosen randomly instead')
                        else:
                            self.trait = chosen_trait
                            print(self.name, 'TRAIT TYPE:', x, 'NEW TRAIT PICKED:', chosen_trait, 'CHANCE:', chance)
            else:
                print(self.name, 'NEW TRAIT TYPE: No change', chance)

    def describe_cat(self):
        if self.genderalign == 'male' or self.genderalign == "transmasc" or self.genderalign == "trans male":
            sex = 'tom'
        elif self.genderalign == 'female' or self.genderalign == "transfem" or self.genderalign == "trans female":
            sex = 'she-cat'
        else:
            sex = 'cat'
        description = str(self.pelt.length).lower() + '-furred'
        description += ' ' + describe_color(self.pelt, self.tortiecolour, self.tortiepattern, self.white_patches) + ' ' + sex
        return description

# ---------------------------------------------------------------------------- #
#                              moon skip functions                             #
# ---------------------------------------------------------------------------- #

    def one_moon(self):
        """Handles a moon skip for a alive cat"""
        if self.exiled:
            # this is handled in events.py
            return

        self.moons += 1
        self.in_camp = 1
        if self.moons < 12:
            self.update_mentor()

        self.update_skill() # should only called sometimes not every moon?
        self.thoughts()
        self.create_interaction()

    def thoughts(self):
        all_cats = self.all_cats
        other_cat = random.choice(list(all_cats.keys()))
        countdown = int(len(all_cats) / 3)

        # get other cat
        while other_cat == self and countdown > 0:
            other_cat = random.choice(list(all_cats.keys()))
            countdown -= 1
        other_cat = all_cats.get(other_cat)

        # get possible thoughts
        thought_possibilities = get_thoughts(self, other_cat)
        chosen_thought = random.choice(thought_possibilities)

        # insert name if it is needed
        if "r_c" in chosen_thought:
            chosen_thought = chosen_thought.replace("r_c", str(other_cat.name))

        # insert thought
        self.thought = str(chosen_thought)

    def create_interaction(self):
        # if the cat has no relationships, skip
        if len(self.relationships) < 1 or self.relationships is None:
            return

        cats_to_choose = list(
            filter(lambda iter_cat_id: iter_cat_id != self.ID,
                   Cat.all_cats.copy()))
        # increase chance of cats, which are already befriended
        like_threshold = 30
        relevant_relationships = list(
            filter(lambda relation: relation.platonic_like >= like_threshold,
                   self.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.platonic_like >= like_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase chance of cats, which are already may be in love
        love_threshold = 30
        relevant_relationships = list(
            filter(lambda relation: relation.romantic_love >= love_threshold,
                   self.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.romantic_love >= love_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase the chance a kitten interact with other kittens
        if self.age == "kitten":
            kittens = list(
                filter(
                    lambda cat_id: self.all_cats.get(cat_id).age == "kitten" and
                    cat_id != self.ID, Cat.all_cats.copy()))
            amount = int(len(cats_to_choose) / 4)
            if len(kittens) > 0:
                amount = int(len(cats_to_choose) / len(kittens))
            cats_to_choose = cats_to_choose + kittens * amount

        # increase the chance a apprentice interact with other apprentices
        if self.age == "adolescent":
            apprentices = list(
                filter(
                    lambda cat_id: self.all_cats.get(cat_id).age == "adolescent"
                    and cat_id != self.ID, Cat.all_cats.copy()))
            amount = int(len(cats_to_choose) / 4)
            if len(apprentices) > 0:
                amount = int(len(cats_to_choose) / len(apprentices))
            cats_to_choose = cats_to_choose + apprentices * amount

        # choose cat and start
        random_id = random.choice(cats_to_choose)
        relevant_relationship_list = list(
            filter(
                lambda relation: str(relation.cat_to) == str(random_id) and
                not relation.cat_to.dead, self.relationships))
        random_cat = self.all_cats.get(random_id)
        kitten_and_exiled = random_cat is not None and random_cat.exiled and self.age == "kitten"

        # is also found in Relation_Events.MAX_ATTEMPTS
        attempts_left = 1000
        while len(relevant_relationship_list) < 1 or random_id == self.ID or kitten_and_exiled:
            random_id = random.choice(cats_to_choose)
            random_cat = self.all_cats.get(random_id)
            kitten_and_exiled = random_cat is not None and random_cat.exiled and self.age == "kitten"
            relevant_relationship_list = list(
                filter(
                    lambda relation: str(relation.cat_to) == str(random_id) and
                    not relation.cat_to.dead, self.relationships))
            attempts_left -= 1
            if attempts_left <= 0:
                return
        relevant_relationship = relevant_relationship_list[0]
        relevant_relationship.start_action()

    def update_skill(self):
        #checking that skill is correct
        if self.status == 'medicine cat' and self.skill not in self.med_skills:
            self.skill = choice(self.med_skills)

        if self.skill == '???':
            if self.status not in ['apprentice', 'medicine cat apprentice', 'kitten']:
                self.skill = choice(self.skills)

# ---------------------------------------------------------------------------- #
#                            !IMPORTANT INFORMATION!                           #
#   conditions ar currently not integrated, this are just the base functions   #
#    me (Lixxis) will integrate them after tests are written and completed     #
# ---------------------------------------------------------------------------- #

    def moon_skip_illness(self):
        "handles the moon skip for illness"
        if not self.is_ill():
            return

        if randint(1,self.illness.mortality) == 1:
            self.die()

        self.illness.duration -= 1
        if self.illness.duration <= 0:
            self.illness = None

    def moon_skip_injury(self):
        "handles the moon skip for injuries"
        if not self.is_injured():
            return
        
        if randint(1,self.injury.mortality) == 1:
            self.die()
        
        for risk in self.injury.risks:
            if randint(1,risk["chance"]) == 1:
                self.get_ill(risk["name"])

        self.injuries.duration -= 1
        if self.injuries.duration <= 0:
            self.injuries = None

# ---------------------------------------------------------------------------- #
#                                   relative                                   #
# ---------------------------------------------------------------------------- #

    def get_parents(self):
        """Returns list containing parents of cat."""
        parents = []
        if self.parent1 is not None:
            parents.append(self.parent1)
            if self.parent2 is not None:
                parents.append(self.parent2)
        return parents

    def get_siblings(self):
        """Returns list of the siblings."""
        return self.siblings

    def get_children(self):
        """Returns list of the children."""
        return self.children

    def is_grandparent(self, other_cat):
        """Check if the cat is the grandparent of the other cat."""
        parents = other_cat.get_parents()
        left_parents = []
        right_parents = []
        if len(parents) == 2:
            left_p = Cat.all_cats.get(parents[0])
            if left_p is not None:
                left_parents = left_p.get_parents()
            right_p = Cat.all_cats.get(parents[1])
            if right_p is not None:
                right_parents = right_p.get_parents()
        if len(parents) == 1:
            left_p = Cat.all_cats.get(parents[0])
            if left_p is not None:
                left_parents = left_p.get_parents()

        if self.ID in left_parents or self.ID in right_parents:
            return True
        return False

    def is_parent(self, other_cat):
        """Check if the cat is the parent of the other cat."""
        if self.ID in other_cat.get_parents():
            return True
        return False

    def is_sibling(self, other_cat):
        """Check if the cats are siblings."""
        if set(self.get_parents()) & set(other_cat.get_parents()):
            return True
        return False

    def is_uncle_aunt(self, other_cat):
        """Check if the cats are related as uncle/aunt and niece/nephew."""
        if self.is_parent(other_cat):
            return False
        if set(self.get_siblings()) & set(other_cat.get_parents()):
            return True
        return False

# ---------------------------------------------------------------------------- #
#                            !IMPORTANT INFORMATION!                           #
#   conditions ar currently not integrated, this are just the base functions   #
#    me (Lixxis) will integrate them after tests are written and completed     #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
#                                  conditions                                  #
# ---------------------------------------------------------------------------- #
  
    def get_ill(self, name):
        if self.is_ill() or name not in ILLNESSES.keys():
            if name not in ILLNESSES.keys():
                print(f"WARNING: {name} is not in the illnesses collection.")
            return
        
        illness = ILLNESSES[name]
        self.illness = Illness(
            name,
            mortality= illness["mortality"],
            infectiousness = illness["infectiousness"], 
            duration = illness["duration"], 
            medicine_duration = illness["medicine_duration"], 
            medicine_mortality = illness["medicine_mortality"], 
            number_medicine_cats = illness["number_medicine_cats"],
            number_medicine_apprentices = illness["number_medicine_apprentices"]
        )

    def get_injured(self,name):
        if self.is_injured() or name not in INJURIES.keys():
            if name not in INJURIES.keys():
                print(f"WARNING: {name} is not in the injuries collection.")
            return

        injury = INJURIES[name]
        self.injury = Injury(
            name,
            duration = injury["duration"],
            medicine_duration = injury["medicine_duration"], 
            mortality = injury["mortality"],
            medicine_mortality = injury["medicine_mortality"],
            risks = injury["risks"],
            illness_infectiousness = injury["illness_infectiousness"],
            number_medicine_cats = injury["number_medicine_cats"],
            number_medicine_apprentices = injury["number_medicine_apprentices"]
        )

    def is_ill(self):
        return self.illness is not None

    def is_injured(self):
        return self.injury is not None

    def contact_with_ill_cat(self, cat):
        "handles if one cat had contact with a ill cat"
        if self.is_ill() or cat is None or not cat.is_ill() or cat.illness.infectiousness == 0:
            return

        illness_name = cat.illness.name
        rate = cat.illness.infectiousness
        if self.is_injured():
            illness_infect = list(filter(lambda ill: ill["name"] == illness_name ,self.injuries.illness_infectiousness))
            if illness_infect is not None and len(illness_infect) > 0:
                illness_infect = illness_infect[0]
                rate -= illness_infect["lower_by"]
        
        # prevent rate lower 0 and print warning message
        if rate < 0:
            print(f"WARNING: injury {self.injuries.name} has lowered chance of {illness_name} infection to {rate}")
            rate = 1

        if randint(1, rate) == 1:
            self.get_ill(illness_name)

# ---------------------------------------------------------------------------- #
#                                    mentor                                    #
# ---------------------------------------------------------------------------- #

    def is_valid_med_mentor(self, potential_mentor):
        # Dead or exiled cats can't be mentors
        if potential_mentor.dead or potential_mentor.exiled:
            return False
        # Match jobs
        if self.status == 'medicine cat apprentice' and potential_mentor.status == 'medicine cat':
            return True
        if self.status == 'medicine cat apprentice' and potential_mentor.status != 'medicine cat':
            return False
        # If not an app, don't need a mentor
        if 'medicine cat apprentice' not in self.status:
            return False
        # Dead cats don't need mentors
        if self.dead:
            return False
        return True

    def is_valid_mentor(self, potential_mentor):
        # Dead or exiled cats can't be mentors
        if potential_mentor.dead or potential_mentor.exiled:
            return False
        # Match jobs
        if self.status == 'medicine cat apprentice' and potential_mentor.status != 'medicine cat':
            return False
        if self.status == 'apprentice' and potential_mentor.status not in [
                'leader', 'deputy', 'warrior'
        ]:
            return False
        # If not an app, don't need a mentor
        if 'apprentice' not in self.status:
            return False
        # Dead cats don't need mentors
        if self.dead:
            return False
        return True

    def update_med_mentor(self, new_mentor=None):
        if new_mentor is None:
            # If not reassigning and current mentor works, leave it
            if self.mentor and self.is_valid_med_mentor(self.mentor):
                return
        old_mentor = self.mentor
        # Should only have mentor if alive and some kind of apprentice
        if 'medicine cat apprentice' in self.status and not self.dead and not self.exiled:
            # Need to pick a random mentor if not specified
            if new_mentor is None:
                potential_mentors = []
                priority_mentors = []
                for cat in self.all_cats.values():
                    if self.is_valid_med_mentor(cat):
                        potential_mentors.append(cat)
                        if len(cat.apprentice) == 0:
                            priority_mentors.append(cat)
                # First try for a cat who currently has no apprentices
                if len(priority_mentors) > 0:
                    new_mentor = choice(priority_mentors)
                elif len(potential_mentors) > 0:
                    new_mentor = choice(potential_mentors)
            # Mentor changing to chosen/specified cat
            self.mentor = new_mentor
            if new_mentor is not None:
                if self not in new_mentor.apprentice:
                    new_mentor.apprentice.append(self)
                if self in new_mentor.former_apprentices:
                    new_mentor.former_apprentices.remove(self)
        else:
            self.mentor = None
        # Move from old mentor's apps to former apps
        if old_mentor is not None and old_mentor != self.mentor:
            if self in old_mentor.apprentice:
                old_mentor.apprentice.remove(self)
            if self not in old_mentor.former_apprentices:
                old_mentor.former_apprentices.append(self)
            if old_mentor not in self.former_mentor:
                self.former_mentor.append(old_mentor)

    def update_mentor(self, new_mentor=None):
        if new_mentor is None:
            # If not reassigning and current mentor works, leave it
            if self.mentor and self.is_valid_mentor(self.mentor):
                return
        old_mentor = self.mentor
        # Should only have mentor if alive and some kind of apprentice
        if 'apprentice' in self.status and not self.dead and not self.exiled:
            # Need to pick a random mentor if not specified
            if new_mentor is None:
                potential_mentors = []
                priority_mentors = []
                for cat in self.all_cats.values():
                    if self.is_valid_mentor(cat):
                        potential_mentors.append(cat)
                        if len(cat.apprentice) == 0:
                            priority_mentors.append(cat)
                # First try for a cat who currently has no apprentices
                if len(priority_mentors) > 0:
                    new_mentor = choice(priority_mentors)
                elif len(potential_mentors) > 0:
                    new_mentor = choice(potential_mentors)
            # Mentor changing to chosen/specified cat
            self.mentor = new_mentor
            if new_mentor is not None:
                if self not in new_mentor.apprentice:
                    new_mentor.apprentice.append(self)
                if self in new_mentor.former_apprentices:
                    new_mentor.former_apprentices.remove(self)
        else:
            self.mentor = None
        # Move from old mentor's apps to former apps
        if self.status == 'warrior' or self.status == 'medicine cat':
            self.former_mentor.append(old_mentor)
            self.mentor = None
            if old_mentor is not None:
                if self in old_mentor.apprentice:
                    old_mentor.apprentice.remove(self)
                if self not in old_mentor.former_apprentices:
                    old_mentor.former_apprentices.append(self)

        if old_mentor is not None and old_mentor != self.mentor:
            if self in old_mentor.apprentice:
                old_mentor.apprentice.remove(self)
            if self not in old_mentor.former_apprentices:
                old_mentor.former_apprentices.append(self)
            if old_mentor not in self.former_mentor:
                self.former_mentor.append(old_mentor)


# ---------------------------------------------------------------------------- #
#                                 relationships                                #
# ---------------------------------------------------------------------------- #

    def is_potential_mate(self, other_cat, for_love_interest = False, former_mentor_setting = game.settings['romantic with former mentor']):
        """Checks if this cat is a free and potential mate for the other cat."""
        # just to be sure, check if it is not the same cat
        if self.ID == other_cat.ID:
            return False

        # check exiles and dead cats
        if self.dead or self.exiled or other_cat.dead or other_cat.exiled:
            return False

        # check for current mate
        # if the cat has a mate, they are not open for a new mate
        if not for_love_interest and self.mate is not None:
            return False

        if self.mate is not None or other_cat.mate is not None:
            return False

        # check for mentor
        is_former_mentor = (other_cat in self.former_apprentices or self in other_cat.former_apprentices)
        if is_former_mentor and not former_mentor_setting:
            return False

        # check for relation
        far_related = self.is_grandparent(other_cat) or other_cat.is_grandparent(self)
        direct_related = self.is_sibling(other_cat) or self.is_parent(other_cat) or other_cat.is_parent(self)
        indirect_related = self.is_uncle_aunt(other_cat) or other_cat.is_uncle_aunt(self)
        if direct_related or indirect_related or far_related:
            return False

        # check for age
        if (self.moons < 14 or other_cat.moons < 14) and not for_love_interest:
            return False

        if self.age == other_cat.age:
            return True

        invalid_age_mate = ['kitten', 'adolescent']
        not_invalid_age = self.age not in invalid_age_mate and other_cat.age not in invalid_age_mate
        if not_invalid_age and abs(self.moons - other_cat.moons) <= 40:
            return True

        return False

    def unset_mate(self, breakup = False, fight = False):
        """Unset the mate."""
        if self.mate is None:
            return

        relation = list(
            filter(lambda r: r.cat_to.ID == self.mate, self.relationships))
        if relation is not None and len(relation) > 0:
            relation = relation[0]
            relation.mates = False
            if breakup:
                relation.romantic_love -= 40
                relation.comfortable -= 20
                relation.trust -= 10
                if fight:
                    relation.platonic_like -= 30
        else:
            mate = self.all_cats.get(self.mate)
            self.relationships.append(Relationship(self, mate))

        self.mate = None

    def set_mate(self, other_cat):
        """Assigns other_cat as mate to self."""
        self.mate = other_cat.ID
        other_cat.mate = self.ID

        cat_relationship = list(
            filter(lambda r: r.cat_to.ID == other_cat.ID, self.relationships))
        if cat_relationship is not None and len(cat_relationship) > 0:
            cat_relationship[0].romantic_love += 20
            cat_relationship[0].comfortable += 20
            cat_relationship[0].trust += 10
        else:
            self.relationships.append(
                Relationship(self, other_cat, True))

    def create_new_relationships(self):
        """Create Relationships to all current clan cats."""
        relationships = []
        for id in self.all_cats.keys():
            the_cat = self.all_cats.get(id)
            if the_cat.ID is not self.ID:
                mates = the_cat is self.mate
                are_parents = False
                parents = False
                siblings = False

                if self.parent1 is not None and self.parent2 is not None and \
                    the_cat.parent1 is not None and the_cat.parent2 is not None:
                    are_parents = the_cat.ID in [self.parent1, self.parent2]
                    parents = are_parents or self.ID in [
                        the_cat.parent1, the_cat.parent2
                    ]
                    siblings = self.parent1 in [
                        the_cat.parent1, the_cat.parent2
                    ] or self.parent2 in [the_cat.parent1, the_cat.parent2]

                related = parents or siblings

                # set the different stats
                romantic_love = 0
                like = 0
                dislike = 0
                admiration = 0
                comfortable = 0
                jealousy = 0
                trust = 0
                if game.settings['random relation']:
                    if randint(1, 20) == 1 and romantic_love < 1:
                        dislike = randint(10, 25)
                        jealousy = randint(5, 15)
                        if randint(1, 30) == 1:
                            trust = randint(1, 10)
                    else:
                        like = randint(0, 35)
                        comfortable = randint(0, 25)
                        trust = randint(0, 15)
                        admiration = randint(0, 20)
                        if randint(
                                1, 100 - like
                        ) == 1 and self.moons > 11 and the_cat.moons > 11:
                            romantic_love = randint(15, 30)
                            comfortable = int(comfortable * 1.3)
                            trust = int(trust * 1.2)

                if are_parents and like < 60:
                    like = 60
                if siblings and like < 30:
                    like = 30

                rel = Relationship(cat_from=self,
                                   cat_to=the_cat,
                                   mates=mates,
                                   family=related,
                                   romantic_love=romantic_love,
                                   platonic_like=like,
                                   dislike=dislike,
                                   admiration=admiration,
                                   comfortable=comfortable,
                                   jealousy=jealousy,
                                   trust=trust)
                relationships.append(rel)
        self.relationships = relationships

    def save_relationship_of_cat(self):
        # save relationships for each cat
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]
        elif game.clan is not None:
            clanname = game.clan.name
        relationship_dir = 'saves/' + clanname + '/relationships'
        if not os.path.exists(relationship_dir):
            os.makedirs(relationship_dir)

        rel = []
        for r in self.relationships:
            r_data = {
                "cat_from_id": r.cat_from.ID,
                "cat_to_id": r.cat_to.ID,
                "mates": r.mates,
                "family": r.family,
                "romantic_love": r.romantic_love,
                "platonic_like": r.platonic_like,
                "dislike": r.dislike,
                "admiration": r.admiration,
                "comfortable": r.comfortable,
                "jealousy": r.jealousy,
                "trust": r.trust,
                "log": r.log
            }
            rel.append(r_data)

        try:
            with open(relationship_dir + '/' + self.ID + '_relations.json',
                      'w') as rel_file:
                json_string = ujson.dumps(rel, indent = 4)
                rel_file.write(json_string)
        except:
            print(f"Saving relationship of cat #{self} didn't work.")

    def load_relationship_of_cat(self):
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        else:
            clanname = game.switches['clan_list'][0]

        relation_directory = 'saves/' + clanname + '/relationships/'
        relation_cat_directory = relation_directory + self.ID + '_relations.json'

        self.relationships = []
        if os.path.exists(relation_directory):
            if not os.path.exists(relation_cat_directory):
                self.create_new_relationships()
                for cat in Cat.all_cats.values():
                    cat.relationships.append(Relationship(cat,self))
                update_sprite(self)
                return
            try:
                with open(relation_cat_directory, 'r') as read_file:
                    rel_data = ujson.loads(read_file.read())
                    relationships = []
                    for rel in rel_data:
                        cat_to = self.all_cats.get(rel['cat_to_id'])
                        if cat_to is None:
                            continue
                        new_rel = Relationship(
                            cat_from=self,
                            cat_to=cat_to,
                            mates=rel['mates'] if rel['mates'] else False,
                            family=rel['family'] if rel['family'] else False,
                            romantic_love=rel['romantic_love'] if rel['romantic_love'] else 0,
                            platonic_like=rel['platonic_like'] if rel['platonic_like'] else 0,
                            dislike=rel['dislike'] if rel['dislike'] else 0,
                            admiration=rel['admiration'] if rel['admiration'] else 0,
                            comfortable=rel['comfortable'] if rel['comfortable'] else 0,
                            jealousy=rel['jealousy'] if rel['jealousy'] else 0,
                            trust=rel['trust'] if rel['trust'] else 0,
                            log =rel['log'] if rel['log'] else [])
                        relationships.append(new_rel)
                    self.relationships = relationships
            except:
                print(f'There was an error reading the relationship file of cat #{self}.')


# ---------------------------------------------------------------------------- #
#                                  properties                                  #
# ---------------------------------------------------------------------------- #

    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, exp):
        if (exp > 80):
            exp = 80
        self._experience = exp
        experience_levels = [
            'very low', 'low', 'slightly low', 'average', 'somewhat high',
            'high', 'very high', 'master', 'max'
        ]
        self.experience_level = experience_levels[math.floor(self.experience /
                                                             10)]

    @property
    def moons(self):
        return self._moons

    @moons.setter
    def moons(self, value):
        self._moons = value

        updated_age = False
        for key_age in self.age_moons.keys():
            if self._moons in range(self.age_moons[key_age][0], self.age_moons[key_age][1]+1):
                updated_age = True
                self.age = key_age
        if not updated_age and self.age is not None:
            self.age = "elder"

# ---------------------------------------------------------------------------- #
#                               END OF CAT CLASS                               #
# ---------------------------------------------------------------------------- #

# Twelve example cats
def create_example_cats():
    e = random.sample(range(12), 3)
    for a in range(12):
        if a in e:
            game.choose_cats[a] = Cat(status='warrior')
        else:
            game.choose_cats[a] = Cat(status=choice(
                ['kitten', 'apprentice', 'warrior', 'warrior', 'elder']))
        update_sprite(game.choose_cats[a])


# CAT CLASS ITEMS
cat_class = Cat(example=True)
game.cat_class = cat_class

# ---------------------------------------------------------------------------- #
#                                load json files                               #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

ILLNESSES = None
with open(f"{resource_directory}Illnesses.json", 'r') as read_file:
    ILLNESSES = ujson.loads(read_file.read())

INJURIES = None
with open(f"{resource_directory}Injuries.json", 'r') as read_file:
    INJURIES = ujson.loads(read_file.read())
