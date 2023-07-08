
from copy import deepcopy
from random import choice
import random

import ujson

from scripts.cat.history import History
from scripts.utility import (
    get_highest_romantic_relation,
    event_text_adjust,
    get_personality_compatibility,
    process_text

)
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event
from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import (
    INTERACTION_MASTER_DICT,
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints
)


class Romantic_Events():
    """All events which are related to mate's such as becoming mates and breakups, but also for possible mates and romantic interactions."""

    def __init__(self) -> None:
        self.history = History()
        self.had_one_event = False

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
        if cat_to.ID in cat_from.mate and not cat_to.dead:
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
                
                injuries = []
                for inj in injury_dict["injury_names"]:
                    injured_cat.get_injured(inj, True)
                    injuries.append(inj)

                possible_scar = injury_dict["scar_text"] if "scar_text" in injury_dict else None
                possible_death = injury_dict["death_text"] if "death_text" in injury_dict else None
                if injured_cat.status == "leader":
                    possible_death = injury_dict["death_leader_text"] if "death_leader_text" in injury_dict else None
                
                if possible_scar or possible_death:
                    for condition in injuries:
                        self.history.add_possible_history(injured_cat, condition, death_text=possible_death, scar_text=possible_scar)

        # get any possible interaction string out of this interaction
        interaction_str = choice(chosen_interaction.interactions)

        # prepare string for display
        cat_dict = {
            "m_c": (str(cat_from.name), choice(cat_from.pronouns)),
            "r_c": (str(cat_to.name), choice(cat_to.pronouns))
        }
        interaction_str = process_text(interaction_str, cat_dict)
        
        # extract intensity from the interaction
        intensity = getattr(chosen_interaction, 'intensity', 'neutral')

        effect = " (neutral effect)"
        if in_de_crease != "neutral" and positive:
            effect = f" ({intensity} positive effect)"
        if in_de_crease != "neutral" and not positive:
            effect = f" ({intensity} negative effect)"

        interaction_str = interaction_str + effect

        # send string to current moon relationship events before adding age of cats
        relevant_event_tabs = ["relation", "interaction"]
        if len(chosen_interaction.get_injuries) > 0:
            relevant_event_tabs.append("health")
        game.cur_events_list.append(Single_Event(
            interaction_str, relevant_event_tabs, [cat_to.ID, cat_from.ID]
        ))

        # now add the age of the cats before the string is sent to the cats' relationship logs
        relationship.log.append(interaction_str + f" - {cat_from.name} was {cat_from.moons} moon(s) old")

        if not relationship.opposite_relationship and cat_from.ID != cat_to.ID:
            relationship.link_relationship()
            relationship.opposite_relationship.log.append(interaction_str)

        #print(f"ROMANTIC! {cat_from.name} to {cat_to.name}")
        return True

    def handle_new_mates(self, relationship, cat_from, cat_to):
        """More in depth check if the cats will become mates."""
        if cat_from.ID in cat_to.mate:
            if cat_to.ID not in cat_from.mate:
                cat_to.set_mate(cat_from)
            return
        relationship_to = relationship.opposite_relationship
        become_mates, mate_string = self.check_if_new_mate(relationship, relationship_to, cat_from, cat_to)

        if become_mates and mate_string:
            self.had_one_event = True
            cat_from.set_mate(cat_to)
            game.cur_events_list.append(Single_Event(mate_string, ["relation", "misc"], [cat_from.ID, cat_to.ID]))

    def handle_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        ''' Handles cats breaking up their relationship '''
        from_mate_in_clan = False
        if cat_to.ID in cat_from.mate:
            from_mate_in_clan = cat_to.is_alive() and not cat_to.outside
        else:
            return

        if not self.had_one_event and relationship_from.mates and from_mate_in_clan:
            if self.check_if_breakup(relationship_from, relationship_to, cat_from, cat_to):
                # TODO: filter log to check if last interaction was a fight
                had_fight = False
                self.had_one_event = True
                cat_from.unset_mate(cat_to, breakup=True, fight=had_fight)
                text = f"{cat_from.name} and {cat_to.name} broke up."
                game.cur_events_list.append(Single_Event(text, ["relation", "misc"], [cat_from.ID, cat_to.ID]))

    def handle_confession(self, cat_from):
        """
        Check if the cat has a high love for another and mate them if there are in the boundaries 
        :param cat: cat in question

        return: bool if event is triggered or not
        """
        # get the highest romantic love relationships and
        rel_list = cat_from.relationships.values()
        highest_romantic_relation = get_highest_romantic_relation(rel_list, exclude_mate=True)
        if not highest_romantic_relation:
            return False

        condition = game.config["mates"]["confession"]["make_confession"]
        if not self.relationship_fulfill_condition(highest_romantic_relation, condition):
            return False

        cat_to = highest_romantic_relation.cat_to
        if not cat_to.is_potential_mate(cat_from) or not cat_from.is_potential_mate(cat_to):
            return False

        alive_inclan_from_mates = [mate for mate in cat_from.mate if not cat_from.fetch_cat(mate).dead and not cat_from.fetch_cat(mate).outside]
        alive_inclan_to_mates = [mate for mate in cat_to.mate if not cat_to.fetch_cat(mate).dead and not cat_to.fetch_cat(mate).outside]
        poly = len(alive_inclan_from_mates) > 0 or len(alive_inclan_to_mates) > 0

        if poly and not self.current_mates_allow_new_mate(cat_from, cat_to):
            return False

        become_mate = False
        condition = game.config["mates"]["confession"]["accept_confession"]
        rel_to_check = highest_romantic_relation.opposite_relationship
        if not rel_to_check:
            highest_romantic_relation.link_relationship()
            rel_to_check = highest_romantic_relation.opposite_relationship
        if self.relationship_fulfill_condition(rel_to_check, condition):
            become_mate = True
            mate_string = self.get_mate_string("high_romantic", poly, cat_from, cat_to)
        # second acceptance chance if the romantic is high enough
        elif "romantic" in condition and condition["romantic"] != 0 and\
            condition["romantic"] > 0 and rel_to_check.romantic_love >= condition["romantic"] * 1.5:
            become_mate = True
            mate_string = self.get_mate_string("high_romantic", poly, cat_from, cat_to)
        else:
            mate_string = self.get_mate_string("rejected", poly, cat_from, cat_to)
            cat_from.relationships[cat_to.ID].romantic_love -= 8
            cat_to.relationships[cat_from.ID].comfortable -= 8

        mate_string = self.prepare_relationship_string(mate_string, cat_from, cat_to)
        game.cur_events_list.append(Single_Event(mate_string, ["relation", "misc"], [cat_from.ID, cat_to.ID]))

        if become_mate:
            cat_from.set_mate(cat_to)

        return True

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
        if not relationship_from or not relationship_to or not cat_from or cat_to:
            return False
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
        young_age = ['newborn', 'kitten', 'adolescent']
        if cat_from.age in young_age or cat_to.age in young_age:
            return  False, None

        mate_string = None
        mate_chance = game.config["mates"]["chance_fulfilled_condition"]
        hit = int(random.random() * mate_chance)

        # has to be high because every moon this will be checked for each relationship in the game
        friends_to_lovers = game.config["mates"]["chance_friends_to_lovers"]
        random_hit = int(random.random() * friends_to_lovers)

        # already return if there is 'no' hit (everything above 0), other checks are not necessary
        if hit > 0 and random_hit > 0:
            return False, None

        alive_inclan_from_mates = [mate for mate in cat_from.mate if not cat_from.fetch_cat(mate).dead and not cat_from.fetch_cat(mate).outside]
        alive_inclan_to_mates = [mate for mate in cat_to.mate if not cat_to.fetch_cat(mate).dead and not cat_to.fetch_cat(mate).outside]
        poly = len(alive_inclan_from_mates) > 0 or len(alive_inclan_to_mates) > 0

        if poly and not self.current_mates_allow_new_mate(cat_from, cat_to):
            return False, None

        if not hit and self.relationship_fulfill_condition(relationship_from, game.config["mates"]["mate_condition"]) and\
            self.relationship_fulfill_condition(relationship_to, game.config["mates"]["mate_condition"]):
            become_mates = True
            mate_string = self.get_mate_string("low_romantic", poly, cat_from, cat_to)
        if not random_hit and self.relationship_fulfill_condition(relationship_from, game.config["mates"]["platonic_to_romantic"]) and\
            self.relationship_fulfill_condition(relationship_to, game.config["mates"]["platonic_to_romantic"]):
            become_mates = True
            mate_string = self.get_mate_string("platonic_to_romantic", poly, cat_from, cat_to)

        if not become_mates:
            return False, None

        if poly:
            print("----- POLY-POLY-POLY", cat_from.name, cat_to.name)
            print(cat_from.mate)
            print(cat_to.mate)

        mate_string = self.prepare_relationship_string(mate_string, cat_from, cat_to)

        return become_mates, mate_string

    def relationship_fulfill_condition(self, relationship, condition):
        """
        Check if the relationship can fulfill the condition. 
        Example condition:
            {
            "romantic": 20,
            "platonic": 30,
            "dislike": -10,
            "admiration": 0,
            "comfortable": 20,
            "jealousy": 0,
            "trust": 0
            }

        VALUES: 
            - 0: no condition
            - positive number: value has to be higher than number
            - negative number: value has to be lower than number
        
        """
        if not relationship:
            return False
        if "romantic" in condition and condition["romantic"] != 0:
            if condition["romantic"] > 0 and relationship.romantic_love < condition["romantic"]:
                return False
            if condition["romantic"] < 0 and relationship.romantic_love > abs(condition["romantic"]):
                return False
        if "platonic" in condition and condition["platonic"] != 0:
            if condition["platonic"] > 0 and relationship.platonic_like < condition["platonic"]:
                return False
            if condition["platonic"] < 0 and relationship.platonic_like > abs(condition["platonic"]):
                return False
        if "dislike" in condition and condition["dislike"] != 0:
            if condition["dislike"] > 0 and relationship.dislike < condition["dislike"]:
                return False
            if condition["dislike"] < 0 and relationship.dislike > abs(condition["dislike"]):
                return False
        if "admiration" in condition and condition["admiration"] != 0:
            if condition["admiration"] > 0 and relationship.admiration < condition["admiration"]:
                return False
            if condition["admiration"] < 0 and relationship.admiration > abs(condition["admiration"]):
                return False
        if "comfortable" in condition and condition["comfortable"] != 0:
            if condition["comfortable"] > 0 and relationship.comfortable < condition["comfortable"]:
                return False
            if condition["comfortable"] < 0 and relationship.comfortable > abs(condition["comfortable"]):
                return False
        if "jealousy" in condition and condition["jealousy"] != 0:
            if condition["jealousy"] > 0 and relationship.jealousy < condition["jealousy"]:
                return False
            if condition["jealousy"] < 0 and relationship.jealousy > abs(condition["jealousy"]):
                return False
        if "trust" in condition and condition["trust"] != 0:
            if condition["trust"] > 0 and relationship.trust < condition["trust"]:
                return False
            if condition["trust"] < 0 and relationship.trust > abs(condition["trust"]):
                return False
        return True

    def current_mates_allow_new_mate(self, cat_from, cat_to) -> bool:
        """Check if all current mates are fulfill the given conditions."""
        current_mate_condition = game.config["mates"]["poly"]["current_mate_condition"]
        current_to_new_condition = game.config["mates"]["poly"]["mates_to_each_other"]

        # check relationship from current mates from cat_from
        all_mates_fulfill_current_mate_condition = True
        all_mates_fulfill_current_to_new = True
        alive_inclan_from_mates = [mate for mate in cat_from.mate if not cat_from.fetch_cat(mate).dead and not cat_from.fetch_cat(mate).outside]
        if len(alive_inclan_from_mates) > 0:
            for mate_id in alive_inclan_from_mates:
                mate_cat = cat_from.fetch_cat(mate_id)
                if mate_cat.dead:
                    continue
                if mate_id in cat_from.relationships and cat_from.ID in mate_cat.relationships:
                    if not self.relationship_fulfill_condition(cat_from.relationships[mate_id], current_mate_condition) or\
                        not self.relationship_fulfill_condition(mate_cat.relationships[cat_from.ID], current_mate_condition):
                        all_mates_fulfill_current_mate_condition = False
                
                if mate_id in cat_to.relationships and cat_to.ID in mate_cat.relationships:
                    if not self.relationship_fulfill_condition(cat_to.relationships[mate_id], current_to_new_condition) or\
                        not self.relationship_fulfill_condition(mate_cat.relationships[cat_to.ID], current_to_new_condition):
                        all_mates_fulfill_current_to_new = False
        if not all_mates_fulfill_current_mate_condition or\
            not all_mates_fulfill_current_to_new:
            return False

        # check relationship from current mates from cat_to
        all_mates_fulfill_current_mate_condition = True
        all_mates_fulfill_current_to_new = True
        alive_inclan_to_mates = [mate for mate in cat_to.mate if not cat_to.fetch_cat(mate).dead and not cat_to.fetch_cat(mate).outside]
        if len(alive_inclan_to_mates) > 0:
            for mate_id in alive_inclan_to_mates:
                mate_cat = cat_to.fetch_cat(mate_id)
                if mate_cat.dead:
                    continue
                if mate_id in cat_to.relationships and cat_to.ID in mate_cat.relationships:
                    if not self.relationship_fulfill_condition(cat_to.relationships[mate_id], current_mate_condition) or\
                        not self.relationship_fulfill_condition(mate_cat.relationships[cat_to.ID], current_mate_condition):
                        all_mates_fulfill_current_mate_condition = False

                if mate_id in cat_from.relationships and cat_from.ID in mate_cat.relationships:
                    if not self.relationship_fulfill_condition(cat_from.relationships[mate_id], current_to_new_condition) or\
                        not self.relationship_fulfill_condition(mate_cat.relationships[cat_from.ID], current_to_new_condition):
                        all_mates_fulfill_current_to_new = False
        if not all_mates_fulfill_current_mate_condition or\
            not all_mates_fulfill_current_to_new:
            return False

        return True

    def prepare_relationship_string(self, mate_string, cat_from, cat_to):
        """Prepares the relationship event string for display"""
        # replace mates with their names
        if "[m_c_mates]" in mate_string:
            mate_names = [str(cat_from.fetch_cat(mate_id).name) for mate_id in cat_from.mate]
            mate_name_string = mate_names[0]
            if len(mate_names) == 2:
                mate_name_string = mate_names[0] + " and " + mate_names[1]
            if len(mate_names) > 2:
                mate_name_string = ", ".join(mate_names[:-1]) + ", and " + mate_names[-1]
            mate_string = mate_string.replace("[m_c_mates]", mate_name_string)

        if "[r_c_mates]" in mate_string:
            mate_names = [str(cat_to.fetch_cat(mate_id).name) for mate_id in cat_to.mate]
            mate_name_string = mate_names[0]
            if len(mate_names) == 2:
                mate_name_string = mate_names[0] + " and " + mate_names[1]
            if len(mate_names) > 2:
                mate_name_string = ", ".join(mate_names[:-1]) + ", and " + mate_names[-1]
            mate_string = mate_string.replace("[r_c_mates]", mate_name_string)

        if "(m_c_mate/mates)":
            insert = "mate"
            if len(cat_from.mate) > 1:
                insert = "mates"
            mate_string = mate_string.replace("(m_c_mate/mates)", insert)

        if "(r_c_mate/mates)":
            insert = "mate"
            if len(cat_to.mate) > 1:
                insert = "mates"
            mate_string = mate_string.replace("(r_c_mate/mates)", insert)

        mate_string = event_text_adjust(Cat, mate_string, cat_from, cat_to)
        return mate_string

    def get_mate_string(self, key, poly, cat_from, cat_to):
        """Returns the mate string with the certain key, cats and poly."""
        if not poly:
            return choice(MATE_DICTS[key])
        else:
            poly_key = ""
            alive_inclan_from_mates = [mate for mate in cat_from.mate if not cat_from.fetch_cat(mate).dead and not cat_from.fetch_cat(mate).outside]
            alive_inclan_to_mates = [mate for mate in cat_to.mate if not cat_to.fetch_cat(mate).dead and not cat_to.fetch_cat(mate).outside]
            if len(alive_inclan_from_mates) > 0 and len(alive_inclan_to_mates) > 0:
                poly_key = "both_mates"
            elif len(alive_inclan_from_mates) > 0 and len(alive_inclan_to_mates) <= 0:
                poly_key = "m_c_mates"
            elif len(alive_inclan_from_mates) <= 0 and len(alive_inclan_to_mates) > 0:
                poly_key = "r_c_mates"
            return choice(POLY_MATE_DICTS[key][poly_key])

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
            last_log1 = relationship_from.log[len(relationship_from.log) - 1]

            if 'negative' in last_log1:
                chance_number -= 30
                if 'fight' in last_log1:
                    chance_number -= 20
                if 'argument' in last_log1:
                    chance_number -= 10
                if 'different view' in last_log1:
                    chance_number -= 5
            
            # also look at the last 3 interactions if there are more than that
            if len(relationship_from.log) > 2:
                last_log2 = relationship_from.log[len(relationship_from.log) - 2]
                if 'negative' in last_log2:
                    chance_number -= 15
                last_log3 = relationship_from.log[len(relationship_from.log) - 3]
                if 'negative' in last_log3:
                    chance_number -= 10

            # check all interactions - positive and negative will "balance" each other out
            negative_interactions = list(filter(lambda inter: 'negative' in inter, relationship_from.log))
            chance_number -= len(negative_interactions)
            positive_interactions = list(filter(lambda inter: 'positive' in inter, relationship_from.log))
            chance_number += len(positive_interactions)

            if len(negative_interactions) * 2 > len(positive_interactions) and len(relationship_from.log) > 5 :
                chance_number -= 20

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

POLY_MATE_DICTS = None
with open(f"{resource_directory}become_mates_poly.json", 'r') as read_file:
    POLY_MATE_DICTS = ujson.loads(read_file.read())

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
        MATE_INTERACTIONS["positive"].extend(dictionary["decrease"])
        MATE_INTERACTIONS["negative"].extend(dictionary["increase"])
    else:
        MATE_INTERACTIONS["positive"].extend(dictionary["increase"])
        MATE_INTERACTIONS["negative"].extend(dictionary["decrease"])

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