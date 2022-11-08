from scripts.cat.cats import *
from scripts.cat_relations.relation_events import Relation_Events
from scripts.condition_events import Condition_Events
from scripts.game_structure.buttons import *
from scripts.game_structure.load_cat import * 

class Events():
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
        self.relation_events = Relation_Events()
        self.condition_events = Condition_Events()

    def one_moon(self):
        if game.switches['timeskip']:
            game.switches['saved_clan'] = False
            self.living_cats = 0
            self.new_cat_invited = False
            game.patrolled.clear()
            if any(str(cat.status) in {'leader', 'deputy', 'warrior', 'apprentice'}
                    and not cat.dead and not cat.exiled for cat in Cat.all_cats.values()):
                game.switches['no_able_left'] = False
            self.relation_events.handle_pregnancy_age(clan = game.clan)
            for cat in Cat.all_cats.copy().values():
                if not cat.exiled:
                    self.one_moon_cat(cat)
                else:
                    cat.moons += 1
                    if cat.moons == 6:
                        cat.age = 'adolescent'
                    elif cat.moons == 12:
                        cat.age = 'adult'
                    elif cat.moons == 100:
                        cat.age = 'elder'
                    if cat.moons > randint(100, 200):
                        if choice([1, 2, 3, 4, 5]) == 1 and not cat.dead:
                            cat.dead = True
                            game.cur_events_list.append(f'Rumors reach your clan that the exiled {str(cat.name)} has died recently ')

                    if cat.exiled and cat.status == 'leader' and not cat.dead and randint(
                            1, 10) == 1:
                        game.clan.leader_lives -= 1
                        if game.clan.leader_lives <= 0:
                            cat.dead = True
                            game.cur_events_list.append(f'Rumors reach your clan that the exiled {str(cat.name)} has died recently')

                            game.clan.leader_lives = 0
                    elif cat.exiled and cat.status == 'leader' and not cat.dead and randint(
                            1, 45) == 1:
                        game.clan.leader_lives -= 10
                        cat.dead = True
                        game.cur_events_list.append(f'Rumors reach your clan that the exiled {str(cat.name)} has died recently')

                        game.clan.leader_lives = 0

            self.check_clan_relations()
            game.clan.age += 1
            if game.settings.get('autosave') is True and game.clan.age % 5 == 0:
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
            game.clan.current_season = game.clan.seasons[game.clan.age % 12]
            game.event_scroll_ct = 0
            has_med = any(
                str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                and not cat.dead and not cat.exiled
                for cat in Cat.all_cats.values())

            if not has_med:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no medicine cat!")
            if game.clan.deputy == 0 or game.clan.deputy is None or game.clan.deputy.dead or game.clan.deputy.exiled:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no deputy!")
            if game.clan.leader.dead or game.clan.leader.exiled:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no leader!")

        game.switches['timeskip'] = False

    def one_moon_cat(self, cat):
        if cat.dead:
            cat.thoughts()
            cat.dead_for += 1
            return
        
        self.living_cats += 1

        self.perform_ceremonies(cat)

        # switches between the two death handles
        if randint(1,2) == 1:
            triggered_death = self.handle_injuries_or_general_death(cat)
            if not triggered_death:
                triggered_death = self.handle_illnesses_or_illness_deaths(cat)
        else:
            triggered_death = self.handle_illnesses_or_illness_deaths(cat)
            if not triggered_death:
                triggered_death = self.handle_injuries_or_general_death(cat)

        #self.handle_deaths(cat)
        if not self.new_cat_invited or self.living_cats < 10:
            self.invite_new_cats(cat)
        self.other_interactions(cat)
        self.coming_out(cat)
        self.gain_accessories(cat)
        self.gain_scars(cat)

        # all actions, which do not trigger and event display and 
        # are connected to cats are located in there
        cat.one_moon()

        self.relation_events.handle_relationships(cat)
        self.relation_events.handle_having_kits(cat, clan = game.clan)

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
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.status == 'medicine cat' and game.clan.medicine_cat is None:
                game.clan.medicine_cat = cat
            if cat.status in ['warrior', 'deputy'] and cat.age == 'elder' and len(cat.apprentice) < 1:
                if cat.status == 'deputy':
                    game.clan.deputy = None
                self.ceremony(cat, 'elder', ' has retired to the elder den')
                cat.status_change('elder')
            if cat.moons == cat_class.age_moons[cat.age][1]:
                if cat.status == 'kitten':
                    # check if the medicine cat is an elder
                    has_elder_med = any(
                        cat.status == 'medicine cat' and cat.age == 'elder'
                        and not cat.dead and not cat.exiled
                        for cat in Cat.all_cats.values())
                    very_old_med = any(
                        cat.status == 'medicine cat' and cat.moons >= 150
                        and not cat.dead and not cat.exiled
                        for cat in Cat.all_cats.values())
                    # check if a med cat of a different age exists
                    has_med = any(
                        cat.status == 'medicine cat' and cat.age != 'elder'
                        and not cat.dead and not cat.exiled
                        for cat in Cat.all_cats.values())
                    # check if a med cat app already exists
                    has_med_app = any(
                        cat.status == 'medicine cat apprentice'
                        and not cat.dead and not cat.exiled
                        for cat in Cat.all_cats.values())
                    # assign chance to become med app depending on current med cat and traits
                    if has_elder_med is True and has_med is False:
                        #chance = randint(0, 2)
                        chance = int(random.random() * 3)  # 3 is not part of the range
                        print('POSSIBLE MED APP - ELDER MED MENTOR - CHANCE:', chance)
                    elif has_elder_med is False and has_med is True:
                        #chance = randint(0, 90)
                        chance = int(random.random() * 91)
                    elif has_elder_med and has_med:
                        if very_old_med:
                            #chance = randint(0, 40)
                            chance = int(random.random() * 41)
                        else:
                            chance = 0
                    else:
                        chance = int(random.random() * 41)
                    print('POSSIBLE MED APP - CHANCE:', chance)
                    if chance in range(1, 6):    
                        if cat.trait in ['polite', 'quiet', 'sweet', 'daydreamer']:
                            chance = 1
                        print('POSSIBLE MED APP - TRAIT:', cat.trait, '- CHANCE:', chance)
                    if has_med_app is False and chance == 1:
                        self.ceremony(cat, 'medicine cat apprentice', ' has chosen to walk the path of a medicine cat')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    else:
                        self.ceremony(cat, 'apprentice', ' has started their apprenticeship ')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                elif cat.status == 'apprentice':
                    self.ceremony(cat, 'warrior', ' has earned their warrior name ')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)
                elif cat.status == 'medicine cat apprentice':
                    self.ceremony(cat, 'medicine cat', ' has earned their medicine cat name ')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

    def ceremony(self, cat, promoted_to, ceremony_text):
        cat.status_change(promoted_to)
        game.cur_events_list.append(f'{str(cat.name)}{ceremony_text}')

    def gain_accessories(self, cat):
        if cat.accessory is not None:
            return
        name = str(cat.name)
        other_cat = choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(Cat.all_cats.values()))
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
                acc_singular = plural_acc_names(cat.accessory, False, True)
                acc_plural = plural_acc_names(cat.accessory, True, False)
                #if self.ceremony_accessory == True:
                 #   acc_text.extend([f'{other_name} gives {name} something to adorn their pelt as congratulations', f'{name} decides to pick something to adorn their pelt as celebration'])
                if cat.age != 'kitten':
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        if game.clan.current_season == 'Leaf-bare':
                            acc_text.append(f'{name} found a mysterious {acc_singular} growing in the {choice(["snow", "ice", "frost"])} and decided to wear it')
                        else:
                            acc_text.extend([f'{name} received a cool {acc_singular} from {other_name} and decided to wear it on their pelt ',
                                            f'{name} found a pretty {acc_singular} and decided to wear it on their pelt', f'A clanmate gave {name} some {acc_plural} and they decided to wear them '
                            ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"] and cat.specialty != "NOTAIL" and cat.specialty2 != "NOTAIL":
                        acc_text.append(f'{name} found a bunch of pretty {acc_plural} and decided to wear them ')
                    elif cat.accessory in ["HERBS", "PETALS", "DRY_HERBS"]:
                        acc_text.append(f'{name} always seems to have {acc_plural} stuck in their fur ')
                    elif cat.accessory in plant_accessories and cat.status in ['medicine cat apprentice', 'medicine cat']:
                        acc_text.extend([f'{name} has decided to always bring some {acc_plural} with them ',
                                        f'{acc_plural} are so important to {name} that they always carry it around '.capitalize,
                                        f'{acc_plural} are so vital for {name} that they always have some on them '.capitalize
                        ])
                    else:
                        acc_text.extend([f'{name} finds a(n) {acc_singular} and decides to wear it on their pelt', f'A clanmate gives {name} a pretty {acc_singular} and they decide to wear it on their pelt ',
                                        f'{name} finds a(n) {acc_singular} while out on a walk and decides to wear it on their pelt', f'{name} finds {acc_plural} fascinating and decides to wear some on their pelt ',
                                        f'A clanmate gives {name} a pretty {acc_singular} to adorn their pelt as a gift', f'{other_name} gives {name} a pretty {acc_singular} and they decide to wear it on their pelt '
                        ])
                else:
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        acc_text.extend([f'{name} received a {acc_singular} from {other_name} and decided to wear it on their pelt ',
                                            f'{name} found a {acc_singular} and decided to wear it on their pelt', f'A clanmate gave {name} a {acc_singular} and they decided to wear it '
                            ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"] and cat.specialty != "NOTAIL" and cat.specialty2 != "NOTAIL":
                        acc_text.append(f'{name} was playing with {acc_plural} earlier and decided to wear some of them ')
                    elif cat.accessory in ["HERBS", "PETALS", "DRYHERBS"]:
                        acc_text.append(f'{name}\'s parents try their best to groom them, but something is always stuck in their fur ')
                    else:    
                        acc_text.extend([f'{name} seems to have picked up a neat {acc_singular} while playing out in the camp', f'{name} finds something interesting and decides to wear it on their pelt ',
                                        f'A clanmate gives {name} a pretty {acc_singular} and they decide to wear it on their pelt', f'{other_name} gives {name} a pretty {acc_singular} and they decide to wear it on their pelt ',
                                        f'{name} is so cute that they are given {acc_plural} as a gift', f'{name} starts to wear {acc_plural} on their pelt after their friend gave some to them ',
                                        f'{name} was playing with {acc_plural} earlier and has decided to use it to adorn themselves '
                        ])
        if acc_text:
            game.cur_events_list.append(choice(acc_text))
            if self.ceremony_accessory:
                self.ceremony_accessory = False   

    def gain_scars(self, cat):
        if cat.specialty and cat.specialty2 or cat.age == 'kitten':
            return
        risky_traits = ["bloodthirsty", "ambitious", "vengeful", "strict", "cold", "fierce"]
        danger = ["rogue", "dog", "fox", "otter", "rat", "hawk", "enemy warrior", "badger"]
        tail_danger = ["rogue", "dog", "fox", "otter", "rat", "hawk",
                       "enemy warrior", "badger", "twoleg trap"]
        name = str(cat.name)
        scar_chance = 0.015  # 1.5%
        clancats = self.living_cats
        scar_text = []
        specialty = None  # Scar to be set
        alive_kits = list(filter(lambda kitty: (kitty.age == "kitten"
                                                and not kitty.dead
                                                and not kitty.exiled),
                                 Cat.all_cats.values()))
        leader = Cat.all_cats[str(game.clan.leader)]
        
        # Older cats are scarred more often
        if cat.age in ["adult", "senior adult"]:
            scar_chance += 0.01  # + 1%

        # Check cat mentor/leader status and traits
        risky_mentor = False
        risky_leader = False
        other_name = "[this string should not appear :'3 ]"
        if cat.mentor:
            if cat.mentor.trait in risky_traits:
                risky_mentor = True
                scar_chance += 0.0225  # + 2.25%
        if leader:
            if leader.trait in risky_traits:
                risky_leader = True
                other_name = str(leader.name)
                scar_chance += 0.005  # + 0.5%
                if leader.trait in ["bloodthirsty", "vengeful"]:
                    scar_chance += 0.005

        # Modify scar chance by trait
        # Increased chance
        if cat.trait in ['bloodthirsty', 'vengeful']:
            scar_chance = scar_chance * 1.75
        elif cat.trait in cat.personality_groups["Abrasive"]:
            scar_chance = scar_chance * 1.5
        elif cat.trait in cat.personality_groups["Outgoing"]:
            scar_chance = scar_chance * 1.25
        # Reduced chance
        elif cat.trait in ['calm', 'careful']:
            scar_chance = scar_chance / 1.75
        elif cat.trait in cat.personality_groups["Reserved"]:
            scar_chance = scar_chance / 1.5
        elif cat.trait in cat.personality_groups["Benevolent"]:
            scar_chance = scar_chance / 1.25

        # Bloodthirsty leader mod
        leader_scar_chance = scar_chance
        if leader.trait in ["bloodthirsty", "vengeful"]:
            leader_scar_chance = leader_scar_chance * 1.75

        # Set pools and check which scars we can still get
        all_scars = scars1 + scars2 + scars4 + scars5
        base_scars = scars1 + scars2  # Can be caused by other cats
        for scar_pool in [all_scars, base_scars]:
            for special in [cat.specialty, cat.specialty2]:
                if special:
                    try:
                        if "NOPAW" == special and 'TOETRAP' in scar_pool:
                            scar_pool.remove('TOETRAP')
                        if "NOTAIL" == special:
                            for scar in ["HALFTAIL", "TAILBASE", "TAILSCAR"]:
                                if scar in scar_pool:
                                    scar_pool.remove(scar)
                        if special in scar_pool:
                            scar_pool.remove(special)  # No doubles
                    except ValueError as e:
                        print(f"Failed to exclude scar from pool: {e}")

        # Always possible scar events
        if scar_chance > random.random():
            specialty = choice(all_scars)
            if specialty in ["NOTAIL", "HALFTAIL"]:
                if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                    cat.accessory = None
                scar_text.append(f"{name} lost their tail to a {choice(tail_danger)} ")
                if not random.getrandbits(2):
                    scar_text.append(f"{name} lost their tail to a falling tree ")
            elif specialty == "SNAKE":
                scar_text.append(f"{name} was bit by a snake but miraculously survived ")
            elif specialty == "TOETRAP":
                scar_text.append(
                    f"{name} got their paw stuck in a twoleg trap and earned a scar "
                )
            elif specialty == "NOPAW":
                scar_text.append(f"{name} lost their paw to a twoleg trap ")
            else:
                scar_text.extend(
                    [
                        f"{name} earned a scar fighting a {choice(danger)} ",
                        f"{name} earned a scar defending the territory ",
                        f"{name} is injured after falling into a river ",
                        f"{name} is injured by enemy warriors after accidentally wandering over the border ",
                        f"{name} is injured after messing with a twoleg object ",
                    ]
                )
                if alive_kits:
                    scar_text.extend([f"{name} earned a scar protecting the kits "])
        
        # MENTOR CAUSES INJURY >:O
        elif (scar_chance * 1.5 > random.random()
              and cat.status in ['apprentice', 'medicine cat apprentice']
              and risky_mentor):
            specialty = choice(base_scars)
            scar_text.extend(
                [
                    f"{name} earned a scar recklessly fighting a {choice(danger)} encouraged by their mentor ",
                    f"{name} earned a scar for not defending the territory well enough ",
                    f"{name} is injured after being pushed into a river ",
                    f"{name} is punished by their mentor after accidentally wandering over the border ",
                    f"{name} is injured by their mentor after being caught messing with a twoleg object ",
                    f"{name} is injured by their mentor while practicing with their claws out ",
                    f"{name}'s mentor punished them for disobeying ",
                    f"{name} gained a scar while fighting their mentor ",
                    f"{name} is injured while practicing their battle moves with {other_name} ",
                    f"{name} is injured after a fight broke out with {other_name} ",
                    f"{name} could not handle their mentor's harsh training and got injured as a result ",
                    f"{name} could not handle their mentor's harsh training and got injured as a result ",
                ]
            )
            if specialty == "NOPAW":
                scar_text.append(f"{name} lost their paw after {other_name} decided to use twoleg traps for a training exercice ")
        # leader is sus guys
        elif leader_scar_chance > random.random() and risky_leader and cat.ID != leader.ID:
            specialty = choice(base_scars)
            if specialty in ["NOTAIL", "HALFTAIL"]:
                if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                    cat.accessory = None

                scar_text.extend([
                    f"{name} lost their tail to a {choice(tail_danger)} while following {other_name}'s orders ",
                    f"{name} is ordered to fend off a {choice(danger)} by {other_name}, and looses their tail in the ensuing battle ",
                    ]
                )
            else:
                if specialty in ["NOPAW"]:
                    scar_text.extend([f"{name} is maimed by {other_name} for questioning their leadership ",
                                      f"{name} loses a paw after {other_name} forces them to fight a {choice(danger)} by themselves "])
                else:
                    scar_text.extend(
                        [
                            f"{name} earned a scar fighting a {choice(danger)} on {other_name}'s orders ",
                            f"{name} earned a scar defending the territory from outsiders ",
                            f"{name} earned a scar protecting the leader ",
                            f"{name} is wounded during a harsh training exercice led by {other_name} ",
                            f"{name} is injured during an unsupervised training exercice ",
                            f"{name} is hurt by enemy warriors after being ordered by {other_name} to go over the border ",
                            f"{name} is injured after being ordered by {other_name} to check out a twoleg object ",
                            f"{name} is battered while fighting a clanmate after {other_name} encouraged a fight ",
                            f"{name} is injured by {other_name} for disobeying orders ",
                            f"{name} is injured by {other_name} for speaking out against them ",
                            f"{name} is cruelly injured by {other_name} to make an example out of them ",
                        ]
                    )
        if scar_text:
            game.cur_events_list.append(choice(scar_text))

        # Apply scar
        if specialty:
            if not cat.specialty:
                cat.specialty = specialty
            else:
                cat.specialty2 = specialty
            
    def invite_new_cats(self, cat):
        chance = 100
        if self.living_cats < 10:
            chance = 100
        elif self.living_cats > 50:
            chance = 700
        elif self.living_cats > 30:
            chance = 300
        if randint(1, chance) == 1 and cat.age != 'kitten' and cat.age != 'adolescent':
            self.new_cat_invited = True
            name = str(cat.name)
            type_of_new_cat = choice([1, 2, 3, 4, 5, 6, 7])
            if type_of_new_cat == 1:
                backstory_choice = choice(['abandoned2', 'abandoned1'])
                created_cats = self.create_new_cat(loner = False, loner_name = False, kittypet = choice([True, False]), kit=True, backstory=backstory_choice)
                kit = created_cats[0]
                kit_text = [
                    f'{name} finds an abandoned kit and names them {kit.name} ',
                    f'A loner brings their kit named {kit.name.prefix} to the clan, stating they no longer can care for them '
                ]
                game.cur_events_list.append(choice(kit_text))

            elif type_of_new_cat == 2:
                backstory_choice = choice(['loner1', 'loner2', 'kittypet2',
                'rogue1', 'rogue2'])
                created_cats = self.create_new_cat(loner=True, loner_name=True, backstory=backstory_choice)
                loner_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a loner named {loner_name.prefix} who joins the clan',
                    f'A loner waits on the border for a patrol, asking to join the clan'
                ]
                if loner_name.suffix != '':
                    success_text = [
                        f'{loner_name} decides to keep their name'
                    ]
                else:
                    success_text = [
                        f'The loner decides to take on a slightly more clan-like name, and is now called {loner_name}'
                    ]
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append(choice(success_text))

            elif type_of_new_cat == 3:
                backstory_choice = choice(['loner1', 'loner2', 'kittypet2', 'rogue1', 'rogue2'])
                created_cats = self.create_new_cat(loner=True, loner_name=True, backstory=backstory_choice)
                loner_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a loner named {loner_name.prefix} who wishes to join the clan',
                    f'A loner says that they are interested in clan life and joins the clan'
                ]
                if loner_name.suffix != '':
                    success_text = [
                        f'The loner decides to take on a slightly more clan-like name, and is now called {loner_name}'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name'
                    ]
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append(choice(success_text))

            elif type_of_new_cat == 4:
                otherclan = str(choice(game.clan.all_clans).name)
                backstory_choice = choice(['otherclan', 'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee', 'tragedy_survivor'])
                created_cats = self.create_new_cat(kit=False,litter=False,loner=True,backstory=backstory_choice,other_clan=otherclan)
                warrior_name = created_cats[0].name
                warrior_text = []
                if len(game.clan.all_clans) > 0:
                    warrior_text.extend([
                        f'{name} finds a warrior from {otherclan}Clan named {warrior_name} who asks to join the clan ',
                        f'An injured warrior from {otherclan}Clan asks to join in exchange for healing '
                    ])
                else:
                    warrior_text.extend([
                        f'{name} finds a warrior from a different clan named {warrior_name} who asks to join the clan '
                    ])
                game.cur_events_list.append(choice(warrior_text))

            elif type_of_new_cat == 5:
                created_cats = self.create_new_cat(loner=False,loner_name=True,kittypet=True,kit=False,litter=False,relevant_cat=None,
                backstory=choice(['kittypet1', 'kittypet2']))
                loner_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a kittypet named {str(loner_name.prefix)} who wants to join the clan',
                    f'A kittypet called {str(loner_name.prefix)} stops {name} and asks to join the clan'
                ]
                if loner_name.suffix != '':
                    success_text = [ 
                        f'The kittypet decides to take on a slightly more clan-like name, and is now called {str(loner_name)} '
                    ]
                else:
                    success_text = [
                        f'{str(loner_name)} decides to keep their name'
                ]
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append(choice(success_text))
            
            elif type_of_new_cat == 6:
                created_cats = self.create_new_cat(loner=True, backstory=choice(['kittypet1', 'kittypet2']))
                warrior_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a kittypet named {choice(names.loner_names)} who wants to join the clan '
                ]
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append(
                    f'The kittypet changes their name to {str(warrior_name)} ')

            elif type_of_new_cat == 7:
                otherclan = str(choice(game.clan.all_clans).name)
                backstory_choice = choice(['abandoned1', 'abandoned2', 'abandoned3'])
                backstory = backstory_choice
                parent1 = cat.name
                created_cats = self.create_new_cat(
                    loner=True,
                    loner_name=False,
                    kittypet=False,
                    kit=False,
                    litter=True,
                    relevant_cat=cat,
                    backstory=backstory_choice,
                    other_clan=otherclan
                )
                if backstory == 'abandoned3':
                    A_kit_text = ([
                        f'A {otherclan}Clan queen decides to leave their litter with you. {str(parent1)} takes them as their own '
                    ])
                else:
                    A_kit_text = ([
                        f'{parent1} finds an abandoned litter and decides to adopt them as their own ',
                        f'A loner leaves their litter to the clan. {str(parent1)} decides to adopt them as their own '
                    ])
                game.cur_events_list.append(choice(A_kit_text))            

    def create_new_cat(self,
                       loner=False,
                       loner_name=False,
                       kittypet=False,
                       kit=False,
                       litter=False,
                       relevant_cat=None,
                       backstory=None,
                       other_clan=None):
        name = None
        skill = None
        accessory = None
        status = "kitten"
        backstory = backstory
        other_clan = other_clan

        age = randint(0, 5)
        kp_name_chance = (1, 5)
        if not litter and not kit:
            age = randint(6, 120)

        if (loner or kittypet) and not kit and not litter:
            if loner_name:
                if loner and kp_name_chance == 1:
                    name = choice(names.normal_prefixes)
                else:
                    name = choice(names.loner_names)
            if age >= 12:
                status = "warrior"
            else:
                status = "apprentice"
        if kittypet:
            if choice([1, 2]) == 1:
                accessory = choice(collars)

        amount = choice([1, 1, 2, 2, 2, 3]) if litter else 1
        created_cats = []
        a = randint(0, 1)
        for number in range(amount):
            new_cat = None
            if loner_name and a == 1:
                new_cat = Cat(moons=age, prefix=name, status=status, gender=choice(['female', 'male']), backstory=backstory)
            elif loner_name:
                new_cat = Cat(moons=age, prefix=name, suffix='', status=status, gender=choice(['female', 'male']), backstory=backstory)
            else:
                new_cat = Cat(moons=age, status=status, gender=choice(['female', 'male']), backstory=backstory)
            if skill:
                new_cat.skill = skill
            if accessory:
                new_cat.accessory = accessory

            if (kit or litter) and relevant_cat and relevant_cat.ID in Cat.all_cats:
                new_cat.parent1 = relevant_cat.ID
                if relevant_cat.mate:
                    new_cat.parent2 = relevant_cat.mate

            #create and update relationships
            relationships = []
            for the_cat in new_cat.all_cats.values():
                if the_cat.dead or the_cat.exiled:
                    continue
                the_cat.relationships.append(Relationship(the_cat, new_cat))
                relationships.append(Relationship(new_cat, the_cat))
            new_cat.relationships = relationships
            new_cat.thought = 'Is looking around the camp with wonder'
            created_cats.append(new_cat)
        
        for new_cat in created_cats:
            add_siblings_to_cat(new_cat,cat_class)
            add_children_to_cat(new_cat,cat_class)
            game.clan.add_cat(new_cat)

        return created_cats

    def other_interactions(self, cat):
        if randint(1, 100) != 1:
            return
        interactions = []
        other_cat = choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(Cat.all_cats.values()))
            countdown-=1
            if countdown <= 0:
                return
        name = str(cat.name)
        other_name = str(other_cat.name)
        if cat.status in ['warrior', 'deputy'] and randint(
                1, 15) == 1 and game.settings.get('retirement') is True:
            game.cur_events_list.append(
                f'{name} retires to the elders den after injuries sustained defending {other_name} '
            )
            if cat.status == 'deputy':
                game.clan.deputy = None

            cat.status_change('elder')
            return
        if cat.status == 'kitten' and other_cat.status != 'kitten':
            interactions.extend([
                f'{name} is scolded after sneaking out of camp ',
                f'{name} falls into a river but is saved by {other_name} '
            ])
        elif cat.status in ['apprentice', 'medicine cat apprentice'] and other_cat.status != 'kitten':
            interactions.extend([
                f'{name} is scolded after sneaking out of camp ',
                f'{name} falls into a river but is saved by {other_name} ',
                name +
                " accidentally trespasses onto another clan\'s territory "
            ])
            if other_cat.status == 'apprentice':
                interactions.append(
                    f'{name} sneaks out of camp with {other_name} ')
        elif cat.status == 'warrior':
            interactions.extend([
                name + " is caught outside of the Clan\'s territory ",
                f'{name} is caught breaking the Warrior Code ',
                f'{name} went missing for a few days ',
                f'{name} believes they are a part of the new prophecy '
            ])
        elif cat.status == 'medicine cat':
            interactions.extend([
                f'{name} learns of a new prophecy ',
                f'{name} is worried about an outbreak of greencough ',
                f'{name} is worried about how low their herb stores has gotten ',
                f'{name} visits the other medicine cats '
            ])
        elif cat.status == 'deputy':
            interactions.extend([
                f'{name} thinks about retiring ',
                f'{name} travels to the other clans to bring them an important message '
            ])
        elif cat.status == 'leader':
            if game.clan.leader_lives <= 5:
                interactions.extend([
                    f'{name} thinks about retiring ',
                    name + " confesses they don\'t have many lives left "
                ])
            if other_cat.status not in [
                    'kitten', 'apprentice', 'medicine cat apprentice'
            ]:
                interactions.append(
                    f'{name} confesses to {other_name} that the responsibility of leadership is crushing them '
                )
            elif other_cat.status == 'apprentice':
                interactions.append(f'{name} assesses {other_name}' +
                                    "\'s progress")
            interactions.extend([
                f'{name} calls a clan meeting to give an important announcement '
            ])
        elif cat.status == 'elder':
            interactions.extend(
                [f'{name} is brought back to camp after wandering off '])
        if cat.age == other_cat.age:
            interactions.extend([
                f'{name} tries to convince {other_name} to run away together '
            ])

        if interactions:
            game.cur_events_list.append(choice(interactions))

    def handle_injuries_or_general_death(self, cat):
        """ 
        This function will handle:
            - classic mode: death events with injuries
            - expanded mode: getting a new injuries (extra function in own class)
        Returns: 
            - boolean if a death event occurred or not
        """
        # get the general information about the cat and a random other cat
        triggered = False
        clan_has_kits = any(
                cat.status in "kitten"
                and not cat.dead and not cat.exiled
                for cat in Cat.all_cats.values())
        #Leader lost a life EVENTS
        current_lives = int(game.clan.leader_lives)
        if not int(random.random() * 100):  # 1/100
            name = str(cat.name)
            other_cat = choice(list(Cat.all_cats.values()))
            countdown = int(len(Cat.all_cats) / 3)
            while cat == other_cat or other_cat.dead or other_cat.status == 'leader' or other_cat.exiled:
                other_cat = choice(list(Cat.all_cats.values()))
                countdown -= 1
                if countdown <= 0:
                    return
            if cat.status == 'leader':
                other_name = other_cat.name
                if game.clan.current_season in ['Leaf-fall', 'Leaf-bare']:
                    cause_of_death = [
                        f'{name} lost a life due to greencough ',
                        f'{name} lost a life due to whitecough ',
                        f'{name} lost a life due to yellowcough ',
                    ]
                else:
                    cause_of_death = [
                        f'{name} lost a life after falling into a river ',
                        f'Lightning fell in camp and {name} lost a life ',
                        f'{name} was mortally wounded by a fox ',
                        f'{name} lost a life to a dog ',
                        f'{name} lost a life to a badger ',
                        f'{name} lost a life to a hawk ',
                        f'{name} lost a life while fighting off a rogue ',
                        f'{name} lost a life to an eagle ',
                        f'{name} was grabbed and dropped by an eagle, losing a life ',
                        f'{name} was grabbed and dropped by a hawk, losing a life ',
                        f'{name} lost a life after being swept away by a flood ',
                        f'{name} lost a life after falling off a tree ',
                        f'{name} was bit by a venomous spider and lost a life ',
                        f'{name} was bit by a venomous snake and lost a life ',
                        f'{name} ate poisoned fresh-kill and lost a life ',
                        f'{name} failed to interpret a warning sign from StarClan and lost a life as a result ',
                        f'{name} lost a life defending {other_name} from a dog ',
                        f'{name} lost a life defending {other_name} from a badger ',
                        f'{name} lost a life defending {other_name} from a fox ',
                        f'{name} lost a life defending {other_name} from a hawk ',
                        f'{name} lost a life defending {other_name} from an eagle ',
                        f'{name} lost a life while saving {other_name} from drowning ',
                        f'{name} lost a life while saving {other_name} from a monster ',
                        f'{name} was pushed under a monster and lost a life ',
                        f'{name} lost a life after saving {other_name} from a snake '
                    ]

                    
                if game.clan.all_clans:
                    cause_of_death.extend([
                        name + ' lost a life defending the kits from ' +
                        choice(game.clan.all_clans).name + 'Clan warriors',
                        name + ' lost a life defending ' + other_name +
                        ' from ' + choice(game.clan.all_clans).name +
                        'Clan warriors',
                        name + ' lost a life to a ' +
                        choice(game.clan.all_clans).name + 'Clan apprentice',
                        name + ' lost a life to a ' +
                        choice(game.clan.all_clans).name + 'Clan warrior'
                    ])
                game.clan.leader_lives -= 1
                cat.die()
                game.cur_events_list.append(
                    choice(cause_of_death) + ' at ' + str(cat.moons + 1) +
                    ' moons old ')

        #Several/All Lives loss
        elif not int(random.random() * 200) and cat.status == 'leader':  # 1/200
            name = str(cat.name)
            allorsome = randint(1, 10)
            if cat.status == 'leader':
                if allorsome == 1:
                    cause_of_death = [
                        name + ' was brutally attacked by a rogue and lost all of their lives',
                        name + ' was mauled by dogs and lost all of their lives',
                        name + ' was carried off by an eagle, never to be seen again',
                        name + ' was carried off by a hawk, never to be seen again',
                        name + ' was taken by twolegs, never to be seen again',
                        name + ' fell into a river and was swept away by the current, never to be seen again',
                        name + ' was burnt alive while trying to save their clanmates from a fire'
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
                            name + ' was buried alive by a landslide',
                            name + ' was pushed off a cliff with sharp rocks at the bottom',
                            name + ' accidentally fell off a cliff with sharp rocks at the bottom'
                        ])
                    if game.clan.biome == "Beach":
                        cause_of_death.extend([
                            name + ' was washed out to sea and was never seen again',
                            name + ' was lost to sea while saving a clanmate from drowning'
                        ])
                    if game.clan.biome == "Plains":
                        cause_of_death.extend([
                            name + ' fell into a sinkhole and was never seen again',
                            name + ' fell into a hidden burrow and was buried alive',
                            name + ' was buried alive when a burrow collapsed on them'
                        ])
                    game.clan.leader_lives -= 10
                else:
                    lostlives = choice([2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6])
                    if cat.moons >= 130 and game.clan.current_season in ['Leaf-fall', 'Leaf-bare']:
                        cause_of_death = [
                            name + ' lost ' + str(lostlives) +
                            ' lives due to greencough',
                            name + ' lost ' +
                            str(lostlives) + ' lives due to whitecough',
                            name + ' lost ' + str(lostlives) +
                            ' lives due to yellowcough',
                            name + ' lost ' +
                            str(lostlives) + ' lives due to an illness'
                        ]
                        game.clan.leader_lives = current_lives - lostlives
                        cat.die()
                        game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons + 1) + ' moons old ')

        elif not int(random.random() * 400): # 1/400
            name = str(cat.name)
            cause_of_death = [
                name + ' was murdered',
                'A tree fell in camp and killed ' + name,
                name + ' was found dead near a fox den',
                name + ' was bitten by a snake and died'
            ]
            if clan_has_kits and cat.status != 'kitten':
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
                        ' was playing on the ice when the ice cracked and they drowned',
                        name + ' died of greencough'
                    ])
                    if cat.status == 'kitten':
                        cause_of_death.extend([
                        name + ' died of kittencough', name +
                        ' was too weak to fight off whitecough and passed',
                        name + ' caught a cold and slowly faded'
                    ])
                    if cat.status == 'elder' or cat.moons < 150:
                        cause_of_death.extend([
                        name + ' was already feeling weak and a case of whitecough finished them off',
                        name + ' was too weak to recover from an illness and passed',
                        'Weakened by a lack of prey, ' + name + ' couldn\'t fight off whitecough and passed',
                        name + ' was taken quickly by a case of greencough'
                    ])
                if game.clan.current_season == 'Greenleaf':
                    cause_of_death.extend([name + ' died to overheating'])
            elif cat.status == 'apprentice':
                cause_of_death.extend([
                    name + ' died in a training accident',
                    name + ' was killed by enemy warriors after accidentally wandering over the border',
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
                if game.clan.all_clans:
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
                        name + ' went missing and was later found mortally wounded'
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
                if game.clan.all_clans:
                    cause_of_death.extend([
                        name + ' lost a life to greencough',
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
            cat.die()

            game.cur_events_list.append(
                choice(cause_of_death) + ' at ' + str(cat.moons + 1) +
                ' moons old')

        elif not random.getrandbits(9):  # multiple deaths, 1/512
            name = str(cat.name)
            other_cat = choice(list(Cat.all_cats.values()))
            countdown = int(len(Cat.all_cats) / 3)
            while cat == other_cat or other_cat.dead or other_cat.exiled:
                other_cat = choice(list(Cat.all_cats.values()))
                countdown-=1
                if countdown <= 0:
                    return
            other_name = str(other_cat.name)
            cause_of_death = [
                name + ' and ' + other_name + ' die from eating poisoned prey'
            ]
            if game.clan.current_season == 'Leaf-bare':
                if cat.status == 'kitten' and other_cat.status == 'kitten':
                    cause_of_death = [
                        'Greencough reaches the nursery. ' + name + ' and ' + other_name + ' die',
                        name + ' and ' + other_name + ' die from a bout of kittencough',
                        name + ' and ' + other_name + ' catch whitecough and fade away quickly'
                    ]
                else:
                    cause_of_death = [
                        name + ' and ' + other_name + ' die of greencough',
                        name + ' and ' + other_name + ' die of yellowcough',
                        'A bad case of greencough strikes, and ' + name + ' and ' + other_name +
                        ' die'
                    ]
                
            if cat.status not in ['elder', 'kitten'] and other_cat.status not in ['elder', 'kitten']:
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
                    str(Cat.all_cats.get(cat.mate).name))
                cat.die()
                return
            if cat.status == 'leader' or other_cat.status == 'leader':
                game.clan.leader_lives -= 1
                game.cur_events_list.append(choice(cause_of_death) + ' and the leader lost a life')
            else:
                game.cur_events_list.append(choice(cause_of_death))
            cat.die()
            other_cat.die()

        elif not random.getrandbits(6):  #Death with Personalities (1/64)
            murder_chance = 20
            name = str(cat.name)
            countdown = int(len(Cat.all_cats) / 3)
            other_cat = choice(list(Cat.all_cats.values()))
            while cat == other_cat or other_cat.dead or other_cat.exiled:
                other_cat = choice(list(Cat.all_cats.values()))
                countdown-=1
                if countdown <= 0:
                    return
            other_name = str(other_cat.name)
            # murdering leader/deputy
            if cat.trait in ['bloodthirsty', 'vengeful']:
                murder_chance = 10
            if cat.trait in ['bloodthirsty', 'ambitious', 'vengeful', 'sneaky'] and cat.status in ['warrior', 'deputy']\
                and randint(1, murder_chance) == 1:
                if cat.status == 'deputy' and other_cat.status == 'leader' and current_lives <= 6:
                        cause_of_death = [
                            name + ' murdered ' + other_name +
                            ' in cold blood to take their place',
                            name + ' murdered ' + other_name +
                            ' to take their place and made it look like an accident'
                        ]
                        game.clan.leader_lives = 0
                        other_cat.die()
                        game.cur_events_list.append(choice(cause_of_death))
                elif cat.status == 'deputy' and other_cat.status == 'leader' and current_lives >= 7:
                        cause_of_death = [
                        name + ' murdered ' + other_name +
                        ' to take their place, but the leader had more lives than they expected. ' +
                        other_name + ' retaliated and killed ' + name + ' in self-defense'
                        ]
                        liveslost = choice([1, 2, 3, 4])
                        game.clan.leader_lives = current_lives - liveslost                            
                        cat.die()
                        game.cur_events_list.append(choice(cause_of_death))
                elif cat.status == 'warrior':
                        if other_cat.status == 'leader' and current_lives <= 6:
                            cause_of_death = [
                                name + ' murdered ' + other_name + ' in cold blood in hopes of taking their place',
                                name + ' murdered ' + other_name + ' in cold blood and made it look accidental in hopes of taking their place'
                            ]
                            if other_cat == 'leader':
                                game.clan.leader_lives -= 10
                            other_cat.die()
                            game.cur_events_list.append(choice(cause_of_death))
                        elif other_cat == 'leader' and current_lives >= 7:
                            cause_of_death = [
                            name + ' murdered ' + other_name +
                            ' in hopes of taking their place, but the leader had more lives than they expected. ' +
                            other_name + ' retaliated and killed ' + name + ' in self-defense'
                            ]
                            liveslost = choice([1, 2, 2, 2, 3, 3, 3, 4])
                            game.clan.leader_lives = current_lives - liveslost
                            cat.die()
                            game.cur_events_list.append(choice(cause_of_death))
                        elif other_cat.status == 'deputy':
                            cause_of_death = [
                            name + ' murdered ' + other_name +
                            ' in cold blood in hopes of taking their place',
                            name + ' murdered ' + other_name +
                            ' in cold blood and made it look accidental in hopes of taking their place'
                            ]
                            other_cat.die()
                            game.cur_events_list.append(choice(cause_of_death))                        
            # just murder
            elif cat.trait in ['bloodthirsty', 'vengeful', 'sadistic'] and not int(random.random() * murder_chance):
                    if other_cat.status == 'leader' and current_lives <= 6:
                        cause_of_death = [
                        name + ' murdered ' + other_name +
                        ' in cold blood ',
                        name + ' murdered ' + other_name +
                        ' in cold blood and made it look accidental'
                        ]
                        game.clan.leader_lives -= 10
                        other_cat.die()
                        game.cur_events_list.append( choice(cause_of_death) + ' at ' + str(other_cat.moons + 1) + ' moons old')
                elif cat.status in [ 'medicine cat', 'medicine cat apprentice' ] and\
                    cat.trait in ['bloodthirsty', 'vengeful', 'sadistic']:
                    if randint(1, murder_chance) == 1:
                        cause_of_death = [
                            name + ' killed ' + other_name + ' by giving them ' + 
                            choice('deathberries', 'foxglove seeds', 'nightshade berries', 'water hemlock'),
                            name + ' killed ' + other_name + ' by consciously giving them the wrong herbs'
                        ]
                        liveslost = choice([1, 2, 3, 4])
                        game.clan.leader_lives = current_lives - liveslost
                        cat.die()
                        game.cur_events_list.append(choice(cause_of_death))
                    else:
                        cause_of_death = [
                        name + ' murdered ' + other_name +
                        ' in cold blood ',
                        name + ' murdered ' + other_name +
                        ' in cold blood and made it look accidental'
                        ]
                        other_cat.die()
                        game.cur_events_list.append(choice(cause_of_death))
            elif cat.status in ['medicine cat', 'medicine cat apprentice']\
            and cat.trait in ['bloodthirsty', 'vengeful', 'sadistic'] and not int(random.random() * murder_chance):
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
                other_cat.die()
                game.cur_events_list.append(
                        choice(cause_of_death) + ' at ' +
                        str(other_cat.moons + 1) + ' moons old')

        elif cat.moons > randint(150, 200):  # extra chance of cat dying to age
            if not int(random.random() * 5):  # 1/5
                if cat.status != 'leader':
                    cat.die()
                    game.cur_events_list.append(
                        str(cat.name) +
                        ' has passed due to their old age at ' +
                        str(cat.moons + 1) + ' moons old')
                else:
                    game.clan.leader_lives -= 1
                    cat.die()
                    game.cur_events_list.append(
                        str(cat.name) +
                        ' has lost a life due to their old age at ' +
                        str(cat.moons + 1) + ' moons old')
            if cat.status == 'leader' and cat.moons > 269:
                game.clan.leader_lives -= 10
                cat.die()
                game.cur_events_list.append(
                    str(cat.name) + ' has passed due to their old age at ' +
                    str(cat.moons + 1) + ' moons old')

        if game.settings.get('disasters') is True:
            alive_count = 0
            alive_cats = []
            for cat in list(Cat.all_cats.values()):
                if not cat.dead and not cat.exiled and cat.status != 'leader':
                    alive_count += 1
                    alive_cats.append(cat)
            if game.clan.all_clans:
                other_clan = game.clan.all_clans
            addition = randint(0, 20)
            # Are death_chance & dead_count unused? Should maybe be removed if so... -Shou
            death_chance = int(alive_count / 3)
            if addition == 1:
                death_chance = int(death_chance + randint(0, 10) / 2)
            else:
                death_chance = death_chance
            dead_count = int(death_chance / 5)
            if alive_count > 15:
                chance = int(alive_count / 10)
                if randint(chance, 1000) == 999:
                    disaster = []
                    dead_cats = random.sample(alive_cats, 5) # alive_cats, death_count for when scaling is added
                    name1 = str(dead_cats[0].name)
                    name2 = str(dead_cats[1].name)
                    name3 = str(dead_cats[2].name)
                    name4 = str(dead_cats[3].name)
                    name5 = str(dead_cats[4].name)
                    if cat.status in dead_cats != 'kitten':
                        disaster.extend([
                            ' drown after the camp becomes flooded',
                            ' are killed in a battle against ' +
                            choice(other_clan).name + 'Clan',
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
                    else:
                        disaster.extend([
                            ' drown after the camp becomes flooded',
                            ' are killed after a fire rages through the camp',
                            ' go missing in the night',
                            ' are killed after a badger attack',
                            ' die to a greencough outbreak',
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

                    game.cur_events_list.append("{name1}, {name2}, {name3}, + {name4}, and {name5} {choice(disaster)}")
                    for cat in dead_cats:
                        cat.die()

    def handle_illnesses_or_illness_deaths(self, cat):
        """ 
        This function will handle:
            - classic mode: death events with illnesses
            - expanded mode: getting a new illness (extra function in own class)
        Returns: 
            - boolean if a death event occurred or not
        """
        # get the general information about the cat and a random other cat
        triggered = False
        other_cat = choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.status == 'leader' or other_cat.exiled:
            other_cat = choice(list(Cat.all_cats.values()))
            countdown-=1
            if countdown <= 0:
                return
        
        name = str(cat.name)
        other_name = str(other_cat.name)

        if game.clan.game_mode == 'expanded':
            return self.condition_events.handle_illnesses(cat, game.clan.current_season)
        
        if game.clan.game_mode == 'classic':
            # leader loses lives
            if randint(1, 100) == 1 and cat.status == 'leader':
                if game.clan.current_season in ['Leaf-fall', 'Leaf-bare']:
                    cause_of_death = [
                        name + ' lost a life due to greencough',
                        name + ' lost a life due to whitecough',
                        name + ' lost a life due to yellowcough',
                    ]
                    game.clan.leader_lives -= 1
                    cat.die()
                    game.cur_events_list.append(
                        choice(cause_of_death) + ' at ' + str(cat.moons + 1) +' moons old')
            elif randint(1,200) == 1 and cat.status == 'leader':
                all_lives = randint(1, 10)
                if all_lives != 1:
                    lostlives = choice([2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6])
                    if cat.moons >= 130 and game.clan.current_season in ['Leaf-fall', 'Leaf-bare']:
                        cause_of_death = [
                            name + ' lost ' + str(lostlives) +
                            ' lives due to greencough', name + ' lost ' +
                            str(lostlives) + ' lives due to whitecough',
                            name + ' lost ' + str(lostlives) +
                            ' lives due to yellowcough', name + ' lost ' +
                            str(lostlives) + ' lives due to an illness'
                        ]
                        game.clan.leader_lives = game.clan.leader_lives - lostlives
                cat.die()
                game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons + 1) + ' moons old')
            # normal death
            elif randint(1, 400) == 1:
                triggered = True
                cause_of_death = []

                # STATUS
                if cat.status == 'kitten':
                    if game.clan.current_season == 'Leaf-bare':
                        cause_of_death.extend([
                            name + ' died of greencough',
                            name + ' died of kittencough',
                            name + ' was too weak to fight off whitecough and passed',
                            name + ' caught a cold and slowly faded'
                        ])
                elif cat.status == 'apprentice':
                    cause_of_death.extend([
                        name + ' died from infected wounds'
                    ])
                elif cat.status == 'warrior' or cat.status == 'deputy':
                    cause_of_death.extend([
                        name + ' died from infected wounds'
                    ])
                elif cat.status == 'elder':
                    if game.clan.current_season == 'Leaf-bare':
                        cause_of_death.extend([
                            name + ' was already feeling weak and a case of whitecough finished them off',
                            name + ' was too weak to recover from an illness and passed',
                            'Weakened by a lack of prey, ' + name + ' couldn\'t fight off whitecough and passed',
                            name + ' was taken quickly by a case of greencough'
                        ])
                elif cat.status == 'leader':
                    # reset the cause_of_death, because for leaders the text is different
                    cause_of_death = [
                        name + ' lost a life to greencough',
                        name + ' lost a life from infected wounds'
                    ]
                elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
                    cause_of_death.extend([])
                elif cat.status == 'deputy':
                    cause_of_death.extend([])

                if cat.status == 'leader':
                    game.clan.leader_lives -= 1

                if len(cause_of_death) > 1:
                    cat.die()
                    game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons + 1) + ' moons old')
                else:
                    triggered = False
            # multiple deaths
            elif randint(1, 500) == 1:
                triggered = True
                cause_of_death = []
                if game.clan.current_season == 'Leaf-bare':
                    if cat.status == 'kitten' and other_cat.status == 'kitten':
                        cause_of_death = [
                            'Greencough reaches the nursery. ' + name + ' and ' + other_name + ' die',
                            name + ' and ' + other_name + ' die from a bout of kittencough',
                            name + ' and ' + other_name + ' catch whitecough and fade away quickly'
                        ]
                    else:
                        cause_of_death = [
                            name + ' and ' + other_name + ' die of greencough',
                            name + ' and ' + other_name + ' die of yellowcough',
                            'A bad case of greencough strikes, and ' + name + ' and ' + other_name + ' die'
                        ]
                if len(cause_of_death) > 1:
                    if cat.status == 'leader' or other_cat.status == 'leader':
                        game.clan.leader_lives -= 1
                        game.cur_events_list.append(choice(cause_of_death) + ' and the leader lost a life')
                    else:
                        game.cur_events_list.append(choice(cause_of_death))
                    cat.die()
                    other_cat.die()
                else:
                    triggered = False

        return triggered

    def coming_out(self, cat):
        """turnin' the kitties trans..."""
        if cat.genderalign == cat.gender:
            if cat.moons < 6:
                return

            if cat.age == 'adolescent':
                transing_chance = random.getrandbits(8)  # 2/256
            elif cat.age == 'young adult':
                transing_chance = random.getrandbits(9)  # 2/512
            else:
                # adult, senior adult, elder
                transing_chance = random.getrandbits(10)  # 2/1028
                
            if transing_chance:
                # transing_chance != 0, no trans kitties today...
                return

            if random.getrandbits(1):  # 50/50
                if cat.gender == "male":
                    cat.genderalign = "trans female"
                else:
                    cat.genderalign = "trans male"
            else:
                cat.genderalign = "nonbinary"
                    
            if cat.gender == 'male':
                gender = 'tom'
            else:
                gender = 'she-cat'
            game.cur_events_list.append(f"{cat.name} has realized that {gender} doesn't describe how they feel anymore")

events_class = Events()
