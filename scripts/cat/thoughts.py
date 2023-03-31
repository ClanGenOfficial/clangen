import os
from random import choice

try:
    import ujson
except ImportError:
    import json as ujson

class Thoughts():
    @staticmethod
    def thought_fulfill_rel_constraints(main_cat, random_cat, constraint) -> bool:
        """Check if the relationship fulfills the interaction relationship constraints."""
        # if the constraints are not existing, they are considered to be fulfilled
        
        # No current relationship-value bases tags, so this is commented out. 
        if random_cat in main_cat.relationships:
            relationship = main_cat.relationships[random_cat]
        else:
            relationship = None
                
        if "siblings" in constraint and not main_cat.is_sibling(random_cat):
            return False

        if "mates" in constraint and main_cat.mate != random_cat.ID:
            return False

        if "not_mates" in constraint and main_cat.mate == random_cat.ID:
            return False

        if "parent/child" in constraint and not main_cat.is_parent(random_cat):
            return False

        if "child/parent" in constraint and not random_cat.is_parent(main_cat):
            return False
        
        if "mentor/app" in constraint and random_cat not in main_cat.current_apprentice:
            return False
        
        if "app/mentor" in constraint and random_cat not in main_cat.mentor:
            return False
        
        if "strangers" in constraint and not (relationship.platonic_like < 1 or relationship.romantic_love < 1):
            return False

        return True

    @staticmethod
    def cats_fulfill_thought_constraints(main_cat, random_cat, thought, game_mode, biome, season, camp) -> bool:
        """Check if the two cats fulfills the thought constraints."""
        # This is for checking biome
        if "biome" in thought:
            if biome not in thought["biome"]:
                return False
            
        # This is checking for season
        if "season" in thought:
            if season == None:
                return False
            if season not in thought["season"]:
                return False

        # This is for checking camp
        if "camp" in thought:
            if camp not in thought["camp"]:
                return False
            
        # This is for filtering certain relationship types between the main cat and random cat. 
        if "relationship_constraint" in thought:
            if not Thoughts.thought_fulfill_rel_constraints(main_cat, random_cat, thought["relationship_constraint"]):
                return False
        
        # Contraints for the status of the main cat
        if 'main_status_constraint' in thought:
            if 'main_status_constraint' in thought and main_cat.status not in thought['main_status_constraint']:
                return False
        
        # Contraints for the status of the random cat
        if 'random_status_constraint' in thought:
            if random_cat.status not in thought['random_status_constraint']:
                return False
        
        # main cat age contraint
        if 'main_age_constraint' in thought:
            if main_cat.age not in thought['main_age_constraint']:
                return False
        
        if 'random_age_constraint' in thought:
            if random_cat.age not in thought['random_age_constraint']:
                return False

        if 'main_trait_constraint' in thought:
            if main_cat.trait not in thought['main_trait_constraint']:
                return False
            
        if 'random_trait_constraint' in thought:
            if random_cat.trait not in thought['random_trait_constraint']:
                return False

        if 'main_skill_constraint' in thought:
            if main_cat.skill not in thought['main_skill_constraint']:
                return False
        
        if 'random_skill_constraint' in thought:
            if random_cat.skill not in thought['random_skill_constraint']:
                return False

        if 'backstory_constraint' in thought:
            if main_cat.backstory not in thought['backstory_constraint']["m_c"]:
                return False
            if random_cat.backstory not in thought['backstory_constraint']["r_c"]:
                return False
        
        # Filter for the living status of the random cat. The living status of the main cat
        # is taken into account in the thought loading process. 
        if 'random_living_status' in thought:
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
        # this covers if living status isn't stated
        elif 'random_living_status' not in thought:
            if not random_cat.dead:
                living_status = "living"
            else:
                living_status = "dead"
            if living_status == "living":
                pass
            else:
                return False
            
        if 'random_outside_status' in thought:
            if random_cat.outside and random_cat.status not in ["kittypet", "loner", "rogue", "former Clancat", "exiled"]:
                outside_status = "lost"
            elif random_cat.outside:
                outside_status = "outside cat"
            else:
                outside_status = "clancat"
            if outside_status not in thought['random_outside_status']:
                return False
            
        if game_mode != "classic" and 'has_injuries' in thought:
            if "m_c" in thought['has_injuries']:
                if not ([i for i in main_cat.injuries if i in thought['has_injuries']["m_c"]] or [i for i in main_cat.illnesses if i in thought['has_injuries']["m_c"]]):
                    return False
            if "r_c" in thought['has_injuries']:
                if not ([i for i in random_cat.injuries if i in thought['has_injuries']["r_c"]] or [i for i in main_cat.illnesses if i in thought['has_injuries']["m_c"]]):
                    return False
        
        if game_mode != "classic" and "perm_conditions" in thought:
            if "m_c" in thought["perm_conditions"]:
                if not [i for i in main_cat.permanent_condition if i in thought["perm_conditions"]["m_c"]]:
                    return False
            if "r_c" in thought["perm_conditions"]:
                if not [i for i in random_cat.permanent_condition if i in thought["perm_conditions"]["r_c"]]:
                    return False

        return True
    # ---------------------------------------------------------------------------- #
    #                            BUILD MASTER DICTIONARY                           #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def create_thoughts(inter_list, main_cat, other_cat, game_mode, biome, season, camp) -> list:
        created_list = []
        for inter in inter_list:
            if Thoughts.cats_fulfill_thought_constraints(main_cat, other_cat, inter, game_mode, biome, season, camp):
                created_list.append(inter)
        return created_list

    @staticmethod
    def load_thoughts(main_cat, other_cat, game_mode, biome, season, camp):
        base_path = f"resources/dicts/thoughts/"
        life_dir = None
        status = main_cat.status
        loaded_thoughts = []

        if status == "medicine cat apprentice":
            status = "medicine_cat_apprentice"
        elif status == "mediator apprentice":
            status = "mediator_apprentice"
        elif status == "medicine cat":
            status = "medicine_cat"

        if not main_cat.dead:
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
        final_thoughts = Thoughts.create_thoughts(loaded_thoughts, main_cat, other_cat, game_mode, biome, season, camp)

        return final_thoughts
    
    @staticmethod
    def get_chosen_thought(main_cat, other_cat, game_mode, biome, season, camp):
        # get possible thoughts
        try:
            chosen_thought_group = choice(Thoughts.load_thoughts(main_cat, other_cat, game_mode, biome, season, camp))
            chosen_thought = choice(chosen_thought_group["thoughts"])
        except:
            chosen_thought = "No thoughts, head empty"

        return chosen_thought
