from .pelts import *
from .names import *
from .sprites import *
from .game_essentials import *
from .relationship import *
from .thoughts import *
from .utility import *
from random import choice, randint
import math
import os.path
import ujson


class Cat(object):
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
        'elder': [120, 199]
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

    all_cats = {}  # ID: object
    other_cats = {}  # cats outside the clan

    def __init__(self,
                 prefix=None,
                 gender=None,
                 status="kitten",
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

        # setting ID
        if ID is None:
            potential_ID = str(randint(10000, 9999999))
            while potential_ID in self.all_cats:
                potential_ID = str(randint(10000, 9999999))
            self.ID = potential_ID
        else:
            self.ID = ID

        # age
        if status is None and moons is None:
            self.age = choice(self.ages)
        elif moons != None:
            for key_age in self.age_moons.keys():
                if moons in range(self.age_moons[key_age][0], self.age_moons[key_age][1]+1):
                    self.age = key_age
        else:
            if status in ['kitten', 'elder']:
                self.age = status
            elif status == 'apprentice':
                self.age = 'adolescent'
            elif status == 'medicine cat apprentice':
                self.age = 'adolescent'
            else:
                self.age = choice(
                    ['young adult', 'adult', 'adult', 'senior adult'])
        if moons is None:
            self.moons = randint(self.age_moons[self.age][0],
                                 self.age_moons[self.age][1])
        else:
            self.moons = moons

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

        # sex
        if self.gender is None:
            self.gender = choice(["female", "male"])
        self.g_tag = self.gender_tags[self.gender]

        #trans cat chances
        trans_chance = randint(0, 50)
        nb_chance = randint(0, 75)
        if self.age == 'kitten':
            self.gender_align = self.gender
        if self.gender == "female":
            if trans_chance == 1:
                self.genderalign = "trans male"
            elif nb_chance == 1:
                self.genderalign = "nonbinary"
            else:
                self.genderalign = self.gender
        if self.gender == "male":
            if trans_chance == 1:
                self.genderalign = "trans female"
            elif nb_chance == 1:
                self.genderalign = "nonbinary"
            else:
                self.genderalign = self.gender

        # eye colour
        if self.eye_colour is None:
            a = randint(0, 200)
            if a == 1:
                self.eye_colour = choice(["BLUEYELLOW", "BLUEGREEN"])
            else:
                if self.parent1 is None:
                    self.eye_colour = choice(eye_colours)
                elif self.parent2 is None:
                    par1 = self.all_cats[self.parent1]
                    self.eye_colour = choice(
                        [par1.eye_colour, choice(eye_colours)])
                else:
                    par1 = self.all_cats[self.parent1]
                    par2 = self.all_cats[self.parent2]
                    self.eye_colour = choice([
                        par1.eye_colour, par2.eye_colour,
                        choice(eye_colours)
                    ])

        # pelt
        if self.pelt is None:
            if self.parent2 is None and self.parent1 in self.all_cats.keys():
                # 1 in 3 chance to inherit a single parent's pelt
                par1 = self.all_cats[self.parent1]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, None]), choice([par1.pelt.white, None]), choice([par1.pelt.name, None]),
                                        choice([par1.pelt.length, None]))
            if self.parent1 in self.all_cats.keys() and self.parent2 in self.all_cats.keys():
                # 2 in 3 chance to inherit either parent's pelt
                par1 = self.all_cats[self.parent1]
                par2 = self.all_cats[self.parent2]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, par2.pelt.colour, None]), choice([par1.pelt.white, par2.pelt.white, None]),
                                        choice([par1.pelt.name, par2.pelt.name, None]), choice([par1.pelt.length, par2.pelt.length, None]))                  
            else:
                self.pelt = choose_pelt(self.gender)

        # NAME
        if self.pelt is not None:
            self.name = Name(status, prefix, suffix, self.pelt.colour,
                             self.eye_colour, self.pelt.name)
        else:
            self.name = Name(status, prefix, suffix, eyes=self.eye_colour)

        # SPRITE
        self.age_sprites = {
            'kitten': randint(0, 2),
            'adolescent': randint(3, 5),
            'elder': randint(3, 5)
        }
        self.reverse = choice([True, False])
        self.skin = choice(skin_sprites)

        # scars & more
        scar_choice = randint(0, 15)
        if self.age in ['kitten', 'adolescent']:
            scar_choice = randint(0, 50)
        elif self.age in ['young adult', 'adult']:
            scar_choice = randint(0, 20)
        if scar_choice == 1:
            self.specialty = choice([
                choice(scars1),
                choice(scars2),
                choice(scars4),
                choice(scars5)
            ])
        else:
            self.specialty = None

        scar_choice2 = randint(0, 30)
        if self.age in ['kitten', 'adolescent']:
            scar_choice2 = randint(0, 100)
        elif self.age in ['young adult', 'adult']:
            scar_choice2 = randint(0, 40)
        if scar_choice2 == 1:
            self.specialty2 = choice([
                choice(scars1),
                choice(scars2),
                choice(scars4),
                choice(scars5)
            ])
        else:
            self.specialty2 = None

        # Accessories
        accessory_choice = randint(0, 35)
        if self.age in ['kitten', 'adolescent']:
            accessory_choice = randint(0, 15)
        elif self.age in ['young adult', 'adult']:    
            accessory_choice = randint(0, 50)
        if accessory_choice == 1:
            self.accessory = choice([
                choice(plant_accessories),
                choice(wild_accessories)
            ])
        else:
            self.accessory = None
        
        # random event
        if self.pelt is not None:
            if self.pelt.length != 'long':
                self.age_sprites['adult'] = randint(6, 8)
            else:
                self.age_sprites['adult'] = randint(0, 2)
            self.age_sprites['young adult'] = self.age_sprites['adult']
            self.age_sprites['senior adult'] = self.age_sprites['adult']
            self.age_sprites[
                'dead'] = None  # The sprite that the cat has in starclan

                # WHITE PATCHES
        non_white_pelt = False
        if self.pelt.colour != 'WHITE' and self.pelt.name in\
        ['Tortie', 'TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette']:
            non_white_pelt = True
        little_white_poss = little_white * 6
        mid_white_poss = mid_white * 4
        high_white_poss = high_white * 2
        mostly_white_poss = mostly_white
        if self.pelt is not None:
            if self.pelt.white is True:
                pelt_choice = randint(0, 10)
                vit_chance = randint(0, 40)
                direct_inherit = randint(0, 10)
                # inheritance
                # one parent
                if self.parent1 is not None and self.parent2 is None:
                    par1 = self.all_cats[self.parent1]
                    if direct_inherit == 1:
                        if par1.pelt.white is False:
                            self.pelt.white = False
                        else:
                            self.white_patches = par1.white_patches
                    elif vit_chance == 1:
                        self.white_patches = choice(vit)
                    else:
                        if par1.white_patches in point_markings and non_white_pelt is True:
                            self.white_patches = choice(point_markings)
                        elif par1.white_patches in vit:
                            self.white_patches = choice(vit)
                        elif par1.white_patches in [None] + little_white + mid_white + high_white:
                            self.white_patches = choice([None] + little_white_poss + mid_white_poss + high_white_poss + mostly_white_poss)
                        elif par1.white_patches in mostly_white:
                            self.white_patches = choice(mid_white + high_white + mostly_white + ['FULLWHITE'])
                    if par1.white_patches == None and self.pelt.name == 'Calico':
                        self.pelt.name = 'Tortie'
                    # two parents
                elif self.parent1 is not None and self.parent2 is not None:
                    # if 1, cat directly inherits parent 1's white patches. if 2, it directly inherits parent 2's
                    par1 = self.all_cats[self.parent1]
                    par2 = self.all_cats[self.parent2]
                    if direct_inherit == 1:
                        if par1.pelt.white is False:
                            self.pelt.white = False
                        else:
                            self.white_patches = par1.white_patches
                    elif direct_inherit == 2:
                        if par2.pelt.white is False:
                            self.pelt.white = False
                        else:
                            self.white_patches = par2.white_patches
                    elif vit_chance == 1:
                        self.white_patches = choice(vit)
                    else:
                        if par1.white_patches in point_markings and non_white_pelt is True\
                        or par2.white_patches in point_markings and non_white_pelt is True:
                            self.white_patches = choice(point_markings)
                        elif par1.white_patches in vit and non_white_pelt is True\
                        or par2.white_patches in vit and non_white_pelt is True:
                            self.white_patches = choice(vit)
                        elif par1.white_patches is None:
                            if par2.white_patches is None:
                                self.white_patches = None
                            elif par2.white_patches in little_white:
                                self.white_patches = choice(little_white_poss + [None])
                            elif par2.white_patches in mid_white:
                                self.white_patches = choice(little_white_poss + mid_white_poss)
                            elif par2.white_patches in high_white:
                                self.white_patches = choice(little_white + mid_white_poss * 2 + high_white)
                            elif par2.white_patches in mostly_white:
                                self.white_patches = choice(mid_white_poss + high_white_poss + mostly_white)
                            elif par2.white_patches == 'FULLWHITE':
                                self.white_patches = choice(little_white_poss + mid_white_poss + high_white_poss + mostly_white_poss + ['FULLWHITE'])
                            else:
                                self.white_patches = choice(little_white)
                        elif par1.white_patches in little_white:
                            if par2.white_patches is None:
                                self.white_patches = choice(little_white + [None])
                            elif par2.white_patches in little_white:
                                self.white_patches = choice(little_white_poss * 2 + mid_white_poss + [None])
                            elif par2.white_patches in mid_white:
                                self.white_patches = choice(little_white_poss + mid_white_poss + high_white)
                            elif par2.white_patches in high_white:
                                self.white_patches = choice(little_white + mid_white_poss * 2 + high_white_poss + mostly_white)
                            elif par2.white_patches in mostly_white:
                                self.white_patches = choice(mid_white + high_white_poss + mostly_white + ['FULLWHITE'])
                            elif par2.white_patches == 'FULLWHITE':
                                self.white_patches = choice(high_white_poss + mostly_white_poss + ['FULLWHITE'])
                            else:
                                self.white_patches = choice(little_white)
                        elif par1.white_patches in mid_white:
                            if par2.white_patches is None:
                                self.white_patches = choice(little_white + mid_white + [None])
                            elif par2.white_patches in little_white:
                                self.white_patches = choice(little_white_poss + mid_white_poss + high_white)
                            elif par2.white_patches in mid_white:
                                self.white_patches = choice(little_white + mid_white_poss * 3 + high_white)
                            elif par2.white_patches in high_white:
                                self.white_patches = choice(mid_white_poss + high_white_poss * 3 + mostly_white)
                            elif par2.white_patches in mostly_white:
                                self.white_patches = choice(mid_white + high_white_poss * 2 + mostly_white + ['FULLWHITE'])
                            elif par2.white_patches == 'FULLWHITE':
                                self.white_patches = choice(high_white_poss + mostly_white_poss + ['FULLWHITE'])
                            else:
                                self.white_patches = choice(mid_white)
                        elif par1.white_patches in high_white:
                            if par2.white_patches is None:
                                self.white_patches = choice(little_white + mid_white_poss + high_white + [None])
                            elif par2.white_patches in little_white:
                                self.white_patches = choice(little_white_poss + mid_white_poss + high_white)
                            elif par2.white_patches in mid_white:
                                self.white_patches = choice(little_white + mid_white_poss + high_white_poss)
                            elif par2.white_patches in high_white:
                                self.white_patches = choice(mid_white_poss + high_white_poss * 2 + mostly_white)
                            elif par2.white_patches in mostly_white:
                                self.white_patches = choice(mid_white + high_white_poss + mostly_white + ['FULLWHITE'])
                            elif par2.white_patches == 'FULLWHITE':
                                self.white_patches = choice(high_white_poss + mostly_white_poss + ['FULLWHITE'])
                            else:
                                self.white_patches = choice(high_white)
                        elif par1.white_patches in mostly_white:
                            if par2.white_patches is None:
                                self.white_patches = choice(little_white + mid_white + high_white + mostly_white)
                            elif par2.white_patches in little_white:
                                self.white_patches = choice(little_white + mid_white_poss + high_white_poss + mostly_white)
                            elif par2.white_patches in mid_white:
                                self.white_patches = choice(mid_white_poss + high_white_poss + mostly_white + ['FULLWHITE'])
                            elif par2.white_patches in high_white:
                                self.white_patches = choice(high_white_poss + mostly_white + mostly_white + mostly_white + ['FULLWHITE'])
                            elif par2.white_patches in mostly_white:
                                self.white_patches = choice(high_white + mostly_white * 4 + ['FULLWHITE'])
                            elif par2.white_patches == 'FULLWHITE':
                                self.white_patches = choice(mostly_white * 5 + ['FULLWHITE', 'FULLWHITE', 'FULLWHITE'])
                            else:
                                self.white_patches = choice(mostly_white)
                        elif par1.white_patches == 'FULLWHITE':
                            if par2.white_patches is None:
                                self.white_patches = choice(little_white + mid_white + high_white + mostly_white + [None] + ['FULLWHITE'])
                            elif par2.white_patches in little_white:
                                self.white_patches = choice(mid_white_poss + high_white_poss * 2 + mostly_white * 2)
                            elif par2.white_patches in mid_white:
                                self.white_patches = choice(mid_white + high_white_poss * 3 + mostly_white * 3 + ['FULLWHITE'])
                            elif par2.white_patches in high_white:
                                self.white_patches = choice(high_white_poss + mostly_white * 4 + ['FULLWHITE'] * 3)
                            elif par2.white_patches in mostly_white:
                                self.white_patches = choice(high_white + mostly_white * 4 + ['FULLWHITE'] * 4)
                            elif par2.white_patches == 'FULLWHITE':
                                self.white_patches = choice(mostly_white + ['FULLWHITE'] * 6)
                            else:
                                self.white_patches = choice(mostly_white)
                    if self.pelt.name == 'Calico' and par1.white_patches not in mid_white + high_white + mostly_white\
                    and par2.white_patches not in mid_white + high_white + mostly_white:
                        self.pelt.name = 'Tortie'
                        
                # regular non-inheritance white patches generation
                else:
                    if pelt_choice == 1 and non_white_pelt is True:
                        self.white_patches = choice(point_markings)
                    elif pelt_choice == 1 and self.pelt.name == 'TwoColour' and self.pelt.colour != 'WHITE':
                        self.white_patches = choice(point_markings + ['POINTMARK'])
                    elif pelt_choice == 2 and self.pelt.name in ['Calico', 'TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette']:
                        self.white_patches = choice(mostly_white_poss)
                    elif pelt_choice == 3 and self.pelt.name in ['TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette']\
                    and self.pelt.colour != 'WHITE':
                        self.white_patches = choice(['EXTRA', None, 'FULLWHITE'])
                    else:
                        if self.pelt.name in ['TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette']:
                            self.white_patches = choice(little_white_poss + mid_white_poss + high_white_poss)
                        elif self.pelt.name in ['Tortie']:
                            self.white_patches = choice(little_white_poss + mid_white_poss)
                        elif self.pelt.name in ['Calico']:
                            self.white_patches = choice(high_white_poss)
                        elif pelt_choice == 1 and vit_chance == 1 and self.pelt.name in ['Tortie', 'TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette']\
                        and self.pelt.colour != 'WHITE':
                            self.white_patches = choice(vit)
                        else:
                            self.white_patches = choice(self.white_patches)
            else:
                self.white_patches = None
            
        # pattern for tortie/calico cats
        if self.pelt.name in ['Calico', 'Tortie']:
            self.tortiecolour = self.pelt.colour
            self.tortiebase = choice(['single', 'tabby', 'bengal', 'marbled', 'ticked', 'smoke', 'rosette', 'speckled'])
            if self.tortiebase == 'tabby':
                self.tortiepattern = 'tortietabby'
            elif self.tortiebase == 'bengal':
                self.tortiepattern = 'tortiebengal'
            elif self.tortiebase == 'marbled':
                self.tortiepattern = 'tortiemarbled'
            elif self.tortiebase == 'ticked':
                self.tortiepattern = 'tortieticked'
            elif self.tortiebase == 'rosette':
                self.tortiepattern = 'tortierosette'
            elif self.tortiebase == 'smoke':
                self.tortiepattern = 'tortiesmoke'
            elif self.tortiebase == 'speckled':
                self.tortiepattern = 'tortiespeckled'
            else:
                self.tortiepattern = 'tortietabby'
        else:
            self.tortiebase = None
            self.tortiepattern = None
            self.tortiecolour = None

        if self.pelt.name in ['Calico', 'Tortie'] and self.pelt.colour != None:
            if self.pelt.colour in ["BLACK", "DARKBROWN"]:
                self.pattern = choice(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR', 'GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR',
                                        'DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR'])
            elif self.pelt.colour in ["DARKGREY", "BROWN"]:
                self.pattern = choice(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR', 'GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR'])
            elif self.pelt.colour in ["SILVER", "GREY", "LIGHTBROWN"]:
                self.pattern = choice(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR'])
        else:
            self.pattern = None
            

        self.paralyzed = False
        self.no_kits = False
        self.exiled = False
        if self.genderalign == None:                             #gender stuff?? not sure why this is right here
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

        experience_levels = [
            'very low', 'low', 'slightly low', 'average', 'somewhat high',
            'high', 'very high', 'master', 'max'
        ]
        self.experience_level = experience_levels[math.floor(self.experience /
                                                             10)]

        self.paralyzed = False
        self.no_kits = False
        self.exiled = False
        if self.genderalign == None:
            self.genderalign = self.gender        


        # SAVE CAT INTO ALL_CATS DICTIONARY IN CATS-CLASS
        self.all_cats[self.ID] = self

    def is_alive(self):
        return not self.dead

    def __repr__(self):
        return self.ID

    def thoughts(self):
        old_thoughts(self.all_cats)

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

    def status_change(self, new_status):  # revealing of traits and skills
        # updates traits
        if self.moons == 6:
            chance = randint(0, 5)  # chance for cat to gain trait that matches their previous trait's personality group
            if chance == 0:
                self.trait = choice(self.traits)
                print('TRAIT TYPE: Random - CHANCE', chance)
            else:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        self.trait = choice(possible_trait)
                        print('TRAIT TYPE:', x, 'CHANCE:', chance)
        if self.moons == 12:
            chance = randint(0, 5)  # chance for cat to gain new trait or keep old
            if chance == 0:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        self.trait = choice(possible_trait)
                        print('TRAIT TYPE:', x, 'CHANCE:', chance)
            else:
                print('TRAIT TYPE: No change', chance)
        if self.moons == 120:
            chance = randint(0, 5)  # chance for cat to gain new trait or keep old
            if chance == 0:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        self.trait = choice(possible_trait)
                        print('TRAIT TYPE:', x, 'CHANCE:', chance)
            elif chance == 1:
                self.trait = choice(self.traits)
                print('TRAIT TYPE: Random - CHANCE', chance)
            else:
                print('TRAIT TYPE: No change', chance)
        # updates mentors
        if new_status == 'apprentice':
            self.update_mentor()
        elif new_status == 'medicine cat apprentice':
            self.update_med_mentor()
        # updates skill
        if self.skill == '???':
            if new_status == 'warrior' or self.status == 'warrior' and new_status != 'medicine cat':
                self.skill = choice(self.skills)
                self.update_mentor()
            elif new_status == 'medicine cat':
                self.skill = choice(self.med_skills)
                self.update_med_mentor()
        else:
            self.skill = self.skill

        if self.moons >= 120 and self.status != 'leader' and self.status != 'medicine cat':
            self.skill = choice(self.elder_skills)

        self.status = new_status
        self.name.status = new_status
        # update class dictionary
        self.all_cats[self.ID] = self

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
        if old_mentor is not None and old_mentor != self.mentor:
            if self in old_mentor.apprentice:
                old_mentor.apprentice.remove(self)
            if self not in old_mentor.former_apprentices:
                old_mentor.former_apprentices.append(self)
            if old_mentor not in self.former_mentor:
                self.former_mentor.append(old_mentor)

    def save_relationship_of_cat(self):
        # save relationships for each cat
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]
        elif game.clan != None:
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
                for cat in cat_class.all_cats.values():
                    cat.relationships.append(Relationship(cat,self))
                update_sprite(self)
                return
            try:
                with open(relation_cat_directory, 'r') as read_file:
                    rel_data = ujson.loads(read_file.read())
                    relationships = []
                    for rel in rel_data:
                        cat_to = self.all_cats.get(rel['cat_to_id'])
                        if cat_to == None:
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

    def describe_color(self):
        color_name = ''
        color_name = str(self.pelt.colour).lower()
        if self.tortiecolour != None:
            color_name = str(self.tortiecolour).lower()
        if color_name == 'palegrey':
            color_name = 'pale grey'
        elif color_name == 'darkgrey':
            color_name = 'dark grey'
        elif color_name == 'paleginger':
            color_name = 'pale ginger'
        elif color_name == 'darkginger':
            color_name = 'dark ginger'
        elif color_name == 'lightbrown':
            color_name = 'light brown'
        elif color_name == 'darkbrown':
            color_name = 'dark brown'
        if self.pelt.name == "Tabby":
            color_name = color_name + ' tabby'
        elif self.pelt.name == "Speckled":
            color_name = color_name + ' speckled'
        elif self.pelt.name == "Bengal":
            color_name = color_name + ' bengal'
        elif self.pelt.name == "Marbled":
            color_name = color_name + ' marbled tabby'
        elif self.pelt.name == "Rosette":
            color_name = color_name + ' rosetted'
        elif self.pelt.name == "Ticked":
            color_name = color_name + ' ticked tabby'
        elif self.pelt.name == "Smoke":
            color_name = color_name + ' smoke'

        elif self.pelt.name == "Tortie":
            if self.tortiepattern not in ["tortiesolid", "tortiesmoke"]:
                color_name = color_name + ' torbie'
            else:
                color_name = color_name + ' tortie'
        elif self.pelt.name == "Calico":
            if self.tortiepattern not in ["tortiesolid", "tortiesmoke"]:
                color_name = color_name + ' tabico'
            else:
                color_name = color_name + ' calico'
        # enough to comment but not make calico
        if self.white_patches is not None:
            if self.white_patches in little_white + mid_white:
                color_name = color_name + ' and white'
            # and white
            elif self.white_patches in high_white:
                if self.pelt.name != "Calico":
                    color_name = color_name + ' and white'
            # white and
            elif self.white_patches in mostly_white:
                color_name = 'white and ' + color_name
            # colorpoint
            elif self.white_patches in point_markings:
                color_name = color_name + ' point'
                if color_name == 'dark ginger point' or color_name == 'ginger point':
                    color_name = 'flame point'
            # vitiligo
            elif self.white_patches in vit:
                color_name = color_name + ' with vitiligo'
        else:
            color_name = color_name

        if color_name == 'tortie':
            color_name = 'tortoiseshell'

        if self.white_patches == 'FULLWHITE':
            color_name = 'white'

        if color_name == 'white and white':
            color_name = 'white'

        return color_name

    def accessory_display_name(self):
        accessory = str(self.accessory).lower()
        acc_display = accessory
        if self.accessory != None:
            if self.accessory in collars:
                collar_color = None
                if accessory.startswith('crimson'):
                    collar_color = 'crimson'
                elif accessory.startswith('blue'):
                    collar_color = 'blue'
                elif accessory.startswith('yellow'):
                    collar_color = 'yellow'
                elif accessory.startswith('cyan'):
                    collar_color = 'cyan'
                elif accessory.startswith('red'):
                    collar_color = 'red'
                elif accessory.startswith('lime'):
                    collar_color = 'lime'
                elif accessory.startswith('green'):
                    collar_color = 'green'
                elif accessory.startswith('rainbow'):
                    collar_color = 'rainbow'
                elif accessory.startswith('black'):
                    collar_color = 'black'
                elif accessory.startswith('spikes'):
                    collar_color = 'spiky'
                elif accessory.startswith('pink'):
                    collar_color = 'pink'
                elif accessory.startswith('purple'):
                    collar_color = 'purple'
                elif accessory.startswith('multi'):
                    collar_color = 'multi'
                if accessory.endswith('bow') and not accessory == 'rainbow':
                    acc_display = collar_color + ' bow'
                elif accessory.endswith('bell'):
                    acc_display = collar_color + ' bell collar'
                else:
                    acc_display = collar_color + ' collar'
                
            elif self.accessory in wild_accessories:
                if acc_display == 'blue feathers':
                    acc_display = 'crow feathers'
                elif acc_display == 'red feathers':
                    acc_display = 'cardinal feathers'
                else:
                    acc_display = acc_display
            
            else:
                acc_display = acc_display

            if self.accessory == None:
                acc_display = None
        return acc_display

    def plural_acc_names(self, plural, singular):
        accessory = self.accessory.lower()
        acc_display = accessory
        if accessory == 'maple leaf':
            if plural == True:
                acc_display = 'maple leaves'
            if singular == True:
                acc_display = 'maple leaf'
        elif accessory == 'holly':
            if plural == True:
                acc_display = 'holly berries'
            if singular == True:
                acc_display = 'holly berry'
        elif accessory == 'blue berries':
            if plural == True:        
                acc_display = 'blueberries'
            if singular == True:
                acc_display = 'blueberry'
        elif accessory == 'forget me nots':
            if plural == True:
                acc_display = 'forget me nots'
            if singular == True:
                acc_display = 'forget me not flower'                
        elif accessory == 'rye stalk':
            if plural == True:
                acc_display = 'rye stalks'
            if singular == True:
                acc_display = 'rye stalk'
        elif accessory == 'laurel':
            if plural == True:
                acc_display = 'laurel'
            if singular == True:
                acc_display = 'laurel plant'
        elif accessory == 'bluebells':
            if plural == True:
                acc_display = 'bluebells'
            if singular == True:
                acc_display = 'bluebell flower'                
        elif accessory == 'nettle':
            if plural == True:
                acc_display = 'nettles'
            if singular == True:
                acc_display = 'nettle'
        elif accessory == 'poppy':
            if plural == True:
                acc_display = 'poppies'
            if singular == True:
                acc_display = 'poppy flower'
        elif accessory == 'lavender':
            if plural == True:
                acc_display = 'lavender'
            if singular == True:
                acc_display = 'lavender flower'
        elif accessory == 'herbs':
            if plural == True:
                acc_display = 'herbs'
            if singular == True:
                acc_display = 'herb'
        elif accessory == 'petals':
            if plural == True:
                acc_display = 'petals'
            if singular == True:
                acc_display = 'petal'
        elif accessory == 'dry herbs':
            if plural == True:
                acc_display = 'dry herbs'
            if singular == True:
                acc_display = 'dry herb'
        elif accessory == 'oak leaves':
            if plural == True:
                acc_display = 'oak leaves'
            if singular == True:
                acc_display = 'oak leaf'
        elif accessory == 'catmint':
            if plural == True:
                acc_display = 'catnip'
            if singular == True:
                acc_display = 'catnip leaf'
        elif accessory == 'maple seed':
            if plural == True:
                acc_display = 'maple seeds'
            if singular == True:
                acc_display = 'maple seed'
        elif accessory == 'juniper':
            if plural == True:
                acc_display = 'juniper berries'
            if singular == True:
                acc_display = 'juniper berry'
        elif accessory == 'red feathers':
            if plural == True:
                acc_display = 'cardinal feathers'
            if singular == True:
                acc_display = 'cardinal feather'
        elif accessory == 'blue feathers':
            if plural == True:
                acc_display = 'crow feathers'
            if singular == True:
                acc_display = 'crow feather'
        elif accessory == 'jay feathers':
            if plural == True:
                acc_display = 'jay feathers'
            if singular == True:
                acc_display = 'jay feather'
        elif accessory == 'moth wings':
            if plural == True:
                acc_display = 'moth wings'
            if singular == True:
                acc_display = 'moth wing'
        elif accessory == 'cicada wings':
            if plural == True:
                acc_display = 'cicada wings'
            if singular == True:
                acc_display = 'cicada wing'
            
        if plural is True and singular is False:
            return acc_display
        elif singular is True and plural is False:
            return acc_display

    def describe_cat(self):
        if self.genderalign == 'male' or self.genderalign == "transmasc" or self.genderalign == "trans male":
            sex = 'tom'
        elif self.genderalign == 'female' or self.genderalign == "transfem" or self.genderalign == "trans female":
            sex = 'she-cat'
        else:
            sex = 'cat'
        description = str(self.pelt.length).lower() + '-furred'
        description += ' ' + self.describe_color() + ' ' + sex
        return description

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
            cat_relationship[0].cut_boundaries()
        else:
            self.relationships.append(
                Relationship(self, other_cat, True))

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
                relation.cut_boundaries()
        else:
            mate = self.all_cats.get(self.mate)
            self.relationships.append(Relationship(self, mate))

        self.mate = None

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

    def is_grandparent(self, other_cat):
        """Check if the cat is the grandparent of the other cat."""
        parents = other_cat.get_parents()
        left_parents = []
        right_parents = []
        if len(parents) == 2:
            left_p = cat_class.all_cats.get(parents[0])
            if left_p != None:
                left_parents = left_p.get_parents()
            right_p = cat_class.all_cats.get(parents[1])
            if right_p != None:
                right_parents = right_p.get_parents()
        if len(parents) == 1:
            left_p = cat_class.all_cats.get(parents[0])
            if left_p != None:
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
