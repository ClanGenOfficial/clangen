import random
from typing import List

from scripts.cat.cats import Cat, INJURIES
from scripts.cat.history import History
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan import HERBS
from scripts.clan_resources.freshkill import Freshkill_Pile
from scripts.events_module.condition_events import INJURY_GROUPS
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values, get_alive_kits, \
    history_text_adjust, get_warring_clan, unpack_rel_block, change_clan_reputation, create_new_cat_block, \
    get_living_clan_cat_count
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event


# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class HandleShortEvents():
    """Handles generating and executing ShortEvents"""

    def __init__(self):
        self.involved_cats = []
        self.types = []

        self.main_cat = None
        self.random_cat = None
        self.new_cats: List[List[Cat]] = []
        self.victim_cat = None
        self.other_clan = None
        self.other_clan_name = None

        self.chosen_event = None
        self.additional_event_text = ""

    def handle_event(self, event_type: str, main_cat: Cat, random_cat: Cat, murder: bool = False):
        """ 
        This function handles the generation and execution of the event
        """
        # gather main and random cats
        self.main_cat = main_cat
        self.random_cat = random_cat

        # random cat gets added to involved later on, only if the event chosen requires a random cat
        self.involved_cats = [self.main_cat.ID]

        # check for war and assign self.other_clan accordingly
        if game.clan.war.get("at_war", False):
            enemy_clan = get_warring_clan()  # TODO: if we can just find enemy clan here, take these checks out of event.py
            self.other_clan = enemy_clan
            self.other_clan_name = None
            war = True
        else:
            self.other_clan = random.choice(game.clan.all_clans if game.clan.all_clans else None)
            self.other_clan_name = f'{self.other_clan.name}Clan'
            war = False

        # checking if a murder reveal should happen
        reveal = False
        if event_type == "misc":
            self.victim_cat = None
            cat_history = History.get_murders(self.main_cat)
            if cat_history:
                if "is_murderer" in cat_history:
                    murder_history = cat_history["is_murderer"]
                    for murder in murder_history:
                        murder_index = murder_history.index(murder)
                        if murder_history[murder_index]["revealed"] is True:
                            continue
                        self.victim_cat = murder_history[murder_index]["victim"]
                        reveal = True
                        break

        # NOW find the possible events and filter
        possible_short_events = GenerateEvents.possible_short_events("death")

        final_events = GenerateEvents.filter_possible_short_events(possible_short_events,
                                                                   self.main_cat,
                                                                   self.random_cat,
                                                                   war,
                                                                   self.other_clan,
                                                                   murder=murder,
                                                                   murder_reveal=reveal)

        # ---------------------------------------------------------------------------- #
        #                                  kill cats                                   #
        # ---------------------------------------------------------------------------- #
        try:
            self.chosen_event = (random.choice(final_events))
        except IndexError:
            print('WARNING: no death events found for', main_cat.name)
            return

        self.additional_event_text = ""

        # check if another cat is present
        if self.chosen_event.r_c:
            self.involved_cats.append(self.random_cat.ID)

        # create new cats (must happen here so that new cats can be included in further changes)
        self.handle_new_cats()

        # change relationships before killing anyone
        unpack_rel_block(Cat, self.chosen_event.relationships, self)

        # used in some murder events, this kinda sucks tho it would be nice to change how this sort of thing is handled
        if "kit_manipulated" in self.chosen_event.tags:
            kit = Cat.fetch_cat(random.choice(get_alive_kits(Cat)))
            self.involved_cats.append(kit.ID)
            change_relationship_values([self.random_cat.ID],
                                       [kit],
                                       platonic_like=-20,
                                       dislike=40,
                                       admiration=-30,
                                       comfortable=-30,
                                       jealousy=0,
                                       trust=-30)

        # kill cats
        self.handle_death()

        # add necessary histories
        self.handle_death_history(murder)

        # handle injuries and injury history
        self.handle_injury()

        # change outsider rep
        if self.chosen_event.outsider:
            change_clan_reputation(self.chosen_event.outsider["changed"])
            if "misc" not in self.types:
                self.types.append("misc")

        # change other_clan rep
        if self.chosen_event.other_clan:
            change_clan_relations(self.other_clan, self.chosen_event.other_clan["changed"])
            if "other_clans" not in self.types:
                self.types.append("other_clans")

        # change supplies
        if self.chosen_event.supplies:
            for block in self.chosen_event.supplies:
                if block["type"] == "freshkill":
                    self.handle_freshkill_supply(block)
                else:  # if freshkill isn't being adjusted, then it must be a herb supply
                    self.handle_herb_supply(block)

        # give accessory
        if self.chosen_event.new_accessory:
            self.handle_accessories()

        death_text = event_text_adjust(Cat, self.chosen_event.event_text, self)
        additional_event_text = ""

        game.cur_events_list.append(Single_Event(death_text + " " + additional_event_text, self.types, self.involved_cats))

    def handle_new_cats(self):

        if not self.chosen_event.new_cat:
            return

        if "new_cat" not in self.types:
            self.types.append("new_cat")

        extra_text = None

        in_event_cats = {
            "m_c": self.main_cat
        }
        if self.random_cat:
            in_event_cats["r_c"] = self.random_cat
        for i, attribute_list in enumerate(self.chosen_event.new_cat):

            self.new_cats.append(
                create_new_cat_block(Cat, Relationship, self, in_event_cats, i, attribute_list))

            # check if we want to add some extra info to the event text
            for cat in self.new_cats[-1]:
                if cat.dead:
                    extra_text = f"{cat.name}'s ghost now wanders."
                elif cat.outside:
                    extra_text = f"The Clan now knows of {cat.name}."

        # Check to see if any young litters joined with alive parents.
        # If so, see if recoveing from birth condition is needed and give the condition
        for sub in self.new_cats:
            if sub[0].moons < 3:
                # Search for parent
                for sub_sub in self.new_cats:
                    if sub_sub[0] != sub[0] and (
                            sub_sub[0].gender == "female" or game.clan.clan_settings['same sex birth']) \
                            and sub_sub[0].ID in (sub[0].parent1, sub[0].parent2) and not (
                            sub_sub[0].dead or sub_sub[0].outside):
                        sub_sub[0].get_injured("recovering from birth")
                        break  # Break - only one parent ever gives birth

        if extra_text:
            self.chosen_event.event_text = self.chosen_event.event_text + " " + extra_text

    def handle_accessories(self):
        """
        handles giving accessories to the main_cat
        """
        if "misc" not in self.types:
            self.types.append("misc")
        acc_list = []
        possible_accs = self.chosen_event.new_accessory
        if "WILD" in possible_accs:
            acc_list.extend(Pelt.wild_accessories)
        if "PLANT" in possible_accs:
            acc_list.extend(Pelt.plant_accessories)
        if "COLLAR" in possible_accs:
            acc_list.extend(Pelt.collars)

        for acc in possible_accs:
            if acc not in ["WILD", "PLANT", "COLLAR"]:
                acc_list.append(acc)

        if "NOTAIL" in self.main_cat.pelt.scars or "HALFTAIL" in self.main_cat.pelt.scars:
            for acc in Pelt.tail_accessories:
                try:
                    acc_list.remove(acc)
                except ValueError:
                    print(f'attempted to remove {acc} from possible acc list, but it was not in the list!')

        self.main_cat.pelt.accessory = random.choice(acc_list)

    def handle_death(self):
        """
        handles killing/murdering cats and assigning histories
        """

        current_lives = int(game.clan.leader_lives)

        # check if the bodies are retrievable
        if "no_body" in self.chosen_event.tags:
            body = False
        else:
            body = True
        pass

        # kill main cat
        if self.chosen_event.m_c["dies"]:
            if "birth_death" not in self.types:
                self.types.append("birth_death")

            if self.main_cat.status == 'leader':
                if "all_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= 10
                    self.additional_event_text += self.main_cat.die(body)
                elif "some_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= random.randrange(2, current_lives - 1)
                    self.additional_event_text += self.main_cat.die(body)
                else:
                    game.clan.leader_lives -= 1
                    self.additional_event_text += self.main_cat.die(body)

            else:
                self.additional_event_text += self.main_cat.die(body)

        # kill random_cat
        if self.chosen_event.r_c["dies"]:
            if "birth_death" not in self.types:
                self.types.append("birth_death")

            if self.random_cat.status == 'leader':
                if "all_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= 10
                    self.additional_event_text += self.random_cat.die(body)
                elif "some_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= random.randrange(2, current_lives - 1)
                    self.additional_event_text += self.random_cat.die(body)
                else:
                    game.clan.leader_lives -= 1
                    self.additional_event_text += self.random_cat.die(body)

            else:
                self.additional_event_text += self.random_cat.die(body)

    def handle_death_history(self, murder):
        """
        handles assigning histories
        """
        for block in self.chosen_event.history:
            # main_cat's history
            if "m_c" in block["cats"]:
                # death history
                if self.chosen_event.r_c["dies"]:
                    # find history
                    if self.main_cat.status == "leader":
                        death_history = block.get("lead_death")
                    else:
                        death_history = block.get("reg_death")

                    # handle murder
                    murder_unrevealed_history = None
                    if murder:
                        if "revealed" in self.chosen_event.tags:
                            revealed = True
                        else:
                            # FIXME: seems like there are no events that make use of unrevealed history?
                            #  does it work? is it just not being utilized correctly?
                            if self.main_cat.status == 'leader':
                                murder_unrevealed_history = block.get("lead_murder_unrevealed")
                            else:
                                murder_unrevealed_history = block.get("reg_murder_unrevealed")
                            revealed = False

                        death_history = history_text_adjust(death_history, self.other_clan_name, game.clan,
                                                            self.random_cat)

                        if murder_unrevealed_history:
                            murder_unrevealed_history = history_text_adjust(murder_unrevealed_history,
                                                                            self.other_clan_name,
                                                                            game.clan, self.random_cat)
                        History.add_murders(self.main_cat, self.random_cat, revealed, death_history,
                                            murder_unrevealed_history)

                    History.add_death(self.main_cat, death_history, other_cat=self.random_cat,
                                      extra_text=murder_unrevealed_history)

            # random_cat history
            if "r_c" in block["cats"]:
                # death history
                # TODO: problematic as we currently cannot mark who is the r_c and who is the m_c
                #  should consider if we can have history text be converted to use the cat's ID number in place of abbrs
                if self.chosen_event.r_c["dies"]:
                    if self.random_cat.status == 'leader':
                        death_history = history_text_adjust(block.get('lead_death'),
                                                            self.other_clan_name, game.clan, self.random_cat)
                    else:
                        death_history = history_text_adjust(block.get('reg_death'),
                                                            self.other_clan_name, game.clan, self.random_cat)

                    History.add_death(self.random_cat, death_history, other_cat=self.random_cat)

            for abbr in self.chosen_event.history["cats"]:
                if "n_c" in abbr:
                    for i, new_cats in enumerate(self.new_cats):
                        if new_cats[i].dead:
                            death_history = history_text_adjust(self.chosen_event.history_text.get('reg_death'),
                                                                self.other_clan_name, game.clan, self.random_cat)
                            History.add_death(new_cats[i], death_history, other_cat=self.random_cat)

    def handle_injury(self):
        """
        assigns an injury to involved cats and then assigns possible histories (if in classic, assigns scar and scar history)
        """

        # if no injury block, then no injury gets assigned
        if not self.chosen_event.injury:
            return

        if "health" not in self.types:
            self.types.append("health")

        # now go through each injury block
        for block in self.chosen_event.injury:
            cats_affected = self.chosen_event.injury["cats"]

            # classic mode only gains scars, not injuries
            if game.clan.game_mode == "classic":
                for abbr in cats_affected:
                    # MAIN CAT
                    if abbr == "m_c":
                        if self.chosen_event.injury["scars"] and len(self.main_cat.pelt.scars) < 4:
                            # add a scar
                            self.main_cat.pelt.scars.append(random.choice(self.chosen_event.injury["scars"]))
                            self.handle_injury_history(self.main_cat, "m_c")

                    # RANDOM CAT
                    elif abbr == "r_c":
                        if self.chosen_event.injury["scars"] and len(self.random_cat.pelt.scars) < 4:
                            # add a scar
                            self.random_cat.pelt.scars.append(random.choice(self.chosen_event.injury["scars"]))
                            self.handle_injury_history(self.random_cat, "r_c")

                    # NEW CATS
                    elif "n_c" in abbr:
                        for i, new_cats in enumerate(self.new_cats):
                            if self.chosen_event.injury["scars"] and len(new_cats[i].pelt.scars) < 4:
                                # add a scar
                                new_cats[i].pelt.scars.append(random.choice(self.chosen_event.injury["scars"]))
                                self.handle_injury_history(new_cats[i], abbr)

            # now give injuries to other modes
            else:
                # find all possible injuries
                possible_injuries = []
                for injury in block["injuries"]:
                    if injury in INJURY_GROUPS:
                        possible_injuries.extend(INJURY_GROUPS[injury])
                    else:
                        possible_injuries.append(injury)

                # give the injury
                for abbr in cats_affected:
                    # MAIN CAT
                    if abbr == "m_c":
                        injury = random.choice(possible_injuries)
                        self.main_cat.get_injured(injury)
                        self.handle_injury_history(self.main_cat, "m_c", injury)

                    # RANDOM CAT
                    elif abbr == "r_c":
                        injury = random.choice(possible_injuries)
                        self.random_cat.get_injured(injury)
                        self.handle_injury_history(self.random_cat, "r_c", injury)

                    # NEW CATS
                    elif "n_c" in abbr:
                        for i, new_cats in enumerate(self.new_cats):
                            injury = random.choice(possible_injuries)
                            new_cats[i].get_injured(injury)
                            self.handle_injury_history(new_cats[i], abbr, injury)

    def handle_injury_history(self, cat, cat_abbr, injury=None):
        """
        handle injury histories
        :param cat: the cat object for cat being injured
        :param cat_abbr: the abbreviation used for this cat within the event format (i.e. m_c, r_c, ect)
        :param injury: the injury being given, if in classic then leave this as the default None
        """
        # TODO: problematic as we currently cannot mark who is the r_c and who is the m_c
        #  should consider if we can have history text be converted to use the cat's ID number in place of abbrs

        # if injury is false, then this is classic and they just need scar history
        if not injury:
            for block in self.chosen_event.history:
                if cat_abbr in block["cats"]:
                    history_text = history_text_adjust(block["scar"], self.other_clan_name, game.clan, self.random_cat)
                    History.add_scar(cat, history_text)
                    break
        else:
            for block in self.chosen_event.history:
                if cat_abbr in block["cats"]:
                    possible_death = None
                    possible_scar = history_text_adjust(block["scar"], self.other_clan_name, game.clan, self.random_cat)
                    if cat.status == "leader":
                        possible_death = history_text_adjust(block["lead_death"], self.other_clan_name, game.clan,
                                                             self.random_cat)
                    else:
                        possible_death = history_text_adjust(block["reg_death"], self.other_clan_name, game.clan,
                                                             self.random_cat)
                    if possible_scar or possible_death:
                        History.add_possible_history(cat, injury, scar_text=possible_scar, death_text=possible_death,
                                                     other_cat=self.random_cat)

    def handle_freshkill_supply(self, block, freshkill_pile: Freshkill_Pile = game.clan.freshkill_pile):
        """
        handles adjusting the amount of freshkill according to info in block
        """
        if game.clan.game_mode == "classic":
            return

        if "misc" not in self.types:
            self.types.append("misc")

        adjustment = block["adjust"]
        reduce_amount = 0
        increase_amount = 0

        if adjustment == "reduce_full":
            reduce_amount = int(freshkill_pile.total_amount)
        elif adjustment == "reduce_half":
            reduce_amount = int(freshkill_pile.total_amount / 2)
        elif adjustment == "reduce_quarter":
            reduce_amount = int(freshkill_pile.total_amount / 4)
        elif adjustment == "reduce_eighth":
            reduce_amount = -int(freshkill_pile.total_amount / 8)
        elif "increase" in adjustment:
            increase_amount = adjustment.split("_")[1]

        if reduce_amount != 0:
            freshkill_pile.remove_freshkill(reduce_amount, take_random=True)
        if increase_amount != 0:
            freshkill_pile.add_freshkill(increase_amount)

    def handle_herb_supply(self, block):
        if "misc" not in self.types:
            self.types.append("misc")

        herbs = game.clan.herbs

        adjustment = block["adjust"]
        supply_type = block["type"]

        # adjust entire herb store
        if supply_type == "all_herb":
            for herb in herbs:
                if adjustment == "reduce_full":
                    herbs[herb] = 0
                elif adjustment == "reduce_half":
                    herbs[herb] = game.clan.herbs[herb] / 2
                elif adjustment == "reduce_quarter":
                    herbs[herb] = game.clan.herbs[herb] / 4
                elif adjustment == "reduce_eighth":
                    herbs[herb] = game.clan.herbs[herb] / 8
                elif "increase" in adjustment:
                    herbs[herb] += adjustment.split("_")[1]

        # if we weren't adjusted the whole herb store, then adjust an individual
        else:
            # picking a random herb to adjust
            if supply_type == "any_herb":
                chosen_herb = random.choice(herbs.keys)
            # if it wasn't a random herb or all herbs, then it's one specific herb
            else:
                chosen_herb = supply_type

            # now adjust the supply for the chosen_herb
            if adjustment == "reduce_full":
                game.clan.herbs[chosen_herb] = 0
            elif adjustment == "reduce_half":
                game.clan.herbs[chosen_herb] = game.clan.herbs[chosen_herb] / 2
            elif adjustment == "reduce_quarter":
                game.clan.herbs[chosen_herb] = game.clan.herbs[chosen_herb] / 4
            elif adjustment == "reduce_eighth":
                game.clan.herbs[chosen_herb] = game.clan.herbs[chosen_herb] / 8
            elif "increase" in adjustment:
                game.clan.herbs[chosen_herb] += adjustment.split("_")[1]

    @staticmethod
    def handle_witness(main_cat, random_cat):
        """
        on hold until personality rework because i'd rather not have to figure this out a second time
        tentative plan is to have capability for a cat to witness the murder and then have a reaction based off trait
        and perhaps reveal it to other Clan members
        """
        # TODO: this is unused and I'm unsure of the plan for it
        witness = None
        # choose the witness
        possible_witness = list(
            filter(
                lambda c: not c.dead and not c.exiled and not c.outside and
                          (c.ID != main_cat.ID) and (c.ID != random_cat.ID), Cat.all_cats.values()))
        # If there are possible other cats...
        if possible_witness:
            witness = random.choice(possible_witness)
        if witness:
            # first, affect relationship
            change_relationship_values([random_cat],
                                       [witness.ID],
                                       romantic_love=-40,
                                       platonic_like=-40,
                                       dislike=50,
                                       admiration=-40,
                                       comfortable=-40,
                                       trust=-50
                                       )
