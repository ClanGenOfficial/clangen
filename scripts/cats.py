from multiprocessing import reduction
from .pelts import *
from .names import *
from .sprites import *
from .game_essentials import *
from .relationship import *
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
        self.birth_cooldown = 0
        if ID is None:
            potential_ID = str(randint(10000, 9999999))
            while potential_ID in self.all_cats:
                potential_ID = str(randint(10000, 9999999))
            self.ID = potential_ID
        else:
            self.ID = ID
        # personality trait and skill
        if self.status != 'kitten':
            self.trait = choice(self.traits)
            if self.status == 'medicine cat':
                self.skill = choice(self.med_skills)
            elif self.status != 'apprentice' and self.status != 'medicine cat apprentice':
                self.skill = choice(self.skills)
            else:
                self.skill = '???'
        else:
            self.trait = self.trait = choice(self.kit_traits)
            self.skill = '???'
        if self.gender is None:
            self.gender = choice(["female", "male"])
        self.g_tag = self.gender_tags[self.gender]
        if status is None:
            self.age = choice(self.ages)
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
        little_white_poss = little_white * 6
        mid_white_poss = mid_white * 4
        high_white_poss = high_white * 2
        mostly_white_poss = mostly_white
        if self.pelt is not None:
            if self.pelt.white and self.pelt.white_patches is not None:
                pelt_choice = randint(0, 10)
                vit_chance = randint(0, 40)
                if pelt_choice == 1 and self.pelt.name in ['Tortie', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette']\
                and self.pelt.colour != 'WHITE':
                    self.white_patches = choice(point_markings)
                elif pelt_choice == 1 and self.pelt.name in 'TwoColour' and self.pelt.colour != 'WHITE':
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
                        self.white_patches = choice(self.pelt.white_patches)
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

    def thoughts(self):
        # actions or thoughts for all cats. These switch either every moon or every time the game is re-opened

        for c in self.all_cats.keys():
            other_cat = random.choice(list(self.all_cats.keys()))
            countdown = int(len(cat_class.all_cats) / 3)
            while other_cat == c:
                other_cat = random.choice(list(self.all_cats.keys()))
                countdown-=1
                if countdown <= 0:
                    continue
            other_cat = self.all_cats.get(other_cat)
            other_name = str(other_cat.name)
            cat = self.all_cats.get(c)
            thoughts = ['Is not thinking about much right now'
                        ]  # placeholder thought - should never appear in game

            if cat.dead:
                # individual thoughts
                starclan_thoughts = [
                    'Is feeling quite lazy',
                    'Is spending a considerable amount of time grooming',
                    'Is looking forward to today', 'Is feeling down...',
                    'Is feeling happy!', 'Is curious about other Clans',
                    'Is feeling sassy today',
                    "Is thinking about a message to send",
                    "Wishes they were still alive",
                    "Is admiring StarClan territory",
                    "Is thinking about their life", "Is missing a loved one",
                    "Is hoping to meet with a medicine cat soon",
                    "Is admiring the stars in their fur",
                    "Is watching over a Clan ceremony",
                    "Is hoping to give a life to a new leader",
                    "Is hoping they will be remembered",
                    "Is watching over the Clan", "Is worried about the Clan",
                    "Is relaxing in the sun", "Is wondering about Twolegs",
                    "Is thinking about their ancient ancestors",
                    "Is worried about the cats in the Dark Forest",
                    "Is thinking of advice to give to a medicine cat",
                    "Is exploring StarClan",
                    "Is sad seeing how the Clan has changed",
                    "Wishes they could speak to old friends",
                    "Is sneezing on stardust",
                    "Is comforting another StarClan cat",
                    "Is exploring StarClan\'s hunting grounds",
                    "Is hunting mice in StarClan",
                    "Is chattering at the birds in StarClan",
                    "Is chasing rabbits in StarClan",
                    "Can feel some cat forgetting them..."
                ]
                # thoughts with other cats that are dead
                if other_cat.dead:
                    starclan_thoughts.extend([
                        'Is sharing tongues with ' + other_name,
                        'Has been spending time with ' + other_name +
                        ' lately', 'Is acting huffy at ' + other_name,
                        'Is sharing a freshkill with ' + other_name,
                        'Is curious about ' + other_name, 'Is talking with ' +
                        other_name, 'Doesn\'t want to talk to ' + other_name,
                        'Is having a serious fight with ' + other_name,
                        'Wants to spend more time with ' + other_name + '!',
                        'Is thinking about future prophecies with ' +
                        other_name,
                        'Is watching over the Clan with ' + other_name,
                        'Is listening to long-forgotten stories about the Clan'
                    ])
                # thoughts with other cats that are alive
                elif not other_cat.dead:
                    starclan_thoughts.extend([
                        'Is watching over ' + other_name,
                        'Is curious about what ' + other_name + ' is doing',
                        'Wants to send a message to ' + other_name,
                        'Is currently walking in the dreams of ' + other_name,
                        'Is proud of ' + other_name, 'Is disappointed in ' +
                        other_name, 'Wants to warn ' + other_name,
                        'Has been following the growth of ' + other_name,
                        'Has seen ' + other_name + '\'s future demise',
                        'Is looking to visit ' + other_name +
                        ' in a dream soon',
                        'Accidentally found themselves in ' + other_name +
                        '\'s dreams the other night', 'Wants to warn ' +
                        other_name + ' about something that will happen soon',
                        'Knows what ' + other_name +
                        '\'s secret is and wants to tell some cat'
                    ])
                # dead young cat thoughts
                if cat.status in [
                        'kitten', 'apprentice', 'medicine cat apprentice'
                ]:
                    starclan_thoughts.extend([
                        'Wishes they had more time to grow up',
                        'Wonders what their full name would have been',
                        'Is bothering older StarClan cats',
                        'Is learning about the other cats in StarClan'
                    ])
                # dead elder thoughts
                elif cat.status == 'elder':
                    starclan_thoughts.extend([
                        'Is grateful that they lived such a long life',
                        'Is happy that their joints no longer ache',
                        'Is telling stories to the younger cats of StarClan',
                        'Watches over the younger cats of StarClan',
                        'Is observing how different the Clan is from when they were alive'
                    ])
                # dead leader thoughts
                elif cat.status == 'leader':
                    starclan_thoughts.extend([
                        'Hoped that they were a good leader',
                        'Wishes that they had ten lives',
                        'Is proud of their clan from StarClan',
                        'Is pleased to see the new direction the Clan is heading in',
                        'Still frets over their beloved former Clanmates from afar'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        starclan_thoughts.extend([
                            'Rejoices with every new kit born to the Clan they still hold so dear'
                        ])

                thoughts = starclan_thoughts  # sets current thought to a random applicable thought

            elif not cat.dead:
                # general individual thoughts
                thoughts = [
                    'Is feeling quite lazy',
                    'Is spending a considerable amount of time grooming',
                    'Is looking forward to today', 'Is feeling down...',
                    'Is feeling excited', 'Is feeling nervous',
                    'Is feeling content', "Is relaxing in camp",
                    'Is daydreaming', 'Is napping',
                    'Thinks they are going crazy', 'Is feeling gloomy',
                    "Is looking around camp", 'Is feeling happy!',
                    'Is curious about the other clans',
                    'Is feeling sassy today',
                    'Wants to spend time alone today',
                    "Is eating some freshkill", 'Is heading to the dirtplace',
                    'Is rethinking their life choices',
                    'Is in the medicine den', 'Is having a good day',
                    'Is having a hard day', 'Is talking to themselves',
                    'Regrets not eating the bird on the freshkill pile earlier',
                    'Is basking in the sun', 'Feels a sense of dread',
                    'Is feeling unappreciated', 'Is staring off into space',
                    'Is worried others are judging them',
                    'Almost choked on their prey',
                    'Is chattering at the birds in the trees above',
                    'Was recently caught humming to themselves',
                    'Had a nightmare involving the rushing river nearby',
                    'Wishes they were still in their nest sleeping',
                    'Is craving the taste of mouse',
                    'Is craving the taste of rabbit',
                    'Is craving the taste of vole',
                    'Is craving the taste of frog',
                    'Is craving the taste of shrew',
                    'Is wondering if they would be a good swimmer',
                    'Is thinking about how awful kittypet food must taste',
                    'Is feeling underappreciated...',
                    'Is staring off into space',
                    'Is picking the burrs from their pelt',
                    'Has a sore paw from a bee sting',
                    'Is sharpening their claws',
                    'Woke up on the wrong side of the nest'
                ]

                # thoughts with other cats who are dead
                if other_cat.dead:
                    # young cat thoughts about dead cat
                    if cat.status in [
                            'kitten', 'apprentice', 'medicine cat apprentice'
                    ]:
                        thoughts.extend([
                            'Is listening to stories about ' + other_name,
                            'Is learning more about ' + other_name,
                            'Is sad they couldn\'t spend time with ' +
                            other_name, 'Is wondering if ' + other_name +
                            ' would have been their friend'
                        ])
                    # older cat thoughts about dead cat
                    elif cat.status in [
                            'warrior', 'medicine cat', 'deputy', 'leader'
                    ]:
                        thoughts.extend([
                            'Is listening to stories about ' + other_name,
                            'Is learning more about ' + other_name,
                            'Is sad they couldn\'t spend more time with ' +
                            other_name, 'Wishes they could visit ' +
                            other_name + ' in StarClan',
                            'Is remembering ' + other_name
                        ])
                    # elder thoughts about dead cat
                    elif cat.status == 'elder':
                        thoughts.extend([
                            'Is telling stories about ' + other_name,
                            'Is sad they couldn\'t spend more time with ' +
                            other_name, 'Wishes they could visit ' +
                            other_name + ' in StarClan',
                            'Is remembering ' + other_name,
                            'Wishes that ' + other_name + ' were still alive',
                            'Found a trinket that used to belong to ' +
                            other_name, 'Is forgetting who ' + other_name +
                            ' was', 'Is thinking fondly of ' + other_name,
                            'Sometimes feels like ' + other_name +
                            " is still right there next to them"
                        ])
                    elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice' or cat.skill == 'strong connection to StarClan':  # medicine cat/strong connection
                        # thoughts about dead cat
                        thoughts.extend([
                            'Was given a prophecy by ' + other_name,
                            'Was sent an omen by ' + other_name,
                            'Is dreaming about ' + other_name +
                            ' who gives them a message', 'Is visited by ' +
                            other_name, 'Senses ' + other_name + ' is nearby',
                            'Saw ' + other_name +
                            ' in a dream, warning them about... something',
                            'Is asking for guidance from ' + other_name,
                            'Is wondering desperately why ' + other_name +
                            ' wasn\'t there when they needed them',
                            'Is sure that they saw ' + other_name +
                            ' appear in the forest today... why?',
                            'Blames themselves for ' + other_name +
                            '\'s death...'
                        ])

                # thoughts with other cat who is alive
                elif not other_cat.dead and not other_cat.exiled:
                    if cat.status in [
                            'warrior', 'elder', 'deputy', 'leader'
                    ] and other_cat.status == 'apprentice':  # older cat thoughts about younger cat
                        thoughts.extend([
                            'Is giving ' + other_name + ' advice',
                            'Is telling ' + other_name +
                            ' about a hunting technique',
                            'Is scolding ' + other_name,
                            'Is giving ' + other_name + ' a task', other_name +
                            ' reminds them of when they were their age',
                            'Is telling ' + other_name +
                            ' about their own days as an apprentice',
                            'Is frustrated that ' + other_name +
                            ' won\'t take their duties more seriously',
                            'Can\'t believe ' + other_name +
                            ' caught that rabbit on patrol yesterday',
                            'Doesn\'t think that ' + other_name +
                            ' has been completely honest lately',
                            'Is fuming from an argument with ' + other_name
                        ])
                    elif cat.status in ['warrior', 'elder', 'deputy'] and other_cat.status == 'apprentice':
                        thoughts.extend([
                            'Has successfully tricked ' + other_name +
                            ' into believing a crazy tale about the Clan leader',
                        ])

                    # kit thoughts
                    if cat.status == 'kitten':
                        # kit thoughts with other kit
                        if other_cat.status == 'kitten':
                            thoughts.extend([
                                'Pretends to be a warrior with ' + other_name,
                                'Plays mossball with ' + other_name,
                                'Has a mock battle with ' + other_name,
                                'Comes up with a plan to sneak out of camp with '
                                + other_name, 'Whines about ' + other_name,
                                'Chomps on ' + other_name + '\'s ear',
                                'Is pretending to ward off foxes with ' +
                                other_name,
                                'Is pretending to fight off badgers with ' +
                                other_name, 'Is racing ' + other_name +
                                ' back and forth across the camp clearing',
                                'Is talking excitedly with ' + other_name +
                                ' about how cool their Clan leader is',
                                'Is talking excitedly with ' + other_name +
                                ' about how cool their Clan deputy is',
                                'Is jealous that ' + other_name +
                                ' is getting more attention than them',
                                'Won\'t stop crying that they\'re hungry... but they just ate!'
                            ])
                        # kit thoughts about older cat
                        elif other_cat.status != 'kitten':
                            thoughts.extend([
                                'Is biting ' + other_name + '\'s tail',
                                'Sticks their tongue out at ' + other_name,
                                'Whines to ' + other_name,
                                'Is demanding ' + other_name + '\'s attention',
                                'Really looks up to ' + other_name,
                                'Is hiding under a bush from ' + other_name +
                                ', but they can\'t stop giggling',
                                'Is pretending to be ' + other_name
                            ])
                    elif cat.status in [
                            'apprentice', 'medicine cat apprentice', 'warrior',
                            'medicine cat', 'deputy', 'leader'
                    ]:
                        # older cat thoughts about kit
                        if other_cat.status == 'kitten':
                            thoughts.extend([
                                'Trips over ' + other_name,
                                'Is giving advice to ' + other_name,
                                'Is giving ' + other_name +
                                ' a badger ride on their back!',
                                'Had to nip ' + other_name +
                                ' on the rump because they were being naughty',
                                'Is promising to take ' + other_name +
                                ' outside of camp if they behave',
                                'Is watching ' + other_name +
                                ' perform an almost-decent hunting crouch',
                                'Can\'t take their eyes off of ' + other_name +
                                ' for more than a few seconds',
                                'Gave ' + other_name +
                                ' a trinket they found while out on patrol today'
                            ])
                            if cat.ID not in [other_cat.parent1, other_cat.parent2]:
                                thoughts.append('Hopes that their own kits are as cute as ' +
                                other_name + ' someday')
                        else:
                            thoughts.extend([
                                'Is fighting with ' + other_name,
                                'Is talking with ' + other_name,
                                'Is sharing prey with ' + other_name,
                                'Heard a rumor about ' + other_name,
                                'Just told ' + other_name + ' a hilarious joke'
                            ])

                    if other_cat.is_potential_mate(cat,for_love_interest=True):
                        thoughts.extend([
                            'Is developing a crush on ' + other_name,
                            'Is spending a lot of time with ' + other_name,
                            'Feels guilty about hurting ' + other_name +
                            '\'s feelings',
                            'Can\'t seem to stop talking about ' + other_name,
                            'Would spend the entire day with ' + other_name +
                            ' if they could',
                            'Was caught enjoying a moonlit stroll with ' +
                            other_name + ' last night...',
                            'Keeps shyly glancing over at ' + other_name +
                            ' as the Clan talks about kits',
                            'Gave a pretty flower they found to ' + other_name,
                            'Is admiring ' + other_name + ' from afar...',
                            'Is thinking of the best ways to impress ' +
                            other_name, 'Doesn\'t want ' + other_name +
                            ' to overwork themselves',
                            'Is rolling around a little too playfully with ' +
                            other_name + '...',
                            'Is wondering what it would be like to grow old with '
                            + other_name
                        ])

                # kitten specific thoughts
                if cat.status == 'kitten':
                    thoughts.extend([
                        'Plays mossball by themselves',
                        'Is annoying older cats',
                        'Wonders who their mentor will be',
                        'Wants to take a nap', 'Tries to sneak out of camp',
                        'Is rolling around on the ground',
                        'Is chasing their tail', 'Is playing with a stick',
                        'Is nervous for their apprentice ceremony',
                        'Is excited for their apprentice ceremony',
                        'Is scared after having a nightmare',
                        'Wants to snuggle',
                        'Is asking older cats how kits are born',
                        'Wishes other cats would stop babying them',
                        'Is hiding from other cats',
                        'Is bouncing around in excitement',
                        'Whines about being hungry',
                        'Is asking the older cats about how kittens are made',
                        'Is pestering older cats to play with them',
                        'Is whining for milk', 'Is whimpering in their sleep',
                        'Is trying to growl menacingly',
                        'Is adamantly refusing to take their nap',
                        'Is batting pebbles across the camp clearing',
                        'Is crying after rough-housing too hard with the older cats',
                        'Is regretting eating the bug that they caught',
                        'Recently took a tumble off of a log',
                        'Is busy mastering a battle move they are performing incorrectly',
                        'Refuses to eat the herbs the medicine cat has given them for their tummy',
                        'Is hatching a plan to sneak out of camp and play',
                        'Is running like a whirlwind around the camp',
                        'Is pretending to be the clan leader',
                        'Doesn\'t want to grow up yet...',
                        'Got in trouble for bringing thorns into the nest'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend([
                            'Was nipped on the rump by an elder for being naughty'
                        ])

                    # kitten trait thoughts
                    if cat.trait == 'charming':
                        thoughts.extend([
                            'Is rolling around cutely while warriors look upon them',
                            'Is rubbing up against the warriors\' legs',
                            'Is hoping the patrol will come back with a special gift for them like usual',
                            'Is trying to purr their way out of trouble with the medicine cat'
                        ])
                    elif cat.trait == 'impulsive':
                        thoughts.extend([
                            'Keeps streaking across the clearing',
                            'Is stuck in a tree... again',
                            'Is complaining of a tummy ache after eating too much',
                            'Is awfully close to getting a nip on the rump for misbehaving',
                            'Is waiting for an opportunity to sprint out of sight'
                        ])
                    elif cat.trait == 'nervous':
                        thoughts.extend([
                            'Was startled by a croaking frog',
                            'Is doing their best not to get stepped on by the bigger cats'
                        ])

                    # kitten and skill specific thoughts
                    elif cat.skills == 'strong connection to starclan':
                        thoughts.extend([
                            'Thinks they saw a StarClan cat in their dreams',
                            'Is scrambling the medicine cat\'s herbs!',
                            'Is pretending to be the medicine cat'
                        ])

                # Traits are sorted by rank and age group
                # Kittens, Cats under 12 moons, all apprentices, warrior apprentices, medicine at apprentices,
                # warriors, deputy, leader, medicine cat, elders, cats over 12 moons old, active cats

                # kitten and warrior apprentice thoughts
                elif cat.status != 'medicine cat apprentice' and cat.status != 'warrior' and cat.status != 'deputy' and cat.status != 'medicine cat' and cat.status != 'leader' and cat.status != 'elder' and cat.status != 'queen':
                    thoughts.extend([
                        'Wonders what their full name will be',
                        'Pretends to be a warrior',
                        "Practices the hunting crouch",
                        'Pretends to fight an enemy warrior',
                        'Wants to be a warrior already!',
                        'Can\'t wait to be a warrior',
                        'Is pretending to be deputy',
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend(
                            ['Is helping the elders with their ticks'])

                # general apprentice thoughts
                elif cat.status == 'apprentice' or cat.status == 'medicine cat apprentice':
                    thoughts.extend([
                        'Is gathering moss',
                        'Is gossiping',
                        'Is acting angsty',
                        'Is dreading their apprentice duties',
                        'Fell into the nearby creek yesterday and is still feeling damp',
                        'Is making their mentor laugh',
                        'Is really bonding with their mentor',
                        'Is having a hard time keeping up with their training',
                        'Was tasked with lining nests with fresh moss today',
                        'Is dreaming of someday making their Clan proud',
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is awkwardly deflecting kits\' questions about where kits come from',
                            'Was put on kit-sitting duty',
                            'Is showing off to the kits',
                            'Is telling off kits for being immature',
                            'Is rambling on to kits about the importance of respecting their elders'
                        ])
                    elif other_cat.status == 'elder':
                        thoughts.extend([
                            'Was asked to gather fresh moss for the elders\' bedding',
                            'Plans to visit the elders soon',
                            'Is checking in on the elder\'s den',
                            'Plans to help the elders with their ticks'
                        ])
                    # checks for specific traits  (unused traits: 'calm', 'compassionate', 'faithful', 'cold', childish, confident, fierce, patient, sneaky, strange, thoughtful
                    if cat.trait == 'adventurous':
                        thoughts.extend([
                            'Is quietly trying to recruit other apprentices for a quick adventure'
                        ])
                    elif cat.trait == 'altruistic':
                        thoughts.extend([
                            'Is thinking of giving their mentor a gift for their hard work',
                            'Made a keen suggestion to their mentor the other day'
                        ])
                    elif cat.trait == 'ambitious':
                        thoughts.extend([
                            'Is asking the Clan leader what they can do to help out around camp',
                            'Has been asking their mentor for more training',
                            'Tries to put on a brave face for their fellow apprentices',
                            'Is feeling proud of themselves',
                            'Made sure to wake up early to train',
                            'Is daydreaming about a Clan celebration in their honor someday'
                        ])
                    elif cat.trait == 'bloodthirsty':
                        thoughts.extend([
                            'Starts a fight with another apprentice',
                            'Is hoping their warrior name will end in -claw'
                        ])
                    elif cat.trait == 'bold':
                        thoughts.extend(
                            ['Winked cheekily at another apprentice'])
                    elif cat.trait == 'careful':
                        thoughts.extend(
                            ['Is asking if they need more training'])
                    elif cat.trait == 'charismatic':
                        thoughts.extend([
                            'Winked playfully at another apprentice from across the clearing!',
                            'Is this moon\'s heartthrob to the other apprentices',
                            'Has recently given a wonderful speech to fellow apprentices, boosting morale'
                        ])
                        # checks for specific roles
                        if other_cat.status == 'kitten':
                            thoughts.extend([
                                'Has the kits very engaged in a very, very tall tale'
                            ])
                        elif cat.status == 'elder':
                            thoughts.extend(
                                ['Is a favorite among the elders lately'])
                    elif cat.trait == 'daring':
                        thoughts.extend(['Is itching to go out and train'])
                    elif cat.trait == 'empathetic':
                        thoughts.extend([
                            'Is doing extra apprentice tasks around camp, to help lighten the load'
                        ])
                    elif cat.trait == 'insecure':
                        thoughts.extend([
                            'Doesn\'t think that they have performing up to their mentor\'s standards lately...',
                        ])
                    elif cat.trait == 'lonesome':
                        thoughts.extend(
                            ['Is feeling cramped in the apprentice\'s den'])
                    elif cat.trait == 'loving':
                        thoughts.extend([
                            'Is listening to another apprentice\'s troubles sympathetically'
                        ])
                    elif cat.trait == 'loyal':
                        thoughts.extend([
                            'Is listening to their mentor intently',
                            'Proclaimed to their mentor their unwavering loyalty'
                        ])
                    elif cat.trait == 'nervous':
                        thoughts.extend([
                            'Is hoping to not train with their mentor today...',
                            'Wishes they were back in the nursery',
                            'Has agreed to their mentor\'s orders recently, despite their own doubts',
                        ])
                    elif cat.trait == 'playful':
                        thoughts.extend([
                            'Won\'t stop making funny faces when their mentor\'s back is turned',
                            'Annoyed their mentor on accident the other day',
                            'Successfully lightened a dreary mood while out training the other day',
                        ])
                    elif cat.trait == 'responsible':
                        thoughts.extend([
                            'Is licking their chest in embarrassment after being praised by their mentor',
                            'Is asking their mentor what they can do to be helpful around camp today'
                        ])
                    elif cat.trait == 'righteous':
                        thoughts.extend([
                            'Is refusing to follow their mentor\'s recent orders due to their own morals'
                        ])
                    elif cat.trait == 'shameless':
                        thoughts.extend(
                            ['Was found napping in the warrior\'s den!'])
                    elif cat.trait == 'strict':
                        thoughts.extend([
                            'Is busy chastising fellow apprentices... but no cat is sure what for',
                            'Is participating in a rather rigorous training session'
                        ])
                    elif cat.trait == 'troublesome':
                        thoughts.extend([
                            'Is ignoring their mentor\'s orders',
                            'Is making other apprentices laugh',
                            'Got in trouble for shirking their training the other day...'
                        ])
                    elif cat.trait == 'vengeful':
                        thoughts.extend(['Snaps at another apprentice'])
                    elif cat.trait == 'wise':
                        thoughts.extend([
                            'Is giving somber advice to a fellow apprentice',
                            'Was sought out by another apprentice recently for their wisdom'
                        ])

                    # warrior apprentice specific thoughts
                    if cat.status == 'apprentice':
                        thoughts.extend([
                            'Is thinking about the time they caught a huge rabbit',
                            'Practices some battle moves',
                            'Is helping to reinforce the camp wall with brambles',
                            'Is daydreaming about having a mate and kits someday',
                            'Had quite the adventure today'
                        ])
                        # role specific apprentice thoughts
                        # unused traits: adventurous, altruistic, calm, careful, charismatic, childish, cold, compassionate, empathetic, faithful, lonesome, loving, loyal,
                        # patient, playful, responsible, righteous, shameless, sneaky, strange, strict, troublesome, vengeful, wise
                        if other_cat.status == 'elder':
                            thoughts.extend(
                                ['Is helping to repair the elder\'s den'])
                        # trait specific apprentice thoughts
                        if cat.trait == 'ambitious':
                            thoughts.extend([
                                'Begs to be made a warrior early',
                                'Seems to be ordering their fellow apprentices around',
                                'Has been catching the most prey out of all the apprentices'
                            ])
                        elif cat.trait == 'bloodthirsty':
                            thoughts.extend([
                                'Pesters their mentor about doing battle training',
                                'Is thinking about murder',
                                'Draws blood during their battle training',
                            ])
                        elif cat.trait == 'cold':
                            thoughts.extend([
                                'Is hoping their warrior name will end in -claw'
                            ])
                        elif cat.trait == 'bold':
                            thoughts.extend([
                                'Is criticizing their mentor',
                                'Taunted rival Clan apprentices at the border the other day',
                                'Is looking to challenge a warrior to a sparring match'
                            ])
                        elif cat.trait == 'confident':
                            thoughts.extend([
                                'Is sure that they\'ll be made into a warrior today'
                            ])
                        elif cat.trait == 'daring':
                            thoughts.extend([
                                'Is being scolded by the deputy for reckless behavior while out training'
                            ])
                        elif cat.trait == 'fierce':
                            thoughts.extend([
                                'Is showing off their new battle moves',
                                'Is pushing hard for more battle training',
                                'Was recently chastised by their mentor for reckless behaviour out on patrol',
                                'Practiced battle moves with their claws out'
                            ])
                        elif cat.trait == 'insecure':
                            thoughts.extend([
                                'Is wondering if they are good enough to be a warrior...',
                                'Wonders if the medicine cat life would have better suited them...',
                                'Is reluctant to spar with their mentor today',
                                'Doesn\'t think their hauls on hunting patrols have been substantial enough as of late'
                            ])
                        elif cat.trait == 'nervous':
                            thoughts.extend([
                                'Hopes that they will be a strong enough warrior...',
                                'Is wondering if they are more suited for life as a medicine cat...',
                                'Was startled by a squirrel while out training!',
                            ])
                        elif cat.trait == 'thoughtful':
                            thoughts.extend([
                                'Offered to go on the dawn patrol with their mentor'
                            ])

                    # medicine cat apprentice specific thoughts
                    if cat.status == 'medicine cat apprentice':
                        thoughts.extend([
                            'Is wondering if they are good enough to become a medicine cat',
                            'Wishes the other apprentices could understand how they feel',
                            'Helps apply a poultice to a small wound',
                            'Is enjoying learning all of the herbs a medicine cat needs!'
                        ])
                        # checks for specific roles
                        if other_cat.status == 'kitten':
                            thoughts.extend([])
                        elif other_cat.status == 'elder':
                            thoughts.extend([])
                        # trait specific medicine cat apprentice thoughts
                        # unused traits: adventurous, altruistic, ambitious, bloodthirsty, bold, calm, careful, charismatic, childish, compassionate, confident, daring, empathetic,
                        # faithful, fierce, lonesome, loving, loyal, patient, playful, responsible, righteous, shameless, sneaky, strange, strict, thoughtful, troublesome, vengeful, wise
                        if cat.trait == 'cold':
                            thoughts.extend([
                                'Is hoping their medicine cat name will end in -claw'
                            ])
                        elif cat.trait == 'insecure':
                            thoughts.extend([
                                'Is wondering if they are good enough to be a medicine cat...',
                                'Wonders if the warrior life would have better suited them...'
                            ])
                        elif cat.trait == 'nervous':
                            thoughts.extend([
                                'Is wondering if they are more suited for life as a warrior...'
                            ])

                # elder specific thoughts
                if cat.status == 'elder':
                    thoughts.extend([
                        'Is complaining about their nest being too rough',
                        'Is complaining about their aching joints',
                        'Is telling stories about when they were young',
                        'Is giving advice to younger cats',
                        'Is complaining about thorns in their nest',
                        'Is bossing around the younger cats',
                        'Is telling scary stories to the younger cats',
                        'Is snoring in their sleep',
                        'Thinking about how too many cats die young',
                        'Is complaining about being cold',
                        'Is grateful they have lived so long',
                        'Is sharing their wisdom',
                        'Is being pestered by fleas',
                        'Is requesting an apprentice\'s help with their ticks',
                        'Is predicting rainy weather based on their aching bones',
                        'Hopes their legacy will continue on after their death',
                        'Is sharing wisdom with younger cats that is... less than helpful',
                        'Is recounting daring expeditions for the younger cats to hear',
                        'Is in quite the mood today',
                        'Is feeling rather chipper today',
                        'Is snoring loudly in their sleep',
                        'Is telling a rather tall tale to any cat who will listen',
                        'Is asking apprentices to help check them for ticks',
                        'Is assisting with camp cleanup',
                        'Feels too stiff to leave their nest today...',
                        'Has been sleeping a lot more as of late',
                        'Has been enjoying their old age',
                        'Got lost outside of camp for a bit today',
                        'Doesn\'t like how times have changed since they were young',
                        'Is feeling rather cross today',
                        'Thinks that times have changed for the better since they were young',
                        'Is recalling something no other cat remembers anymore',
                        'Is enjoying the warm sun in the camp clearing',
                        'Is grumbling about the weather',
                        'Is giving the Clan leader attitude'
                    ])
                    # no trait specific elder thoughts yet

                # medicine cat specific thoughts
                if cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
                    thoughts.extend([
                        'Is looking for herbs',
                        'Is organizing the herb stores',
                        'Is drying some herbs', 'Is counting the poppy seeds',
                        'Is gathering cobwebs', 'Is interpreting an omen',
                        'Is interpreting a prophecy',
                        'Hopes for a message from StarClan soon',
                        'Is checking up on the warriors',
                        'Is feeling stressed taking care of the Clan',
                        'Is wondering if they could borrow some catmint from the other Clans',
                        'Is wrapping a wound with cobwebs',
                        'Is clearing out old herbs',
                        'Is tending growing herbs', 'Is making new nests',
                        'Wishes they had an extra set of paws',
                        'Is carefully picking up spilled poppy seeds',
                        'Is out gathering more cobwebs',
                        'Is reciting the names of herbs aloud',
                        'Was startled awake in the wee hours by a vivid dream',
                        'Is running low on catmint',
                        'Is running low on marigold',
                        'Is running low on burdock root',
                        'Is running low on poppy seeds',
                        'Is running low on cobwebs',
                        'Is running low on feverfew',
                        'Is running low on borage leaves',
                        'Is running low on tansy',
                        'Is running low on mouse bile',
                        'Plans to go out gathering herbs today',
                        'Is looking forward to the half-moon meeting',
                        'Is struggling to remember all of the names of herbs',
                        'Is helping organize the herb stores',
                        'Is proud of their ability to care for their Clanmates',
                        'Made a mess of the herbs and is panicking',
                        'Has been hearing the voices of StarClan cats...',
                        'Has the foul taste of bitter herbs in their mouth',
                        'Is happy that they chose life as a medicine cat',
                        'Is lining nests with fresh moss and feathers'
                    ])
                    # medicine cat only thoughts no apprentices allowed
                    if cat.status != 'medicine cat apprentice':
                        thoughts.extend(
                            ['Is thinking about taking on a new apprentice'])
                    # checks for specific roles
                    if cat.status == 'kitten':
                        thoughts.extend([
                            'Is teaching kits about what plants to stay away from',
                            'Chased kits out of their den',
                        ])
                        # roles + traits
                        if cat.trait == 'bloodthirsty':
                            thoughts.extend([
                                'Encourages kits to eat some strange red berries'
                            ])
                    # trait specific medicine cat thoughts
                    if cat.trait == 'adventurous':
                        thoughts.extend([
                            'Heads out of Clan territories to look for new herbs'
                        ])
                    elif cat.trait == 'altruistic':
                        thoughts.extend(['Declines to eat when prey is low'])
                    elif cat.trait == 'ambitious':
                        thoughts.extend([
                            'Insists on taking on more tasks',
                            'Spends all day gathering herbs'
                        ])
                    elif cat.trait == 'bloodthirsty':
                        thoughts.extend([
                            'Is gathering deathberries',
                            'Has been disappearing a lot lately',
                            'Insists only on treating cats who need it',
                            'Is ripping some leaves to shreds',
                            'Debates becoming a warrior',
                            'Gives the wrong herbs to a warrior on purpose'
                        ])
                    elif cat.trait == 'bold':
                        thoughts.extend([
                            'Decides to try a new herb as treatment for an injury'
                        ])
                    elif cat.trait == 'calm':
                        thoughts.extend(
                            ['Stays composed when treating a severe injury'])
                    elif cat.trait == 'careful':
                        thoughts.extend(
                            ['Counts and recounts the poppy seeds'])
                    elif cat.trait == 'charismatic':
                        thoughts.extend(
                            ['Is doing their daily checkup on the elders'])
                    elif cat.trait == 'childish':
                        thoughts.extend(
                            ['Bounces excitedly at the half-moon meeting'])
                    elif cat.trait == 'cold':
                        thoughts.extend(
                            ['Refuses to treat an injured, abandoned kit'])
                    elif cat.trait == 'compassionate':
                        thoughts.extend([
                            'Works long into the night taking care of the Clan'
                        ])
                    elif cat.trait == 'confident':
                        thoughts.extend([
                            'Is proud of their ability to care for their Clanmates'
                        ])
                    elif cat.trait == 'daring':
                        thoughts.extend(
                            ['Steals catmint from a Twoleg garden'])
                    elif cat.trait == 'empathetic':
                        thoughts.extend([
                            'Listens to the apprentices complain about their training'
                        ])
                    elif cat.trait == 'faithful':
                        thoughts.extend([
                            'Has been hearing the voices of StarClan cats...'
                        ])
                    elif cat.trait == 'fierce':
                        thoughts.extend(
                            ['Insists on joining battle training once a moon'])
                    elif cat.trait == 'insecure':
                        thoughts.extend([
                            'Is saying that they don\'t deserve their full name'
                        ])
                    elif cat.trait == 'lonesome':
                        thoughts.extend([
                            'Is wishing they could have a mate and kits',
                            'Wishes their Clanmates could understand their struggles'
                        ])
                    elif cat.trait == 'loving':
                        thoughts.extend(['Watches over some newborn kits'])
                    elif cat.trait == 'loyal':
                        thoughts.extend([
                            'Refuses to share gossip at the half-moon meeting',
                            'Refuses to give another Clan\'s medicine cat some herbs'
                        ])
                    elif cat.trait == 'nervous':
                        thoughts.extend(
                            ['Recounts the amount of catmint in their stores'])
                    elif cat.trait == 'patient':
                        thoughts.extend(
                            ['Helps a warrior regain their strength'])
                    elif cat.trait == 'playful':
                        thoughts.extend(
                            ['Excitedly teaches the kits about basic herbs'])
                    elif cat.trait == 'responsible':
                        thoughts.extend([
                            'Ensures that all of their duties are taken care of'
                        ])
                    elif cat.trait == 'righteous':
                        thoughts.extend(['Gives herbs to an injured loner'])
                    elif cat.trait == 'shameless':
                        thoughts.extend(['Refuses to groom themselves'])
                    elif cat.trait == 'sneaky':
                        thoughts.extend([
                            'Seems to be hiding something in the medicine they give to the leader'
                        ])
                    elif cat.trait == 'strange':
                        thoughts.extend([
                            'Insists everyone eat chamomile leaves everyday at moonhigh',
                            'Sleeps in the middle of the clearing',
                            'Looks dazed', 'Hisses at the kits randomly'
                        ])
                    elif cat.trait == 'strict':
                        thoughts.extend([
                            'Forbids anyone from disturbing them when working'
                        ])
                    elif cat.trait == 'thoughtful':
                        thoughts.extend(['Realizes what an omen might mean'])
                    elif cat.trait == 'troublesome':
                        thoughts.extend(['Mixes up herbs'])
                    elif cat.trait == 'vengeful':
                        thoughts.extend(
                            ['Refuses to treat a cat that once bullied them'])
                    elif cat.trait == 'wise':
                        thoughts.extend(
                            ['Tells an ancient tale about StarClan'])

                # deputy specific thoughts
                if cat.status == 'deputy':
                    thoughts.extend([
                        'Is assigning cats to a border patrol',
                        'Is assigning cats to a hunting patrol',
                        'Is wondering what it would be like to be a leader',
                        'Is stressed about organizing patrols',
                        'Wonders who will give them nine lives',
                        'Feels overworked', 'Is hoping for a break',
                        'Is assessing the apprentices',
                        'Wishes they had an extra set of paws',
                        'Is assigning cats to the dawn patrol',
                        'Is assigning cats to the hunting patrol',
                        'Is assigning cats to patrol the borders',
                        'Can\'t believe they overslept today',
                        'Is unsure of what the rest of the clan thinks of them as deputy',
                        'Is doing their best to honor their Clan and their leader',
                        'Must speak with the leader soon about something they found while out on patrol'
                    ])
                    # trait specific deputy thoughts
                    if cat.trait == 'bloodthirsty':
                        thoughts.extend([
                            'Thinks about killing the leader and staging it as an accident',
                            'Encourages the leader to start a war'
                        ])
                    elif cat.trait == 'strange':
                        thoughts.extend([
                            'Accidentally assigns the same cat to three patrols',
                            'Insists a hunting patrol only bring back mice',
                            'Goes missing and comes back smelling like garlic',
                            'Is making odd noises'
                        ])

                # leader specific thoughts
                if cat.status == 'leader':
                    thoughts.extend([
                        'Is hoping for a sign from StarClan',
                        'Is hoping that they are leading their Clan well',
                        'Thinks about who should mentor new apprentices',
                        'Is worried about Clan relations',
                        'Tries to set a good example for the deputy',
                        'Is assessing some apprentices',
                        'Is thinking about forming an alliance',
                        'Is thinking about battle strategies',
                        'Almost lost a life recently',
                        'Is counting how many lives they have left',
                        'Is thinking about what to say at the Gathering',
                        'Is questioning their ability to lead',
                        'Is dreading the Clan meeting they must call later today',
                        'Is finding the responsibility of leadership to be quite the heavy burden',
                        'Is feeling blessed by StarClan this moon',
                        'Is making a solemn vow to protect their Clanmates',
                        'Has been letting their deputy call the shots recently, and is proud of their initiative',
                        'Called an important Clan meeting recently',
                        'Is pondering the next mentors for the kits of the Clan',
                        'Think they have been hearing the voices of StarClan cats...',
                        'Is pondering recent dreams they have had... perhaps from StarClan?',
                        'Recently called a Clan meeting, but forgot what to say'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Has recently picked up the scent of mischievous kits in their den...'
                        ])
                    # trait specific leader thoughts
                    if cat.trait == 'bloodthirsty':
                        thoughts.extend([
                            'Encourages warriors to start fights on border patrols',
                            'Is debating if they should declare a war with another Clan',
                            'Is wondering if they could hold apprentice ceremonies at 4 moons old instead'
                        ])
                    elif cat.trait == 'strange':
                        thoughts.extend([
                            'No thoughts, head empty',
                            'Insists they they received ten lives instead of nine',
                            'Has a crazed look in their eyes',
                            'Is wondering how many cats would agree to changing the Clan\'s name...'
                        ])

                # warrior specific thoughts
                if cat.status == 'warrior':
                    thoughts.extend(['Wants to be chosen as the new deputy'])
                    if cat.trait == 'ambitious':
                        thoughts.extend([
                            'Is asking the Clan leader what they can do to help out around camp',
                            'Has been imitating the Clan leader\'s behaviour recently',
                            'Envies the deputy\'s position',
                        ])
                    elif cat.trait == 'fierce':
                        thoughts.extend([
                            'Was recently chastised by the deputy for reckless behaviour out on patrol'
                        ])
                    elif cat.trait == 'loyal':
                        thoughts.extend([
                            'Is listening to the Clan leader intently',
                            'Is listening to the deputy intently',
                            'Is telling the Clan leader details about the recent patrol',
                            'Is telling the deputy details about the recent patrol',
                            'Is offering constructive criticism to the deputy',
                            'Has agreed to their Clan leader\'s orders recently, despite their own doubts',
                            'Proclaimed to the Clan leader their unwavering loyalty'
                        ])
                    elif cat.trait == 'righteous':
                        thoughts.extend([
                            'Is refusing to follow the deputy\'s recent orders due to their own morals'
                        ])

                # active cat specific thoughts
                if cat.status == 'warrior':
                    thoughts.extend([
                        'Caught scent of a fox earlier',
                        'Caught scent of an enemy warrior earlier',
                        'Is helping to gather herbs', 'Is thinking about love',
                        'Is decorating their nest',
                        'Is reinforcing the camp with brambles',
                        'Caught a huge rabbit',
                        'Tries to set a good example for younger cats',
                        'Wants to go on a patrol',
                        'Wants to go on a hunting patrol',
                        'Is guarding the camp entrance', 'Is gossiping',
                        'Plans to visit the medicine cat',
                        'Is sharpening their claws',
                        'Is helping to escort the medicine cat to gather herbs',
                        'Is feeling sore', 'Is being pestered by flies',
                        'Feels overworked',
                        'Is exhausted from yesterday\'s patrol',
                        'Wants to have kits',
                        'Is sparring with some Clanmates',
                        'Fell into the nearby creek yesterday and is still feeling damp',
                        'Is guarding the camp entrance',
                        'Is helping to reinforce the nursery wall with brambles',
                        'Is assigned to the dawn patrol tomorrow',
                        'Is assigned to the hunting patrol today',
                        'Is thinking about kits'
                    ])
                    # check for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend(['Is watching over the kits'])
                        if cat.trait == 'cold':
                            thoughts.extend([
                                'Recently snapped at the kits, making them cry'
                            ])
                        elif cat.trait == 'childish':
                            thoughts.extend(
                                ['Is teaching new games to the kits'])
                        elif cat.trait == 'empathetic':
                            thoughts.extend([
                                'Is comforting kits after a scary experience'
                            ])
                        elif cat.trait == 'fierce':
                            thoughts.extend([
                                'Is roaring playfully at kits, making them laugh',
                                'Has been rough housing with the kits a little too hard lately'
                            ])
                        elif cat.trait == 'loving':
                            thoughts.extend(
                                ['Is helping out with kits around camp'])
                        elif cat.trait == 'playful':
                            thoughts.extend([
                                'Is giving kits badger rides on their back!',
                                'Is riling up the kits, much to the queens\'s dismay'
                            ])
                        elif cat.trait == 'shameless':
                            thoughts.extend([
                                'Pushed a kit out of their way thoughtlessly'
                            ])
                        elif cat.trait == 'strict':
                            thoughts.extend(
                                ['Is grumbling about troublesome kits'])
                        elif cat.trait == 'thoughtful':
                            thoughts.extend([
                                'Is bringing soaked moss to the queens in the nursery',
                                'Is promising to take the kits out on a stroll today if they behave',
                                'Plucked feathers from their meal for the kits to play with',
                                'Is offering to look after the kits while the queens rest'
                            ])
                        elif cat.trait == 'troublesome':
                            thoughts.extend([
                                'Got scolded for telling the kits a naughty joke!'
                            ])
                    elif other_cat.status == 'elder':
                        if cat.trait == 'calm':
                            thoughts.extend(
                                ['Is politely listening to elders\'s stories'])
                        elif cat.trait == 'charismatic':
                            thoughts.extend(
                                ['Is a favorite among the elders lately'])
                        elif cat.trait == 'compassionate':
                            thoughts.extend([
                                'Helped the elders to rise stiffly from their nests this morning'
                            ])
                        elif cat.trait == 'empathetic':
                            thoughts.extend([
                                'Volunteered to gather fresh lining to the elders\' nests'
                            ])
                        elif cat.trait == 'loyal':
                            thoughts.extend([
                                'Is checking in on the elder\'s den',
                                'Is rambling on to younger cats about the importance of respecting their elders'
                            ])
                        elif cat.trait == 'thoughtful':
                            thoughts.extend([
                                'Gave an elder their favorite piece of fresh kill',
                                'Is making sure that the elders all have fresh bedding'
                            ])
                        elif cat.trait == 'troublesome':
                            thoughts.extend([
                                'Recently was scolded for eating prey before the queens and elders'
                            ])
                    elif other_cat.status == 'apprentice':
                        thoughts.extend([
                            'Has the apprentices very engaged in a very, very tall tale'
                        ])
                        if cat.trait == 'childish':
                            thoughts.extend(
                                ['Is pouncing on unsuspecting apprentices'])
                        elif cat.trait == 'cold':
                            thoughts.extend([
                                'Is scolding the apprentices over something slight'
                            ])
                        elif cat.trait == 'thoughtful':
                            thoughts.extend([
                                'Is hosting a modified training session for the beginner apprentices'
                            ])
                    # unused traits: bloodthirsty, calm, charismatic, cold, compassionate, empathetic, lonesome, loyal, patient, righteous, shameless, sneaky, strange, vengeful, wise
                    if cat.trait == 'adventurous':
                        thoughts.extend([
                            'Is itching to explore the land beyond their Clan\'s territory',
                            'Wants to go on a journey',
                            'Wishes their leader would choose them to go on a quest'
                        ])
                    elif cat.trait == 'altruistic':
                        thoughts.extend([
                            'Offered to walk at the front of the patrol',
                            'Offered to stick their nose inside a badger set to see if the badger was still there',
                            'Offered to stick their nose inside a fox den to see if the fox was still there',
                            'Volunteered for extra patrols',
                            'Volunteered for extra duties',
                            'Volunteered to stand guard of the camp'
                        ])
                    elif cat.trait == 'ambitious':
                        thoughts.extend([
                            'Is boasting loudly about having defeated an enemy warrior on patrol the other day',
                            'Has been taking on extra patrols lately',
                        ])
                    elif cat.trait == 'bold':
                        thoughts.extend([
                            'Is getting some looks after speaking up at the last Clan meeting',
                            'Spoke up recently at a Clan meeting'
                        ])
                    elif cat.trait == 'careful':
                        thoughts.extend([
                            'Is dutifully standing guard outside of camp',
                            'Is helping to reinforce the nursery walls',
                            'Is helping to reinforce the camp walls',
                            'Is patching up a hole in the camp wall',
                            'Is helping to reinforce the walls of the elders\' den',
                            'Is going back to check out an old fox burrow they discovered yesterday, just to be safe',
                            'Is going back to check out an old badger set they discovered yesterday, just to be safe'
                        ])
                    elif cat.trait == 'childish':
                        thoughts.extend([
                            'Splashes in a puddle of water during a patrol',
                            'Jumps around while on patrol',
                        ])
                    elif cat.trait == 'confident':
                        thoughts.extend([
                            'Boasts about how much fresh kill they intend to bring back to camp today',
                            'Thinks that they are the best hunter in the Clan',
                            'Thinks that they are the fastest runner in the Clan',
                            'Is showing off their battle moves',
                            'Thinks that they are the fiercest fighter in the Clan'
                        ])
                    elif cat.trait == 'daring':
                        thoughts.extend([
                            'Batted at a snake on a patrol recently and fled',
                            'Is leaping from boulder to boulder out in the forest',
                            'Is climbing to the top of a very tall tree!',
                            'Recently avoided a monster on the Thunderpath by the skin of their teeth!'
                        ])
                    elif cat.trait == 'faithful':
                        thoughts.extend([
                            'Is thanking StarClan for their catch out on a hunting patrol today'
                        ])
                    elif cat.trait == 'fierce':
                        thoughts.extend([
                            'Is asking with the medicine cat what herbs may help them to be stronger in battle',
                            'Is showing off their battle moves',
                            'Is offering to lead the patrol today'
                        ])
                    elif cat.trait == 'insecure':
                        thoughts.extend([
                            'Almost died of embarrassment after a recent fumble on a patrol'
                        ])
                    elif cat.trait == 'loving':
                        # checks for specific roles
                        if other_cat.status == 'kitten':
                            thoughts.extend([
                                'Is helping out with kits around camp',
                                'Is smiling at the antics of the kits',
                                'Is offering words of comfort to the kits'
                            ])
                    elif cat.trait == 'nervous':
                        thoughts.extend([
                            'Was startled by a shrew while out on patrol!',
                            'Was startled by a fluttering bird while out on patrol!',
                            'Acted bravely on a recent patrol, despite their anxieties',
                        ])
                    elif cat.trait == 'playful':
                        # checks for specific roles
                        if other_cat.status == 'kitten':
                            thoughts.extend([
                                'Is giving kits badger rides on their back!',
                                'Is showing kits a game they used to play when they were that age',
                                'Is riling up the kits, much to the queens\' dismay'
                            ])
                    elif cat.trait == 'responsible':
                        thoughts.extend([
                            'Is repairing one of the camp walls',
                            'Is offering to lead the next patrol out'
                        ])
                    elif cat.trait == 'strict':
                        thoughts.extend([
                            'Can\'t stand to watch the younger cats make fools of themselves',
                            'Is conducting a rather rigorous training session for the younger warriors',
                            'Takes pride in how well-run their patrols always are',
                            'Is telling off younger cats for petty dishonesty out on patrol'
                        ])
                    elif cat.trait == 'thoughtful':
                        thoughts.extend([
                            'Brought back a much-needed herb to a grateful medicine cat after a hunting patrol'
                        ])
                    elif cat.trait == 'troublesome':
                        thoughts.extend([
                            'Is grumbling as they carry out a task for the medicine cat',
                            'Climbed up a tree and nearly fell out!'
                        ])

                # nonspecific age trait thoughts (unused traits: bold)
                if cat.trait == 'adventurous':
                    thoughts.extend([
                        'Wants to explore far beyond the borders of their territory...',
                        'Wonders what lays beyond the distant horizon...',
                        'Is dreaming of one day discovering something new and exciting!',
                        'Is itching to run, run, run!',
                        'Wants to climb the tallest tree in the territory!',
                        'Is itching for some excitement around camp',
                        'Is considering bending the rules a bit... just this once',
                        'Is showing off a trinket they found while exploring',
                        'Is daydreaming about how much there must be to see out in the world!'
                    ])
                elif cat.trait == 'altruistic':
                    thoughts.extend([
                        'Is laughing at a Clanmate\'s joke, even though they didn\'t find it too terribly funny',
                        'Helped to gather herbs all day'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend([
                            'Is taking fresh kill to the elders and queens',
                            'Gave their share of fresh kill to the elders',
                            'Is putting mousebile on the elder\'s ticks'
                        ])
                    elif other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is following the kits around camp, giving the queens a break',
                            'Let the kits sleep in their nest with them last night',
                            'Is grooming the scruffiest kits around camp dutifully'
                        ])
                elif cat.trait == 'ambitious':
                    thoughts.extend([
                        'Is being admired by many Clanmates for their recent feats',
                        'Is boasting loudly about having defeated an enemy warrior on patrol the other day',
                        'Seems to be ordering their fellow Clanmates around',
                        'Tries to put on a brave face for their Clanmates',
                        'Is feeling proud of themselves',
                        'Made sure to wake up early to volunteer for the dawn patrol',
                        'Has been catching the most prey on the latest hunting patrols',
                        'Is daydreaming about a Clan celebration in their honor someday'
                    ])
                elif cat.trait == 'bloodthirsty':
                    thoughts.extend([
                        'Is acting suspicious',
                        'Has been washing their paws a lot lately',
                        'Growls to themselves',
                        'Has disappeared often recently',
                        'Is thinking about murder',
                        'Tells the warriors to get ready for a battle',
                        'Yearns to fight',
                        'Daydreams about killing a certain cat',
                        'Wonders if they could kill a fox all by themselves',
                        'Started a fight with a fellow Clanmate'
                    ])
                elif cat.trait == 'calm':
                    thoughts.extend([
                        'Is taking a moment to appreciate some peace and quiet',
                        'Looks on as the camp buzzes around them',
                        'Is basking in the gentle sunlight around camp',
                        'Is meditating upon a sun-warmed rock',
                        'Is humming a soothing tune to themselves as they work',
                        'Is out on a peaceful stroll',
                        'Is remembering simpler days with fondness',
                        'Is offering gentle advice to a frustrated Clanmate',
                        'Is lining their nest with lavender',
                        'Smells sweet, like lavender',
                        'Never fails to offer comfort to their Clanmates',
                        'Is taking their sweet time eating their meal',
                        'Is purring quietly'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend(
                            ['Is politely listening to elders\'s stories'])
                elif cat.trait == 'careful':
                    thoughts.extend([
                        'Is double-checking their nest for burrs',
                        'Is getting a small scratch checked out by the medicine cat',
                        'Is slowly and methodically grooming themselves',
                        'Is chiding a younger cat for being so reckless',
                        'Is padding back and forth, across the camp'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend(
                            ['Is warning the kits to stay in camp'])
                elif cat.trait == 'charismatic':
                    thoughts.extend([
                        'Is smiling warmly at their Clanmates',
                        'Is making everyone laugh at a very funny quip',
                        'Always manages to turn the mood into a lighter one',
                        'Is laughing with friends',
                        'Is looking around camp for someone to share tongues with',
                        'Winked playfully at a Clanmate from across the clearing!',
                        'Has received several invitations to share tongues... and is deciding which to take',
                        'Is basking in a sunray in the camp clearing',
                        'Plans to go on a stroll with some cat today',
                        'Is swishing their tail back and forth in a laid back manner',
                        'Is grooming their already silky soft coat',
                        'Is purring warmly', 'Is purring loudly',
                        'Is purring sweetly', 'Is this moon\'s heartthrob',
                        'Has recently given a wonderful speech to fellow Clanmates, boosting morale'
                    ])
                elif cat.trait == 'childish':
                    thoughts.extend([
                        'Is chasing a butterfly around the camp',
                        'Is playing with their food',
                        'Is giggling about Clan drama with friends',
                        'Is crunching leaves with their paws',
                        'Is whining about Clan duties',
                        'Is distracted by a shiny Twoleg trinket they found',
                        'Is gnawing on a small bone busily',
                        'Is batting at a ball of moss',
                        'Is preoccupied playing an important game of hide and seek',
                        'Is laughing gleefully!'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is pouncing on unsuspecting kits',
                            'Is teaching new games to the kits'
                        ])
                elif cat.trait == 'cold':
                    thoughts.extend([
                        'Is hissing in frustration',
                        'Is grunting rudely at passersby',
                        'Wonders why others snap back at them',
                        'Notices that their Clanmates have been nervous around them lately',
                        'Is scolding the apprentices over something slight'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend(
                            ['Recently snapped at the kits, making them cry'])
                elif cat.trait == 'compassionate':
                    thoughts.extend([
                        'Spent time today with a grieving Clanmate',
                        'Is helping the medicine cat organize herb stores',
                        'Let their Clanmate have the last piece of fresh kill on the pile this morning',
                        'Is noticing with joy how well the Clan is looking after one another as of late',
                        'Is listening to a Clanmate\'s struggles with love'
                    ])
                    if cat.status != 'leader':
                        thoughts.extend([
                        'Is making sure that the leader has eaten before they dig in to their own meal',
                        'Is being scolded for giving their prey away to a starving loner'
                        ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend([
                            'Helped the elders to rise stiffly from their nests this morning'
                        ])
                elif cat.trait == 'confident':
                    thoughts.extend([
                        'Is building up a fellow Clanmate\'s confidence in battle!',
                        'Is puffing their chest out',
                        'Thinks that they are the smartest cat in the Clan',
                        'Thinks that they are the funniest cat around',
                        'Is strutting around confidently'
                    ])
                    if cat.status != 'deputy' and cat.status != 'leader':
                        thoughts.extend([
                            'Is letting the Clan leader know their opinion on a rather serious matter',
                            'Knows without a doubt that the Clan deputy respects them',
                            'Knows without a doubt that the Clan leader must respect them',
                            'Is sure to stand tall when the Clan leader walks by'
                        ])
                elif cat.trait == 'daring':
                    thoughts.extend([
                        'Is racing through camp, accidentally knocking into Clanmates',
                        'Suffered a bellyache after being dared to swallow a beetle',
                        'Is challenging any Clanmate they can to a sparring match... with minimal recruiting success',
                        'Is challenging some Clanmates to a sparring match, two-on-one!',
                        'Is twitching their tail in excitement about something'
                    ])
                elif cat.trait == 'empathetic':
                    thoughts.extend([
                        'Is listening to the woes of a fellow Clanmate',
                        'Notices an apprentice struggling with a task and offers their help',
                        'Is doing some apprentice tasks around camp, to help lighten the load',
                        'Is sharing tongues with friends',
                        'Is going to keep cats in the medicine den company',
                        'Is taking a breath, and ponders the burdens of others they have listened to'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend([
                            'Volunteered to gather fresh lining to the elders\' nests'
                        ])
                    elif other_cat.status == 'kitten':
                        thoughts.extend(
                            ['Is comforting kits after a scary experience'])
                elif cat.trait == 'faithful':
                    thoughts.extend([
                        'Is giving thanks to StarClan',
                        'Is assuring some worried Clanmates that StarClan will guide them',
                        'Is pondering their warrior ancestors, and the protections they grant the Clan',
                        'Would follow their Clanmates to the ends of the earth',
                        'Feels safe within the walls of the camp',
                        'Is promising to always serve StarClan',
                        'Is hoping that StarClan protects their loved ones...'
                    ])
                elif cat.trait == 'fierce':
                    thoughts.extend([
                        'Isn\'t scared of anything today!',
                        'Can\'t stop flexing their claws',
                        'Woke up with a flame in their belly this morning!',
                        'Is unusually tame today',
                        'Is looking forward to a challenge',
                        'Thinks that they could take on a badger solo',
                        'Thinks that they could take on a fox solo',
                        'Thinks that they could take on a dog solo',
                        'Hopes to earn more battle scars to show off',
                        'Is pushing hard for more battle training for the apprentices'
                    ])
                elif cat.trait == 'insecure':
                    thoughts.extend([
                        'Is wondering if they are good enough...',
                        'Is thinking about where they belong',
                        'Is hoping no cat saw them trip just now',
                        'Hopes that they will make it through leaf-bare',
                        'Took their own insecurities out on a friend the other day and feels awfully guilty...'
                    ])
                elif cat.trait == 'lonesome':
                    thoughts.extend([
                        'Is sitting alone',
                        'Looks on as others share tongues around the camp clearing',
                        'Is eating a piece of fresh kill in a corner of camp',
                        'Went out to hunt by themselves',
                        'Thinks that they are alone in their thoughts and beliefs...',
                        'Is looking longingly at other cats as they talk amongst themselves',
                        'Went on a long, moonlit stroll the other night',
                        'Is nowhere to be seen around camp',
                        'Wonders if any cat would miss them if they travelled far away',
                        'Is thinking wistfully about the past...',
                        'Is unsure of how to start up a conversation',
                        'Is fumbling with their words',
                        'Is enjoying some peace and quiet away from others',
                        'Is seeking out a place where they can be by themselves for a bit',
                        'Is feeling a bit anxious after having been around so many cats at the last Gathering'
                    ])
                elif cat.trait == 'loving':
                    thoughts.extend([
                        'Is feeling content with the little things in life',
                        'Is offering any help they can to the medicine cat',
                        'Is purring with friends', 'Is purring loudly',
                        'Is purring gently', 'Needs a bit of time alone today',
                        'Is talking with friends about recent celebrations'
                    ])
                elif cat.trait == 'loyal':
                    thoughts.extend([
                        'Is determined to protect their loved ones',
                        'Is making sure that everyone has eaten well',
                        'Is boasting about their loyalty to the Clan',
                        'Recently reported the nearby scent of rogues in the territory',
                        'Is determined to protect their loved ones, now moreso than ever',
                        'Is making sure that everyone has eaten well',
                        'Recently reported the nearby scent of rogues in the territory',
                        'Is boasting about their loyalty to the Clan'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is roaring playfully at kits, making them laugh',
                            'Has been rough housing with the kits a little to hard lately',
                            'Is telling the kits tales about valiant warriors in the thick of epic battles'
                        ])
                elif cat.trait == 'nervous':
                    thoughts.extend([
                        'Feels like there are ants pricking their pelt...',
                        'Is dreading the thought of failure...',
                        'Is nervously pacing around camp',
                        'Is nervously glancing around camp',
                        'Thinks that they are hearing things...',
                        'Keeps checking their nest for burrs',
                        'Is double checking that the camp walls are thoroughly reinforced... just in case',
                        'Is fumbling over their words',
                        'Is visibly stressed about something'
                    ])
                elif cat.trait == 'patient':
                    thoughts.extend([
                        'Is waiting until everyone else has taken from the fresh kill pile to eat',
                        'Is patiently standing guard outside of camp',
                        'Is winning a staring contest against a Clanmate',
                        'Is listening to a story they\'ve heard many, many times',
                        'Is listening to older cats gripe about their day',
                        'Is looking up, watching the clouds roll by',
                        'Is watching the breeze blow around the camp',
                        'Is listening to the grass sway',
                        'Is listening closely to the sounds of the forest',
                        'Is waiting to watch the sun rise',
                        'Is waiting to watch the sun set',
                        'Is grooming, grooming, grooming away...'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend(['Is letting a kit tug on their tail'])
                elif cat.trait == 'playful':
                    thoughts.extend([
                        'Is playing tag with cats around camp',
                        'Is tossing mossballs around',
                        'Pounced on a stray leaf with satisfaction',
                        'Seems to be playing with their food',
                        'Is play-fighting with friends',
                        'Is playing a games of counting stones',
                        'Is hoping to be on friendly terms with neighboring Clans someday',
                        'Has been joking around a bit too much recently',
                        'Is chasing a bug around the camp clearing',
                        'Has been distracting their fellow Clanmates lately',
                        'Is cracking jokes',
                        'Is chasing their own tail, making others laugh',
                        'Is happily chasing a butterfly',
                        'Is running after a colorful beetle',
                        'Is letting out mrrows of laughter'
                    ])
                elif cat.trait == 'responsible':
                    thoughts.extend([
                        'Is making sure they\'ve done all of their daily duties',
                        'Is planning to wake up early tomorrow',
                        'Was the first to rise this morning',
                        'Roused the other cats awake this morning',
                        'Isn\'t sure that they should be idling around at the moment',
                        'Is planning on going to sleep early tonight',
                        'Is making sure no work is being shirked!'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend(
                            ['Is going to fetch the elders new bedding today'])
                    elif other_cat.status == 'kitten':
                        thoughts.extend(['Is making sure the kits behave'])
                elif cat.trait == 'righteous':
                    thoughts.extend([
                        'Wants nothing more than to live by the Warrior Code',
                        'Is praying to StarClan for guidance...',
                        'Is reevaluating their morals',
                        'Hopes to help guide their Clanmates down the right path...',
                        'Always cheers the loudest of any cat at naming ceremonies'
                    ])
                elif cat.trait == 'shameless':
                    thoughts.extend([
                        'Is grooming intensely in clear view of everyone else in camp',
                        'Is snoring... at a ridiculous volume',
                        'Announced that they are heading to the dirtplace',
                        'Is eating, chewing very loudly',
                        'Was found to be faking a bellyache, earning a stern lecture',
                        'Stumbled into mud earlier and has yet to wash',
                        'Was found napping in another cat\'s nest!',
                        'Is fishing for compliments on their recently groomed fur'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend(
                            ['Pushed a kit out of their way thoughtlessly'])
                elif cat.trait == 'sneaky':
                    thoughts.extend([
                        'Is sniffing the edges of the camp wall suspiciously...',
                        'Smells like they may have rolled in catmint recently...',
                        'Is currently eavesdropping on two Clanmates, ears pricked',
                        'Is avoiding the conversation topic at paw',
                        'Is spreading rumors about Clanmates',
                        'Is whispering with a fellow Clanmate at the edges of camp',
                        'Recently spent the night outside of camp',
                        'Is licking their chops after an unknown tasty treat'
                    ])
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is teaching kits how to walk without making a sound'
                        ])
                elif cat.trait == 'strange':
                    thoughts.extend([
                        'Is telling every cat about their weird dreams',
                        'Is chasing a butterfly', 'Stares at random cats',
                        'Volunteered to guard the dirtplace...?',
                        'Is telling stories that only make sense to them',
                        'Doesn\'t feel understood by their Clanmates',
                        'Wandered off alone somewhere the other day',
                        'Is staring intently at something no other cat can see',
                        'Is staring intently at a wall',
                        'Has been distracted during recent Clan meetings',
                        'Recently wandered off during training, not returning until dusk',
                        'Is making odd noises', 'Is tearing up their food',
                        'Is gnawing on a stick', 'Collects the bones of prey',
                        'Is staring intently at a wall',
                        'Drawing symbols in the dirt with their claws',
                        'Paces back and forth', 'Is zoned out',
                        'Is telling every cat about their weird dreams'
                    ])
                elif cat.trait == 'strict':
                    thoughts.extend([
                        'Is lecturing any cat who will listen about the Warrior Code',
                        'Is lashing their tail furiously',
                        'Will not allow themselves to rest',
                        'Has been tough on themselves recently',
                        'Is surveying the camp scornfully from a higher vantage point',
                        'Is grooming themselves, making sure every whisker is in place',
                        'Is busy chastising Clanmates... but no cat is sure what for'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is grumbling about troublesome kits',
                            'Can\'t stand to watch the kits make fools of themselves'
                        ])
                elif cat.trait == 'thoughtful':
                    thoughts.extend([
                        'Offered to fetch more herbs for the medicine cat',
                        'Is offering helpful advice to a gloomy Clanmate'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder':
                        thoughts.extend([
                            'Gave an elder their favorite piece of fresh kill',
                            'Is making sure that the elders all have fresh bedding'
                        ])
                    elif other_cat.status == 'queen':
                        thoughts.extend([
                            'Is bringing soaked moss to the queens in the nursery'
                        ])
                    elif other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is promising to take the kits out on a stroll today if they behave',
                            'Plucked feathers from their meal for the kits to play with',
                            'Is hosting a mock training session for the kits',
                            'Is offering to look after the kits while the queens rest'
                        ])
                elif cat.trait == 'troublesome':
                    thoughts.extend([
                        'Won\'t stop pulling pranks', 'Is causing problems',
                        'Recently put a dead snake at the camp entrance to scare Clanmates',
                        'Is embarrassed after getting a taste of their own bitter herbs... Serves them right!',
                        'Can\'t seem to sit still!',
                        'Is surprisingly on task today',
                        'Is lightening the mood around camp with their shenanigans',
                        'Got distracted quite a bit today',
                        'Is bored, and looking for something to get into',
                        'Ate their fill and then some from the fresh kill pile',
                        'Is considering bending the rules just this once... again'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'elder' or other_cat.status == 'queen':
                        thoughts.extend([
                            'Recently was scolded for eating prey before the queens and elders'
                        ])
                    elif other_cat.status == 'kitten':
                        thoughts.extend([
                            'Got scolded for telling the kits a naughty joke!'
                        ])
                elif cat.trait == 'vengeful':
                    thoughts.extend([
                        'Seems to be plotting something',
                        'Is definitely plotting something',
                        'Is glaring daggers across the camp clearing',
                        'Swears that they will get their revenge... but for what?',                        
                        'Is angrily clawing up the ground, lost in deep thought',
                        'Is shredding the grass underpaw'
                    ])
                    if cat.status != 'leader':
                        thoughts.extend([
                            'Thinks that the Clan leader should declare war on a neighboring Clan'
                        ])
                elif cat.trait == 'wise':
                    thoughts.extend([
                        'Has a suggestion for the Clan leader that they wish to present',
                        'Is grooming themselves thoughtfully',
                        'Is telling stories to a very interested bunch of apprentices'
                    ])
                    # checks for specific roles
                    if other_cat.status == 'kitten':
                        thoughts.extend([
                            'Is teaching kits how to identify prey prints in the dirt',
                            'Is counseling the kits'
                        ])

                # skill specific thoughts
                elif cat.skills == 'strong connection to starclan' and cat.status != 'medicine cat' and cat.status != 'medicine cat apprentice':
                    thoughts.extend([
                        'Is becoming interested in herbs',
                        'Volunteers to gather herbs',
                        'Has been lending the medicine cat a paw lately'
                    ])

            else:
                # if this else is reached dead is not set, just to be sure the cat should be alive
                self.dead = False

            thought = choice(thoughts)
            cat.thought = thought

            # on_patrol = ['Is having a good time out on patrol', 'Wants to return to camp to see ' + other_name,  #              'Is currently out on patrol',
            # 'Is getting rained on during their patrol',  #              'Is out hunting'] //will add later  # interact_with_loner = ['Wants to know where ' + other_name + '  #
            # came from.'] // will add

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

    def status_change(self, new_status):
        # revealing of traits and skills
        if self.status == 'kitten':
            self.trait = choice(self.traits)
        if (self.status == 'apprentice'
                and new_status != 'medicine cat apprentice') or (
                    self.status == 'medicine cat apprentice'
                    and new_status != 'apprentice'):
            self.skill = choice(self.skills)
        elif new_status == 'medicine cat':
            self.skill = choice(self.med_skills)
        self.status = new_status
        self.name.status = new_status
        if 'apprentice' in new_status:
            self.update_mentor()
        # update class dictionary
        self.all_cats[self.ID] = self

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

    def update_sprite(self):
        # First make pelt, if it wasn't possible before

        if self.pelt is None:
            if self.parent1 is None:
                # If pelt has not been picked manually, this function chooses one based on possible inheritances
                self.pelt = choose_pelt(self.gender)

            elif self.parent2 is None and self.parent1 in self.all_cats.keys():
                # 1 in 3 chance to inherit a single parent's pelt
                par1 = self.all_cats[self.parent1]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, None]), choice([par1.pelt.white, None]), choice([par1.pelt.name, None]),
                                        choice([par1.pelt.length, None]))

            elif self.parent1 in self.all_cats.keys() and self.parent2 in self.all_cats.keys():
                # 2 in 3 chance to inherit either parent's pelt
                par1 = self.all_cats[self.parent1]
                par2 = self.all_cats[self.parent2]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, par2.pelt.colour, None]), choice([par1.pelt.white, par2.pelt.white, None]),
                                        choice([par1.pelt.name, par2.pelt.name, None]), choice([par1.pelt.length, par2.pelt.length, None]))
            else:
                self.pelt = choose_pelt(self.gender)

        # THE SPRITE UPDATE
        # draw colour & style
        new_sprite = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
        game.switches['error_message'] = 'There was an error loading a cat\'s base coat sprite. Last cat read was ' + str(self)
        if self.pelt.name not in ['Tortie', 'Calico']:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice', 'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(sprites.sprites[self.pelt.sprites[1] + 'extra' + self.pelt.colour + str(self.age_sprites[self.age])], (0, 0))
            else:
                new_sprite.blit(sprites.sprites[self.pelt.sprites[1] + self.pelt.colour + str(self.age_sprites[self.age])], (0, 0))
        else:
            game.switches['error_message'] = 'There was an error loading a tortie\'s base coat sprite. Last cat read was ' + str(self)
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice', 'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(sprites.sprites[self.tortiebase + 'extra' + self.tortiecolour + str(self.age_sprites[self.age])], (0, 0))
                game.switches['error_message'] = 'There was an error loading a tortie\'s pattern sprite. Last cat read was ' + str(self)
                new_sprite.blit(sprites.sprites[self.tortiepattern + 'extra' + self.pattern + str(self.age_sprites[self.age])], (0, 0))
            else:
                new_sprite.blit(sprites.sprites[self.tortiebase + self.tortiecolour + str(self.age_sprites[self.age])], (0, 0))
                game.switches['error_message'] = 'There was an error loading a tortie\'s pattern sprite. Last cat read was ' + str(self)
                new_sprite.blit(sprites.sprites[self.tortiepattern + self.pattern + str(self.age_sprites[self.age])], (0, 0))
        game.switches['error_message'] = 'There was an error loading a cat\'s white patches sprite. Last cat read was ' + str(self)
        # draw white patches
        if self.white_patches is not None:
            if self.pelt.length == 'long' and self.status not in [
                    'kitten', 'apprentice', 'medicine cat apprentice'
            ] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['whiteextra' + self.white_patches +
                                    str(self.age_sprites[self.age])], (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['white' + self.white_patches +
                                    str(self.age_sprites[self.age])], (0, 0))
        game.switches[
            'error_message'] = 'There was an error loading a cat\'s scar and eye sprites. Last cat read was ' + str(
                self)
        # draw eyes & scars1
        if self.pelt.length == 'long' and self.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
        ] or self.age == 'elder':
            if self.specialty in scars1:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars1:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars4:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars4:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars5:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars5:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            new_sprite.blit(
                sprites.sprites['eyesextra' + self.eye_colour +
                                str(self.age_sprites[self.age])], (0, 0))
        else:
            if self.specialty in scars1:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars1:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars4:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars4:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars5:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars5:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            new_sprite.blit(
                sprites.sprites['eyes' + self.eye_colour +
                                str(self.age_sprites[self.age])], (0, 0))
        game.switches[
            'error_message'] = 'There was an error loading a cat\'s shader sprites. Last cat read was ' + str(
                self)
        # draw line art
        if game.settings['shaders'] and not self.dead:
            if self.pelt.length == 'long' and self.status not in [
                    'kitten', 'apprentice', 'medicine cat apprentice'
            ] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['shaders' +
                                    str(self.age_sprites[self.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['shaders' +
                                    str(self.age_sprites[self.age])], (0, 0))
        elif not self.dead:
            if self.pelt.length == 'long' and self.status not in [
                    'kitten', 'apprentice', 'medicine cat apprentice'
            ] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['lines' +
                                    str(self.age_sprites[self.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['lines' + str(self.age_sprites[self.age])],
                    (0, 0))
        elif self.dead:
            if self.pelt.length == 'long' and self.status not in [
                    'kitten', 'apprentice', 'medicine cat apprentice'
            ] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['lineartdead' +
                                    str(self.age_sprites[self.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['lineartdead' +
                                    str(self.age_sprites[self.age])], (0, 0))

        game.switches[
            'error_message'] = 'There was an error loading a cat\'s skin and second set of scar sprites. Last cat read was ' + str(
                self)
        # draw skin and scars2 and scars3
        blendmode = pygame.BLEND_RGBA_MIN
        if self.pelt.length == 'long' and self.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
        ] or self.age == 'elder':
            new_sprite.blit(
                sprites.sprites['skinextra' + self.skin +
                                str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars2:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0),
                    special_flags=blendmode)
            if self.specialty2 in scars2:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0),
                    special_flags=blendmode)
            if self.specialty in scars3:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars3:
                new_sprite.blit(
                    sprites.sprites['scarsextra' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
        else:
            new_sprite.blit(
                sprites.sprites['skin' + self.skin +
                                str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars2:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0),
                    special_flags=blendmode)
            if self.specialty2 in scars2:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0),
                    special_flags=blendmode)
            if self.specialty in scars3:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty +
                                    str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars3:
                new_sprite.blit(
                    sprites.sprites['scars' + self.specialty2 +
                                    str(self.age_sprites[self.age])], (0, 0))
            
        game.switches[
        'error_message'] = 'There was an error loading a cat\'s accessory. Last cat read was ' + str(
            self)                            
        # draw accessories        
        if self.pelt.length == 'long' and self.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
        ] or self.age == 'elder':
            if self.accessory in plant_accessories:
                new_sprite.blit(
                    sprites.sprites['acc_herbsextra' + self.accessory +
                                    str(self.age_sprites[self.age])], (0, 0))
            elif self.accessory in wild_accessories:
                new_sprite.blit(
                    sprites.sprites['acc_wildextra' + self.accessory +
                                    str(self.age_sprites[self.age])], (0, 0))
        else:
            if self.accessory in plant_accessories:
                new_sprite.blit(
                    sprites.sprites['acc_herbs' + self.accessory +
                                    str(self.age_sprites[self.age])], (0, 0))
            elif self.accessory in wild_accessories:
                new_sprite.blit(
                    sprites.sprites['acc_wild' + self.accessory +
                                    str(self.age_sprites[self.age])], (0, 0))
        game.switches[
            'error_message'] = 'There was an error loading a cat\'s skin and second set of scar sprites. Last cat read was ' + str(
                self)
        game.switches[
            'error_message'] = 'There was an error reversing a cat\'s sprite. Last cat read was ' + str(
                self)
                
        # reverse, if assigned so
        if self.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)
        game.switches[
            'error_message'] = 'There was an error scaling a cat\'s sprites. Last cat read was ' + str(
                self)
        # apply
        self.sprite = new_sprite
        self.big_sprite = pygame.transform.scale(
            new_sprite, (sprites.new_size, sprites.new_size))
        self.large_sprite = pygame.transform.scale(
            self.big_sprite, (sprites.size * 3, sprites.size * 3))
        game.switches[
            'error_message'] = 'There was an error updating a cat\'s sprites. Last cat read was ' + str(
                self)
        # update class dictionary
        self.all_cats[self.ID] = self
        game.switches['error_message'] = ''

    def draw(self, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - sprites.size / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - sprites.size
        self.used_screen.blit(self.sprite, new_pos)

    def draw_big(self, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - sprites.new_size / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - sprites.new_size
        self.used_screen.blit(self.big_sprite, new_pos)

    def draw_large(self, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - sprites.size * 3 / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - sprites.size * 3
        self.used_screen.blit(self.large_sprite, new_pos)

    def json_save_cats(self):
        """Save the cat data."""
        clanname = ''        
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]
        elif game.clan != None:
            clanname = game.clan.name

        directory = 'saves/' + clanname
        if not os.path.exists(directory):
            os.makedirs(directory)

        clan_cats = []
        for inter_cat in self.all_cats.values():
            cat_data = {
                "ID": inter_cat.ID,
                "name_prefix": inter_cat.name.prefix,
                "name_suffix": inter_cat.name.suffix,
                "gender": inter_cat.gender,
                "gender_align": inter_cat.genderalign,
                "status": inter_cat.status,
                "age": inter_cat.age,
                "moons": inter_cat.moons,
                "trait": inter_cat.trait,
                "parent1": inter_cat.parent1,
                "parent2": inter_cat.parent2,
                "mentor": inter_cat.mentor.ID if inter_cat.mentor else None,
                "paralyzed": inter_cat.paralyzed,
                "no_kits": inter_cat.no_kits,
                "exiled": inter_cat.exiled,
                "pelt_name": inter_cat.pelt.name,
                "pelt_color": inter_cat.pelt.colour,
                "pelt_white": inter_cat.pelt.white,
                "pelt_length": inter_cat.pelt.length,
                "spirit_kitten": inter_cat.age_sprites['kitten'],
                "spirit_adolescent": inter_cat.age_sprites['adolescent'],
                "spirit_young_adult": inter_cat.age_sprites['young adult'],
                "spirit_adult": inter_cat.age_sprites['adult'],
                "spirit_senior_adult": inter_cat.age_sprites['senior adult'],
                "spirit_elder": inter_cat.age_sprites['elder'],
                "eye_colour": inter_cat.eye_colour,
                "reverse": inter_cat.reverse,
                "white_patches": inter_cat.white_patches,
                "pattern": inter_cat.pattern,
                "tortie_base": inter_cat.tortiebase,
                "tortie_color": inter_cat.tortiecolour,
                "tortie_pattern": inter_cat.tortiepattern,
                "skin": inter_cat.skin,
                "skill": inter_cat.skill,
                "specialty": inter_cat.specialty,
                "specialty2": inter_cat.specialty2,
                "accessory": inter_cat.accessory,
                "mate": inter_cat.mate,
                "dead": inter_cat.dead,
                "spirit_dead": inter_cat.age_sprites['dead'],
                "experience": inter_cat.experience,
                "dead_moons": inter_cat.dead_for,
                "current_apprentice": [appr.ID for appr in inter_cat.apprentice],
                "former_apprentices" :[appr.ID for appr in inter_cat.former_apprentices]
            }
            clan_cats.append(cat_data)
            inter_cat.save_relationship_of_cat()

        try:
            with open('saves/' + clanname + '/clan_cats.json', 'w') as write_file:
                json_string = ujson.dumps(clan_cats, indent = 4)
                write_file.write(json_string)
        except:
            print("Saving cats didn't work.")

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

    def load_cats(self):
        directory = 'saves/' + game.switches['clan_list'][0] + '/clan_cats.json'
        if os.path.exists(directory):
            self.json_load()
        else:
            self.csv_load()

    def csv_load(self):
        if game.switches['clan_list'][0].strip() == '':
            cat_data = ''
        else:
            if os.path.exists('saves/' + game.switches['clan_list'][0] +
                              'cats.csv'):
                with open(
                        'saves/' + game.switches['clan_list'][0] + 'cats.csv',
                        'r') as read_file:
                    cat_data = read_file.read()
            else:
                with open(
                        'saves/' + game.switches['clan_list'][0] + 'cats.txt',
                        'r') as read_file:
                    cat_data = read_file.read()

        if len(cat_data) > 0:
            cat_data = cat_data.replace('\t', ',')
            for i in cat_data.split('\n'):
                # CAT: ID(0) - prefix:suffix(1) - gender(2) - status(3) - age(4) - trait(5) - parent1(6) - parent2(7) - mentor(8)
                # PELT: pelt(9) - colour(10) - white(11) - length(12)
                # SPRITE: kitten(13) - apprentice(14) - warrior(15) - elder(16) - eye colour(17) - reverse(18)
                # - white patches(19) - pattern(20) - tortiebase(21) - tortiepattern(22) - tortiecolour(23) - skin(24) - skill(25) - NONE(26) - spec(27) - accessory(28) -
                # spec2(29) - moons(30) - mate(31)
                # dead(32) - SPRITE:dead(33) - exp(34) - dead for _ moons(35) - current apprentice(36) 
                # (BOOLS, either TRUE OR FALSE) paralyzed(37) - no kits(38) - exiled(39)
                # genderalign(40) - former apprentices list (41)[FORMER APPS SHOULD ALWAYS BE MOVED TO THE END]
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

                    game.switches['error_message'] = '1There was an error loading cat # ' + str(attr[0])

                    the_pelt = choose_pelt(attr[2], attr[10], attr[11], attr[9], attr[12], True)
                    game.switches['error_message'] = '2There was an error loading cat # ' + str(attr[0])
                    the_cat = Cat(ID=attr[0], prefix=attr[1].split(':')[0], suffix=attr[1].split(':')[1], gender=attr[2], status=attr[3], pelt=the_pelt, parent1=attr[6],
                                  parent2=attr[7], eye_colour=attr[17])
                    game.switches['error_message'] = '3There was an error loading cat # ' + str(attr[0])
                    the_cat.age, the_cat.mentor = attr[4], attr[8]
                    game.switches['error_message'] = '4There was an error loading cat # ' + str(attr[0])
                    the_cat.age_sprites['kitten'], the_cat.age_sprites['adolescent'] = int(attr[13]), int(attr[14])
                    game.switches['error_message'] = '5There was an error loading cat # ' + str(attr[0])
                    the_cat.age_sprites['adult'], the_cat.age_sprites['elder'] = int(attr[15]), int(attr[16])
                    game.switches['error_message'] = '6There was an error loading cat # ' + str(attr[0])
                    the_cat.age_sprites['young adult'], the_cat.age_sprites['senior adult'] = int(attr[15]), int(attr[15])
                    game.switches['error_message'] = '7There was an error loading cat # ' + str(attr[0])
                    the_cat.reverse, the_cat.white_patches, the_cat.pattern = attr[18], attr[19], attr[20]
                    game.switches['error_message'] = '8There was an error loading cat # ' + str(attr[0])
                    the_cat.tortiebase, the_cat.tortiepattern, the_cat.tortiecolour = attr[21], attr[22], attr[23]
                    game.switches['error_message'] = '9There was an error loading cat # ' + str(attr[0])
                    the_cat.trait, the_cat.skin, the_cat.specialty = attr[5], attr[24], attr[27]
                    game.switches['error_message'] = '10There was an error loading cat # ' + str(attr[0])
                    the_cat.skill = attr[25]
                    if len(attr) > 28:
                        the_cat.accessory = attr[28]

                    if len(attr) > 29:
                        the_cat.specialty2 = attr[29]
                    else:
                        the_cat.specialty2 = None
                    game.switches['error_message'] = '11There was an error loading cat # ' + str(attr[0])
                    if len(attr) > 34:
                        the_cat.experience = int(attr[34])
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        the_cat.experience_level = experiencelevels[math.floor(int(the_cat.experience) / 10)]
                    else:
                        the_cat.experience = 0
                    game.switches['error_message'] = '12There was an error loading cat # ' + str(attr[0])
                    if len(attr) > 30:
                        # Attributes that are to be added after the update
                        the_cat.moons = int(attr[30])
                        if len(attr) >= 31:
                            # assigning mate to cat, if any
                            the_cat.mate = attr[31]
                        if len(attr) >= 32:
                            # Is the cat dead
                            the_cat.dead = attr[32]
                            the_cat.age_sprites['dead'] = attr[33]
                    game.switches['error_message'] = '13There was an error loading cat # ' + str(attr[0])
                    if len(attr) > 35:
                        the_cat.dead_for = int(attr[35])
                    game.switches['error_message'] = '14There was an error loading cat # ' + str(attr[0])
                    if len(attr) > 36 and attr[36] is not None:
                        the_cat.apprentice = attr[36].split(';')
                    game.switches['error_message'] = '15There was an error loading cat # ' + str(attr[0])
                    if len(attr) > 37:
                        the_cat.paralyzed = bool(attr[37])
                    if len(attr) > 38:
                        the_cat.no_kits = bool(attr[38])
                    if len(attr) > 39:
                        the_cat.exiled = bool(attr[39])
                    if len(attr) > 40:
                        the_cat.genderalign = attr[40]
                    if len(attr) > 41 and attr[41] is not None:                 #KEEP THIS AT THE END
                        the_cat.former_apprentices = attr[41].split(';')

            game.switches[
                'error_message'] = 'There was an error loading this clan\'s mentors, apprentices, relationships, or sprite info.'

            for inter_cat in self.all_cats.values():
                # Load the mentors and apprentices after all cats have been loaded
                game.switches[
                    'error_message'] = 'There was an error loading this clan\'s mentors/apprentices. Last cat read was ' + str(
                        inter_cat)
                inter_cat.mentor = cat_class.all_cats.get(inter_cat.mentor)
                apps = []
                former_apps = []
                for app_id in inter_cat.apprentice:
                    app = cat_class.all_cats.get(app_id)
                    # Make sure if cat isn't an apprentice, they're a former apprentice
                    if 'apprentice' in app.status:
                        apps.append(app)
                    else:
                        former_apps.append(app)
                for f_app_id in inter_cat.former_apprentices:
                    f_app = cat_class.all_cats.get(f_app_id)
                    former_apps.append(f_app)
                inter_cat.apprentice = apps
                inter_cat.former_apprentices = former_apps
                game.switches[
                    'error_message'] = 'There was an error loading this clan\'s relationships. Last cat read was ' + str(inter_cat)
                inter_cat.load_relationship_of_cat()
                game.switches[
                    'error_message'] = 'There was an error loading a cat\'s sprite info. Last cat read was ' + str(inter_cat)
                inter_cat.update_sprite()

            # generate the relationship if some is missing
            game.switches['error_message'] = 'There was an error when relationships where created.'
            for id in self.all_cats.keys():
                the_cat = self.all_cats.get(id)
                game.switches['error_message'] = f'There was an error when relationships for cat #{the_cat} are created.'
                if the_cat.relationships != None and len(the_cat.relationships) < 1:
                    the_cat.create_new_relationships()

            game.switches['error_message'] = ''

    def json_load(self):
        all_cats = []
        cat_data = None
        clanname = game.switches['clan_list'][0]
        try:
            with open('saves/' + clanname + '/clan_cats.json', 'r') as read_file:
                cat_data = ujson.loads(read_file.read())
        except:
            game.switches['error_message'] = 'There was an error loading the json cats file!'
            return
        # create new cat objects
        for cat in cat_data:
            new_pelt = choose_pelt(cat["gender"], cat["pelt_color"], cat["pelt_white"], cat["pelt_name"], cat["pelt_length"], True)
            
            new_cat = Cat(ID=cat["ID"], prefix=cat["name_prefix"], suffix=cat["name_suffix"], gender=cat["gender"],
                            status=cat["status"], parent1=cat["parent1"], parent2=cat["parent2"], moons=cat["moons"],
                            eye_colour=cat["eye_colour"], pelt=new_pelt)
            new_cat.age = cat["age"]
            new_cat.genderalign = cat["gender_align"]
            new_cat.moons = cat["moons"]
            new_cat.trait = cat["trait"]
            new_cat.mentor = cat["mentor"]
            new_cat.paralyzed = cat["paralyzed"]
            new_cat.no_kits = cat["no_kits"]
            new_cat.exiled = cat["exiled"]
            new_cat.age_sprites['kitten'] = cat["spirit_kitten"]
            new_cat.age_sprites['adolescent'] = cat["spirit_adolescent"]
            new_cat.age_sprites['young adult'] = cat["spirit_young_adult"]
            new_cat.age_sprites['adult'] = cat["spirit_adult"]
            new_cat.age_sprites['senior adult'] = cat["spirit_senior_adult"]
            new_cat.age_sprites['elder'] = cat["spirit_elder"]
            new_cat.eye_colour = cat["eye_colour"]
            new_cat.reverse = cat["reverse"]
            new_cat.white_patches = cat["white_patches"]
            new_cat.pattern = cat["pattern"]
            new_cat.tortiebase = cat["tortie_base"]
            new_cat.tortiecolour = cat["tortie_color"]
            new_cat.tortiepattern = cat["tortie_pattern"]
            new_cat.skin = cat["skin"]
            new_cat.skill = cat["skill"]
            new_cat.specialty = cat["specialty"]
            new_cat.specialty2 = cat["specialty2"]
            new_cat.accessory = cat["accessory"]
            new_cat.mate = cat["mate"]
            new_cat.dead = cat["dead"]
            new_cat.age_sprites['dead'] = cat["spirit_dead"]
            new_cat.experience = cat["experience"]
            new_cat.dead_for = cat["dead_moons"]
            new_cat.apprentice = cat["current_apprentice"]
            new_cat.former_apprentices = cat["former_apprentices"]

            all_cats.append(new_cat)

            
        # replace cat ids with cat objects (only needed by mentor)
        for cat in all_cats:
            # load the relationships
            cat.load_relationship_of_cat()

            mentor_relevant = list(filter(lambda inter_cat: inter_cat.ID == cat.mentor, all_cats))
            cat.mentor = None
            if len(mentor_relevant) == 1:
                cat.mentor = mentor_relevant[0]
            
            # Update the apprentice
            if len(cat.apprentice) > 0:
                new_apprentices = []
                for cat_id in cat.apprentice:
                    relevant_list = list(filter(lambda cat: cat.ID == cat_id, all_cats))
                    if len(relevant_list) > 0:
                        # if the cat can't be found, drop the cat_id
                        new_apprentices.append(relevant_list[0])
                cat.apprentice = new_apprentices

            # Update the apprentice
            if len(cat.former_apprentices) > 0:
                new_apprentices = []
                for cat_id in cat.former_apprentices:
                    relevant_list = list(filter(lambda cat: cat.ID == cat_id, all_cats))
                    if len(relevant_list) > 0:
                        # if the cat can't be found, drop the cat_id
                        new_apprentices.append(relevant_list[0])
                cat.former_apprentices = new_apprentices

    def load_relationship_of_cat(self):
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        else:
            clanname = game.switches['clan_list'][0]

        relation_directory = 'saves/' + clanname + '/relationships/'
        relation_cat_directory = relation_directory + self.ID + '_relations.json'

        self.relationships = []
        if os.path.exists(relation_directory and relation_cat_directory):
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
        else:
            self.create_new_relationships()

    def load(self, cat_dict):
        """ A function that takes a dictionary containing other dictionaries with attributes and values of all(?)
         cats from a save file and redistributes the values onto new cat object attributes.
         The dict is in form:
         cat_dict = { ID : [(prefix, suffix), {attribute: value}] }"""
        for cat in cat_dict.keys():  # cat is the ID of the cats
            # create the cat object
            name = cat_dict[cat][0]
            new_cat = Cat(prefix=name[0], suffix=name[1], ID=cat)

            # put attribute dict into easier accessible variable
            attr_dict = cat_dict[cat][1]

            # go through attributes
            for attr in attr_dict.keys():
                value = attr_dict[attr]  # value of attribute
                # turn value into other forms than string if necessary
                if value == 'None':
                    value = None
                elif value == 'False':
                    value = False
                elif value == 'True':
                    value = True

                # Assign values to cat object
                if attr == 'status':
                    new_cat.status = value  # STATUS
                if attr == 'parent1':
                    new_cat.parent1 = value  # PARENT1
                if attr == 'parent2':
                    new_cat.parent2 = value  # PARENT2
                if attr == 'sex':
                    new_cat.gender = value  # SEX / GENDER
                if attr == 'moons':
                    new_cat.moons = int(value)  # MOONS
                if attr == 'age':
                    new_cat.age = int(value)  # AGE
                if attr == 'dead':
                    new_cat.dead = value  # DEAD ( OR NOT )
                if attr == 'dead_for':
                    new_cat.dead_for = int(value)  # DEAD FOR ( MOONS )
                if attr == 'pelt':
                    new_cat.pelt = value  # PELT
                if attr == 'eye_colour':
                    new_cat.eye_colour = value  # EYES
                if attr == 'tortiebase':
                    new_cat.tortiebase = value
                if attr == 'tortiepattern':
                    new_cat.tortiepattern = value
                if attr == 'mate':
                    new_cat.mate = value  # MATE
                if attr == 'trait':
                    new_cat.trait = value  # TRAIT
                if attr == 'skill':
                    new_cat.skill = value  # SKILL
                if attr == 'mentor':
                    new_cat.mentor = value

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
        if self.white_patches in [little_white, mid_white]:
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
            if color_name == 'darkginger point' or color_name == 'ginger point':
                color_name = 'flame point'
        # vitiligo
        elif self.white_patches in [vit]:
            color_name = color_name + ' with vitiligo'

        if color_name == 'tortie':
            color_name = 'tortoiseshell'

        if self.white_patches == 'FULLWHITE':
            color_name = 'white'

        if color_name == 'white and white':
            color_name = 'white'

        return color_name

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
            cat_relationship[0].cut_boundries()
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
                relation.cut_boundries()
        else:
            mate = self.all_cats.get(self.mate)
            self.relationships.append(Relationship(self, mate))

        self.mate = None

    def is_potential_mate(self, other_cat, for_love_interest = False):
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
        if is_former_mentor and not game.settings['romantic with former mentor']:
            return False

        # check for relation
        direct_related = self.is_sibling(other_cat) or self.is_parent(other_cat) or other_cat.is_parent(self)
        indirect_related = self.is_uncle_aunt(other_cat) or other_cat.is_uncle_aunt(self)
        if direct_related or indirect_related:
            return False
        
        # check for age
        if self.moons < 14 or other_cat.moons < 14:
            return False

        if self.age == other_cat.age:
            return True

        invalid_status_mate = ['kitten', 'apprentice', 'medicine cat apprentice']
        not_invalid_status = self.status not in invalid_status_mate and other_cat.status not in invalid_status_mate
        if not_invalid_status and abs(self.moons - other_cat.moons) <= 40:
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
        siblings = []
        for inter_cat in self.all_cats.values():
            if self.is_sibling(inter_cat):
                siblings.append(inter_cat.ID)
        return siblings


# Twelve example cats
def create_example_cats():
    e = random.sample(range(12), 3)
    for a in range(12):
        if a in e:
            game.choose_cats[a] = Cat(status='warrior')
        else:
            game.choose_cats[a] = Cat(status=choice(
                ['kitten', 'apprentice', 'warrior', 'warrior', 'elder']))
        game.choose_cats[a].update_sprite()


# CAT CLASS ITEMS
cat_class = Cat(example=True)
game.cat_class = cat_class
