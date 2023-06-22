import itertools
import random
from random import choice, randint
import os
import ujson

from scripts.game_structure.game_essentials import game
from scripts.events_module.condition_events import Condition_Events
from scripts.cat.cats import Cat
from scripts.utility import get_cats_same_age, get_cats_of_romantic_interest, get_free_possible_mates
from scripts.event_class import Single_Event
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.relationship.romantic_events import Romantic_Events
from scripts.events_module.relationship.welcoming_events import Welcoming_Events
from scripts.events_module.relationship.group_events import Group_Events

class Relation_Events():
    """All relationship events."""
    def __init__(self) -> None:
        self.had_one_event = False
        self.condition_events = Condition_Events()
        self.romantic_events_class = Romantic_Events()
        self.welcome_events_class = Welcoming_Events()
        self.group_events_class = Group_Events()
        self.cats_triggered_events = {}
        pass

    def handle_relationships(self, cat: Cat):
        """Checks the relationships of the cat and trigger additional events if possible.

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

        self.same_age_events(cat)

        # 1/16 for an additional event
        if not random.getrandbits(4):
            self.romantic_events(cat)

        for mate_id in cat.mate:
            if mate_id not in Cat.all_cats:
                print(f"WARNING: Cat #{cat} has a invalid mate. It will be removed.")
                cat.mate.remove(mate_id)
                continue

            cat_mate = Cat.fetch_cat(mate_id)
            # Move on from dead mates
            if cat_mate and "grief stricken" not in cat.illnesses and ((cat_mate.dead and cat_mate.dead_for >= 4) or cat_mate.outside):
                # randint is a slow function, don't call it unless we have to.
                if random.random() > 0.5: 
                    text = f'{cat.name} will always love {cat_mate.name} but has decided to move on.'
                    game.cur_events_list.append(Single_Event(text, "relation", [cat.ID, cat_mate.ID]))
                    cat.unset_mate(cat_mate)

        cats_amount = len(Cat.all_cats)
        # cap the maximal checks
        range_number = int(cats_amount / 1.8)  # int(1.9) rounds to 1
        
        if range_number > 60:
            range_number = 60

        used_relationships = []
        # for i in range(0, range_number):
        for _ in itertools.repeat(None, range_number):
            random_index = int(random.random() * len(cat.relationships))
            if random_index in used_relationships:
                continue
            current_relationship = list(cat.relationships.values())[random_index]
            used_relationships.append(random_index)

            if not current_relationship.opposite_relationship:
                current_relationship.link_relationship()

            self.handle_mating(current_relationship)
    # ---------------------------------------------------------------------------- #
    #                                new event types                               #
    # ---------------------------------------------------------------------------- #

    def handle_mating(self, current_relationship):
        """Handle mating for the selected relationship."""
        cat = current_relationship.cat_from
        cat_to = current_relationship.cat_to

        if not self.can_trigger_events(cat):
            return

        # fix the settings if the current cats are mates
        if (cat.ID in cat_to.mate or cat_to.ID in cat.mate) and\
            not current_relationship.mates:
            current_relationship.mates = True


        # TODO: find a solution
        cat_mate = None if len(cat.mate) < 1 else Cat.fetch_cat(cat.mate[0])
        
        # TODO: find a solution 
        cat_to_mate = None

        # Remove deleted mates if ther are some
        if len(cat_to.mate) > 0:
            for mate_id in cat.mate:
                if mate_id not in Cat.all_cats:
                    print(f"WARNING: Cat #{cat_to} has a invalid mate. It will be removed.")
                    cat_to.mate.remove(mate_id)
                    return
            cat_to_mate = Cat.all_cats.get(cat_to.mate[0])

        potential_mates = cat.is_potential_mate(cat_to) and cat_to.is_potential_mate(cat)
        both_alive = not cat.dead and not cat_to.dead

        # breakup and new mate
        if not self.had_one_event and len(cat_to.mate) > 0 and potential_mates and not current_relationship.mates:
            love_over_30 = current_relationship.romantic_love > 30 and\
                current_relationship.opposite_relationship.romantic_love > 30

            normal_chance = int(random.random() * 10)

            # compare love value of current mates
            bigger_than_current = False
            bigger_love_chance = int(random.random() * 3)

            mate_relationship = None
            if cat_mate and cat_mate.ID in cat.relationships:
                mate_relationship = cat.relationships[cat_mate.ID]
                bigger_than_current = current_relationship.romantic_love > mate_relationship.romantic_love

            # check cat_to values
            if cat_to_mate:
                if cat.ID in cat_to.relationships:
                    other_mate_relationship = cat_to.relationships[cat_to_mate.ID]
                    bigger_than_current = (bigger_than_current and
                                           current_relationship.romantic_love
                                           > other_mate_relationship.romantic_love)
                else:
                    cat_to_mate.create_one_relationship(cat_to)
                    cat_to_mate.relationships[cat_to.ID].mate = True
                    other_mate_relationship = cat_to.relationships[cat_to_mate.ID]

            if ((love_over_30 and not normal_chance) or (bigger_than_current and not bigger_love_chance)):
                self.had_one_event = True
                # break up the old mate relationships
                if cat_mate:
                    cat_mate = Cat.all_cats.get(cat_mate.ID)
                    if cat_mate:
                        self.romantic_events_class.handle_breakup(
                            mate_relationship, 
                            mate_relationship.opposite_relationship, 
                            cat, 
                            cat_mate
                        )
                        cat.unset_mate(cat_mate, breakup=True, fight=False)
                        text = f"{cat.name} and {cat_mate.name} broke up."
                        game.cur_events_list.append(Single_Event(text, ["relation", "misc"], [cat.ID, cat_mate.ID]))

                if cat_to_mate:
                    self.romantic_events_class.handle_breakup(
                        other_mate_relationship, 
                        other_mate_relationship.opposite_relationship,
                        cat_to, 
                        cat_to_mate
                    )
                    cat_to.unset_mate(cat_to_mate, breakup=True, fight=False)
                    text = f"{cat_to.name} and {cat_to_mate.name} broke up."
                    game.cur_events_list.append(Single_Event(text, ["relation", "misc"], [cat_to.ID, cat_to_mate.ID]))

                # new mate relationship
                text = f"{cat.name} and {cat_to.name} can't ignore their feelings for each other."
                game.cur_events_list.append(Single_Event(text, ["relation", "misc"], [cat.ID, cat_to.ID]))
                cat.set_mate(cat_to)
                cat_to.set_mate(cat)

        # breakup
        if not self.had_one_event and current_relationship.mates and both_alive:
            breakup = self.romantic_events_class.check_if_breakup(
                current_relationship,
                current_relationship.opposite_relationship,
                cat,
                cat_to)
            if breakup:
                self.romantic_events_class.handle_breakup(
                    current_relationship,
                    current_relationship.opposite_relationship,
                    cat,
                    cat_to
                )
                self.had_one_event = True

        # new mates
        if not self.had_one_event:
            if cat_to.is_potential_mate(cat) and cat.ID not in cat.mate:
                self.romantic_events_class.handle_new_mates(current_relationship, cat, cat_to)
            self.had_one_event = True
        
        if self.had_one_event:
            self.trigger_event(cat)
            self.trigger_event(cat_to)

        # confession 
        if random.random() > 0.85 and potential_mates and not current_relationship.mates:
            if self.romantic_events_class.handle_confession(cat):
                self.had_one_event = True

    def romantic_events(self, cat):
        """
            ONLY for cat OLDER than 12 moons.
            To increase mating chance this function is used.
            It will boost the romantic values of either mate or possible mates.
            This also increase the chance of affairs.
        """
        if cat.moons < 12:
            return

        if not self.can_trigger_events(cat):
            return

        other_cat = None

        # get the cats which are relevant for romantic interactions
        free_possible_mates = get_free_possible_mates(cat, Relationship)
        other_love_interest = get_cats_of_romantic_interest(cat, Relationship)  
        possible_cats = free_possible_mates
        if len(other_love_interest) > 0 and len(other_love_interest) < 3:
            possible_cats.extend(other_love_interest)
            possible_cats.extend(other_love_interest)
        elif len(other_love_interest) >= 3:
            possible_cats = other_love_interest

        # only adding cats which already have SOME relationship with each other
        cat_to_choose_from = []
        for inter_cat in possible_cats:
            if inter_cat.ID not in cat.relationships:
                cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)

            cat_to_inter = cat.relationships[inter_cat.ID].platonic_like > 10 or\
                cat.relationships[inter_cat.ID].comfortable > 10
            inter_to_cat = inter_cat.relationships[cat.ID].platonic_like > 10 or\
                inter_cat.relationships[cat.ID].comfortable > 10
            if cat_to_inter and inter_to_cat:
                cat_to_choose_from.append(inter_cat)

        # if the cat has one or more mates, check how high the chance is, 
        # that the cat interacts romantic with ANOTHER cat than their mate
        if len(cat.mate) > 0:
            chance_number = game.config["relationship"]["chance_romantic_not_mate"]
             
            # the more mates the cat has, the less likely it will be that they interact with another cat romantically
            for mate_id in cat.mate:
                chance_number += int(cat.relationships[mate_id].romantic_love / 10)
            use_mate = int(random.random() * chance_number)  
            
            # only if it is 0 then all the other cats should be used
            # otherwise only the mates are chosen for romantic interactions
            if use_mate:
                cat_to_choose_from = [cat.all_cats[mate_id] for mate_id in cat.mate if\
                                      not cat.all_cats[mate_id].dead and not cat.all_cats[mate_id].outside]

        if len(cat_to_choose_from) < 1:
            return
            
        other_cat = choice(cat_to_choose_from)
        if self.romantic_events_class.start_interaction(cat, other_cat):
            self.trigger_event(cat)
            self.trigger_event(other_cat)

    def same_age_events(self, cat):
        """	
            To increase the relationship amounts with cats of the same age. 
            This should lead to 'friends', 'enemies' and possible mates around the same age group.
        """
        if not self.can_trigger_events(cat):
            return

        same_age_cats = get_cats_same_age(cat, Relationship, game.config["mates"]["age_range"])
        if len(same_age_cats) > 0:
            random_cat = choice(same_age_cats)
            if self.can_trigger_events(random_cat) and random_cat.ID in cat.relationships:
                cat.relationships[random_cat.ID].start_interaction()
                self.trigger_event(cat)
                self.trigger_event(random_cat)

    def group_events(self, cat):
        """
            This function triggers group events, based on the given cat. 
            First it will be decided if a special type of group (found in relationship_events/group_interactions/group_types.json).
            As default all cats will be a possible 'group' of interaction.
        """
        if not self.can_trigger_events(cat):
            return

        chosen_type = "all"
        if len(GROUP_TYPES) > 0 and randint(0,game.config["relationship"]["chance_of_special_group"]):
            types_to_choose = []
            for group, value in GROUP_TYPES.items():
                types_to_choose.extend([group] * value["frequency"])
                chosen_type = choice(list(GROUP_TYPES.keys()))

        if cat.status == "leader":
            chosen_type = "all"
        possible_interaction_cats = list(
            filter(
                lambda cat:
                (not cat.dead and not cat.outside and not cat.exiled),
                Cat.all_cats.values())
        )
        if cat in possible_interaction_cats:
            possible_interaction_cats.remove(cat)

        if chosen_type != "all":
            possible_interaction_cats = self.cats_with_relationship_constraints(cat, GROUP_TYPES[chosen_type]["constraint"])

        interacted_cat_ids = self.group_events_class.start_interaction(cat, possible_interaction_cats)
        for id in interacted_cat_ids:
            inter_cat = Cat.all_cats[id]
            self.trigger_event(inter_cat)

    def family_events(self, cat):
        """
            To have more family related events.
        """
        print("TODO")

    def outsider_events(self, cat):
        """
            ONLY for cat OLDER than 6 moons and not major injured.
            This function will handle when the cat interacts with cat which are outside of the clan.
        """
        print("TODO")

    def welcome_new_cats(self, new_cats = None):
        """This function will handle the welcome of new cats, if there are new cats in the clan."""
        if new_cats is None or len(new_cats) <= 0:
            return

        for new_cat in new_cats:
            same_age_cats = get_cats_same_age(new_cat, Relationship)
            alive_cats = [i for i in new_cat.all_cats.values() if not i.dead and not i.outside]
            number = game.config["new_cat"]["cat_amount_welcoming"]

            if len(alive_cats) == 0:
                return
            elif len(same_age_cats) < number and len(same_age_cats) > 0:
                for age_cat in same_age_cats:
                    self.welcome_events_class.welcome_cat(age_cat, new_cat)
                
                rest_number = number - len(same_age_cats)
                same_age_ids = [c.ID for c in same_age_cats]
                alive_cats = [alive_cat for alive_cat in alive_cats if alive_cat.ID not in same_age_ids]
                
                chosen_rest = random.choices(population=alive_cats, k=len(alive_cats))
                if rest_number >= len(alive_cats):
                    chosen_rest = random.choices(population=alive_cats, k=rest_number)
                for inter_cat in chosen_rest:
                    self.welcome_events_class.welcome_cat(inter_cat, new_cat)
            elif len(same_age_cats) >= number:
                chosen = random.choices(population=same_age_cats, k=number)
                for chosen_cat in chosen:
                    self.welcome_events_class.welcome_cat(chosen_cat, new_cat)
            elif len(alive_cats) <= number:
                for alive_cat in alive_cats:
                    self.welcome_events_class.welcome_cat(alive_cat, new_cat)
            else:
                chosen = random.choices(population=alive_cats, k=number)
                for chosen_cat in chosen:
                    self.welcome_events_class.welcome_cat(chosen_cat, new_cat)

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
                cat_from.create_one_relationship(cat_to)
                if cat_from.ID not in cat_to.relationships:
                    cat_to.create_one_relationship(cat_from)
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
                tags = [i for i in constraint if v_type in i]
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
        special_status = ["leader", "deputy", "medicine cat", "mediator"]
        
        # set the threshold correctly
        threshold = game.config["relationship"]["max_interaction"]
        if cat.status in special_status:
            threshold = game.config["relationship"]["max_interaction_special"]
        
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