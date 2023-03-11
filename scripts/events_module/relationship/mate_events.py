
from random import choice
import random

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.utility import (get_highest_romantic_relation, event_text_adjust, get_personality_compatibility)
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event
from scripts.cat.cats import Cat

class Mate_Events():
    """All events which are related to mate's such as becoming mates and breakups."""
    
    def __init__(self) -> None:
        self.had_one_event = False
        pass


    def handle_new_mates(self, relationship, cat_from, cat_to):
        """More in depth check if the cats will become mates."""
        relationship_to = relationship.opposite_relationship
        become_mates, mate_string = self.check_if_new_mate(relationship, relationship_to, cat_from, cat_to)

        if become_mates and mate_string:
            self.had_one_event = True
            cat_from.set_mate(cat_to)
            cat_to.set_mate(cat_from)
            game.cur_events_list.append(Single_Event(mate_string, "relation", [cat_from.ID, cat_to.ID]))

    def handle_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        from_mate_in_clan = False
        if cat_from.mate:
            if cat_from.mate not in Cat.all_cats.keys():
                print(f"WARNING: Cat #{cat_from} has a invalid mate. It will set to none.")
                cat_from.mate = None
                return
            cat_from_mate = Cat.all_cats.get(cat_from.mate)
            from_mate_in_clan = cat_from_mate.is_alive() and not cat_from_mate.outside

        if not self.had_one_event and relationship_from.mates and from_mate_in_clan:
            if self.check_if_breakup(relationship_from, relationship_to, cat_from, cat_to):
                # TODO: filter log to check if last interaction was a fight
                had_fight = False
                self.had_one_event = True
                cat_from.unset_mate(breakup=True, fight=had_fight)
                cat_to.unset_mate(breakup=True, fight=had_fight)
                text = f"{cat_from.name} and {cat_to.name} broke up."
                # game.relation_events_list.insert(0, text)
                game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_to.ID]))

    def big_love_check(self, cat, upper_threshold=40, lower_threshold=15):
        """
        Check if the cat has a high love for another and mate them if there are in the boundaries 
        :param cat: cat in question
        :upper_threshold integer:
        :lower_threshold integer:

        return: bool if event is triggered or not
        """
        # get the highest romantic love relationships and
        highest_romantic_relation = get_highest_romantic_relation(cat.relationships.values())
        max_love_value = 0
        if highest_romantic_relation is not None:
            max_love_value = highest_romantic_relation.romantic_love

        if max_love_value < upper_threshold:
            return False

        cat_to = highest_romantic_relation.cat_to
        if cat_to.is_potential_mate(cat) and cat.is_potential_mate(cat_to):
            if cat_to.mate is None and cat.mate is None:
                self.had_one_event = True
                cat.set_mate(cat_to)
                cat_to.set_mate(cat)

                if highest_romantic_relation.opposite_relationship is None:
                    highest_romantic_relation.link_relationship()

                if highest_romantic_relation.opposite_relationship.romantic_love <= lower_threshold:
                    mate_string = choice(MATE_DICTS["rejected"])
                    mate_string = event_text_adjust(Cat, mate_string, cat, cat_to)
                    game.cur_events_list.append(Single_Event(mate_string, "relation", [cat.ID, cat_to.ID]))
                    return False
                else:
                    mate_string = choice(MATE_DICTS["high_romantic"])
                    mate_string = event_text_adjust(Cat, mate_string, cat, cat_to)
                    game.cur_events_list.append(Single_Event(mate_string, "relation", [cat.ID, cat_to.ID]))
                    return True
        return False


    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    def check_if_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        """ More in depth check if the cats will break up.
            Returns:
                bool (True or False)
        """
        will_break_up = False
        # TODO: Check log for had fight check
        had_fight = False

        chance_number = self.get_breakup_chance(relationship_from, relationship_to, cat_from, cat_to)

        # chance = randint(1, chance_number)
        chance = int(random.random() * chance_number)
        if not chance:
            if relationship_from.dislike > 30:
                will_break_up = True
                relationship_to.romantic_love -= 10
                relationship_from.romantic_love -= 10
            elif relationship_from.romantic_love < 50:
                will_break_up = True
                relationship_to.romantic_love -= 10
                relationship_from.romantic_love -= 10
            elif had_fight:
                text = f"{cat_from.name} and {cat_to.name} had a fight and nearly broke up."
                # game.relation_events_list.insert(0, text)
                game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_to.ID]))
            else:
                text = f"{cat_from.name} and {cat_to.name} have somewhat different views about their relationship."
                # game.relation_events_list.insert(0, text)
                game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_to.ID]))
                relationship_from.romantic_love -= 10
                relationship_to.romantic_love -= 10
                relationship_from.comfortable -= 20
                relationship_to.comfortable -= 20
                relationship_from.platonic_like -= 20
                relationship_to.platonic_like -= 20
                relationship_from.admiration -= 10
                relationship_to.admiration -= 10

        return will_break_up

    def check_if_new_mate(self, relationship_from, relationship_to, cat_from, cat_to):
        """Checks if the two cats can become mates, or not. Returns: boolean and event_string"""
        become_mates = False
        young_age = ['kitten', 'adolescent']
        if cat_from.age in young_age or cat_to.age in young_age:
            return become_mates

        mate_string = None
        mate_chance = 5
        hit = int(random.random() * mate_chance)

        # has to be high because every moon this will be checked for each relationship in the came
        random_mate_chance = 300
        random_hit = int(random.random() * random_mate_chance)

        low_dislike = relationship_from.dislike < 15 and relationship_to.dislike < 15
        high_like = relationship_from.platonic_like > 30 and relationship_to.platonic_like > 30
        semi_high_like = relationship_from.platonic_like > 20 and relationship_to.platonic_like > 20
        high_comfort = relationship_from.comfortable > 25 and relationship_to.comfortable > 25

        if not hit and relationship_from.romantic_love > 20 and relationship_to.romantic_love > 20 and semi_high_like:
            mate_string = choice(MATE_DICTS["low_romantic"])
            mate_string = event_text_adjust(Cat, mate_string, cat_from, cat_to)
            become_mates = True
        elif not random_hit and low_dislike and (high_like or high_comfort):
            mate_string = choice(MATE_DICTS["platonic_to_romantic"])
            mate_string = event_text_adjust(Cat, mate_string, cat_from, cat_to)
            become_mates = True

        return become_mates, mate_string

    # ---------------------------------------------------------------------------- #
    #                             get/calculate chances                            #
    # ---------------------------------------------------------------------------- #

    def get_breakup_chance(self, relationship_from, relationship_to, cat_from, cat_to):
        """ Looks into the current values and calculate the chance of breaking up. The lower, the more likely they will break up.
            Returns:
                integer (number)
        """
        chance_number = 80

        # change the chance based on the current relationship
        if relationship_from.romantic_love > 80:
            chance_number += 15
        elif relationship_from.romantic_love > 60:
            chance_number += 10
        if relationship_to.romantic_love > 80:
            chance_number += 15
        elif relationship_to.romantic_love > 60:
            chance_number += 10

        if relationship_from.platonic_like > 80:
            chance_number += 15
        elif relationship_from.platonic_like > 60:
            chance_number += 10
        if relationship_from.platonic_like > 80:
            chance_number += 15
        elif relationship_from.platonic_like > 60:
            chance_number += 10

        chance_number -= int(relationship_from.dislike / 2)
        chance_number -= int(relationship_from.jealousy / 4)
        chance_number -= int(relationship_to.dislike / 2)
        chance_number -= int(relationship_to.jealousy / 4)

        # change the change based on the personality
        get_along = get_personality_compatibility(cat_from, cat_to)
        if get_along is not None and get_along:
            chance_number += 5
        if get_along is not None and not get_along:
            chance_number -= 10

        # change the chance based on the last interactions
        if len(relationship_from.log) > 0:
            # check last interaction
            last_log = relationship_from.log[len(relationship_from.log) - 1]

            if 'negative' in last_log:
                chance_number -= 30
                if 'fight' in last_log:
                    chance_number -= 20

            # check all interactions - the logs are still buggy
            # negative_interactions = list(filter(lambda inter: 'negative' in inter, relationship_from.log))
            # chance_number -= len(negative_interactions)
            # positive_interactions = list(filter(lambda inter: 'positive' in inter, relationship_from.log))
            # chance_number += len(positive_interactions)

            # if len(negative_interactions) > len(positive_interactions) and len(relationship_from.log) > 5 :
            #    chance_number -= 20

        # this should be nearly impossible, that chance is lower than 0
        if chance_number <= 0:
            chance_number = 1

        return chance_number



# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/relationship_events/"

MATE_DICTS = None
with open(f"{resource_directory}become_mates.json", 'r') as read_file:
    MATE_DICTS = ujson.loads(read_file.read())