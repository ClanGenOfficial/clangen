import random

from scripts.cat.cats import Cat
from scripts.cat.pelts import wild_accessories, plant_accessories, collars, tail_accessories
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
        self.event_sums = 0
        self.had_one_event = False
        self.generate_events = GenerateEvents()
        pass

    def handle_misc_events(self, cat, other_cat=None, war=False, enemy_clan=None, alive_kits=False, accessory=False, ceremony=False):
        """ 
        This function handles the misc events
        """
        involved_cats = [cat.ID]
        if war:
            other_clan = enemy_clan
        else:
            other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{other_clan.name}Clan'

        possible_events = self.generate_events.possible_short_events(cat.status, cat.age, "misc_events")
        acc_checked_events = []
        for event in possible_events:
            if (ceremony and "ceremony" not in event.tags) or (not ceremony and "ceremony" in event.tags):
                continue

            if (not accessory and event.accessories) or (accessory and not event.accessories):
                continue

            acc_checked_events.append(event)

        print('misc event', cat.ID)
        final_events = self.generate_events.filter_possible_short_events(acc_checked_events, cat, other_cat, war, enemy_clan, other_clan,
                                                                   alive_kits)

        # ---------------------------------------------------------------------------- #
        #                                    event                                     #
        # ---------------------------------------------------------------------------- #
        try:
            misc_event = random.choice(final_events)
        except:
            print('ERROR: no misc events available for this cat')
            return

        if misc_event.accessories:
            self.handle_accessories(cat, misc_event.accessories)

        # let's change some relationship values \o/ check if another cat is mentioned and if they live
        if "other_cat" in misc_event.tags:
            involved_cats.append(other_cat.ID)
            self.handle_relationship_changes(cat, misc_event, other_cat)
        else:
            other_cat = None

        if "rel_down" in misc_event.tags:
            difference = -1
            change_clan_relations(other_clan, difference=difference)

        elif "rel_up" in misc_event.tags:
            difference = 1
            change_clan_relations(other_clan, difference=difference)

        event_text = event_text_adjust(Cat, misc_event.event_text, cat, other_cat, other_clan_name)

        types = ["misc"]
        if "other_clan" in misc_event.tags:
            types.append("other_clans")
        if ceremony:
            types.append("ceremony")
        game.cur_events_list.append(Single_Event(event_text, types, involved_cats))

    def handle_relationship_changes(self, cat, misc_event, other_cat):

        n = 5
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "rc_to_mc" in misc_event.tags:
            cat_to = [cat.ID]
            cat_from = [other_cat]
        elif "mc_to_rc" in misc_event.tags:
            cat_to = [other_cat.ID]
            cat_from = [cat]
        elif "to_both" in misc_event.tags:
            cat_to = [cat.ID, other_cat.ID]
            cat_from = [other_cat, cat]
        else:
            return
        if "romantic" in misc_event.tags:
            romantic = n
        elif "neg_romantic" in misc_event.tags:
            romantic = -n
        if "platonic" in misc_event.tags:
            platonic = n
        elif "neg_platonic" in misc_event.tags:
            platonic = -n
        if "dislike" in misc_event.tags:
            dislike = n
        elif "neg_dislike" in misc_event.tags:
            dislike = -n
        if "respect" in misc_event.tags:
            admiration = n
        elif "neg_respect" in misc_event.tags:
            admiration = -n
        if "comfort" in misc_event.tags:
            comfortable = n
        elif "neg_comfort" in misc_event.tags:
            comfortable = -n
        if "jealousy" in misc_event.tags:
            jealousy = n
        elif "neg_jealousy" in misc_event.tags:
            jealousy = -n
        if "trust" in misc_event.tags:
            trust = n
        elif "neg_trust" in misc_event.tags:
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

    def handle_accessories(self, cat, possible_accs):
        acc_list = []
        if "WILD" in possible_accs:
            acc_list.extend(wild_accessories)
        if "PLANT" in possible_accs:
            acc_list.extend(plant_accessories)
        if "COLLAR" in possible_accs:
            acc_list.extend(collars)

        for acc in possible_accs:
            if acc not in ["WILD", "PLANT", "COLLAR"]:
                acc_list.append(acc)

        if ("NOTAIL" or "HALFTAIL") in cat.scars:
            try:
                acc_list.remove(acc for acc in tail_accessories)
            except:
                print('attempted to remove tail accs from possible acc list, but no tail accs were in the list!')

        cat.accessory = random.choice(acc_list)
