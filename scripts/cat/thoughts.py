import os
from random import choice

try:
    import ujson
except ImportError:
    import json as ujson

class Thoughts():
    def __init__(self,
                 id,
                 biome=None,
                 season=None,
                 thoughts=None,
                 has_injuries=None,
                 perm_conditions=None,
                 relationship_constraint=None,
                 backstory_constraint=None,
                 main_status_constraint=None,
                 random_status_constraint=None,
                 main_age_constraint=None,
                 random_age_constraint=None,
                 main_trait_constraint=None,
                 random_trait_constraint=None,
                 main_skill_constraint=None,
                 random_skill_constraint=None,
                 random_living_status=None,
                 random_outside_status=None):
        self.id = id
        self.biome = biome if biome else ["Any"]
        self.season = season if season else ["Any"]

        if thoughts:
            self.thoughts = thoughts
        else:
            self.thoughts = [f"Isn't thinking about much at the moment"]
        
        if has_injuries: # for if a cat has injuries
            self.has_injuries = has_injuries
        else:
            self.has_injuries = {}
        
        if perm_conditions: # for a cat with a perm condition
            self.perm_conditions = perm_conditions
        else:
            self.perm_conditions = []
        
        if relationship_constraint: # handles relationships such as sibling, parents, etc
            self.relationship_constraint = relationship_constraint
        else:
            self.relationship_constraint = []
        
        '''for backstory constraint, m_c and r_c should be lists within the dict'''
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

        if main_age_constraint:
            self.main_age_constraint = main_age_constraint
        else:
            self.main_age_constraint = []

        if random_age_constraint:
            self.random_age_constraint = random_age_constraint
        else:
            self.random_age_constraint = []

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

        if random_living_status:
            self.random_living_status = random_living_status
        else:
            self.random_living_status = []
        if random_outside_status:
            self.random_outside_status = random_outside_status
        else:
            self.random_outside_status = []

    def __str__(self) -> str:
        if len(self.thoughts) > 0:
            return choice(self.thoughts)
        else:
            #This should never happen. 
            return "Has no thoughts, head empty"

# ---------------------------------------------------------------------------- #
#                some useful functions, related to thoughts                    #
# ---------------------------------------------------------------------------- #

    def thought_fulfill_rel_constraints(self, relationship, constraint, thought_id) -> bool:
        """Check if the relationship fulfills the interaction relationship constraints."""
        # if the constraints are not existing, they are considered to be fulfilled
        if relationship == None:
            return False
        if not constraint:
            return True
        if len(constraint) == 0:
            return True
                
        if "siblings" in constraint and not relationship.cat_from.is_sibling(relationship.cat_to):
            return False

        if "mates" in constraint and not relationship.mates:
            return False

        if "not_mates" in constraint and relationship.mates:
            return False

        if "parent/child" in constraint and not relationship.cat_from.is_parent(relationship.cat_to):
            return False

        if "child/parent" in constraint and not relationship.cat_to.is_parent(relationship.cat_from):
            return False

        return True

    def cats_fulfill_thought_constraints(self, main_cat, random_cat, thought, game_mode) -> bool:
        """Check if the two cats fulfills the thought constraints."""
        if random_cat.ID in main_cat.relationships:
            relationship = main_cat.relationships[random_cat.ID]
        else:
            relationship = None
        try:
            if len(thought['relationship_constraint']) >= 1:
                for constraint in thought['relationship_constraint']:
                    if self.thought_fulfill_rel_constraints(self, relationship, constraint, thought['id']):
                        continue
        except KeyError:
            pass
        
        try:
            if len(thought['main_status_constraint']) >= 1:
                if main_cat.status not in thought['main_status_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['random_status_constraint']) >= 1:
                if random_cat.status not in thought['random_status_constraint']:
                    return False
        except KeyError:
            pass
        
        try:
            if len(thought['main_age_constraint']) >= 1:
                if main_cat.age not in thought['main_age_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['random_age_constraint']) >= 1:
                if random_cat.age not in thought['random_age_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['main_trait_constraint']) >= 1:
                if main_cat.trait not in thought['main_trait_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['random_trait_constraint']) >= 1:
                if random_cat.trait not in thought['random_trait_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['main_skill_constraint']) >= 1:
                if main_cat.skill not in thought['main_skill_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['random_skill_constraint']) >= 1:
                if random_cat.skill not in thought['random_skill_constraint']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['backstory_constraint']) >= 1:
                if main_cat.backstory not in thought['backstory_constraint']["m_c"]:
                    return False
                if random_cat.backstory not in thought['backstory_constraint']["r_c"]:
                    return False
        except KeyError:
            pass
        
        try:
            if len(thought['random_living_status']) >= 1:
                living_status = None
                if not random_cat.dead:
                    living_status = "living"
                elif random_cat.dead and random_cat.df:
                    living_status = "darkforest"
                elif random_cat.dead and not random_cat.df:
                    living_status = "starclan"
                else:
                    living_status = 'unknownresidence'
                if living_status not in thought['random_living_status']:
                    return False
        except KeyError:
            pass
            
        try:
            if len(thought['random_outside_status']) >= 1:
                outside_status = None
                if random_cat.outside and random_cat.status not in ["kittypet", "loner", "rogue", "former Clancat"]:
                    outside_status = "lost"
                else:
                    outside_status = "outside cat"
                if outside_status not in thought['random_outside_status']:
                    return False
        except KeyError:
            pass

        try:
            if len(thought['has_injuries']) >= 1:
                # if there is a injury constraint and the clan is in classic mode, this interact can not be used
                if game_mode == "classic":
                    return False

                if "m_c" in thought['has_injuries']:
                    injuries_in_needed = list(
                        filter(lambda inj: inj in thought['has_injuries']["m_c"], main_cat.injuries.keys())
                    )
                    if len(injuries_in_needed) <= 0:
                        return False
                if "r_c" in thought['has_injuries']:
                    injuries_in_needed = list(
                        filter(lambda inj: inj in thought['has_injuries']["r_c"], random_cat.injuries.keys())
                    )
                    if len(injuries_in_needed) <= 0:
                        return False
        except KeyError:
            pass

        return True
    # ---------------------------------------------------------------------------- #
    #                            BUILD MASTER DICTIONARY                           #
    # ---------------------------------------------------------------------------- #

    def create_thoughts(self, inter_list, main_cat, other_cat, game_mode) -> list:
        created_list = []
        for inter in inter_list:
            if self.cats_fulfill_thought_constraints(self, main_cat, other_cat, inter, game_mode):
                created_list.append(Thoughts(
                id=inter["id"],
                biome=inter["biome"] if "biome" in inter else ["Any"],
                season=inter["season"] if "season" in inter else ["Any"],
                thoughts=inter["thoughts"] if "thoughts" in inter else None,
                has_injuries=inter["has_injuries"] if "has_injuries" in inter else None,
                perm_conditions=inter["perm_conditions"] if "perm_conditions" in inter else None,
                relationship_constraint = inter["relationship_constraint"] if "relationship_constraint" in inter else None,
                backstory_constraint = inter["backstory_constraint"] if "backstory_constraint" in inter else None,
                main_status_constraint = inter["main_status_constraint"] if "main_status_constraint" in inter else None,
                random_status_constraint = inter["random_status_constraint"] if "random_status_constraint" in inter else None,
                main_age_constraint = inter["main_age_constraint"] if "main_age_constraint" in inter else None,
                random_age_constraint = inter["random_age_constraint"] if "random_age_constraint" in inter else None,
                main_trait_constraint = inter["main_trait_constraint"] if "main_trait_constraint" in inter else None,
                random_trait_constraint = inter["random_trait_constraint"] if "random_trait_constraint" in inter else None,
                main_skill_constraint = inter["main_skill_constraint"] if "main_skill_constraint" in inter else None,
                random_skill_constraint = inter["random_skill_constraint"] if "random_skill_constraint" in inter else None,
                random_living_status = inter["random_living_status"] if "random_living_status" in inter else None,
                random_outside_status = inter["random_outside_status"] if "random_outside_status" in inter else None
            ))
        return created_list

    def load_thoughts(self, main_cat, other_cat, status, game_mode):
        base_path = f"resources/dicts/thoughts/"
        life_dir = None
        status = status
        loaded_thoughts = []

        if not main_cat.dead and not main_cat.outside:
            life_dir = "alive"
        else:
            life_dir = "dead"

        if not main_cat.dead and main_cat.outside:
            spec_dir = "/alive_outside"
        elif main_cat.dead and not main_cat.outside and not main_cat.df:
            spec_dir = "/starclan"
        elif main_cat.dead and not main_cat.outside and main_cat.df:
            spec_dir = "/darkforest"
        elif main_cat.dead and main_cat.outside:
            spec_dir = "/unknownresidence"
        else:
            spec_dir = ""

        THOUGHTS = []
        with open(f"{base_path}{life_dir}{spec_dir}/{status}.json", 'r') as read_file:
            THOUGHTS = ujson.loads(read_file.read())
        GENTHOUGHTS = []
        with open(f"{base_path}{life_dir}{spec_dir}/general.json", 'r') as read_file:
            GENTHOUGHTS = ujson.loads(read_file.read())
        loaded_thoughts += THOUGHTS
        loaded_thoughts += GENTHOUGHTS
        final_thoughts = choice(self.create_thoughts(self, loaded_thoughts, main_cat, other_cat, game_mode))

        return final_thoughts
    
    def get_chosen_thought(self, main_cat, other_cat, status, game_mode):
        # get possible thoughts
        thought_str = str(self.load_thoughts(self, main_cat, other_cat, status, game_mode))
        chosen_thought = thought_str

        return chosen_thought
