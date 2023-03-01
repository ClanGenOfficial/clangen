import random
import traceback
try:
    import ujson as json
except ImportError:
    import json

from scripts.cat.appearance_utility import plural_acc_names
from scripts.cat.names import names
from scripts.cat.cats import Cat, cat_class
from scripts.cat.pelts import plant_accessories, wild_accessories, collars
from scripts.clan import HERBS
from scripts.clan_resources.freshkill import FRESHKILL_EVENT_ACTIVE
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.events_module.misc_events import MiscEvents
from scripts.events_module.new_cat_events import NewCatEvents
from scripts.events_module.relation_events import Relation_Events
from scripts.events_module.condition_events import Condition_Events
from scripts.events_module.death_events import Death_Events
from scripts.events_module.freshkill_pile_events import Freshkill_Events
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.utility import get_alive_kits, get_med_cats, ceremony_text_adjust

class Events():
    all_events = {}
    game.switches['timeskip'] = False

    def __init__(self, e_type=None, **cats):
        self.e_type = e_type
        self.ID = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(
            0, 9)) + str(random.randint(0, 9))
        if e_type is not None:
            self.all_events[self.ID] = self
        self.cats = cats
        self.at_war = False
        self.time_at_war = False
        self.enemy_clan = None
        self.new_cat_invited = False
        self.ceremony_accessory = False
        self.relation_events = Relation_Events()
        self.condition_events = Condition_Events()
        self.death_events = Death_Events()
        self.freshkill_events = Freshkill_Events()
        self.new_cat_events = NewCatEvents()
        self.misc_events = MiscEvents()
        self.CEREMONY_TXT = None
        self.load_ceremonies()

    def one_moon(self):
        game.cur_events_list = []
        game.herb_events_list = []
        game.mediated = []
        game.switches['saved_clan'] = False
        self.new_cat_invited = False

        # This is a bandaid solution, and isn't perfect. But this will help reputation from growing without limit.
        game.clan.reputation = min(game.clan.reputation, 100)  # <-- Returns the smallest, so caps at 100.

        game.patrolled.clear()

        if any(str(cat.status) in {'leader', 'deputy', 'warrior', 'medicine cat', 'medicine cat apprentice',
                                   'apprentice', 'mediator', 'mediator apprentice'}
               and not cat.dead and not cat.outside for cat in Cat.all_cats.values()):
            game.switches['no_able_left'] = False

        self.relation_events.handle_pregnancy_age(game.clan)

        if game.clan.game_mode in ['expanded', 'cruel season'] and game.clan.freshkill_pile:
            needed_amount = game.clan.freshkill_pile.amount_food_needed()
            #print(f" -- FRESHKILL: prey amount before feeding {game.clan.freshkill_pile.total_amount}")
            #print(f" -- FRESHKILL: clan needs {needed_amount} prey")
            # feed the cats and update the nutrient status
            relevant_cats = list(
                filter(lambda _cat: _cat.is_alive() and not _cat.exiled and not _cat.outside, Cat.all_cats.values())
            )
            game.clan.freshkill_pile.time_skip(relevant_cats)
            self.get_moon_freshkill()
            # handle freshkill pile events, after feeding
            # first 5 moons there will not be any freshkill pile event
            if game.clan.age >= 5:
                self.freshkill_events.handle_amount_freshkill_pile(game.clan.freshkill_pile, relevant_cats)
            # make a notification if the clan has not enough prey
            if not game.clan.freshkill_pile.clan_has_enough_food() and FRESHKILL_EVENT_ACTIVE:
                game.cur_events_list.insert(0, Single_Event(
                    f"{game.clan.name}Clan doesn't have enough prey for next moon!"))
            #print(f" -- FRESHKILL: prey amount after feeding {game.clan.freshkill_pile.total_amount}")
        
        kittypet_ub = game.config["cotc_generation"]["kittypet_chance"]
        rogue_ub = game.config["cotc_generation"]["rogue_chance"]
        loner_ub = game.config["cotc_generation"]["loner_chance"]
        if random.randint(1,kittypet_ub) == 1:  
            self.create_outside_cat("kittypet")   
        if random.randint(1,rogue_ub) == 1:  
            self.create_outside_cat("rogue")  
        if random.randint(1,loner_ub) == 1:  
            self.create_outside_cat("loner")   
        rejoin_upperbound = game.config["lost_cat"]["rejoin_chance"]
        if random.randint(1,rejoin_upperbound) == 1:  
            self.handle_lost_cats_return()   

        for cat in Cat.all_cats.copy().values():
            if not cat.outside or cat.dead:
                self.one_moon_cat(cat)

            else:
                # ---------------------------------------------------------------------------- #
                #                              exiled cat events                               #
                # ---------------------------------------------------------------------------- #
                # aging the cat
                cat.one_moon()
                cat.moons += 1
                cat.update_traits()
                if cat.moons == 6:
                    cat.age = 'adolescent'
                elif cat.moons == 12:
                    cat.age = 'adult'
                elif cat.moons == 120:
                    cat.age = 'elder'

                # killing exiled cats
                if cat.exiled or cat.outside:
                    if random.getrandbits(6) == 1 and not cat.dead:
                        print("Cat Died: " + str(cat.name))
                        cat.dead = True
                        if cat.exiled:
                            text = f'Rumors reach your Clan that the exiled {cat.name} has died recently.'
                        elif cat.status in ['kittypet', 'loner', 'rogue']:
                            text = f'Rumors reach your Clan that the {cat.status} {cat.name} has died recently.'
                        else:
                            cat.outside = False
                            text = f"Will they reach StarClan, even so far away? {cat.name} isn't sure, " \
                                   f"but as they drift away, they hope to see familiar starry fur on the other side."
                        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))

                if cat.exiled and cat.status == 'leader' and not cat.dead and random.randint(
                        1, 10) == 1:
                    game.clan.leader_lives -= 1
                    if game.clan.leader_lives > 0:
                        text = f'Rumors reach your Clan that the exiled {cat.name} lost a life recently.'
                        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))
                    else:
                        text = f'Rumors reach your Clan that the exiled {cat.name} has died recently.'
                        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))
                        cat.dead = True

                elif cat.exiled and cat.status == 'leader' and not cat.dead and random.randint(
                        1, 45) == 1:
                    game.clan.leader_lives -= 10
                    cat.dead = True
                    text = f'Rumors reach your Clan that the exiled {cat.name} has died recently.'
                    game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))
                    game.clan.leader_lives = 0

        # Handle injuries and relationships.
        for cat in Cat.all_cats.values():
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

            # relationships have to be handled separately, because of the ceremony name change
            if not cat.dead or cat.outside:
                self.relation_events.handle_relationships(cat)

        # Handle grief events.
        if Cat.grief_strings:
            remove_cats = []
            death_report_cats = []

            # Grab all the dead or outside cats, who should not have grief text
            for ID in Cat.grief_strings:
                check_cat = Cat.all_cats.get(ID)
                if check_cat:
                    if check_cat.dead or check_cat.outside:
                        remove_cats.append(check_cat.ID)
                    else:
                        death_report_cats.append(check_cat.ID)

            # Remove the dead or outside cats
            for ID in remove_cats:
                if ID in Cat.grief_strings.keys():
                    Cat.grief_strings.pop(ID)

            # Generate events
            for ID in Cat.grief_strings:
                game.cur_events_list.append(Single_Event(Cat.grief_strings[ID][0], ["birth_death", "relation"],
                                                         Cat.grief_strings[ID][1]))

            Cat.grief_strings.clear()

        self.check_clan_relations()

        # age up the clan
        game.clan.age += 1

        self.herb_destruction()
        self.herb_gather()

        if game.clan.game_mode in ["expanded", "cruel season"]:
            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            med_fullfilled = medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med)
            if not med_fullfilled:
                string = f"{game.clan.name}Clan does not have enough healthy medicine cats! Cats will be sick/hurt " \
                         f"for longer and have a higher chance of dying. "
                game.cur_events_list.insert(0, Single_Event(string, "health"))
        else:
            has_med = any(
                str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                and not cat.dead and not cat.outside
                for cat in Cat.all_cats.values())
            if not has_med:
                string = f"{game.clan.name}Clan has no medicine cat!"
                game.cur_events_list.insert(0, Single_Event(string, "health"))

        # Promote leader and deputy, if needed.
        self.check_and_promote_leader()
        self.check_and_promote_deputy()

        # Resort if needed
        if game.ranks_changed_timeskip and game.sort_type == "rank":
            game.ranks_changed_timeskip = False
            Cat.sort_cats()

        # change season
        game.clan.current_season = game.clan.seasons[game.clan.age % 12]

        # autosave
        if game.settings.get('autosave') is True and game.clan.age % 5 == 0:
            game.save_cats()
            game.clan.save_clan()
            game.clan.save_pregnancy(game.clan)

    def mediator_events(self, cat):
        """ Check for mediator events """
        # If the cat is a mediator, check if they visited other clans
        if cat.status in ["mediator", "mediator apprentice"]:
            # 1 /10 chance
            if not int(random.random() * 10):
                increase = random.randint(-2, 6)
                clan = random.choice(game.clan.all_clans)
                clan.relations += increase
                dispute_type = random.choice(["hunting", "border", "personal", "herb-gathering"])
                text = f"{cat.name} travels to {clan} to resolve some recent {dispute_type} disputes. "
                if increase > 4:
                    text += f"The meeting goes better than expected, and {cat.name} returns with a plan to solve the " \
                            f"issue for good."
                elif increase == 0:
                    text += "However, no progress was made."
                elif increase < 0:
                    text += f"However, it seems {cat.name} only made {clan} more upset."

                game.cur_events_list.append(Single_Event(text, "other_clans", cat.ID))

        if game.settings['become_mediator']:
            # Note: These chances are large since it triggers every moon.
            # Checking every moon has the effect giving older cats more chances to become a mediator

            if cat.status in game.config["roles"]["become_mediator_chances"] and \
                    not int(random.random() * game.config["roles"]["become_mediator_chances"][cat.status]):
                game.cur_events_list.append(
                    Single_Event(f"{cat.name} had chosen to use their skills and experience to help "
                                 f"solve the Clan's disagreements. A meeting is called, and they "
                                 f"become the Clan's newest mediator. ", "ceremony", cat.ID))
                cat.status_change("mediator")
                game.ranks_changed_timeskip = True

    def get_moon_freshkill(self):
        """Adding auto freshkill for the current moon."""
        healthy_hunter = list(filter(
            lambda c: c.status in ['warrior', 'apprentice', 'leader',
                                   'deputy'] and not c.dead and not c.outside and not c.exiled and not c.not_working()
            , Cat.all_cats.values()
        ))

        prey_amount = 0
        for cat in healthy_hunter:
            lower_value = game.config["freshkill"]["auto_warrior_prey"][0]
            upper_value = game.config["freshkill"]["auto_warrior_prey"][1]
            if cat.status == "apprentice":
                lower_value = game.config["freshkill"]["auto_apprentice_prey"][0]
                upper_value = game.config["freshkill"]["auto_apprentice_prey"][1]

            prey_amount += random.randint(lower_value, upper_value)
        game.clan.freshkill_pile.add_freshkill(prey_amount)

    def herb_gather(self):
        if game.clan.game_mode == 'classic':
            herbs = game.clan.herbs.copy()
            # print(game.clan.herbs)
            for herb in herbs:
                adjust_by = random.choices([-2, -1, 0, 1, 2], [1, 2, 3, 2, 1], k=1)
                # print(adjust_by)
                game.clan.herbs[herb] += adjust_by[0]
                if game.clan.herbs[herb] <= 0:
                    game.clan.herbs.pop(herb)
            if not int(random.random() * 5):
                new_herb = random.choice(HERBS)
                game.clan.herbs.update({new_herb: 1})
            # print(game.clan.herbs)
        else:
            event_list = []
            meds_available = get_med_cats(Cat)
            # print(game.clan.herbs)
            for med in meds_available:
                if game.clan.current_season in ['Newleaf', 'Greenleaf']:
                    amount = random.choices([0, 1, 2, 3], [1, 2, 2, 2], k=1)
                elif game.clan.current_season == 'Leaf-fall':
                    amount = random.choices([0, 1, 2], [3, 2, 1], k=1)
                else:
                    amount = random.choices([0, 1], [3, 1], k=1)
                if amount[0] != 0:
                    herbs_found = random.sample(HERBS, k=amount[0])
                    herb_display = []
                    for herb in herbs_found:
                        # TODO: need to add bee sting events so that this herb is relevant.
                        if herb in ['blackberry']:
                            continue
                        if game.clan.current_season in ['Newleaf', 'Greenleaf']:
                            amount = random.choices([1, 2, 3], [3, 3, 1], k=1)
                        else:
                            amount = random.choices([1, 2], [4, 1], k=1)
                        # print(amount)
                        if herb in game.clan.herbs.keys():
                            game.clan.herbs[herb] += amount[0]
                        else:
                            game.clan.herbs.update({herb: amount[0]})
                        herb_display.append(herb.replace("_", " "))
                else:
                    herbs_found = []
                    herb_display = []
                if not herbs_found:
                    event_list.append(f"{med.name} could not find any herbs this moon.")
                else:
                    try:
                        if len(herbs_found) == 1:
                            insert = f"{herb_display[0]}"
                        elif len(herbs_found) == 2:
                            insert = f"{herb_display[0]} and {herb_display[1]}"
                        else:
                            insert = f"{', '.join(herb_display[:-1])}, and {herb_display[-1]}"
                        event_list.append(f"{med.name} gathered {insert} this moon.")
                    except IndexError:  # IndexError was popping up sometimes, couldn't find why so this is my solution
                        event_list.append(f"{med.name} could not find any herbs this moon.")
                        return
            game.herb_events_list.extend(event_list)
            # print(game.clan.herbs)

    def herb_destruction(self):
        allies = []
        for clan in game.clan.all_clans:
            if clan.relations > 17:
                allies.append(clan)

        meds = get_med_cats(Cat, working=False)
        if len(meds) == 1:
            insert = "medicine cat"
        else:
            insert = "medicine cats"
        #herbs = game.clan.herbs

        herbs_lost = []
        for herb in game.clan.herbs:
            if game.clan.herbs[herb] > 25:
                game.clan.herbs[herb] = 25
                herbs_lost.append(herb)

        if herbs_lost:
            if len(herbs_lost) == 1 and herbs_lost[0] != 'cobwebs':
                insert2 = f"much {herbs_lost[0]}"
            elif len(herbs_lost) == 1 and herbs_lost[0] == 'cobwebs':
                insert2 = f"many {herbs_lost[0]}"
            elif len(herbs_lost) == 2:
                insert2 = f"much {herbs_lost[0]} and {herbs_lost[1]}"
            else:
                insert2 = f"much {', '.join(herbs_lost[:-1])}, and {herbs_lost[-1]}"
            text = f"The herb stores have too {insert2}. The excess is given back to the earth."
            game.herb_events_list.append(text)

        if sum(game.clan.herbs.values()) >= 50:
            chance = 2
        else:
            chance = 5

        if len(game.clan.herbs.keys()) >= 10 and not int(random.random() * chance):
            bad_herb = random.choice(list(game.clan.herbs.keys()))

            # Failsafe, since I have no idea why we are getting 0-herb entries.
            while game.clan.herbs[bad_herb] <= 0:
                print(f"Warning: {bad_herb} was chosen to destroy, although you currently have "
                      f"{game.clan.herbs[bad_herb]}. Removing {bad_herb} from herb dict, finding a new herb...")
                game.clan.herbs.pop(bad_herb)
                if game.clan.herbs:
                    bad_herb = random.choice(list(game.clan.herbs.keys()))
                else:
                    print("No herbs to destroy")
                    return
                print(f"New herb found: {bad_herb}")

            herb_amount = random.randrange(1, game.clan.herbs[bad_herb] + 1)
            # deplete the herb
            game.clan.herbs[bad_herb] -= herb_amount
            insert2 = 'some of'
            if game.clan.herbs[bad_herb] <= 0:
                game.clan.herbs.pop(bad_herb)
                insert2 = "all of"

            event = f"As the herb stores are inspected by the {insert}, it's noticed that {insert2} the {bad_herb.replace('_', ' ')}" \
                    f" went bad. They'll have to be replaced with new ones. "
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif allies and not int(random.random() * 5):
            chosen_ally = random.choice(allies)
            if game.clan.herbs == {}:
                # If you have no herbs, you can't give any to a clan. Special events for that.
                possible_events = [
                    f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any herbs to spare. "
                    f"Unfortunately, your stocks are bare, and you are unable to provide any help. ",
                    f"A medicine cat from {chosen_ally.name}Clan comes comes to your Clan, asking for herbs "
                    f"to heal their sick Clanmates. Your Clan quickly shoos them away, not willing to "
                    f"admit that they don't have a single herb in their stores. "
                ]
                chosen_ally.relations -= 2
            else:
                herb_given = random.choice(list(game.clan.herbs.keys()))

                # Failsafe, since I have no idea why we are getting 0-herb entries.
                while game.clan.herbs[herb_given] <= 0:
                    print(f"Warning: {herb_given} was chosen to give to another clan, although you currently have "
                          f"{game.clan.herbs[herb_given]}. Removing {herb_given} from herb dict, finding a new herb...")
                    game.clan.herbs.pop(herb_given)
                    if game.clan.herbs:
                        herb_given = random.choice(list(game.clan.herbs.keys()))
                    else:
                        print("No herbs to destroy")
                        return
                    print(f"New herb found: {herb_given}")

                if game.clan.herbs[herb_given] > 2:
                    herb_amount = random.randrange(1, int(game.clan.herbs[herb_given] - 1))
                    # deplete the herb
                    game.clan.herbs[herb_given] -= herb_amount

                    possible_events = [
                        f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any {herb_given.replace('_', ' ')} to spare. "
                        f"Graciously, your Clan decides to aid their allies and share the herbs.",
                        f"The medicine cat apprentice from {chosen_ally.name}Clan comes asking for {herb_given.replace('_', ' ')}. "
                        f"They refuse to say why their Clan needs them but your Clan still provides them with {herb_given.replace('_', ' ')}."
                    ]
                    if herb_given == 'lungwort':
                        possible_events.extend([
                            f"The {chosen_ally.name}Clan medicine cat apprentice comes to your camp, pleading for help "
                            f"with a yellowcough epidemic. Your Clan provides the cat with some of their extra lungwort.",
                            f"A medicine cat from {chosen_ally.name}Clan comes to your Clan, asking for lungwort to heal a "
                            f"case of yellowcough. Your Clan has some extra, and so decides to share with their allies."
                        ])
                    chosen_ally.relations += 5
                else:
                    possible_events = [
                        f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any {herb_given.replace('_', ' ')} to spare. "
                        f"However, your Clan only has enough for themselves and they refuse to share.",
                        f"The medicine cat apprentice from {chosen_ally.name}Clan comes asking for herbs. They refuse to "
                        f"say why their Clan needs them and your Clan decides not to share their precious few {herb_given.replace('_', ' ')}."
                    ]
                    if herb_given == 'lungwort':
                        possible_events.extend([
                            f"The {chosen_ally.name}Clan medicine cat apprentice comes to your camp, pleading for help with"
                            f" a yellowcough epidemic. Your Clan can't spare the precious herb however, and turns them away.",
                            f"A medicine cat from {chosen_ally.name}Clan comes to your Clan, asking for lungwort to heal "
                            f"a case of yellowcough. However, your Clan has no extra lungwort to give."
                        ])
                    chosen_ally.relations -= 5
            event = random.choice(possible_events)
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif not int(random.random() * 10) and 'moss' in game.clan.herbs:
            herb_amount = random.randrange(1, game.clan.herbs['moss'] + 1)
            game.clan.herbs['moss'] -= herb_amount
            if game.clan.herbs['moss'] <= 0:
                game.clan.herbs.pop('moss')
            event = "The medicine den nests have been refreshed with new moss from the herb stores."
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif not int(random.random() * 80) and sum(game.clan.herbs.values()) > 0 and len(meds) > 0:
            possible_events = []
            if self.at_war and self.enemy_clan:
                possible_events.append(f"{self.enemy_clan} breaks into the camp and ravages the herb stores, "
                                       f"taking some for themselves and destroying the rest.")
            possible_events.extend([
                f"Some sort of pest got into the herb stores and completely destroyed them. The {insert} will have to "
                f"clean it out and start over anew.",
                "Abnormally strong winds blew through the camp last night and scattered the herb store into a "
                "useless state.",
                f"Some kind of blight has infected the herb stores. The {insert} have no choice but to clear out all "
                f"the old herbs."
            ])
            if game.clan.current_season == 'Leaf-bare':
                possible_events.extend([
                    "Freezing temperatures have not just affected the cats. It's also frostbitten the stored herbs. "
                    "They're useless now and will have to be replaced.",
                ])
            elif game.clan.current_season == 'Newleaf':
                possible_events.extend([
                    "The newleaf rain has left the air humid and the whole camp damp. The herb stores are found to "
                    "be growing mold and have to be thrown out. "
                ])
            elif game.clan.current_season == 'Greenleaf' and game.clan.biome != 'Mountainous':
                possible_events.extend([
                    "The persistent, dry heat managed to cause a small fire in the herb stores. While no one was "
                    "injured, the herbs are little more than ashes now."
                ])
            elif game.clan.biome == 'Beach' and game.clan.current_season in ["Leaf-fall", "Leaf-bare"]:
                possible_events.extend([
                    "A huge wave crashes into camp, leaving everyone soaked and the herb stores irreparably damaged."
                ])
            game.clan.herbs.clear()
            chosen_event = random.choice(possible_events)
            game.cur_events_list.append(Single_Event(chosen_event, "health"))
            game.herb_events_list.append(chosen_event)
            
    def handle_lost_cats_return(self):
        for id, cat in Cat.all_cats.items():
            if cat.outside and cat.ID not in Cat.outside_cats.keys():
                # The outside-value must be set to True before the cat can go to cotc
                Cat.outside_cats.update({cat.ID: cat})
                
        lost_cat = None
        for id, cat in Cat.outside_cats.items():
            if cat.outside and cat.status not in ['kittypet', 'loner', 'rogue'] and not cat.exiled and not cat.dead:
                lost_cat = cat
                break
        if lost_cat:
            lost_cat_name = lost_cat.name
            text = [f'After a long journey, {lost_cat_name} has finally returned home to the Clan.']
            lost_cat.outside = False
            game.cur_events_list.append(Single_Event(random.choice(text), "misc", [lost_cat.ID]))
            lost_cat.add_to_clan()
            
    def create_outside_cat(self, status):
        if status == 'kittypet':
            name = random.choice(names.loner_names)
        elif status in ['loner', 'rogue']:
            name = random.choice(names.loner_names + names.normal_prefixes)
        else:
            name = random.choice(names.loner_names)
        new_cat = Cat(prefix=name, suffix=None, status=status, gender=random.choice(['female', 'male']))
        if status == 'kittypet':
            new_cat.accessory = random.choice(collars)
        new_cat.outside = True
        game.clan.add_cat(new_cat)
        game.clan.add_to_outside(new_cat)

    def handle_fading(self, cat):
        if game.settings["fading"] and not cat.prevent_fading and cat.ID != game.clan.instructor.ID and \
                not cat.faded:

            age_to_fade = game.config["fading"]["age_to_fade"]
            opacity_at_fade = game.config["fading"]["opacity_at_fade"]
            fading_speed = game.config["fading"]["visual_fading_speed"]
            # Handle opacity
            cat.opacity = int((100 - opacity_at_fade) * (1 - (cat.dead_for / age_to_fade) ** fading_speed)
                              + opacity_at_fade)

            # Deal with fading the cat if they are old enough.
            if cat.dead_for > age_to_fade:
                # If order not to add a cat to the faded list twice, we can't remove them or add them to
                # faded cat list here. Rather, they are added to a list of cats that will be "faded" at the next save.

                # Remove from med cat list, just in case. This should never be triggered, but I've has an issue or
                # two with this, so here it is.
                if cat.ID in game.clan.med_cat_list:
                    game.clan.med_cat_list.remove(cat.ID)

                # If the cat is the current med, leader, or deputy, remove them
                if game.clan.leader:
                    if game.clan.leader.ID == cat.ID:
                        game.clan.leader = None
                if game.clan.deputy:
                    if game.clan.deputy.ID == cat.ID:
                        game.clan.deputy = None
                if game.clan.medicine_cat:
                    if game.clan.medicine_cat.ID == cat.ID:
                        if game.clan.med_cat_list:  # If there are other med cats
                            game.clan.medicine_cat = Cat.fetch_cat(game.clan.med_cat_list[0])
                        else:
                            game.clan.medicine_cat = None

                game.cat_to_fade.append(cat.ID)
                cat.set_faded()  # This is a flag to ensure they behave like a faded cat in the meantime.

    def one_moon_cat(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                trigger events                                #
        # ---------------------------------------------------------------------------- #

        if cat.dead:
            cat.thoughts()
            cat.dead_for += 1
            self.handle_fading(cat)  # Deal with fading.
            return

        # all actions, which do not trigger an event display and
        # are connected to cats are located in there
        cat.one_moon()

        # Handle Mediator Events
        self.mediator_events(cat)

        # handle nutrition amount (CARE: the cats has to be fed before - should be handled in "one_moon" function)
        if game.clan.game_mode in ['expanded', 'cruel season'] and game.clan.freshkill_pile:
           self.freshkill_events.handle_nutrient(cat, game.clan.freshkill_pile.nutrition_info)
           if cat.dead:
               return

        # prevent injured or sick cats from unrealistic clan events
        if cat.is_ill() or cat.is_injured():
            if cat.is_disabled():
                self.condition_events.handle_already_disabled(cat)
            self.perform_ceremonies(cat)
            self.coming_out(cat)
            self.relation_events.handle_having_kits(cat, clan=game.clan)
            cat.create_interaction()
            # this is the new interaction function, currently not active
            #cat.relationship_interaction()
            cat.thoughts()
            return

        # check for death/reveal/risks/retire caused by permanent conditions
        if cat.is_disabled():
            self.condition_events.handle_already_disabled(cat)
        self.perform_ceremonies(cat)  # here is age up included

        self.invite_new_cats(cat)

        self.other_interactions(cat)
        self.coming_out(cat)
        self.gain_accessories(cat)
        self.relation_events.handle_having_kits(cat, clan=game.clan)

        cat.create_interaction()
        # this is the new interaction function, currently not active
        #cat.relationship_interaction()
        cat.thoughts()

    def check_clan_relations(self):
        # ---------------------------------------------------------------------------- #
        #                      interactions with other clans                           #
        # ---------------------------------------------------------------------------- #

        if len(game.clan.all_clans) > 0 and random.randint(1, 5) == 1:
            war_notice = ''
            for other_clan in game.clan.all_clans:
                if int(other_clan.relations) <= 5:
                    if random.randint(1, 5) == 1 and self.time_at_war > 2:
                        self.at_war = False
                        self.time_at_war = 0
                        other_clan.relations = 10
                        text = 'The war against ' + str(other_clan.name) + 'Clan has ended.'
                        game.cur_events_list.append(Single_Event(text, "other_clans"))
                    elif self.time_at_war == 0:
                        text = 'The war against ' + str(other_clan.name) + 'Clan has begun.'
                        # game.other_clans_events_list.append(text)
                        game.cur_events_list.append(Single_Event(text, "other_clans"))
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
                            f'{game.clan.name}Clan warriors reinforce the camp walls.',
                            f'{game.clan.name}Clan warriors evaluate their battle strategies against {other_clan.name}Clan.'
                        ]
                        if game.clan.medicine_cat is not None:
                            possible_text.extend([
                                'The medicine cats worry about having enough herbs to treat their Clan\'s wounds.',
                                'The medicine cats wonder what StarClan thinks of the war.'
                            ])
                        war_notice = random.choice(possible_text)
                        self.time_at_war += 1
                        self.at_war = True
                    break
                if int(other_clan.relations) > 30:
                    other_clan.relations = 10
                else:
                    self.at_war = False
            if war_notice:
                # game.other_clans_events_list.append(war_notice)
                game.cur_events_list.append(Single_Event(war_notice, "other_clans"))

    def perform_ceremonies(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                  ceremonies                                  #
        # ---------------------------------------------------------------------------- #

        # PROMOTE DEPUTY TO LEADER, IF NEEDED -----------------------
        if game.clan.leader:
            leader_dead = game.clan.leader.dead
            leader_outside = game.clan.leader.outside
        else:
            leader_dead = True  # If leader is None, treat them as dead (since they are dead - and faded away.)
            leader_outside = True

        # If a clan deputy exists, and the leader is dead, outside, or doesn't exist, make the deputy leader.
        if game.clan.deputy:
            if game.clan.deputy is not None and \
                    not game.clan.deputy.dead and \
                    not game.clan.deputy.outside and \
                    (leader_dead or leader_outside):
                game.clan.new_leader(game.clan.deputy)
                game.ranks_changed_timeskip = True
                game.clan.leader_lives = 9
                text = ''
                self.handle_leadership_ceremony(game.clan.deputy)
                if game.clan.deputy.trait == 'bloodthirsty':
                    text = f'{game.clan.deputy.name} has become the new leader. ' \
                           f'They stare down at their Clanmates with unsheathed claws, ' \
                           f'promising a new era for the Clans.'
                else:
                    c = random.choice([1, 2, 3])
                    if c == 1:
                        text = str(game.clan.deputy.name.prefix) + str(
                            game.clan.deputy.name.suffix) + ' has been promoted to the new leader of the Clan. ' \
                                                            'They travel immediately to the Moonstone to get their ' \
                                                            'nine lives and are hailed by their new name, ' + \
                               str(game.clan.deputy.name) + '.'
                    elif c == 2:
                        text = f'{game.clan.deputy.name} has become the new leader of the Clan. ' \
                               f'They vow that they will protect the Clan, even at the cost of their nine lives.'
                    elif c == 3:
                        text = f'{game.clan.deputy.name} has received their nine lives and became the ' \
                               f'new leader of the Clan. They feel like they are not ready for this new ' \
                               f'responsibility, but will try their best to do what is right for the Clan.'

                # game.ceremony_events_list.append(text)
                text += f"\nVisit {game.clan.deputy.name}'s profile to see their full leader ceremony."

                game.cur_events_list.append(Single_Event(text, "ceremony", game.clan.deputy.ID))
                self.ceremony_accessory = True
                self.gain_accessories(cat)
                game.clan.deputy = None

        # OTHER CEREMONIES ---------------------------------------

        # Protection check, to ensure "None" cats won't cause a crash.
        if cat:
            cat_dead = cat.dead
        else:
            cat_dead = True

        if not cat_dead:
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.status == 'medicine cat' and game.clan.medicine_cat is None:
                game.clan.medicine_cat = cat

            # retiring to elder den
            if cat.status in ['warrior', 'deputy'] and cat.age == 'elder' and len(cat.apprentice) < 1:
                if cat.status == 'deputy':
                    game.clan.deputy = None
                self.ceremony(cat, 'elder')
                # cat.status_change('elder')

            # apprentice a kitten to either med or warrior
            if cat.moons == cat_class.age_moons[cat.age][0]:
                if cat.status == 'kitten':

                    med_cat_list = list(filter(lambda x: x.status in ["medicine cat", "medicine cat apprentice"]
                                                         and not x.dead and not x.outside, Cat.all_cats_list))

                    # check if the medicine cat is an elder
                    has_elder_med = [c for c in med_cat_list if c.age == 'elder' and c.status == "medicine cat"]

                    very_old_med = [c for c in med_cat_list if c.moons >= 150 and c.status == "medicine cat"]

                    # check if the clan has sufficient med cats
                    has_med = medical_cats_condition_fulfilled(Cat.all_cats.values(),
                                                               amount_per_med=get_amount_cat_for_one_medic(
                                                                   game.clan))

                    # check if a med cat app already exists
                    has_med_app = any(cat.status == "medicine cat apprentice" for cat in med_cat_list)

                    # assign chance to become med app depending on current med cat and traits
                    chance = game.config["roles"]["base_medicine_app_chance"]
                    if has_elder_med == med_cat_list:
                        # These chances apply if all the current medicine cats are elders.
                        if has_med:
                            chance = int(chance / 2.22)
                        else:
                            chance = int(chance / 13.67)
                    elif very_old_med == med_cat_list:
                        # These chances apply is all the current medicine cats are very old.
                        if has_med:
                            chance = int(chance / 3)
                        else:
                            chance = int(chance / 14)
                    # These chances will only be reached if the clan has at least one non-elder medicine cat.
                    elif not has_med:
                        chance = int(chance / 7.125)
                    elif has_med:
                        chance = int(chance * 2.22)

                    if cat.trait in ['altruistic', 'compassionate', 'empathetic', 'wise', 'faithful']:
                        chance = int(chance/1.3)

                    if not has_med_app and not int(random.random() * chance):
                        self.ceremony(cat, 'medicine cat apprentice')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    else:
                        # Chance for mediator apprentice
                        mediator_list = list(filter(lambda x: x.status == "mediator" and not x.dead
                                                              and not x.outside, Cat.all_cats_list))

                        # This checks if at least one mediator already has an apprentice.
                        has_mediator_apprentice = False
                        for c in mediator_list:
                            if c.apprentice:
                                has_mediator_apprentice = True
                                break

                        chance = game.config["roles"]["mediator_app_chance"]
                        if cat.trait in ['charismatic', 'empathetic', 'responsible', 'wise', 'thoughtful']:
                            chance = int(chance / 1.5)

                        # Only become a mediator if there is already one in the clan.
                        if mediator_list and not has_mediator_apprentice and \
                                not int(random.random() * chance):
                            self.ceremony(cat, 'mediator apprentice')
                            self.ceremony_accessory = True
                            self.gain_accessories(cat)
                        else:
                            self.ceremony(cat, 'apprentice')
                            self.ceremony_accessory = True
                            self.gain_accessories(cat)

                # promote to warrior
                elif cat.status == 'apprentice':
                    self.ceremony(cat, 'warrior')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

                # promote to med cat
                elif cat.status == 'medicine cat apprentice':
                    self.ceremony(cat, 'medicine cat')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

                elif cat.status == 'mediator apprentice':
                    self.ceremony(cat, 'mediator')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

    def load_ceremonies(self):
        if self.CEREMONY_TXT:
            return

        resource_dir = "resources/dicts/events/ceremonies/"
        with open(f"{resource_dir}ceremony-master.json", encoding="ascii") as read_file:
            self.CEREMONY_TXT = json.loads(read_file.read())

        self.ceremony_id_by_tag = {}
        # Sorting.
        for ID in self.CEREMONY_TXT:
            for tag in self.CEREMONY_TXT[ID][0]:
                if tag in self.ceremony_id_by_tag:
                    self.ceremony_id_by_tag[tag].add(ID)
                else:
                    self.ceremony_id_by_tag[tag] = {ID}

    def ceremony(self, cat, promoted_to):
        # ---------------------------------------------------------------------------- #
        #                      promote cats and add to event list                      #
        # ---------------------------------------------------------------------------- #
        #ceremony = []
        cat.status_change(promoted_to)
        involved_cats = [cat.ID]  # Clearly, the cat the ceremony is about is involved.
        game.ranks_changed_timeskip = True

        # Time to gather ceremonies. First, lets gather all the ceremony ID's.
        possible_ceremonies = set()
        dead_mentor = None
        mentor = None
        previous_alive_mentor = None
        dead_parents = []
        living_parents = []
        mentor_type = {
            "medicine cat": ["medicine cat"],
            "warrior": ["warrior", "deputy", "leader", "elder"],
            "mediator": ["mediator"]
        }

        try:
            # Get all the ceremonies for the role ----------------------------------------
            possible_ceremonies.update(self.ceremony_id_by_tag[promoted_to])

            # Gather ones for mentor. -----------------------------------------------------
            tags = []

            # CURRENT MENTOR TAG CHECK
            if cat.mentor:
                if Cat.fetch_cat(cat.mentor).status == "leader":
                    tags.append("yes_leader_mentor")
                else:
                    tags.append("yes_mentor")
                mentor = Cat.fetch_cat(cat.mentor)
            else:
                tags.append("no_mentor")

            for c in reversed(cat.former_mentor):
                if Cat.fetch_cat(c) and Cat.fetch_cat(c).dead:
                    tags.append("dead_mentor")
                    dead_mentor = Cat.fetch_cat(c)
                    break

            # Unlike dead mentors, living mentors must be VALID - they must have the correct status for the role the cat
            # is being promoted too.
            valid_living_former_mentors = []
            for c in cat.former_mentor:
                if not(Cat.fetch_cat(c).dead or Cat.fetch_cat(c).outside):
                    if promoted_to in mentor_type:
                        if Cat.fetch_cat(c).status in mentor_type[promoted_to]:
                            valid_living_former_mentors.append(c)
                    else:
                        valid_living_former_mentors.append(c)

            # ALL FORMER MENTOR TAG CHECKS
            if valid_living_former_mentors:
                #  Living Former mentors. Grab the latest living valid mentor.
                previous_alive_mentor = Cat.fetch_cat(valid_living_former_mentors[-1])
                if previous_alive_mentor.status == "leader":
                    tags.append("alive_leader_mentor")
                else:
                    tags.append("alive_mentor")
            else:
                # This tag means the cat has no living, valid mentors.
                tags.append("no_valid_previous_mentor")

            # Now we add the mentor stuff:
            temp = possible_ceremonies.intersection(self.ceremony_id_by_tag["general_mentor"])

            for t in tags:
                temp.update(possible_ceremonies.intersection(self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp

            # Gather for parents ---------------------------------------------------------
            for p in [cat.parent1, cat.parent2]:
                if Cat.fetch_cat(p):
                    if Cat.fetch_cat(p).dead:
                        dead_parents.append(Cat.fetch_cat(p))
                    # For the purposes of ceremonies, living parents who are also the leader are not counted.
                    elif not Cat.fetch_cat(p).dead and not Cat.fetch_cat(p).outside and \
                            Cat.fetch_cat(p).status != "leader":
                        living_parents.append(Cat.fetch_cat(p))

            tags = []
            if len(dead_parents) >= 1:
                tags.append("dead1_parents")
            if len(dead_parents) >= 2:
                tags.append("dead1_parents")
                tags.append("dead2_parents")

            if len(living_parents) >= 1:
                tags.append("alive1_parents")
            if len(living_parents) >= 2:
                tags.append("alive2_parents")

            temp = possible_ceremonies.intersection(self.ceremony_id_by_tag["general_parents"])

            for t in tags:
                temp.update(possible_ceremonies.intersection(self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp

            # Gather for leader ---------------------------------------------------------

            tags = []
            if game.clan.leader and not game.clan.leader.dead and not game.clan.leader.outside:
                tags.append("yes_leader")
            else:
                tags.append("no_leader")

            temp = possible_ceremonies.intersection(self.ceremony_id_by_tag["general_leader"])

            for t in tags:
                temp.update(possible_ceremonies.intersection(self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp

            # Gather for backstories ----------------------------------------------------
            tags = []
            if cat.backstory == ['abandoned1', 'abandoned2', 'abandoned3']:
                tags.append("abandoned")
            elif cat.backstory == "clanborn":
                tags.append("clanborn")

            temp = possible_ceremonies.intersection(self.ceremony_id_by_tag["general_backstory"])

            for t in tags:
                temp.update(possible_ceremonies.intersection(self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp
            # Gather for traits --------------------------------------------------------------

            temp = possible_ceremonies.intersection(self.ceremony_id_by_tag["all_traits"])

            temp.update(possible_ceremonies.intersection(self.ceremony_id_by_tag[cat.trait]))

            possible_ceremonies = temp
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            print("Issue gathering ceremony text.", str(cat.name), promoted_to)

        # getting the random honor if it's needed
        random_honor = None
        if promoted_to == 'warrior':
            resource_dir = "resources/dicts/events/ceremonies/"
            with open(f"{resource_dir}ceremony_traits.json", encoding="ascii") as read_file:
                TRAITS = json.loads(read_file.read())
            try:
                random_honor = random.choice(TRAITS[cat.trait])
            except KeyError:
                random_honor = "hard work"

        # print(possible_ceremonies)
        ceremony_tags, ceremony_text = self.CEREMONY_TXT[random.choice(list(possible_ceremonies))]

        # This is a bit strange, but it works. If there is only one parent involved, but more than one living
        # or dead parent, the adjust text function will pick a random parent. However, we need to know the
        # parent to include in the involved cats. Therefore, text adjust also returns the random parents it picked,
        # which will be added to the involved cats if needed.
        ceremony_text, involved_living_parent, involved_dead_parent = \
            ceremony_text_adjust(Cat, ceremony_text, cat, dead_mentor=dead_mentor,
                                 random_honor=random_honor,
                                 mentor=mentor, previous_alive_mentor=previous_alive_mentor,
                                 living_parents=living_parents, dead_parents=dead_parents)

        # Gather additional involved cats
        for tag in ceremony_tags:
            if tag == "yes_leader":
                involved_cats.append(game.clan.leader.ID)
            elif tag in ["yes_mentor", "yes_leader_mentor"]:
                involved_cats.append(cat.mentor)
            elif tag == "dead_mentor":
                involved_cats.append(dead_mentor.ID)
            elif tag in ["alive_mentor", "alive_leader_mentor"]:
                involved_cats.append(previous_alive_mentor.ID)
            elif tag == "alive2_parents" and len(living_parents) >= 2:
                for c in living_parents[:2]:
                    involved_cats.append(c.ID)
            elif tag == "alive1_parents" and involved_living_parent:
                involved_cats.append(involved_living_parent.ID)
            elif tag == "dead2_parents" and len(dead_parents) >= 2:
                for c in dead_parents[:2]:
                    involved_cats.append(c.ID)
            elif tag == "dead1_parent" and involved_dead_parent:
                involved_cats.append(involved_dead_parent.ID)

        # remove duplicates
        involved_cats = list(set(involved_cats))

        game.cur_events_list.append(Single_Event(f'{ceremony_text}', "ceremony", involved_cats))
        # game.ceremony_events_list.append(f'{cat.name}{ceremony_text}')
    def gain_accessories(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                  accessories                                 #
        # ---------------------------------------------------------------------------- #

        if not cat:
            return

        if cat.dead:
            return

        # check if cat already has acc
        if cat.accessory is not None:
            self.ceremony_accessory = False
            return

        name = str(cat.name)
        involved_cats = [cat.ID]

        # find other_cat
        other_cat = random.choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = random.choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return
        other_name = str(other_cat.name)

        acc_text = []

        # chance to gain acc
        chance = random.randint(0, 50)
        if cat.status in ['medicine cat', 'medicine cat apprentice']:
            chance = random.randint(0, 30)
        elif cat.age in ['kitten', 'adolescent']:
            chance = random.randint(0, 80)
        elif cat.age in ['young adult', 'adult', 'senior adult', 'elder']:
            chance = random.randint(0, 150)
        elif cat.trait in ['childish', 'lonesome', 'loving', 'playful', 'shameless', 'strange', 'troublesome']:
            chance = random.randint(0, 50)

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
                cat.accessory = random.choice([
                    random.choice(plant_accessories),
                    random.choice(wild_accessories)
                ])
                # check if the cat is missing a tail before giving feather acc
                if cat.accessory in ['RED FEATHERS', 'BLUE FEATHERS', 'JAY FEATHERS']:
                    if 'NOTAIL' in cat.scars:
                        cat.accessory = random.choice(plant_accessories)
                    if 'HALFTAIL' in cat.scars:
                        cat.accessory = random.choice(plant_accessories)
                acc_singular = plural_acc_names(cat.accessory, False, True)
                acc_plural = plural_acc_names(cat.accessory, True, False)
                if self.ceremony_accessory is True:
                    acc_text.extend([f'{other_name} gives {name} something to adorn their pelt as congratulations.',
                                     f'{name} decides to pick something to adorn their pelt as celebration.'])
                if cat.age != 'kitten':
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        if game.clan.current_season == 'Leaf-bare':
                            acc_text.append(
                                f'{name} found a mysterious {acc_singular} growing in the '
                                f'{random.choice(["snow", "ice", "frost"])} and decided to wear it.')
                        else:
                            acc_text.extend([
                                f'{name} received a cool {acc_singular} from {other_name} '
                                f'and decided to wear it on their pelt.',
                                f'{name} found a pretty {acc_singular} and decided to wear it on their pelt.',
                                f'A Clanmate gave {name} some {acc_plural} and they decided to wear them.'
                            ])
                    elif cat.accessory in ["RED FEATHERS", "BLUE FEATHERS",
                                           "JAY FEATHERS"] and "NOTAIL" in cat.scars:
                        acc_text.append(f'{name} found a bunch of pretty {acc_plural} and decided to wear them.')
                    elif cat.accessory in ["HERBS", "PETALS", "DRY_HERBS"]:
                        acc_text.append(f'{name} always seems to have {acc_plural} stuck in their fur.')
                    elif cat.accessory in plant_accessories and cat.status in ['medicine cat apprentice',
                                                                               'medicine cat']:
                        acc_text.extend([f'{name} has decided to always bring some {acc_plural} with them.',
                                         f'{acc_plural}'.capitalize() + f' are so important to {name} '
                                                                        f'that they always carry it around.',
                                         f'{acc_plural}'.capitalize() + f' are so vital for {name} that they '
                                                                        f'always have some on them.'
                                         ])
                    else:
                        acc_text.extend([f'{name} finds a(n) {acc_singular} and decides to wear it on their pelt.',
                                         f'A Clanmate gives {name} a pretty {acc_singular} '
                                         f'and they decide to wear it on their pelt.',
                                         f'{name} finds a(n) {acc_singular} '
                                         f'while out on a walk and decides to wear it on their pelt.',
                                         f'{name} finds {acc_plural} '
                                         f'fascinating and decides to wear some on their pelt.',
                                         f'A Clanmate gives {name} a pretty {acc_singular} '
                                         f'to adorn their pelt as a gift.',
                                         f'{other_name} gives {name} a pretty {acc_singular} '
                                         f'and they decide to wear it on their pelt.'
                                         ])
                else:
                    if cat.accessory in ["FORGET ME NOTS", "BLUEBELLS", "POPPY"]:
                        acc_text.extend([
                            f'{name} received a {acc_singular} from {other_name} and decided to wear it on their pelt.',
                            f'{name} found a {acc_singular} and decided to wear it on their pelt.',
                            f'A Clanmate gave {name} a {acc_singular} and they decided to wear it.'

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
                             f'A Clanmate gives {name} a pretty {acc_singular} '
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
            text = random.choice(acc_text)
            # game.misc_events_list.append(text)
            game.cur_events_list.append(Single_Event(text, "misc", involved_cats))
            if self.ceremony_accessory:
                self.ceremony_accessory = False
    
    def handle_leadership_ceremony(self, cat):
        queen = ""
        warrior = ""
        kit = ""
        warrior2 = ""
        app = ""
        elder = ""
        warrior3 = ""
        med_cat = ""
        prev_lead = ""
        known = None
        virtues = None
        if len(cat.life_givers) == 0:
            queen_virtues = ["affection", "compassion", "empathy", "duty", "protection", "pride"]
            warrior_virtues = ["acceptance", "bravery", "certainty", "clear judgement", "confidence"]
            kit_virtues = ["adventure", "curiosity", "forgiveness", "hope", "perspective", "protection"]
            warrior2_virtues = ["courage", "determination", "endurance", "sympathy"]
            app_virtues = ["happiness", "honesty", "humor", "justice", "mentoring", "trust"]
            elder_virtues = ["empathy", "grace", "humility", "integrity", "persistence", "resilience"]
            warrior3_virtues = ["farsightedness", "friendship", "instincts", "mercy", "strength", "unity"]
            med_cat_virtues = ["clear sight", "devotion", "faith", "healing", "patience", "selflessness", "wisdom"]
            prev_lead_virtues = ["endurance in the face of hardship", "knowing when to fight and when to choose peace",
                                 "leadership through the darkest times", "loyalty to their Clan",
                                 "the strength to overcome their fears", "tireless energy"]
            virtues = [random.choice(queen_virtues), random.choice(warrior_virtues), random.choice(kit_virtues), random.choice(warrior2_virtues),
                       random.choice(app_virtues), random.choice(elder_virtues), random.choice(warrior3_virtues), random.choice(med_cat_virtues),
                       random.choice(prev_lead_virtues)]
            known = [False, False, False, False, False, False, False, False, False]

            for i in reversed(game.clan.starclan_cats):
                c = Cat.all_cats[i]
                if c.dead and not c.outside and not c.df:
                    if not queen and c.status == 'queen':
                        queen = str(c.name)
                        known[0] = True
                        continue
                    elif not kit and c.status == 'kitten':
                        kit = str(c.name)
                        known[2] = True
                        continue
                    elif not app and c.status == 'apprentice':
                        app = str(c.name)
                        known[4] = True
                        continue
                    elif not prev_lead and c.status == 'leader':
                        prev_lead = str(c.name)
                        known[8] = True
                        continue
                    elif not elder and c.status == 'elder':
                        elder = str(c.name)
                        known[5] = True
                        continue
                    elif not warrior and c.status == 'warrior':
                        warrior = str(c.name)
                        known[1] = True
                        continue
                    elif not warrior2 and c.status == 'warrior':
                        warrior2 = str(c.name)
                        known[3] = True
                        continue
                    elif not warrior3 and c.status == 'warrior':
                        warrior3 = str(c.name)
                        known[6] = True
                        continue
                    elif not med_cat and (c.status == 'medicine cat' or c.status == 'medicine cat apprentice'):
                        med_cat = str(c.name)
                        known[7] = True
                        continue
                    if queen and warrior and kit and warrior2 and app and elder and warrior3 and med_cat and prev_lead:
                        break
            if not queen:
                queen = str(random.choice(names.normal_prefixes)) + str(random.choice(names.normal_suffixes))
            if not warrior:
                warrior = str(random.choice(names.normal_prefixes)) + str(random.choice(names.normal_suffixes))
            if not kit:
                kit = str(random.choice(names.normal_prefixes)) + "kit"
            if not warrior2:
                warrior2 = str(random.choice(names.normal_prefixes)) + str(random.choice(names.normal_suffixes))
            if not app:
                app = str(random.choice(names.normal_prefixes)) + "paw"
            if not elder:
                elder = str(random.choice(names.normal_prefixes)) + str(random.choice(names.normal_suffixes))
            if not warrior3:
                warrior3 = str(random.choice(names.normal_prefixes)) + str(random.choice(names.normal_suffixes))
            if not med_cat:
                med_cat = str(random.choice(names.normal_prefixes)) + str(random.choice(names.normal_suffixes))
            if not prev_lead:
                prev_lead = str(random.choice(names.normal_prefixes)) + "star"
            cat.life_givers.extend([queen, warrior, kit, warrior2, app, elder, warrior3, med_cat, prev_lead])
            cat.known_life_givers.extend(known)
            cat.virtues.extend(virtues)
        else:
            queen, warrior, kit, warrior2, app, elder, warrior3, med_cat, prev_lead = cat.life_givers[0], \
                                                                                      cat.life_givers[1], \
                                                                                      cat.life_givers[2], \
                                                                                      cat.life_givers[3], \
                                                                                      cat.life_givers[4], \
                                                                                      cat.life_givers[5], \
                                                                                      cat.life_givers[6], \
                                                                                      cat.life_givers[7], \
                                                                                      cat.life_givers[8]

    def invite_new_cats(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                   new cats                                   #
        # ---------------------------------------------------------------------------- #
        chance = 200

        alive_cats = list(filter(
            lambda kitty: (kitty.status != "leader"
                           and not kitty.dead
                           and not kitty.outside),
            Cat.all_cats.values()
        ))

        clan_size = len(alive_cats)

        base_chance = 200
        if clan_size < 10:
            base_chance = 200
        elif clan_size > 50:
            base_chance = 700
        elif clan_size > 30:
            base_chance = 300

        reputation = game.clan.reputation
        # hostile
        if 1 <= reputation <= 30:
            if clan_size < 10:
                chance = base_chance
            else:
                rep_adjust = int(reputation / 2)
                chance = base_chance + int(300 / rep_adjust)
        # neutral
        elif 31 <= reputation <= 70:
            if clan_size < 10:
                chance = base_chance - reputation
            else:
                chance = base_chance
        # welcoming
        elif 71 <= reputation <= 100:
            chance = base_chance - reputation

        chance = max(chance, 1)

        # choose other cat
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.exiled and not c.outside and (c.ID != cat.ID), Cat.all_cats.values()
        ))

        # If there are possible other cats...
        if possible_other_cats:
            other_cat = random.choice(possible_other_cats)

            if cat.status in ["apprentice", "medicine cat apprentice"] and not int(random.random() * 3):
                if cat.mentor is not None:
                    other_cat = Cat.fetch_cat(cat.mentor)
        else:
            # Otherwise, other_cat is None
            other_cat = None

        if not int(
                random.random() * chance) and cat.age != 'kitten' and cat.age != 'adolescent' and not self.new_cat_invited:
            self.new_cat_invited = True

            self.new_cat_events.handle_new_cats(cat=cat, other_cat=other_cat, war=self.at_war,
                                                enemy_clan=self.enemy_clan, alive_kits=get_alive_kits(Cat))

    def other_interactions(self, cat):

        if random.randint(1, 90) != 1:
            return

        other_cat = random.choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = random.choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return

        self.misc_events.handle_misc_events(cat, other_cat, self.at_war, self.enemy_clan, alive_kits=get_alive_kits(Cat))

    def handle_injuries_or_general_death(self, cat):
        # ---------------------------------------------------------------------------- #
        #                           decide if cat dies                                 #
        # ---------------------------------------------------------------------------- #
        # choose other cat
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.exiled and not c.outside and (c.ID != cat.ID), Cat.all_cats.values()
        ))

        # If there are possible other cats...
        if possible_other_cats:
            other_cat = random.choice(possible_other_cats)

            if cat.status in ["apprentice", "medicine cat apprentice"] and not int(random.random() * 3):
                if cat.mentor is not None:
                    other_cat = Cat.fetch_cat(cat.mentor)
        else:
            # Otherwise, other_cat is None
            other_cat = None

        # check if clan has kits, if True then clan has kits
        alive_kits = get_alive_kits(Cat)

        # chance to kill leader: 1/100
        # chance to kill leader: 1/100
        if not int(
                random.random() * 100) and cat.status == 'leader' and not cat.not_working():
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            return True

        # chance to die of old age
        if cat.moons > int(random.random() * 51) + 150:  # cat.moons > 150 <--> 200
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            return True

        # classic death chance
        if game.clan.game_mode == "classic" and not int(random.random() * 500):  # 1/500
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            return True

        # disaster death chance
        if game.settings.get('disasters'):
            if not random.getrandbits(9):  # 1/512
                self.handle_disasters()
                return True

        # extra death chance and injuries in expanded & cruel season
        if game.clan.game_mode != 'classic' and not int(random.random() * 500) and not cat.not_working():  # 1/400
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            return True
        else:
            triggered_death = self.condition_events.handle_injuries(cat, other_cat, alive_kits, self.at_war,
                                                                    self.enemy_clan, game.clan.current_season)
            return triggered_death


    def handle_disasters(self):
        """Handles events when the setting of disasters is turned on.

        Affects random cats in the clan, no cat needs to be passed to this function."""
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
            else:
                other_clan = [""]

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
            involved_cats = []
            dead_cats = random.sample(alive_cats, dead_count)
            for kitty in dead_cats:  # use "kitty" to not redefine "cat"
                dead_names.append(kitty.name)
                involved_cats.append(kitty.ID)
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
                f' are killed in a battle against {random.choice(other_clan).name}Clan.',
                ' are killed after a fire rages through the camp.',
                ' are killed in an ambush by a group of rogues.',
                ' go missing in the night.',
                ' are killed after a badger attack.',
                ' die to a greencough outbreak.',
                ' are taken away by Twolegs.',
                ' eat tainted fresh-kill and die.',
            ])
            if game.clan.current_season == 'Leaf-bare':
                disaster.extend([
                    ' die after freezing from a snowstorm.'
                ])
                if game.clan.game_mode == "classic":
                    disaster.extend([
                    	' starve to death when no prey is found.'
                	])
            elif game.clan.current_season == 'Greenleaf':
                disaster.extend([
                    ' die after overheating.',
                    ' die after the water dries up from drought.'
                ])
            if dead_count >= 2:
                event_string = f'{names}{random.choice(disaster)}'
                if event_string == f'{names} are taken away by Twolegs.':
                    for kitty in dead_cats:
                        self.handle_twoleg_capture(kitty)
                    game.cur_events_list.append(Single_Event(event_string, "birth_death", involved_cats))
                    # game.birth_death_events_list.append(event_string)
                    return
                game.cur_events_list.append(Single_Event(event_string, "birth_death", involved_cats))
                # game.birth_death_events_list.append(event_string)

            else:
                disaster_str = random.choice(disaster)
                disaster_str = disaster_str.replace('are', 'is')
                disaster_str = disaster_str.replace('go', 'goes')
                disaster_str = disaster_str.replace('die', 'dies')
                disaster_str = disaster_str.replace('drown', 'drowns')
                disaster_str = disaster_str.replace('eat', 'eats')
                disaster_str = disaster_str.replace('starve', 'starves')
                event_string = f'{names}{disaster_str}'
                game.cur_events_list.append(Single_Event(event_string, "birth_death", involved_cats))
                # game.birth_death_events_list.append(event_string)

            for poor_little_meowmeow in dead_cats:
                poor_little_meowmeow.die()

    def handle_illnesses_or_illness_deaths(self, cat):
        """ 
        This function will handle:
            - expanded mode: getting a new illness (extra function in own class)
            - classic mode illness related deaths is already handled in the general death function
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

    def handle_twoleg_capture(self, cat):
        cat.outside = True
        cat.gone()
        # The outside-value must be set to True before the cat can go to cotc
        cat.thought = "Is terrified as they are trapped in a large silver Twoleg den"
        # FIXME: Not sure what this is intended to do; 'cat_class' has no 'other_cats' attribute.
        # cat_class.other_cats[cat.ID] = cat

    def handle_outbreaks(self, cat):
        """Try to infect some cats."""
        # check if the cat is ill, if game mode is classic, or if clan has sufficient med cats in expanded mode
        #amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if not cat.is_ill() or game.clan.game_mode == 'classic':
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
            return

        meds = get_med_cats(Cat)

        for illness in cat.illnesses:
            # check if illness can infect other cats
            if cat.illnesses[illness]["infectiousness"] == 0:
                continue
            chance = cat.illnesses[illness]["infectiousness"]
            chance += len(meds) * 10
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
                # If there are less than two cat to infect, you are allowed to infect all the cats
                if max_infected < 2:
                    max_infected = alive_count
                # If, event with all the cats, there is less than two cats to infect, cancel outbreak. 
                if max_infected < 2:
                    return

                weights = []
                population = []
                for n in range(2, max_infected + 1):
                    population.append(n)
                    weight = 1 / (0.75 * n)  # Lower chance for more infected cats
                    weights.append(weight)
                infected_count = random.choices(population, weights=weights)[0]  # the infected..

                infected_names = []
                involved_cats = []
                infected_cats = random.sample(alive_cats, infected_count)
                for sick_meowmeow in infected_cats:
                    infected_names.append(str(sick_meowmeow.name))
                    involved_cats.append(sick_meowmeow.ID)
                    sick_meowmeow.get_ill(illness, event_triggered=True)  # SPREAD THE GERMS >:)

                illness_name = str(illness).capitalize()
                if illness == 'kittencough':
                    event = f'{illness_name} has spread around the nursery. ' \
                            f'{", ".join(infected_names[:-1])}, and {infected_names[-1]} have been infected.'
                elif illness == 'fleas':
                    event = f'Fleas have been hopping from pelt to pelt and now {", ".join(infected_names[:-1])}, and {infected_names[-1]} are all infested.'
                else:
                    event = f'{illness_name} has spread around the camp. ' \
                            f'{", ".join(infected_names[:-1])}, and {infected_names[-1]} have been infected.'

                game.cur_events_list.append(Single_Event(event, "health", involved_cats))
                # game.health_events_list.append(event)
                break

    def coming_out(self, cat):
        """turnin' the kitties trans..."""
        if cat.genderalign == cat.gender:
            if cat.moons < 6:
                return

            involved_cats = [cat.ID]
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
            game.cur_events_list.append(Single_Event(text, "misc", involved_cats))
            # game.misc_events_list.append(text)

    def check_and_promote_leader(self):
        """ Checks if a new leader need to be promoted, and promotes them, if needed.  """
        # check for leader
        if game.clan.leader:
            leader_invalid = game.clan.leader.dead or game.clan.leader.outside
        else:
            leader_invalid = True

        if leader_invalid:
            self.perform_ceremonies(game.clan.leader)  # This is where the deputy will be make leader

            if game.clan.leader:
                leader_dead = game.clan.leader.dead
                leader_outside = game.clan.leader.outside
            else:
                leader_dead = True
                leader_outside = True

            if leader_dead or leader_outside:
                game.cur_events_list.insert(0, Single_Event(f"{game.clan.name}Clan has no leader!"))

    def check_and_promote_deputy(self):
        """Checks if a new deputy needs to be appointed, and appointed them if needed. """
        if (not game.clan.deputy
                or game.clan.deputy.dead
                or game.clan.deputy.outside
                or game.clan.deputy.retired):
            if game.settings.get('deputy'):

                # This determines all the cats who are eligible to be deputy.
                possible_deputies = list(filter(lambda x: not x.dead and not x.outside and x.status == "warrior" and
                                                          (x.apprentice or x.former_apprentices), Cat.all_cats_list))

                # If there are possible deputies, choose from that list.
                if possible_deputies:
                    random_cat = random.choice(possible_deputies)
                    involved_cats = [random_cat.ID]

                    # Gather deputy and leader status, for determination of the text.
                    if game.clan.leader:
                        if game.clan.leader.dead or game.clan.leader.outside:
                            leader_status = "not_here"
                        else:
                            leader_status = "here"
                    else:
                        leader_status = "not_here"

                    if game.clan.deputy:
                        if game.clan.deputy.dead or game.clan.deputy.outside:
                            deputy_status = "not_here"
                        else:
                            deputy_status = "here"
                    else:
                        deputy_status = "not_here"

                    if leader_status == "here" and deputy_status == "not_here":

                        if random_cat.trait == 'bloodthirsty':
                            text = f"{random_cat.name} has been chosen as the new deputy. " \
                                   f"They look at the Clan leader with an odd glint in their eyes."
                            # No additional involved cats
                        else:
                            if game.clan.deputy:
                                previous_deputy_mention = random.choice(
                                    [f"They know that {game.clan.deputy.name} would approve.",
                                     f"They hope that {game.clan.deputy.name} would approve.",
                                     f"They don't know if {game.clan.deputy.name} would approve, "
                                     f"but life must go on. "])
                                involved_cats.append(game.clan.deputy.ID)

                            else:
                                previous_deputy_mention = ""

                            text = f"{game.clan.leader.name} chooses {random_cat.name} to take over " \
                                   f"as deputy. " + previous_deputy_mention

                            involved_cats.append(game.clan.leader.ID)
                    elif leader_status == "not_here" and deputy_status == "here":
                        text = f"The clan is without a leader, but a new deputy must still be named.  " \
                               f"{random_cat.name} is chosen as the new deputy. " \
                               f"The retired deputy nods their approval."
                    elif leader_status == "not_here" and deputy_status == "not_here":
                        text = f"Without a leader or deputy, the Clan has been directionless. " \
                               f"They all turn to {random_cat.name} with hope for the future."
                    elif leader_status == "here" and deputy_status == "here":
                        possible_events = [
                            f"{random_cat.name} has been chosen as the new deputy. "
                            f"The Clan yowls their name in approval.",
                            f"{random_cat.name} has been chosen as the new deputy. "
                            f"Some of the older Clan members question the wisdom in this choice.",
                            f"{random_cat.name} has been chosen as the new deputy. "
                            f"They hold their head up high and promise to do their best for the Clan.",
                            f"{game.clan.leader.name} has been thinking deeply all day who they would "
                            f"respect and trust enough to stand at their side, and at sunhigh makes the "
                            f"announcement that {random_cat.name} will be the Clan's new deputy.",
                            f"{random_cat.name} has been chosen as the new deputy. They pray to "
                            f"StarClan that they are the right choice for the Clan.",
                            f"{random_cat.name} has been chosen as the new deputy. Although"
                            f"they are nervous, they put on a brave front and look forward to serving"
                            f"the clan.",
                        ]
                        # No additional involved cats
                        text = random.choice(possible_events)
                    else:
                        # This should never happen. Failsafe.
                        text = f"{random_cat.name} becomes deputy. "
                else:
                    # If there are no possible deputies, choose someone else, with special text.
                    all_warriors = list(filter(lambda x: not x.dead and not x.outside and x.status == "warrior",
                                               Cat.all_cats_list))
                    if all_warriors:
                        random_cat = random.choice(all_warriors)
                        involved_cats = [random_cat.ID]
                        text = f"No cat in is truly fit to be deputy, but the position can't remain vacant. " \
                               f"{random_cat.name} is appointed as the new deputy. "

                    else:
                        # Is there are no warriors at all, no one is named deputy.
                        game.cur_events_list.append(Single_Event("There are no cats fit to become deputy. ",
                                                                 "ceremony"))
                        return

                random_cat.status_change("deputy")
                game.clan.deputy = random_cat
                game.ranks_changed_timeskip = True

                game.cur_events_list.append(Single_Event(text, "ceremony", involved_cats))

            else:
                game.cur_events_list.insert(0, Single_Event(f"{game.clan.name}Clan has no deputy!"))


events_class = Events()
