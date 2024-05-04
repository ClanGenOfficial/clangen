import random
from typing import List

from scripts.cat.cats import Cat, INJURIES
from scripts.cat.history import History
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values, get_alive_kits, \
    history_text_adjust, get_warring_clan, unpack_rel_block
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event


# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class Death_Events():
    """All events with a connection to death."""
    # TODO: adjust to fit new event format, consider what can move to utility.py
    def __init__(self):
        self.involved_cats = []

        self.main_cat = None
        self.random_cat = None
        self.new_cats: List[List[Cat]] = []
        self.victim_cat = None
        self.other_clan = None
        self.other_clan_name = None
        
        self.chosen_event = None
        self.additional_event_text = ""

    def handle_event(self, main_cat, random_cat, war, alive_kits, murder=False):
        """ 
        This function handles the deaths
        """
        self.main_cat = main_cat
        self.random_cat = random_cat

        self.involved_cats = [self.main_cat.ID]

        enemy_clan = get_warring_clan()  # TODO: if we can just find enemy clan here, take these checks out of event.py

        if enemy_clan:
            self.other_clan = enemy_clan
        else:
            self.other_clan = random.choice(game.clan.all_clans if game.clan.all_clans else None)

        if self.other_clan:
            self.other_clan_name = f'{self.other_clan.name}Clan'
        else:
            self.other_clan_name = None

        possible_short_events = GenerateEvents.possible_short_events("death")

        final_events = GenerateEvents.filter_possible_short_events(possible_short_events,
                                                                   self.main_cat,
                                                                   self.random_cat,
                                                                   war,
                                                                   enemy_clan,
                                                                   self.other_clan,
                                                                   alive_kits,
                                                                   murder=murder)

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

        # change relationships before killing anyone
        unpack_rel_block(Cat, self.chosen_event.relationships, Death_Events)

        # kill cats
        self.handle_death(murder)

        # handle injuries
        if self.chosen_event.injury:
            for injury in self.chosen_event.injury:
                pass

        # change outsider rep
        if self.chosen_event.outsider:
            pass

        # change other_clan rep
        if self.chosen_event.other_clan:
            pass

        # change supplies
        if self.chosen_event.supplies:
            pass

        # give accessory
        if self.chosen_event.new_accessory:
            pass

        # TODO: move text adjust down? i don't think that breaks it
        death_text = event_text_adjust(Cat, self.chosen_event.event_text, main_cat, random_cat, self.other_clan_name)
        additional_event_text = ""

        # give injuries to other cat if tagged as such
        if "other_cat_injured" in chosen_event.tags:
            for tag in chosen_event.tags:
                if tag in INJURIES:
                    random_cat.get_injured(tag)
                    #TODO: consider how best to handle history for this (aka fix it later cus i don't wanna rn ;-;
                    #  and it's not being used by any events yet anyways)

        # handle relationships with other clans
        if "rel_down" in chosen_event.tags:
            difference = -3
            change_clan_relations(other_clan, difference=difference)
        elif "rel_up" in chosen_event.tags:
            difference = 3
            change_clan_relations(other_clan, difference=difference)

        types = ["birth_death"]
        if "other_clan" in chosen_event.tags:
            types.append("other_clans")
        game.cur_events_list.append(Single_Event(death_text + " " + additional_event_text, types, self.involved_cats))

    def handle_death(self, murder):
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
            # find history
            if self.main_cat.status == "leader":
                death_history = self.chosen_event.history.get("lead_death")
            else:
                death_history = self.chosen_event.history.get("reg_death")

            # handle murder
            murder_unrevealed_history = None
            if murder:
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
                if "revealed" in self.chosen_event.tags:
                    revealed = True
                else:
                    if self.main_cat.status == 'leader':
                        murder_unrevealed_history = self.chosen_event.history_text.get("lead_murder_unrevealed")
                    else:
                        murder_unrevealed_history = self.chosen_event.history_text.get("reg_murder_unrevealed")
                    revealed = False

                death_history = history_text_adjust(death_history, self.other_clan_name, game.clan)
                if murder_unrevealed_history:
                    murder_unrevealed_history = history_text_adjust(murder_unrevealed_history,
                                                                    self.other_clan_name,
                                                                    game.clan)
                History.add_murders(self.main_cat, self.random_cat, revealed, death_history, murder_unrevealed_history)

            # kill main cat and assign history
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
                death_history = history_text_adjust(death_history, self.other_clan_name, game.clan)

            else:
                self.additional_event_text += self.main_cat.die(body)
                death_history = history_text_adjust(death_history, self.other_clan_name, game.clan)

            History.add_death(self.main_cat, death_history, other_cat=self.random_cat,
                              extra_text=murder_unrevealed_history)

        # kill r_c
        if self.chosen_event.r_c["dies"]:
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
                death_history = history_text_adjust(self.chosen_event.history_text.get('lead_death'), self.other_clan_name, game.clan)

            else:
                self.additional_event_text += self.random_cat.die(body)
                death_history = history_text_adjust(self.chosen_event.history_text.get('reg_death'), self.other_clan_name, game.clan)

            History.add_death(self.random_cat, death_history, other_cat=self.random_cat)


    @staticmethod
    def handle_witness(main_cat, random_cat):
        """
        on hold until personality rework because i'd rather not have to figure this out a second time
        tentative plan is to have capability for a cat to witness the murder and then have a reaction based off trait
        and perhaps reveal it to other Clan members
        """
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


