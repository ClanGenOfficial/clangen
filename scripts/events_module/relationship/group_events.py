import os
try:
    import ujson
except ImportError:
    import json as ujson
from copy import deepcopy
from random import choice

from scripts.utility import change_relationship_values
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event
from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship, create_group_interaction

class Group_Events():

    def __init__(self) -> None:
        self.chosen_interaction = None
        self.abbreviations_cat_id = {}
        self.involved_cats = {}
        pass

    def filter_interactions(self, interactions):
        filtered_interactions = []
        for interaction in interactions:
            filtered_interactions.append(interaction)
        return filtered_interactions

    def influence_general_relationship(self):
        """
        Influence the relationship between all cats with the same amount, defined by the chosen group relationship.
        """

    def influence_specific_relationships(self, reaction_list, amount):
        """
        Influence the relationships based on the list of the reaction of the chosen group interaction.
        """
        if len(reaction_list) <= 0:
            return

        for name, dictionary in reaction_list.items():
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

    def injuring_cats(self, injury_list):
        """
        Injuring the cats based on the list of the injuries of the chosen group interaction.
        """
        if len(injury_list) <= 0:
            return

        for abbreviations, injuries in injury_list.items():
            injured_cat = Cat.all_cats[self.abbreviations_cat_id[abbreviations]]
            
            for inj in injuries:
                injured_cat.get_injured(inj, True)


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
        GROUP_INTERACTION_MASTER_DICT[cat_amount] = create_group_interaction(welcome_list)