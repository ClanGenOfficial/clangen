import random

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event

# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class MiscEvents():
    """All events that do not fit in a different category."""

    @staticmethod
    def handle_misc_events(cat, other_cat=None, war=False, enemy_clan=None, alive_kits=False, accessory=False, ceremony=False):
        """ 
        This function handles the misc events
        """
        involved_cats = [cat.ID]
        if war:
            other_clan = enemy_clan
        else:
            other_clan = random.choice(game.clan.all_clans)
        
        other_clan_name = None
        if other_clan:
            other_clan_name = f'{other_clan.name}Clan'

        possible_events = GenerateEvents.possible_short_events(cat.status, cat.age, "misc_events")
        acc_checked_events = []
        for event in possible_events:
            if (ceremony and "ceremony" not in event.tags) or (not ceremony and "ceremony" in event.tags):
                continue

            if (not accessory and event.accessories) or (accessory and not event.accessories):
                continue

            if "other_cat" in event.tags and not other_cat:
                other_cat = Cat.fetch_cat(random.choice(Cat.all_cats_list))
                if other_cat.dead or other_cat.outside:
                    other_cat = None

            acc_checked_events.append(event)
            
        reveal = False
        victim = None
        cat_history = History.get_murders(cat)
        if cat_history:
            if "is_murderer" in cat_history:
                murder_history = cat_history["is_murderer"]
                for murder in murder_history:
                    murder_index = murder_history.index(murder)
                    if murder_history[murder_index]["revealed"] is True:
                        continue
                    victim = murder_history[murder_index]["victim"]
                    reveal = True
                    break

        #print('misc event', cat.ID)
        final_events = GenerateEvents.filter_possible_short_events(acc_checked_events, cat, other_cat, war, enemy_clan, other_clan,
                                                                   alive_kits, murder_reveal=reveal)

        # ---------------------------------------------------------------------------- #
        #                                    event                                     #
        # ---------------------------------------------------------------------------- #
        try:
            misc_event = random.choice(final_events)
        except:
            print('ERROR: no misc events available for this cat')
            return

        if misc_event.accessories:
            MiscEvents.handle_accessories(cat, misc_event.accessories)

        # let's change some relationship values \o/ check if another cat is mentioned and if they live
        if "other_cat" in misc_event.tags:
            involved_cats.append(other_cat.ID)
            MiscEvents.handle_relationship_changes(cat, misc_event, other_cat)
        else:
            other_cat = None

        if "rel_down" in misc_event.tags:
            difference = -1
            change_clan_relations(other_clan, difference=difference)

        elif "rel_up" in misc_event.tags:
            difference = 1
            change_clan_relations(other_clan, difference=difference)

        event_text = event_text_adjust(Cat, misc_event.event_text, cat, other_cat, other_clan_name, murder_reveal=reveal, victim=victim)
        
        if event_text:
            # Add event text to the relationship log if two cats are involved
            if other_cat:
                pos_rel_event = ["romantic", "platonic", "neg_dislike", "respect", "comfort", "neg_jealousy", "trust"]
                neg_rel_event = ["neg_romantic", "neg_platonic", "dislike", "neg_respect", "neg_comfort", "jealousy", "neg_trust"]
                effect = ""
                if any(tag in misc_event.tags for tag in pos_rel_event):
                    effect = " (positive effect)"
                elif any(tag in misc_event.tags for tag in neg_rel_event):
                    effect = " (negative effect)"

                log_text = event_text + effect

                if other_cat.ID not in cat.relationships:
                    cat.relationships[other_cat.ID] = Relationship(cat, other_cat)

                if cat.ID not in other_cat.relationships:
                    other_cat.relationships[cat.ID] = Relationship(other_cat, cat)

                if cat.moons == 1:
                    cat.relationships[other_cat.ID].log.append(log_text + f" - {cat.name} was {cat.moons} moon old")
                else:
                    cat.relationships[other_cat.ID].log.append(log_text + f" - {cat.name} was {cat.moons} moons old")

        types = ["misc"]
        if "other_clan" in misc_event.tags:
            types.append("other_clans")
        if ceremony:
            types.append("ceremony")

        # to remove double the event
        # (example which might happen would be: "The tension between c_n and o_c is palpable, with even the smallest actions potentially leading to violence.")
        same_text_events = [event for event in game.cur_events_list if event.text == event_text]
        if len(same_text_events) > 0:
            return

        game.cur_events_list.append(Single_Event(event_text, types, involved_cats))

        if reveal:
            History.reveal_murder(cat, other_cat, Cat, victim, murder_index)

    @staticmethod
    def handle_relationship_changes(cat, misc_event, other_cat):

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

    @staticmethod
    def handle_accessories(cat, possible_accs):
        acc_list = []
        if "WILD" in possible_accs:
            acc_list.extend(Pelt.wild_accessories)
        if "PLANT" in possible_accs:
            acc_list.extend(Pelt.plant_accessories)
        if "COLLAR" in possible_accs:
            acc_list.extend(Pelt.collars)

        for acc in possible_accs:
            if acc not in ["WILD", "PLANT", "COLLAR"]:
                acc_list.append(acc)

        if "NOTAIL" in cat.pelt.scars or "HALFTAIL" in cat.pelt.scars:
            for acc in Pelt.tail_accessories:
                try:
                    acc_list.remove(acc)
                except ValueError:
                    print(f'attempted to remove {acc} from possible acc list, but it was not in the list!')


        cat.pelt.accessory = random.choice(acc_list)

    @staticmethod
    def handle_murder_self_reveals(cat):
        ''' Handles reveals for murders where the murderer reveals themself '''
        if cat.personality.lawfulness > 8:
            murderer_guilty = random.choice([True, False])
        chance_of_reveal = 120
        if murderer_guilty:
            chance_of_reveal = chance_of_reveal - 100

        # testing purposes
        chance_of_reveal = 1

        chance_roll = random.randint(0, chance_of_reveal)
        print(chance_roll)

        return bool(chance_roll = 1)

    @staticmethod
    def handle_murder_witness_reveals(cat, other_cat):
        ''' Handles reveals where the witness reveals the murderer '''