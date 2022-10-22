from .cats import *
from .buttons import *
from .relation_events import * 

class Events(object):
    all_events = {}

    def __init__(self, e_type=None, **cats):
        self.e_type = e_type
        self.ID = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(
            0, 9)) + str(randint(0, 9))
        if e_type is not None:
            self.all_events[self.ID] = self
        self.cats = cats
        self.at_war = False
        self.time_at_war = False
        self.enemy_clan = None
        self.living_cats = 0
        self.new_cat_invited = False
        self.ceremony_accessory = False
        game.switches['pregnancy'] = False
        game.switches['birth_cooldown'] = False
        if game.switches['birth_cooldown']:
            birth_range = randint(6, 9)

    def one_moon(self):
        if game.switches['timeskip']:
            game.switches['saved_clan'] = False
            self.living_cats = 0
            self.new_cat_invited = False
            game.patrolled.clear()
            for cat in cat_class.all_cats.copy().values():
                if not cat.dead and not cat.exiled:
                    self._extracted_from_one_moon_7(cat)
                elif cat.exiled:
                    cat.moons += 1
                    if cat.moons == 6:
                        cat.age = 'adolescent'
                    elif cat.moons == 12:
                        cat.age = 'adult'
                    elif cat.moons == 100:
                        cat.age = 'elder'
                    if cat.moons > randint(100, 200):
                        if choice([1, 2, 3, 4, 5]) == 1 and cat.dead == False:
                            cat.dead = True
                            game.cur_events_list.append(f'Rumors reach your clan that the exiled {str(cat.name)} has died recently')

                    if cat.exiled and cat.status == 'leader' and cat.dead == False and randint(
                            1, 10) == 1:
                        game.clan.leader_lives -= 1
                        if game.clan.leader_lives <= 0:
                            cat.dead = True
                            game.cur_events_list.append(f'Rumors reach your clan that the exiled {str(cat.name)} has died recently')

                            game.clan.leader_lives = 0
                    elif cat.exiled and cat.status == 'leader' and cat.dead == False and randint(
                            1, 45) == 1:
                        game.clan.leader_lives -= 10
                        cat.dead = True
                        game.cur_events_list.append(f'Rumors reach your clan that the exiled {str(cat.name)} has died recently')

                        game.clan.leader_lives = 0
                else:
                    cat.dead_for += 1

            # interaction here so every cat may have got a new name
            relation_events = Relation_Events()
            cat_list = list(cat_class.all_cats.copy().values())
            random.shuffle(cat_list)
            for cat in cat_list:
                if not cat.dead and not cat.exiled:
                    relation_events.create_interaction(cat)
                    relation_events.handle_relationships(cat)
                    relation_events.check_if_having_kits(cat)
                    #relation_events.have_kits(cat)
            cat_class.thoughts()
            self.check_clan_relations()
            game.clan.age += 1
            if game.settings.get(
                    'autosave') is True and game.clan.age % 5 == 0:
                cat_class.json_save_cats()
                game.clan.save_clan()
            game.clan.current_season = game.clan.seasons[game.clan.age % 12]
            game.event_scroll_ct = 0
            has_med = any(
                str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                and not cat.dead and not cat.exiled
                for cat in cat_class.all_cats.values())

            if not has_med:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no medicine cat!")
            if game.clan.deputy == 0 or game.clan.deputy is None or game.clan.deputy.dead or game.clan.deputy.exiled:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no deputy!")
            if game.clan.leader.dead or game.clan.leader.exiled:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no leader!")
            if game.switches['birth_cooldown']:
                birth_range -= 1

        game.switches['timeskip'] = False

    # TODO Rename this here and in `one_moon`
    def _extracted_from_one_moon_7(self, cat):
        self.living_cats += 1
        cat.in_camp = 1
        self.check_age(cat)
        self.perform_ceremonies(cat)
        if self.new_cat_invited == False or self.living_cats < 10:
            self.invite_new_cats(cat)
        self.other_interactions(cat)
        self.gain_accessories(cat)
        self.gain_scars(cat)
        self.handle_deaths(cat)

    def check_clan_relations(self):
        if len(game.clan.all_clans) > 0 and randint(1, 5) == 1:
            war_notice = ''
            for other_clan in game.clan.all_clans:
                if int(other_clan.relations) <= 5:
                    if randint(1, 5) == 1 and self.time_at_war > 2:
                        self.at_war = False
                        self.time_at_war = 0
                        other_clan.relations = 10
                        game.cur_events_list.append('The war against ' +
                                                    str(other_clan.name) +
                                                    'Clan has ended')
                    elif self.time_at_war == 0:
                        game.cur_events_list.append('The war against ' +
                                                    str(other_clan.name) +
                                                    'Clan has begun')
                        self.time_at_war += 1
                    else:
                        self.enemy_clan = f'{str(other_clan.name)}Clan'
                        possible_text = [
                            f'War rages between {game.clan.name}Clan and {other_clan.name}Clan',
                            f'{other_clan.name}Clan has taken some of {game.clan.name}'
                            + "Clan\'s territory",
                            f'{game.clan.name}Clan has claimed some of {other_clan.name}'
                            + "Clan\'s territory",
                            f'{other_clan.name}Clan attempted to break into your camp during the war',
                            f'The war against {other_clan.name}Clan continues',
                            f'{game.clan.name}Clan is starting to get tired of the war against {other_clan.name}Clan',
                            f'{game.clan.name}Clan warriors plan new battle strategies for the war',
                            f'{game.clan.name}Clan warriors reinforce the camp walls'
                        ]
                        if game.clan.medicine_cat is not None:
                            possible_text.extend([
                                'The medicine cats worry about having enough herbs to treat their clan\'s wounds'
                            ])
                        war_notice = choice(possible_text)
                        self.time_at_war += 1
                    break
                elif int(other_clan.relations) > 30:
                    other_clan.relations = 10
                else:
                    self.at_war = False
                    r_num = choice([-1, 1])
                    other_clan.relations = str(
                        int(other_clan.relations) + r_num)
            if war_notice:
                game.cur_events_list.append(war_notice)

    def perform_ceremonies(self, cat):
        if (game.clan.leader.dead or game.clan.leader.exiled
            ) and game.clan.deputy is not None and not game.clan.deputy.dead:
            if game.clan.leader.exiled:
                game.cur_events_list.append(
                    str(game.clan.leader.name) + ' was exiled')
            else:
                game.cur_events_list.append(
                    str(game.clan.leader.name) +
                    ' has lost their last life and has travelled to StarClan')
            game.clan.new_leader(game.clan.deputy)
            game.clan.leader_lives = 9
            game.cur_events_list.append(
                f'{str(game.clan.deputy.name)} has been promoted to the new leader of the clan'
            )
            self.ceremony_accessory = True
            self.gain_accessories(cat)
            game.clan.deputy = None
        if not cat.dead:
            cat.moons += 1
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.moons > cat_class.age_moons[cat.age][1]:
                if cat.age != 'elder':
                    cat.age = cat_class.ages[cat_class.ages.index(cat.age) + 1]
                if cat.status == 'kitten' and cat.age == 'adolescent':
                    cat.status_change('apprentice')
                    game.cur_events_list.append(
                        f'{str(cat.name)} has started their apprenticeship')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)
                    cat.update_mentor()
                elif cat.status == 'apprentice' and cat.age == 'young adult':
                    self._extracted_from_perform_ceremonies_19(
                        cat, 'warrior', ' has earned their warrior name')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)
                elif cat.status == 'medicine cat apprentice' and cat.age == 'young adult':
                    self._extracted_from_perform_ceremonies_19(
                        cat, 'medicine cat',
                        ' has earned their medicine cat name')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)
                    game.clan.new_medicine_cat(cat)
                elif cat.status == 'deputy' and cat.age == 'elder' and len(
                        cat.apprentice) < 1:
                    cat.status_change('elder')
                    game.clan.deputy = None
                    game.cur_events_list.append(
                        f'The deputy {str(cat.name)} has retired to the elder den'
                    )
                elif cat.status == 'warrior' and cat.age == 'elder' and len(
                        cat.apprentice) < 1:
                    cat.status_change('elder')
                    game.cur_events_list.append(
                        f'{str(cat.name)} has retired to the elder den')
            if cat.status in [
                    'warrior', 'deputy'
            ] and cat.age == 'elder' and len(cat.apprentice) < 1:
                cat.status_change('elder')
                if str(cat.status) == 'deputy':
                    game.clan.deputy = None
                game.cur_events_list.append(
                    f'{str(cat.name)} has retired to the elder den')

    # TODO Rename this here and in `perform_ceremonies`
    def _extracted_from_perform_ceremonies_19(self, cat, arg1, arg2):
        cat.status_change(arg1)
        cat.update_mentor()
        game.cur_events_list.append(f'{str(cat.name)}{arg2}')

    def gain_accessories(self, cat):
        if cat.accessory is not None:
            return
        name = str(cat.name)
        other_cat = choice(list(cat_class.all_cats.values()))
        countdown = int(len(cat_class.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(cat_class.all_cats.values()))
            countdown-=1
            if countdown <= 0:
                return
        other_name = str(other_cat.name)
        acc_text = []
        chance = randint(0, 50)
        if cat.age in ['kitten', 'adolescent']:
            chance = randint(0, 70)
        elif cat.age in ['young adult', 'adult', 'senior adult', 'elder']:
            chance = randint(0, 150)
        elif cat.trait in ['childish', 'lonesome', 'loving', 'playful', 'shameless', 'strange', 'troublesome']:
            chance = randint(0, 40)
        elif cat.status in ['medicine cat', 'medicine cat apprentice']:
            chance = randint(0, 30)
        if chance == 1:
            if cat.accessory is None:
                cat.accessory = choice([
                    choice(plant_accessories),
                    choice(wild_accessories)
                ])
                accessory = cat.accessory
                #if self.ceremony_accessory == True:
                 #   acc_text.extend([f'{other_name} gives {name} something to adorn their pelt as congratulations', f'{name} decides to pick something to adorn their pelt as celebration'])
                if cat.age != 'kitten':
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        if game.clan.current_season == 'Leaf-bare':
                            acc_text.append(f'{name} found a mysterious flower growing in the {choice(["snow", "ice", "frost"])} and decided to wear it')
                        else:
                            acc_text.extend([f'{name} received a flower from {other_name} and decided to wear it on their pelt',
                                            f'{name} found a pretty flower and decided to wear it on their pelt', f'A clanmate gave {name} a flower and they decided to wear it'
                            ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"] and cat.specialty != "NOTAIL" and cat.specialty2 != "NOTAIL":
                        acc_text.append(f'{name} found a bunch of pretty feathers and decided to wear them')
                    elif cat.accessory in ["HERBS", "PETALS", "DRY_HERBS"]:
                        acc_text.append(f'{name} always seems to have something stuck in their fur')
                    elif cat.accessory in plant_accessories and cat.status in ['medicine cat apprentice', 'medicine cat']:
                        acc_text.extend([f'{name} has decided to always bring their {accessory.lower()} with them',
                                        f'{accessory.lower()} - an item so important to {name} that they always carry it around'.capitalize,
                                        f'{accessory.lower()} - so vital for {name} that they always have it on them'.capitalize
                        ])
                    else:
                        acc_text.extend([f'{name} finds something interesting and decides to wear it on their pelt', f'A clanmate gives {name} a pretty accessory and they decide to wear it on their pelt',
                                        f'{name} finds something interesting while out on a walk and decides to wear it on their pelt', f'{name} finds {accessory.lower()} fascinating and decides to wear it on their pelt',
                                        f'A clanmate gives {name} something to adorn their pelt as a gift', f'{other_name} gives {name} a pretty accessory and they decide to wear it on their pelt'
                        ])
                else:
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        acc_text.extend([f'{name} received a flower from {other_name} and decided to wear it on their pelt',
                                            f'{name} found a pretty flower and decided to wear it on their pelt', f'A clanmate gave {name} a flower and they decided to wear it'
                            ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"] and cat.specialty != "NOTAIL" and cat.specialty2 != "NOTAIL":
                        acc_text.append(f'{name} was playing with feathers earlier and decided to wear some of them')
                    elif cat.accessory in ["HERBS", "PETALS", "DRYHERBS"]:
                        acc_text.append(f'{name}\'s parents try their best to groom them, but something is always stuck in their fur')
                    else:    
                        acc_text.extend([f'{name} seems to have picked something up while playing out in the camp', f'{name} finds something interesting and decides to wear it on their pelt',
                                        f'A clanmate gives {name} a pretty accessory and they decide to wear it on their pelt', f'{other_name} gives {name} a pretty accessory and they decide to wear it on their pelt',
                                        f'{name} is so cute that they are given {accessory.lower()} as a gift', f'{name} starts to wear {accessory.lower()} on their pelt after their friend gave it to them',
                                        f'{name} was playing with {accessory.lower()} earlier and has decided to use it to adorn themselves'
                        ])
        if acc_text:
            game.cur_events_list.append(choice(acc_text))
            if self.ceremony_accessory:
                self.ceremony_accessory = False   

    def gain_scars(self, cat):
        if cat.specialty is not None and cat.specialty2 is not None or cat.age == 'kitten':
            return
        name = str(cat.name)
        other_cat = choice(list(cat_class.all_cats.values()))
        scar_chance = randint(0, 40)
        clancats = int(self.living_cats)
        countdown = int(len(cat_class.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(cat_class.all_cats.values()))
            countdown-=1
            if countdown <= 0:
                return
        other_name = str(other_cat.name)
        scar_text = []
        clan_has_kits = any(
                str(cat.status) in "kitten"
                and not cat.dead and not cat.exiled
                for cat in cat_class.all_cats.values())
        if clancats > 45:
            scar_chance = scar_chance + 20
        elif clancats > 120:
            scar_chance = scar_chance * 2
        elif clancats > 300:
            scar_chance = scar_chance + 80
        else:
            scar_chance = scar_chance
        if cat.age in ['adolescent', 'young adult']:
            chance = scar_chance
        elif cat.age in ['adult', 'senior adult']:
            chance = scar_chance + 10
        elif cat.age in [
                'apprentice', 'medicine cat apprentice'
        ] and cat.mentor.ID == other_cat.ID and other_cat.trait in [
                'bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'cold',
                'tough', 'clumsy', 'controlling', 'fierce', 'petty', 'strict'
        ]:
            chance = scar_chance - 15
        elif other_cat.status in ['leader', 'deputy'] and other_cat.trait in [
                'bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'cold',
                'tough', 'clumsy', 'controlling', 'fierce', 'petty', 'strict'
        ]:
            chance = scar_chance
        else:
            chance = scar_chance
        if chance == 1:
            if cat.specialty is None:
                cat.specialty = choice([
                    choice(scars1),
                    choice(scars2),
                    choice(scars4),
                    choice(scars5)
                ])
                if cat.specialty == 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]))
                elif cat.specialty == 'SNAKE':
                    scar_text.append(f'{name} was bit by a snake but lived')
                elif cat.specialty == 'TOETRAP':
                    scar_text.append(
                        f'{name} got their paw stuck in a twoleg trap and earned a scar'
                    )
                else:
                    scar_text.extend([
                        f'{name} earned a scar fighting a ' + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]), f'{name} earned a scar defending the territory',
                        f'{name} earned a scar protecting the kits',
                        f'{name} is injured after falling into a river',
                        f'{name} is injured by enemy warriors after accidentally wandering over the border',
                        f'{name} is injured after messing with a twoleg object'
                    ])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([
                    choice(scars1),
                    choice(scars2),
                    choice(scars4),
                    choice(scars5)
                ])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None


                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]))
                elif cat.specialty2 == 'SNAKE' and cat.specialty != 'SNAKE':
                    scar_text.append(f'{name} was bit by a snake but lived')
                elif cat.specialty2 == 'TOETRAP' and cat.specialty != 'TOETRAP':
                    scar_text.append(
                        f'{name} got their paw stuck in a twoleg trap and earned a scar'
                    )
                else:
                    if clan_has_kits == True:
                        scar_text.extend([
                        f'{name} earned a scar protecting the kits'])
                    else:
                        scar_text.extend([
                        f'{name} earned a scar fighting a ' + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]), f'{name} earned a scar defending the territory',
                        f'{name} is injured after falling into a river',
                        f'{name} is injured by enemy warriors after accidentally wandering over the border',
                        f'{name} is injured after messing with a twoleg object',
                        f'{name} is injured after a fight broke out with ' +
                        other_name
                    ])

        elif chance == 1 and cat.status in [
                'apprentice', 'medicine cat apprentice'
        ] and cat.mentor.ID == other_cat.ID and other_cat.trait in [
                'bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'cold',
                'tough', 'clumsy', 'controlling', 'fierce', 'petty', 'strict'
        ]:
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                    scar_text.append(
                        f'{name} recklessly lost their tail to a ' + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger', 'tree', 'twoleg trap'
                        ]) + ' encouraged by their mentor')
                else:
                    if clan_has_kits == True:
                        scar_text.extend([
                        f'{name} earned a scar protecting the kits'])
                    else:
                        scar_text.extend([
                        f'{name} earned a scar  recklessly fighting a ' +
                        choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]) + ' encouraged by their mentor',
                        f'{name} earned a scar for not defending the territory well enough',
                        f'{name} is injured after being pushed into a river',
                        f'{name} is punished by their mentor after accidentally wandering over the border',
                        f'{name} is injured by their mentor after being caught messing with a twoleg object'
                        f'{name} is injured by their mentor while practicing with their claws out',
                        f'{name}\'s mentor punished them for disobeying',
                        f'{name} gained a scar while fighting their mentor',
                        f'{name} is injured while practicing their battle moves with '
                        + other_name,
                        f'{name} is injured after a fight broke out with ' +
                        other_name,
                        f'{name} could not handle their mentor\'s harsh training and got injured as a result',
                        f'{name} could not handle their mentor\'s harsh training and got injured as a result'
                    ])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None


                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]) + ' encouraged by their mentor')
                else:
                    if clan_has_kits == True:
                        scar_text.extend([
                        f'{name} earned a scar protecting the kits'])
                    else:
                        scar_text.extend([
                        f'{name} earned a scar recklessly fighting a ' +
                        choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]) + ' encouraged by their mentor',
                        f'{name} earned a scar for not defending the territory well enough',
                        f'{name} is injured after being pushed into a river',
                        f'{name} is punished by their mentor after accidentally wandering over the border',
                        f'{name} is injured by their mentor after being caught messing with a twoleg object'
                        f'{name} is injured by their mentor while practicing with their claws out',
                        f'{name}\'s mentor punished them for disobeying',
                        f'{name} gained a scar while fighting their mentor',
                        f'{name} is injured while practicing their batle moves with '
                        + other_name,
                        f'{name} is injured after a fight broke out with ' +
                        other_name,
                        f'{name} could not handle their mentor\'s harsh training and got injured as a result'
                    ])

        elif chance == 1 and cat.status in [
                'warrior', 'deputy', 'medicine cat'
        ] and other_cat.status == 'leader':
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]) + ' while following orders')
                else:
                    scar_text.extend([
                        f'While following orders {name} earned a scar fighting a '
                        + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]),
                        f'{name} earned a scar defending the territory from outsiders',
                        f'{name} earned a scar protecting the leader',
                        f'{name} is injured after falling into a river',
                        f'{name} is injured by enemy warriors after being ordered to go over the border',
                        f'{name} is injured after being ordered to check out a twoleg object'
                    ])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None


                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]) + ' while following orders')
                else:
                    scar_text.extend([
                        f'While following orders, {name} earned a scar fighting a '
                        + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]),
                        f'{name} earned a scar defending the territory from outsiders',
                        f'{name} earned a scar protecting the leader',
                        f'{name} is injured after falling into a river',
                        f'{name} is injured by enemy warriors after being ordered to go over the border',
                        f'{name} is injured after being ordered to check out a twoleg object'
                    ])

        elif chance == 1 and other_cat.status == 'leader' and other_cat.trait in [
                'bloodthirsty', 'ambitious', 'vengeful', 'sadistic',
                'controlling', 'fierce', 'petty'
        ]:
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]) + ' while following orders')
                else:
                    scar_text.extend([
                        f'While following orders, {name} earned a scar fighting a '
                        + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]),
                        f'{name} earned a scar defending the territory from outsiders',
                        f'{name} earned a scar protecting the leader',
                        f'{name} is injured after falling into a river',
                        f'{name} is injured by enemy warriors after being ordered to go over the border',
                        f'{name} is injured after being ordered to check out a twoleg object',
                        f'{name} is injured while fighting a clanmate encouraged by '
                        + other_name, f'{name} is injured by ' + other_name +
                        ' for disobeying orders', f'{name} is injured by ' +
                        other_name + ' for speaking out against them',
                        f'{name} is cruelly injured by ' + other_name +
                        ' to make an example out of them'
                    ])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                    scar_text.append(f'{name} lost their tail to a ' + choice([
                        'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                        'enemy warrior', 'badger', 'tree', 'twoleg trap'
                    ]) + ' while following orders')
                else:
                    scar_text.extend([
                        f'While following orders {name} earned a scar fighting a '
                        + choice([
                            'rogue', 'dog', 'fox', 'otter', 'rat', 'hawk',
                            'enemy warrior', 'badger'
                        ]),
                        f'{name} earned a scar defending the territory from outsiders',
                        f'{name} earned a scar protecting the leader',
                        f'{name} is injured after falling into a river',
                        f'{name} is injured by enemy warriors after being ordered to go over the border',
                        f'{name} is injured after being ordered to check out a twoleg object',
                        f'{name} is injured while fighting a clanmate encouraged by '
                        + other_name, f'{name} is injured by ' + other_name +
                        ' for disobeying orders', f'{name} is injured by ' +
                        other_name + ' for speaking out against them',
                        f'{name} is cruelly injured by ' + other_name +
                        ' to make an example out of them'
                    ])

        if scar_text:
            game.cur_events_list.append(choice(scar_text))

    def invite_new_cats(self, cat):
        chance = 100
        if self.living_cats < 10:
            chance = 100
        elif self.living_cats > 50:
            chance = 700
        elif self.living_cats > 30:
            chance = 300
        if randint(1, chance
                   ) == 1 and cat.age != 'kitten' and cat.age != 'adolescent':
            self.new_cat_invited = True
            name = str(cat.name)
            type_of_new_cat = choice([1, 2, 3, 4, 5, 6, 7])
            if type_of_new_cat == 1:
                kit = Cat(moons=0)
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat, kit))
                    relationships.append(Relationship(kit, the_cat))
                kit.relationships = relationships
                game.clan.add_cat(kit)
                kit_text = [
                    f'{name} finds an abandoned kit and names them {str(kit.name)}',
                    f'A loner brings their kit named {str(kit.name.prefix)} to the clan, stating they no longer can care for them'
                ]
                game.cur_events_list.append(choice(kit_text))
                self.check_age(kit)

            elif type_of_new_cat == 2:
                self._extracted_from_invite_new_cats_19(name)

            elif type_of_new_cat == 3:
                loner = Cat(status='warrior', moons=randint(12, 120))
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat, loner))
                    relationships.append(Relationship(loner, the_cat))
                loner.relationships = relationships
                loner.skill = 'formerly a loner'
                game.clan.add_cat(loner)
                loner_text = [
                    f'{name} finds a loner who joins the clan',
                    f'A loner says that they are interested in clan life and joins the clan'
                ]
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append(
                    'The loner changes their name to ' + str(loner.name))
                self.check_age(loner)

            elif type_of_new_cat == 4:
                warrior = Cat(status='warrior', moons=randint(12, 150))
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(
                        the_cat, warrior))
                    relationships.append(Relationship(warrior, the_cat))
                warrior.relationships = relationships
                game.clan.add_cat(warrior)
                warrior_text = []
                if len(game.clan.all_clans) > 0:
                    warrior_text.extend([
                        f'{name} finds a warrior from {str(choice(game.clan.all_clans).name)}Clan named {str(warrior.name)} who asks to join the clan',
                        f'An injured warrior from {str(choice(game.clan.all_clans).name)}Clan asks to join in exchange for healing'
                    ])
                else:
                    warrior_text.extend([
                        f'{name} finds a warrior from a different clan named {str(warrior.name)} who asks to join the clan'
                    ])
                game.cur_events_list.append(choice(warrior_text))
                self.check_age(warrior)

            elif type_of_new_cat == 5:
                self._extracted_from_invite_new_cats_47(name)
            elif type_of_new_cat == 6:
                loner = Cat(status='warrior', moons=randint(12, 120))
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat, loner))
                    relationships.append(Relationship(loner, the_cat))
                loner.relationships = relationships
                self._extracted_from_invite_new_cats_59(loner)
                loner_text = [
                    f'{name} finds a kittypet named {choice(names.loner_names)} who wants to join the clan'
                ]
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append(
                    'The kittypet changes their name to ' + str(loner.name))
                self.check_age(loner)

            elif type_of_new_cat == 7:
                parent1 = cat.name
                kits = choice([1, 1, 2, 2, 2, 3])
                for kit in range(kits):
                    if cat.mate is not None:
                        kit = Cat(parent1=cat.ID, parent2=cat.mate, moons=0)
                        game.clan.add_cat(kit)
                        #create and update relationships
                        relationships = []
                        for cat_id in game.clan.clan_cats:
                            the_cat = cat_class.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if the_cat.ID in [kit.parent1, kit.parent2]:
                                the_cat.relationships.append(
                                    Relationship(the_cat, kit, False, True))
                                relationships.append(
                                    Relationship(kit, the_cat, False, True))
                            else:
                                the_cat.relationships.append(
                                    Relationship(the_cat, kit))
                                relationships.append(Relationship(
                                    kit, the_cat))
                        kit.relationships = relationships
                    else:
                        kit = Cat(parent1=cat.ID, moons=0)
                        #create and update relationships
                        relationships = []
                        for cat_id in game.clan.clan_cats:
                            the_cat = cat_class.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if the_cat.ID == kit.parent1:
                                the_cat.relationships.append(
                                    Relationship(the_cat, kit, False, True))
                                relationships.append(
                                    Relationship(kit, the_cat, False, True))
                            else:
                                the_cat.relationships.append(
                                    Relationship(the_cat, kit))
                                relationships.append(Relationship(
                                    kit, the_cat))
                        kit.relationships = relationships
                        game.clan.add_cat(kit)
                if len(game.clan.all_clans) > 0:
                    Akit_text = ([
                        f'{parent1} finds an abandoned litter and decides to adopt them',
                        f'A loner leaves their litter to the clan. {str(parent1)} decides to adopt them as their own',
                        f'A {str(choice(game.clan.all_clans).name)}Clan queen decides to leave their litter with you. {str(parent1)} takes them as their own'
                    ])
                else:
                    Akit_text = ([
                        f'{parent1} finds an abandoned litter and decides to adopt them as their own',
                        f'A loner leaves their litter to the clan. {str(parent1)} decides to adopt them as their own'
                    ])
                game.cur_events_list.append(choice(Akit_text))
                self.check_age(kit)

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_59(self, loner):
        loner.skill = 'formerly a kittypet'
        if choice([1, 2]) == 1:
            loner.specialty2 = choice(scars3)
        game.clan.add_cat(loner)
        self.check_age(loner)

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_47(self, name):
        loner_name = choice(names.loner_names)
        loner = Cat(prefix=loner_name,
                    gender=choice(['female', 'male']),
                    status='warrior',
                    moons=randint(12, 120),
                    suffix='')
        #create and update relationships
        relationships = []
        for cat_id in game.clan.clan_cats:
            the_cat = cat_class.all_cats.get(cat_id)
            if the_cat.dead or the_cat.exiled:
                continue
            the_cat.relationships.append(Relationship(the_cat, loner))
            relationships.append(Relationship(loner, the_cat))
        loner.relationships = relationships
        self._extracted_from_invite_new_cats_59(loner)
        loner_text = [
            f'{name} finds a kittypet named {str(loner_name)} who wants to join the clan',
            f'A kittypet named {str(loner_name)} stops {name} and asks to join the clan'
        ]
        game.cur_events_list.append(choice(loner_text))
        game.cur_events_list.append(
            str(loner_name) + ' decides to keep their name')

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_19(self, name):
        loner_name = choice(names.loner_names)
        loner = Cat(prefix=loner_name,
                    gender=choice(['female', 'male']),
                    status='warrior',
                    moons=randint(12, 120),
                    suffix='')
        loner.skill = 'formerly a loner'
        #create and update relationships
        relationships = []
        for cat_id in game.clan.clan_cats:
            the_cat = cat_class.all_cats.get(cat_id)
            if the_cat.dead or the_cat.exiled:
                continue
            the_cat.relationships.append(Relationship(the_cat, loner))
            relationships.append(Relationship(loner, the_cat))
        loner.relationships = relationships
        game.clan.add_cat(loner)
        loner_text = [
            f'{name} finds a loner named {str(loner.name)} who joins the clan',
            f'A loner named {str(loner.name)} waits on the border for a patrol, asking to join the clan'
        ]
        game.cur_events_list.append(choice(loner_text))
        game.cur_events_list.append(
            str(loner_name) + ' decides to keep their name')
        self.check_age(loner)

    def other_interactions(self, cat):
        if randint(1, 100) != 1:
            return
        interactions = []
        other_cat = choice(list(cat_class.all_cats.values()))
        countdown = int(len(cat_class.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(cat_class.all_cats.values()))
            countdown-=1
            if countdown <= 0:
                return
        name = str(cat.name)
        other_name = str(other_cat.name)
        if cat.status in ['warrior', 'deputy'] and randint(
                1, 15) == 1 and game.settings.get('retirement') is True:
            game.cur_events_list.append(
                f'{name} retires to the elders den after injuries sustained defending {other_name}'
            )
            if cat.status == 'deputy':
                game.clan.deputy = None

            cat.status_change('elder')
            return
        if cat.status == 'kitten' and other_cat.status != 'kitten':
            interactions.extend([
                f'{name} is scolded after sneaking out of camp',
                f'{name} falls into a river but is saved by {other_name}'
            ])
        elif cat.status in ['apprentice', 'medicine cat apprentice'] and other_cat.status != 'kitten':
            interactions.extend([
                f'{name} is scolded after sneaking out of camp',
                f'{name} falls into a river but is saved by {other_name}',
                name +
                " accidentally trespasses onto another clan\'s territory"
            ])
            if other_cat.status == 'apprentice':
                interactions.append(
                    f'{name} sneaks out of camp with {other_name}')
        elif cat.status == 'warrior':
            interactions.extend([
                name + " is caught outside of the Clan\'s territory",
                f'{name} is caught breaking the Warrior Code',
                f'{name} went missing for a few days',
                f'{name} believes they are a part of the new prophecy'
            ])
        elif cat.status == 'medicine cat':
            interactions.extend([
                f'{name} learns of a new prophecy',
                f'{name} is worried about an outbreak of greencough',
                f'{name} is worried about how low their herb stores has gotten',
                f'{name} visits the other medicine cats'
            ])
        elif cat.status == 'deputy':
            interactions.extend([
                f'{name} thinks about retiring',
                f'{name} travels to the other clans to bring them an important message'
            ])
        elif cat.status == 'leader':
            if game.clan.leader_lives <= 5:
                interactions.extend([
                    f'{name} thinks about retiring',
                    name + " confesses they don\'t have many lives left"
                ])
            if other_cat.status not in [
                    'kitten', 'apprentice', 'medicine cat apprentice'
            ]:
                interactions.append(
                    f'{name} confesses to {other_name} that the responsibility of leadership is crushing them'
                )
            elif other_cat.status == 'apprentice':
                interactions.append(f'{name} assesses {other_name}' +
                                    "\'s progress")
            interactions.extend([
                f'{name} calls a clan meeting to give an important announcement'
            ])
        elif cat.status == 'elder':
            interactions.extend(
                [f'{name} is brought back to camp after wandering off'])
        if cat.age == other_cat.age:
            interactions.extend([
                f'{name} tries to convince {other_name} to run away together'
            ])

        if interactions:
            game.cur_events_list.append(choice(interactions))

    def handle_deaths(self, cat):
        clan_has_kits = any(
                str(cat.status) in "kitten"
                and not cat.dead and not cat.exiled
                for cat in cat_class.all_cats.values())
        #Leader lost a life EVENTS
        if randint(1, 100) == 1:
            name = str(cat.name)
            other_cat = choice(list(cat_class.all_cats.values()))
            countdown = int(len(cat_class.all_cats) / 3)
            while cat == other_cat or other_cat.dead or other_cat.status == 'leader' or other_cat.exiled:
                other_cat = choice(list(cat_class.all_cats.values()))
                countdown-=1
                if countdown <= 0:
                    return
            if cat.status == 'leader':
                other_name = str(other_cat.name)
                cause_of_death = [
                    name + ' lost a life after falling into a river',
                    name + ' lost a life due to greencough',
                    name + ' lost a life due to whitecough',
                    'Lightning fell in camp and ' + name + ' lost a life',
                    name + ' was mortally wounded by a fox', name +
                    ' lost a life to a dog', name + ' lost a life to a badger',
                    name + ' lost a life to a hawk',
                    name + ' lost a life due to yellowcough',
                    name + ' lost a life while fighting off a rogue',
                    name + ' lost a life to an eagle', name +
                    ' was grabbed and dropped by an eagle, losing a life',
                    name + ' was grabbed and dropped by a hawk, losing a life',
                    name + ' lost a life after being swept away by a flood',
                    name + ' lost a life after falling off a tree',
                    name + ' was bit by a venomous spider and lost a life',
                    name + ' was bit by a venomous snake and lost a life',
                    name + ' ate poisoned fresh-kill and lost a life', name +
                    ' failed to interpret a warning sign from StarClan and lost a life as a result',
                    name + ' lost a life defending ' + other_name +
                    ' from a dog', name + ' lost a life defending ' +
                    other_name + ' from a badger', name +
                    ' lost a life defending ' + other_name + ' from a fox',
                    name + ' lost a life defending ' + other_name +
                    ' from a hawk', name + ' lost a life defending ' +
                    other_name + ' from an eagle',
                    name + ' lost a life while saving ' + other_name +
                    ' from drowning', name + ' lost a life while saving ' +
                    other_name + ' from a monster',
                    name + ' was pushed under a monster and lost a life',
                    name + ' lost a life after saving ' + other_name + ' from a snake'
                ]
                if len(game.clan.all_clans) > 0:
                    cause_of_death.extend([
                        name + ' lost a life defending the kits from ' +
                        choice(game.clan.all_clans).name + 'Clan warriors',
                        name + ' lost a life defending ' + other_name +
                        ' from ' + choice(game.clan.all_clans).name +
                        'Clan warriors', name + ' lost a life to a ' +
                        choice(game.clan.all_clans).name + 'Clan apprentice',
                        name + ' lost a life to a ' +
                        choice(game.clan.all_clans).name + 'Clan warrior'
                    ])
                game.clan.leader_lives -= 1
                self.dies(cat)
                game.cur_events_list.append(
                    choice(cause_of_death) + ' at ' + str(cat.moons) +
                    ' moons old')

        #Several/All Lives loss
        elif randint(1,200) == 1 and cat.status == 'leader':  
            name = str(cat.name)
            allorsome = randint(1, 10)
            if cat.status == 'leader':
                if allorsome == 1:
                    cause_of_death = [
                        name +
                        ' was brutally attacked by a rogue and lost all of their lives',
                        name +
                        ' was mauled by dogs and lost all of their lives',
                        name +
                        ' was carried off by an eagle, never to be seen again',
                        name +
                        ' was carried off by a hawk, never to be seen again',
                        name + ' was taken by twolegs, never to be seen again',
                        name +
                        ' fell into a river and was swept away by the current, never to be seen again',
                        name +
                        ' was burnt alive while trying to save their clanmates from a fire'
                    ]
                    if self.at_war and len(game.clan.all_clans) > 0:
                        cause_of_death.extend([
                            name + ' was brutally murdered by a ' +
                            choice(game.clan.all_clans).name +
                            'Clan warrior and lost all of their lives',
                            name + ' was brutally murdered by the ' +
                            choice(game.clan.all_clans).name +
                            'Clan deputy and lost all of their lives',
                            name + ' was brutally murdered by the ' +
                            choice(game.clan.all_clans).name +
                            'Clan leader and lost all of their lives'
                        ])
                    if game.clan.biome == "Mountainous":
                        cause_of_death.extend([
                            name + ' was buried alive in an avalanche',
                            name + ' was buried alive by a landslide', name +
                            ' was pushed off a cliff with sharp rocks at the bottom',
                            name +
                            ' accidentally fell off a cliff with sharp rocks at the bottom'
                        ])
                    if game.clan.biome == "Beach":
                        cause_of_death.extend([
                            name +
                            ' was washed out to sea and was never seen again',
                            name +
                            ' was lost to sea while saving a clanmate from drowning'
                        ])
                    if game.clan.biome == "Plains":
                        cause_of_death.extend([
                            name +
                            ' fell into a sinkhole and was never seen again',
                            name +
                            ' fell into a hidden burrow and was buried alive',
                            name +
                            ' was buried alive when a burrow collapsed on them'
                        ])
                    game.clan.leader_lives -= 10
                else:
                    lostlives = choice([2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6])
                    cause_of_death = [
                        name + ' lost ' + str(lostlives) +
                        ' lives due to greencough', name + ' lost ' +
                        str(lostlives) + ' lives due to whitecough',
                        name + ' lost ' + str(lostlives) +
                        ' lives due to yellowcough', name + ' lost ' +
                        str(lostlives) + ' lives due to an illness',
                        name + ' lost ' + str(lostlives) +
                        ' lives due to an infection'
                    ]
                    game.clan.leader_lives = game.clan.leader_lives - lostlives
                self.dies(cat)
                game.cur_events_list.append(
                    choice(cause_of_death) + ' at ' + str(cat.moons) +
                    ' moons old')

        elif randint(1, 400) == 1:
            name = str(cat.name)
            cause_of_death = [
                name + ' was murdered', name + ' died of greencough',
                'A tree fell in camp and killed ' + name,
                name + ' was found dead near a fox den',
                name + ' was bitten by a snake and died'
            ]
            if clan_has_kits == True and cat.status != 'kitten':
                cause_of_death.extend([
                    name + ' was bitten by a snake while saving a kit and died'
                ])
            if cat.status == 'kitten':
                cause_of_death.extend([
                    name + ' fell into a river and drowned',
                    name + ' was taken by a hawk',
                    name + ' grew weak as the days passed and died',
                    name + ' was killed after sneaking out of camp',
                    name + ' died after accidentally eating deathberries',
                    name +
                    ' was killed in their sleep after a snake snuck into camp'
                ])
                if game.clan.current_season == 'Leaf-bare':
                    cause_of_death.extend([
                        name + ' was found dead in the snow',
                        name + ' froze to death in a harsh snowstorm', name +
                        ' disappeared from the nursery and was found dead in the territory',
                        name +
                        ' was playing on the ice when the ice cracked and they drowned'
                    ])
                if game.clan.current_season == 'Greenleaf':
                    cause_of_death.extend([name + ' died to overheating'])
            elif cat.status == 'apprentice':
                cause_of_death.extend([
                    name + ' died in a training accident', name +
                    ' was killed by enemy warriors after accidentally wandering over the border',
                    name + ' went missing and was found dead',
                    name + ' died in a border skirmish'
                ])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([
                        name + ' was crushed to death by an avalanche',
                        name + ' fell from a cliff and died'
                    ])
                if game.clan.biome == "Beach":
                    cause_of_death.extend([
                        name + ' was washed out to sea and drowned',
                        name + ' was poisoned by a sea creature and died'
                    ])
            elif cat.status == 'warrior' or cat.status == 'deputy':
                if len(game.clan.all_clans) > 0:
                    cause_of_death.append(name + ' was found dead near the ' +
                                          choice(game.clan.all_clans).name +
                                          'Clan border')
                cause_of_death.extend([
                    name + ' died from infected wounds',
                    name + ' went missing and was found dead'
                ])
                if self.at_war:
                    cause_of_death.extend([
                        name + ' was killed by enemy ' + self.enemy_clan +
                        ' warriors', name + ' was killed by enemy ' +
                        self.enemy_clan + ' warriors',
                        name + ' was killed by enemy ' + self.enemy_clan +
                        ' warriors', name + ' died in a border skirmish'
                    ])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([
                        name + ' was crushed by an avalanche',
                        name + ' fell from a cliff and died'
                    ])
                if game.clan.biome == "Beach":
                    cause_of_death.extend([
                        name + ' was washed out to sea and drowned',
                        name + ' was poisoned by a sea creature and died'
                    ])
                if game.clan.biome == "Plains":
                    cause_of_death.extend([
                        name + ' fell into a sinkhole and died', name +
                        ' fell into a hidden burrow and could not get out',
                        name +
                        ' was buried alive when a burrow collapsed on them'
                    ])
            #Leader loses a life
            elif cat.status == 'leader':
                cause_of_death = []
                if len(game.clan.all_clans) > 0:
                    cause_of_death.extend([
                        name + ' lost a live to greencough',
                        'A tree fell in camp and ' + name + ' lost a life'
                    ])
                    cause_of_death.extend([
                        name + ' was found dead near the ' +
                        choice(game.clan.all_clans).name +
                        'Clan border mortally injured'
                    ])
                    cause_of_death.extend([
                        name + ' lost a life from infected wounds', name +
                        ' went missing and was later found mortally wounded'
                    ])
                if self.at_war:
                    cause_of_death.extend([
                        name + ' was killed by enemy ' + self.enemy_clan +
                        ' warriors and lost a life',
                        name + ' was killed by enemy ' + self.enemy_clan +
                        ' warriors and lost a life',
                        name + ' was killed by enemy ' + self.enemy_clan +
                        ' warriors and lost a life',
                        name + ' lost a life in a border skirmish'
                    ])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([
                        name + ' lost a life in an avalanche',
                        name + ' lost a life in a landslide',
                        name + ' was pushed off a cliff and lost a life',
                        name + ' accidentally fell off a cliff and lost a life'
                    ])
                elif game.clan.biome == "Beach":
                    cause_of_death.extend([
                        name + ' was washed out to sea and lost a life', name +
                        ' was poisoned by a sea creature and lost a life'
                    ])
                elif game.clan.biome == "Plains":
                    cause_of_death.extend([
                        name + ' fell into a sinkhole and lost a life',
                        name + ' fell into a hidden burrow and lost a life',
                        name + ' lost a life when a burrow collapsed on them'
                    ])
                elif self.at_war:
                    cause_of_death.extend([
                        name + ' was killed by the ' + self.enemy_clan +
                        ' deputy and lost a life',
                        name + ' was killed by the ' + self.enemy_clan +
                        ' leader and lost a life'
                    ])

            elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
                cause_of_death.extend([
                    'The herb stores were damaged and ' + name +
                    ' was murdered by an enemy warrior'
                ])
                if self.at_war:
                    cause_of_death.extend([
                        name + ' was killed by a ' + self.enemy_clan +
                        ' warrior while pulling an injured cat out of the battlefield'
                    ])
            if cat.status == 'deputy':
                if self.at_war:
                    cause_of_death.extend([
                        name + ' was killed by the ' + self.enemy_clan +
                        ' deputy', name + ' was killed by the ' +
                        self.enemy_clan + ' leader'
                    ])

            if cat.status == 'leader':
                game.clan.leader_lives -= 1
            self.dies(cat)

            game.cur_events_list.append(
                choice(cause_of_death) + ' at ' + str(cat.moons) +
                ' moons old')

        elif randint(1, 500) == 1:  # multiple deaths
            name = str(cat.name)
            other_cat = choice(list(cat_class.all_cats.values()))
            countdown = int(len(cat_class.all_cats) / 3)
            while cat == other_cat or other_cat.dead or other_cat.exiled:
                other_cat = choice(list(cat_class.all_cats.values()))
                countdown-=1
                if countdown <= 0:
                    return
            other_name = str(other_cat.name)
            cause_of_death = [
                name + ' and ' + other_name + ' die of greencough',
                name + ' and ' + other_name + ' die of yellowcough',
                name + ' and ' + other_name + ' die of whitecough',
                name + ' and ' + other_name + ' die from eating poisoned prey'
            ]
            if cat.status == ['kitten', 'leader'] or other_cat.status == ['kitten', 'leader']:
                cause_of_death.extend([
                    name + ' and ' + other_name +
                    ' are killed in a border skirmish',
                    name + ' and ' + other_name +
                    ' are killed in a battle against a gang of rogues'
                ])
            if cat.mate is not None and cat.age == other_cat.age and other_cat.mate is None:
                if cat.status == 'leader':
                    game.clan.leader_lives -= 10
                game.cur_events_list.append(
                    name + ' is killed by ' + other_name +
                    ' in an argument over ' +
                    str(cat_class.all_cats.get(cat.mate).name))
                self.dies(cat)
                return
            if cat.status == 'leader' or other_cat.status == 'leader':
                game.clan.leader_lives -= 1
                game.cur_events_list.append(choice(cause_of_death) + ' and the leader lost a life')
            else:
                game.cur_events_list.append(choice(cause_of_death))
            self.dies(cat)
            self.dies(other_cat)

        elif randint(1, 80) == 1:  #Death with Personalities
            murder_chance = 20
            name = str(cat.name)
            countdown = int(len(cat_class.all_cats) / 3)
            other_cat = choice(list(cat_class.all_cats.values()))
            while cat == other_cat or other_cat.dead or other_cat.exiled:
                other_cat = choice(list(cat_class.all_cats.values()))
                countdown-=1
                if countdown <= 0:
                    return
            other_name = str(other_cat.name)
            if cat.trait in [
                    'bloodthirsty', 'ambitious', 'vengeful', 'sneaky',
                    'sadistic', 'greedy', 'selfish'
            ] and other_cat.status in ['leader', 'deputy']:
                if cat.status == 'deputy' and other_cat.status == 'leader':
                    if randint(1, murder_chance - 15) == 1:
                        cause_of_death = [
                            name + ' murdered ' + other_name +
                            ' in cold blood to take their place',
                            name + ' murdered ' + other_name +
                            ' to take their place and made it look like an accident'
                        ]
                        game.clan.leader_lives -= 10
                        self.dies(other_cat)
                        game.cur_events_list.append(
                            choice(cause_of_death) + ' at ' +
                            str(other_cat.moons) + ' moons old')
                elif cat.status == 'warrior':
                    if randint(1, murder_chance - 15) == 1:
                        cause_of_death = [
                            name + ' murdered ' + other_name +
                            ' in cold blood '
                            'in hopes of taking their place',
                            name + ' murdered ' + other_name +
                            ' in cold blood and made it look accidental '
                            'in hopes of taking their place'
                        ]
                        if other_cat == 'leader':
                            game.clan.leader_lives -= 10
                        self.dies(other_cat)
                        game.cur_events_list.append(
                            choice(cause_of_death) + ' at ' +
                            str(other_cat.moons) + ' moons old')
            elif cat.trait in ['bloodthirsty', 'vengeful', 'sadistic']:
                if randint(1, murder_chance) == 1:
                    cause_of_death = [
                        name + ' murdered ' + other_name + ' in cold blood',
                        name + ' murdered ' + other_name +
                        ' in cold blood and made it look accidental'
                    ]
                    if other_cat == 'leader':
                        game.clan.leader_lives -= 10
                    self.dies(other_cat)
                    game.cur_events_list.append(
                        choice(cause_of_death) + ' at ' +
                        str(other_cat.moons) + ' moons old')
            elif cat.status in [
                    'medicine cat', 'medicine cat apprentice'
            ] and cat.trait in ['bloodthirsty', 'vengeful', 'sadistic']:
                if randint(1, murder_chance) == 1:
                    cause_of_death = [
                        name + ' killed ' + other_name +
                        ' by giving them deathberries', name + ' killed ' +
                        other_name + ' by giving them foxglove seeds',
                        name + ' killed ' + other_name +
                        ' by giving them nightshade berries',
                        name + ' killed ' + other_name +
                        ' by giving them water hemlock',
                        name + ' killed ' + other_name +
                        ' by consciously giving them the wrong herbs'
                    ]
                    if other_cat == 'leader':
                        game.clan.leader_lives -= 10
                    self.dies(other_cat)
                    game.cur_events_list.append(
                        choice(cause_of_death) + ' at ' +
                        str(other_cat.moons) + ' moons old')

        elif cat.moons > randint(150, 200):  # extra chance of cat dying to age
            if choice([1, 2, 3, 4, 5, 6]) == 1:
                if cat.status != 'leader':
                    self.dies(cat)
                    game.cur_events_list.append(
                        str(cat.name) +
                        ' has passed due to their old age at ' +
                        str(cat.moons) + ' moons old')
                else:
                    game.clan.leader_lives -= 1
                    self.dies(cat)
                    game.cur_events_list.append(
                        str(cat.name) +
                        ' has lost a life due to their old age at ' +
                        str(cat.moons) + ' moons old')
            if cat.status == 'leader' and cat.moons > 269:
                game.clan.leader_lives -= 10
                self.dies(cat)
                game.cur_events_list.append(
                    str(cat.name) + ' has passed due to their old age at ' +
                    str(cat.moons) + ' moons old')

        if game.settings.get('disasters') is True:
            alive_count = 0
            alive_cats = []
            for cat in list(cat_class.all_cats.values()):
                if not cat.dead and not cat.exiled and cat.status != 'leader':
                    alive_count += 1
                    alive_cats.append(cat)
            if alive_count > 10:
                chance = int(alive_count / 10)
                if randint(chance, 1000) == 999:
                    disaster = []
                    dead_cats = random.sample(alive_cats, 5)
                    name1 = str(dead_cats[0].name)
                    name2 = str(dead_cats[1].name)
                    name3 = str(dead_cats[2].name)
                    name4 = str(dead_cats[3].name)
                    name5 = str(dead_cats[4].name)
                    disaster.extend([
                        ' drown after the camp becomes flooded',
                        ' are killed in a battle against ' +
                        choice(names.normal_prefixes) + 'Clan',
                        ' are killed after a fire rages through the camp',
                        ' are killed in an ambush by a group of rogues',
                        ' go missing in the night',
                        ' are killed after a badger attack',
                        ' die to a greencough outbreak',
                        ' are taken away by twolegs',
                        ' eat poisoned freshkill and die'
                    ])
                    if game.clan.current_season == 'Leaf-bare':
                        disaster.extend([
                            ' die after freezing from a snowstorm',
                            ' starve to death when no prey is found'
                        ])
                    elif game.clan.current_season == 'Greenleaf':
                        disaster.extend([
                            ' die after overheating',
                            ' die after the water dries up from drought'
                        ])

                    game.cur_events_list.append(name1 + ', ' + name2 + ', ' +
                                                name3 + ', ' + name4 +
                                                ', and ' + name5 +
                                                choice(disaster))
                    for cat in dead_cats:
                        self.dies(cat)

    def dies(self, cat):  # This function is called every time a cat dies
        if cat.status == 'leader' and game.clan.leader_lives > 0:
            return
        elif cat.status == 'leader' and game.clan.leader_lives <= 0:
            cat.dead = True
            game.clan.leader_lives = 0
        else:
            cat.dead = True

        if cat.mate != None:
            cat.mate = None
            if type(cat.mate) == str:
                mate = cat_class.all_cats.get(cat.mate)
                mate.mate = None
            elif type(cat.mate) == Cat:
                cat.mate.mate = None

        for app in cat.apprentice.copy():
            app.update_mentor()
        cat.update_mentor()
        game.clan.add_to_starclan(cat)

    def check_age(self, cat):
        if 0 <= cat.moons <= 5:
            cat.age = 'kitten'
        elif 6 <= cat.moons <= 11:
            cat.age = 'adolescent'
        elif 12 <= cat.moons <= 47:
            cat.age = 'young adult'
        elif 48 <= cat.moons <= 95:
            cat.age = 'adult'
        elif 96 <= cat.moons <= 119:
            cat.age = 'senior adult'
        else:
            cat.age = 'elder'

events_class = Events()