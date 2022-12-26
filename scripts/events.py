from scripts.cat.cats import *
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.cat_relations.relation_events import *
from scripts.game_structure.load_cat import *
from scripts.events_module.condition_events import Condition_Events
from scripts.events_module.death_events import Death_Events


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
        self.death_events = Death_Events()

    def one_moon(self):
        game.cur_events_list = []
        game.relation_events_list = []
        game.ceremony_events_list = []
        game.birth_death_events_list = []
        game.health_events_list = []
        game.other_clans_events_list = []
        game.misc_events_list = []
        game.switches['saved_clan'] = False
        self.living_cats = 0
        self.new_cat_invited = False
        game.patrolled.clear()
        if any(str(cat.status) in {'leader', 'deputy', 'warrior', 'medicine cat', 'medicine cat apprentice',
                                   'apprentice'}
               and not cat.dead and not cat.outside for cat in Cat.all_cats.values()):
            game.switches['no_able_left'] = False
        self.relation_events.handle_pregnancy_age(game.clan)
        for cat in Cat.all_cats.copy().values():
            if not cat.outside:
                self.one_moon_cat(cat)
            else:
                # ---------------------------------------------------------------------------- #
                #                              exiled cat events                               #
                # ---------------------------------------------------------------------------- #
                # aging the cat
                cat.one_moon()
                cat.moons += 1
                if cat.moons == 6:
                    cat.age = 'adolescent'
                elif cat.moons == 12:
                    cat.age = 'adult'
                elif cat.moons == 100:
                    cat.age = 'elder'

                # killing exiled cats
                if cat.moons > randint(100, 200) and cat.exiled:
                    if choice([1, 2, 3, 4, 5]) == 1 and not cat.dead:
                        cat.dead = True
                        text = f'Rumors reach your clan that the exiled {str(cat.name)} has died recently.'
                        game.cur_events_list.append(text)
                        game.birth_death_events_list.append(text)

                if cat.exiled and cat.status == 'leader' and not cat.dead and randint(
                        1, 10) == 1:
                    game.clan.leader_lives -= 1
                    if game.clan.leader_lives > 0:
                        text = f'Rumors reach your clan that the exiled {str(cat.name)} lost a life recently.'
                        game.cur_events_list.append(text)
                        game.birth_death_events_list.append(text)
                    else:
                        text = f'Rumors reach your clan that the exiled {str(cat.name)} has died recently.'
                        game.cur_events_list.append(text)
                        game.birth_death_events_list.append(text)
                        cat.dead = True

                elif cat.exiled and cat.status == 'leader' and not cat.dead and randint(
                        1, 45) == 1:
                    game.clan.leader_lives -= 10
                    cat.dead = True
                    text = f'Rumors reach your clan that the exiled {str(cat.name)} has died recently.'
                    game.cur_events_list.append(text)
                    game.birth_death_events_list.append(text)
                    game.clan.leader_lives = 0

        # relationships have to be handled separately, because of the ceremony name change
        for cat in Cat.all_cats.copy().values():
            if cat.dead or cat.outside:
                continue
            # switches between the two death handles
            self.handle_outbreaks(cat)
            if random.getrandbits(1):
                triggered_death = self.handle_injuries_or_general_death(cat)
                if not triggered_death:
                    triggered_death = self.handle_illnesses_or_illness_deaths(cat)
            else:
                triggered_death = self.handle_illnesses_or_illness_deaths(cat)
                if not triggered_death:
                    triggered_death = self.handle_injuries_or_general_death(cat)

            if not cat.dead or cat.outside:
                self.relation_events.handle_relationships(cat)

        if Cat.grief_strings:
            remove_cats = []

            for ID in Cat.grief_strings.keys():
                check_cat = Cat.all_cats.get(ID)
                if check_cat.dead or check_cat.outside:
                    remove_cats.append(check_cat.ID)
            for ID in remove_cats:
                if ID in Cat.grief_strings.keys():
                    Cat.grief_strings.pop(ID)

            grief_strings = "<br><br>".join(Cat.grief_strings.values())
            game.cur_events_list.append(grief_strings)
            game.birth_death_events_list.append(grief_strings)
            game.relation_events_list.append(grief_strings)
            Cat.grief_strings.clear()

        self.check_clan_relations()

        # age up the clan
        game.clan.age += 1

        # autosave
        if game.settings.get('autosave') is True and game.clan.age % 5 == 0:
            game.save_cats()
            game.clan.save_clan()
            game.clan.save_pregnancy(game.clan)

        # change season
        game.clan.current_season = game.clan.seasons[game.clan.age % 12]

        game.event_scroll_ct = 0

        if game.clan.game_mode in ["expanded", "cruel season"]:
            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            med_fullfilled = medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med)
            if not med_fullfilled:
                string = f"{game.clan.name}Clan does not have enough healthy medicine cats! Cats will be sick/hurt " \
                         f"for longer and have a higher chance of dying. "
                game.cur_events_list.insert(0, string)
                game.health_events_list.insert(0, string)
        else:
            has_med = any(
                str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                and not cat.dead and not cat.outside
                for cat in Cat.all_cats.values())
            if not has_med:
                string = f"{game.clan.name}Clan has no medicine cat!"
                game.cur_events_list.insert(0, string)
                game.health_events_list.insert(0, string)

        if game.clan.deputy == 0 or game.clan.deputy is None or game.clan.deputy.dead or game.clan.deputy.outside or game.clan.deputy.retired:
            if game.settings.get('deputy') is True:
                random_count = 0
                while random_count < 30:
                    random_cat = str(random.choice(list(Cat.all_cats.keys())))
                    if not Cat.all_cats[random_cat].dead and not Cat.all_cats[random_cat].outside:
                        if Cat.all_cats[random_cat].status == 'warrior' and (
                                len(Cat.all_cats[random_cat].former_apprentices) > 0 or len(
                            Cat.all_cats[random_cat].apprentice) > 0):
                            Cat.all_cats[random_cat].status = 'deputy'
                            text = ''
                            if game.clan.deputy is not None:
                                if game.clan.deputy.dead and not game.clan.leader.dead and not game.clan.leader.exiled:
                                    text = str(game.clan.leader.name) + ' chooses ' + str(Cat.all_cats[
                                                                                              random_cat].name) + ' to take over as deputy. They know that ' + str(
                                        game.clan.deputy.name) + ' would agree.'
                                if not game.clan.deputy.dead and not game.clan.deputy.outside:
                                    text = str(Cat.all_cats[
                                                   random_cat].name) + ' has been chosen as the new deputy. The retired deputy nods their approval.'

                                if game.clan.deputy.outside:
                                    text = str(Cat.all_cats[
                                                   random_cat].name) + ' has been chosen as the new deputy. The Clan hopes that ' + str(
                                        game.clan.deputy.name) + ' would approve.'
                            else:
                                if Cat.all_cats[random_cat].trait == 'bloodthirsty':
                                    text = str(Cat.all_cats[
                                                   random_cat].name) + ' has been chosen as the new deputy. They look at the clan leader with an odd glint in their eyes.'
                                else:
                                    r = choice([1, 2, 3, 4, 5])
                                    if r == 1:
                                        text = str(Cat.all_cats[
                                                       random_cat].name) + ' has been chosen as the new deputy. The clan yowls their name in approval.'
                                    elif r == 2:
                                        text = str(Cat.all_cats[
                                                       random_cat].name) + ' has been chosen as the new deputy. The clan chants their name out in support of the choice.'
                                    elif r == 3:
                                        text = str(Cat.all_cats[
                                                       random_cat].name) + ' has been chosen as the new deputy. Some of the older clan members question the wisdom in this choice.'
                                    elif r == 4:
                                        text = str(Cat.all_cats[
                                                       random_cat].name) + ' has been chosen as the new deputy. They hold their head up high and promise to do their best for the clan.'
                                    else:
                                        text = str(Cat.all_cats[
                                                       random_cat].name) + ' has been chosen as the new deputy. They pray to StarClan that they are the right choice for the clan.'

                            game.clan.deputy = Cat.all_cats[random_cat]
                            game.cur_events_list.append(text)
                            game.ceremony_events_list.append(text)
                            break
                    random_count += 1
                if random_count == 30:
                    text = 'The clan decides that no cat is fit to be deputy'
                    game.cur_events_list.append(text)
                    game.ceremony_events_list.append(text)
            else:
                game.cur_events_list.insert(
                    0, f"{game.clan.name}Clan has no deputy!")

            # check for leader
            if game.clan.leader.dead or game.clan.leader.outside:
                self.perform_ceremonies(game.clan.leader)
                if game.clan.leader.dead or game.clan.leader.outside:
                    game.cur_events_list.insert(0, f"{game.clan.name}Clan has no leader!")

    game.switches['timeskip'] = False

    def handle_fading(self, cat):
        if game.settings["fading"] and not cat.prevent_fading and cat.ID != game.clan.instructor.ID and \
                not cat.faded:

            age_to_fade = 302
            # Handle opacity
            cat.opacity = int(100*(1-(cat.dead_for/age_to_fade)**5)+30)

            # Deal with fading the cat if they are old enough.
            if cat.dead_for > age_to_fade:
                print(str(cat.name) + " is fading away...")
                print("dead_for: " + str(cat.dead_for))
                # If order not to add a cat to the faded list twice, we can't remove them or add them to
                # faded cat list here. Rather, they are added to a list of cats that will be "faded" at the next save.
                game.cat_to_fade.append(cat.ID)
                cat.set_faded()  # This is a flag to ensure they behave like a faded cat in the meantime.

    def one_moon_cat(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                trigger events                                #
        # ---------------------------------------------------------------------------- #

        if cat.dead:
            cat.thoughts()
            cat.dead_for += 1
            self.handle_fading(cat) # Deal with fading.
            return

        self.living_cats += 1

        # prevent injured or sick cats from unrealistic clan events
        if cat.is_ill() or cat.is_injured():
            self.perform_ceremonies(cat)
            self.coming_out(cat)
            self.relation_events.handle_having_kits(cat, clan=game.clan)
            cat.one_moon()
            return

        # check for death/reveal/risks/retire caused by permanent conditions
        if cat.is_disabled():
            self.condition_events.handle_already_disabled(cat)
        self.perform_ceremonies(cat)  # here is age up included

        if not game.clan.closed_borders:
            self.invite_new_cats(cat)

        self.other_interactions(cat)
        self.coming_out(cat)
        self.gain_accessories(cat)
        if game.clan.game_mode == "classic" and not int(random.random() * 3):
            self.gain_scars(cat)
        self.relation_events.handle_having_kits(cat, clan=game.clan)

        # all actions, which do not trigger an event display and
        # are connected to cats are located in there
        cat.one_moon()

    def check_clan_relations(self):
        # ---------------------------------------------------------------------------- #
        #                      interactions with other clans                           #
        # ---------------------------------------------------------------------------- #

        if len(game.clan.all_clans) > 0 and randint(1, 5) == 1:
            war_notice = ''
            for other_clan in game.clan.all_clans:
                if int(other_clan.relations) <= 5:
                    if randint(1, 5) == 1 and self.time_at_war > 2:
                        self.at_war = False
                        self.time_at_war = 0
                        other_clan.relations = 10
                        text = 'The war against ' + str(other_clan.name) + 'Clan has ended.'
                        game.other_clans_events_list.append(text)
                        game.cur_events_list.append(text)
                    elif self.time_at_war == 0:
                        text = 'The war against ' + str(other_clan.name) + 'Clan has begun.'
                        game.other_clans_events_list.append(text)
                        game.cur_events_list.append(text)
                        self.time_at_war += 1
                        self.at_war = True
                    else:
                        self.enemy_clan = other_clan
                        possible_text = [
                            f'War rages between {game.clan.name}Clan and {other_clan.name}Clan.',
                            f'{other_clan.name}Clan has taken some of {game.clan.name}'
                            + "Clan\'s territory.",
                            f'{game.clan.name}Clan has claimed some of {other_clan.name}'
                            + "Clan\'s territory.",
                            f'{other_clan.name}Clan attempted to break into your camp during the war.',
                            f'The war against {other_clan.name}Clan continues.',
                            f'{game.clan.name}Clan is starting to get tired of the war against {other_clan.name}Clan.',
                            f'{game.clan.name}Clan warriors plan new battle strategies for the war.',
                            f'{game.clan.name}Clan warriors reinforce the camp walls.'
                        ]
                        if game.clan.medicine_cat is not None:
                            possible_text.extend([
                                'The medicine cats worry about having enough herbs to treat their clan\'s wounds.'
                            ])
                        war_notice = choice(possible_text)
                        self.time_at_war += 1
                        self.at_war = True
                    break
                elif int(other_clan.relations) > 30:
                    other_clan.relations = 10
                else:
                    self.at_war = False
            if war_notice:
                game.other_clans_events_list.append(war_notice)
                game.cur_events_list.append(war_notice)

    def perform_ceremonies(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                  ceremonies                                  #
        # ---------------------------------------------------------------------------- #

        # leader dying or being exiled and dep promotion to leader
        if (game.clan.leader.dead or game.clan.leader.outside) \
                and game.clan.deputy is not None and not game.clan.deputy.dead and not game.clan.deputy.outside:
            if game.clan.leader.exiled:
                text = str(game.clan.leader.name) + ' was exiled.'
                game.ceremony_events_list.append(text)
                game.cur_events_list.append(text)
            else:
                if game.clan.instructor.df is False:
                    text = str(game.clan.leader.name) + ' has lost their last life and has travelled to StarClan.'
                    game.birth_death_events_list.append(text)
                    game.cur_events_list.append(text)
                else:
                    text = str(
                        game.clan.leader.name) + ' has lost their last life and has travelled to the Dark Forest.'
                    game.birth_death_events_list.append(text)
                    game.cur_events_list.append(text)
            game.clan.new_leader(game.clan.deputy)
            game.clan.leader_lives = 9
            text = ''
            if (game.clan.deputy.trait == 'bloodthirsty'):
                text = f'{str(game.clan.deputy.name)} has become the new leader. They stare down at their clanmates with unsheathed claws, promising a new era for the clans.'
            else:
                c = choice([1,2,3])
                if c == 1:
                    text = str(game.clan.deputy.name.prefix) + str(game.clan.deputy.name.suffix) + ' has been promoted to the new leader of the clan. They travel immediately to the Moonstone to get their nine lives and are hailed by their new name, ' + str(game.clan.deputy.name) + '.'
                elif c == 2:
                    text = f'{str(game.clan.deputy.name)} has become the new leader of the clan. They vow that they will protect the clan, even at the cost of their nine lives.'
                elif c == 3:
                    text = f'{str(game.clan.deputy.name)} has received their nine lives and became the new leader of the clan. They feel like they are not ready for this new responsibility, but will try their best to do what is right for the clan.'
            game.ceremony_events_list.append(text)
            game.cur_events_list.append(text)
            self.ceremony_accessory = True
            self.gain_accessories(cat)
            game.clan.deputy = None

        # other ceremonies
        if not cat.dead:
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.status == 'medicine cat' and game.clan.medicine_cat is None:
                game.clan.medicine_cat = cat

            # retiring to elder den
            if cat.status in ['warrior', 'deputy'] and cat.age == 'elder' and len(cat.apprentice) < 1:
                if cat.status == 'deputy':
                    game.clan.deputy = None
                self.ceremony(cat, 'elder', ' has retired to the elder den.')
                cat.status_change('elder')

            # apprentice a kitten to either med or warrior
            if cat.moons == cat_class.age_moons[cat.age][1]:
                if cat.status == 'kitten':

                    # check if the medicine cat is an elder
                    has_elder_med = any(
                        cat.status == 'medicine cat' and cat.age == 'elder'
                        and not cat.dead and not cat.outside
                        for cat in Cat.all_cats.values())

                    very_old_med = any(
                        cat.status == 'medicine cat' and cat.moons >= 150
                        and not cat.dead and not cat.outside
                        for cat in Cat.all_cats.values())

                    # check if the clan has sufficient med cats
                    if game.clan.game_mode != 'classic':
                        has_med = medical_cats_condition_fulfilled(Cat.all_cats.values(),
                                                                   amount_per_med=get_amount_cat_for_one_medic(
                                                                       game.clan))
                    else:
                        has_med = any(str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                                      and not cat.dead and not cat.outside for cat in Cat.all_cats.values())
                    # check if a med cat app already exists
                    has_med_app = any(
                        cat.status == 'medicine cat apprentice'
                        and not cat.dead and not cat.outside
                        for cat in Cat.all_cats.values())

                    # assign chance to become med app depending on current med cat and traits
                    if has_elder_med is True and has_med is False:
                        chance = int(random.random() * 3)  # 3 is not part of the range
                    elif has_med is False and game.clan.game_mode != 'classic':
                        chance = int(random.random() * 8)
                    elif has_elder_med is False and has_med is True:
                        chance = int(random.random() * 91)
                    elif has_elder_med and has_med:
                        if very_old_med:
                            chance = int(random.random() * 20)
                        else:
                            chance = 0
                    else:
                        chance = int(random.random() * 41)

                    if chance in range(1, 10):
                        if cat.trait in ['polite', 'quiet', 'sweet', 'daydreamer']:
                            chance = 1
                    if has_med_app is False and chance == 1:
                        self.ceremony(cat, 'medicine cat apprentice', ' has chosen to walk the path of a medicine cat.')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    else:
                        self.ceremony(cat, 'apprentice', ' has started their apprenticeship.')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

                # promote to warrior
                elif cat.status == 'apprentice':
                    self.ceremony(cat, 'warrior', ' has earned their warrior name.')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

                # promote to med cat
                elif cat.status == 'medicine cat apprentice':
                    self.ceremony(cat, 'medicine cat', ' has earned their medicine cat name.')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

    def ceremony(self, cat, promoted_to, ceremony_text):
        # ---------------------------------------------------------------------------- #
        #                      promote cats and add to event list                      #
        # ---------------------------------------------------------------------------- #
        ceremony = []
        cat.status_change(promoted_to)

        if (promoted_to == 'warrior'):
            resource_directory = "resources/dicts/events/ceremonies/"
            TRAITS = None
            with open(f"{resource_directory}ceremony_traits.json", 'r') as read_file:
                TRAITS = ujson.loads(read_file.read())
            random_honor = choice(TRAITS[cat.trait])
            if not game.clan.leader.dead:
                ceremony.extend([
                    str(game.clan.leader.name) +
                    " calls the Clan to a meeting, and declares " + str(cat.name.prefix) +
                    "paw to be a warrior. They are now called " +
                    str(cat.name.prefix) + str(cat.name.suffix) +
                    " and are celebrated for their " + str(random_honor) + ".",
                    str(game.clan.leader.name) +
                    " stands above the Clan and proclaims that " + str(cat.name.prefix) +
                    "paw shall now be known as " + str(cat.name.prefix) +
                    str(cat.name.suffix) + ", honoring their " +
                    str(random_honor) + ".",
                    str(game.clan.name) + "Clan welcomes " + str(cat.name.prefix) +
                    str(cat.name.suffix) + " as a new warrior, honoring their " +
                    str(random_honor) + ".",
                    str(game.clan.leader.name) + " rests their muzzle on " +
                    str(cat.name.prefix) + str(cat.name.suffix) +
                    "'s head and declares them to be a full warrior of " +
                    str(game.clan.name) + "Clan, honoring their " +
                    str(random_honor) + "."
                ])
            else:
                ceremony.extend([str(game.clan.name) + "Clan welcomes " + str(cat.name.prefix) +
                                 str(cat.name.suffix) + " as a new warrior, honoring their " +
                                 str(random_honor) + "."])
        elif (promoted_to == 'apprentice') and cat.mentor is not None:
            ceremony.extend([
                str(cat.name) +
                " has reached the age of six moons and has been made an apprentice, with "
                + str(cat.mentor.name) + " as their mentor.",
                "Newly-made apprentice " + str(cat.name) +
                " touched noses with their new mentor, " +
                str(cat.mentor.name) + "."
            ])
            if cat.parent1 is not None and str(
                    cat_class.all_cats[cat.parent1].name) != str(
                        cat.mentor.name) and str(cat_class.all_cats[cat.parent1].name) != "unnamed queen":
                ceremony.extend([
                    str(cat_class.all_cats[cat.parent1].name) +
                    " is watching in pride as " + str(cat.name) +
                    " is named and given to " + str(cat.mentor.name) +
                    " to apprentice under. They know that " +
                    str(cat.mentor.name) + " was a good choice."
                ])

            if cat.is_disabled() and not game.clan.leader.dead:
                ceremony.extend([
                    str(cat.name) + " is confidently telling " +
                    str(game.clan.leader.name) +
                    " that they can do anything any cat can. " +
                    str(game.clan.leader.name) + " assigns " +
                    str(cat.mentor.name) +
                    " as their mentor to make sure that happens."
                ])
        elif (promoted_to == 'apprentice') and cat.mentor is None:
            ceremony.extend(["Newly-made apprentice " + str(cat.name) +
                             " wished they had someone to mentor them."])
        elif (promoted_to == 'medicine cat apprentice') and cat.mentor is not None:
            ceremony.extend([
                str(cat.name) +
                " has decided that hunting and fighting is not the way they can provide for their Clan. Instead, they have decided to serve their Clan by healing and communing with StarClan. "
                + str(cat.mentor.name) + " proudly becomes their mentor."
            ])
        elif (promoted_to == 'medicine cat apprentice') and cat.mentor is None:
            ceremony.extend(["Newly-made medicine cat apprentice " + str(cat.name) +
                             " learns the way of healing through guidance from StarClan."])
        elif (promoted_to == 'medicine cat'):
            ceremony.extend(
                [str(cat.name) + " is taken to speak with StarClan. They are now a full medicine cat of the Clan."])
        elif (promoted_to == 'elder' and not game.clan.leader.dead):
            ceremony.extend([
                str(game.clan.leader.name) +
                " proudly calls a Clan meeting to honor " + str(cat.name) +
                "'s service to the Clan. It is time they retire peacefully to the elder's den.",
                str(cat.name) + " wished to join the elders. The Clan honors them and all the service they have given to them."
            ])
        elif (promoted_to == 'elder' and game.clan.leader.dead):
            ceremony.extend([
                str(cat.name) + " wished to join the elders. The Clan honors them and all the service they have given to them."
            ])
        if (
                promoted_to == 'warrior' or promoted_to == 'apprentice' or promoted_to == 'medicine cat apprentice' or promoted_to == 'medicine cat' or promoted_to == 'elder'):
            ceremony_text = choice(ceremony)
            game.cur_events_list.append(ceremony_text)
            game.ceremony_events_list.append(ceremony_text)
        else:
            game.cur_events_list.append(f'{str(cat.name)}{ceremony_text}')
            game.ceremony_events_list.append(f'{str(cat.name)}{ceremony_text}')
    
    def gain_accessories(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                  accessories                                 #
        # ---------------------------------------------------------------------------- #
        
        if cat.dead:
            return
        
        # check if cat already has acc
        if cat.accessory is not None:
            self.ceremony_accessory = False
            return

        name = str(cat.name)

        # find other_cat
        other_cat = choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return
        other_name = str(other_cat.name)

        acc_text = []

        # chance to gain acc
        chance = randint(0, 50)
        if cat.status in ['medicine cat', 'medicine cat apprentice']:
            chance = randint(0, 30)
        elif cat.age in ['kitten', 'adolescent']:
            chance = randint(0, 80)
        elif cat.age in ['young adult', 'adult', 'senior adult', 'elder']:
            chance = randint(0, 150)
        elif cat.trait in ['childish', 'lonesome', 'loving', 'playful', 'shameless', 'strange', 'troublesome']:
            chance = randint(0, 50)

        give = False

        # increase chance of acc if the cat had a ceremony
        if self.ceremony_accessory is True:
            if chance in [0, 1, 2, 3, 4, 5]:
                give = True
        else:
            if chance == 1:
                give = True

        # give them an acc! \o/
        if give is True:
            if cat.accessory is None:
                cat.accessory = choice([
                    choice(plant_accessories),
                    choice(wild_accessories)
                ])
                # check if the cat is missing a tail before giving feather acc
                if cat.accessory in ['RED FEATHERS', 'BLUE FEATHERS', 'JAY FEATHERS']:
                    if 'NOTAIL' in cat.scars:
                        cat.accessory = choice(plant_accessories)
                    if 'HALFTAIL' in cat.scars:
                        cat.accessory = choice(plant_accessories)
                acc_singular = plural_acc_names(cat.accessory, False, True)
                acc_plural = plural_acc_names(cat.accessory, True, False)
                if self.ceremony_accessory is True:
                    acc_text.extend([f'{other_name} gives {name} something to adorn their pelt as congratulations',
                                     f'{name} decides to pick something to adorn their pelt as celebration'])
                if cat.age != 'kitten':
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        if game.clan.current_season == 'Leaf-bare':
                            acc_text.append(
                                f'{name} found a mysterious {acc_singular} growing in the '
                                f'{choice(["snow", "ice", "frost"])} and decided to wear it.')
                        else:
                            acc_text.extend([
                                f'{name} received a cool {acc_singular} from {other_name} '
                                f'and decided to wear it on their pelt.',
                                f'{name} found a pretty {acc_singular} and decided to wear it on their pelt.',
                                f'A clanmate gave {name} some {acc_plural} and they decided to wear them.'
                            ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS",
                                           "JAY FEATHERS"] and "NOTAIL" in cat.scars:
                        acc_text.append(f'{name} found a bunch of pretty {acc_plural} and decided to wear them.')
                    elif cat.accessory in ["HERBS", "PETALS", "DRY_HERBS"]:
                        acc_text.append(f'{name} always seems to have {acc_plural} stuck in their fur.')
                    elif cat.accessory in plant_accessories and cat.status in ['medicine cat apprentice',
                                                                               'medicine cat']:
                        acc_text.extend([f'{name} has decided to always bring some {acc_plural} with them.',
                                         f'{acc_plural} are so important to {name} that they always carry it around.'.capitalize,
                                         f'{acc_plural} are so vital for {name} that they always have some on them.'.capitalize
                                         ])
                    else:
                        acc_text.extend([f'{name} finds a(n) {acc_singular} and decides to wear it on their pelt.',
                                         f'A clanmate gives {name} a pretty {acc_singular} '
                                         f'and they decide to wear it on their pelt.',
                                         f'{name} finds a(n) {acc_singular} '
                                         f'while out on a walk and decides to wear it on their pelt.',
                                         f'{name} finds {acc_plural} '
                                         f'fascinating and decides to wear some on their pelt.',
                                         f'A clanmate gives {name} a pretty {acc_singular} '
                                         f'to adorn their pelt as a gift.',
                                         f'{other_name} gives {name} a pretty {acc_singular} '
                                         f'and they decide to wear it on their pelt.'
                                         ])
                else:
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        acc_text.extend([
                            f'{name} received a {acc_singular} from {other_name} and decided to wear it on their pelt.',
                            f'{name} found a {acc_singular} and decided to wear it on their pelt.',
                            f'A clanmate gave {name} a {acc_singular} and they decided to wear it.'

                        ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS",
                                           "JAY FEATHERS"] and "NOTAIL" in cat.scars:
                        acc_text.append(
                            f'{name} was playing with {acc_plural} earlier and decided to wear some of them.')
                    elif cat.accessory in ["HERBS", "PETALS", "DRYHERBS"]:
                        acc_text.append(
                            f'{name}\'s parents try their best to groom them, '
                            f'but something is always stuck in their fur.')
                    else:
                        acc_text.extend(
                            [f'{name} seems to have picked up a neat {acc_singular} while playing out in the camp.',
                             f'{name} finds something interesting and decides to wear it on their pelt.',
                             f'A clanmate gives {name} a pretty {acc_singular} '
                             f'and they decide to wear it on their pelt.',
                             f'{other_name} gives {name} a pretty {acc_singular} '
                             f'and they decide to wear it on their pelt.',
                             f'{name} is so cute that they are given {acc_plural} as a gift.',
                             f'{name} starts to wear {acc_plural} on their pelt after their friend gave some to them.',
                             f'{name} was playing with {acc_plural} '
                             f'earlier and has decided to use it to adorn themselves.'
                             ])
        else:
            self.ceremony_accessory = False
        if acc_text:
            text = choice(acc_text)
            game.misc_events_list.append(text)
            game.cur_events_list.append(text)
            if self.ceremony_accessory:
                self.ceremony_accessory = False

    def gain_scars(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                    scars                                     #
        # ---------------------------------------------------------------------------- #
        if len(cat.scars) == 4 or cat.age == 'kitten':
            return

        risky_traits = ["bloodthirsty", "ambitious", "vengeful", "strict", "cold", "fierce"]
        danger = ["a rogue", "a dog", "a fox", "an otter", "a rat", "a hawk", "an enemy warrior", "a badger"]
        tail_danger = ["a rogue", "a dog", "a fox", "an otter", "a rat", "a hawk",
                       "an enemy warrior", "a badger", "a twoleg trap"]

        name = str(cat.name)
        scar_chance = 0.015  # 1.5%
        clancats = self.living_cats
        scar_text = []
        specialty = None  # Scar to be set
        alive_kits = list(filter(lambda kitty: (kitty.age == "kitten"
                                                and not kitty.dead
                                                and not kitty.outside),
                                 Cat.all_cats.values()))
        leader = Cat.all_cats[str(game.clan.leader)]

        if cat.mentor:
            mentor = cat.mentor

        # Older cats are scarred more often
        if cat.age in ["adult", "senior adult"]:
            scar_chance += 0.01  # + 1%

        # Check cat mentor/leader status and traits
        risky_mentor = False
        risky_leader = False
        if cat.mentor:
            if cat.mentor.trait in risky_traits:
                risky_mentor = True
                scar_chance += 0.0125  # + 1.25%
                mentor_name = str(mentor.name)
        if leader:
            if leader.trait in risky_traits:
                risky_leader = True
                leader_name = str(leader.name)
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
            leader_scar_chance = leader_scar_chance * 1.5

        # Set pools and check which scars we can still get
        all_scars = scars1 + scars2 + scars3
        base_scars = scars1 + scars2  # Can be caused by other cats
        for scar_pool in [all_scars, base_scars]:
            for scar in cat.scars:
                if scar:
                    try:
                        if "NOPAW" == scar and 'TOETRAP' in scar_pool:
                            scar_pool.remove('TOETRAP')
                        if "NOTAIL" == scar:
                            for option in ["HALFTAIL", "TAILBASE", "TAILSCAR"]:
                                if option in scar_pool:
                                    scar_pool.remove(option)
                        if scar in scar_pool:
                            scar_pool.remove(scar)  # No doubles
                    except ValueError as e:
                        print(f"Failed to exclude scar from pool: {e}")

        # Always possible scar events
        if scar_chance > random.random():
            specialty = choice(all_scars)
            if specialty in ["NOTAIL", "HALFTAIL"]:
                if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                    cat.accessory = None
                scar_text.append(f"{name} lost their tail to {choice(tail_danger)}.")
                if not random.getrandbits(2):
                    scar_text.append(f"{name} lost their tail to a falling tree.")
            elif specialty == "SNAKE":
                scar_text.append(f"{name} was bit by a snake but miraculously survived.")
            elif specialty == "TOETRAP":
                scar_text.append(
                    f"{name} got their paw stuck in a twoleg trap and earned a scar."
                )
            elif specialty == "NOPAW":
                scar_text.append(f"{name} lost their paw to a twoleg trap.")
            else:
                scar_text.extend(
                    [
                        f"{name} earned a scar fighting {choice(danger)}.",
                        f"{name} earned a scar defending the territory.",
                        f"{name} is injured after falling into a river.",
                        f"{name} is injured by enemy warriors after accidentally wandering over the border.",
                        f"{name} is injured after messing with a twoleg object.",
                    ]
                )
                if alive_kits:
                    scar_text.extend([f"{name} earned a scar protecting the kits."])

        # MENTOR CAUSES INJURY >:O
        elif (scar_chance * 1.5 > random.random()
              and cat.status in ['apprentice', 'medicine cat apprentice']
              and risky_mentor):
            specialty = choice(base_scars)
            scar_text.extend(
                [
                    f"{name} earned a scar recklessly fighting {choice(danger)}, encouraged by their mentor.",
                    f"{name} earned a scar for not defending the territory well enough.",
                    f"{name} is injured after being pushed into a river.",
                    f"{name} is punished by their mentor after accidentally wandering over the border.",
                    f"{name} is injured by their mentor after being caught messing with a twoleg object.",
                    f"{name} is injured by their mentor while practicing with their claws out.",
                    f"{name}'s mentor punished them for disobeying.",
                    f"{name} gained a scar while fighting their mentor.",
                    f"{name} is injured while practicing their battle moves with {mentor_name}.",
                    f"{name} is injured after a fight broke out with {mentor_name}.",
                    f"{name} could not handle their mentor's harsh training and got injured as a result.",
                    f"{name} could not handle their mentor's harsh training and got injured as a result.",
                ]
            )
            if specialty == "NOPAW":
                scar_text.append(
                    f"{name} lost their paw after {mentor_name} decided to use twoleg traps for a training exercice.")
        # leader is sus guys
        elif leader_scar_chance > random.random() and risky_leader and cat.ID != leader.ID:
            specialty = choice(base_scars)
            if specialty in ["NOTAIL", "HALFTAIL"]:
                if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                    cat.accessory = None

                scar_text.extend([
                    f"{name} lost their tail to {choice(tail_danger)} while following {leader_name}'s orders.",
                    f"{name} is ordered to fend off {choice(danger)} by {leader_name}, and loses their tail in the ensuing battle.",
                ]
                )
            else:
                if specialty in ["NOPAW"]:
                    scar_text.extend([f"{name} is maimed by {leader_name} for questioning their leadership.",
                                      f"{name} loses a paw after {leader_name} forces them to fight {choice(danger)} by themselves."])
                else:
                    scar_text.extend(
                        [
                            f"{name} earned a scar fighting {choice(danger)} on {leader_name}'s orders.",
                            f"{name} earned a scar defending the territory from outsiders.",
                            f"{name} earned a scar protecting the leader.",
                            f"{name} is wounded during a harsh training exercise led by {leader_name}.",
                            f"{name} is injured during an unsupervised training exercise.",
                            f"{name} is hurt by enemy warriors after being ordered by {leader_name} to go over the border.",
                            f"{name} is injured after being ordered by {leader_name} to check out a twoleg object.",
                            f"{name} is battered while fighting a clanmate after {leader_name} encouraged a fight.",
                            f"{name} is injured by {leader_name} for disobeying orders.",
                            f"{name} is injured by {leader_name} for speaking out against them.",
                            f"{name} is cruelly injured by {leader_name} to make an example out of them.",
                        ]
                    )
        if scar_text:
            chosen_scar = choice(scar_text)

            game.health_events_list.append(chosen_scar)
            game.cur_events_list.append(chosen_scar)
            cat.scar_event.append(chosen_scar)

        # Apply scar
        if specialty:
            cat.scars.append(specialty)

    def invite_new_cats(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                   new cats                                   #
        # ---------------------------------------------------------------------------- #
        chance = 100
        if self.living_cats < 10:
            chance = 100
        elif self.living_cats > 50:
            chance = 700
        elif self.living_cats > 30:
            chance = 300
        if randint(1, chance) == 1 and cat.age != 'kitten' and cat.age != 'adolescent' and not self.new_cat_invited:
            self.new_cat_invited = True
            name = str(cat.name)
            type_of_new_cat = choice([1, 2, 3, 4, 5, 6, 7])
            if type_of_new_cat == 1:
                backstory_choice = choice(['abandoned2', 'abandoned1'])
                created_cats = self.create_new_cat(
                    loner=False,
                    loner_name=False,
                    kittypet=choice([True, False]),
                    kit=True,
                    backstory=backstory_choice
                )
                kit = created_cats[0]
                kit_text = [
                    f'{name} finds an abandoned kit and names them {kit.name}.',
                    f'A loner brings their kit named {kit.name.prefix} to the clan, stating they no longer can care for them.'
                ]
                text = choice(kit_text)
                game.misc_events_list.append(text)
                game.cur_events_list.append(text)

            elif type_of_new_cat == 2:
                backstory_choice = choice(['loner1', 'loner2', 'kittypet2',
                                           'rogue1', 'rogue2'])
                created_cats = self.create_new_cat(
                    loner=True,
                    loner_name=True,
                    backstory=backstory_choice
                )
                loner_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a loner named {loner_name.prefix} who joins the clan.',
                    f'A loner waits on the border for a patrol, asking to join the clan.'
                ]
                if loner_name.suffix:
                    success_text = [
                        f'The loner decides to take on a slightly more clan-like name, and is now called {loner_name}.'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name.'
                    ]
                loner_text = choice(loner_text)
                success_text = choice(success_text)
                game.misc_events_list.append(loner_text)
                game.misc_events_list.append(success_text)
                game.cur_events_list.append(loner_text)
                game.cur_events_list.append(success_text)

            elif type_of_new_cat == 3:
                backstory_choice = choice(['loner1', 'loner2', 'kittypet2', 'rogue1', 'rogue2'])
                created_cats = self.create_new_cat(
                    loner=True,
                    loner_name=True,
                    backstory=backstory_choice
                )
                loner_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a loner named {loner_name.prefix} who wishes to join the clan.',
                    f'A loner says that they are interested in clan life and joins the clan.'
                ]
                if loner_name.suffix:
                    success_text = [
                        f'The loner decides to take on a slightly more clan-like name, and is now called {loner_name}.'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name.'
                    ]
                loner_text = choice(loner_text)
                success_text = choice(success_text)
                game.misc_events_list.append(loner_text)
                game.misc_events_list.append(success_text)
                game.cur_events_list.append(loner_text)
                game.cur_events_list.append(success_text)

            elif type_of_new_cat == 4:
                otherclan = str(choice(game.clan.all_clans).name)
                backstory_choice = choice(
                    ['otherclan', 'ostracized_warrior', 'disgraced', 'retired_leader', 'refugee', 'tragedy_survivor'])
                created_cats = self.create_new_cat(
                    kit=False,
                    litter=False,
                    loner=True,
                    backstory=backstory_choice,
                    other_clan=otherclan
                )
                warrior_name = created_cats[0].name
                warrior_text = []
                if len(game.clan.all_clans) > 0:
                    warrior_text.extend([
                        f'{name} finds a warrior from {otherclan}Clan named {warrior_name} who asks to join the clan.'
                        # f'An injured warrior from {otherclan}Clan asks to join in exchange for healing.'
                        # commenting out until I can make these new cats come injured
                    ])
                else:
                    warrior_text.extend([
                        f'{name} finds a warrior from a different clan named {warrior_name} who asks to join the clan.'
                    ])
                text = choice(warrior_text)

                game.other_clans_events_list.append(text)
                game.cur_events_list.append(text)

            elif type_of_new_cat == 5:
                created_cats = self.create_new_cat(
                    loner=False,
                    loner_name=True,
                    kittypet=True,
                    kit=False,
                    litter=False,
                    backstory=choice(['kittypet1', 'kittypet2'])
                )
                loner_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a kittypet named {loner_name.prefix} who wants to join the clan.',
                    f'A kittypet called {loner_name.prefix} stops {name} and asks to join the clan.'
                ]
                if loner_name.suffix:
                    success_text = [
                        f'The kittypet decides to take on a slightly more clan-like name, and is now called {loner_name}.'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name.'
                    ]
                game.cur_events_list.append(choice(loner_text))
                game.misc_events_list.append(choice(loner_text))
                game.cur_events_list.append(choice(success_text))
                game.misc_events_list.append(choice(success_text))

            elif type_of_new_cat == 6:
                created_cats = self.create_new_cat(
                    loner=True,
                    backstory=choice(['kittypet1', 'kittypet2'])
                )
                warrior_name = created_cats[0].name
                loner_text = [
                    f'{name} finds a kittypet named {choice(names.loner_names)} who wants to join the clan.'
                ]
                game.cur_events_list.append(choice(loner_text))
                game.misc_events_list.append(choice(loner_text))
                game.cur_events_list.append(
                    f'The kittypet changes their name to {str(warrior_name)}.')
                game.misc_events_list.append(
                    f'The kittypet changes their name to {str(warrior_name)}.')

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
                    a_kit_text = ([
                        f'A {otherclan}Clan queen decides to leave their litter with you. {str(parent1)} takes them as their own.'
                    ])
                    game.other_clans_events_list.append(a_kit_text)
                    game.cur_events_list.append(a_kit_text)
                else:
                    a_kit_text = ([
                        f'{parent1} finds an abandoned litter and decides to adopt them as their own.',
                        f'A loner leaves their litter to the clan. {str(parent1)} decides to adopt them as their own.'
                    ])
                    text = choice(a_kit_text)
                    game.cur_events_list.append(a_kit_text)
                    game.misc_events_list.append(a_kit_text)

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
            if other_clan is not None:
                age = randint(16, 120)
            else:
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
                new_cat = Cat(moons=age, prefix=name, status=status, gender=choice(['female', 'male']),
                              backstory=backstory)
            elif loner_name:
                new_cat = Cat(moons=age, prefix=name, suffix=None, status=status, gender=choice(['female', 'male']),
                              backstory=backstory)
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

            # create and update relationships
            for the_cat in new_cat.all_cats.values():
                if the_cat.dead or the_cat.outside:
                    continue
                the_cat.relationships[new_cat.ID] = Relationship(the_cat, new_cat)
                new_cat.relationships[the_cat.ID] = Relationship(new_cat, the_cat)
            new_cat.thought = 'Is looking around the camp with wonder'

            # chance to give the new cat a permanent condition, higher chance for found kits and litters
            if game.clan.game_mode != 'classic':
                if kit or litter:
                    chance = 10
                else:
                    chance = 200
                if not int(random.random() * chance):
                    possible_conditions = []
                    for condition in PERMANENT:
                        possible_conditions.append(condition)
                    chosen_condition = choice(possible_conditions)
                    born_with = False
                    if PERMANENT[chosen_condition]['congenital'] in ['always', 'sometimes']:
                        born_with = True
                    new_cat.get_permanent_condition(chosen_condition, born_with)

                    # assign scars
                    if chosen_condition in ['lost a leg', 'born without a leg']:
                        new_cat.scars.append('NOPAW')
                    elif chosen_condition in ['lost their tail', 'born without a tail']:
                        new_cat.scars.append("NOTAIL")

            created_cats.append(new_cat)

        for new_cat in created_cats:
            add_siblings_to_cat(new_cat, cat_class)
            add_children_to_cat(new_cat, cat_class)
            game.clan.add_cat(new_cat)

        return created_cats

    def other_interactions(self, cat):
        if randint(1, 100) != 1:
            return
        interactions = []
        other_cat = choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return
        name = str(cat.name)
        other_name = str(other_cat.name)

        if cat.status == 'kitten' and other_cat.status != 'kitten':
            interactions.extend([
                f'{name} is scolded after sneaking out of camp.',
                f'{name} falls into a river but is saved by {other_name}.'
            ])
        elif cat.status in ['apprentice', 'medicine cat apprentice'] and other_cat.status != 'kitten':
            interactions.extend([
                f'{name} is scolded after sneaking out of camp.',
                f'{name} falls into a river but is saved by {other_name}.',
                name +
                " accidentally trespasses onto another clan\'s territory."
            ])
            if other_cat.status == 'apprentice':
                interactions.append(
                    f'{name} sneaks out of camp with {other_name}.')
        elif cat.status == 'warrior':
            interactions.extend([
                name + " is caught outside of the Clan\'s territory.",
                f'{name} is caught breaking the Warrior Code.',
                f'{name} went missing for a few days.',
                f'{name} believes they are a part of the new prophecy.'
            ])
        elif cat.status == 'medicine cat':
            interactions.extend([
                f'{name} learns of a new prophecy.',
                f'{name} is worried about an outbreak of greencough.',
                f'{name} is worried about how low their herb stores has gotten.',
                f'{name} visits the other medicine cats.'
            ])
        elif cat.status == 'deputy':
            interactions.extend([
                f'{name} thinks about retiring.',
                f'{name} travels to the other clans to bring them an important message.'
            ])
        elif cat.status == 'leader':
            if game.clan.leader_lives <= 5:
                interactions.extend([
                    f'{name} thinks about retiring.',
                    name + " confesses they don\'t have many lives left."
                ])
            if other_cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
            ]:
                interactions.append(
                    f'{name} confesses to {other_name} that the responsibility of leadership is crushing them.'
                )
            elif other_cat.status == 'apprentice':
                interactions.append(f'{name} assesses {other_name}' +
                                    "\'s progress.")
            interactions.extend([
                f'{name} calls a clan meeting to give an important announcement.'
            ])
        elif cat.status == 'elder':
            interactions.extend(
                [f'{name} is brought back to camp after wandering off.'])
        if cat.age == other_cat.age:
            interactions.extend([
                f'{name} tries to convince {other_name} to run away together.'
            ])

        if interactions:
            text = choice(interactions)
            game.cur_events_list.append(text)
            game.misc_events_list.append(text)

    def handle_injuries_or_general_death(self, cat):
        # ---------------------------------------------------------------------------- #
        #                           decide if cat dies                                 #
        # ---------------------------------------------------------------------------- #
        # if triggered_death is True then the cat will die
        triggered_death = False
        # choose other cat
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.outside, Cat.all_cats.values()
        ))

        other_cat = choice(possible_other_cats)
        countdown = int(len(Cat.all_cats) / 2)
        while cat == other_cat or other_cat.dead:
            other_cat = choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return

        if cat.status in ["apprentice", "medicine cat apprentice"] and not int(random.random() * 3):
            if cat.mentor is not None:
                other_cat = cat.mentor

        # check if clan has kits, if True then clan has kits
        alive_kits = list(filter(
            lambda kitty: (kitty.age == "kitten"
                           and not kitty.dead
                           and not kitty.outside),
            Cat.all_cats.values()
        ))

        # chance to kill leader
        if not int(
                random.random() * 100) and cat.status == 'leader' and not triggered_death and not cat.not_working():  # 1/80
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        # chance to die of old age
        if cat.moons > int(random.random() * 51) + 150 and not triggered_death:  # cat.moons > 150 <--> 200
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        # extra death chance and injuries in expanded & cruel season
        if game.clan.game_mode in ["expanded", "cruel season"]:
            if not int(random.random() * 500) and not cat.not_working():  # 1/400
                self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
                triggered_death = True
            else:
                triggered_death = self.condition_events.handle_injuries(cat, other_cat, alive_kits, self.at_war,
                                                                        self.enemy_clan, game.clan.current_season)
                return triggered_death

            # disaster death chance
            if game.settings.get('disasters') and not triggered_death:
                if not random.getrandbits(10):  # 1/1024
                    triggered_death = True
                    self.handle_disasters(cat)

        # classic death chance
        elif game.clan.game_mode == "classic" and not int(random.random() * 500):  # 1/500
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        return triggered_death

    def handle_disasters(self, cat):
        """Handles events when the setting of disasters is turned on"""
        alive_cats = list(filter(
            lambda kitty: (kitty.status != "leader"
                           and not kitty.dead
                           and not kitty.outside),
            Cat.all_cats.values()
        )
        )
        alive_count = len(alive_cats)
        if alive_count > 15:
            if game.clan.all_clans:
                other_clan = game.clan.all_clans
            # Do some population/weight scrunkling to get amount of deaths
            max_deaths = int(alive_count / 2)  # 1/2 of alive cats
            weights = []
            population = []
            for n in range(2, max_deaths):
                population.append(n)
                weight = 1 / (0.75 * n)  # Lower chance for more dead cats
                weights.append(weight)
            dead_count = random.choices(population, weights=weights)[0]  # the dieded..

            disaster = []
            dead_names = []
            dead_cats = random.sample(alive_cats, dead_count)
            for cat in dead_cats:
                dead_names.append(cat.name)
            names = f"{dead_names.pop(0)}"  # Get first
            if dead_names:
                last_name = dead_names.pop()  # Get last
                if dead_names:
                    for name in dead_names:  # In-between
                        names += f", {name}"
                    names += f", and {last_name}"
                else:
                    names += f" and {last_name}"
            disaster.extend([
                ' drown after the camp becomes flooded.',
                f' are killed in a battle against {choice(other_clan).name}Clan.',
                ' are killed after a fire rages through the camp.',
                ' are killed in an ambush by a group of rogues.',
                ' go missing in the night.',
                ' are killed after a badger attack.',
                ' die to a greencough outbreak.',
                ' are taken away by twolegs.',
                ' eat tainted freshkill and die.',
            ])
            if game.clan.current_season == 'Leaf-bare':
                disaster.extend([
                    ' die after freezing from a snowstorm.',
                    ' starve to death when no prey is found.'
                ])
            elif game.clan.current_season == 'Greenleaf':
                disaster.extend([
                    ' die after overheating.',
                    ' die after the water dries up from drought.'
                ])
            if dead_count >= 2:
                event_string = f'{names}{choice(disaster)}'
                if event_string == f'{names} are taken away by twolegs.':
                    for cat in dead_cats:
                        self.handle_twoleg_capture(cat)
                    game.cur_events_list.append(event_string)
                    game.birth_death_events_list.append(event_string)
                    if SAVE_DEATH:
                        save_death(cat, event_string)
                    return
                game.cur_events_list.append(event_string)
                game.birth_death_events_list.append(event_string)
                if SAVE_DEATH:
                    save_death(cat, event_string)

            else:
                disaster_str = choice(disaster)
                disaster_str = disaster_str.replace('are', 'is')
                disaster_str = disaster_str.replace('go', 'goes')
                disaster_str = disaster_str.replace('die', 'dies')
                disaster_str = disaster_str.replace('drown', 'drowns')
                disaster_str = disaster_str.replace('eat', 'eats')
                disaster_str = disaster_str.replace('starve', 'starves')
                event_string = f'{names}{disaster_str}'
                game.cur_events_list.append(event_string)
                game.birth_death_events_list.append(event_string)
                if SAVE_DEATH:
                    save_death(cat, event_string)

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
        # ---------------------------------------------------------------------------- #
        #                           decide if cat dies                                 #
        # ---------------------------------------------------------------------------- #
        # if triggered_death is True then the cat will die
        triggered_death = False

        if game.clan.game_mode in ["expanded", "cruel season"]:
            triggered_death = self.condition_events.handle_illnesses(cat, game.clan.current_season)
            return triggered_death

        elif game.clan.game_mode == "classic":
            # choose other cat
            other_cat = choice(list(Cat.all_cats.values()))
            countdown = int(len(Cat.all_cats) / 2)
            while cat == other_cat or other_cat.dead:
                other_cat = choice(list(Cat.all_cats.values()))
                countdown -= 1
                if countdown <= 0:
                    return

            # check if clan has kits, if True then clan has kits
            alive_kits = list(filter(
                lambda kitty: (kitty.age == "kitten"
                               and not kitty.dead
                               and not kitty.outside),
                Cat.all_cats.values()
            ))

            # chance to kill leader
            if not int(random.random() * 100) and cat.status == 'leader' and not triggered_death:  # 1/100
                self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
                triggered_death = True

            # chance to die of old age
            if cat.moons > int(random.random() * 51) + 150 and not triggered_death:  # cat.moons > 150 <--> 200
                self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
                triggered_death = True

            # classic death chance
            if not int(random.random() * 500):  # 1/500
                self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
                triggered_death = True

            return triggered_death

    def handle_twoleg_capture(self, cat):
        cat.outside = True
        if cat.ID in cat_class.all_cats.keys() and cat.outside and cat.ID not in cat_class.other_cats.keys():
            # The outside-value must be set to True before the cat can go to cotc
            cat.thought = "Is terrified as they are trapped in a large silver twoleg den"
            cat_class.other_cats[cat.ID] = cat

    def handle_outbreaks(self, cat):
        """
        try to infect some cats
        """
        # check if the cat is ill, if game mode is classic, or if clan has sufficient med cats in expanded mode
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if not cat.is_ill() or game.clan.game_mode == 'classic' or \
                (medical_cats_condition_fulfilled(Cat.all_cats.values(),
                                                  amount_per_med) and game.clan.game_mode != 'cruel season'):
            return

        # check how many kitties are already ill
        already_sick = list(filter(
            lambda kitty: (not kitty.dead
                           and not kitty.outside
                           and kitty.is_ill()),
            Cat.all_cats.values()
        ))
        already_sick_count = len(already_sick)

        # round up the living kitties
        alive_cats = list(filter(
            lambda kitty: (not kitty.dead
                           and not kitty.outside
                           and not kitty.is_ill()),
            Cat.all_cats.values()
        ))
        alive_count = len(alive_cats)

        # if large amount of the population is already sick, stop spreading
        if already_sick_count >= alive_count * .25:
            # print('CURRENT SICK COUNT TOO HIGH', already_sick_count, alive_count)
            return

        for illness in cat.illnesses:
            # check if illness can infect other cats
            if cat.illnesses[illness]["infectiousness"] == 0:
                continue
            chance = cat.illnesses[illness]["infectiousness"]
            if not int(random.random() * chance):  # 1/chance to infect
                # fleas are the only condition allowed to spread outside of cold seasons
                if game.clan.current_season not in ["Leaf-bare", "Leaf-fall"] and illness != 'fleas':
                    continue
                if illness == 'kittencough':
                    # adjust alive cats list to only include kittens
                    alive_cats = list(filter(
                        lambda kitty: (kitty.status == "kitten"
                                       and not kitty.dead
                                       and not kitty.outside),
                        Cat.all_cats.values()
                    ))
                    alive_count = len(alive_cats)

                max_infected = int(alive_count / 2)  # 1/2 of alive cats
                weights = []
                population = []
                for n in range(2, max_infected):
                    population.append(n)
                    weight = 1 / (0.75 * n)  # Lower chance for more infected cats
                    weights.append(weight)
                infected_count = random.choices(population, weights=weights)[0]  # the infected..

                infected_names = []
                infected_cats = random.sample(alive_cats, infected_count)
                for cat in infected_cats:
                    infected_names.append(str(cat.name))
                    cat.get_ill(illness, event_triggered=True)  # SPREAD THE GERMS >:)

                illness_name = str(illness).capitalize()
                if illness == 'kittencough':
                    event = f'{illness_name} has spread around the nursery. ' \
                            f'{", ".join(infected_names[:-1])}, and {infected_names[-1]} have been infected.'
                elif illness == 'fleas':
                    event = f'Fleas have been hopping from pelt to pelt and now {", ".join(infected_names[:-1])}, and {infected_names[-1]} are all infested.'
                else:
                    event = f'{illness_name} has spread around the camp. ' \
                            f'{", ".join(infected_names[:-1])}, and {infected_names[-1]} have been infected.'

                print('OUTBREAK - PANDEMIC ALERT')
                game.cur_events_list.append(event)
                game.health_events_list.append(event)
                break

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
                # transing_chance != 0, no trans kitties today...    L
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
            text = f"{cat.name} has realized that {gender} doesn't describe how they feel anymore."
            game.cur_events_list.append(text)
            game.misc_events_list.append(text)


events_class = Events()
