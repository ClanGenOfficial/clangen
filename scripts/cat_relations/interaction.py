import os
try:
    import ujson
except ImportError:
    import json as ujson

class Single_Interaction():

    def __init__(self,
                 id,
                 biome=None,
                 season=None,
                 intensity="medium",
                 interactions=None,
                 injuries=None,
                 relationship_constraint=None,
                 backstory_constraint=None,
                 main_status_constraint=None,
                 random_status_constraint=None,
                 main_trait_constraint=None,
                 random_trait_constraint=None,
                 main_skill_constraint=None,
                 random_skill_constraint=None,
                 reaction_random_cat=None,
                 also_influences=None):
        self.id = id
        self.intensity = intensity
        self.biome = biome if biome else ["Any"]
        self.season = season if season else ["Any"]

        if interactions:
            self.interactions = interactions
        else:
            self.interactions = [f"This is a default interaction! ID: {id} with cats (m_c), (r_c)"]

        if injuries:
            self.injuries = injuries
        else:
            self.injuries = {}

        if relationship_constraint:
            self.relationship_constraint = relationship_constraint
        else:
            self.relationship_constraint = []

        if backstory_constraint:
            self.backstory_constraint = backstory_constraint
        else:
            self.backstory_constraint = {}

        if main_status_constraint:
            self.main_status_constraint = main_status_constraint
        else:
            self.main_status_constraint = []

        if random_status_constraint:
            self.random_status_constraint = random_status_constraint
        else:
            self.random_status_constraint = []

        if main_trait_constraint:
            self.main_trait_constraint = main_trait_constraint
        else:
            self.main_trait_constraint = []

        if random_trait_constraint:
            self.random_trait_constraint = random_trait_constraint
        else:
            self.random_trait_constraint = []

        if main_skill_constraint:
            self.main_skill_constraint = main_skill_constraint
        else:
            self.main_skill_constraint = []

        if random_skill_constraint:
            self.random_skill_constraint = random_skill_constraint
        else:
            self.random_skill_constraint = []

        if reaction_random_cat:
            self.reaction_random_cat = reaction_random_cat
        else:
            self.reaction_random_cat = {}

        if also_influences:
            self.also_influences = also_influences
        else:
            self.also_influences = {}

class Group_Interaction():

    def __init__(self, 
                 id,
                 biome=None,
                 season=None,
                 intensity="medium",
                 cat_amount=None,
                 interactions=None,
                 injuries=None,
                 status_constraint=None,
                 trait_constraint=None,
                 skill_constraint=None,
                 relationship_constraint=None,
                 backstory_constraint=None,
                 specific_reaction=None,
                 general_reaction=None
                 ):
        self.id = id
        self.intensity = intensity
        self.biome = biome if biome else ["Any"]
        self.season = season if season else ["Any"]
        self.cat_amount = cat_amount

        if interactions:
            self.interactions = interactions
        else:
            self.interactions = [f"This is a default interaction! ID: {id} with cats (m_c), (r_c)"]

        if injuries:
            self.injuries = injuries
        else:
            self.injuries = {}

        if status_constraint:
            self.status_constraint = status_constraint
        else:
            self.status_constraint = {}

        if trait_constraint:
            self.trait_constraint = trait_constraint
        else:
            self.trait_constraint = {}

        if skill_constraint:
            self.skill_constraint = skill_constraint
        else:
            self.skill_constraint = {}

        if relationship_constraint:
            self.relationship_constraint = relationship_constraint
        else:
            self.relationship_constraint = {}

        if backstory_constraint:
            self.backstory_constraint = backstory_constraint
        else:
            self.backstory_constraint = {}

        if specific_reaction:
            self.specific_reaction = specific_reaction
        else:
            self.specific_reaction = {}

        if general_reaction:
            self.general_reaction = general_reaction
        else:
            self.general_reaction = {}

# ---------------------------------------------------------------------------- #
#                   build master dictionary for interactions                   #
# ---------------------------------------------------------------------------- #

def create_interaction(inter_list) -> list:
    created_list = []
    for inter in inter_list:
        created_list.append(Single_Interaction(
            id=inter["id"],
            biome=inter["biome"] if "biome" in inter else ["Any"],
            season=inter["season"] if "season" in inter else ["Any"],
            intensity=inter["intensity"] if "intensity" in inter else "medium",
            interactions=inter["interactions"] if "interactions" in inter else None,
            injuries=inter["injuries"] if "injuries" in inter else None,
            relationship_constraint = inter["relationship_constraint"] if "relationship_constraint" in inter else None,
            main_status_constraint = inter["main_status_constraint"] if "main_status_constraint" in inter else None,
            random_status_constraint = inter["random_status_constraint"] if "random_status_constraint" in inter else None,
            main_trait_constraint = inter["main_trait_constraint"] if "main_trait_constraint" in inter else None,
            random_trait_constraint = inter["random_trait_constraint"] if "random_trait_constraint" in inter else None,
            main_skill_constraint = inter["main_skill_constraint"] if "main_skill_constraint" in inter else None,
            random_skill_constraint = inter["random_skill_constraint"] if "random_skill_constraint" in inter else None,
            reaction_random_cat= inter["reaction_random_cat"] if "reaction_random_cat" in inter else None,
            also_influences = inter["also_influences"] if "also_influences" in inter else None
        ))
    return created_list

def create_group_interaction(inter_list) -> list:
    created_list = []
    for inter in inter_list:
        created_list.append(Group_Interaction(
            id=inter["id"],
            biome=inter["biome"] if "biome" in inter else ["Any"],
            season=inter["season"] if "season" in inter else ["Any"],
            cat_amount=inter["cat_amount"] if "cat_amount" in inter else None,
            intensity=inter["intensity"] if "intensity" in inter else "medium",
            interactions=inter["interactions"] if "interactions" in inter else None,
            injuries=inter["injuries"] if "injuries" in inter else None,
            status_constraint = inter["status_constraint"] if "status_constraint" in inter else None,
            trait_constraint = inter["trait_constraint"] if "trait_constraint" in inter else None,
            skill_constraint = inter["skill_constraint"] if "skill_constraint" in inter else None,
            relationship_constraint = inter["relationship_constraint"] if "relationship_constraint" in inter else None,
            specific_reaction= inter["specific_reaction"] if "specific_reaction" in inter else None,
            general_reaction= inter["general_reaction"] if "general_reaction" in inter else None
        ))
    return created_list

INTERACTION_MASTER_DICT = {"romantic": {}, "platonic": {}, "dislike": {}, "admiration": {}, "comfortable": {}, "jealousy": {}, "trust": {}}
rel_types = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
base_path = os.path.join("resources","dicts", "relationship_events", "normal_interactions")
for rel in rel_types:
    with open(os.path.join(base_path, rel , "increase.json"), 'r') as read_file:
        loaded_list = ujson.loads(read_file.read())
        INTERACTION_MASTER_DICT[rel]["increase"] = create_interaction(loaded_list)
    with open(os.path.join(base_path, rel , "decrease.json"), 'r') as read_file:
        loaded_list = ujson.loads(read_file.read())
        INTERACTION_MASTER_DICT[rel]["decrease"] = create_interaction(loaded_list)

NEUTRAL_INTERACTIONS = []
with open(os.path.join(base_path, "neutral.json"), 'r') as read_file:
    loaded_list = ujson.loads(read_file.read())
    NEUTRAL_INTERACTIONS = create_interaction(loaded_list)

