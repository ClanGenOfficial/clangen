from .pelts import *
from .names import *
from .sprites import *
from .game_essentials import *
from random import choice, randint
import math
import os.path


class Cat(object):
    used_screen = screen
    traits = ['strange', 'bloodthirsty', 'ambitious', 'loyal', 'righteous', 'fierce', 'nervous', 'strict',
              'charismatic', 'calm',
              'daring', 'loving', 'playful', 'lonesome', 'cold', 'insecure', 'vengeful',
              'shameless', 'faithful', 'troublesome', 'empathetic']
    kit_traits = ['bouncy', 'bullying', 'daydreamer', 'nervous', 'charming', 'attention-seeker',
                  'inquisitive', 'bossy', 'troublesome', 'quiet', 'daring', 'sweet', 'insecure']
    ages = ['kitten', 'adolescent', 'young adult', 'adult', 'senior adult', 'elder', 'dead']
    age_moons = {'kitten': [0, 5], 'adolescent': [6, 11], 'young adult': [12, 47], 'adult': [48, 95],
                 'senior adult': [96, 119], 'elder': [120, 199]}
    gender_tags = {'female': 'F', 'male': 'M'}
    skills = ['good hunter', 'great hunter', 'fantastic hunter', 'smart', 'very smart', 'extremely smart',
              'good fighter', 'great fighter', 'excellent fighter', 'good speaker', 'great speaker',
              'excellent speaker', 'strong connection to starclan', 'good teacher', 'great teacher',
              'fantastic teacher']

    all_cats = {}  # ID: object

    def __init__(self, prefix=None, gender=None, status="kitten", parent1=None, parent2=None, pelt=None,
                 eye_colour=None, suffix=None, ID=None, moons=None, example=False):
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
        self.mate = None
        self.placement = None
        self.example = example
        self.dead = False
        self.died_by = None  # once the cat dies, tell the cause
        self.dead_for = 0  # moons
        self.thought = ''
        if ID is None:
            self.ID = str(randint(10000, 99999))
        else:
            self.ID = ID
        # personality trait and skill
        if self.status != 'kitten':
            self.trait = choice(self.traits)
            if self.status != 'apprentice' and self.status != 'medicine cat apprentice':
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
                self.age = choice(['young adult', 'adult', 'adult', 'senior adult'])
        if moons is None:
            self.moons = randint(self.age_moons[self.age][0], self.age_moons[self.age][1])
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
                    self.eye_colour = choice([par1.eye_colour, choice(eye_colours)])
                else:
                    par1 = self.all_cats[self.parent1]
                    par2 = self.all_cats[self.parent2]
                    self.eye_colour = choice([par1.eye_colour, par2.eye_colour, choice(eye_colours)])

        # pelt
        if self.pelt is None:
            if self.parent1 is None:
                # If pelt has not been picked manually, this function chooses one based on possible inheritances
                self.pelt = choose_pelt(self.gender)

            elif self.parent2 is None and self.parent1 in self.all_cats.keys():
                # 1 in 3 chance to inherit a single parent's pelt
                par1 = self.all_cats[self.parent1]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, None]),
                                        choice([par1.pelt.white, None]),
                                        choice([par1.pelt.name, None]),
                                        choice([par1.pelt.length, None]))

            elif self.parent1 in self.all_cats.keys() and self.parent2 in self.all_cats.keys():
                # 2 in 3 chance to inherit either parent's pelt
                par1 = self.all_cats[self.parent1]
                par2 = self.all_cats[self.parent2]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, par2.pelt.colour, None]),
                                        choice([par1.pelt.white, par2.pelt.white, None]),
                                        choice([par1.pelt.name, par2.pelt.name, None]),
                                        choice([par1.pelt.length, par2.pelt.length, None]))

        # NAME
        if self.pelt is not None:
            self.name = Name(status, prefix, suffix, self.pelt.colour, self.eye_colour, self.pelt.name)
        else:
            self.name = Name(status, prefix, suffix, eyes=self.eye_colour)

        # SPRITE
        self.age_sprites = {'kitten': randint(0, 2), 'adolescent': randint(3, 5), 'elder': randint(3, 5)}
        self.reverse = choice([True, False])
        self.skin = choice(skin_sprites)

        # scars & more
        scar_choice = randint(0, 15)
        if self.age in ['kitten', 'adolescent']:
            scar_choice = randint(0, 50)
        elif self.age in ['young adult', 'adult']:
            scar_choice = randint(0, 20)
        if scar_choice == 1:
            self.specialty = choice([choice(scars1), choice(scars2)])
        else:
            self.specialty = None

        scar_choice2 = randint(0, 30)
        if self.age in ['kitten', 'adolescent']:
            scar_choice2 = randint(0, 100)
        elif self.age in ['young adult', 'adult']:
            scar_choice2 = randint(0, 40)
        if scar_choice2 == 1:
            self.specialty2 = choice([choice(scars1), choice(scars2)])
        else:
            self.specialty2 = None

        # random event
        if self.pelt is not None:
            if self.pelt.length != 'long':
                self.age_sprites['adult'] = randint(6, 8)
            else:
                self.age_sprites['adult'] = randint(0, 2)
            self.age_sprites['young adult'] = self.age_sprites['adult']
            self.age_sprites['senior adult'] = self.age_sprites['adult']
            self.age_sprites['dead'] = None  # The sprite that the cat has in starclan

            # WHITE PATCHES
            if self.pelt.white and self.pelt.white_patches is not None:
                pelt_choice = randint(0, 10)
                if pelt_choice == 1 and self.pelt.name in ['Calico', 'TwoColour', 'Tabby', 'Speckled'] \
                        and self.pelt.colour != 'WHITE':
                    self.white_patches = choice(['COLOURPOINT', 'COLOURPOINTCREAMY', 'RAGDOLL'])
                elif pelt_choice == 1 and self.pelt.name in ['Calico', 'TwoColour', 'Tabby', 'Speckled']:
                    self.white_patches = choice(['COLOURPOINT', 'RAGDOLL'])
                elif self.pelt.name in ['Tabby', 'Speckled', 'TwoColour'] and self.pelt.colour == 'WHITE':
                    self.white_patches = choice(
                        ['ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
                         'LIGHTSONG', 'VITILIGO'])
                else:
                    self.white_patches = choice(self.pelt.white_patches)
            else:
                self.white_patches = choice(['EXTRA', None, None])

            # pattern for tortie/calico cats
            if self.pelt.name == 'Calico':
                self.pattern = choice(calico_pattern)
            elif self.pelt.name == 'Tortie':
                self.pattern = choice(tortie_pattern)
            else:
                self.pattern = None
        else:
            self.white_patches = None
            self.pattern = None

        # Sprite sizes
        self.sprite = None
        self.big_sprite = None
        self.large_sprite = None

        # experience and current patrol status
        self.experience = 0
        self.in_camp = 1

        experience_levels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high',
                             'master', 'max']
        self.experience_level = experience_levels[math.floor(self.experience / 10)]

        # SAVE CAT INTO ALL_CATS DICTIONARY IN CATS-CLASS
        self.all_cats[self.ID] = self

    def __repr__(self):
        return self.ID

    def one_moon(self):  # Go forward in time one moon
        if game.switches['timeskip']:
            key_copy = tuple(cat_class.all_cats.keys())
            for index, i in enumerate(key_copy):
                cat = cat_class.all_cats[i]
                if not cat.dead:
                    cat.in_camp = 1
                    self.perform_ceremonies(cat)
                    self.gain_scars(cat)
                    self.handle_deaths(cat)
                    # possibly have kits
                    cat.have_kits()
                else:  # if cat was already dead
                    cat.dead_for += 1
            self.thoughts()

            # Age the clan itself
            game.clan.age += 1
            game.clan.current_season = game.clan.seasons[game.clan.age % 12]
            game.event_scroll_ct = 0
            has_med = False
            for cat in cat_class.all_cats.values():
                if str(cat.status) == "medicine cat" or str(cat.status) == "medicine cat apprentice":
                    if not cat.dead:
                        has_med = True
                        break
            if not has_med:
                game.cur_events_list.insert(0, game.clan.name + "Clan has no medicine cat!")
            if game.clan.deputy == 0 or game.clan.deputy is None or game.clan.deputy.dead:
                game.cur_events_list.insert(0, game.clan.name + "Clan has no deputy!")
            if game.clan.leader.dead:
                game.cur_events_list.insert(0, game.clan.name + "Clan has no leader!")
        game.switches['timeskip'] = False

    def perform_ceremonies(self,
                           cat):  # This function is called when apprentice/warrior/other ceremonies are performed every moon
        if game.clan.leader.dead and game.clan.deputy is not None and not game.clan.deputy.dead:
            game.clan.new_leader(game.clan.deputy)
            game.cur_events_list.append(
                str(game.clan.deputy.name) + ' has been promoted to the new leader of the clan')
            game.clan.deputy = None
        if not cat.dead:
            cat.moons += 1
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.moons > self.age_moons[cat.age][1]:
                # Give the cat a new age group, if old enough
                if cat.age != 'elder':
                    cat.age = self.ages[self.ages.index(cat.age) + 1]
                # change the status
                if cat.status == 'kitten' and cat.age == 'adolescent':
                    cat.status_change('apprentice')
                    game.cur_events_list.append(str(cat.name) + ' has started their apprenticeship')
                elif cat.status == 'apprentice' and cat.age == 'young adult':
                    cat.status_change('warrior')
                    cat.update_mentor()
                    game.cur_events_list.append(str(cat.name) + ' has earned their warrior name')
                elif cat.status == 'medicine cat apprentice' and cat.age == 'young adult':
                    cat.status_change('medicine cat')
                    cat.update_mentor()
                    game.cur_events_list.append(str(cat.name) + ' has earned their medicine cat name')
                    game.clan.new_medicine_cat(cat)
                elif cat.status == 'warrior' and cat.age == 'elder':
                    cat.status_change('elder')
                    game.cur_events_list.append(str(cat.name) + ' has retired to the elder den')
                elif cat.status == 'deputy' and cat.age == 'elder':
                    cat.status_change('elder')
                    game.clan.deputy = None
                    game.cur_events_list.append('The deputy ' + str(cat.name) + ' has retired to the elder den')

    def gain_scars(self, cat):
        # gaining scars with age
        if cat.specialty is None and cat.age != 'kitten':
            chance = 0
            if cat.age in ['adolescent', 'young adult']:
                chance = randint(0, 50)
            elif cat.age in ['adult', 'senior adult']:
                chance = randint(0, 70)
            else:
                chance = randint(0, 90)
            if chance == 1:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    game.cur_events_list.append(str(cat.name) + ' lost their tail to a ' + choice(
                        ['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk']))
                else:
                    game.cur_events_list.append(
                        str(cat.name) + ' earned a scar fighting a ' + choice(
                            ['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk']))
            else:
                cat.specialty = None

        elif cat.specialty2 is None and cat.age != 'kitten':
            chance = 0
            if cat.age in ['adolescent', 'young adult']:
                chance = randint(0, 50)
            elif cat.age in ['adult', 'senior adult']:
                chance = randint(0, 70)
            else:
                chance = randint(0, 90)
            if chance == 1:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL':
                    game.cur_events_list.append(str(cat.name) + ' lost their tail to a ' + choice(
                        ['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'tree', 'badger', 'enemy warrior']))
                else:
                    game.cur_events_list.append(str(cat.name) + ' earned a scar fighting a ' + choice(
                        ['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'badger', 'enemy warrior']))
            else:
                cat.specialty2 = None

    def create_interactions(self, cat, index, key_copy):
        if randint(1, 50) == 49:
            # interact with other cat
            append_str = None
            # check if cat is dead
            if randint(1, 4) == 4:
                cat_number = key_copy[randint(0, index)]
            else:
                cat_number = key_copy[index - randint(1, index)]

            if self.all_cats[cat_number].dead:
                if randint(1, 4) == 4:
                    append_str = str(cat.name) + ' mourns the loss of ' + str(
                        self.all_cats[cat_number].name)
            elif cat_number == cat.ID:
                append_str = str(cat.name) + ' thinks they are going crazy.'
            else:
                # all other interactions here
                event_choice = randint(1, 6)
                if event_choice == 1:
                    if cat.specialty is None:
                        if cat.age in ['adolescent', 'young adult']:
                            i = randint(0, 1)
                        elif cat.age in ['adult', 'senior adult']:
                            i = randint(0, 2)
                        else:
                            i = randint(0, 10)
                        if i == 1:
                            cat.specialty = choice([choice(scars1), choice(scars2)])
                            if cat.age in ['kitten']:
                                append_str = str(cat.name) + ' is injured when they sneak out of camp'
                            else:
                                if randint(1, 3) == 3 and (
                                        cat.status == 'warrior' or cat.status == 'deputy'):
                                    append_str = str(
                                        cat.name) + ' retires the elder den after injuries sustained defending ' + str(
                                        self.all_cats[cat_number].name)
                                    cat.status_change('elder')
                                else:
                                    append_str = str(cat.name) + ' earned a scar defending ' + str(
                                        self.all_cats[cat_number].name) + ' from a ' + choice(
                                        ['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk'])
                        else:
                            cat.specialty = None
                            append_str = str(cat.name) + ' tried to convince ' + str(
                                self.all_cats[cat_number].name) + ' to run away together.'
                    elif cat.status != 'kitten':
                        cat.specialty = None
                        append_str = str(cat.name) + ' tried to convince ' + str(
                            self.all_cats[cat_number].name) + ' to run away together.'
                    elif game.clan.current_season != 'Leaf-bare':
                        cat.specialty = None
                        append_str = str(cat.name) + ' asks ' + str(
                            self.all_cats[cat_number].name) + ' to show them ' + str(
                            game.clan.name) + 'Clan territory.'
                    else:
                        if game.clan.current_season == 'Leaf-bare' and cat.status == 'kitten':
                            cat.dies()
                            append_str = str(cat.name) + '  dies of a chill during a snowstorm.'
                        else:
                            append_str = str(cat.name) + '  feels lost.'

                # defends
                elif event_choice == 2:
                    if cat.status == 'leader':
                        append_str = str(cat.name) + ' confesses to ' + str(self.all_cats[
                                                                                cat_number].name) + ' that the responsibility of leadership is crushing them.'
                    elif game.clan.current_season == 'Leaf-bare' and cat.status == 'kitten':
                        cat.dies()
                        append_str = str(self.all_cats[cat_number].name) + ' finds ' + str(
                            cat.name) + ' dead in the snow.'
                    # sus
                elif event_choice == 3:
                    if cat.mate is not None and randint(1, 3) == 1:
                        append_str = str(cat.name) + ' is killed by ' + str(
                            self.all_cats[cat_number].name) + ' in an argument over ' + str(
                            self.all_cats[cat.mate].name)
                        cat.dies()
                    elif cat.mate is not None:
                        append_str = str(cat.name) + ' breaks up with ' + str(
                            self.all_cats[cat.mate].name)
                        self.all_cats[cat.mate].mate = None
                        cat.mate = None
                    else:
                        valid_mates = 0
                        if not self.all_cats[cat_number].dead and self.all_cats[cat_number].age in [
                            'young adult', 'adult', 'senior adult', 'elder'] and \
                                cat != self.all_cats[cat_number] and cat.ID not in [
                            self.all_cats[cat_number].parent1, self.all_cats[cat_number].parent2] and \
                                self.all_cats[cat_number].ID not in [cat.parent1, cat.parent2] and \
                                self.all_cats[cat_number].mate is None and \
                                (self.all_cats[cat_number].parent1 is None or self.all_cats[
                                    cat_number].parent1 not in [cat.parent1, cat.parent2]) and \
                                (self.all_cats[cat_number].parent2 is None or self.all_cats[
                                    cat_number].parent2 not in [cat.parent1, cat.parent2]):

                            # Making sure the ages are appropriate
                            if (cat.age in ['senior adult', 'elder'] and self.all_cats[cat_number].age in [
                                'senior adult', 'elder']) or (self.all_cats[
                                                                  cat_number].age != 'elder' and cat.age != 'elder' and cat.age != 'kitten' and cat.age != 'adolescent'):
                                valid_mates = 1

                        if self.all_cats[cat_number].ID == cat.ID:
                            valid_mates = 0

                        if valid_mates:
                            cat.mate = self.all_cats[cat_number].ID
                            self.all_cats[cat_number].mate = cat.ID
                            append_str = str(cat.name) + ' and ' + str(
                                self.all_cats[cat_number].name) + ' have become mates.'

                        else:
                            append_str = str(cat.name) + ' talks with ' + str(
                                self.all_cats[cat_number].name) + ' about love.'

                    # angry mate
                elif event_choice == 4:
                    # training
                    if cat.status == 'apprentice':
                        append_str = str(cat.name) + ' trains with their mentor, ' + str(cat.mentor.name)
                    elif cat.age in ['adolescent', 'young adult', 'adult', 'senior adult']:
                        append_str = str(cat.name) + ' learns some new moves from ' + str(
                            self.all_cats[cat_number].name)
                    else:
                        append_str = str(cat.name) + ' sneaks out of the camp with ' + str(
                            self.all_cats[cat_number].name)

                elif event_choice == 5:

                    # if cat has mate adopts kit, otherwise two invite in new cat
                    if randint(1, 4) < 4 and cat.status != 'kitten':
                        kit = Cat(moons=0)
                        game.clan.add_cat(kit)
                        append_str = str(cat.name) + ' adopts an abandoned kit named ' + str(kit.name)
                    else:
                        kit = Cat(status='warrior', moons=14)
                        game.clan.add_cat(kit)
                        append_str = str(cat.name) + ' invites the loner ' + choice(
                            names.loner_names) + ' to join. They change their name to' + str(kit.name) + ''
                        kit.skill = 'formerly a loner'

                elif event_choice == 6:
                    append_str = str(cat.name) + ' and ' + str(
                        self.all_cats[cat_number].name) + ' die of a contagious disease'
                    cat.dies()
                    self.all_cats[cat_number].dies()
                else:
                    append_str = str(cat.name) + ' interacted with ' + str(
                        self.all_cats[cat_number].name)

            if game.cur_events_list is not None and append_str is not None and append_str != '':
                game.cur_events_list.append(append_str)
            else:
                game.cur_events_list = [append_str]

    def handle_deaths(self, cat):
        if randint(1, 300) == 299:
            if randint(1, 4) == 4:
                cat.dies()
                if game.cur_events_list is not None:
                    game.cur_events_list.append(
                        str(cat.name) + ' was murdered at ' + str(cat.moons) + ' moons old')
            elif randint(1, 3) == 3:
                cat.dies()
                if game.cur_events_list is not None:
                    game.cur_events_list.append(
                        str(cat.name) + ' died of a disease at ' + str(cat.moons) + ' moons old')
            else:
                cat.dies()
                if game.cur_events_list is not None:
                    game.cur_events_list.append(
                        str(cat.name) + ' died in an accident at ' + str(cat.moons) + ' moons old')

        if cat.moons > randint(150, 200):  # Cat dies of old age
            if choice([1, 2, 3, 4, 5, 6]) == 1:
                cat.dies()
                if game.cur_events_list is not None:
                    game.cur_events_list.append(
                        str(cat.name) + ' has passed away at ' + str(cat.moons) + ' moons old')

    def dies(self):  # This function is called every time a cat dies
        self.dead = True
        self.update_mentor()
        for app in self.apprentice:
            app.update_mentor()
        game.clan.add_to_starclan(self)

    def have_kits(self):
        # decide chances of having kits, and if it's possible at all
        chance = 0
        if self.mate is not None:
            if self.mate in self.all_cats:
                if self.all_cats[self.mate].dead:
                    chance = 0
                elif self.all_cats[self.mate].gender != self.gender and self.all_cats[
                    self.mate].age != 'elder':
                    chance = 25
                elif game.settings['no gendered breeding'] and self.all_cats[
                    self.mate].age != 'elder' and chance is not None:
                    chance = 25
                else:
                    chance = 0
            else:
                game.cur_events_list.append(
                    "Warning: " + str(self.name) + " has an invalid mate #" + str(self.mate) + ". This has been unset.")
                self.mate = None
        else:
            chance = 50
            if not game.settings['no unknown fathers']:
                chance = 0

        if self.age in ['kitten', 'adolescent', 'elder'] or self.example or \
                (not game.settings['no gendered breeding'] and self.gender == 'male'):
            chance = 0

        # Decide randomly if kits will be born, if possible
        if chance != 0:
            hit = randint(0, chance)
            if len(game.clan.clan_cats) > 30:
                hit = randint(0, chance + 20)
            elif len(game.clan.clan_cats) < 10:
                hit = randint(0, chance - 10)
            kits = choice([1, 1, 2, 2, 3, 3, 4])
            if hit == 1 and self.mate is not None:
                if game.cur_events_list is not None:
                    game.cur_events_list.append(str(self.name) + ' had a litter of ' + str(kits) + ' kit(s)')
                else:
                    game.cur_events_list = [str(self.name) + ' had a litter of ' + str(kits) + ' kit(s)']

                for kit in range(kits):
                    kit = Cat(parent1=self.ID, parent2=self.mate, moons=0)
                    game.clan.add_cat(kit)
            elif hit == 1:
                game.cur_events_list.append(str(self.name) + ' had a litter of ' + str(kits) + ' kit(s)')

                for kit in range(kits):
                    kit = Cat(parent1=self.ID, moons=0)
                    game.clan.add_cat(kit)

    def thoughts(self):
        # actions or thoughts for all cats. These switch either every moon or every time the game is re-opened

        for c in self.all_cats.keys():
            other_cat = random.choice(list(self.all_cats.keys()))
            while other_cat == c:
                other_cat = random.choice(list(self.all_cats.keys()))
            other_cat = self.all_cats.get(other_cat)
            other_name = str(other_cat.name)
            cat = self.all_cats.get(c)
            thought = 'Is not thinking about much right now'  # placeholder thought - should never appear in game
            if cat.dead:
                # individual thoughts
                starclan_thoughts = ['Is feeling quite lazy', 'Is spending a considerable amount of time grooming',
                                     'Is looking forward to today', 'Is feeling down...',
                                     'Is feeling happy!', 'Is curious about other clans', 'Is feeling sassy today',
                                     "Is thinking about a message to send", "Wishes they were still alive",
                                     "Is admiring StarClan territory", "Is thinking about their life",
                                     "Is missing a loved one",
                                     "Is hoping to meet with a medicine cat soon", "Is admiring the stars in their fur",
                                     "Is watching over a clan ceremony", "Is hoping to give a life to a new leader",
                                     "Is hoping they will be remembered", "Is watching over the clan",
                                     "Is worried about the clan",
                                     "Is relaxing in the sun", "Is wondering about twolegs",
                                     "Is thinking about their ancient ancestors",
                                     "Is worried about the cats in the Dark Forest",
                                     "Is thinking of advice to give to a medicine cat"]
                if other_cat.dead:
                    starclan_thoughts.extend([  # thoughts with other cats that are dead
                        'Is sharing tongues with ' + other_name,
                        'Has been spending time with ' + other_name + ' lately',
                        'Is acting huffy at ' + other_name,
                        'Is sharing a freshkill with ' + other_name,
                        'Is curious about ' + other_name,
                        'Is talking with ' + other_name,
                        'Doesn\'t want to talk to ' + other_name,
                        'Is having a serious fight with ' + other_name,
                        'Wants to spend more time with ' + other_name + '!',
                        'Is thinking about future prophecies with ' + other_name,
                        'Is watching over the clan with ' + other_name])
                elif not other_cat.dead:
                    starclan_thoughts.extend([  # thoughts with other cats that are alive
                        'Is watching over ' + other_name,
                        'Is curious about what ' + other_name + ' is doing'
                                                                'Wants to send a message to ' + other_name,
                        'Is currently walking in the dreams of ' + other_name,
                        'Is proud of ' + other_name,
                        'Is disappointed in ' + other_name,
                        'Wants to warn ' + other_name,
                        'Has been following the growth of ' + other_name])
                if cat.status in ['kitten', 'apprentice', 'medicine cat apprentice']:  # dead young cat thoughts
                    starclan_thoughts.extend(['Wishes they had more time to grow up',
                                              'Wonders what their full name would have been',
                                              'Is bothering older StarClan cats',
                                              'Is learning about the other cats in StarClan'])
                elif cat.status == 'elder':  # dead elder thoughts
                    starclan_thoughts.extend(['Is grateful that they lived such a long life',
                                              'Is happy that their joints no longer ache',
                                              'Is telling stories to the younger cats of StarClan',
                                              'Watches over the younger cats of StarClan', ])
                elif cat.status == 'leader':  # dead leader thoughts
                    starclan_thoughts.extend(['Hoped that they were a good leader,'
                                              'Wishes that they had ten lives',
                                              'Is proud of their clan from StarClan', ])
                thought = choice(starclan_thoughts)  # sets current thought to a random applicable thought
            elif not cat.dead:
                # general individual thoughts
                thoughts = ['Is feeling quite lazy', 'Is spending a considerable amount of time grooming',
                            'Is looking forward to today', 'Is feeling down...', 'Is feeling excited',
                            'Is feeling nervous', 'Is feeling content', "Is relaxing in camp", 'Is daydreaming',
                            'Is napping', 'Thinks they are going crazy', 'Is feeling gloomy', "Is looking around camp",
                            'Is feeling happy!', 'Is curious about the other clans', 'Is feeling sassy today',
                            'Wants to spend time alone today', "Is eating some freshkill",
                            'Is heading to the dirtplace', 'Is rethinking their life choices',
                            'Is visiting the medicine den', 'Is having a good day', 'Is having a hard day',
                            'Is talking to themselves', 'Regrets not eating the bird on the freshkill pile earlier']
                if other_cat.dead:  # thoughts with other cats who are dead
                    if cat.status in ['kitten', 'apprentice',
                                      'medicine cat apprentice']:  # young cat thoughts about dead cat
                        thoughts.extend(['Is listening to stories about ' + other_name,
                                         'Is learning more about ' + other_name,
                                         'Is sad they couldn\'t spend time with ' + other_name])
                    elif cat.status in ['warrior', 'medicine cat', 'deputy',
                                        'leader']:  # older cat thoughts about dead cat
                        thoughts.extend(['Is listening to stories about ' + other_name,
                                         'Is learning more about ' + other_name,
                                         'Is sad they couldn\'t spend more time with ' + other_name,
                                         'Wishes they could visit ' + other_name + ' in StarClan',
                                         'Is remembering ' + other_name])
                    if cat.status == 'elder':  # elder thoughts about dead cat
                        thoughts.extend(['Is telling stories about ' + other_name,
                                         'Is sad they couldn\'t spend more time with ' + other_name,
                                         'Wishes they could visit ' + other_name + ' in StarClan',
                                         'Is remembering ' + other_name,
                                         'Wishes that ' + other_name + ' were still alive',
                                         'Found a trinket that used to belong to ' + other_name,
                                         'Is forgetting who ' + other_name + ' was',
                                         'Is thinking fondly of ' + other_name])
                    if cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice' or cat.skill == 'strong connection to starclan':  # medicine cat/strong connection thoughts about dead cat
                        thoughts.extend(['Was given a prophecy by ' + other_name,
                                         'Was sent an omen by ' + other_name,
                                         'Is dreaming about ' + other_name + ' who gives them a message',
                                         'Is visited by ' + other_name,
                                         'Senses ' + other_name + ' is nearby',
                                         'Saw ' + other_name + ' in a dream, warning them about... something',
                                         'Is asking for guidance from ' + other_name])
                elif not other_cat.dead:  # thoughts with other cat who is alive
                    if cat.status in ['warrior', 'elder', 'deputy',
                                      'leader'] and other_cat.status == 'apprentice':  # older cat thoughts about younger cat
                        thoughts.extend(['Is giving ' + other_name + ' advice',
                                         'Is telling ' + other_name + ' about a hunting technique',
                                         'Is scolding ' + other_name,
                                         'Is giving ' + other_name + ' a task'])
                    if cat.status == 'kitten':  # kit thoughts
                        if other_cat.status == 'kitten':  # kit thoughts with other kit
                            thoughts.extend(['Pretends to be a warrior with ' + other_name,
                                             'Plays mossball with ' + other_name,
                                             'Has a mock battle with ' + other_name,
                                             'Comes up with a plan to sneak out of camp with ' + other_cat,
                                             'Whines about ' + other_cat])
                        elif other_cat.status != 'kitten':  # kit thoughts about older cat
                            thoughts.extend(
                                ['Is biting ' + other_name + '\'s tail', 'Sticks their tongue out at ' + other_name,
                                 'Whines to ' + other_name])
                    elif cat.status in ['apprentice', 'medicine cat apprentice', 'warrior', 'medicine cat', 'deputy',
                                        'leader']:
                        if other_cat.status == 'kitten':  # older cat thoughts about kit
                            thoughts.extend(['Trips over ' + other_name, 'Is giving advice to ' + other_name])
                        else:
                            thoughts.extend(['Is fighting with ' + other_name, 'Is talking with ' + other_name,
                                             'Is sharing prey with ' + other_name, 'Heard a rumor about ' + other_name])
                    if cat.age == other_cat.age:
                        thoughts.extend(
                            ['Is developing a crush on ' + other_name, 'Is spending a lot of time with ' + other_name])
                if cat.status == 'kitten':
                    thoughts.extend(['Plays mossball by themselves', 'Is annoying older cats',
                                     'Wonders what their full name will be', 'Pretends to be a warrior',
                                     'Is becoming interested in herbs', 'Tries to sneak out of camp',
                                     'Is rolling around on the ground', 'Is chasing their tail',
                                     'Is playing with a stick', 'Is nervous for their apprentice ceremony',
                                     'Is excited for their apprentice ceremony', 'Wonders who their mentor will be',
                                     "Practices the hunting crouch", 'Pretends to fight an enemy warrior',
                                     'Wants to take a nap', 'Is scared after having a nightmare',
                                     'Thinks they saw a StarClan cat in their dreams', 'Wants to snuggle',
                                     'Wishes other cats would stop babying them', 'Is hiding from other cats',
                                     'Is bouncing around in excitement', 'Whines about being hungry'])
                elif cat.status == 'apprentice':
                    thoughts.extend(
                        ['Is thinking about the time they caught a huge rabbit', 'Wonders what their full name will be',
                         'Is irritating their mentor',
                         'Is arguing with their mentor', 'Is listening to their mentor',
                         'Plans to visit the elders soon', "Practices the hunting crouch",
                         'Pretends to fight an enemy warrior', 'Practices some battle moves',
                         'Is becoming interested in herbs', 'Volunteers for the dawn patrol',
                         'Volunteers to gather herbs', 'Hopes they will do battle training soon',
                         'Is pulling a prank on the warriors', 'Can\'t wait to be a warrior',
                         'Is wondering if they are good enough to become a warrior', 'Is gathering moss',
                         'Doesn\'t want to become a warrior yet', 'Is gossiping', 'Is acting angsty'])
                elif cat.status == 'medicine cat apprentice':
                    thoughts.extend(
                        ['Is struggling to remember all of the names of herbs', 'Is counting the poppy seeds',
                         'Is helping organize the herb stores', 'Wonders what their full name will be',
                         'Plans to help the elders with their ticks', 'Is looking forward to the half-moon meeting',
                         'Is wondering if they are good enough to become a medicine cat',
                         'Helps apply a poultice to a small wound', 'Is making new nests',
                         'Is proud of their ability to care for their clanmates'])
                elif cat.status == 'medicine cat':
                    thoughts.extend(
                        ['Is looking for herbs', 'Is organizing the herb stores', 'Is drying some herbs',
                         'Is counting the poppy seeds', 'Is gathering cobwebs', 'Is interpreting an omen',
                         'Is interpreting a prophecy', 'Hopes for a message from StarClan soon',
                         'Is checking up on the warriors', 'Is feeling stressed taking care of the clan',
                         'Is thinking about taking on a new apprentice',
                         'Is wondering if they could borrow some catmint from the other clans',
                         'Is looking forward to the half-moon meeting', 'Is wrapping a wound with cobwebs',
                         'Is clearing out old herbs', 'Is gathering death berries',
                         'Is proud of their ability to care for their clanmates', 'Chased kits out of their den'])
                elif cat.status == 'warrior':
                    thoughts.extend(
                        ['Caught scent of a fox earlier', 'Caught scent of an enemy warrior earlier',
                         'Is helping gathering herbs', 'Is thinking about love', 'Is decorating their nest',
                         'Is reinforcing the camp with brambles', 'Wants to be chosen as the new deputy',
                         'Caught a huge rabbit', 'Is dreaming about being leader', 'Is acting suspicious',
                         'Tries to set a good example for younger cats', 'Wants to go on a patrol',
                         'Wants to go on a hunting patrol', 'Is hoping to lead the next patrol',
                         'Is guarding the camp entrance', 'Is thinking about kits', 'Is watching over the kits',
                         'Is gossiping', 'Plans to visit the medicine cat'])
                elif cat.status == 'deputy':
                    thoughts.extend(
                        ['Is assigning cats to a border patrol', 'Is assigning cats to a hunting patrol',
                         'Is wondering what it would be like to be a leader', 'Is spending time alone',
                         'Tries to set a good example for younger cats', 'Is thinking about kits',
                         'Is stressed about organizing patrols', "Wonders who will give them nine lives"])
                elif cat.status == 'leader':
                    thoughts.extend(
                        ['Is hoping for a sign from StarClan', 'Is hoping that they are leading their clan well',
                         'Thinks about who should mentor new apprentices', 'Is worried about clan relations',
                         'Is spending time alone', 'Tries to set a good example for the deputy',
                         'Is thinking about forming an alliance',
                         'Is debating if they should declare a war with another clan', 'Is assessing some apprentices',
                         'Is thinking about battle stategies', 'Almost lost a life recently',
                         'Is counting how many lives they have left'])
                elif cat.status == 'elder':
                    thoughts.extend(
                        ['Is complaining about their nest being too rough', 'Is complaining about their aching joints',
                         'Is telling stories about when they were young', 'Is giving advice to younger cats',
                         'Is complaining about thorns in their nest', 'Is bossing around the younger cats',
                         'Is telling scary stories to the younger cats', 'Is snoring in their sleep',
                         'Thinking about how too many cats die young', 'Is complaining about being cold',
                         'Is grateful they have lived so long', 'Is sharing their wisdom'])
                cat.thought = choice(thoughts)

                # on_patrol = ['Is having a good time out on patrol', 'Wants to return to camp to see ' + other_name,
                #              'Is currently out on patrol', 'Is getting rained on during their patrol',
                #              'Is out hunting'] //will add later
                # interact_with_loner = ['Wants to know where ' + other_name + ' came from.'] // will add

    def status_change(self, new_status):
        # revealing of traits and skills
        if self.status == 'kitten':
            a = randint(0, 50)
            if a == 1:
                self.trait = 'strange'
            elif a == 2:
                self.trait = 'bloodthirsty'
            else:
                self.trait = choice(self.traits)
        if (self.status == 'apprentice' and new_status != 'medicine cat apprentice') or (
                self.status == 'medicine cat apprentice' and new_status != 'apprentice'):
            self.skill = choice(self.skills)

        self.status = new_status
        self.name.status = new_status
        if 'apprentice' in new_status:
            self.update_mentor()
        # update class dictionary
        self.all_cats[self.ID] = self

    def is_valid_mentor(self, potential_mentor):
        # Dead cats can't be mentors
        if potential_mentor.dead:
            return False
        # Match jobs
        if self.status == 'medicine cat apprentice' and potential_mentor.status != 'medicine cat':
            return False
        if self.status == 'apprentice' and potential_mentor.status not in ['leader', 'deputy', 'warrior']:
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
        if 'apprentice' in self.status and not self.dead:
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
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, None]),
                                        choice([par1.pelt.white, None]),
                                        choice([par1.pelt.name, None]),
                                        choice([par1.pelt.length, None]))

            elif self.parent1 in self.all_cats.keys() and self.parent2 in self.all_cats.keys():
                # 2 in 3 chance to inherit either parent's pelt
                par1 = self.all_cats[self.parent1]
                par2 = self.all_cats[self.parent2]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, par2.pelt.colour, None]),
                                        choice([par1.pelt.white, par2.pelt.white, None]),
                                        choice([par1.pelt.name, par2.pelt.name, None]),
                                        choice([par1.pelt.length, par2.pelt.length, None]))
            else:
                self.pelt = choose_pelt(self.gender)

        # THE SPRITE UPDATE
        # draw colour & style
        new_sprite = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)

        if self.pelt.name not in ['Tortie', 'Calico']:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                                  'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites[self.pelt.sprites[1] + 'extra' + self.pelt.colour + str(
                        self.age_sprites[self.age])], (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites[self.pelt.sprites[1] + self.pelt.colour + str(self.age_sprites[self.age])],
                    (0, 0))
        else:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                                  'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites[self.pelt.sprites[1] + 'extra' + self.pattern + str(
                        self.age_sprites[self.age])], (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites[self.pelt.sprites[1] + self.pattern + str(self.age_sprites[self.age])],
                    (0, 0))

        # draw white patches
        if self.white_patches is not None:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                                  'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['whiteextra' + self.white_patches + str(self.age_sprites[self.age])],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['white' + self.white_patches + str(self.age_sprites[self.age])], (0, 0))

        # draw eyes & scars1
        if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                              'medicine cat apprentice'] or self.age == 'elder':
            if self.specialty in scars1:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars1:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
            new_sprite.blit(sprites.sprites['eyesextra' + self.eye_colour + str(self.age_sprites[self.age])],
                            (0, 0))
        else:
            if self.specialty in scars1:
                new_sprite.blit(sprites.sprites['scars' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars1:
                new_sprite.blit(sprites.sprites['scars' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
            new_sprite.blit(sprites.sprites['eyes' + self.eye_colour + str(self.age_sprites[self.age])], (0, 0))

        # draw line art
        if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                              'medicine cat apprentice'] or self.age == 'elder':
            new_sprite.blit(sprites.sprites['lines' + str(self.age_sprites[self.age] + 9)], (0, 0))
        else:
            new_sprite.blit(sprites.sprites['lines' + str(self.age_sprites[self.age])], (0, 0))

        # draw skin and scars2 and scars3
        if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                              'medicine cat apprentice'] or self.age == 'elder':
            new_sprite.blit(sprites.sprites['skinextra' + self.skin + str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars2:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars2:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty in scars3:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars3:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
        else:
            new_sprite.blit(sprites.sprites['skin' + self.skin + str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars2:
                new_sprite.blit(sprites.sprites['scars' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars2:
                new_sprite.blit(sprites.sprites['scars' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty in scars3:
                new_sprite.blit(sprites.sprites['scars' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars3:
                new_sprite.blit(sprites.sprites['scars' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))

        # reverse, if assigned so
        if self.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

        # apply
        self.sprite = new_sprite
        self.big_sprite = pygame.transform.scale(new_sprite, (sprites.new_size, sprites.new_size))
        self.large_sprite = pygame.transform.scale(self.big_sprite, (sprites.size * 3, sprites.size * 3))

        # update class dictionary
        self.all_cats[self.ID] = self

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

    def save_cats(self):
        data = ''
        for x in self.all_cats.values():
            # cat ID -- name prefix : name suffix
            data += x.ID + ',' + x.name.prefix + ':' + x.name.suffix + ','
            # cat gender -- status -- age -- trait
            data += x.gender + ',' + x.status + ',' + str(x.age) + ',' + x.trait + ','
            # cat parent1 -- parent2 -- mentor
            if x.parent1 is None:
                data += 'None ,'
            else:
                data += x.parent1 + ','
            if x.parent2 is None:
                data += 'None ,'
            else:
                data += x.parent2 + ','
            if x.mentor is None:
                data += 'None ,'
            else:
                data += x.mentor.ID + ','

            # pelt type -- colour -- white -- length
            data += x.pelt.name + ',' + x.pelt.colour + ',' + str(x.pelt.white) + ',' + x.pelt.length + ','
            # sprite kitten -- adolescent
            data += str(x.age_sprites['kitten']) + ',' + str(x.age_sprites['adolescent']) + ','
            # sprite adult -- elder
            data += str(x.age_sprites['adult']) + ',' + str(x.age_sprites['elder']) + ','
            # eye colour -- reverse -- white patches -- pattern
            data += x.eye_colour + ',' + str(x.reverse) + ',' + str(x.white_patches) + ',' + str(x.pattern) + ','
            # skin -- skill -- NONE  -- specs  -- moons
            data += x.skin + ',' + x.skill + ',' + 'None' + ',' + str(x.specialty) + ',' + str(x.moons) + ','
            # mate -- dead  -- dead sprite
            data += str(x.mate) + ',' + str(x.dead) + ',' + str(x.age_sprites['dead'])

            # scar 2
            data += ',' + str(x.specialty2)
            # experience
            data += ',' + str(x.experience)
            # dead_for x moons
            data += ',' + str(x.dead_for)
            # apprentice
            if x.apprentice:
                data += ','
                for cat in x.apprentice:
                    data += str(cat.ID) + ';'
                # remove last semicolon
                data = data[:-1]
            else:
                data += ',' + 'None'
            # former apprentice
            if x.former_apprentices:
                data += ','
                for cat in x.former_apprentices:
                    data += str(cat.ID) + ';'
                # remove last semicolon
                data = data[:-1]
            else:
                data += ',' + 'None'
            # next cat
            data += '\n'

        # remove one last unnecessary new line
        data = data[:-1]

        if game.switches['naming_text'] != '':
            clanname = game.switches['naming_text']
        elif game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        else:
            clanname = game.switches['clan_list'][0]
        with open('saves/' + clanname + 'cats.csv', 'w') as write_file:
            write_file.write(data)

    def load_cats(self):
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

                    the_pelt = choose_pelt(attr[2], attr[10], attr[11], attr[9], attr[12], True)
                    the_cat = Cat(ID=attr[0], prefix=attr[1].split(':')[0], suffix=attr[1].split(':')[1],
                                  gender=attr[2],
                                  status=attr[3], pelt=the_pelt, parent1=attr[6], parent2=attr[7], eye_colour=attr[17])
                    the_cat.age, the_cat.mentor = attr[4], attr[8]
                    the_cat.age_sprites['kitten'], the_cat.age_sprites['adolescent'] = int(attr[13]), int(attr[14])
                    the_cat.age_sprites['adult'], the_cat.age_sprites['elder'] = int(attr[15]), int(attr[16])
                    the_cat.age_sprites['young adult'], the_cat.age_sprites['senior adult'] = int(attr[15]), int(
                        attr[15])
                    the_cat.reverse, the_cat.white_patches, the_cat.pattern = attr[18], attr[19], attr[20]
                    the_cat.trait, the_cat.skin, the_cat.specialty = attr[5], attr[21], attr[24]

                    if len(attr) > 29:
                        the_cat.specialty2 = attr[29]
                    else:
                        the_cat.specialty2 = None

                    if len(attr) > 30:
                        the_cat.experience = int(attr[30])
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high',
                                            'very high', 'master', 'max']
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

            for n in self.all_cats.values():
                # Load the mentors and apprentices after all cats have been loaded
                n.mentor = cat_class.all_cats.get(n.mentor)
                apps = []
                former_apps = []
                for app_id in n.apprentice:
                    app = cat_class.all_cats.get(app_id)
                    # Make sure if cat isn't an apprentice, they're a former apprentice
                    if 'apprentice' in app.status:
                        apps.append(app)
                    else:
                        former_apps.append(app)
                for f_app_id in n.former_apprentices:
                    f_app = cat_class.all_cats.get(f_app_id)
                    former_apps.append(f_app)
                n.apprentice = apps
                n.former_apprentices = former_apps
                n.update_sprite()

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
        if self.pelt.name == 'SingleColour' or self.pelt.name == 'TwoColour':
            color_name = str(self.pelt.colour).lower()
        elif self.pelt.name == "Tabby":
            color_name = str(self.pelt.colour).lower() + ' tabby'
        elif self.pelt.name == "Speckled":
            color_name = str(self.pelt.colour).lower() + ' speckled'
        elif self.pelt.name == "Tortie" or self.pelt.name == "Calico":
            color_name = 'tortie'  # check for calico or for white later

        # not enough to comment on
        if self.white_patches is None or self.white_patches in ['EXTRA']:
            color_name = color_name  # what is this even lol
        # enough to comment but not make calico
        elif self.white_patches in ['LITTLE', 'LITTLECREAMY', 'LIGHTTUXEDO', 'BUZZARDFANG']:
            color_name = color_name + ' and white'
        # and white
        elif self.white_patches in ['ANY', 'TUXEDO', 'ANY2', 'ANYCREAMY', 'TUXEDOCREAMY', 'ANY2CREAMY', 'BROKEN']:
            if color_name == 'tortie':
                color_name = 'calico'
            else:
                color_name = color_name + ' and white'
        # white and
        elif self.white_patches in ['VAN', 'VANCREAMY', 'ONEEAR', 'LIGHTSONG']:
            color_name = 'white and ' + color_name
        # colorpoint
        elif self.white_patches in ['COLOURPOINT', 'RAGDOLL', 'COLOURPOINTCREAMY']:
            color_name = color_name + ' point'
            if color_name == 'darkginger point':
                color_name = 'flame point'
        # vitiligo
        elif self.white_patches in ['VITILIGO']:
            color_name = color_name + ' with vitiligo'
        else:
            color_name = color_name + ' color error'

        if color_name == 'tortie':
            color_name = 'tortoiseshell'

        if color_name == 'white and white':
            color = name = 'white'

        return color_name

    def describe_cat(self):
        if self.gender == 'male':
            sex = 'tom'
        else:
            sex = 'she-cat'
        description = self.describe_color()
        description += ' ' + str(self.pelt.length).lower() + '-furred ' + sex
        return description


# CAT CLASS ITEMS
cat_class = Cat(example=True)
game.cat_class = cat_class

# The randomized cat sprite in Main Menu screen
example_cat = Cat(status=choice(["kitten", "apprentice", "warrior", "elder"]), example=True)
example_cat.update_sprite()


# Twelve example cats
def example_cats():
    e = random.sample(range(12), 2)
    for a in range(12):
        if a in e:
            game.choose_cats[a] = Cat(status='warrior')
        else:
            game.choose_cats[a] = Cat(status=choice(['kitten', 'apprentice', 'warrior', 'warrior', 'elder']))
        game.choose_cats[a].update_sprite()
