from __future__ import annotations
from random import choice, randint, sample
from typing import Dict, List, Any
import random
import os.path
import itertools

from ..events_module.generate_events import GenerateEvents
try:
    import ujson
except ImportError:
    import json as ujson

from .pelts import describe_color
from .names import Name
from .thoughts import get_thoughts
from .appearance_utility import (
    init_pelt,
    init_tint,
    init_sprite,
    init_scars,
    init_accessories,
    init_white_patches,
    init_eyes,
    init_pattern,
    )
from scripts.conditions import Illness, Injury, PermanentCondition, get_amount_cat_for_one_medic, \
    medical_cats_condition_fulfilled
import bisect
import pygame

from scripts.utility import get_med_cats, get_personality_compatibility, event_text_adjust, update_sprite
from scripts.game_structure.game_essentials import game, screen
from scripts.cat.thoughts import get_thoughts
from scripts.cat_relations.relationship import Relationship
from scripts.game_structure import image_cache
from scripts.event_class import Single_Event


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

    # This in is in reverse order: top of the list at the bottom
    rank_sort_order = [
        "kitten",
        "elder",
        "apprentice",
        "warrior",
        "mediator apprentice",
        "mediator",
        "medicine cat apprentice",
        "medicine cat",
        "deputy",
        "leader"
    ]

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
        'smart tactician', 'valuable tactician', 'valuable insight',
        'good mediator', 'great mediator', 'excellent mediator',
        'good teacher', 'great teacher', 'fantastic teacher',
        'strong connection to StarClan', 'smart', 'very smart', 'extremely smart',
        'good kitsitter', 'great kitsitter', 'excellent kitsitter', 'camp keeper', 'den builder',
    ]

    skill_groups = {
        'special': ['omen sight', 'dream walker', 'clairvoyant', 'prophet', 'lore keeper', 'keen eye'],
        'star': ['strong connection to StarClan'],
        'heal': ['good healer', 'great healer', 'fantastic healer'],
        'teach': ['good teacher', 'great teacher', 'fantastic teacher'],
        'mediate': ['good mediator', 'great mediator', 'excellent mediator'],
        'smart': ['smart', 'very smart', 'extremely smart'],
        'hunt': ['good hunter', 'great hunter', 'fantastic hunter'],
        'fight': ['good fighter', 'great fighter', 'excellent fighter'],
        'speak': ['good speaker', 'great speaker', 'excellent speaker'],
        'story': ['good storyteller', 'great storyteller', 'fantastic storyteller'],
        'tactician': ['smart tactician', 'valuable tactician', 'valuable insight'],
        'home': ['good kitsitter', 'great kitsitter', 'excellent kitsitter', 'camp keeper', 'den builder']
    }

    backstories = [
        'clanborn', 'halfclan1', 'halfclan2', 'outsider_roots1', 'outsider_roots2',
        'loner1', 'loner2', 'kittypet1', 'kittypet2', 'rogue1', 'rogue2', 'abandoned1',
        'abandoned2', 'abandoned3', 'medicine_cat', 'otherclan', 'otherclan2', 'ostracized_warrior', 'disgraced',
        'retired_leader', 'refugee', 'tragedy_survivor', 'clan_founder', 'orphaned', "orphaned2", "guided1", "guided2",
        "guided3", "guided4"
    ]
    all_cats: Dict[str, Cat] = {}  # ID: object
    outside_cats: Dict[str, Cat] = {}  # cats outside the clan
    id_iter = itertools.count()

    all_cats_list: List[Cat] = []

    grief_strings = {}

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
                 example=False,
                 faded=False,
                 # Set this to True if you are loading a faded cat. This will prevent the cat from being added to the list
                 loading_cat=False  # Set to true if you are loading a cat at start-up.
                 ):

        # This must be at the top. It's a smaller list of things to init, which is only for faded cats
        if faded:
            self.ID = ID
            self.name = Name(status, prefix=prefix, suffix=suffix)
            self.parent1 = None
            self.parent2 = None
            self.status = status
            self.moons = moons
            if moons > 300:
                # Out of range, always elder
                self.age = 'elder'
            else:
                # In range
                for key_age in self.age_moons.keys():
                    if moons in range(self.age_moons[key_age][0], self.age_moons[key_age][1] + 1):
                        self.age = key_age

            self.set_faded()  # Sets the faded sprite and faded tag (self.faded = True)

            return

        self.generate_events = GenerateEvents()

        # Private attributes
        self._mentor = None  # plz
        self._experience = None
        self._moons = None

        # Public attributes
        self.gender = gender
        self.status = status
        self.backstory = backstory
        self.age = None
        self.skill = None
        self.trait = None
        self.parent1 = parent1
        self.parent2 = parent2
        self.pelt = pelt
        self.tint = None
        self.eye_colour = eye_colour
        self.eye_colour2 = None
        self.scars = []
        self.former_mentor = []
        self.patrol_with_mentor = 0
        self.mentor_influence = []
        self.apprentice = []
        self.former_apprentices = []
        self.relationships = {}
        self.mate = None
        self.placement = None
        self.example = example
        self.dead = False
        self.exiled = False
        self.outside = False
        self.died_by = []  # once the cat dies, tell the cause
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
        self.illnesses = {}
        self.injuries = {}
        self.healed_condition = None
        self.leader_death_heal = None
        self.also_got = False
        self.permanent_condition = {}
        self.retired = False
        self.possible_scar = None
        self.possible_death = None
        self.scar_event = []
        self.death_event = []
        self.df = False
        self.experience_level = None
        self.corruption = 0
        self.life_givers = []
        self.known_life_givers = []
        self.virtues = []
        self.no_kits = False
        self.paralyzed = False
        self.age_sprites = {
            "kitten": None,
            "adolescent": None,
            "young adult": None,
            "adult": None,
            "senior adult": None,
            "elder": None
        }

        self.opacity = 100
        self.prevent_fading = False  # Prevents a cat from fading.
        self.faded_offspring = []  # Stores of a list of faded offspring, for family page purposes.

        self.faded = faded  # This is only used to flag cat that are faded, but won't be added to the faded list until
        # the next save.

        # setting ID
        if ID is None:
            potential_id = str(next(Cat.id_iter))

            if game.clan:
                faded_cats = game.clan.faded_ids
            else:
                faded_cats = []

            while potential_id in self.all_cats or potential_id in faded_cats:
                potential_id = str(next(Cat.id_iter))
            self.ID = potential_id
        else:
            self.ID = ID

        # age and status
        if status is None and moons is None:
            self.age = choice(self.ages)
        elif moons is not None:
            self.moons = moons
            if moons > 300:
                # Out of range, always elder
                self.age = 'elder'
            else:
                # In range
                for key_age in self.age_moons.keys():
                    if moons in range(self.age_moons[key_age][0], self.age_moons[key_age][1] + 1):
                        self.age = key_age
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

        if self.trait in self.kit_traits and self.status != 'kitten':
            self.trait = choice(self.traits)

        if self.skill is None or self.skill == '???':
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

        # These things should only run when generating a new cat, rather than loading one in.
        if not loading_cat:
            # trans cat chances
            trans_chance = randint(0, 50)
            nb_chance = randint(0, 75)
            if self.gender == "female" and not self.age == 'kitten':
                if trans_chance == 1:
                    self.genderalign = "trans male"
                elif nb_chance == 1:
                    self.genderalign = "nonbinary"
                else:
                    self.genderalign = self.gender
            elif self.gender == "male" and not self.age == 'kitten':
                if trans_chance == 1:
                    self.genderalign = "trans female"
                elif nb_chance == 1:
                    self.genderalign = "nonbinary"
                else:
                    self.genderalign = self.gender
            else:
                self.genderalign = self.gender

            # APPEARANCE
            init_pelt(self)
            init_tint(self)
            init_sprite(self)
            init_scars(self)
            init_accessories(self)
            init_white_patches(self)
            init_eyes(self)
            init_pattern(self)

            # experience and current patrol status
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

        # In camp status
        self.in_camp = 1

        # NAME
        if self.pelt is not None:
            self.name = Name(status,
                             prefix,
                             suffix,
                             self.pelt.colour,
                             self.eye_colour,
                             self.pelt.name,
                             self.tortiepattern)
        else:
            self.name = Name(status, prefix, suffix, eyes=self.eye_colour)

        # Sprite sizes
        self.sprite = None
        self.big_sprite = None
        self.large_sprite = None

        # SAVE CAT INTO ALL_CATS DICTIONARY IN CATS-CLASS
        self.all_cats[self.ID] = self

        if self.ID not in ["0", None]:
            Cat.insert_cat(self)

    def __repr__(self):
        return self.ID

    @property
    def mentor(self):
        """Return managed attribute '_mentor', which is the ID of the cat's mentor."""
        return self._mentor

    @mentor.setter
    def mentor(self, mentor_id: Any):
        """Makes sure Cat.mentor can only be None (no mentor) or a string (mentor ID)."""
        if mentor_id is None or isinstance(mentor_id, str):
            self._mentor = mentor_id
        else:
            print(f"Mentor ID {mentor_id} of type {type(mentor_id)} isn't valid :("
                  "\nCat.mentor has to be either None (no mentor) or the mentor's ID as a string.")

    def is_alive(self):
        return not self.dead

    def die(self, body: bool = True):
        """
        This is used to kill a cat.

        body - defaults to True, use this to mark if the body was recovered so
        that grief messages will align with body status

        died_by_condition - defaults to False, use this to mark if the cat is dying via a condition.

        May return some additional text to add to the death event.
        """
        self.injuries.clear()
        self.illnesses.clear()

        # Deal with leader death
        text = ""
        if self.status == 'leader':
            if game.clan.leader_lives > 0:
                return ""
            elif game.clan.leader_lives <= 0:
                self.dead = True
                game.clan.leader_lives = 0
                if game.clan.instructor.df is False:
                    text = 'They\'ve lost their last life and have travelled to StarClan.'
                else:
                    text = 'They\'ve has lost their last life and have travelled to the Dark Forest.'
        else:
            self.dead = True

        # They are not removed from the mate's "mate" property. There is a "cooldown" period, which prevents
        # cats from getting into relationships the same moon their mates dies.
        self.mate = None
        """if self.mate is not None:
            if isinstance(self.mate, str):
                mate_cat: Cat = Cat.all_cats[self.mate]
                if isinstance(mate_cat, Cat):
                    mate_cat.mate = None
            elif isinstance(self.mate, Cat):
                self.mate.mate = None
            self.mate = None"""

        for app in self.apprentice.copy():
            Cat.fetch_cat(app).update_mentor()
        self.update_mentor()

        if game.clan.instructor.df is False:
            game.clan.add_to_starclan(self)
        elif game.clan.instructor.df is True:
            game.clan.add_to_darkforest(self)

        if game.clan.game_mode != 'classic':
            self.grief(body)

        return text

    def grief(self, body: bool):
        """
        compiles grief moon event text
        """
        if body is True:
            body_status = 'body'
        else:
            body_status = 'no_body'

        # major, cat won't patrol
        grief_major = [
            'loving', 'compassionate', 'empathetic', 'insecure', 'lonesome', 'nervous'
        ]
        # minor, cat will patrol
        grief_minor = [
            'daring', 'cold', 'bold', 'ambitious', 'bloodthirsty', 'responsible', 'loyal', 'strict', 'vengeful'
        ]

        text = None

        # apply grief to cats with high positive relationships to dead cat
        for cat in Cat.all_cats.values():
            if cat.dead or cat.outside or cat.moons < 1:
                continue
            relationships = cat.relationships.values()

            pos_rel_values = {
                "romantic": list(filter(lambda rel: rel.romantic_love > 55, relationships)),
                "platonic": list(filter(lambda rel: rel.platonic_like > 50, relationships)),
                "admiration": list(filter(lambda rel: rel.admiration > 70, relationships)),
                "comfort": list(filter(lambda rel: rel.comfortable > 60, relationships)),
                "trust": list(filter(lambda rel: rel.trust > 70, relationships))
            }

            neg_rel_values = {
                "dislike": list(filter(lambda rel: rel.dislike > 50, relationships)),
                "jealousy": list(filter(lambda rel: rel.jealousy > 50, relationships))
            }

            possible_strings = []
            for value in pos_rel_values:
                value_list = pos_rel_values[value]
                for y in range(len(value_list)):
                    cat_to = value_list[y].cat_to
                    if cat_to == self:
                        family_relation = self.familial_grief(living_cat=cat)
                        possible_strings.extend(
                            self.generate_events.get_possible_death_reactions(family_relation, value, cat.trait, body_status))

            if possible_strings:
                # choose string
                text = [choice(possible_strings)]

                # check if the cat will get Major or Minor severity for grief
                weights = [1, 1]
                if cat.trait in grief_major:
                    weights = [3, 1]
                if cat.trait in grief_minor:
                    weights = [1, 3]
                if "rosemary" in game.clan.herbs:  # decrease major grief chance if grave herbs are used
                    weights = [1, 6]
                    amount_used = random.choice([1, 2])
                    game.clan.herbs["rosemary"] -= amount_used
                    if game.clan.herbs["rosemary"] <= 0:
                        game.clan.herbs.pop("rosemary")
                    if f"Rosemary was used for {self.name}'s body." not in game.herb_events_list:
                        game.herb_events_list.append(f"Rosemary was used for {self.name}'s body.")

                severity = random.choices(['major', 'minor'], weights=weights, k=1)
                # give the cat the relevant severity text
                severity = severity[0]
                if severity == 'major':
                    text.append(choice(
                        MINOR_MAJOR_REACTION["major"]
                    ))
                elif severity == 'minor':
                    text.append(choice(
                        MINOR_MAJOR_REACTION["minor"]
                    ))

                # grief the cat
                if game.clan.game_mode != 'classic':
                    cat.get_ill("grief stricken", event_triggered=True, severity=severity)

            # negative reactions, no grief
            else:
                for value in neg_rel_values:
                    value_list = neg_rel_values[value]
                    for y in range(len(value_list)):
                        cat_to = value_list[y].cat_to
                        if cat_to == self:
                            family_relation = self.familial_grief(living_cat=cat)
                            possible_strings.extend(
                                self.generate_events.get_possible_death_reactions(family_relation, value, cat.trait, body_status))

                if possible_strings:
                    # choose string
                    text = [choice(possible_strings)]

            if text:
                # adjust and append text to grief string list
                # print(text)
                text = ' '.join(text)
                text = event_text_adjust(Cat, text, self, cat)
                Cat.grief_strings[cat.ID] = (text, (self.ID, cat.ID))
                possible_strings.clear()
                text = None

    def familial_grief(self, living_cat: Cat):
        """
        returns relevant grief strings for family members, if no relevant strings then returns None
        """
        dead_cat = self

        if dead_cat.is_parent(living_cat):
            return "child"
        elif living_cat.is_parent(dead_cat):
            return "parent"
        elif dead_cat.is_sibling(living_cat):
            return "sibling"
        else:
            return "general"

    def gone(self):
        """ Makes a clan cat an "outside" cat. Handles removing them from special positions, and removing
        mentors and apprentices. """
        if self.status == 'leader':
            self.outside = True
            game.clan.leader_lives = 1
            game.clan.leader.outside = True

        elif self.status == 'deputy':
            self.outside = True
            self.status = 'warrior'
            game.clan.deputy.outside = True
        else:
            self.outside = True
        for app in self.apprentice.copy():
            app_ob = Cat.fetch_cat(app)
            app_ob.update_mentor()
        self.update_mentor()
        game.clan.add_to_outside(self)
    
    def add_to_clan(self):
        """ Makes a "outside cat" a clan cat. Former leaders, deputies will become warriors. Apprentices will be assigned a mentor."""
        self.outside = False
        if self.status in ['leader', 'deputy']:
            self.status_change('warrior')
            self.status = 'warrior'
        elif self.status == 'apprentice' and self.moons >= 12:
            self.status_change('warrior')
            involved_cats = [self.ID]
            game.cur_events_list.append(Single_Event('A long overdue warrior ceremony is held for ' + str(self.name.prefix) + 'paw. They smile as they finally become a warrior of the Clan and are now named ' + str(self.name) + '.', "ceremony", involved_cats))
        elif self.status == 'kitten' and self.moons >= 12:
            self.status_change('warrior')
            involved_cats = [self]
            game.cur_events_list.append(Single_Event('A long overdue warrior ceremony is held for ' + str(self.name.prefix) + 'kit. They smile as they finally become a warrior of the Clan and are now named ' + str(self.name) + '.', "ceremony", involved_cats))
        elif self.status == 'kitten' and self.moons >= 6:
            self.status_change('apprentice')
            involved_cats = [self.ID]
            game.cur_events_list.append(Single_Event('A long overdue apprentice ceremony is held for ' + str(self.name.prefix) + 'kit. They smile as they finally become a warrior of the Clan and are now named ' + str(self.name) + '.', "ceremony", involved_cats))
        elif self.status in ['kittypet', 'loner', 'rogue']:
            if self.moons < 6:
                self.status = "kitten"
            elif self.moons < 12:
                self.status_change('apprentice')
            elif self.moons < 120:
                self.status_change('warrior')
            else:
                self.status_change('elder')
        game.clan.add_to_clan(self)
        self.update_mentor()

    def status_change(self, new_status, resort=False):
        """ Changes the status of a cat. Additional functions are needed if you want to make a cat a leader or deputy.
            new_status = The new status of a cat. Can be 'apprentice', 'medicine cat apprentice', 'warrior'
                        'medicine cat', 'elder'.
            resort = If sorting type is 'rank', and resort is True, it will resort the cat list. This should
                    only be true for non-timeskip status changes. """
        old_status = self.status
        self.status = new_status
        self.name.status = new_status

        # If they have any apprentices, make sure they are still valid:
        if old_status == "medicine cat":
            game.clan.remove_med_cat(self)
            for app in self.apprentice.copy():
                Cat.fetch_cat(app).update_med_mentor()
        else:
            for app in self.apprentice.copy():
                Cat.fetch_cat(app).update_mentor()

        # updates mentors
        if self.status == 'apprentice':
            self.update_mentor()

        elif self.status == 'medicine cat apprentice':
            self.update_med_mentor()

        elif self.status == 'warrior':
            self.update_mentor()
            self.update_skill()

            if old_status == 'leader':
                game.clan.leader_lives = 0
                self.died_by = []  # Clear their deaths.
                if game.clan.leader:
                    if game.clan.leader.ID == self.ID:
                        game.clan.leader = None
                        game.clan.leader_predecessors += 1

                    # don't remove the check for game.clan, this is needed for tests
            if game.clan and game.clan.deputy:
                if game.clan.deputy.ID == self.ID:
                    game.clan.deputy = None
                    game.clan.deputy_predecessors += 1

        elif self.status == 'medicine cat':
            self.update_med_mentor()
            self.update_skill()
            if game.clan is not None:
                game.clan.new_medicine_cat(self)

        elif self.status == 'elder':
            self.update_mentor()
            self.skill = choice(self.elder_skills)

            # Ideally, this should also be triggered for cats that retired due to
            # health conditions. However, it is currently being triggered for all elders to
            # prevent "unretiring" by switching to med or mediator, then warrior.
            self.retired = True

            if old_status == 'leader':
                game.clan.leader_lives = 0
                self.died_by = []  # Clear their deaths.
                if game.clan.leader:
                    if game.clan.leader.ID == self.ID:
                        game.clan.leader = None
                        game.clan.leader_predecessors += 1

            if game.clan.deputy:
                if game.clan.deputy.ID == self.ID:
                    game.clan.deputy = None
                    game.clan.deputy_predecessors += 1

        elif self.status == 'mediator':
            self.update_mentor()
            self.update_skill()

        elif self.status == 'mediator apprentice':
            self.update_mentor()

        # update class dictionary
        self.all_cats[self.ID] = self

        # If we have it sorted by rank, we also need to re-sort
        if game.sort_type == "rank" and resort:
            Cat.sort_cats()

    def update_traits(self):
        """Updates the traits of a cat upon ageing up.  """
        if self.moons == 6:
            chance = randint(0, 5)  # chance for cat to gain trait that matches their previous trait's personality group
            if chance == 0:
                self.trait = choice(self.traits)
            else:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        chosen_trait = choice(possible_trait)
                        if chosen_trait in self.kit_traits:
                            self.trait = choice(self.traits)
                        else:
                            self.trait = chosen_trait
        elif self.moons == 12:
            chance = randint(0, 9) + int(self.patrol_with_mentor)  # chance for cat to gain new trait or keep old
            if chance == 0:
                self.trait = choice(self.traits)
                self.mentor_influence.insert(0, 'None')
            elif 1 <= chance <= 6:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        chosen_trait = choice(possible_trait)
                        if chosen_trait in self.kit_traits:
                            self.trait = self.trait
                            self.mentor_influence.insert(0, 'None')
                        else:
                            self.trait = chosen_trait
                            self.mentor_influence.insert(0, 'None')
            elif chance >= 7:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    mentor = None
                    if self.mentor:
                        mentor = Cat.fetch_cat(self.mentor)
                    elif not self.mentor and len(self.former_mentor) != 0:
                        if len(self.former_mentor) > 1:
                            mentor = Cat.fetch_cat(self.former_mentor[-1])
                        else:
                            mentor = Cat.fetch_cat(self.former_mentor[0])
                    else:
                        self.mentor_influence.insert(0, 'None')
                    if mentor and mentor.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)

                        if x == 'Abrasive' and chance >= 12:
                            possible_trait = self.personality_groups.get('Reserved')
                            self.mentor_influence.insert(0, 'Reserved')
                        chosen_trait = choice(possible_trait)

                        if chosen_trait in self.kit_traits:
                            self.trait = choice(self.traits)
                            if 'Reserved' in self.mentor_influence:
                                self.mentor_influence.pop(0)
                            self.mentor_influence.insert(0, 'None')
                        else:
                            self.trait = chosen_trait
                            if 'Reserved' not in self.mentor_influence:
                                self.mentor_influence.insert(0, x)
            else:
                self.mentor_influence.insert(0, 'None')

        elif self.moons == 120:
            chance = randint(0, 7)  # chance for cat to gain new trait or keep old
            if chance == 0:
                self.trait = choice(self.traits)
            elif chance == 1:
                possible_groups = ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']
                for x in possible_groups:
                    if self.trait in self.personality_groups[x]:
                        possible_trait = self.personality_groups.get(x)
                        chosen_trait = choice(possible_trait)
                        if chosen_trait in self.kit_traits:
                            self.trait = choice(self.traits)
                        else:
                            self.trait = chosen_trait

    def describe_cat(self):
        """ Generates a string describing the cat's appearance and gender. Mainly used for generating
        the allegiances."""
        if self.genderalign == 'male' or self.genderalign == "transmasc" or self.genderalign == "trans male":
            sex = 'tom'
        elif self.genderalign == 'female' or self.genderalign == "transfem" or self.genderalign == "trans female":
            sex = 'she-cat'
        else:
            sex = 'cat'
        description = str(self.pelt.length).lower() + '-furred'
        description += ' ' + describe_color(self.pelt, self.tortiecolour, self.tortiepattern,
                                            self.white_patches) + ' ' + sex
        return description

    def describe_eyes(self):
        colour = str(self.eye_colour).lower()
        colour2 = str(self.eye_colour2).lower()

        if colour == 'palegreen':
            colour = 'pale green'
        elif colour == 'darkblue':
            colour = 'dark blue'
        elif colour == 'paleblue':
            colour = 'pale blue'
        elif colour == 'paleyellow':
            colour = 'pale yellow'
        elif colour == 'heatherblue':
            colour = 'heather blue'
        elif colour == 'blue2':
            colour = 'blue'
        elif colour == 'sunlitice':
            colour = 'sunlit ice'
        elif colour == 'greenyellow':
            colour = 'green-yellow'
        if self.eye_colour2 != None:
            if colour2 == 'palegreen':
                colour2 = 'pale green'
            if colour2 == 'darkblue':
                colour2 = 'dark blue'
            if colour2 == 'paleblue':
                colour2 = 'pale blue'
            if colour2 == 'paleyellow':
                colour2 = 'pale yellow'
            if colour2 == 'heatherblue':
                colour2 = 'heather blue'
            if colour2 == 'blue2':
                colour2 = 'blue'
            if colour2 == 'sunlitice':
                colour2 = 'sunlit ice'
            if colour2 == 'greenyellow':
                colour2 = 'green-yellow'
            colour = colour + ' and ' + colour2
        return colour

    # ---------------------------------------------------------------------------- #
    #                              moon skip functions                             #
    # ---------------------------------------------------------------------------- #

    def one_moon(self):
        """Handles a moon skip for an alive cat. """
        if self.exiled or self.outside:
            # this is handled in events.py
            self.thoughts()
            return

        if self.dead:
            self.thoughts()
            return

        self.moons += 1
        self.update_traits()
        self.in_camp = 1

        if self.status in ['apprentice', 'mediator apprentice']:
            self.update_mentor()
        elif self.status == 'medicine cat apprentice':
            self.update_med_mentor()
        else:
            self.update_skill()

    def thoughts(self):
        """ Generates a thought for the cat, which displays on their profile. """
        all_cats = self.all_cats
        other_cat = random.choice(list(all_cats.keys()))

        # get other cat
        i = 0
        while other_cat == self.ID and len(all_cats) > 1 or (all_cats.get(other_cat).status in ['kittypet', 'rogue', 'loner']):
            other_cat = random.choice(list(all_cats.keys()))
            i += 1
            if i > 100:
                other_cat = None
                break

        other_cat = all_cats.get(other_cat)
            
        # get possible thoughts
        thought_possibilities = get_thoughts(self, other_cat)
        chosen_thought = random.choice(thought_possibilities)

        # insert name if it is needed
        if "r_c" in chosen_thought:
            chosen_thought = chosen_thought.replace("r_c", str(other_cat.name))

        # insert Clan name if needed
        try:
            if "c_n" in chosen_thought:
                chosen_thought = chosen_thought.replace("c_n", str(game.clan.name) + 'Clan')
        except AttributeError:
            if "c_n" in chosen_thought:
                chosen_thought = chosen_thought.replace("c_n", game.switches["clan_list"][0] + 'Clan')

        # insert thought
        self.thought = str(chosen_thought)

    def create_interaction(self):
        """Creates an interaction between this cat and another, which effects relationship values. """
        # if the cat has no relationships, skip
        if len(self.relationships) < 1 or not self.relationships:
            return

        cats_to_choose = list(
            filter(lambda iter_cat_id: iter_cat_id != self.ID,
                   Cat.all_cats.copy()))
        # increase chance of cats, which are already befriended
        like_threshold = 30
        relevant_relationships = list(
            filter(lambda relation: relation.platonic_like >= like_threshold,
                   self.relationships.values()))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.platonic_like >= like_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase chance of cats, which are already may be in love
        love_threshold = 30
        relevant_relationships = list(
            filter(lambda relation: relation.romantic_love >= love_threshold,
                   self.relationships.values()))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.romantic_love >= love_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase the chance a kitten interacts with other kittens
        if self.age == "kitten":
            kittens = list(
                filter(
                    lambda cat_id: self.all_cats.get(cat_id).age == "kitten" and
                                   cat_id != self.ID, Cat.all_cats.copy()))
            amount = int(len(cats_to_choose) / 4)
            if len(kittens) > 0:
                amount = int(len(cats_to_choose) / len(kittens))
            cats_to_choose = cats_to_choose + kittens * amount

        # increase the chance an apprentice interacts with other apprentices
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
                                 not relation.cat_to.dead, self.relationships.values()))
        random_cat = self.all_cats.get(random_id)
        kitten_and_outside = random_cat is not None and random_cat.outside and self.age == "kitten"

        # is also found in Relation_Events.MAX_ATTEMPTS
        attempts_left = 1000
        while len(relevant_relationship_list) < 1 or random_id == self.ID or kitten_and_outside:
            random_id = random.choice(cats_to_choose)
            random_cat = self.all_cats.get(random_id)
            kitten_and_outside = random_cat is not None and random_cat.outside and self.age == "kitten"
            relevant_relationship_list = list(
                filter(
                    lambda relation: str(relation.cat_to) == str(random_id) and
                                     not relation.cat_to.dead, self.relationships.values()))
            attempts_left -= 1
            if attempts_left <= 0:
                return
        relevant_relationship = relevant_relationship_list[0]
        relevant_relationship.start_action()

        if game.game_mode == "classic":
            return
        # handle contact with ill cat if
        if self.is_ill():
            relevant_relationship.cat_to.contact_with_ill_cat(self)
        if relevant_relationship.cat_to.is_ill():
            self.contact_with_ill_cat(relevant_relationship.cat_to)

    def relationship_interaction(self):
        """Randomly choose a cat of the clan and have a interaction with them."""
        # if the cat has no relationships, skip
        if len(self.relationships) < 1 or not self.relationships:
            return

        cats_to_choose = list(
            filter(lambda iter_cat: iter_cat.ID != self.ID and not iter_cat.outside and not iter_cat.exiled and not iter_cat.dead,
                   Cat.all_cats.values())
        )
        # if there are not cats to interact, stop
        if len(cats_to_choose) < 1:
            return

        chosen_cat = choice(cats_to_choose)
        relevant_relationship = self.relationships[chosen_cat.ID]
        relevant_relationship.start_interaction()

        if game.game_mode == "classic":
            return
        # handle contact with ill cat if
        if self.is_ill():
            relevant_relationship.cat_to.contact_with_ill_cat(self)
        if relevant_relationship.cat_to.is_ill():
            self.contact_with_ill_cat(relevant_relationship.cat_to)
        

    def update_skill(self):
        """Checks for skill and replaces empty skill if cat is old enough
        # also adds a chance for cat to take a skill similar to their mentor"""

        if self.skill == '???':
            if len(self.mentor_influence) < 1:
                self.mentor_influence = ['None']
            # assign skill to new medicine cat
            if self.status == 'medicine cat' and self.skill not in self.med_skills:
                # skill groups they can take from
                possible_groups = ['special', 'heal', 'star', 'mediate', 'smart', 'teach']
                # check if they had a mentor
                if self.former_mentor:
                    chance = randint(0, 9) + int(self.patrol_with_mentor)
                    mentor = Cat.fetch_cat(self.former_mentor[-1])
                    if not mentor:
                        print("WARNING: mentor not found")
                        return
                    # give skill from mentor, this is a higher chance of happening than the warrior has
                    # bc med cats have no patrol_with_mentor modifier
                    if chance >= 9:
                        for x in possible_groups:
                            if mentor.skill in self.skill_groups[x]:
                                possible_skill = self.skill_groups.get(x)
                                self.skill = choice(possible_skill)
                                self.mentor_influence.insert(1, self.skill)
                                return

                # Will only be reached if a mentor skill was not applied.
                self.skill = choice(self.med_skills)
                self.mentor_influence.insert(1, 'None')

            # assign skill to new warrior
            elif self.status == 'warrior':
                # possible skill groups they can take from
                possible_groups = ['star', 'smart', 'teach', 'hunt', 'fight', 'speak']
                # check if they had a mentor
                if self.former_mentor:
                    chance = randint(0, 9) + int(self.patrol_with_mentor)
                    mentor = Cat.fetch_cat(self.former_mentor[-1])
                    if not mentor:
                        print("WARNING: mentor not found")
                        return
                    # give skill from mentor
                    if chance >= 9:
                        for x in possible_groups:
                            if mentor.skill in self.skill_groups[x]:
                                possible_skill = self.skill_groups.get(x)
                                self.skill = choice(possible_skill)
                                self.mentor_influence.insert(1, self.skill)
                                return

                self.skill = choice(self.skills)
                self.mentor_influence.insert(1, 'None')

            elif self.status == 'mediator':
                possible_groups = ['star', 'smart', 'teach', 'speak', 'mediate']
                if self.former_mentor:
                    chance = randint(0, 12)
                    mentor = Cat.fetch_cat(self.former_mentor[-1])
                    if not mentor:
                        print("WARNING: mentor not found")
                        return
                # give skill from mentor
                    if chance >= 9:
                        for x in possible_groups:
                            if mentor.skill in self.skill_groups[x]:
                                possible_skill = self.skill_groups.get(x)
                                self.skill = choice(possible_skill)
                                self.mentor_influence.insert(1, self.skill)
                                return

                    all_skills = []
                    for x in possible_groups:
                        all_skills.extend(self.skill_groups[x])
                    self.skill = choice(all_skills)
                    self.mentor_influence.insert(1, 'None')


            # assign new skill to elder
            elif self.status == 'elder':
                self.skill = choice(self.elder_skills)

            # if a cat somehow has no skill, assign one after checking that they aren't a kit or adolescent
            elif self.skill == '???' and self.status not in ['apprentice', 'medicine cat apprentice',
                                                             'mediator apprentice', 'kitten']:
                self.skill = choice(self.skills)

    def moon_skip_illness(self, illness):
        """handles the moon skip for illness"""
        if not self.is_ill():
            return False

        if self.illnesses[illness]["event_triggered"]:
            self.illnesses[illness]["event_triggered"] = False
            return True

        mortality = self.illnesses[illness]["mortality"]

        # leader should have a higher chance of death
        if self.status == "leader" and mortality != 0:
            mortality = int(mortality * 0.7)
            if mortality == 0:
                mortality = 1

        if mortality and not int(random.random() * mortality):
            if self.status == "leader":
                self.leader_death_heal = True
                game.clan.leader_lives -= 1
                if game.clan.leader_lives > 0:
                    text = f"{self.name} lost a life to {illness}."
                    # game.health_events_list.append(text)
                    # game.birth_death_events_list.append(text)
                    game.cur_events_list.append(Single_Event(text, ["birth_death", "health"], game.clan.leader.ID))
                elif game.clan.leader_lives <= 0:
                    text = f"{self.name} lost their last life to {illness}."
                    # game.health_events_list.append(text)
                    # game.birth_death_events_list.append(text)
                    game.cur_events_list.append(Single_Event(text, ["birth_death", "health"], game.clan.leader.ID))
            self.die()
            return False

        keys = self.illnesses[illness].keys()
        if 'moons_with' in keys:
            self.illnesses[illness]["moons_with"] += 1
        else:
            self.illnesses[illness].update({'moons_with': 1})

        self.illnesses[illness]["duration"] -= 1
        if self.illnesses[illness]["duration"] <= 0:
            self.healed_condition = True
            return False

    def moon_skip_injury(self, injury):
        """handles the moon skip for injury"""
        if not self.is_injured():
            return

        if self.injuries[injury]["event_triggered"] is True:
            self.injuries[injury]["event_triggered"] = False
            return True

        mortality = self.injuries[injury]["mortality"]

        # leader should have a higher chance of death
        if self.status == "leader" and mortality != 0:
            mortality = int(mortality * 0.7)
            if mortality == 0:
                mortality = 1

        if mortality and not int(random.random() * mortality):
            if self.status == 'leader':
                game.clan.leader_lives -= 1
            self.die()
            return

        keys = self.injuries[injury].keys()
        if 'moons_with' in keys:
            self.injuries[injury]["moons_with"] += 1
        else:
            self.injuries[injury].update({'moons_with': 1})

        # if the cat has an infected wound, the wound shouldn't heal till the illness is cured
        if not self.injuries[injury]["complication"]:
            self.injuries[injury]["duration"] -= 1
        if self.injuries[injury]["duration"] <= 0:
            self.healed_condition = True
            return

    def moon_skip_permanent_condition(self, condition):
        """handles the moon skip for permanent conditions"""
        if not self.is_disabled():
            return False

        if self.permanent_condition[condition]["event_triggered"]:
            self.permanent_condition[condition]["event_triggered"] = False
            return False

        mortality = self.permanent_condition[condition]["mortality"]
        moons_until = self.permanent_condition[condition]["moons_until"]
        born_with = self.permanent_condition[condition]["born_with"]

        # handling the countdown till a congenital condition is revealed
        if moons_until is not None and moons_until >= 0 and born_with is True:
            self.permanent_condition[condition]["moons_until"] = int(moons_until - 1)
            self.permanent_condition[condition]["moons_with"] = 0
            if self.permanent_condition[condition]["moons_until"] != -1:
                return False
        if self.permanent_condition[condition]["moons_until"] == -1 and \
                self.permanent_condition[condition]["born_with"] is True:
            self.permanent_condition[condition]["moons_until"] = -2
            return True

        keys = self.permanent_condition[condition].keys()
        if 'moons_with' in keys:
            self.permanent_condition[condition]["moons_with"] += 1
        else:
            self.permanent_condition[condition].update({'moons_with': 1})

        # leader should have a higher chance of death
        if self.status == "leader" and mortality != 0:
            mortality = int(mortality * 0.7)
            if mortality == 0:
                mortality = 1

        if mortality and not int(random.random() * mortality):
            if self.status == 'leader':
                game.clan.leader_lives -= 1
            self.die()
            return True

    # ---------------------------------------------------------------------------- #
    #                                   relative                                   #
    # ---------------------------------------------------------------------------- #
    def get_parents(self):
        """Returns list containing parents of cat."""
        if self.parent1:
            if self.parent2:
                return [self.parent1, self.parent2]
            return [self.parent1]
        return []

    def get_siblings(self):
        """Returns list of the siblings."""
        return self.siblings

    def get_children(self):
        """Returns list of the children."""
        return self.children

    def is_grandparent(self, other_cat: Cat):
        """Check if the cat is the grandparent of the other cat."""
        # Get parents ID
        parents = other_cat.get_parents()
        for parent in parents:
            # Get parent 'Cat'
            if parent in Cat.all_cats.keys():
                parent_obj = Cat.all_cats.get(parent)
            else:
                parent_obj = Cat.load_faded_cat(parent)
            if parent_obj:
                # If there are parents, get grandparents and check if our ID is among them.
                if self.ID in parent_obj.get_parents():
                    return True
        return False

    def is_parent(self, other_cat: Cat):
        """Check if the cat is the parent of the other cat."""
        if self.ID in other_cat.get_parents():
            return True
        return False

    def is_sibling(self, other_cat: Cat):
        """Check if the cats are siblings."""
        if other_cat == self:
            return False
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

    def is_cousin(self, other_cat):
        grandparent_id = []
        for parent in other_cat.get_parents():
            parent_ob = Cat.fetch_cat(parent)
            grandparent_id.extend(parent_ob.get_parents())
        for parent in self.get_parents():
            parent_ob = Cat.fetch_cat(parent)
            if set(parent_ob.get_parents()) & set(grandparent_id):
                return True
        return False

    # ---------------------------------------------------------------------------- #
    #                                  conditions                                  #
    # ---------------------------------------------------------------------------- #

    def get_ill(self, name, event_triggered=False, lethal=True, severity='default'):
        """
        use to make a cat ill.
        name = name of the illness you want the cat to get
        event_triggered = make True to have this illness skip the illness_moonskip for 1 moon
        lethal = set True to leave the illness mortality rate at its default level.
                 set False to force the illness to have 0 mortality
        severity = leave 'default' to keep default severity, otherwise set to the desired severity
                   ('minor', 'major', 'severe')
        """
        if name not in ILLNESSES:
            print(f"WARNING: {name} is not in the illnesses collection.")
            return
        if name == 'kittencough' and self.status != 'kitten':
            return

        illness = ILLNESSES[name]
        mortality = illness["mortality"][self.age]
        med_mortality = illness["medicine_mortality"][self.age]
        if severity == 'default':
            illness_severity = illness["severity"]
        else:
            illness_severity = severity

        duration = illness['duration']
        med_duration = illness['medicine_duration']

        amount_per_med = get_amount_cat_for_one_medic(game.clan)

        if medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med):
            duration = med_duration
        if severity != 'minor':
            duration += random.randrange(-1, 1)
        if duration == 0:
            duration = 1

        if game.clan.game_mode == "cruel season":
            if mortality != 0:
                mortality = int(mortality * 0.5)
                med_mortality = int(med_mortality * 0.5)

                # to prevent an illness gets no mortality, check and set it to 1 if needed
                if mortality == 0 or med_mortality == 0:
                    mortality = 1
                    med_mortality = 1
        if lethal is False:
            mortality = 0

        new_illness = Illness(
            name=name,
            severity=illness_severity,
            mortality=mortality,
            infectiousness=illness["infectiousness"],
            duration=duration,
            medicine_duration=illness["medicine_duration"],
            medicine_mortality=med_mortality,
            risks=illness["risks"],
            event_triggered=event_triggered
        )

        if new_illness.name not in self.illnesses:
            self.illnesses[new_illness.name] = {
                "severity": new_illness.severity,
                "mortality": new_illness.current_mortality,
                "infectiousness": new_illness.infectiousness,
                "duration": new_illness.duration,
                "moons_with": 1,
                "risks": new_illness.risks,
                "event_triggered": new_illness.new
            }

    def get_injured(self, name, event_triggered=False, lethal=True):
        if name not in INJURIES:
            if name not in INJURIES:
                print(f"WARNING: {name} is not in the injuries collection.")
            return

        if name == 'mangled tail' and 'NOTAIL' in self.scars:
            return
        if name == 'torn ear' and 'NOEAR' in self.scars:
            return

        injury = INJURIES[name]
        mortality = injury["mortality"][self.age]
        duration = injury['duration']
        med_duration = injury['medicine_duration']

        amount_per_med = get_amount_cat_for_one_medic(game.clan)

        if medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med):
            duration = med_duration
        duration += random.randrange(-1, 1)
        if duration == 0:
            duration = 1

        if mortality != 0:
            if game.clan.game_mode == "cruel season":
                mortality = int(mortality * 0.5)

                if mortality == 0:
                    mortality = 1
        if lethal is False:
            mortality = 0

        new_injury = Injury(
            name=name,
            severity=injury["severity"],
            duration=injury["duration"],
            medicine_duration=duration,
            mortality=mortality,
            risks=injury["risks"],
            illness_infectiousness=injury["illness_infectiousness"],
            also_got=injury["also_got"],
            cause_permanent=injury["cause_permanent"],
            event_triggered=event_triggered
        )

        if new_injury.name not in self.injuries:
            self.injuries[new_injury.name] = {
                "severity": new_injury.severity,
                "mortality": new_injury.current_mortality,
                "duration": new_injury.duration,
                "moons_with": 1,
                "illness_infectiousness": new_injury.illness_infectiousness,
                "risks": new_injury.risks,
                "complication": None,
                "cause_permanent": new_injury.cause_permanent,
                "event_triggered": new_injury.new
            }

        if len(new_injury.also_got) > 0 and not int(random.random() * 5):
            avoided = False
            if 'blood loss' in new_injury.also_got and len(get_med_cats(Cat)) != 0:
                clan_herbs = set()
                needed_herbs = {"horsetail", "raspberry", "marigold", "cobwebs"}
                clan_herbs.update(game.clan.herbs.keys())
                herb_set = needed_herbs.intersection(clan_herbs)
                usable_herbs = []
                usable_herbs.extend(herb_set)

                if usable_herbs:
                    # deplete the herb
                    herb_used = random.choice(usable_herbs)
                    game.clan.herbs[herb_used] -= 1
                    if game.clan.herbs[herb_used] <= 0:
                        game.clan.herbs.pop(herb_used)
                    avoided = True
                    text = f"{herb_used.capitalize()} was used to stop blood loss for {self.name}."
                    game.herb_events_list.append(text)

            if not avoided:
                self.also_got = True
                additional_injury = choice(new_injury.also_got)
                if additional_injury in INJURIES:
                    self.additional_injury(additional_injury)
                else:
                    self.get_ill(additional_injury, event_triggered=True)
        else:
            self.also_got = False

    def congenital_condition(self, cat):
        possible_conditions = []

        for condition in PERMANENT:
            possible = PERMANENT[condition]
            if possible["congenital"] in ['always', 'sometimes']:
                possible_conditions.append(condition)

        new_condition = choice(possible_conditions)

        if new_condition == "born without a leg":
            cat.scars.append('NOPAW')
        elif new_condition == "born without a tail":
            cat.scars.append('NOTAIL')

        self.get_permanent_condition(new_condition, born_with=True)

    def get_permanent_condition(self, name, born_with=False, event_triggered=False):
        if name not in PERMANENT:
            print(str(self.name), f"WARNING: {name} is not in the permanent conditions collection.")
            return

        # remove accessories if need be
        if 'NOTAIL' in self.scars and self.accessory in ['RED FEATHERS', 'BLUE FEATHERS', 'JAY FEATHERS']:
            self.accessory = None
        if 'HALFTAIL' in self.scars and self.accessory in ['RED FEATHERS', 'BLUE FEATHERS', 'JAY FEATHERS']:
            self.accessory = None

        condition = PERMANENT[name]
        new_condition = False
        mortality = condition["mortality"][self.age]
        if mortality != 0:
            if game.clan.game_mode == "cruel season":
                mortality = int(mortality * 0.65)

        if condition['congenital'] == 'always':
            born_with = True
        moons_until = condition["moons_until"]
        if born_with and moons_until != 0:
            moons_until = randint(moons_until - 1, moons_until + 1)  # creating a range in which a condition can present
            if moons_until < 0:
                moons_until = 0

        if born_with and self.status != 'kitten':
                moons_until = -2
        elif born_with is False:
            moons_until = 0

        new_perm_condition = PermanentCondition(
            name=name,
            severity=condition["severity"],
            congenital=condition["congenital"],
            moons_until=moons_until,
            mortality=mortality,
            risks=condition["risks"],
            illness_infectiousness=condition["illness_infectiousness"],
            event_triggered=event_triggered
        )

        if new_perm_condition.name not in self.permanent_condition:
            self.permanent_condition[new_perm_condition.name] = {
                "severity": new_perm_condition.severity,
                "born_with": born_with,
                "moons_until": new_perm_condition.moons_until,
                "moons_with": 1,
                "mortality": new_perm_condition.current_mortality,
                "illness_infectiousness": new_perm_condition.illness_infectiousness,
                "risks": new_perm_condition.risks,
                "complication": None,
                "event_triggered": new_perm_condition.new
            }
            new_condition = True

        return new_condition

    def not_working(self):
        """returns True if the cat cannot work, False if the cat can work"""
        not_working = False
        for illness in self.illnesses:
            if self.illnesses[illness]['severity'] != 'minor':
                not_working = True
                break
        for injury in self.injuries:
            if self.injuries[injury]['severity'] != 'minor':
                not_working = True
                break
        return not_working

    # This is only for cats that retire due to the health condition.
    def retire_cat(self):
        old_status = self.status
        self.retired = True
        self.status = 'elder'
        self.name.status = 'elder'

        if old_status == 'leader':
            game.clan.leader_lives = 0
            self.died_by = []  # Clear their deaths.
            if game.clan.leader:
                if game.clan.leader.ID == self.ID:
                    game.clan.leader = None
                    game.clan.leader_predecessors += 1

        if game.clan.deputy:
            if game.clan.deputy.ID == self.ID:
                game.clan.deputy = None
                game.clan.deputy_predecessors += 1

        self.update_mentor()

    def additional_injury(self, injury):
        self.get_injured(injury, event_triggered=True)

    def is_ill(self):
        is_ill = True
        if len(self.illnesses) <= 0:
            is_ill = False
        return is_ill is not False

    def is_injured(self):
        is_injured = True
        if len(self.injuries) <= 0:
            is_injured = False
        return is_injured is not False

    def is_disabled(self):
        is_disabled = True
        if len(self.permanent_condition) <= 0:
            is_disabled = False
        return is_disabled is not False

    def contact_with_ill_cat(self, cat: Cat):
        """handles if one cat had contact with an ill cat"""

        infectious_illnesses = []
        if self.is_ill() or cat is None or not cat.is_ill():
            return
        elif cat.is_ill():
            for illness in cat.illnesses:
                if cat.illnesses[illness]["infectiousness"] != 0:
                    infectious_illnesses.append(illness)
            if len(infectious_illnesses) == 0:
                return

        for illness in infectious_illnesses:
            illness_name = illness
            rate = cat.illnesses[illness]["infectiousness"]
            if self.is_injured():
                for y in self.injuries:
                    illness_infect = list(
                        filter(lambda ill: ill["name"] == illness_name, self.injuries[y]["illness_infectiousness"]))
                    if illness_infect is not None and len(illness_infect) > 0:
                        illness_infect = illness_infect[0]
                        rate -= illness_infect["lower_by"]

                    # prevent rate lower 0 and print warning message
                    if rate < 0:
                        print(
                            f"WARNING: injury {self.injuries[y]['name']} has lowered chance of {illness_name} infection to {rate}")
                        rate = 1

            if not random.random() * rate:
                text = f"{self.name} had contact with {cat.name} and now has {illness_name}."
                # game.health_events_list.append(text)
                game.cur_events_list.append(Single_Event(text, "health", [self.ID, cat.ID]))
                self.get_ill(illness_name)

    def save_condition(self):
        # save conditions for each cat
        clanname = None
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]
        elif game.clan is not None:
            clanname = game.clan.name

        condition_directory = 'saves/' + clanname + '/conditions'
        condition_file_path = condition_directory + '/' + self.ID + '_conditions.json'

        if not os.path.exists(condition_directory):
            os.makedirs(condition_directory)

        if (not self.is_ill() and not self.is_injured() and not self.is_disabled()) or self.dead or self.outside:
            if os.path.exists(condition_file_path):
                os.remove(condition_file_path)
            return

        conditions = {}

        if self.is_ill():
            conditions["illnesses"] = self.illnesses

        if self.is_injured():
            conditions["injuries"] = self.injuries

        if self.is_disabled():
            conditions["permanent conditions"] = self.permanent_condition

        try:
            with open(condition_file_path, 'w') as rel_file:
                json_string = ujson.dumps(conditions, indent=4)
                rel_file.write(json_string)
        except:
            print(f"WARNING: Saving conditions of cat #{self} didn't work.")

    def load_conditions(self):
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        else:
            clanname = game.switches['clan_list'][0]

        condition_directory = 'saves/' + clanname + '/conditions/'
        condition_cat_directory = condition_directory + self.ID + '_conditions.json'
        if not os.path.exists(condition_cat_directory):
            return

        try:
            with open(condition_cat_directory, 'r') as read_file:
                rel_data = ujson.loads(read_file.read())
                if "illnesses" in rel_data:
                    self.illnesses = rel_data.get("illnesses")
                if "injuries" in rel_data:
                    self.injuries = rel_data.get("injuries")
                if "permanent conditions" in rel_data:
                    self.permanent_condition = rel_data.get("permanent conditions")

        except Exception as e:
            print(f"WARNING: There was an error reading the condition file of cat #{self}.\n", e)

    # ---------------------------------------------------------------------------- #
    #                                    mentor                                    #
    # ---------------------------------------------------------------------------- #

    def is_valid_med_mentor(self, potential_mentor: Cat):
        # Dead or outside cats can't be mentors
        if potential_mentor.dead or potential_mentor.outside:
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

    def is_valid_mentor(self, potential_mentor: Cat):
        # Dead or outside cats can't be mentors
        if potential_mentor.dead or potential_mentor.outside:
            return False
        # Match jobs
        if self.status == 'medicine cat apprentice' and potential_mentor.status != 'medicine cat':
            return False
        if self.status == 'apprentice' and potential_mentor.status not in [
            'leader', 'deputy', 'warrior'
        ]:
            return False
        if self.status == 'mediator apprentice' and potential_mentor.status != 'mediator':
            return False

        # If not an app, don't need a mentor
        if 'apprentice' not in self.status:
            return False
        # Dead cats don't need mentors
        if self.dead:
            return False
        return True

    def update_med_mentor(self, new_mentor: Any = None):
        # No !!
        if isinstance(new_mentor, Cat):
            print("Everything is terrible!! (new_mentor {new_mentor} is a Cat D:)")
            return
        # Check if cat can have a mentor
        illegible_for_mentor = self.dead or self.outside or self.exiled or self.status != "medicine cat apprentice"
        if illegible_for_mentor:
            self.__remove_mentor()
            return

        # If eligible, cat should get a mentor.
        if new_mentor:
            self.__remove_mentor()
            self.__add_mentor(new_mentor)

        # Check if current mentor is valid
        if self.mentor:
            mentor_cat = Cat.fetch_cat(self.mentor)  # This will return None if there is no current mentor
            if not self.is_valid_med_mentor(mentor_cat):
                self.__remove_mentor()

        # Need to pick a random mentor if not specified
        if not self.mentor:
            potential_mentors = []
            priority_mentors = []
            for cat in self.all_cats.values():
                if self.is_valid_med_mentor(cat):
                    potential_mentors.append(cat)
                    if not cat.apprentice:  # length of list is 0
                        priority_mentors.append(cat)
            # First try for a cat who currently has no apprentices
            if priority_mentors:  # length of list > 0
                new_mentor = choice(priority_mentors)
            elif potential_mentors:  # length of list > 0
                new_mentor = choice(potential_mentors)
            if new_mentor:
                self.__add_mentor(new_mentor.ID)

    def __remove_mentor(self):
        """Should only be called by update_mentor, also sets fields on mentor."""
        if not self.mentor:
            return
        mentor_cat = Cat.fetch_cat(self.mentor)
        if self.ID in mentor_cat.apprentice:
            mentor_cat.apprentice.remove(self.ID)
        if self.moons > 6 and self.ID not in mentor_cat.former_apprentices:
            mentor_cat.former_apprentices.append(self.ID)
        if self.moons > 6 and mentor_cat.ID not in self.former_mentor:
            self.former_mentor.append(mentor_cat.ID)
        self.mentor = None

    def __add_mentor(self, new_mentor_id: str):
        """Should only be called by update_mentor, also sets fields on mentor."""
        # reset patrol number
        self.patrol_with_mentor = 0
        self.mentor = new_mentor_id
        mentor_cat = Cat.fetch_cat(self.mentor)
        if self.ID not in mentor_cat.apprentice:
            mentor_cat.apprentice.append(self.ID)

    def update_mentor(self, new_mentor: Any = None):
        """Takes mentor's ID as argument, mentor could just be set via this function."""
        # No !!
        if isinstance(new_mentor, Cat):
            print("Everything is terrible!! (new_mentor {new_mentor} is a Cat D:)")
            return
        # Check if cat can have a mentor
        illegible_for_mentor = self.dead or self.outside or self.exiled or self.status not in ["apprentice",
                                                                                               "mediator apprentice"]
        if illegible_for_mentor:
            self.__remove_mentor()
            return
        # If eligible, cat should get a mentor.
        if new_mentor:
            self.__remove_mentor()
            self.__add_mentor(new_mentor)

        # Check if current mentor is valid
        if self.mentor:
            mentor_cat = Cat.fetch_cat(self.mentor)  # This will return None if there is no current mentor
            if not self.is_valid_mentor(mentor_cat):
                self.__remove_mentor()

        # Need to pick a random mentor if not specified
        if not self.mentor:
            potential_mentors = []
            priority_mentors = []
            for cat in self.all_cats.values():
                if self.is_valid_mentor(cat) and not cat.not_working():
                    potential_mentors.append(cat)
                    if not cat.apprentice:  # length of list is 0
                        priority_mentors.append(cat)
            # First try for a cat who currently has no apprentices
            if priority_mentors:  # length of list > 0
                new_mentor = choice(priority_mentors)
            elif potential_mentors:  # length of list > 0
                new_mentor = choice(potential_mentors)
            if new_mentor:
                self.__add_mentor(new_mentor.ID)

    # ---------------------------------------------------------------------------- #
    #                                 relationships                                #
    # ---------------------------------------------------------------------------- #
    def is_potential_mate(self,
                          other_cat: Cat,
                          for_love_interest: bool = False,
                          for_patrol: bool = False):
        """Add aditional information to call the check."""
        former_mentor_setting = game.settings['romantic with former mentor']
        for_patrol = for_patrol
        return self._intern_potential_mate(other_cat, for_love_interest, former_mentor_setting, for_patrol)

    def _intern_potential_mate(self,
                               other_cat: Cat,
                               for_love_interest: bool,
                               former_mentor_setting: bool,
                               for_patrol: bool = False):
        """Checks if this cat is a free and potential mate for the other cat."""
        # checks if affairs are turned on

        affair = False
        if game.settings['affair']:
            affair = True

        # just to be sure, check if it is not the same cat
        if self.ID == other_cat.ID:
            return False

        # check exiled, outside, and dead cats
        if self.dead or self.outside or other_cat.dead or other_cat.outside:
            return False

        # check for age
        if (self.moons < 14 or other_cat.moons < 14) and not for_love_interest:
            return False

        age_restricted_ages = ["kitten", "adolescent"]
        if self.age in age_restricted_ages or other_cat.age in age_restricted_ages:
            if self.age != other_cat.age:
                return False

        # check for current mate
        # if the cat has a mate, they are not open for a new mate
        if for_patrol:
            if self.mate or other_cat.mate:
                if not for_love_interest:
                    return False
                elif not affair:
                    return False
                else:
                    return True
        else:
            if self.mate or other_cat.mate and not for_love_interest:
                return False

        # check for mentor
        is_former_mentor = (other_cat.ID in self.former_apprentices or self.ID in other_cat.former_apprentices)
        if is_former_mentor and not former_mentor_setting:
            return False

        # Relationship checks
        # Apparently, parent2 can't exist without parent1, so we only need to check parent1
        if self.parent1 or other_cat.parent1:
            # Check for relation via other_cat's parents (parent/grandparent)
            if other_cat.parent1:
                if self.is_grandparent(other_cat) or self.is_parent(other_cat):
                    return False
                # Check for uncle/aunt via self's sibs & other's parents
                if self.siblings:
                    if self.is_uncle_aunt(other_cat):
                        return False
                # Check for sibs via self's parents and other_cat's parents
                if self.parent1:
                    if self.is_sibling(other_cat) or other_cat.is_sibling(self):
                        return False

            # Check for relation via self's parents (parent/grandparent)
            if self.parent1:
                if other_cat.is_grandparent(self) or other_cat.is_parent(self):
                    return False
                # Check for uncle/aunt via other_cat's sibs & self's parents
                if other_cat.siblings:
                    if other_cat.is_uncle_aunt(self):
                        return False

            # Only need to check one.
            if not game.settings['first_cousin_mates']:
                if self.is_cousin(other_cat):
                    return False

        else:
            if self.is_sibling(other_cat) or other_cat.is_sibling(self):
                return False

        if abs(self.moons - other_cat.moons) > 40:
            return False

        return True

    def unset_mate(self, breakup: bool = False, fight: bool = False):
        """Unset the mate."""
        if self.mate is None:
            return

        if self.mate in self.relationships:
            relation = self.relationships[self.mate]
            relation.mates = False
            if breakup:
                relation.romantic_love -= 40
                relation.comfortable -= 20
                relation.trust -= 10
                if fight:
                    relation.platonic_like -= 30
        else:
            mate = self.all_cats.get(self.mate)
            if mate:
                self.relationships[self.mate] = Relationship(self, mate)

        self.mate = None

    def set_mate(self, other_cat: Cat):
        """Assigns other_cat as mate to self."""
        self.mate = other_cat.ID
        other_cat.mate = self.ID

        if other_cat.ID in self.relationships:
            cat_relationship = self.relationships[other_cat.ID]
            cat_relationship.romantic_love += 20
            cat_relationship.comfortable += 20
            cat_relationship.trust += 10
        else:
            self.relationships[other_cat.ID] = Relationship(self, other_cat, True)

    def create_one_relationship(self, other_cat: Cat):
        """Create a new relationship between current cat and other cat. Returns: Relationship"""
        relationship = Relationship(self, other_cat)
        self.relationships[other_cat.ID] = relationship
        return relationship

    def create_all_relationships(self):
        """Create Relationships to all current Clancats."""
        for id in self.all_cats:
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
                self.relationships[the_cat.ID] = rel

    def save_relationship_of_cat(self):
        # save relationships for each cat
        clanname = None
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
        for r in self.relationships.values():
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
                json_string = ujson.dumps(rel, indent=4)
                rel_file.write(json_string)
        except:
            print(f"WARNING: Saving relationship of cat #{self} didn't work.")

    def load_relationship_of_cat(self):
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        else:
            clanname = game.switches['clan_list'][0]

        relation_directory = 'saves/' + clanname + '/relationships/'
        relation_cat_directory = relation_directory + self.ID + '_relations.json'

        self.relationships = {}
        if os.path.exists(relation_directory):
            if not os.path.exists(relation_cat_directory):
                self.create_all_relationships()
                for cat in Cat.all_cats.values():
                    cat.relationships[self.ID] = Relationship(cat, self)
                return
            try:
                with open(relation_cat_directory, 'r') as read_file:
                    rel_data = ujson.loads(read_file.read())
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
                            log=rel['log'])
                        self.relationships[rel['cat_to_id']] = new_rel
            except:
                print(f'WARNING: There was an error reading the relationship file of cat #{self}.')

    @staticmethod
    def mediate_relationship(mediator, cat1, cat2, allow_romantic, sabotage=False):
        # Gather some important info

        # Gathering the relationships.
        if cat1.ID in cat2.relationships:
            rel1 = cat1.relationships[cat2.ID]
        else:
            rel1 = cat1.create_one_relationship(cat2)

        if cat2.ID in cat1.relationships:
            rel2 = cat2.relationships[cat1.ID]
        else:
            rel2 = cat2.create_one_relationship(cat1)

        # Are they mates?
        if rel1.cat_to.mate == rel1.cat_from.ID:
            mates = True
        else:
            mates = False

        # Relation Checking
        direct_related = cat1.is_sibling(cat2) or cat1.is_parent(cat2) or cat2.is_parent(cat1)
        indirect_related = cat1.is_uncle_aunt(cat2) or \
                           cat2.is_uncle_aunt(cat1)
        if not game.settings["first_cousin_mates"]:
            indirect_related = indirect_related or cat1.is_cousin(cat2)
        related = direct_related or indirect_related

        # Check for both adults, or same age type:
        if cat1.age == cat2.age or (cat1.age not in ['kitten', 'adolescent'] and
                                    cat2.age not in ['kitten', 'adolescent']):
            valid_age = True
        else:
            valid_age = False

        # Small check to prevent huge age gaps. Will be bypassed if the cats are already mates.
        if abs(cat1.moons - cat2.moons) > 85:
            age_diff = False
        else:
            age_diff = True

        # Output string.
        output = ""

        # Determine the chance of failure.
        if mediator.experience_level == "very low":
            # Negative bonus for very low.
            chance = 20
        elif mediator.experience_level == "low":
            chance = 35
        elif mediator.experience_level == "high":
            chance = 55
        elif mediator.experience_level == "master":
            chance = 70
        elif mediator.experience_level == "max":
            chance = 100
        else:
            chance = 40  # Average gets no bonus.

        compat = get_personality_compatibility(cat1, cat2)
        if compat is True:
            chance += 10
        elif compat is False:
            chance -= 5

        # Cat's compatablity with mediator also has an effect on success chance.
        for cat in [cat1, cat2]:
            if get_personality_compatibility(cat, mediator) is True:
                chance += 5
            elif get_personality_compatibility(cat, mediator) is False:
                chance -= 5

        # Determine chance to fail, turing sabotage into mediate and mediate into sabotage
        if not int(random.random() * chance):
            apply_bonus = False
            if sabotage:
                output += "Sabotage Failed!\n"
                sabotage = False
            else:
                output += "Mediate Failed!\n"
                sabotage = True
        else:
            apply_bonus = True
            # EX gain on success
            EX_gain = randint(5, 12)

            gm_modifier = 1
            if game.clan.game_mode == 'expanded':
                gm_modifier = 3
            elif game.clan.game_mode == 'cruel season':
                gm_modifier = 6

            if mediator.experience_level == "average":
                lvl_modifier = 1.25
            elif mediator.experience_level == "high":
                lvl_modifier = 1.75
            elif mediator.experience_level == "master":
                lvl_modifier = 2
            else:
                lvl_modifier = 1
            mediator.experience += EX_gain / lvl_modifier / gm_modifier

        no_romantic_mentor = False
        if not game.settings['romantic with former mentor']:
            if cat2.ID in cat1.former_apprentices or cat1.ID in cat2.former_apprentices:
                no_romantic_mentor = True

        # determine the traits to effect
        pos_traits = ["platonic", "respect", "comfortable", "trust"]
        if allow_romantic and (mates or (valid_age and not related and age_diff and not no_romantic_mentor)):
            pos_traits.append("romantic")

        neg_traits = ["dislike", "jealousy"]

        # Determine the number of positive traits to effect, and choose the traits
        chosen_pos = sample(pos_traits, k=randint(2, len(pos_traits)))

        # Determine netative trains effected
        neg_traits = sample(neg_traits, k=randint(1, 2))

        if compat is True:
            personality_bonus = 2
        elif compat is False:
            personality_bonus = -2
        else:
            personality_bonus = 0

        # Effects on traits
        for trait in chosen_pos + neg_traits:

            # The EX bonus in not applied upon a fail.
            if apply_bonus:
                if mediator.experience_level == "very low":
                    # Negative bonus for very low.
                    bonus = randint(-2, -1)
                elif mediator.experience_level == "low":
                    bonus = randint(-2, 0)
                elif mediator.experience_level == "high":
                    bonus = randint(1, 3)
                elif mediator.experience_level == "master":
                    bonus = randint(3, 4)
                elif mediator.experience_level == "max":
                    bonus = randint(4, 5)
                else:
                    bonus = 0  # Average gets no bonus.
            else:
                bonus = 0

            if trait == "romantic":
                if mates:
                    ran = (5, 10)
                else:
                    ran = (4, 6)

                if sabotage:
                    rel1.romantic_love = Cat.effect_relation(rel1.romantic_love, -(randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    rel2.romantic_love = Cat.effect_relation(rel1.romantic_love, -(randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    output += f"Romantic interest decreased. "
                else:
                    rel1.romantic_love = Cat.effect_relation(rel1.romantic_love, (randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    rel2.romantic_love = Cat.effect_relation(rel2.romantic_love, (randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    output += f"Romantic interest increased. "

            elif trait == "platonic":
                ran = (4, 6)

                if sabotage:
                    rel1.platonic_like = Cat.effect_relation(rel1.platonic_like, -(randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    rel2.platonic_like = Cat.effect_relation(rel2.platonic_like, -(randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    output += f"Platonic like decreased. "
                else:
                    rel1.platonic_like = Cat.effect_relation(rel1.platonic_like, (randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    rel2.platonic_like = Cat.effect_relation(rel2.platonic_like, (randint(ran[0], ran[1]) + bonus) +
                                                             personality_bonus)
                    output += f"Platonic like increased. "

            elif trait == "respect":
                ran = (4, 6)

                if sabotage:
                    rel1.admiration = Cat.effect_relation(rel1.admiration, -(randint(ran[0], ran[1]) + bonus) +
                                                          personality_bonus)
                    rel2.admiration = Cat.effect_relation(rel2.admiration, -(randint(ran[0], ran[1]) + bonus) +
                                                          personality_bonus)
                    output += f"Respect decreased. "
                else:
                    rel1.admiration = Cat.effect_relation(rel1.admiration, (randint(ran[0], ran[1]) + bonus) +
                                                          personality_bonus)
                    rel2.admiration = Cat.effect_relation(rel2.admiration, (randint(ran[0], ran[1]) + bonus) +
                                                          personality_bonus)
                    output += f"Respect increased. "

            elif trait == "comfortable":
                ran = (4, 6)

                if sabotage:
                    rel1.comfortable = Cat.effect_relation(rel1.comfortable, -(randint(ran[0], ran[1]) + bonus) +
                                                           personality_bonus)
                    rel2.comfortable = Cat.effect_relation(rel2.comfortable, -(randint(ran[0], ran[1]) + bonus) +
                                                           personality_bonus)
                    output += f"Comfort decreased. "
                else:
                    rel1.comfortable = Cat.effect_relation(rel1.comfortable, (randint(ran[0], ran[1]) + bonus) +
                                                           personality_bonus)
                    rel2.comfortable = Cat.effect_relation(rel2.comfortable, (randint(ran[0], ran[1]) + bonus) +
                                                           personality_bonus)
                    output += f"Comfort increased. "

            elif trait == "trust":
                ran = (4, 6)

                if sabotage:
                    rel1.trust = Cat.effect_relation(rel1.trust, -(randint(ran[0], ran[1]) + bonus) +
                                                     personality_bonus)
                    rel2.trust = Cat.effect_relation(rel2.trust, -(randint(ran[0], ran[1]) + bonus) +
                                                     personality_bonus)
                    output += f"Trust decreased. "
                else:
                    rel1.trust = Cat.effect_relation(rel1.trust, (randint(ran[0], ran[1]) + bonus) +
                                                     personality_bonus)
                    rel2.trust = Cat.effect_relation(rel2.trust, (randint(ran[0], ran[1]) + bonus) +
                                                     personality_bonus)
                    output += f"Trust increased. "

            elif trait == "dislike":
                ran = (4, 9)
                if sabotage:
                    rel1.dislike = Cat.effect_relation(rel1.dislike, (randint(ran[0], ran[1]) + bonus) -
                                                       personality_bonus)
                    rel2.dislike = Cat.effect_relation(rel2.dislike, (randint(ran[0], ran[1]) + bonus) -
                                                       personality_bonus)
                    output += f"Dislike increased. "
                else:
                    rel1.dislike = Cat.effect_relation(rel1.dislike, -(randint(ran[0], ran[1]) + bonus) -
                                                       personality_bonus)
                    rel2.dislike = Cat.effect_relation(rel2.dislike, -(randint(ran[0], ran[1]) + bonus) -
                                                       personality_bonus)
                    output += f"Dislike decreased. "

            elif trait == "jealousy":
                ran = (4, 6)

                if sabotage:
                    rel1.jealousy = Cat.effect_relation(rel1.jealousy, (randint(ran[0], ran[1]) + bonus) -
                                                        personality_bonus)
                    rel2.jealousy = Cat.effect_relation(rel2.jealousy, (randint(ran[0], ran[1]) + bonus) -
                                                        personality_bonus)
                    output += f"Jealousy increased. "
                else:
                    rel1.jealousy = Cat.effect_relation(rel1.jealousy, -(randint(ran[0], ran[1]) + bonus) -
                                                        personality_bonus)
                    rel2.jealousy = Cat.effect_relation(rel2.jealousy, -(randint(ran[0], ran[1]) + bonus) -
                                                        personality_bonus)
                    output += f"Jealousy decreased . "

        return output

    @staticmethod
    def effect_relation(current_value, effect):
        if effect < 0:
            if abs(effect) >= current_value:
                return 0

        if effect > 0:
            if current_value + effect >= 100:
                return 100

        return current_value + effect

    def set_faded(self):
        """This function is for cats that are faded. It will set the sprite and the faded tag"""
        self.faded = True

        # Sillotette sprite
        if self.age in ['kitten']:
            file_name = "faded_kitten.png"
        elif self.age in ['adult', 'young adult', 'senior adult']:
            file_name = "faded_adult.png"
        elif self.age in ["adolescent"]:
            file_name = "faded_adol.png"
        else:
            file_name = "faded_elder.png"

        self.sprite = image_cache.load_image(f"sprites/faded/{file_name}").convert_alpha()
        self.big_sprite = pygame.transform.scale(self.sprite, (100, 100))
        self.large_sprite = pygame.transform.scale(self.big_sprite, (150, 150))

    @staticmethod
    def fetch_cat(cat_id: str):
        """Fetches a cat object. Works for both faded and non-faded cats. Returns none if no cat was found. """
        if not cat_id or isinstance(cat_id, Cat):  # Check if argument is None or Cat.
            return cat_id
        elif not isinstance(cat_id, str):  # Invalid type
            return None
        if cat_id in Cat.all_cats:
            return Cat.all_cats[cat_id]
        else:
            ob = Cat.load_faded_cat(cat_id)
            if ob:
                return ob
            else:
                return None

    @staticmethod
    def load_faded_cat(cat: str):
        """Loads a faded cat, returning the cat object. This object is saved nowhere else. """
        try:
            with open('saves/' + game.clan.name + '/faded_cats/' + cat + ".json", 'r') as read_file:
                cat_info = ujson.loads(read_file.read())
        except AttributeError:  # If loading cats is attempted before the clan is loaded, we would need to use this.
            with open('saves/' + game.switches['clan_list'][0] + '/faded_cats/' + cat + ".json", 'r') as read_file:
                cat_info = ujson.loads(read_file.read())
        except:
            print("ERROR: in loading faded cat")
            return False

        cat_ob = Cat(ID=cat_info["ID"], prefix=cat_info["name_prefix"], suffix=cat_info["name_suffix"],
                     status=cat_info["status"], moons=cat_info["moons"], faded=True)
        if cat_info["parent1"]:
            cat_ob.parent1 = cat_info["parent1"]
        if cat_info["parent2"]:
            cat_ob.parent2 = cat_info["parent2"]
        cat_ob.paralyzed = cat_info["paralyzed"]
        cat_ob.faded_offspring = cat_info["faded_offspring"]
        cat_ob.faded = True

        return cat_ob

    # ---------------------------------------------------------------------------- #
    #                                  Sorting                                     #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def sort_cats():
        if game.sort_type == "age":
            Cat.all_cats_list.sort(key=lambda x: Cat.get_adjusted_age(x))
        elif game.sort_type == "reverse_age":
            Cat.all_cats_list.sort(key=lambda x: Cat.get_adjusted_age(x), reverse=True)
        elif game.sort_type == "id":
            Cat.all_cats_list.sort(key=lambda x: int(x.ID))
        elif game.sort_type == "reverse_id":
            Cat.all_cats_list.sort(key=lambda x: int(x.ID), reverse=True)
        elif game.sort_type == "rank":
            Cat.all_cats_list.sort(key=lambda x: (Cat.rank_order(x), Cat.get_adjusted_age(x)), reverse=True)
        return

    @staticmethod
    def insert_cat(c: Cat):
        try:
            if game.sort_type == "age":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: Cat.get_adjusted_age(x))
            elif game.sort_type == "reverse_age":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: -1 * Cat.get_adjusted_age(x))
            elif game.sort_type == "rank":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: (-1 * Cat.rank_order(x), -1 *
                                                                   Cat.get_adjusted_age(x)))
            elif game.sort_type == "id":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: int(x.ID))
            elif game.sort_type == "reverse_id":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: -1 * int(x.ID))
        except (TypeError, NameError):
            # If you are using python 3.8, key is not a supported parameter into insort. Therefore, we'll need to
            # do the slower option of adding the cat, then resorting
            Cat.all_cats_list.append(c)
            Cat.sort_cats()

    @staticmethod
    def rank_order(cat: Cat):
        if cat.status in Cat.rank_sort_order:
            return Cat.rank_sort_order.index(cat.status)
        else:
            return 0

    @staticmethod
    def get_adjusted_age(cat: Cat):
        """Returns the dead_for moons rather than the age for dead cats, so dead cats are sorted by how long
        they have been dead, rather than age at death"""
        if cat.dead:
            return cat.dead_for
        else:
            return cat.moons

    # ---------------------------------------------------------------------------- #
    #                                  properties                                  #
    # ---------------------------------------------------------------------------- #

    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, exp: int):
        if (exp > 100):
            exp = 100
        self._experience = exp
        experience_level = self.experience_level
        experience_levels = [
            'very low', 'low', 'average', 'high', 'master', 'max'
        ]
        if exp < 11:
            experience_level = 'very low'
        elif exp < 31:
            experience_level = 'low'
        elif exp < 70:
            experience_level = 'average'
        elif exp < 81:
            experience_level = 'high'
        elif exp < 100:
            experience_level = 'master'
        elif exp == 100:
            experience_level = 'max'

        self.experience_level = experience_level

    @property
    def moons(self):
        return self._moons

    @moons.setter
    def moons(self, value: int):
        self._moons = value

        updated_age = False
        for key_age in self.age_moons.keys():
            if self._moons in range(self.age_moons[key_age][0], self.age_moons[key_age][1] + 1):
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
    not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 'LEFTBLIND', 'BRIGHTHEART',
                   'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
    for a in range(12):
        if a in e:
            game.choose_cats[a] = Cat(status='warrior')
        else:
            game.choose_cats[a] = Cat(status=choice(
                ['kitten', 'apprentice', 'warrior', 'warrior', 'elder']))
        if game.choose_cats[a].moons >= 160:
            game.choose_cats[a].moons = choice(range(120, 155))
        for scar in game.choose_cats[a].scars:
            if scar in not_allowed:
                game.choose_cats[a].scars.remove(scar)
        update_sprite(game.choose_cats[a])


# CAT CLASS ITEMS
cat_class = Cat(example=True)
game.cat_class = cat_class

# ---------------------------------------------------------------------------- #
#                                load json files                               #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

ILLNESSES = None
with open(f"{resource_directory}illnesses.json", 'r') as read_file:
    ILLNESSES = ujson.loads(read_file.read())

INJURIES = None
with open(f"{resource_directory}injuries.json", 'r') as read_file:
    INJURIES = ujson.loads(read_file.read())

PERMANENT = None
with open(f"{resource_directory}permanent_conditions.json", 'r') as read_file:
    PERMANENT = ujson.loads(read_file.read())


resource_directory = "resources/dicts/events/death/death_reactions/"

MINOR_MAJOR_REACTION = None
with open(f"{resource_directory}minor_major.json", 'r') as read_file:
    MINOR_MAJOR_REACTION = ujson.loads(read_file.read())

