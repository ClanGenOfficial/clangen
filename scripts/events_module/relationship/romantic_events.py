
from copy import deepcopy
from random import choice
import random

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.utility import (
    get_highest_romantic_relation, 
    event_text_adjust, 
    get_personality_compatibility,

)
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event
from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import (
    INTERACTION_MASTER_DICT,
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints,
)


class Romantic_Events():
    """All events which are related to mate's such as becoming mates and breakups, but also for possible mates and romantic interactions."""
    
    def __init__(self) -> None:
        self.had_one_event = False
        pass

    def start_interaction(self, cat_from, cat_to):
        """
            Filters and triggers events which are connected to romance between these two cats.
            
            Returns
            -------
            bool : if an event is triggered or not
        """
        if cat_from.ID == cat_to.ID:
            return False

        relevant_dict = deepcopy(ROMANTIC_INTERACTIONS)
        if cat_from.mate == cat_to.ID:
            relevant_dict = deepcopy(MATE_INTERACTIONS)

        # check if it should be a positive or negative interaction
        relationship = cat_from.relationships[cat_to.ID]
        positive = self.check_if_positive_interaction(relationship)

        # get the possible interaction list and filter them
        possible_interactions = relevant_dict["positive"] if positive else relevant_dict["negative"]
        filtered_interactions = []
        _season = [str(game.clan.current_season).casefold(), "Any", "any"]
        _biome = [str(game.clan.biome).casefold(), "Any", "any"]
        for interaction in possible_interactions:
            in_tags = [i for i in interaction.biome if i not in _biome]
            if len(in_tags) > 0:
                continue

            in_tags = [i for i in interaction.season if i not in _season]
            if len(in_tags) > 0:
                continue

            rel_fulfilled = rel_fulfill_rel_constraints(relationship, interaction.relationship_constraint, interaction.id)
            if not rel_fulfilled:
                continue

            cat_fulfill = cats_fulfill_single_interaction_constraints(cat_from, cat_to, interaction, game.clan.game_mode)
            if not cat_fulfill:
                continue

            filtered_interactions.append(interaction)
        
        if len(filtered_interactions) < 1:
            print(f"There were no romantic interactions for: {cat_from.name} to {cat_to.name}")
            return False
        
        # chose interaction
        chosen_interaction = choice(filtered_interactions)
        # check if the current interaction id is already used and us another if so
        chosen_interaction = choice(possible_interactions)
        while chosen_interaction.id in relationship.used_interaction_ids\
            and len(possible_interactions) > 2:
            possible_interactions.remove(chosen_interaction)
            chosen_interaction = choice(possible_interactions)

        # if the chosen_interaction is still in the TRIGGERED_SINGLE_INTERACTIONS, clean the list
        if chosen_interaction in relationship.used_interaction_ids:
            relationship.used_interaction_ids = []
        relationship.used_interaction_ids.append(chosen_interaction.id)

        # affect relationship - it should always be in a romantic way
        in_de_crease = "increase" if positive else "decrease"
        rel_type = "romantic"
        relationship.chosen_interaction = chosen_interaction
        relationship.interaction_affect_relationships(in_de_crease, interaction.intensity, rel_type)

        # give cats injuries if the game mode is not classic
        if len(chosen_interaction.get_injuries) > 0 and game.clan.game_mode != 'classic':
            for abbreviations, injury_dict in chosen_interaction.get_injuries.items():
                if "injury_names" not in injury_dict:
                    print(f"ERROR: there are no injury names in the chosen interaction {chosen_interaction.id}.")
                    continue

                injured_cat = cat_from
                if abbreviations != "m_c":
                    injured_cat = cat_to
                
                for inj in injury_dict["injury_names"]:
                    injured_cat.get_injured(inj, True)

                injured_cat.possible_scar = injury_dict["scar_text"] if "scar_text" in injury_dict else None
                injured_cat.possible_death = injury_dict["death_text"] if "death_text" in injury_dict else None
                if injured_cat.status == "leader":
                    injured_cat.possible_death = injury_dict["death_leader_text"] if "death_leader_text" in injury_dict else None

        # get any possible interaction string out of this interaction
        interaction_str = choice(chosen_interaction.interactions)

        # prepare string for display
        interaction_str = interaction_str.replace("m_c", str(cat_from.name))
        interaction_str = interaction_str.replace("r_c", str(cat_to.name))

        # display the interaction in the moon events
        effect = " (positive effect)" if positive else " (negative effect)"
        interaction_str = interaction_str + effect

        relationship.log.append(interaction_str)
        if not relationship.opposite_relationship and cat_from.ID != cat_to.ID:
            relationship.link_relationship()
            relationship.opposite_relationship.log.append(interaction_str)

        relevant_event_tabs = ["relation", "interaction"]
        if len(chosen_interaction.get_injuries) > 0:
            relevant_event_tabs.append("health")
        game.cur_events_list.append(Single_Event(
            interaction_str, relevant_event_tabs, [cat_to.ID, cat_from.ID]
        ))
        #print(f"ROMANTIC! {cat_from.name} to {cat_to.name}")
        return True

    def handle_new_mates(self, relationship, cat_from, cat_to):
        """More in depth check if the cats will become mates."""
        relationship_to = relationship.opposite_relationship
        become_mates, mate_string = self.check_if_new_mate(relationship, relationship_to, cat_from, cat_to)

        if become_mates and mate_string:
            self.had_one_event = True
            cat_from.set_mate(cat_to)
            game.cur_events_list.append(Single_Event(mate_string, ["relation", "misc"], [cat_from.ID, cat_to.ID]))

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
                text = f"{cat_from.name} and {cat_to.name} broke up."
                # game.relation_events_list.insert(0, text)
                game.cur_events_list.append(Single_Event(text, ["relation", "misc"], [cat_from.ID, cat_to.ID]))

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

    def check_if_positive_interaction(self, relationship) -> bool:
        """Returns if the interaction should be a positive interaction or not."""
        # base for non-existing platonic like / dislike
        list_to_choice = [True, False]

        # take personality in count
        comp = get_personality_compatibility(relationship.cat_from, relationship.cat_to)
        if comp is not None:
            list_to_choice.append(comp)

        # further influence the partition based on the relationship
        list_to_choice += [True] * int(relationship.platonic_like/15)
        list_to_choice += [True] * int(relationship.romantic_love/15)
        list_to_choice += [False] * int(relationship.dislike/10)

        return choice(list_to_choice)

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

# ---------------------------------------------------------------------------- #
#            build up dictionaries which can be used for moon events           #
#         because there may be less romantic/mate relevant interactions,       #
#        the dictionary will be ordered in only 'positive' and 'negative'      #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                                     MATE                                     #
# ---------------------------------------------------------------------------- #

# Use the overall master interaction dictionary and filter for mate tag
MATE_RELEVANT_INTERACTIONS = {}
for val_type, dictionary in INTERACTION_MASTER_DICT.items():
    MATE_RELEVANT_INTERACTIONS[val_type] = {}
    MATE_RELEVANT_INTERACTIONS[val_type]["increase"] = list(
        filter(lambda inter: "mates" in inter.relationship_constraint and "not_mates" not in inter.relationship_constraint,
            dictionary["increase"]
        )
    )
    MATE_RELEVANT_INTERACTIONS[val_type]["decrease"] = list(
        filter(lambda inter: "mates" in inter.relationship_constraint and "not_mates" not in inter.relationship_constraint,
            dictionary["decrease"]
        )
    )

# resort the first generated overview dictionary to only "positive" and "negative" interactions
MATE_INTERACTIONS = {
    "positive": [],
    "negative": []
}
for val_type, dictionary in MATE_RELEVANT_INTERACTIONS.items():
    if val_type in ["jealousy", "dislike"]:
        MATE_INTERACTIONS["positive"] += dictionary["decrease"]
        MATE_INTERACTIONS["negative"] += dictionary["increase"]
    else:
        MATE_INTERACTIONS["positive"] += dictionary["increase"]
        MATE_INTERACTIONS["negative"] += dictionary["decrease"]

# ---------------------------------------------------------------------------- #
#                                   ROMANTIC                                   #
# ---------------------------------------------------------------------------- #

# Use the overall master interaction dictionary and filter for any interactions, which requires a certain amount of romantic
ROMANTIC_RELEVANT_INTERACTIONS = {}
for val_type, dictionary in INTERACTION_MASTER_DICT.items():
    ROMANTIC_RELEVANT_INTERACTIONS[val_type] = {}

    # if it's the romantic interaction type add all interactions
    if val_type == "romantic":
        ROMANTIC_RELEVANT_INTERACTIONS[val_type]["increase"] = dictionary["increase"]
        ROMANTIC_RELEVANT_INTERACTIONS[val_type]["decrease"] = dictionary["decrease"]
    else:
        increase = []
        for interaction in dictionary["increase"]:
            romantic = ["romantic" in tag for tag in interaction.relationship_constraint]
            if any(romantic):
                increase.append(interaction)
        ROMANTIC_RELEVANT_INTERACTIONS[val_type]["increase"] = increase

        decrease = []
        for interaction in dictionary["decrease"]:
            romantic = ["romantic" in tag for tag in interaction.relationship_constraint]
            if any(romantic):
                decrease.append(interaction)
        ROMANTIC_RELEVANT_INTERACTIONS[val_type]["decrease"] = decrease

# resort the first generated overview dictionary to only "positive" and "negative" interactions
ROMANTIC_INTERACTIONS = {
    "positive": [],
    "negative": []
}
for val_type, dictionary in ROMANTIC_RELEVANT_INTERACTIONS.items():
    if val_type in ["jealousy", "dislike"]:
        ROMANTIC_INTERACTIONS["positive"].extend(dictionary["decrease"])
        ROMANTIC_INTERACTIONS["negative"].extend(dictionary["increase"])
    else:
        ROMANTIC_INTERACTIONS["positive"].extend(dictionary["increase"])
        ROMANTIC_INTERACTIONS["negative"].extend(dictionary["decrease"])