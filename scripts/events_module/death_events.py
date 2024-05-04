import random

from scripts.cat.cats import Cat, INJURIES
from scripts.cat.history import History
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values, get_alive_kits, \
    history_text_adjust, get_warring_clan
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event


# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class Death_Events():
    """All events with a connection to death."""
    # TODO: adjust to fit new event format, consider what can move to utility.py

    @staticmethod
    def handle_deaths(main_cat, random_cat, war, alive_kits, murder=False):
        """ 
        This function handles the deaths
        """
        involved_cats = [main_cat.ID]

        enemy_clan = get_warring_clan()  # TODO: if we can just find enemy clan here, take these checks out of event.py

        if enemy_clan:
            other_clan = enemy_clan
        else:
            other_clan = random.choice(game.clan.all_clans if game.clan.all_clans else None)

        if other_clan:
            other_clan_name = f'{other_clan.name}Clan'
        else:
            other_clan_name = None

        current_lives = int(game.clan.leader_lives)

        possible_short_events = GenerateEvents.possible_short_events("death")

        final_events = GenerateEvents.filter_possible_short_events(possible_short_events,
                                                                   main_cat,
                                                                   random_cat,
                                                                   war,
                                                                   enemy_clan,
                                                                   other_clan,
                                                                   alive_kits,
                                                                   murder=murder)

        # ---------------------------------------------------------------------------- #
        #                                  kill cats                                   #
        # ---------------------------------------------------------------------------- #
        try:
            death_cause = (random.choice(final_events))
        except IndexError:
            print('WARNING: no death events found for', main_cat.name)
            return

        death_text = event_text_adjust(Cat, death_cause.event_text, main_cat, random_cat, other_clan_name)
        additional_event_text = ""

        # assign default history
        if main_cat.status == 'leader':
            death_history = death_cause.history_text.get("lead_death")
        else:
            death_history = death_cause.history_text.get("reg_death")

        # handle murder
        revealed = False
        murder_unrevealed_history = None
        if murder:
            if "kit_manipulated" in death_cause.tags:
                kit = Cat.fetch_cat(random.choice(get_alive_kits(Cat)))
                involved_cats.append(kit.ID)
                change_relationship_values([random_cat.ID],
                                           [kit],
                                           platonic_like=-20,
                                           dislike=40,
                                           admiration=-30,
                                           comfortable=-30,
                                           jealousy=0,
                                           trust=-30)
            if "revealed" in death_cause.tags:
                revealed = True
            else:
                if main_cat.status == 'leader':
                    death_history = death_cause.history_text.get("lead_death")
                    murder_unrevealed_history = death_cause.history_text.get("lead_murder_unrevealed")
                else:
                    death_history = death_cause.history_text.get("reg_death")
                    murder_unrevealed_history = death_cause.history_text.get("reg_murder_unrevealed")
                revealed = False

            death_history = history_text_adjust(death_history, other_clan_name, game.clan)
            if murder_unrevealed_history:
                murder_unrevealed_history = history_text_adjust(murder_unrevealed_history, other_clan_name, game.clan)
            History.add_murders(main_cat, random_cat, revealed, death_history, murder_unrevealed_history)

        # check if the main_cat's body was retrievable
        if "no_body" in death_cause.tags:
            body = False
        else:
            body = True

        # handle other cat
        if random_cat and "other_cat" in death_cause.tags:
            # if at least one cat survives, change relationships
            if "multi_death" not in death_cause.tags:
                Death_Events.handle_relationship_changes(main_cat, death_cause, random_cat)
            # handle murder history
            if murder:
                if revealed:
                    involved_cats.append(random_cat.ID)
            else:
                involved_cats.append(random_cat.ID)

        # give history to main_cat if they die
        if main_cat.status == 'leader':
            if "all_lives" in death_cause.tags:
                game.clan.leader_lives -= 10
                additional_event_text += main_cat.die(body)
            elif "some_lives" in death_cause.tags:
                game.clan.leader_lives -= random.randrange(2, current_lives - 1)
                additional_event_text += main_cat.die(body)
            else:
                game.clan.leader_lives -= 1
                additional_event_text += main_cat.die(body)
            death_history = history_text_adjust(death_history, other_clan_name, game.clan)

        else:
            additional_event_text += main_cat.die(body)
            death_history = history_text_adjust(death_history, other_clan_name, game.clan)

        History.add_death(main_cat, death_history, other_cat=random_cat, extra_text=murder_unrevealed_history)

        # give death history to other cat and kill them if they die
        if "multi_death" in death_cause.tags:
            if random_cat.status == 'leader':
                if "all_lives" in death_cause.tags:
                    game.clan.leader_lives -= 10
                    additional_event_text += random_cat.die(body)
                elif "some_lives" in death_cause.tags:
                    game.clan.leader_lives -= random.randrange(2, current_lives - 1)
                    additional_event_text += random_cat.die(body)
                else:
                    game.clan.leader_lives -= 1
                    additional_event_text += random_cat.die(body)
                other_death_history = history_text_adjust(death_cause.history_text.get('lead_death'), other_clan_name, game.clan)

            else:
                additional_event_text += random_cat.die(body)
                other_death_history = history_text_adjust(death_cause.history_text.get('reg_death'), other_clan_name, game.clan)

            History.add_death(random_cat, other_death_history, other_cat=random_cat)

        # give injuries to other cat if tagged as such
        if "other_cat_injured" in death_cause.tags:
            for tag in death_cause.tags:
                if tag in INJURIES:
                    random_cat.get_injured(tag)
                    #TODO: consider how best to handle history for this (aka fix it later cus i don't wanna rn ;-;
                    #  and it's not being used by any events yet anyways)

        # handle relationships with other clans
        if "rel_down" in death_cause.tags:
            difference = -3
            change_clan_relations(other_clan, difference=difference)
        elif "rel_up" in death_cause.tags:
            difference = 3
            change_clan_relations(other_clan, difference=difference)

        types = ["birth_death"]
        if "other_clan" in death_cause.tags:
            types.append("other_clans")
        game.cur_events_list.append(Single_Event(death_text + " " + additional_event_text, types, involved_cats))

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


