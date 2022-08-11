from .buttons import *
from .cats import *
class Events(object):
    all_events = {}

    def __init__(self, e_type=None, **cats):
        self.e_type = e_type
        self.ID = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9))
        if e_type is not None:
            # Leave "e_type" empty for example class
            self.all_events[self.ID] = self
        self.cats = cats

    def kits_born(self, pos, parent1, parent2=None):
        if parent2 is not None:
            verdana.text('Kittens were born to ' + str(parent1.name) + ' and ' + str(parent2.name) + '!', pos)
        else:
            verdana.text('Kittens were born to ' + str(parent1.name) + '!', pos)

    def one_moon(self):  # Go forward in time one moon
        if game.switches['timeskip']:
            key_copy = tuple(cat_class.all_cats.keys())
            for index, i in enumerate(key_copy):
                cat = cat_class.all_cats[i]
                if not cat.dead:
                    cat.in_camp = 1
                    self.perform_ceremonies(cat)
                    self.gain_scars(cat)
                    self.create_interactions(cat, index, key_copy)
                    # self.create_mates
                    # self.invite_new_cats
                    self.have_kits(cat)
                    self.handle_deaths(cat)
                else:  # if cat was already dead
                    cat.dead_for += 1
            cat_class.thoughts()

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
            if cat.moons > cat_class.age_moons[cat.age][1]:
                # Give the cat a new age group, if old enough
                if cat.age != 'elder':
                    cat.age = cat_class.ages[cat_class.ages.index(cat.age) + 1]
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
            cat_number = choice(list(cat_class.all_cats.keys()))

            if cat_class.all_cats[cat_number].dead:
                if randint(1, 4) == 4:
                    append_str = str(cat.name) + ' mourns the loss of ' + str(
                        cat_class.all_cats[cat_number].name)
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
                                        cat_class.all_cats[cat_number].name)
                                    cat.status_change('elder')
                                else:
                                    append_str = str(cat.name) + ' earned a scar defending ' + str(
                                        cat_class.all_cats[cat_number].name) + ' from a ' + choice(
                                        ['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk'])
                        else:
                            cat.specialty = None
                            append_str = str(cat.name) + ' tried to convince ' + str(
                                cat_class.all_cats[cat_number].name) + ' to run away together.'
                    elif cat.status != 'kitten':
                        cat.specialty = None
                        append_str = str(cat.name) + ' tried to convince ' + str(
                            cat_class.all_cats[cat_number].name) + ' to run away together.'
                    elif game.clan.current_season != 'Leaf-bare':
                        cat.specialty = None
                        append_str = str(cat.name) + ' asks ' + str(
                            cat_class.all_cats[cat_number].name) + ' to show them ' + str(
                            game.clan.name) + 'Clan territory.'
                    else:
                        if game.clan.current_season == 'Leaf-bare' and cat.status == 'kitten':
                            self.dies(cat)
                            append_str = str(cat.name) + '  dies of a chill during a snowstorm.'
                        else:
                            append_str = str(cat.name) + '  feels lost.'

                # defends
                elif event_choice == 2:
                    if cat.status == 'leader':
                        append_str = str(cat.name) + ' confesses to ' + str(cat_class.all_cats[
                                                                                cat_number].name) + ' that the responsibility of leadership is crushing them.'
                    elif game.clan.current_season == 'Leaf-bare' and cat.status == 'kitten':
                        self.dies(cat)
                        append_str = str(cat_class.all_cats[cat_number].name) + ' finds ' + str(
                            cat.name) + ' dead in the snow.'
                    # sus
                elif event_choice == 3:
                    if cat.mate is not None and randint(1, 3) == 1 and cat_class.all_cats[cat_number].name != cat_class.all_cats[
                        cat.mate].name:
                        append_str = str(cat.name) + ' is killed by ' + str(
                            cat_class.all_cats[cat_number].name) + ' in an argument over ' + str(
                            cat_class.all_cats[cat.mate].name)
                        self.dies(cat)
                    elif cat.mate is not None:
                        append_str = str(cat.name) + ' breaks up with ' + str(
                            cat_class.all_cats[cat.mate].name)
                        cat_class.all_cats[cat.mate].mate = None
                        cat.mate = None
                    else:
                        valid_mates = 0
                        if not cat_class.all_cats[cat_number].dead and cat_class.all_cats[cat_number].age in [
                            'young adult', 'adult', 'senior adult', 'elder'] and \
                                cat != cat_class.all_cats[cat_number] and cat.ID not in [
                            cat_class.all_cats[cat_number].parent1, cat_class.all_cats[cat_number].parent2] and \
                                cat_class.all_cats[cat_number].ID not in [cat.parent1, cat.parent2] and \
                                cat_class.all_cats[cat_number].mate is None and \
                                (cat_class.all_cats[cat_number].parent1 is None or cat_class.all_cats[
                                    cat_number].parent1 not in [cat.parent1, cat.parent2]) and \
                                (cat_class.all_cats[cat_number].parent2 is None or cat_class.all_cats[
                                    cat_number].parent2 not in [cat.parent1, cat.parent2]):

                            # Making sure the ages are appropriate
                            if (cat.age in ['senior adult', 'elder'] and cat_class.all_cats[cat_number].age in [
                                'senior adult', 'elder']) or (cat_class.all_cats[
                                                                  cat_number].age != 'elder' and cat.age != 'elder' and cat.age != 'kitten' and cat.age != 'adolescent'):
                                valid_mates = 1

                        if cat_class.all_cats[cat_number].ID == cat.ID:
                            valid_mates = 0

                        if valid_mates:
                            cat.mate = cat_class.all_cats[cat_number].ID
                            cat_class.all_cats[cat_number].mate = cat.ID
                            append_str = str(cat.name) + ' and ' + str(
                                cat_class.all_cats[cat_number].name) + ' have become mates.'

                        else:
                            append_str = str(cat.name) + ' talks with ' + str(
                                cat_class.all_cats[cat_number].name) + ' about love.'

                    # angry mate
                elif event_choice == 4:
                    # training
                    if cat.status == 'apprentice':
                        append_str = str(cat.name) + ' trains with their mentor, ' + str(cat.mentor.name)
                    elif cat.age in ['adolescent', 'young adult', 'adult', 'senior adult']:
                        append_str = str(cat.name) + ' learns some new moves from ' + str(
                            cat_class.all_cats[cat_number].name)
                    else:
                        append_str = str(cat.name) + ' sneaks out of the camp with ' + str(
                            cat_class.all_cats[cat_number].name)

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
                            names.loner_names) + ' to join. They change their name to ' + str(kit.name) + ''
                        kit.skill = 'formerly a loner'

                elif event_choice == 6:
                    append_str = str(cat.name) + ' and ' + str(
                        cat_class.all_cats[cat_number].name) + ' die of a contagious disease'
                    self.dies(cat)
                    self.dies(cat_class.all_cats[cat_number])

            if game.cur_events_list is not None and append_str is not None and append_str != '':
                game.cur_events_list.append(append_str)

    def create_interactions2(self, cat):
        if randint(1, 50) == 1:
            interactions = []
            other_cat = cat_class.all_cats.get(choice(list(cat_class.all_cats.keys())))
            while cat == other_cat or other_cat.dead:
                other_cat = cat_class.all_cats.get(choice(list(cat_class.all_cats.keys())))
            name = str(cat.name)
            other_name = str(other_cat.name)
            event = choice([1, 1, 2])  # 1:general event 2:new cat joins
            if event == 1:
                if cat.status == 'kitten':
                    interactions.extend([name + ' is scolded after sneaking out of camp',
                                         name + ' falls into a river but is saved by ' + other_name])
                elif cat.status in ['apprentice', 'medicine cat apprentice']:
                    interactions.extend([name + ' is scolded after sneaking out of camp',
                                         name + ' falls into a river but is saved by ' + other_name,
                                         name + ' accidentally trespasses onto another clan\'s territory'])
                elif cat.status == 'warrior':
                    interactions.extend([name + ' is caught outside of the clan\'s territory',
                                         name + ' is caught breaking the warrior code',
                                         name + ' went missing for a few days',
                                         name + ' believes they are a part of the new prophecy'])
                elif cat.status == 'medicine cat':
                    interactions.extend(
                        [name + ' learns of a new prophecy', name + ' is worried about an outbreak of greencough',
                         name + ' is worried about how low their herb stores has gotten',
                         name + 'visits the other medicine cats'])
                elif cat.status == 'deputy':
                    interactions.extend([name + ' thinks about retiring',
                                         name + ' travels to the other clans to bring them an important message'])
                elif cat.status == 'leader':
                    interactions.extend(
                        [name + ' thinks about retiring', name + ' confesses they don\'t have many lives left',
                         name + ' calls a clan meeting to give an important announcement'])
                elif cat.status == 'elder':
                    interactions.extend([name + ' is brought back to camp after wandering off'])
                if cat.age == other_cat.age:
                    interactions.extend([name + ' tries to convince ' + other_name + ' to run away together'])
                if cat.mate == other_cat.ID:
                    if choice([1, 2, 3, 4]) == 1:
                        cat.mate = None
                        other_cat.mate = None
                        game.cur_events_list.append(name + ' and ' + other_name + ' have broken up')
                        return
                if cat.status not in ['kitten', 'apprentice'] and other_cat.status not in ['kitten',
                                                                                           'apprentice'] and cat.ID not in [
                    other_cat.parent1, other_cat.parent2] and other_cat.ID not in [cat.parent1,
                                                                                   cat.parent2] and cat.mate is None and other_cat.mate is None and cat.age == other_cat.age:
                    cat.mate = other_cat.ID
                    other_cat.mate = cat.ID
                    game.cur_events_list.append(name + ' and ' + other_name + ' have become mates')
                    return
            elif event == 2:
                if cat.age != 'kitten':
                    type_of_new_cat = choice([1, 1, 2, 3, 4, 5, 6])
                    if type_of_new_cat == 1:
                        kit = Cat(moons=0)
                        game.clan.add_cat(kit)
                        game.cur_events_list.extend([name + ' finds an abandoned kit and names them ' + str(kit.name)])
                    elif type_of_new_cat == 2:
                        loner_name = choice(names.loner_names)
                        loner = Cat(prefix=loner_name, gender=choice(['female', 'male']), status='warrior',
                                    moons=randint(12, 120), suffix='')
                        game.clan.add_cat(loner)
                        game.cur_events_list.extend([name + ' finds a loner named ' + str(
                            loner.name) + ' who wants to join the clan. They decide to keep their name'])
                    elif type_of_new_cat == 3:
                        loner = Cat(status='warrior', moons=randint(12, 120))
                        game.clan.add_cat(loner)
                        game.cur_events_list.extend([name + ' finds a loner named ' + choice(
                            names.loner_names) + ' who wants to join the clan. They change their name to ' + str(
                            loner.name)])
                    elif type_of_new_cat == 4:
                        warrior = Cat(status='warrior', moons=randint(12, 150))
                        game.clan.add_cat(warrior)
                        game.cur_events_list.extend(
                            [name + ' finds a warrior from ' + choice(names.normal_prefixes) + 'Clan named ' + str(
                                warrior.name) + ' who asks to join the clan'])
                    elif type_of_new_cat == 5:
                        loner_name = choice(names.loner_names)
                        loner = Cat(prefix=loner_name, gender=choice(['female', 'male']), status='warrior',
                                    moons=randint(12, 120), suffix='')
                        game.clan.add_cat(loner)
                        game.cur_events_list.extend(
                            [name + ' finds a kittypet named ' + str(
                                loner_name) + ' who wants to join the clan. They decide to keep their name'])
                    elif type_of_new_cat == 6:
                        loner = Cat(status='warrior', moons=randint(12, 120))
                        game.clan.add_cat(loner)
                        game.cur_events_list.extend([name + ' finds a kittypet named ' + choice(
                            names.loner_names) + ' who wants to join the clan. They change their name to ' + str(
                            loner.name)])

            if len(interactions) > 0:
                game.cur_events_list.append(choice(interactions))

    def handle_deaths(self, cat):
        if randint(1, 300) == 1:
            name = str(cat.name)
            cause_of_death = [name + ' was murdered', name + ' died of greencough',
                              'A tree fell in camp and killed ' + name,
                              name + ' was found dead near a fox den']
            if cat.status == 'kitten':
                cause_of_death.extend([name + ' fell into a river and drowned', name + ' was taken by a hawk',
                                       name + ' grew weak as the days passed and died',
                                       name + ' was killed after sneaking out of camp',
                                       name + ' died after accidentally eating deathberries'])
                if game.clan.current_season == 'Leaf-bare':
                    cause_of_death.extend(
                        [name + ' was found dead in the snow', name + ' froze to death in a harsh snowstorm',
                         name + ' disappeared from the nursery and was found dead in the territory'])
                if game.clan.current_season == 'Greenleaf':
                    cause_of_death.extend(
                        [name + ' died to overheating'])
            elif cat.status == 'apprentice':
                cause_of_death.extend([name + ' died in a training accident',
                                       name + ' was killed by enemy warriors after accidentally wandering over the border',
                                       name + ' went missing and was found dead', name + ' died in a border skirmish'])
            elif cat.status == 'warrior' or cat.status == 'deputy' or cat.status == 'leader':
                cause_of_death.extend([name + ' died from infected wounds',
                                       name + ' was killed by enemy ' + str(
                                           choice(names.normal_prefixes)) + 'Clan warriors',
                                       name + ' went missing and was found dead', name + ' died in a border skirmish'])
            if cat.status == 'deputy' or cat.status == 'leader':
                cause_of_death.extend(
                    [name + ' was killed by the ' + str(choice(names.normal_prefixes)) + 'Clan deputy',
                     name + ' was killed by the ' + str(choice(names.normal_prefixes)) + 'Clan leader'])
            self.dies(cat)
            game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons) + ' moons old')

        elif cat.moons > randint(150, 200):  # extra chance of cat dying to age
            if choice([1, 2, 3, 4, 5, 6]) == 1:
                self.dies(cat)
                game.cur_events_list.append(
                    str(cat.name) + ' has passed due to their old age at ' + str(cat.moons) + ' moons old')

    def dies(self, cat):  # This function is called every time a cat dies
        cat.dead = True
        cat.update_mentor()
        for app in cat.apprentice:
            app.update_mentor()
        game.clan.add_to_starclan(cat)

    def have_kits(self, cat):
        # decide chances of having kits, and if it's possible at all
        chance = 0
        if cat.mate is not None:
            if cat.mate in cat.all_cats:
                if cat_class.all_cats[cat.mate].dead:
                    chance = 0
                elif cat_class.all_cats[cat.mate].gender != cat.gender and cat_class.all_cats[
                    cat.mate].age != 'elder':
                    chance = 25
                elif game.settings['no gendered breeding'] and cat_class.all_cats[
                    cat.mate].age != 'elder' and chance is not None:
                    chance = 25
                else:
                    chance = 0
            else:
                game.cur_events_list.append(
                    "Warning: " + str(cat.name) + " has an invalid mate #" + str(cat.mate) + ". This has been unset.")
                cat.mate = None
        else:
            chance = 50
            if not game.settings['no unknown fathers']:
                chance = 0

        if cat.age in ['kitten', 'adolescent', 'elder'] or cat.example or \
                (not game.settings['no gendered breeding'] and cat.gender == 'male'):
            chance = 0

        # Decide randomly if kits will be born, if possible
        if chance != 0:
            hit = randint(0, chance)
            if len(game.clan.clan_cats) > 30:
                hit = randint(0, chance + 20)
            elif len(game.clan.clan_cats) < 10:
                hit = randint(0, chance - 10)
            kits = choice([1, 1, 2, 2, 3, 3, 4])
            if hit == 1 and cat.mate is not None:
                if game.cur_events_list is not None:
                    game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)')
                else:
                    game.cur_events_list = [str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)']

                for kit in range(kits):
                    kit = Cat(parent1=cat.ID, parent2=cat.mate, moons=0)
                    game.clan.add_cat(kit)
            elif hit == 1:
                game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)')

                for kit in range(kits):
                    kit = Cat(parent1=cat.ID, moons=0)
                    game.clan.add_cat(kit)



events_class = Events()
