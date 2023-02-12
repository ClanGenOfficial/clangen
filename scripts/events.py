import random
from random import randrange

from scripts.cat.cats import *
from scripts.clan import HERBS
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.events_module.misc_events import MiscEvents
from scripts.events_module.new_cat_events import NewCatEvents
from scripts.events_module.relation_events import *
from scripts.game_structure.load_cat import *
from scripts.events_module.condition_events import Condition_Events
from scripts.events_module.death_events import Death_Events
from scripts.events_module.freshkill_pile_events import Freshkill_Events
from scripts.event_class import Single_Event
import traceback


class Events():
    all_events = {}
    game.switches['timeskip'] = False

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
        if game.clan.reputation > 100:
            game.clan.reputation = 100

        game.patrolled.clear()

        if any(str(cat.status) in {'leader', 'deputy', 'warrior', 'medicine cat', 'medicine cat apprentice',
                                   'apprentice', 'mediator', 'mediator apprentice'}
               and not cat.dead and not cat.outside for cat in Cat.all_cats.values()):
            game.switches['no_able_left'] = False

        self.relation_events.handle_pregnancy_age(game.clan)

        if game.clan.game_mode in ['expanded', 'cruel season'] and game.clan.freshkill_pile:
            # feed the cats and update the nutrient status
            relevant_cats = [cat for cat in Cat.all_cats.copy().values() if
                             cat.is_alive() and not cat.exiled and not cat.outside]
            game.clan.freshkill_pile.time_skip(relevant_cats)
            # handle freshkill pile events, after feeding
            self.get_moon_freshkill()
            # first 5 moons there will not be any freshkill pile event
            if game.clan.age >= 5:
                self.freshkill_events.handle_amount_freshkill_pile(game.clan.freshkill_pile, relevant_cats)
            if not game.clan.freshkill_pile.clan_has_enough_food():
                game.cur_events_list.insert(0, Single_Event(
                    f"{game.clan.name}Clan doesn't have enough prey for next moon!"))
            needed_amount = game.clan.freshkill_pile.amount_food_needed()
            print(f"current freshkill amount: {game.clan.freshkill_pile.total_amount}, needed {needed_amount}")

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
                if cat.moons == 6:
                    cat.age = 'adolescent'
                elif cat.moons == 12:
                    cat.age = 'adult'
                elif cat.moons == 120:
                    cat.age = 'elder'

                # killing exiled cats
                if cat.moons > randint(100, 200) and (cat.exiled or cat.outside):
                    if choice([1, 2, 3, 4, 5]) == 1 and not cat.dead:
                        cat.dead = True
                        if cat.exiled:
                            text = f'Rumors reach your Clan that the exiled {str(cat.name)} has died recently.'
                        else:
                            text = f'Rumors reach your Clan that {str(cat.name)} has died recently.'
                        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))

                if cat.exiled and cat.status == 'leader' and not cat.dead and randint(
                        1, 10) == 1:
                    game.clan.leader_lives -= 1
                    if game.clan.leader_lives > 0:
                        text = f'Rumors reach your Clan that the exiled {str(cat.name)} lost a life recently.'
                        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))
                    else:
                        text = f'Rumors reach your Clan that the exiled {str(cat.name)} has died recently.'
                        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))
                        cat.dead = True

                elif cat.exiled and cat.status == 'leader' and not cat.dead and randint(
                        1, 45) == 1:
                    game.clan.leader_lives -= 10
                    cat.dead = True
                    text = f'Rumors reach your Clan that the exiled {str(cat.name)} has died recently.'
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

            # Grab all the dead or outside cats, who should not have grief text
            for ID in Cat.grief_strings:
                check_cat = Cat.all_cats.get(ID)
                if check_cat:
                    if check_cat.dead or check_cat.outside:
                        remove_cats.append(check_cat.ID)

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
                increase = randint(-2, 6)
                clan = choice(game.clan.all_clans)
                clan.relations += increase
                dispute_type = choice(["hunting", "border", "personal", "herb-gathering"])
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
            mediator_chance = {
                "warrior": 5000,
                "elder": 400
            }
            if cat.status in mediator_chance and not int(random.random() * mediator_chance[cat.status]):
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
            lower_value = GAME_CONFIG["freshkill"]["auto_warrior_prey"][0]
            upper_value = GAME_CONFIG["freshkill"]["auto_warrior_prey"][1]
            if cat.status == "apprentice":
                lower_value = GAME_CONFIG["freshkill"]["auto_apprentice_prey"][0]
                upper_value = GAME_CONFIG["freshkill"]["auto_apprentice_prey"][1]

            prey_amount += randint(lower_value, upper_value)
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
            print(game.clan.herbs)
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
                        # TODO: need to add bee sting as an injury so that these two herbs are relevant.
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
        herbs = game.clan.herbs

        herbs_lost = []
        for herb in herbs:
            if herbs[herb] > 25:
                herbs.update({herb: 25})
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

        if sum(herbs.values()) >= 50:
            chance = 2
        else:
            chance = 5

        if len(herbs.keys()) >= 10 and not int(random.random() * chance):
            index = randrange(1, int(len(herbs.keys()) / 2))
            count = 0
            bad_herb = None
            for herb in herbs:
                count += 1
                if count == index:
                    bad_herb = herb
                    break
            herb_amount = randrange(1, int(herbs[bad_herb] + 2))
            # deplete the herb
            herbs[bad_herb] -= herb_amount
            insert2 = 'some of'
            if herbs[bad_herb] <= 0:
                herbs.pop(bad_herb)
                insert2 = "all of"

            event = f"As the herb stores are inspected by the {insert}, it's noticed that {insert2} the {str(bad_herb).replace('_', ' ')}" \
                    f" went bad. They'll have to be replaced with new ones. "
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif allies and not int(random.random() * 5):
            chosen_ally = choice(allies)
            if len(herbs.keys()) == 0:
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
                index = randrange(1, int(len(herbs.keys())) + 1)
                count = 0
                herb_given = None
                for herb in herbs:
                    count += 1
                    if count == index:
                        herb_given = herb
                        break
                if herbs[herb_given] > 2:
                    herb_amount = randrange(1, int(herbs[herb_given] - 1))
                    # deplete the herb
                    herbs[herb_given] -= herb_amount

                    possible_events = [
                        f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any {str(herb_given).replace('_', ' ')} to spare. "
                        f"Graciously, your Clan decides to aid their allies and share the herbs.",
                        f"The medicine cat apprentice from {chosen_ally.name}Clan comes asking for {str(herb_given).replace('_', ' ')}. "
                        f"They refuse to say why their Clan needs them but your Clan still provides them with {str(herb_given).replace('_', ' ')}."
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
                        f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any {str(herb_given).replace('_', ' ')} to spare, "
                        f"your Clan only has enough for themselves however and they refuse to share.",
                        f"The medicine cat apprentice from {chosen_ally.name}Clan comes asking for herbs. They refuse to "
                        f"say why their Clan needs them and your Clan decides not to share their precious few {str(herb_given).replace('_', ' ')}."
                    ]
                    if herb_given == 'lungwort':
                        possible_events.extend([
                            f"The {chosen_ally.name}Clan medicine cat apprentice comes to your camp, pleading for help with"
                            f" a yellowcough epidemic. Your Clan can't spare the precious herb however, and turns them away.",
                            f"A medicine cat from {chosen_ally.name}Clan comes to your Clan, asking for lungwort to heal "
                            f"a case of yellowcough. However, your Clan has no extra lungwort to give."
                        ])
                    chosen_ally.relations -= 5
            event = choice(possible_events)
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif not int(random.random() * 10) and 'moss' in herbs:
            herb_amount = randrange(1, herbs['moss'] + 1)
            herbs['moss'] -= herb_amount
            if herbs['moss'] <= 0:
                herbs.pop('moss')
            event = f"The medicine den nests have been refreshed with new moss from the herb stores."
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif not int(random.random() * 80) and sum(game.clan.herbs.values()) > 0 and len(meds) > 0:

            possible_events = []
            if self.at_war is True:
                possible_events.append(f"{self.enemy_clan} breaks into the camp and ravages the herb stores, "
                                       f"taking some for themselves and destroying the rest.")
            possible_events.extend([
                f"Some sort of pest got into the herb stores and completely destroyed them. The {insert} will have to "
                f"clean it out and start over anew.",
                f"Abnormally strong winds blew through the camp last night and scattered the herb store into a "
                f"useless state.",
                f"Some kind of blight has infected the herb stores. The {insert} have no choice but to clear out all "
                f"the old herbs."
            ])
            if game.clan.current_season == 'Leaf-bare':
                possible_events.extend([
                    f"Freezing temperatures have not just affected the cats. It's also frostbitten the stored herbs. "
                    f"They're useless now and will have to be replaced.",
                ])
            elif game.clan.current_season == 'Newleaf':
                possible_events.extend([
                    f"The newleaf rain has left the air humid and the whole camp damp. The herb stores are found to "
                    f"be growing mold and have to be thrown out. "
                ])
            elif game.clan.current_season == 'Greenleaf' and game.clan.biome != 'Mountainous':
                possible_events.extend([
                    f"The persistent, dry heat managed to cause a small fire in the herb stores. While no one was "
                    f"injured, the herbs are little more than ashes now."
                ])
            elif game.clan.biome == 'Beach' and game.clan.current_season in ["Leaf-fall", "Leaf-bare"]:
                possible_events.extend([
                    f"A huge wave crashes into camp, leaving everyone soaked and the herb stores irreparably damaged."
                ])
            game.clan.herbs.clear()
            chosen_event = choice(possible_events)
            game.cur_events_list.append(Single_Event(chosen_event, "health"))
            game.herb_events_list.append(chosen_event)

    def handle_fading(self, cat):
        if game.settings["fading"] and not cat.prevent_fading and cat.ID != game.clan.instructor.ID and \
                not cat.faded:

            age_to_fade = 302
            # Handle opacity
            cat.opacity = int(80 * (1 - (cat.dead_for / age_to_fade) ** 5) + 20)

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
        cat.thoughts()

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
                                f'The medicine cats worry about having enough herbs to treat their Clan\'s wounds.',
                                f'The medicine cats wonder what StarClan thinks of the war.'
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
                if game.clan.deputy.trait == 'bloodthirsty':
                    text = f'{str(game.clan.deputy.name)} has become the new leader. ' \
                           f'They stare down at their Clanmates with unsheathed claws, ' \
                           f'promising a new era for the Clans.'
                else:
                    c = choice([1, 2, 3])
                    if c == 1:
                        text = str(game.clan.deputy.name.prefix) + str(
                            game.clan.deputy.name.suffix) + ' has been promoted to the new leader of the Clan. ' \
                                                            'They travel immediately to the Moonstone to get their ' \
                                                            'nine lives and are hailed by their new name, ' + \
                               str(game.clan.deputy.name) + '.'
                    elif c == 2:
                        text = f'{str(game.clan.deputy.name)} has become the new leader of the Clan. ' \
                               f'They vow that they will protect the Clan, even at the cost of their nine lives.'
                    elif c == 3:
                        text = f'{str(game.clan.deputy.name)} has received their nine lives and became the ' \
                               f'new leader of the Clan. They feel like they are not ready for this new ' \
                               f'responsibility, but will try their best to do what is right for the Clan.'

                # game.ceremony_events_list.append(text)
                text += f"\nVisit {str(game.clan.deputy.name)}'s profile to see their full leader ceremony."

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
                    has_elder_med = any(cat.age == 'elder' and cat.status == "medicine cat" for cat in med_cat_list)

                    very_old_med = any(cat.moons >= 150 and cat.status == "medicine cat" for cat in med_cat_list)

                    # check if the clan has sufficient med cats
                    has_med = medical_cats_condition_fulfilled(Cat.all_cats.values(),
                                                               amount_per_med=get_amount_cat_for_one_medic(
                                                                   game.clan))

                    # check if a med cat app already exists
                    has_med_app = any(cat.status == "medicine cat apprentice" for cat in med_cat_list)

                    # assign chance to become med app depending on current med cat and traits
                    if has_elder_med is True and has_med is False:
                        chance = int(random.random() * 3)  # 3 is not part of the range
                    elif has_med is False:
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
                        self.ceremony(cat, 'medicine cat apprentice')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    else:
                        # Chance for mediator apprentice
                        mediator_list = list(filter(lambda x: x.status == "mediator" and not x.dead
                                                              and not x.outside, Cat.all_cats_list))

                        # Only become a mediator if there is already one in the clan.
                        if mediator_list and not int(random.random() * 80):
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
        with open(f"{resource_dir}ceremony-master.json", 'r') as read_file:
            self.CEREMONY_TXT = ujson.loads(read_file.read())

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
        ceremony = []
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
        try:
            # Get all the ceremonies for the role ----------------------------------------
            possible_ceremonies.update(self.ceremony_id_by_tag[promoted_to])

            # Gather ones for mentor. -----------------------------------------------------
            tags = []

            dead_mentor = None
            if cat.mentor:
                tags.append("yes_mentor")
                mentor = Cat.fetch_cat(cat.mentor)
            else:
                tags.append("no_mentor")

            # Dead mentor
            for c in reversed(cat.former_mentor):
                if Cat.fetch_cat(c) and Cat.fetch_cat(c).dead:
                    tags.append("dead_mentor")
                    dead_mentor = Cat.fetch_cat(c)
                    break

            for c in reversed(cat.former_mentor):
                if Cat.fetch_cat(c) and not Cat.fetch_cat(c).dead and not Cat.fetch_cat(c).outside:
                    tags.append("alive_mentor")
                    previous_alive_mentor = Cat.fetch_cat(c)
                    break

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
                    elif not Cat.fetch_cat(p).dead and not Cat.fetch_cat(p).outside:
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
            with open(f"{resource_dir}ceremony_traits.json", 'r') as read_file:
                TRAITS = ujson.loads(read_file.read())
            try:
                random_honor = choice(TRAITS[cat.trait])
            except KeyError:
                random_honor = "hard work"

        print(possible_ceremonies)
        ceremony_text = self.CEREMONY_TXT[choice(list(possible_ceremonies))][1]

        ceremony_text = ceremony_text_adjust(Cat, ceremony_text, cat, dead_mentor=dead_mentor,
                                             random_honor=random_honor,
                                             mentor=mentor, previous_alive_mentor=previous_alive_mentor,
                                             living_parents=living_parents, dead_parents=dead_parents)
        game.cur_events_list.append(Single_Event(f'{ceremony_text}', "ceremony", involved_cats))
        # game.ceremony_events_list.append(f'{str(cat.name)}{ceremony_text}')
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
                    acc_text.extend([f'{other_name} gives {name} something to adorn their pelt as congratulations.',
                                     f'{name} decides to pick something to adorn their pelt as celebration.'])
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
            text = choice(acc_text)
            # game.misc_events_list.append(text)
            game.cur_events_list.append(Single_Event(text, "misc", involved_cats))
            if self.ceremony_accessory:
                self.ceremony_accessory = False

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

        if chance < 1:
            chance = 1

        # choose other cat
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.exiled and not c.outside and (c.ID != cat.ID), Cat.all_cats.values()
        ))

        # If there are possible other cats...
        if possible_other_cats:
            other_cat = choice(possible_other_cats)

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

        if randint(1, 90) != 1:
            return

        other_cat = choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return

        self.misc_events.handle_misc_events(cat, other_cat, self.at_war, self.enemy_clan, alive_kits=get_alive_kits(Cat))

    def handle_injuries_or_general_death(self, cat):
        # ---------------------------------------------------------------------------- #
        #                           decide if cat dies                                 #
        # ---------------------------------------------------------------------------- #
        # if triggered_death is True then the cat will die
        triggered_death = False
        # choose other cat
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.exiled and not c.outside and (c.ID != cat.ID), Cat.all_cats.values()
        ))

        # If there are possible other cats...
        if possible_other_cats:
            other_cat = choice(possible_other_cats)

            if cat.status in ["apprentice", "medicine cat apprentice"] and not int(random.random() * 3):
                if cat.mentor is not None:
                    other_cat = Cat.fetch_cat(cat.mentor)
        else:
            # Otherwise, other_cat is None
            other_cat = None

        # check if clan has kits, if True then clan has kits
        alive_kits = get_alive_kits(Cat)

        # chance to kill leader: 1/100
        if not int(
                random.random() * 100) and cat.status == 'leader' and not triggered_death and not cat.not_working():
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        # chance to die of old age
        if cat.moons > int(random.random() * 51) + 150 and not triggered_death:  # cat.moons > 150 <--> 200
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        # classic death chance
        if game.clan.game_mode == "classic" and not int(random.random() * 500):  # 1/500
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        # disaster death chance
        if game.settings.get('disasters') and not triggered_death:
            if not random.getrandbits(9):  # 1/512
                triggered_death = True
                self.handle_disasters(cat)

        # extra death chance and injuries in expanded & cruel season
        if game.clan.game_mode != 'classic' and not int(random.random() * 500) and not cat.not_working():  # 1/400
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True
        else:
            triggered_death = self.condition_events.handle_injuries(cat, other_cat, alive_kits, self.at_war,
                                                                    self.enemy_clan, game.clan.current_season)
            return triggered_death

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
            for cat in dead_cats:
                dead_names.append(cat.name)
                involved_cats.append(cat.ID)
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
                ' are taken away by Twolegs.',
                ' eat tainted fresh-kill and die.',
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
                if event_string == f'{names} are taken away by Twolegs.':
                    for cat in dead_cats:
                        self.handle_twoleg_capture(cat)
                    game.cur_events_list.append(Single_Event(event_string, "birth_death", involved_cats))
                    # game.birth_death_events_list.append(event_string)
                    return
                game.cur_events_list.append(Single_Event(event_string, "birth_death", involved_cats))
                # game.birth_death_events_list.append(event_string)

            else:
                disaster_str = choice(disaster)
                disaster_str = disaster_str.replace('are', 'is')
                disaster_str = disaster_str.replace('go', 'goes')
                disaster_str = disaster_str.replace('die', 'dies')
                disaster_str = disaster_str.replace('drown', 'drowns')
                disaster_str = disaster_str.replace('eat', 'eats')
                disaster_str = disaster_str.replace('starve', 'starves')
                event_string = f'{names}{disaster_str}'
                game.cur_events_list.append(Single_Event(event_string, "birth_death", involved_cats))
                # game.birth_death_events_list.append(event_string)

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
            if not int(random.random() * 500) and not triggered_death:  # 1/500
                self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
                triggered_death = True

            return triggered_death

    def handle_twoleg_capture(self, cat):
        cat.outside = True
        cat.gone()
        # The outside-value must be set to True before the cat can go to cotc
        cat.thought = "Is terrified as they are trapped in a large silver Twoleg den"
        # FIXME: Not sure what this is intended to do; 'cat_class' has no 'other_cats' attribute.
        # cat_class.other_cats[cat.ID] = cat

    def handle_outbreaks(self, cat):
        """
        try to infect some cats
        """
        # check if the cat is ill, if game mode is classic, or if clan has sufficient med cats in expanded mode
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
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
                for cat in infected_cats:
                    infected_names.append(str(cat.name))
                    involved_cats.append(cat.ID)
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
        if not game.clan.deputy or \
                game.clan.deputy.dead or \
                game.clan.deputy.outside or \
                game.clan.deputy.retired:
            if game.settings.get('deputy') is True:
                random_count = 0
                while random_count < 30:
                    random_cat = str(random.choice(list(Cat.all_cats.keys())))

                    if Cat.all_cats[random_cat].dead or Cat.all_cats[random_cat].outside:
                        random_count += 1
                        continue
                    elif Cat.all_cats[random_cat].status != 'warrior':
                        random_count += 1
                        continue
                    elif len(Cat.all_cats[random_cat].former_apprentices) == 0 and \
                            len(Cat.all_cats[random_cat].apprentice) == 0:
                        random_count += 1
                        continue

                    Cat.all_cats[random_cat].status_change('deputy')
                    involved_cats = [random_cat]
                    text = ''

                    # Gather deputy and leader status
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

                        if Cat.all_cats[random_cat].trait == 'bloodthirsty':
                            text = f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. " \
                                   f"They look at the Clan leader with an odd glint in their eyes."
                            # No additional involved cats
                        else:
                            if game.clan.deputy:
                                previous_deputy_mention = choice(
                                    [f"They know that {game.clan.deputy.name} would approve.",
                                     f"They hope that {game.clan.deputy.name} would approve.",
                                     f"They don't know if {game.clan.deputy.name} would approve, " \
                                     f"but life must go on. "])
                                involved_cats.append(game.clan.deputy.ID)

                            else:
                                previous_deputy_mention = ""

                            text = f"{game.clan.leader.name} chooses {Cat.all_cats[random_cat].name} to take over " \
                                   f"as deputy. " + previous_deputy_mention

                            involved_cats.append(game.clan.leader.ID)
                    elif leader_status == "not_here" and deputy_status == "here":
                        text = f"The clan is without a leader, but a new deputy must still be named.  " \
                               f"{Cat.all_cats[random_cat].name} is chosen as the new deputy. " \
                               f"The retired deputy nods their approval."
                    elif leader_status == "not_here" and deputy_status == "not_here":
                        text = f"Without a leader or deputy, the Clan has been directionless. " \
                               f"They all turn to {Cat.all_cats[random_cat].name} with hope for the future."
                    elif leader_status == "here" and deputy_status == "here":
                        possible_events = [
                            f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. "
                            f"The Clan yowls their name in approval.",
                            f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. "
                            f"Some of the older Clan members question the wisdom in this choice.",
                            f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. "
                            f"They hold their head up high and promise to do their best for the Clan.",
                            f"{game.clan.leader.name} has been thinking deeply all day who they would "
                            f"respect and trust enough to stand at their side, and at sunhigh makes the "
                            f"announcement that {Cat.all_cats[random_cat].name} will be the Clan's new deputy.",
                            f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. They pray to "
                            f"StarClan that they are the right choice for the Clan.",
                            f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. Although"
                            f"they are nervous, they put on a brave front and look forward to serving"
                            f"the clan.",
                        ]
                        # No additional involved cats
                        text = choice(possible_events)
                    else:
                        # This should never happen. Failsave.
                        text = f"{Cat.all_cats[random_cat].name} becomes deputy. "

                    game.clan.deputy = Cat.all_cats[random_cat]
                    game.ranks_changed_timeskip = True

                    game.cur_events_list.append(Single_Event(text, "ceremony", involved_cats))
                    break

                if random_count >= 30:
                    text = 'The Clan decides that no cat is fit to be deputy.'
                    game.cur_events_list.append(Single_Event(text, "ceremony"))
                    # game.ceremony_events_list.append(text)
            else:
                game.cur_events_list.insert(0, Single_Event(f"{game.clan.name}Clan has no deputy!"))


events_class = Events()

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

GAME_CONFIG = None
with open(f"resources/game_config.json", 'r') as read_file:
    GAME_CONFIG = ujson.loads(read_file.read())
