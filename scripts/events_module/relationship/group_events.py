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
        pass

    def filter_interactions(self, interactions):
        filtered_interactions = []
        for interaction in interactions:
            filtered_interactions.append(interaction)
        return filtered_interactions


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