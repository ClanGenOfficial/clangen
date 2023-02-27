import random

from scripts.cat.cats import Cat
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event

# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class MiscEvents():
    """All events that do not fit in a different category."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        self.generate_events = GenerateEvents()
        pass

    def handle_misc_events(self, cat, other_cat, war, enemy_clan, alive_kits):
        """ 
        This function handles the deaths
        """
        involved_cats = [cat.ID]
        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{other_clan.name}Clan'

        possible_events = self.generate_events.possible_events(cat.status, cat.age, "misc_events")
        final_events = self.generate_events.filter_possible_events(possible_events, cat, other_cat, war,
                                                                   enemy_clan, other_clan,
                                                                   alive_kits)

        # ---------------------------------------------------------------------------- #
        #                                    event                                     #
        # ---------------------------------------------------------------------------- #
        try:
            misc_event = random.choice(final_events)
        except:
            print('ERROR: no misc events available for this cat')
            return

        if "war" in misc_event.tags and other_clan is not None and enemy_clan is not None:
            other_clan = enemy_clan
            other_clan_name = other_clan.name + "Clan"

        # let's change some relationship values \o/ check if another cat is mentioned and if they live
        if "other_cat" in misc_event.tags:
            involved_cats.append(other_cat.ID)
            self.handle_relationship_changes(cat, misc_event, other_cat)
        else:
            other_cat = None
        event_text = event_text_adjust(Cat, misc_event.event_text, cat, other_cat, other_clan_name)

        if "rel_down" in misc_event.tags:
            difference = -5
            change_clan_relations(other_clan, difference=difference)

        elif "rel_up" in misc_event.tags:
            difference = 5
            change_clan_relations(other_clan, difference=difference)

        types = ["misc"]
        if "other_clan" in misc_event.tags:
            types.append("other_clans")
        game.cur_events_list.append(Single_Event(event_text, types, involved_cats))

    def handle_relationship_changes(self, cat, death_cause, other_cat):

        n = 5
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "rc_to_mc" in death_cause.tags:
            cat_to = [cat.ID]
            cat_from = [other_cat]
        elif "mc_to_rc" in death_cause.tags:
            cat_to = [other_cat.ID]
            cat_from = [cat]
        elif "to_both" in death_cause.tags:
            cat_to = [cat.ID, other_cat.ID]
            cat_from = [other_cat, cat]
        else:
            return
        if "romantic" in death_cause.tags:
            romantic = n
        elif "neg_romantic" in death_cause.tags:
            romantic = -n
        if "platonic" in death_cause.tags:
            platonic = n
        elif "neg_platonic" in death_cause.tags:
            platonic = -n
        if "dislike" in death_cause.tags:
            dislike = n
        elif "neg_dislike" in death_cause.tags:
            dislike = -n
        if "respect" in death_cause.tags:
            admiration = n
        elif "neg_respect" in death_cause.tags:
            admiration = -n
        if "comfort" in death_cause.tags:
            comfortable = n
        elif "neg_comfort" in death_cause.tags:
            comfortable = -n
        if "jealousy" in death_cause.tags:
            jealousy = n
        elif "neg_jealousy" in death_cause.tags:
            jealousy = -n
        if "trust" in death_cause.tags:
            trust = n
        elif "neg_trust" in death_cause.tags:
            trust = -n
        change_relationship_values(
            cat_to,
            cat_from,
            romantic,
            platonic,
            dislike,
            admiration,
            comfortable,
            jealousy,
            trust)

