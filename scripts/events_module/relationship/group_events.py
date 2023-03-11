import os
try:
    import ujson
except ImportError:
    import json as ujson
from random import choice, shuffle
from copy import deepcopy

from scripts.utility import change_relationship_values
from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.cat_relations.relationship import create_group_interaction
from scripts.game_structure.game_essentials import game
from scripts.cat_relations.relationship import Group_Interaction

class Group_Events():

    def __init__(self) -> None:
        self.chosen_interaction = None
        self.abbreviations_cat_id = {}
        self.cat_abbreviations_counter = {}
        pass

    def start_interaction(self, cat: Cat, interact_cats: list):
        """Start to define the possible group interactions.

            Parameters
            ----------
            cat : Cat
                the main cat
            interact_cats : list
                a list of cats, which are open to interact with the main cat

            Returns
            -------
        """
        self.abbreviations_cat_id = {}
        self.cat_abbreviations_counter = {}
        self.abbreviations_cat_id["m_c"] = cat.ID
        cat_amount = choice(list(GROUP_INTERACTION_MASTER_DICT.keys()))
        inter_type = choice(["negative", "positive", "neutral"])

        # for testing purposes TODO: Remove after testing
        cat_amount = "3"
        inter_type = "neutral"

        # if the chosen amount is bigger than the given interaction cats,
        # there will be no possible solution and it will be returned
        if len(interact_cats) < int(cat_amount):
            print("RETURN 1")
            return

        # setup the abbreviations_cat_id dictionary
        for integer in range(int(cat_amount)):
            new_key = "r_c" + str(integer+1)
            self.abbreviations_cat_id[new_key] = None

        possibilities = GROUP_INTERACTION_MASTER_DICT[cat_amount][inter_type]
        
        # get some filters premisses
        biome = str(game.clan.biome).casefold()
        season = str(game.clan.current_season).casefold()

        # start filter for main cat
        possibilities = self.get_main_cat_interactions(possibilities,biome,season)

        # get the information, which cat can be which abbreviations and only get the possible interactions
        possibilities = self.get_filtered_interactions(possibilities, int(cat_amount), interact_cats)

        # if there is no possibility return
        if len(possibilities) < 1:
            print("RETURN 2")
            return

        # choose one interaction and trigger all needed functions to reflect the interaction
        self.chosen_interaction = choice(possibilities)

        self.injuring_cats()
        amount = game.config["relationship"]["in_decrease_value"][self.chosen_interaction.intensity]

        # if there is a general reaction in the interaction, then use this
        if len(self.chosen_interaction.general_reaction) > 0:
            self.influence_general_relationship(amount)
        else:
            self.influence_specific_relationships(amount)

        interaction_str = choice(self.chosen_interaction.interactions)
        interaction_str = self.prepare_text(interaction_str)
        # TODO: add the interaction to the relationship log?
        interaction_str = interaction_str + f" ({inter_type})"
        game.cur_events_list.append(Single_Event(
            interaction_str, ["relation", "interaction"], self.abbreviations_cat_id.values()
        ))

    # ---------------------------------------------------------------------------- #
    #                  functions to filter and decide interaction                  #
    # ---------------------------------------------------------------------------- #

    def get_main_cat_interactions(self, interactions: list, biome : str, season : str):
        """Filter interactions for MAIN cat.
            
            Parameters
            ----------
            interactions : list
                the interactions which need to be filtered
            biome : str
                biome of the clan
            season : str
                current season of the clan

            Returns
            -------
            filtered : list
                a list of interactions, which fulfill the criteria
        """
        filtered_interactions = []
        _season = [season, "Any", "any"]
        _biome = [biome, "Any", "any"]
        main_cat = Cat.all_cats[self.abbreviations_cat_id["m_c"]]
        for interact in interactions:
            in_tags = list(filter(lambda biome: biome in _biome, interact.biome))
            if len(in_tags) > 0:
                continue

            in_tags = list(filter(lambda season: season in _season, interact.season))
            if len(in_tags) > 0:
                continue

            if len(interact.status_constraint) >= 1 and "m_c" in interact.status_constraint:
                if main_cat.status not in interact.status_constraint:
                    continue

            if len(interact.trait_constraint) >= 1 and "m_c" in interact.trait_constraint:
                if main_cat.trait not in interact.trait_constraint:
                    continue

            if len(interact.skill_constraint) >= 1 and "m_c" in interact.skill_constraint:
                if main_cat.skill not in interact.skill_constraint:
                    continue

            filtered_interactions.append(interact)
        return filtered_interactions

    def get_filtered_interactions(self, interactions: list, amount: int, interact_cats: list):
        """Handles the whole filtered interaction list based on all other constraints."""
        print("LIST BEFORE FILTERING", len(interactions))
        # first get all abbreviations possibilities for the cats
        abbr_per_interaction = self.get_abbreviations_possibilities(interactions, int(amount), interact_cats)

        # check which combinations are possible
        abbr_per_interaction = self.remove_impossible_abbreviations_combinations(abbr_per_interaction)

        # set which abbreviations is which cat
        self.set_abbreviations_cats(interact_cats)
        # check if any abbreviations_cat_ids is None, if so return, because the interaction should not continue
        not_none = [abbr != None for abbr in self.abbreviations_cat_id.values()]
        if not all(not_none):
            print("RETURN 1.2")
            return []

        # last filter based on relationships between the cats
        filtered_interactions = []
        for interact in interactions:
            # if this interaction is not in the cleared abbreviations dictionary,
            # there is no solution for the cat-abbreviation problem and thus, this
            # interaction is not possible
            if interact.id not in abbr_per_interaction.keys():
                continue

            # check if all cats fulfill the status constraints
            all_fulfilled = True
            for abbr, value in interact.status_constraint.items():
                # main cat is already filtered
                if abbr == "m_c":
                    continue
                relevant_cat = Cat.all_cats[self.abbreviations_cat_id[abbr]]
                if relevant_cat.status not in value:
                    all_fulfilled = False
            if not all_fulfilled:
                continue

            # check if all cats fulfill the skill constraints
            all_fulfilled = True
            for abbr, value in interact.skill_constraint.items():
                # main cat is already filtered
                if abbr == "m_c":
                    continue
                relevant_cat = Cat.all_cats[self.abbreviations_cat_id[abbr]]
                if relevant_cat.skill not in value:
                    all_fulfilled = False
            if not all_fulfilled:
                continue

            # check if all cats fulfill the trait constraints
            all_fulfilled = True
            for abbr, value in interact.trait_constraint.items():
                # main cat is already filtered
                if abbr == "m_c":
                    continue
                relevant_cat = Cat.all_cats[self.abbreviations_cat_id[abbr]]
                if relevant_cat.trait not in value:
                    all_fulfilled = False
            if not all_fulfilled:
                continue

            # now check for relationship constraints
            relationship_allow_interaction = self.relationship_allow_interaction(interact)
            if not relationship_allow_interaction:
                continue

            filtered_interactions.append(interact)

        print("LIST BEFORE FILTERING", len(filtered_interactions))
        return filtered_interactions

    def get_abbreviations_possibilities(self, interactions: list, amount: int, interact_cats: list):
        """ Iterate over all pre-filtered interactions and 
            check which cat fulfills skill/trait/status condition of which abbreviation.

            Parameters
            ----------
            interactions : list
                the interactions which need to be filtered
            amount : int
                the amount of cats for the current interaction
            interact_cats : list
                a list of cats, which are open to interact with the main cat
        """
        possibilities = {}
        # prepare how the base dictionary should look, 
        # this depends on the chosen cat amount -> which abbreviation are needed
        base_dictionary = {}
        for integer in range(amount):
            new_key = "r_c" + str(integer+1)
            base_dictionary[new_key] = []

        # iterate over all interactions and checks for each abbreviation, which cat is possible
        for interact in interactions:
            dictionary = deepcopy(base_dictionary)

            for abbreviation in dictionary:
                dictionary[abbreviation] = []
                status_ids = []
                skill_ids = []
                trait_ids = []

                # if the abbreviation has a status constraint, check in details
                if abbreviation in interact.status_constraint:
                    # if the cat status is in the status constraint, add the id to the list
                    status_ids = [cat.ID for cat in interact_cats if cat.status in interact.status_constraint]
                # if there is no constraint, add all ids to the list 
                else:
                    status_ids = [cat.ID for cat in interact_cats]

                # same as status
                if abbreviation in interact.skill_constraint:
                    skill_ids = [cat.ID for cat in interact_cats if cat.skill in interact.skill_constraint]
                else:
                    skill_ids = [cat.ID for cat in interact_cats]

                if abbreviation in interact.trait_constraint:
                    trait_ids = [cat.ID for cat in interact_cats if cat.trait in interact.trait_constraint]
                else:
                    trait_ids = [cat.ID for cat in interact_cats]

                # only add the id if it is in all other lists
                for cat_id in [cat.ID for cat in interact_cats]:
                    if cat_id in status_ids and cat_id in skill_ids and cat_id in trait_ids:
                        dictionary[abbreviation].append(cat_id)

                        if cat_id in self.cat_abbreviations_counter and\
                            abbreviation in self.cat_abbreviations_counter[cat_id]:
                            self.cat_abbreviations_counter[cat_id][abbreviation] +=1
                        elif cat_id in self.cat_abbreviations_counter and\
                            abbreviation not in self.cat_abbreviations_counter[cat_id]:
                            self.cat_abbreviations_counter[cat_id][abbreviation] = 1
                        else:
                            self.cat_abbreviations_counter[cat_id] = {}
                            self.cat_abbreviations_counter[cat_id][abbreviation] = 1

            possibilities[interact.id] = dictionary
        return possibilities

    def remove_impossible_abbreviations_combinations(self, abbreviations_per_interaction: dict):
        """
        Check which combinations of abbreviations are allowed and possible and which are not, only return a dictionary,
        with possible combinations together with the id for the interaction.
        """
        filtered_abbreviations = {}
        for interaction_id, dictionary in abbreviations_per_interaction.items():
            # check if there is any abbreviation, which is empty
            abbr_length = [len(val) for abr,val in dictionary.items()]
            # if one length is 0 the all function returns false
            if not all(abbr_length):
                continue

            filtered_abbreviations[interaction_id] = dictionary
        return filtered_abbreviations

    def set_abbreviations_cats(self, interact_cats: list):
        """Choose which cat is which abbreviations."""
        free_to_choose = [cat.ID for cat in interact_cats]
        # shuffle the list to prevent choosing the same cats every time
        shuffle(free_to_choose)

        for abbr_key in list(self.abbreviations_cat_id.keys()):
            if abbr_key == "m_c":
                continue
            highest_value = 0
            highest_id = None

            # gets the cat id which fits the abbreviations most of the time
            for cat_id in free_to_choose:
                # first set some values if there are none
                if cat_id not in self.cat_abbreviations_counter:
                    self.cat_abbreviations_counter[cat_id] = {}
                if abbr_key not in self.cat_abbreviations_counter[cat_id]:
                    self.cat_abbreviations_counter[cat_id][abbr_key] = 0

                # find the highest value
                curr_value = self.cat_abbreviations_counter[cat_id][abbr_key]
                if highest_value < curr_value:
                    highest_value = curr_value
                    highest_id = cat_id
            
            self.abbreviations_cat_id[abbr_key] = highest_id
            if highest_id in free_to_choose:
                free_to_choose.remove(highest_id)

    def relationship_allow_interaction(self, interaction: Group_Interaction):
        """Check if the interaction is allowed with the current chosen cats."""
        fulfilled_list = []

        for name, dictionary in interaction.specific_reaction.items():
            abbre_from = name.split('_to_')[0]
            abbre_to = name.split('_to_')[1]

            cat_from_id = self.abbreviations_cat_id[abbre_from]
            cat_to_id = self.abbreviations_cat_id[abbre_to]
            cat_from = Cat.all_cats[cat_from_id]
            cat_to = Cat.all_cats[cat_to_id]

            if "siblings" in dictionary and not cat_from.is_sibling(cat_to):
                continue

            if "mates" in dictionary and not self.mates:
                continue

            if "not_mates" in dictionary and self.mates:
                continue

            if "parent/child" in dictionary and not cat_from.is_parent(cat_to):
                continue

            if "child/parent" in dictionary and not cat_to.is_parent(cat_from):
                continue

            value_types = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
            fulfilled = True
            for v_type in value_types:
                tags = list(filter(lambda constr: v_type in constr, dictionary))
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
                    print(f"ERROR: interaction {interaction.id} with the relationship constraint for the value {v_type} follows not the formatting guidelines.")
                    break

                if threshold > 100:
                    print(f"ERROR: interaction {interaction.id} has a relationship constraints for the value {v_type}, which is higher than the max value of a relationship.")
                    break

                if threshold <= 0:
                    print(f"ERROR: patrol {interaction.id} has a relationship constraints for the value {v_type}, which is lower than the min value of a relationship or 0.")
                    break

                threshold_fulfilled = False
                if v_type == "romantic":
                    if not lower_than and self.romantic_love >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.romantic_love <= threshold:
                        threshold_fulfilled = True
                if v_type == "platonic":
                    if not lower_than and self.platonic_like >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.platonic_like <= threshold:
                        threshold_fulfilled = True
                if v_type == "dislike":
                    if not lower_than and self.dislike >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.dislike <= threshold:
                        threshold_fulfilled = True
                if v_type == "comfortable":
                    if not lower_than and self.comfortable >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.comfortable <= threshold:
                        threshold_fulfilled = True
                if v_type == "jealousy":
                    if not lower_than and self.jealousy >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.jealousy <= threshold:
                        threshold_fulfilled = True
                if v_type == "trust":
                    if not lower_than and self.trust >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.trust <= threshold:
                        threshold_fulfilled = True

                if not threshold_fulfilled:
                    fulfilled = False
                    continue

            fulfilled_list.append(fulfilled)

        return all(fulfilled_list)

    # ---------------------------------------------------------------------------- #
    #                      functions after interaction decision                    #
    # ---------------------------------------------------------------------------- #

    def influence_general_relationship(self, amount):
        """
        Influence the relationship between all cats with the same amount, defined by the chosen group relationship.
        """
        dictionary = self.chosen_interaction.general_interaction

        # set the amount
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "romantic" in dictionary and dictionary["romantic"] != "neutral":
            romantic = amount if dictionary["romantic"] == "increase" else amount *-1
        if "platonic" in dictionary and dictionary["platonic"] != "neutral":
            platonic = amount if dictionary["platonic"] == "increase" else amount *-1
        if "dislike" in dictionary and dictionary["dislike"] != "neutral":
            platonic = amount if dictionary["dislike"] == "increase" else amount *-1
        if "admiration" in dictionary and dictionary["admiration"] != "neutral":
            platonic = amount if dictionary["admiration"] == "increase" else amount *-1
        if "comfortable" in dictionary and dictionary["comfortable"] != "neutral":
            platonic = amount if dictionary["comfortable"] == "increase" else amount *-1
        if "jealousy" in dictionary and dictionary["jealousy"] != "neutral":
            platonic = amount if dictionary["jealousy"] == "increase" else amount *-1
        if "trust" in dictionary and dictionary["trust"] != "neutral":
            platonic = amount if dictionary["trust"] == "increase" else amount *-1


        for inter_cat_id in self.abbreviations_cat_id.values():
            change_relationship_values(
                cats_from=inter_cat_id,
                cats_to=self.abbreviations_cat_id.values(),
                romantic_love=romantic,
                platonic_like=platonic,
                dislike=dislike,
                admiration=admiration,
                comfortable=comfortable,
                jealousy=jealousy,
                trust=trust
            )

    def influence_specific_relationships(self, amount):
        """
        Influence the relationships based on the list of the reaction of the chosen group interaction.
        """
        if len(self.chosen_interaction.specific_reaction) <= 0:
            return

        for name, dictionary in self.chosen_interaction.specific_reaction.items():
            abbre_from = name.split('_to_')[0]
            abbre_to = name.split('_to_')[1]

            cat_from_id = self.abbreviations_cat_id[abbre_from]
            cat_to_id = self.abbreviations_cat_id[abbre_to]

            # set all values to influence the relationship
            romantic = 0
            platonic = 0
            dislike = 0
            admiration = 0
            comfortable = 0
            jealousy = 0
            trust = 0
            if "romantic" in dictionary and dictionary["romantic"] != "neutral":
                romantic = amount if dictionary["romantic"] == "increase" else amount *-1
            if "platonic" in dictionary and dictionary["platonic"] != "neutral":
                platonic = amount if dictionary["platonic"] == "increase" else amount *-1
            if "dislike" in dictionary and dictionary["dislike"] != "neutral":
                platonic = amount if dictionary["dislike"] == "increase" else amount *-1
            if "admiration" in dictionary and dictionary["admiration"] != "neutral":
                platonic = amount if dictionary["admiration"] == "increase" else amount *-1
            if "comfortable" in dictionary and dictionary["comfortable"] != "neutral":
                platonic = amount if dictionary["comfortable"] == "increase" else amount *-1
            if "jealousy" in dictionary and dictionary["jealousy"] != "neutral":
                platonic = amount if dictionary["jealousy"] == "increase" else amount *-1
            if "trust" in dictionary and dictionary["trust"] != "neutral":
                platonic = amount if dictionary["trust"] == "increase" else amount *-1

            change_relationship_values(
                cats_from=cat_from_id,
                cats_to=[cat_to_id],
                romantic_love=romantic,
                platonic_like=platonic,
                dislike=dislike,
                admiration=admiration,
                comfortable=comfortable,
                jealousy=jealousy,
                trust=trust
            )

    def injuring_cats(self):
        """
        Injuring the cats based on the list of the injuries of the chosen group interaction.
        """
        if len(self.chosen_interaction.injuries) <= 0:
            return

        for abbreviations, injuries in self.chosen_interaction.injuries.items():
            injured_cat = Cat.all_cats[self.abbreviations_cat_id[abbreviations]]
            
            for inj in injuries:
                injured_cat.get_injured(inj, True)

    def prepare_text(self, text: str) -> str:
        """Prep the text based of the amount of cats and the assigned abbreviations."""
        for abbr, cat_id in self.abbreviations_cat_id.items():
            current_cat_name = Cat.all_cats[cat_id]
            text = text.replace(abbr, str(current_cat_name))
        return text

# ---------------------------------------------------------------------------- #
#                   build master dictionary for interactions                   #
# ---------------------------------------------------------------------------- #


base_path = os.path.join(
    "resources",
    "dicts",
    "relationship_events",
    "group_interactions"
)

GROUP_INTERACTION_MASTER_DICT = {}
for cat_amount in os.listdir(base_path):
    file_path = os.path.join(base_path, cat_amount, "neutral.json")
    GROUP_INTERACTION_MASTER_DICT[cat_amount] = {}
    with open(file_path, 'r') as read_file:
        welcome_list = ujson.load(read_file)
        GROUP_INTERACTION_MASTER_DICT[cat_amount]["neutral"] = create_group_interaction(welcome_list)
    
    file_path = os.path.join(base_path, cat_amount, "positive.json")
    with open(file_path, 'r') as read_file:
        welcome_list = ujson.load(read_file)
        GROUP_INTERACTION_MASTER_DICT[cat_amount]["positive"] = create_group_interaction(welcome_list)

    file_path = os.path.join(base_path, cat_amount, "negative.json")
    with open(file_path, 'r') as read_file:
        welcome_list = ujson.load(read_file)
        GROUP_INTERACTION_MASTER_DICT[cat_amount]["negative"] = create_group_interaction(welcome_list)