import itertools
import random
from random import choice, randint
import os
try:
    import ujson
except ImportError:
    import json as ujson
from copy import deepcopy

from scripts.game_structure.game_essentials import game
from scripts.events_module.condition_events import Condition_Events
from scripts.cat.cats import Cat
from scripts.utility import get_cats_same_age
from scripts.event_class import Single_Event
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.relationship.mate_events import Mate_Events
from scripts.events_module.relationship.welcoming_events import Welcoming_Events
from scripts.events_module.relationship.group_events import Group_Events

class Relation_Events():
    """All relationship events."""
    def __init__(self) -> None:
        self.had_one_event = False
        self.condition_events = Condition_Events()
        self.mate_events_class = Mate_Events()
        self.welcome_events_class = Welcoming_Events()
        self.group_events_class = Group_Events()
        self.cats_triggered_events = {}
        pass

    def handle_relationships(self, cat: Cat):
        """Checks the relationships of the cat and trigger events if possible.

            Parameters
            ----------
            cat : Cat
                the cat where the relationships should be checked

            Returns
            -------
        """
        if not cat.relationships:
            return
        self.had_one_event = False

        # currently try to trigger every moon, because there are not many group events
        # TODO: maybe change in future
        self.group_events(cat)

        # 1/3 for an additional event
        if not randint(0,2):
            self.same_age_events(cat)

        # this has to be handled at first
        if random.random() > 0.8:
            if self.mate_events_class.big_love_check(cat):
                return

        cats_amount = len(Cat.all_cats)
        # cap the maximal checks
        if cats_amount >= 30:
            range_number = 20
        else:
            range_number = int(cats_amount / 1.5)  # int(1.9) rounds to 1

        # for i in range(0, range_number):
        for _ in itertools.repeat(None, range_number):
            # random_index = randint(0, len(cat.relationships)-1)
            random_index = int(random.random() * len(cat.relationships))
            current_relationship = list(cat.relationships.values())[random_index]
            # get some cats to make easier checks
            cat_from = current_relationship.cat_from
            cat_from_mate = None
            if cat_from.mate:
                if cat_from.mate not in Cat.all_cats:
                    print(f"WARNING: Cat #{cat_from} has a invalid mate. It will set to none.")
                    cat_from.mate = None
                    return
                cat_from_mate = Cat.all_cats.get(cat_from.mate)

            cat_to = current_relationship.cat_to
            cat_to_mate = None
            if cat_to.mate:
                if cat_to.mate not in Cat.all_cats:
                    print(f"WARNING: Cat #{cat_to} has a invalid mate. It will set to none.")
                    cat_to.mate = None
                    return
                cat_to_mate = Cat.all_cats.get(cat_to.mate)

            if not current_relationship.opposite_relationship:
                current_relationship.link_relationship()

            # overcome dead mates
            if cat_from_mate and cat_from_mate.dead and cat_from_mate.dead_for >= 4 and "grief stricken" not in cat_from.illnesses:
                # randint is a slow function, don't call it unless we have to.
                if random.random() > 0.96:  # Roughly 1/25
                    self.had_one_event = True
                    text = f'{cat_from.name} will always love {cat_from_mate.name} but has decided to move on.'
                    # game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_from_mate.ID]))
                    current_relationship.mate = False
                    cat_from.mate = None
                    cat_from_mate.mate = None

            # new mates
            if not self.had_one_event and not cat_from_mate:
                if cat_to.is_potential_mate(cat_from):
                    self.mate_events_class.handle_new_mates(current_relationship, cat_from, cat_to)

            # breakup and new mate
            if (not self.had_one_event and cat_from.mate and
                    cat_from.is_potential_mate(cat_to) and cat_to.is_potential_mate(cat_from)
            ):
                love_over_30 = current_relationship.romantic_love > 30 and current_relationship.opposite_relationship.romantic_love > 30

                normal_chance = int(random.random() * 10)

                # compare love value of current mates
                bigger_than_current = False
                bigger_love_chance = int(random.random() * 3)

                mate_relationship = None
                if cat_from.mate in cat_from.relationships:
                    mate_relationship = cat_from.relationships[cat_from.mate]
                    bigger_than_current = current_relationship.romantic_love > mate_relationship.romantic_love
                else:
                    if cat_from_mate:
                        cat_from_mate.relationships[cat_from.ID] = Relationship(cat_from_mate, cat_from, True)
                    bigger_than_current = True

                # check cat_to values
                if cat_to_mate:
                    if cat_from.ID in cat_to.relationships:
                        other_mate_relationship = cat_to.relationships[cat_to.mate]
                        bigger_than_current = (bigger_than_current and
                                               current_relationship.romantic_love
                                               > other_mate_relationship.romantic_love)
                    else:
                        cat_to_mate.relationships[cat_to.ID] = Relationship(cat_to_mate, cat_to, True)
                        other_mate_relationship = cat_to.relationships[cat_to.mate]

                if ((love_over_30 and not normal_chance) or (bigger_than_current and not bigger_love_chance)):
                    self.had_one_event = True
                    # break up the old relationships
                    cat_from_mate = Cat.all_cats.get(cat_from.mate)
                    self.mate_events_class.handle_breakup(mate_relationship, mate_relationship.opposite_relationship, cat_from,
                                        cat_from_mate)

                    if cat_to_mate:
                        # relationship_from, relationship_to, cat_from, cat_to
                        self.mate_events_class.handle_breakup(other_mate_relationship, other_mate_relationship.opposite_relationship,
                                            cat_to, cat_to_mate)

                    # new relationship
                    text = f"{cat_from.name} and {cat_to.name} can't ignore their feelings for each other."
                    # game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_to.ID]))
                    self.mate_events_class.handle_new_mates(current_relationship, cat_from, cat_to)

            # breakup
            if not self.had_one_event and current_relationship.mates and not cat_from.dead and not cat_to.dead:
                if self.mate_events_class.check_if_breakup(current_relationship, current_relationship.opposite_relationship, cat_from,
                                         cat_to):
                    self.mate_events_class.handle_breakup(current_relationship, current_relationship.opposite_relationship, cat_from,
                                        cat_to)

    # ---------------------------------------------------------------------------- #
    #                                new event types                               #
    # ---------------------------------------------------------------------------- #

    def mate_events(self):
        """Description will follow."""
        """
        > events unique to mates
        """
        print("TODO")

    def same_age_events(self, cat):
        """Description will follow."""
        if not self.can_trigger_events(cat):
            return

        range = 15 + randint(0, 10)
        same_age_cats = get_cats_same_age(cat, range)
        if len(same_age_cats) > 0:
            random_cat = choice(same_age_cats)
            if self.can_trigger_events(random_cat) and random_cat.ID in cat.relationships:
                cat.relationships[random_cat.ID].start_interaction()
                self.trigger_event(cat)
                self.trigger_event(random_cat)

    def group_events(self, cat):
        """Description will follow."""
        if not self.can_trigger_events(cat):
            return

        chosen_type = "all"
        if len(GROUP_TYPES) > 0 and randint(0,game.config["relationship"]["chance_of_special_group"]):
            types_to_choose = []
            for group, value in GROUP_TYPES.items():
                types_to_choose.extend([group] * value["frequency"])
                chosen_type = choice(list(GROUP_TYPES.keys()))

        possible_interaction_cats = list(
            filter(
                lambda cat:
                (not cat.dead and not cat.outside and not cat.exiled),
                Cat.all_cats.values())
        )
        possible_interaction_cats.remove(cat)
        if chosen_type != "all":
            possible_interaction_cats = self.cats_with_relationship_constraints(cat, GROUP_TYPES[chosen_type]["constraint"])

        interacted_cat_ids = self.group_events_class.start_interaction(cat, possible_interaction_cats)
        for id in interacted_cat_ids:
            inter_cat = Cat.all_cats[id]
            self.trigger_event(inter_cat)

    def family_events(self):
        """Description will follow."""
        """
        - parent + child
        - siblings
        - grand parents/children
        """
        print("TODO")

    def outsider_events(self):
        """Description will follow."""
        print("TODO")

    def welcome_new_cats(self, new_cats = None):
        """This function will handle the welcome of new cats, if there are new cats in the clan."""
        if new_cats is None or len(new_cats) <= 0:
            return

        for new_cat in new_cats:
            same_age_cats = get_cats_same_age(new_cat)
            alive_cats = list(filter(lambda c: not c.dead and not c.outside and not c.exiled , list(new_cat.all_cats.values())))
            number = game.config["new_cat"]["cat_amount_welcoming"]

            if len(alive_cats) == 0:
                return
            elif len(same_age_cats) < number and len(same_age_cats) > 0:
                for age_cat in same_age_cats:
                    self.welcome_events_class.welcome_cat(age_cat, new_cat)
                
                rest_number = number - len(same_age_cats)
                chosen_rest = random.choices(population=alive_cats, k=len(alive_cats))
                if rest_number >= len(alive_cats):
                    chosen_rest = random.choices(population=alive_cats, k=rest_number)
                for inter_cat in chosen_rest:
                    self.welcome_events_class.welcome_cat(inter_cat, new_cat)
            elif len(same_age_cats) >= number:
                chosen = random.choices(population=alive_cats, k=number)
                for chosen_cat in chosen:
                    self.welcome_events_class.welcome_cat(chosen_cat, new_cat)
            elif len(alive_cats) <= number:
                for alive_cat in alive_cats:
                    self.welcome_events_class.welcome_cat(alive_cat, new_cat)

    # ---------------------------------------------------------------------------- #
    #                                helper function                               #
    # ---------------------------------------------------------------------------- #

    def cats_with_relationship_constraints(self, main_cat, constraint):
        """Returns a list of cats, where the relationship from main_cat towards the cat fulfill the given constraints."""
        cat_list = list(
            filter(
                lambda cat:
                (not cat.dead and not cat.outside and not cat.exiled),
                Cat.all_cats.values())
        )
        cat_list.remove(main_cat)
        filtered_cat_list = []
        
        for inter_cat in cat_list:
            cat_from = main_cat
            cat_to = inter_cat

            if inter_cat.ID == main_cat.ID:
                continue
            if cat_to.ID not in cat_from.relationships:
                print(f"ERROR: there is no relationship from {cat_from.name} to {cat_to.name}")
                continue

            relationship = cat_from.relationships[cat_to.ID]

            if "siblings" in constraint and not cat_from.is_sibling(cat_to):
                continue

            if "mates" in constraint and not relationship.mates:
                continue

            if "not_mates" in constraint and relationship.mates:
                continue

            if "parent/child" in constraint and not cat_from.is_parent(cat_to):
                continue

            if "child/parent" in constraint and not cat_to.is_parent(cat_from):
                continue

            value_types = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
            fulfilled = True
            for v_type in value_types:
                tags = list(filter(lambda constr: v_type in constr, constraint))
                if len(tags) < 1:
                    continue
                threshold = 0
                lower_than = False
                # try to extract the value/threshold from the text
                try:
                    splitted = tags[0].split('_')
                    threshold = int(splitted[1])
                    if len(splitted) > 3:
                        lower_than = True
                except:
                    print(f"ERROR: while creating a cat group, the relationship constraint for the value {v_type} follows not the formatting guidelines.")
                    break

                if threshold > 100:
                    print(f"ERROR: while creating a cat group, the relationship constraints for the value {v_type}, which is higher than the max value of a relationship.")
                    break

                if threshold <= 0:
                    print(f"ERROR: while creating a cat group, the relationship constraints for the value {v_type}, which is lower than the min value of a relationship or 0.")
                    break

                threshold_fulfilled = False
                if v_type == "romantic":
                    if not lower_than and relationship.romantic_love >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and relationship.romantic_love <= threshold:
                        threshold_fulfilled = True
                if v_type == "platonic":
                    if not lower_than and relationship.platonic_like >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and relationship.platonic_like <= threshold:
                        threshold_fulfilled = True
                if v_type == "dislike":
                    if not lower_than and relationship.dislike >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and relationship.dislike <= threshold:
                        threshold_fulfilled = True
                if v_type == "comfortable":
                    if not lower_than and relationship.comfortable >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and relationship.comfortable <= threshold:
                        threshold_fulfilled = True
                if v_type == "jealousy":
                    if not lower_than and relationship.jealousy >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and relationship.jealousy <= threshold:
                        threshold_fulfilled = True
                if v_type == "trust":
                    if not lower_than and relationship.trust >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and relationship.trust <= threshold:
                        threshold_fulfilled = True

                if not threshold_fulfilled:
                    fulfilled = False
                    continue

            if not fulfilled:
                continue

            filtered_cat_list.append(inter_cat)
        return filtered_cat_list

    def trigger_event(self, cat):
        if cat.ID in self.cats_triggered_events:
            self.cats_triggered_events[cat.ID] += 1
        else:
            self.cats_triggered_events[cat.ID] = 1

    def can_trigger_events(self, cat):
        """Returns if the given cat can still trigger events."""
        MAX_NORMAL = 4
        MAX_SPECIAL = 6
        special_status = ["leader", "deputy", "medicine cat", "mediator"]
        
        # set the threshold correctly
        threshold = MAX_NORMAL
        if cat.status in special_status:
            threshold = MAX_SPECIAL
        
        if cat.ID not in self.cats_triggered_events:
            return True

        return self.cats_triggered_events[cat.ID] < threshold
 
    def clear_trigger_dict(self):
        """Cleans the trigger dictionary, this function should be called every new moon."""
        self.cats_triggered_events = {}


# ---------------------------------------------------------------------------- #
#                                load resources                                #
# ---------------------------------------------------------------------------- #

base_path = os.path.join(
    "resources",
    "dicts",
    "relationship_events"
)

GROUP_TYPES = {}
types_path = os.path.join(base_path,"group_interactions" ,"group_types.json")
with open(types_path, 'r') as read_file:
    GROUP_TYPES = ujson.load(read_file)