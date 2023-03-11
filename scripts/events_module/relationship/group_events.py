import os
try:
    import ujson
except ImportError:
    import json as ujson
from random import choice
from copy import deepcopy

from scripts.utility import change_relationship_values
from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.cat_relations.relationship import create_group_interaction
from scripts.game_structure.game_essentials import game

class Group_Events():

    def __init__(self) -> None:
        self.chosen_interaction = None
        self.abbreviations_cat_id = {}
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
        self.abbreviations_cat_id["m_c"] = cat.id
        cat_amount = choice(GROUP_INTERACTION_MASTER_DICT.keys())
        inter_type = choice(["negative", "positive", "neutral"])

        # if the chosen amount is bigger than the given interaction cats,
        # there will be no possible solution and it will be returned
        if len(interact_cats) < int(cat_amount):
            return

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
            interaction_str, ["relation", "interaction"], [self.cat_to.ID, self.cat_from.ID]
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
        # TODO: finish this function

        # first get all abbreviations possibilities for the cats
        abbreviations_per_interaction = self.get_abbreviations_possibilities(interactions, int(amount), interact_cats)

        # check which combinations are possible

        # set which abbreviations is which cat

        # last filter based on relationships between the cats
        filtered_interactions = []

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

            possibilities[interact.id] = dictionary

    def remove_impossible_abbreviations_combinations(self, abbreviations_per_interaction: dict):
        filtered_abbreviations = {}
        return filtered_abbreviations

    def set_abbreviations_cats(self):
        print("TODO")

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
for file in os.listdir(base_path):
    cat_amount = file.split(".")[0]
    with open(os.path.join(base_path, file), 'r') as read_file:
        welcome_list = ujson.load(read_file)
        GROUP_INTERACTION_MASTER_DICT[cat_amount]["negative"] = create_group_interaction(welcome_list["negative"])
        GROUP_INTERACTION_MASTER_DICT[cat_amount]["neutral"] = create_group_interaction(welcome_list["neutral"])
        GROUP_INTERACTION_MASTER_DICT[cat_amount]["positive"] = create_group_interaction(welcome_list["positive"])