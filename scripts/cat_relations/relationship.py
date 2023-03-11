import os
import random
from random import choice
try:
    import ujson
except ImportError:
    import json as ujson
from scripts.event_class import Single_Event

from scripts.utility import get_personality_compatibility
from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                           START Relationship class                           #
# ---------------------------------------------------------------------------- #

class Relationship():
    used_interaction_ids = []

    def __init__(self, cat_from, cat_to, mates=False, family=False, romantic_love=0, platonic_like=0, dislike=0,
                 admiration=0, comfortable=0, jealousy=0, trust=0, log=None) -> None:
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposite_relationship = None  # link to opposite relationship will be created later
        self.interaction_str = ''
        self.triggered_event = False
        if log:
            self.log = log
        else:
            self.log = []

        # each stat can go from 0 to 100
        self.romantic_love = romantic_love
        self.platonic_like = platonic_like
        self.dislike = dislike
        self.admiration = admiration
        self.comfortable = comfortable
        self.jealousy = jealousy
        self.trust = trust

    def link_relationship(self):
        """Add the other relationship object to this easily access and change the other side."""
        if self.cat_from.ID in self.cat_to.relationships:
            self.opposite_relationship = self.cat_to.relationships[self.cat_from.ID]
        else:
            # create relationship
            relation = Relationship(self.cat_to, self.cat_from)
            self.cat_to.relationships[self.cat_from.ID] = relation
            self.opposite_relationship = relation

    def start_interaction(self) -> None:
        """This function handles the simple interaction of this relationship."""
        # such interactions are only allowed for living clan members
        if self.cat_from.dead or self.cat_from.outside or self.cat_from.exiled:
            return
        if self.cat_to.dead or self.cat_to.outside or self.cat_to.exiled:
            return

        # update relationship
        if self.cat_from.mate == self.cat_to.ID:
            self.mates = True

        # check if opposite_relationship is here, otherwise creates it
        if self.opposite_relationship is None:
            self.link_relationship()

        # get if the interaction is positive or negative for the relationship
        positive = self.positive_interaction()
        rel_type = self.get_interaction_type(positive)

        # look if an increase interaction or an decrease interaction
        in_de_crease = "increase" if positive else "decrease"
        # if the type is jealousy or dislike, then increase and decrease has to be turned around
        if rel_type in ["jealousy", "dislike"]:
            in_de_crease = "decrease" if positive else "increase"

        chance = game.config["relationship"]["chance_for_neutral"]
        if chance == 1:
            in_de_crease = "neutral"
        elif chance > 1 and random.randint(1, chance) == 1:
            in_de_crease = "neutral"

        # choice any type of intensity
        intensity = choice(["low", "medium", "high"])

        # get other possible filters
        season = str(game.clan.current_season).casefold()
        biome = str(game.clan.biome).casefold()

        all_interactions = NEUTRAL_INTERACTIONS.copy()
        if in_de_crease != "neutral":
            all_interactions = INTERACTION_MASTER_DICT[rel_type][in_de_crease].copy()
            possible_interactions = self.get_relevant_interactions(all_interactions, intensity, biome, season)
        else:
            possible_interactions = all_interactions

        if len(possible_interactions) <= 0:
            print("ERROR: No interaction with this conditions. ", rel_type, in_de_crease, intensity)
            possible_interactions = [
                Single_Interaction("fall_back", "Any", "Any", "medium", [
                    "Default string, this should never appear."
                ])
            ]

        # check if the current interaction id is already used and us another if so
        chosen_interaction = choice(possible_interactions)
        while chosen_interaction.id in self.used_interaction_ids\
            and len(possible_interactions) > 2:
            possible_interactions.remove(chosen_interaction)
            chosen_interaction = choice(possible_interactions)

        # if the chosen_interaction is still in the TRIGGERED_SINGLE_INTERACTIONS, clean the list
        if chosen_interaction in self.used_interaction_ids:
            self.used_interaction_ids = []

        # add the chosen interaction id to the TRIGGERED_SINGLE_INTERACTIONS
        self.chosen_interaction = chosen_interaction
        self.used_interaction_ids.append(self.chosen_interaction.id)

        self.interaction_affect_relationships(in_de_crease, intensity, rel_type)
        # give cats injuries
        if len(self.chosen_interaction.injuries) > 0:
            for abbreviations, injuries in self.chosen_interaction.injuries.items():
                injured_cat = self.cat_from
                if abbreviations != "m_c":
                    injured_cat = self.cat_to
                
                for inj in injuries:
                    injured_cat.get_injured(inj, True)
        
        # get any possible interaction string out of this interaction
        interaction_str = choice(self.chosen_interaction.interactions)

        # prepare string for display
        interaction_str = interaction_str.replace("m_c", str(self.cat_from.name))
        interaction_str = interaction_str.replace("r_c", str(self.cat_to.name))

        effect = " (neutral effect)"
        if in_de_crease != "neutral" and positive:
            effect = f" ({intensity} positive effect)"
        if in_de_crease != "neutral" and not positive:
            effect = f" ({intensity} negative effect)"

        interaction_str = interaction_str + effect
        self.log.append(interaction_str)
        game.cur_events_list.append(Single_Event(
            interaction_str, ["relation", "interaction"], [self.cat_to.ID, self.cat_from.ID]
        ))

    def get_amount(self, in_de_crease: str, intensity: str) -> int:
        """Calculates the amount of such an interaction.

            Parameters
            ----------
            in_de_crease : list
                if the relationship value is increasing or decreasing the value
            intensity : str
                the intensity of the affect

            Returns
            -------
            amount : int
                the amount (negative or positive) for the given parameter
        """
        if in_de_crease == "neutral":
            return 0
        # get the normal amount
        amount = game.config["relationship"]["in_decrease_value"][intensity]
        if in_de_crease == "decrease":
            amount = amount * -1

        # take compatibility into account
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            # neutral compatibility
            amount = amount
        elif compatibility:
            # positive compatibility
            amount += game.config["relationship"]["compatibility_bonus"]
        else:
            # negative compatibility
            amount -= game.config["relationship"]["compatibility_bonus"]
        return amount

    def interaction_affect_relationships(self, in_de_crease: str, intensity: str, rel_type: str) -> None:
        """Affects the relationship according to the chosen types.

            Parameters
            ----------
            in_de_crease : list
                if the relationship value is increasing or decreasing the value
            intensity : str
                the intensity of the affect
            rel_type : str
                relationship value type which needs to be affected

            Returns
            -------
        """
        amount = self.get_amount(in_de_crease, intensity)

        # influence the own relationship
        if rel_type == "romantic":
            self.complex_romantic(amount)
        elif rel_type == "platonic":
            self.complex_platonic(amount)
        elif rel_type == "dislike":
            self.complex_dislike(amount)
        elif rel_type == "admiration":
            self.complex_admiration(amount)
        elif rel_type == "comfortable":
            self.complex_comfortable(amount)
        elif rel_type == "jealousy":
            self.complex_jealousy(amount)
        elif rel_type == "trust":
            self.complex_trust(amount)

        # influence the opposite relationship
        if self.opposite_relationship is None:
            return

        rel_dict = self.chosen_interaction.reaction_random_cat
        if rel_dict:
            self.opposite_relationship.change_according_dictionary(rel_dict)

        rel_dict = self.chosen_interaction.also_influences
        if rel_dict:
            self.change_according_dictionary(rel_dict)

    def change_according_dictionary(self, dictionary : dict) -> None:
        """Change the relationship value types according to the in- or decrease of the given dictionary.

            Parameters
            ----------
            dictionary : dict
                dictionary which defines the changes to the relationship

            Returns
            -------
        """
        for key, value in dictionary.items():
            if value == "neutral":
                continue
            amount = self.get_amount(value, "low")

            if key == "romantic":
                self.romantic_love += amount
            elif key == "platonic":
                self.platonic_like += amount
            elif key == "dislike":
                self.dislike += amount
            elif key == "admiration":
                self.admiration += amount
            elif key == "comfortable":
                self.comfortable += amount
            elif key == "jealousy":
                self.jealousy += amount
            elif key == "trust":
                self.trust += amount

    def positive_interaction(self) -> bool:
        """Returns if the interaction should be a positive interaction or not.

            Parameters
            ----------

            Returns
            -------
            positive : bool
                if the event has a positive or negative impact of the relationship

        """
        # base for non-existing platonic like / dislike
        list_to_choice = [True, True, False]

        # take personality in count
        comp = get_personality_compatibility(self.cat_from, self.cat_to)
        if comp is not None:
            list_to_choice.append(comp)

        # further influence the partition based on the relationship
        list_to_choice += [True] * int(self.platonic_like/10)
        list_to_choice += [False] * int(self.dislike/10)

        return choice(list_to_choice)

    def get_interaction_type(self, positive: bool) ->  str:
        """Returns the type of the interaction which should be made.
        
            Parameters
            ----------
            positive : bool
                if the event has a positive or negative impact of the relationship, 
                this define which weight will be used to get the type of the interaction

            Returns
            -------
            rel_type : string
                the relationship type which will happen
        """
        value_weights = {
            "trust": 1,
            "jealousy": 1,
            "comfortable": 1,
            "admiration": 1,
            "dislike": 1,
            "platonic": 1,
            "romantic": 1
        }

        # change the weights according if the interaction should be positive or negative
        if positive:
            value_weights["platonic"] += 1
        else:
            value_weights["dislike"] += 1
            value_weights["jealousy"] += 1

        # increase the chance of a romantic interaction if there already mates
        if self.mates:
            value_weights["romantic"] += 1

        # create the list of choices
        types = []
        for rel_type, weight in value_weights.items():
            types += [rel_type] * weight

        # if a romantic relationship is not possible, remove this type, mut only if there are no mates
        # if there already mates (set up by the user for example), don't remove this type
        mate_from_to = self.cat_from.is_potential_mate(self.cat_to, True)
        mate_to_from = self.cat_to.is_potential_mate(self.cat_from, True)
        if (not mate_from_to or not mate_to_from) and not self.mates:
            while "romantic" in types:
                types.remove("romantic")

        rel_type = choice(types)
        return rel_type

    def get_relevant_interactions(self, interactions : list, intensity : str, biome : str, season : str) -> list:
        """
        Filter interactions based on the status and other constraints.
            
            Parameters
            ----------
            interactions : list
                the interactions which need to be filtered
            intensity : str
                the intensity of the interactions
            biome : str
                biome of the clan
            season : str
                current season of the clan

            Returns
            -------
            filtered : list
                a list of interactions, which fulfill the criteria
        """
        filtered = []
        _season = [season, "Any", "any"]
        _biome = [biome, "Any", "any"]
        # if there are no loaded interactions, return empty list
        if not interactions:
            return filtered

        for interact in interactions:
            in_tags = list(filter(lambda biome: biome not in _biome, interact.biome))
            if len(in_tags) > 0:
                continue

            in_tags = list(filter(lambda season: season not in _season, interact.season))
            if len(in_tags) > 0:
                continue

            if interact.intensity != intensity:
                continue

            if len(interact.main_status_constraint) >= 1:
                if self.cat_from.status not in interact.main_status_constraint:
                    continue

            if len(interact.random_status_constraint) >= 1:
                if self.cat_to.status not in interact.random_status_constraint:
                    continue

            if len(interact.main_trait_constraint) >= 1:
                if self.cat_from.trait not in interact.main_trait_constraint:
                    continue

            if len(interact.random_trait_constraint) >= 1:
                if self.cat_to.trait not in interact.random_trait_constraint:
                    continue

            if len(interact.main_skill_constraint) >= 1:
                if self.cat_from.skill not in interact.main_skill_constraint:
                    continue

            if len(interact.random_skill_constraint) >= 1:
                if self.cat_to.skill not in interact.random_skill_constraint:
                    continue

            # if there is no constraint, skip other checks
            if len(interact.relationship_constraint) == 0:
                filtered.append(interact)
                continue

            if "siblings" in interact.relationship_constraint and not self.cat_from.is_sibling(self.cat_to):
                continue

            if "mates" in interact.relationship_constraint and not self.mates:
                continue

            if "not_mates" in interact.relationship_constraint and self.mates:
                continue

            if "parent/child" in interact.relationship_constraint and not self.cat_from.is_parent(self.cat_to):
                continue

            if "child/parent" in interact.relationship_constraint and not self.cat_to.is_parent(self.cat_from):
                continue

            value_types = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
            fulfilled = True
            for v_type in value_types:
                tags = list(filter(lambda constr: v_type in constr, interact.relationship_constraint))
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
                    print(f"ERROR: interaction {interact.id} with the relationship constraint for the value {v_type} follows not the formatting guidelines.")
                    break

                if threshold > 100:
                    print(f"ERROR: interaction {interact.id} has a relationship constraints for the value {v_type}, which is higher than the max value of a relationship.")
                    break

                if threshold <= 0:
                    print(f"ERROR: patrol {interact.id} has a relationship constraints for the value {v_type}, which is lower than the min value of a relationship or 0.")
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

            if fulfilled:
                filtered.append(interact)

        return filtered


    # ---------------------------------------------------------------------------- #
    #                            complex value addition                            #
    # ---------------------------------------------------------------------------- #

    # How increasing one state influences another directly: (an increase of one state doesn't trigger a chain reaction)
    # increase romantic_love -> decreases: dislike | increases: like, comfortable
    # increase like -> decreases: dislike | increases: comfortable
    # increase dislike -> decreases: romantic_love, like | increases: -
    # increase admiration -> decreases: - | increases: -
    # increase comfortable -> decreases: jealousy, dislike | increases: trust, like
    # increase jealousy -> decreases: - | increases: dislike
    # increase trust -> decreases: dislike | increases: -

    # !! DECREASING ONE STATE DOES'T INFLUENCE OTHERS !!

    def complex_romantic(self, value):
        """Add the value to the romantic type and influence other value types as well."""
        self.romantic_love += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.platonic_like += buff
            self.comfortable += buff
            self.dislike -= buff

    def complex_platonic(self, value):
        """Add the value to the platonic type and influence other value types as well."""
        self.platonic_like += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.comfortable += buff
            self.dislike -= buff

    def complex_dislike(self, value):
        """Add the value to the dislike type and influence other value types as well."""
        self.dislike += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.romantic_love -= buff
            self.platonic_like -= buff

    def complex_admiration(self, value):
        """Add the value to the admiration type and influence other value types as well."""
        self.admiration += value

    def complex_comfortable(self, value):
        """Add the value to the comfortable type and influence other value types as well."""
        self.comfortable += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.trust += buff
            self.platonic_like += buff
            self.dislike -= buff
            self.jealousy -= buff

    def complex_jealousy(self, value):
        """Add the value to the jealousy type and influence other value types as well."""
        self.jealousy += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.dislike += buff

    def complex_trust(self, value):
        """Add the value to the trust type and influence other value types as well."""
        self.trust += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.dislike -= buff


    # ---------------------------------------------------------------------------- #
    #                                   property                                   #
    # ---------------------------------------------------------------------------- #

    @property
    def romantic_love(self):
        return self._romantic_love

    @romantic_love.setter
    def romantic_love(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._romantic_love = value

    @property
    def platonic_like(self):
        return self._platonic_like

    @platonic_like.setter
    def platonic_like(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._platonic_like = value

    @property
    def dislike(self):
        return self._dislike

    @dislike.setter
    def dislike(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._dislike = value

    @property
    def admiration(self):
        return self._admiration

    @admiration.setter
    def admiration(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._admiration = value

    @property
    def comfortable(self):
        return self._comfortable

    @comfortable.setter
    def comfortable(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._comfortable = value

    @property
    def jealousy(self):
        return self._jealousy

    @jealousy.setter
    def jealousy(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._jealousy = value

    @property
    def trust(self):
        return self._trust

    @trust.setter
    def trust(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._trust = value


# ---------------------------------------------------------------------------- #
#                          needed interaction classes                          #
# ---------------------------------------------------------------------------- #

class Single_Interaction():

    def __init__(self,
                 id,
                 biome=None,
                 season=None,
                 intensity="medium",
                 interactions=None,
                 injuries=None,
                 relationship_constraint=None,
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

