from .cats import *
from .buttons import *


class Events(object):
    all_events = {}

    def __init__(self, e_type=None, **cats):
        self.e_type = e_type
        self.ID = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9))
        if e_type is not None:
            # Leave "e_type" empty for example class
            self.all_events[self.ID] = self
        self.cats = cats
        self.at_war = False
        self.enemy_clan = None
        self.living_cats = 0

    def one_moon(self):
        if game.switches['timeskip']:
            game.switches['save_clan'] = False
            self.living_cats = 0
            self.check_clan_relations()
            game.patrolled.clear()
            for cat in cat_class.all_cats.copy().values():
                if not cat.dead:
                    self._extracted_from_one_moon_7(cat)
                else:
                    cat.dead_for += 1
            cat_class.thoughts()
            game.clan.age += 1
            if game.settings.get('autosave') is True and game.clan.age % 5 == 0:
                cat_class.save_cats()
                game.clan.save_clan()
            game.clan.current_season = game.clan.seasons[game.clan.age % 12]
            game.event_scroll_ct = 0
            has_med = any(str(cat.status) in {"medicine cat", "medicine cat apprentice"} and not cat.dead for cat in cat_class.all_cats.values())

            if not has_med:
                game.cur_events_list.insert(0, f"{game.clan.name}Clan has no medicine cat!")
            if game.clan.deputy == 0 or game.clan.deputy is None or game.clan.deputy.dead:
                game.cur_events_list.insert(0, f"{game.clan.name}Clan has no deputy!")
            if game.clan.leader.dead:
                game.cur_events_list.insert(0, f"{game.clan.name}Clan has no leader!")
        game.switches['timeskip'] = False

    # TODO Rename this here and in `one_moon`
    def _extracted_from_one_moon_7(self, cat):
        self.living_cats += 1
        cat.in_camp = 1
        self.perform_ceremonies(cat)
        self.handle_relationships(cat)
        self.invite_new_cats(cat)
        self.have_kits(cat)
        self.other_interactions(cat)
        self.gain_scars(cat)
        self.handle_deaths(cat)
        self.check_age(cat)

    def check_clan_relations(self):
        if len(game.clan.all_clans) > 0:
            for other_clan in game.clan.all_clans:
                war_notice = ''
                if int(other_clan.relations) < 7:
                    self.at_war = True
                    self.enemy_clan = f'{str(other_clan.name)}Clan'
                    war_notice = choice(
                        [f'War rages between {game.clan.name}Clan and {other_clan.name}Clan', f'{other_clan.name}Clan has taken some of {game.clan.name}' + "Clan\'s territory.",
                         f'{game.clan.name}Clan has claimed some of {other_clan.name}' + "Clan\'s territory",
                         f'{other_clan.name}Clan attempted to break into your camp during the war', f'The war against {other_clan.name}Clan continues.',
                         f'{game.clan.name}Clan is starting to get tired of the war against {other_clan.name}Clan'])

                if war_notice:
                    game.cur_events_list.append(war_notice)

    def perform_ceremonies(self, cat):
        if game.clan.leader.dead and game.clan.deputy is not None and not game.clan.deputy.dead:
            game.clan.new_leader(game.clan.deputy)
            game.cur_events_list.append(f'{str(game.clan.deputy.name)} has been promoted to the new leader of the clan')

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
                    game.cur_events_list.append(f'{str(cat.name)} has started their apprenticeship')
                    cat.update_mentor()
                elif cat.status == 'apprentice' and cat.age == 'young adult':
                    self._extracted_from_perform_ceremonies_19(cat, 'warrior', ' has earned their warrior name')

                elif cat.status == 'medicine cat apprentice' and cat.age == 'young adult':
                    self._extracted_from_perform_ceremonies_19(cat, 'medicine cat', ' has earned their medicine cat name')
                    game.clan.new_medicine_cat(cat)
                elif cat.status == 'warrior' and cat.age == 'elder' and len(cat.apprentice) < 1:
                    cat.status_change('elder')
                    game.cur_events_list.append(f'{str(cat.name)} has retired to the elder den')
                elif cat.status == 'deputy' and cat.age == 'elder' and len(cat.apprentice) < 1:
                    cat.status_change('elder')
                    game.clan.deputy = None
                    game.cur_events_list.append(f'The deputy {str(cat.name)} has retired to the elder den')
            if cat.status in ['warrior', 'deputy'] and cat.age == 'elder' and len(cat.apprentice) < 1:
                cat.status_change('elder')
                game.cur_events_list.append(f'{str(cat.name)} has retired to the elder den')

    # TODO Rename this here and in `perform_ceremonies`
    def _extracted_from_perform_ceremonies_19(self, cat, arg1, arg2):
        cat.status_change(arg1)
        cat.update_mentor()
        game.cur_events_list.append(f'{str(cat.name)}{arg2}')

    def gain_scars(self, cat):
        if cat.specialty is not None and cat.specialty2 is not None or cat.age == 'kitten':
            return
        name = str(cat.name)
        scar_text = []
        if cat.age in ['adolescent', 'young adult']:
            chance = randint(0, 50)
        elif cat.age in ['adult', 'senior adult']:
            chance = randint(0, 70)
        else:
            chance = randint(0, 90)
        if chance == 1:
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']))
                else:
                    scar_text.extend([f'{name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                      f'{name} earned a scar defending the territory', f'{name} earned a scar protecting the kits', f'{name} is injured after falling into a river',
                                      f'{name} is injured by enemy warriors after accidentally wandering over the border', f'{name} is injured after messing with a twoleg object'])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']))
                else:
                    scar_text.extend([f'{name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                      f'{name} earned a scar defending the territory', f'{name} earned a scar protecting the kits', f'{name} is injured after falling into a river',
                                      f'{name} is injured by enemy warriors after accidentally wandering over the border', f'{name} is injured after messing with a twoleg object'])
        if scar_text:
            game.cur_events_list.append(choice(scar_text))

    def handle_relationships(self, cat):
        other_cat = choice(list(cat_class.all_cats.values()))
        if randint(1, 50) == 1:
            if cat != other_cat and not other_cat.dead and cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice', 'medicine cat'] and other_cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice', 'medicine cat'] and cat.age == other_cat.age and not {cat, cat.parent1, cat.parent2}.intersection(
                {other_cat, other_cat.parent1, other_cat.parent2}) and cat.mate is None and other_cat.mate is None:
                game.cur_events_list.append(f'{str(cat.name)} and {str(other_cat.name)} have become mates')

                cat.mate = other_cat.ID
                other_cat.mate = cat.ID
        elif randint(1, 50) == 1:
            if cat.mate == other_cat.ID:
                game.cur_events_list.append(f'{str(cat.name)} and {str(other_cat.name)} have broken up')
                cat.mate = None
                other_cat.mate = None

    def invite_new_cats(self, cat):
        chance = 100
        if self.living_cats < 10:
            chance = 100
        elif self.living_cats > 50:
            chance = 700
        elif self.living_cats > 30:
            chance = 300
        if randint(1, chance) == 1 and cat.age != 'kitten':
            name = str(cat.name)
            type_of_new_cat = choice([1, 2, 3, 4, 5, 6])
            if type_of_new_cat == 1:
                kit = Cat(moons=0)
                game.clan.add_cat(kit)
                kit_text = [f'{name} finds an abandoned kit and names them {str(kit.name)}',
                            f'A loner brings their kit named {str(kit.name.prefix)} to the clan, stating they no longer can care for them']
                game.cur_events_list.append(choice(kit_text))
                self.check_age(kit)

            elif type_of_new_cat == 2:
                self._extracted_from_invite_new_cats_19(name)

            elif type_of_new_cat == 3:
                loner = Cat(status='warrior', moons=randint(12, 120))
                loner.skill = 'formerly a loner'
                game.clan.add_cat(loner)
                loner_text = [f'{name} finds a loner who joins the clan', f'A loner says that they are interested in clan life and joins the clan']
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append('The loner changes their name to ' + str(loner.name))
                self.check_age(loner)

            elif type_of_new_cat == 4:
                warrior = Cat(status='warrior', moons=randint(12, 150))
                game.clan.add_cat(warrior)
                warrior_text = []
                if len(game.clan.all_clans) > 0:
                    warrior_text.extend([f'{name} finds a warrior from {str(choice(game.clan.all_clans).name)}Clan named {str(warrior.name)} who asks to join the clan',
                                         f'An injured warrior from {str(choice(game.clan.all_clans).name)}Clan asks to join in exchange for healing'])
                else:
                    warrior_text.extend([f'{name} finds a warrior from a different clan named {str(warrior.name)} who asks to join the clan'])
                game.cur_events_list.append(choice(warrior_text))
                self.check_age(warrior)

            elif type_of_new_cat == 5:
                self._extracted_from_invite_new_cats_47(name)
            elif type_of_new_cat == 6:
                loner = Cat(status='warrior', moons=randint(12, 120))
                self._extracted_from_invite_new_cats_59(loner)
                loner_text = [f'{name} finds a kittypet named {choice(names.loner_names)} who wants to join the clan']
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append('The kittypet changes their name to ' + str(loner.name))
                self.check_age(loner)

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
        loner = Cat(prefix=loner_name, gender=choice(['female', 'male']), status='warrior', moons=randint(12, 120), suffix='')
        self._extracted_from_invite_new_cats_59(loner)
        loner_text = [f'{name} finds a kittypet named {str(loner_name)} who wants to join the clan', f'A kittypet named {str(loner_name)} stops {name} and asks to join the clan']
        game.cur_events_list.append(choice(loner_text))
        game.cur_events_list.append(str(loner_name) + ' decides to keep their name')

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_19(self, name):
        loner_name = choice(names.loner_names)
        loner = Cat(prefix=loner_name, gender=choice(['female', 'male']), status='warrior', moons=randint(12, 120), suffix='')
        loner.skill = 'formerly a loner'
        game.clan.add_cat(loner)
        loner_text = [f'{name} finds a loner named {str(loner.name)} who joins the clan',
                      f'A loner named {str(loner.name)} waits on the border for a patrol, asking to join the clan']
        game.cur_events_list.append(choice(loner_text))
        game.cur_events_list.append(str(loner_name) + ' decides to keep their name')
        self.check_age(loner)

    def other_interactions(self, cat):
        if randint(1, 50) != 1:
            return
        interactions = []
        other_cat = choice(list(cat_class.all_cats.values()))
        while cat == other_cat or other_cat.dead:
            other_cat = choice(list(cat_class.all_cats.values()))
        name = str(cat.name)
        other_name = str(other_cat.name)
        if cat.status in ['warrior', 'deputy', 'leader'] and randint(1, 4) == 1 and game.settings.get('retirement') is True:
            game.cur_events_list.append(f'{name} retires to the elders den after injuries sustained defending {other_name}')
            cat.status_change('elder')
            return
        if cat.status == 'kitten':
            interactions.extend([f'{name} is scolded after sneaking out of camp', f'{name} falls into a river but is saved by {other_name}'])
        elif cat.status in ['apprentice', 'medicine cat apprentice']:
            interactions.extend([f'{name} is scolded after sneaking out of camp', f'{name} falls into a river but is saved by {other_name}',
                                 name + " accidentally trespasses onto another clan\'s territory"])
            if other_cat.status == 'apprentice':
                interactions.append(f'{name} sneaks out of camp with {other_name}')
        elif cat.status == 'warrior':
            interactions.extend([name + " is caught outside of the clan\'s territory", f'{name} is caught breaking the warrior code', f'{name} went missing for a few days',
                                 f'{name} believes they are a part of the new prophecy'])
        elif cat.status == 'medicine cat':
            interactions.extend(
                [f'{name} learns of a new prophecy', f'{name} is worried about an outbreak of greencough', f'{name} is worried about how low their herb stores has gotten',
                 f'{name} visits the other medicine cats'])
        elif cat.status == 'deputy':
            interactions.extend([f'{name} thinks about retiring', f'{name} travels to the other clans to bring them an important message'])
        elif cat.status == 'leader':
            interactions.extend(
                [f'{name} thinks about retiring', name + " confesses they don\'t have many lives left", f'{name} calls a clan meeting to give an important announcement'])
            if other_cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice']:
                interactions.append(f'{name} confesses to {other_name} that the responsibility of leadership is crushing them')
            elif other_cat.status == 'apprentice':
                interactions.append(f'{name} assesses {other_name}' + "\'s progress")
        elif cat.status == 'elder':
            interactions.extend([f'{name} is brought back to camp after wandering off'])
        if cat.age == other_cat.age:
            interactions.extend([f'{name} tries to convince {other_name} to run away together'])

        game.cur_events_list.append(choice(interactions))

    def handle_deaths(self, cat):
        if randint(1, 400) == 1:
            name = str(cat.name)
            cause_of_death = [name + ' was murdered', name + ' died of greencough', 'A tree fell in camp and killed ' + name, name + ' was found dead near a fox den']
            if cat.status == 'kitten':
                cause_of_death.extend([name + ' fell into a river and drowned', name + ' was taken by a hawk', name + ' grew weak as the days passed and died',
                                       name + ' was killed after sneaking out of camp', name + ' died after accidentally eating deathberries'])
                if game.clan.current_season == 'Leaf-bare':
                    cause_of_death.extend([name + ' was found dead in the snow', name + ' froze to death in a harsh snowstorm',
                                           name + ' disappeared from the nursery and was found dead in the territory'])
                if game.clan.current_season == 'Greenleaf':
                    cause_of_death.extend([name + ' died to overheating'])
            elif cat.status == 'apprentice':
                cause_of_death.extend([name + ' died in a training accident', name + ' was killed by enemy warriors after accidentally wandering over the border',
                                       name + ' went missing and was found dead', name + ' died in a border skirmish'])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([name + ' was crushed to death by an avalanche', name + ' fell from a cliff and died'])
                if game.clan.biome == "Beach":
                    cause_of_death.extend([name + ' was washed out to sea and drowned', name + ' was poisoned by a sea creature and died'])
            elif cat.status == 'warrior' or cat.status == 'deputy' or cat.status == 'leader':
                if len(game.clan.all_clans) > 0:
                    cause_of_death.append(name + ' was found dead near the ' + choice(game.clan.all_clans).name + 'Clan border')
                cause_of_death.extend([name + ' died from infected wounds', name + ' went missing and was found dead'])
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by enemy ' + self.enemy_clan + ' warriors', name + ' was killed by enemy ' + self.enemy_clan + ' warriors',
                                           name + ' was killed by enemy ' + self.enemy_clan + ' warriors', name + ' died in a border skirmish'])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([name + ' was crushed by an avalanche', name + ' fell from a cliff and died'])
                if game.clan.biome == "Beach":
                    cause_of_death.extend([name + ' was washed out to sea and drowned', name + ' was poisoned by a sea creature and died'])
            elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
                cause_of_death.extend(['The herb stores were damaged and ' + name + ' was murdered by an enemy warrior'])
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by a ' + self.enemy_clan + ' warrior while pulling an injured cat out of the battlefield'])
            if cat.status == 'deputy' or cat.status == 'leader':
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by the ' + self.enemy_clan + ' deputy', name + ' was killed by the ' + self.enemy_clan + ' leader'])
            self.dies(cat)
            game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons) + ' moons old')
        elif randint(1, 500) == 1:  # multiple deaths
            name = str(cat.name)
            other_cat = choice(list(cat_class.all_cats.values()))
            while cat == other_cat or other_cat.dead:
                other_cat = choice(list(cat_class.all_cats.values()))
            other_name = str(other_cat.name)
            cause_of_death = [name + ' and ' + other_name + ' die of greencough', name + ' and ' + other_name + ' die of yellowcough',
                              name + ' and ' + other_name + ' die from eating poisoned prey']
            if cat.status != 'kitten' and other_cat.status != 'kitten':
                cause_of_death.extend(
                    [name + ' and ' + other_name + ' are killed in a border skirmish', name + ' and ' + other_name + ' are killed in a battle against a gang of rogues'])
            if cat.mate is not None and cat.age == other_cat.age and other_cat.mate is None:
                self.dies(cat)
                game.cur_events_list.append(name + ' is killed by ' + other_name + ' in an argument over ' + str(cat_class.all_cats.get(cat.mate).name))
                return
            self.dies(cat)
            self.dies(other_cat)
            game.cur_events_list.append(choice(cause_of_death))
        elif cat.moons > randint(150, 200):  # extra chance of cat dying to age
            if choice([1, 2, 3, 4, 5, 6]) == 1:
                self.dies(cat)
                game.cur_events_list.append(str(cat.name) + ' has passed due to their old age at ' + str(cat.moons) + ' moons old')
        if game.settings.get('disasters') is True:
            alive_count = 0
            alive_cats = []
            for cat in list(cat_class.all_cats.values()):
                if not cat.dead:
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
                    disaster.extend([' drown after the camp becomes flooded', ' are killed in a battle against ' + choice(names.normal_prefixes) + 'Clan',
                                     ' are killed after a fire rages through the camp', ' are killed in an ambush by a group of rogues', ' go missing in the night',
                                     ' are killed after a badger attack', ' die to a greencough outbreak', ' are taken away by twolegs', ' eat poisoned freshkill and die'])
                    if game.clan.current_season == 'Leaf-bare':
                        disaster.extend([' die after freezing from a snowstorm', ' starve to death when no prey is found'])
                    elif game.clan.current_season == 'Greenleaf':
                        disaster.extend([' die after overheating', ' die after the water dries up from drought'])

                    game.cur_events_list.append(name1 + ', ' + name2 + ', ' + name3 + ', ' + name4 + ', and ' + name5 + choice(disaster))
                    for cat in dead_cats:
                        self.dies(cat)

    def dies(self, cat):  # This function is called every time a cat dies
        cat.dead = True
        for app in cat.apprentice.copy():
            app.update_mentor()
        cat.update_mentor()
        game.clan.add_to_starclan(cat)

    def have_kits(self, cat):
        # decide chances of having kits, and if it's possible at all
        chance = 0
        for kit in cat_class.all_cats.values():
            if str(kit.status) == 'kitten' and kit.parent1 is not None and not kit.dead:
                if cat_class.all_cats.get(kit.parent1) == cat or cat_class.all_cats.get(kit.parent2) == cat:
                    return
        if cat.mate is not None:
            if cat.mate in cat.all_cats:
                if cat_class.all_cats[cat.mate].dead:
                    chance = 0
                elif cat_class.all_cats[cat.mate].gender != cat.gender and cat_class.all_cats[cat.mate].age != 'elder':
                    chance = 25
                elif game.settings['no gendered breeding'] and cat_class.all_cats[cat.mate].age != 'elder' and chance is not None:
                    chance = 25
                else:
                    chance = 0
            else:
                game.cur_events_list.append("Warning: " + str(cat.name) + " has an invalid mate #" + str(cat.mate) + ". This has been unset.")
                cat.mate = None
        else:
            chance = 50
            if not game.settings['no unknown fathers']:
                chance = 0

        if cat.age in ['kitten', 'adolescent', 'elder'] or cat.example or (not game.settings['no gendered breeding'] and cat.gender == 'male'):
            chance = 0

        # Decide randomly if kits will be born, if possible
        if chance != 0:
            hit = randint(0, chance)
            if self.living_cats > 50:
                hit = randint(0, chance + 20)
            elif self.living_cats < 10:
                hit = randint(0, chance - 10)
            kits = choice([1, 1, 2, 2, 3, 3, 4])
            if hit == 1 and cat.mate is not None:
                if not cat.no_kits and not cat_class.all_cats.get(cat.mate).no_kits:
                    if game.cur_events_list is not None:
                        game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)')
                    else:
                        game.cur_events_list = [str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)']

                    for kit in range(kits):
                        kit = Cat(parent1=cat.ID, parent2=cat.mate, moons=0)
                        game.clan.add_cat(kit)
            elif hit == 1 and not cat.no_kits:
                game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)')

                for kit in range(kits):
                    kit = Cat(parent1=cat.ID, moons=0)
                    game.clan.add_cat(kit)

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
