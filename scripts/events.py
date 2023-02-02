import random
from random import randrange

from scripts.cat.cats import *
from scripts.clan import HERBS
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.events_module.relation_events import *
from scripts.game_structure.load_cat import *
from scripts.events_module.condition_events import Condition_Events
from scripts.events_module.death_events import Death_Events
from scripts.events_module.freshkill_pile_events import Freshkill_Events
from scripts.event_class import Single_Event


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

    def one_moon(self):
        game.cur_events_list = []
        game.herb_events_list = []
        game.mediated = False
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
            relevant_cats = [cat for cat in Cat.all_cats.copy().values() if cat.is_alive() and not cat.exiled and not cat.outside]
            game.clan.freshkill_pile.time_skip(relevant_cats)
            # handle freshkill pile events, after feeding
            # self.freshkill_events.handle_amount_freshkill_pile(game.clan.freshkill_pile, relevant_cats)
            # if not game.clan.freshkill_pile.clan_has_enough_food():
            #     game.cur_events_list.insert(0, Single_Event(f"{game.clan.name}Clan has not enough food for the next moon!"))    

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
                game.cur_events_list.append(Single_Event(f"{cat.name} had chosen to use their skills and experience to help "
                                                  f"solve the clan's disagreements. A meeting is called, and they "
                                                  f"become the clan's newest mediator. ", "ceremony", cat.ID))
                cat.status_change("mediator")
                game.ranks_changed_timeskip = True


    def herb_gather(self):
        if game.clan.game_mode == 'classic':
            herbs = game.clan.herbs.copy()
            #print(game.clan.herbs)
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
            #print(game.clan.herbs)
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
                    except IndexError: # IndexError was popping up sometimes, couldn't find why so this is my solution
                        event_list.append(f"{med.name} could not find any herbs this moon.")
                        return
            game.herb_events_list.extend(event_list)
            #print(game.clan.herbs)

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
            cat.opacity = int(100 * (1 - (cat.dead_for / age_to_fade) ** 5) + 30)

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

        #Handle Mediator Events
        self.mediator_events(cat)

        # handle nutrition amount (CARE: the cats has to be fed before - should be handled in "one_moon" function)
        #if game.clan.game_mode in ['expanded', 'cruel season'] and game.clan.freshkill_pile:
        #    self.freshkill_events.handle_nutrient(cat, game.clan.freshkill_pile.nutrition_info)
        #    if cat.dead:
        #        return

        # prevent injured or sick cats from unrealistic clan events
        if cat.is_ill() or cat.is_injured():
            if cat.is_disabled():
                self.condition_events.handle_already_disabled(cat)
            self.perform_ceremonies(cat)
            self.coming_out(cat)
            self.relation_events.handle_having_kits(cat, clan=game.clan)
            cat.one_moon()
            return

        # check for death/reveal/risks/retire caused by permanent conditions
        if cat.is_disabled():
            self.condition_events.handle_already_disabled(cat)
        self.perform_ceremonies(cat)  # here is age up included

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
                            f'{game.clan.name}Clan warriors reinforce the camp walls.'
                        ]
                        if game.clan.medicine_cat is not None:
                            possible_text.extend([
                                'The medicine cats worry about having enough herbs to treat their Clan\'s wounds.'
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
                self.ceremony(cat, 'elder', ' has retired to the elder den.')
                # cat.status_change('elder')

            # apprentice a kitten to either med or warrior
            if cat.moons == cat_class.age_moons[cat.age][1]:
                if cat.status == 'kitten':

                    med_cat_list = list(filter(lambda x: x.status in ["medicine cat", "medicine cat apprentice"]
                                               and not x.dead and not x.outside, Cat.all_cats_list))

                    # check if the medicine cat is an elder
                    has_elder_med = any(cat.age == 'elder' and cat.status == "medicine cat" for cat in med_cat_list)

                    very_old_med = any(cat.moons >= 150 and cat.status == "medicine cat" for cat in med_cat_list)

                    # check if the clan has sufficient med cats
                    if game.clan.game_mode != 'classic':
                        has_med = medical_cats_condition_fulfilled(Cat.all_cats.values(),
                                                                   amount_per_med=get_amount_cat_for_one_medic(
                                                                       game.clan))
                    else:
                        has_med = any(str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                                      and not cat.dead and not cat.outside for cat in Cat.all_cats.values())

                    # check if a med cat app already exists
                    has_med_app = any(cat.status == "medicine cat apprentice" for cat in med_cat_list)

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
                        # Chance for mediator apprentice
                        mediator_list = list(filter(lambda x: x.status == "mediator" and not x.dead
                                                    and not x.outside, Cat.all_cats_list))

                        # Only become a mediator if there is already one in the clan.
                        if mediator_list and not int(random.random() * 80):
                            self.ceremony(cat, 'mediator apprentice', ' has chosen to train as a mediator.')
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

                elif cat.status == 'mediator apprentice':
                    self.ceremony(cat, 'mediator', ' has completed their mediator training')
                    self.ceremony_accessory = True
                    self.gain_accessories(cat)

    def ceremony(self, cat, promoted_to, ceremony_text):
        # ---------------------------------------------------------------------------- #
        #                      promote cats and add to event list                      #
        # ---------------------------------------------------------------------------- #
        ceremony = []
        cat.status_change(promoted_to)
        involved_cats = [cat.ID]  # Clearly, the cat the ceremony is about is involved.
        game.ranks_changed_timeskip = True

        if game.clan.leader:
            leader_dead = game.clan.leader.dead
            leader_exiled = game.clan.leader.exiled
        else:
            leader_dead = True
            leader_exiled = False

        if promoted_to == 'warrior':
            resource_directory = "resources/dicts/events/ceremonies/"
            TRAITS = None
            with open(f"{resource_directory}ceremony_traits.json", 'r') as read_file:
                TRAITS = ujson.loads(read_file.read())
            try:
                random_honor = choice(TRAITS[cat.trait])
            except KeyError:
                random_honor = "hard work"
            if not leader_dead and not leader_exiled:
                involved_cats.append(game.clan.leader.ID)
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
                if cat.trait == 'bloodthirsty':
                    ceremony.extend([str(cat.name.prefix) + "paw has worked long and hard to earn their warrior name but " + str(
                                            game.clan.leader.name) + " can't help but to shiver in unease as they name them " + str(
                                            cat.name) + " after their " + str(random_honor) + "."])
            else:
                ceremony.extend([str(game.clan.name) + "Clan welcomes " + str(cat.name.prefix) +
                                 str(cat.name.suffix) + " as a new warrior, honoring their " +
                                 str(random_honor) + "."])

        elif (promoted_to == 'apprentice') and cat.mentor is not None:
            mentor_name = str(Cat.fetch_cat(cat.mentor).name)
            involved_cats.append(cat.mentor)
            ceremony.extend([
                str(cat.name) +
                " has reached the age of six moons and has been made an apprentice, with "
                + mentor_name + " as their mentor.",
                "Newly-made apprentice " + str(cat.name) +
                " touched noses with their new mentor, " +
                mentor_name + ".",
                str(cat.name) + " carefully touches noses with their new mentor, " + mentor_name + ", looking quite intimidated and nervous.",
                str(cat.name) + " excitedly touches noses with their new mentor, " + mentor_name + ", looking quite eager to start training."
            ])
            if cat.parent1 is not None and str(
                    cat_class.all_cats[cat.parent1].name) != str(
                Cat.fetch_cat(cat.mentor).name) and str(cat_class.all_cats[cat.parent1].name) != "unnamed queen":
                if not cat_class.all_cats[cat.parent1].dead:
                    involved_cats.append(cat.parent1)
                    ceremony.extend([
                        str(cat_class.all_cats[cat.parent1].name) +
                        " is watching in pride as " + str(cat.name) +
                        " is named and given to " + mentor_name +
                        " to apprentice under. They know that " +
                        mentor_name + " was a good choice."
                    ])

            if cat.is_disabled() and not leader_dead:
                if str(game.clan.leader.name) != mentor_name:
                    involved_cats.append(game.clan.leader.ID)
                    ceremony.extend([
                        str(cat.name) + " is confidently telling " +
                        str(game.clan.leader.name) +
                        " that they can do anything any cat can. " +
                        str(game.clan.leader.name) + " assigns " +
                        mentor_name +
                        " as their mentor to make sure that happens.",
                        "Standing proud and tall before their new mentor " + str(
                            cat.name) + " promises " + mentor_name + " that together they will prove "
                                                                     "to everyone that they will be the best warrior."
                    ])

        elif (promoted_to == 'apprentice') and cat.mentor is None:
            ceremony.extend(["Newly-made apprentice " + str(cat.name) +
                             " wished they had someone to mentor them."])

        elif (promoted_to == 'medicine cat apprentice') and cat.mentor is not None:
            mentor_name = str(Cat.fetch_cat(cat.mentor).name)
            involved_cats.append(cat.mentor)
            ceremony.extend([
                str(cat.name) +
                " has decided that hunting and fighting is not the way they can provide for their Clan. "
                "Instead, they have decided to serve their Clan by healing and communing with StarClan. "
                + mentor_name + " proudly becomes their mentor.",

                "Interested in herbs even in their kithood, " + str(cat.name) + " is eager to be apprenticed to "
                + mentor_name + ".",
                "Interested in all the myths and stories told by the elders and queens, " +
                str(cat.name) + " decides to become a medicine cat apprentice, hoping to someday speak to "
                                "those gone before. " + mentor_name + " loves their determination and eagerness "
                                "to learn and agrees to take them on as their apprentice.",
                                "The thought alone of fighting and hurting another cat makes " + str(cat.name) +
                                " shiver. They decide to heal instead of fight and " + mentor_name +
                                " takes them under their wing."
            ])
        elif (promoted_to == 'medicine cat apprentice') and cat.mentor is None:
            ceremony.extend(["Newly-made medicine cat apprentice " + str(cat.name) +
                             " learns the way of healing through guidance from StarClan."])
        elif promoted_to == 'mediator apprentice':
            mentor_name = str(Cat.fetch_cat(cat.mentor).name)
            involved_cats.append(cat.mentor)
            ceremony.extend(
                [f"{cat.name} feel sick at the mere thought of fighting. They decide to train as a mediator, and"
                 f" {mentor_name} is named as their mentor. ",
                 f"{cat.name} is fascinated by {mentor_name}'s ability to solve disputes without tooth or claw. They "
                 f" are eager to learn, and {mentor_name} take them under their wing."])
        elif promoted_to == 'medicine cat':
            ceremony.extend(
                [str(cat.name) + " is taken to speak with StarClan. They are now a full medicine cat of the Clan.",
                 "The senior medicine cat has thought long and hard about this and gives " + str(cat.name.prefix) +
                 "paw their full name of " + str(cat.name) + ". StarClan gives their blessing and the stars "
                 "twinkle in celebration.",
                 f"With the stars softly shining and lighting their pelts, the senior medicine cat gives "
                 f"{cat.name.prefix}paw their full name of {cat.name}. They both share the rest of the night "
                 "with StarClan, celebrating their good fortune in having another medicine cat."])
        elif promoted_to == 'mediator':
            ceremony.extend(
                [f"{cat.name.prefix}paw have proven themselves skilled at handling the clan's disputes. "
                 f"They are given the name {cat.name}, and the clan honors their new mediator.",
                 f"{cat.name} is welcomed as fully trained mediator of the Clan"])

        elif promoted_to == 'elder' and not leader_dead:
            involved_cats.append(game.clan.leader.ID)
            ceremony.extend([
                str(game.clan.leader.name) +
                " proudly calls a Clan meeting to honor " + str(cat.name) +
                "'s service to the Clan. It is time they retire peacefully to the elder's den.",
                str(cat.name) + " wished to join the elders. " + str(game.clan.leader.name) +
                " calls a meeting, and the Clan honors and all the service " + str(cat.name) + " have given to them."
            ])
        elif promoted_to == 'elder' and leader_dead:
            ceremony.extend([
                str(cat.name) + " wished to join the elders. "
                "The Clan honors them and all the service they have given to them."
            ])
        if promoted_to in ['warrior', 'apprentice', 'medicine cat apprentice', 'medicine cat', 'elder', 'mediator',
                           "mediator apprentice"]:
            ceremony_text = choice(ceremony)
            game.cur_events_list.append(Single_Event(ceremony_text, "ceremony", involved_cats))
            # game.ceremony_events_list.append(ceremony_text)
        else:
            game.cur_events_list.append(Single_Event(f'{str(cat.name)}{ceremony_text}', "ceremony", involved_cats))
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

    def gain_scars(self, cat):
        # ---------------------------------------------------------------------------- #
        #                                    scars                                     #
        # ---------------------------------------------------------------------------- #
        if len(cat.scars) == 4 or cat.age == 'kitten':
            return

        risky_traits = ["bloodthirsty", "ambitious", "vengeful", "strict", "cold", "fierce"]
        danger = ["a rogue", "a dog", "a fox", "an otter", "a rat", "a hawk", "an enemy warrior", "a badger"]
        tail_danger = ["a rogue", "a dog", "a fox", "an otter", "a rat", "a hawk",
                       "an enemy warrior", "a badger", "a Twoleg trap"]

        name = str(cat.name)
        involved_cats = [cat.ID]
        scar_chance = 0.015  # 1.5%
        scar_text = []
        specialty = None  # Scar to be set
        alive_kits = list(filter(lambda kitty: (kitty.age == "kitten"
                                                and not kitty.dead
                                                and not kitty.outside),
                                 Cat.all_cats.values()))
        leader = game.clan.leader

        # Older cats are scarred more often
        if cat.age in ["adult", "senior adult"]:
            scar_chance += 0.01  # + 1%

        # Check cat mentor/leader status and traits
        risky_mentor = False
        risky_leader = False
        if cat.mentor:
            mentor_ob = Cat.fetch_cat(cat.mentor)
            mentor_name = str(mentor_ob.name)
            if mentor_ob.trait in risky_traits:
                risky_mentor = True
                scar_chance += 0.0125  # + 1.25%
        else:
            mentor_name = "None"

        if leader:
            leader_name = str(leader.name)
            if leader.trait in risky_traits:
                risky_leader = True
                scar_chance += 0.005  # + 0.5%
                if leader.trait in ["bloodthirsty", "vengeful"]:
                    scar_chance += 0.005
        else:
            leader_name = "None"

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
                        print(f"ERROR: Failed to exclude scar from pool: {e}")

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
                    f"{name} got their paw stuck in a Twoleg trap and earned a scar."
                )
            elif specialty == "NOPAW":
                scar_text.append(f"{name} lost their paw to a Twoleg trap.")
            else:
                scar_text.extend(
                    [
                        f"{name} earned a scar fighting {choice(danger)}.",
                        f"{name} earned a scar defending the territory.",
                        f"{name} is injured after falling into a river.",
                        f"{name} is injured by enemy warriors after accidentally wandering over the border.",
                        f"{name} is injured after messing with a Twoleg object.",
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
                    f"{name} is injured by their mentor after being caught messing with a Twoleg object.",
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
                    f"{name} lost their paw after {mentor_name} decided to use Twoleg traps for a training exercice.")
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
                            f"{name} was wounded during a harsh training exercise led by {leader_name}.",
                            f"{name} was injured during an unsupervised training exercise.",
                            f"{name} was hurt by enemy warriors after being ordered by {leader_name} to go over the border.",
                            f"{name} was injured after being ordered by {leader_name} to check out a Twoleg object.",
                            f"{name} was battered while fighting a Clanmate after {leader_name} encouraged a fight.",
                            f"{name} was injured by {leader_name} for disobeying orders.",
                            f"{name} was injured by {leader_name} for speaking out against them.",
                            f"{name} was cruelly injured by {leader_name} to make an example out of them.",
                        ]
                    )
        if scar_text:
            chosen_scar = choice(scar_text)

            # game.health_events_list.append(chosen_scar)
            game.cur_events_list.append(Single_Event(chosen_scar, "health", involved_cats))
            cat.scar_event.append(chosen_scar)

        # Apply scar
        if specialty:
            cat.scars.append(specialty)

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
            base_chance = 100
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

        if not int(random.random() * chance) and cat.age != 'kitten' and cat.age != 'adolescent' and not self.new_cat_invited:
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
                involved_cats = [kit.ID]
                kit_text = [
                    f'{name} finds an abandoned kit and names them {kit.name}.',
                    f'A loner brings their kit named {kit.name.prefix} '
                    f'to the Clan, stating they no longer can care for them.'
                ]
                text = choice(kit_text)
                # If it's the first one, there is also the cat that found them to be added to the involved list
                if text == kit_text[0]:
                    involved_cats.append(cat.ID)
                # game.misc_events_list.append(text)
                game.cur_events_list.append(Single_Event(text, "misc", involved_cats))

            elif type_of_new_cat == 2:
                backstory_choice = choice(['loner1', 'loner2', 'kittypet2',
                                           'rogue1', 'rogue2'])
                created_cats = self.create_new_cat(
                    loner=True,
                    loner_name=True,
                    backstory=backstory_choice
                )
                loner_name = created_cats[0].name
                involved_cats = [created_cats[0].ID]
                loner_text_options = [
                    f'{name} finds a loner named {loner_name.prefix} who joins the Clan. ',
                    f'A loner waits on the border for a patrol, asking to join the Clan. '
                ]
                if loner_name.suffix:
                    success_text = [
                        f'The loner decides to take on a slightly more Clan-like name, and is now called {loner_name}.'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name.'
                    ]
                loner_text = choice(loner_text_options)
                if loner_text == loner_text_options[0]:
                    # If it's the first option, another cat is also involved in the event
                    involved_cats.append(cat.ID)

                success_text = choice(success_text)

                game.cur_events_list.append(Single_Event(loner_text + " " + success_text, "misc", involved_cats))

            elif type_of_new_cat == 3:
                backstory_choice = choice(['loner1', 'loner2', 'kittypet2', 'rogue1', 'rogue2'])
                created_cats = self.create_new_cat(
                    loner=True,
                    loner_name=True,
                    backstory=backstory_choice
                )
                loner_name = created_cats[0].name
                involved_cats = [created_cats[0].ID]
                loner_text_options = [
                    f'{name} finds a loner named {loner_name.prefix} who wishes to join the Clan. ',
                    f'A loner says that they are interested in Clan life and joins the Clan. '
                ]
                if loner_name.suffix:
                    success_text = [
                        f'The loner decides to take on a slightly more Clan-like name, and is now called {loner_name}.'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name.'
                    ]
                loner_text = choice(loner_text_options)
                if loner_text == loner_text_options[0]:
                    involved_cats.append(cat.ID)

                success_text = choice(success_text)

                game.cur_events_list.append(Single_Event(loner_text + " " + success_text, "misc", involved_cats))

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
                involved_cats = [created_cats[0].ID]
                warrior_text = []
                if len(game.clan.all_clans) > 0:
                    warrior_text.extend([
                        f'{name} finds a warrior from {otherclan}Clan named {warrior_name} who asks to join the Clan. '
                        # f'An injured warrior from {otherclan}Clan asks to join in exchange for healing.'
                        # commenting out until I can make these new cats come injured
                    ])
                else:
                    warrior_text.extend([
                        f'{name} finds a warrior from a different Clan named {warrior_name} who asks to join the Clan. '
                    ])
                involved_cats.append(cat.ID)

                text = choice(warrior_text)

                # game.other_clans_events_list.append(text)
                game.cur_events_list.append(Single_Event(text, "other_clans", involved_cats))

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
                involved_cats = [created_cats[0].ID]
                loner_text_options = [
                    f'{name} finds a kittypet named {loner_name.prefix} who wants to join the Clan. ',
                    f'A kittypet called {loner_name.prefix} stops {name} and asks to join the Clan. '
                ]
                if loner_name.suffix:
                    success_text = [
                        f'The kittypet decides to take on a slightly more Clan-like name, and is now called {loner_name}.'
                    ]
                else:
                    success_text = [
                        f'{loner_name} decides to keep their name.'
                    ]
                involved_cats.append(cat.ID)  # All options have another cat involved.
                loner_text = choice(loner_text_options)
                success_text = choice(success_text)

                game.cur_events_list.append(Single_Event(loner_text + " " + success_text, "misc", involved_cats))

            elif type_of_new_cat == 6:
                created_cats = self.create_new_cat(
                    loner=True,
                    backstory=choice(['kittypet1', 'kittypet2'])
                )
                warrior_name = created_cats[0].name
                involved_cats = [created_cats[0].ID]
                loner_text = [
                    f'{name} finds a kittypet named {choice(names.loner_names)} who wants to join the Clan. '
                ]
                involved_cats.append(cat.ID)

                game.cur_events_list.append(Single_Event(choice(loner_text) +
                                                         f'The kittypet changes their name to {str(warrior_name)}.',
                                                         "misc", involved_cats))

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
                involved_cats = [c.ID for c in created_cats] + [cat.ID]
                if backstory == 'abandoned3':
                    a_kit_text = ([
                        f'A {otherclan}Clan queen decides to leave their litter with you. {str(parent1)} '
                        f'takes them as their own.'
                    ])
                    a_kit_text = choice(a_kit_text)
                    # game.other_clans_events_list.append(a_kit_text)
                    game.cur_events_list.append(Single_Event(a_kit_text, "misc", involved_cats))
                else:
                    a_kit_text = ([
                        f'{parent1} finds an abandoned litter and decides to adopt them as their own.',
                        f'A loner leaves their litter to the Clan. {str(parent1)} decides to adopt them as their own.'
                    ])
                    a_kit_text = choice(a_kit_text)
                    game.cur_events_list.append(Single_Event(a_kit_text, "misc", involved_cats))
                    # game.misc_events_list.append(a_kit_text)

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

            # give apprentice aged cat a mentor
            if new_cat.age == 'adolescent':
                new_cat.update_mentor()

            # Remove disabling scars, if they generated. 
            not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 'LEFTBLIND',
                           'BRIGHTHEART', 'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
            for scar in new_cat.scars:
                if scar in not_allowed:
                    new_cat.scars.remove(scar)


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
        involved_cats = [cat.ID]
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
                " accidentally trespasses onto another Clan\'s territory."
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
                f'{name} travels to the other Clans to bring them an important message.'
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
                f'{name} calls a Clan meeting to give an important announcement.'
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
            game.cur_events_list.append(Single_Event(text, "misc", involved_cats))
            # game.misc_events_list.append(text)

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
        alive_kits = list(filter(
            lambda kitty: (kitty.age == "kitten"
                           and not kitty.dead
                           and not kitty.outside),
            Cat.all_cats.values()
        ))

        # chance to kill leader: 1/100
        if not int(
                random.random() * 100) and cat.status == 'leader' and not triggered_death and not cat.not_working():
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

        # classic death chance
        elif game.clan.game_mode == "classic" and not int(random.random() * 500):  # 1/500
            self.death_events.handle_deaths(cat, other_cat, self.at_war, self.enemy_clan, alive_kits)
            triggered_death = True

        # disaster death chance
        if game.settings.get('disasters') and not triggered_death:
            if not random.getrandbits(9):  # 1/512
                triggered_death = True
                self.handle_disasters(cat)

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
            if not int(random.random() * 500):  # 1/500
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

                    if game.clan.deputy and game.clan.leader:
                        if game.clan.deputy.dead and not (game.clan.leader.dead or game.clan.leader.exiled):
                            text = f"{game.clan.leader.name} chooses {Cat.all_cats[random_cat].name} to take over " \
                                   f"as deputy. They know that {game.clan.deputy.name} would approve."
                            involved_cats.extend([game.clan.leader.ID, game.clan.deputy.ID])
                        if not game.clan.deputy.dead and not game.clan.deputy.outside:
                            text = f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. " \
                                   f"The retired deputy nods their approval."
                            # No other cat are involved here.
                        if game.clan.deputy.outside:
                            text = f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. " \
                                   f"The Clan hopes that {game.clan.deputy.name} would approve."
                            involved_cats.append(game.clan.deputy.ID)
                    elif game.clan.leader.dead or game.clan.leader.exiled:
                        if game.clan.leader:
                            text = f"Since losing {game.clan.leader.name} the Clan has been directionless. " \
                                   f"They all turn to {Cat.all_cats[random_cat].name} with hope for the future."
                            involved_cats.append(game.clan.leader.ID)
                        else:
                            text = f"Without a leader, the Clan has been directionless. " \
                                   f"They all turn to {Cat.all_cats[random_cat].name} with hope for the future."
                            # No additional involved cats.
                    else:
                        if Cat.all_cats[random_cat].trait == 'bloodthirsty':
                            text = f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. " \
                                   f"They look at the Clan leader with an odd glint in their eyes."
                            # No additional involved cats

                        else:
                            possible_events = [
                                f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. "
                                f"The Clan yowls their name in approval.",
                                f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. "
                                f"Some of the older Clan members question the wisdom in this choice.",
                                f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. "
                                f"They hold their head up high and promise to do their best for the Clan.",
                                f"{game.clan.leader.name} has been thinking deeply all day who they would "
                                f"respect and trust enough to stand at their side and at sunhigh makes the "
                                f"announcement that {Cat.all_cats[random_cat].name} will be the Clan's new deputy.",
                                f"{Cat.all_cats[random_cat].name} has been chosen as the new deputy. They pray to "
                                f"StarClan that they are the right choice for the Clan.",
                            ]
                            # No additional involved cats
                            text = choice(possible_events)

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
