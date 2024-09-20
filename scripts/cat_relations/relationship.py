import random
from random import choice

from scripts.cat.history import History
from scripts.cat_relations.interaction import (
    SingleInteraction,
    NEUTRAL_INTERACTIONS,
    INTERACTION_MASTER_DICT,
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints,
)
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.utility import get_personality_compatibility, process_text


# ---------------------------------------------------------------------------- #
#                           START Relationship class                           #
# ---------------------------------------------------------------------------- #


class Relationship:
    used_interaction_ids = []

    def __init__(
        self,
        cat_from,
        cat_to,
        mates=False,
        family=False,
        romantic_love=0,
        platonic_like=0,
        dislike=0,
        admiration=0,
        comfortable=0,
        jealousy=0,
        trust=0,
        log=None,
    ) -> None:
        self.chosen_interaction = None
        self.history = History()
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposite_relationship = (
            None  # link to opposite relationship will be created later
        )
        self.interaction_str = ""
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
        # such interactions are only allowed for living Clan members
        if self.cat_from.dead or self.cat_from.outside or self.cat_from.exiled:
            return
        if self.cat_to.dead or self.cat_to.outside or self.cat_to.exiled:
            return

        # update relationship
        if self.cat_to.ID in self.cat_from.mate:
            self.mates = True

        # check if opposite_relationship is here, otherwise creates it
        if self.opposite_relationship is None:
            self.link_relationship()

        # get if the interaction is positive or negative for the relationship
        positive = self.positive_interaction()
        rel_type = self.get_interaction_type(positive)

        # check if an increase interaction or a decrease interaction
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
        game_mode = game.clan.game_mode

        all_interactions = NEUTRAL_INTERACTIONS.copy()
        if in_de_crease != "neutral":
            all_interactions = INTERACTION_MASTER_DICT[rel_type][in_de_crease].copy()
            possible_interactions = self.get_relevant_interactions(
                all_interactions, intensity, biome, season, game_mode
            )
        else:
            intensity = None
            possible_interactions = self.get_relevant_interactions(
                all_interactions, intensity, biome, season, game_mode
            )

        # return if there are no possible interactions.
        if len(possible_interactions) <= 0:
            print(
                "WARNING: No interaction with this conditions.",
                rel_type,
                in_de_crease,
                intensity,
            )
            return

        # check if the current interaction id is already used and us another if so
        chosen_interaction = choice(possible_interactions)
        while (
            chosen_interaction.id in self.used_interaction_ids
            and len(possible_interactions) > 2
        ):
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
        if self.chosen_interaction.get_injuries:
            injuries = []
            for (
                abbreviations,
                injury_dict,
            ) in self.chosen_interaction.get_injuries.items():
                if "injury_names" not in injury_dict:
                    print(
                        f"ERROR: there are no injury names in the chosen interaction {self.chosen_interaction.id}."
                    )
                    continue

                injured_cat = self.cat_from
                if abbreviations != "m_c":
                    injured_cat = self.cat_to

                for inj in injury_dict["injury_names"]:
                    injured_cat.get_injured(inj, True)
                    injuries.append(inj)

                possible_scar = (
                    self.adjust_interaction_string(injury_dict["scar_text"])
                    if "scar_text" in injury_dict
                    else None
                )
                possible_death = (
                    self.adjust_interaction_string(injury_dict["death_text"])
                    if "death_text" in injury_dict
                    else None
                )
                if injured_cat.status == "leader":
                    possible_death = (
                        self.adjust_interaction_string(injury_dict["death_leader_text"])
                        if "death_leader_text" in injury_dict
                        else None
                    )

                if possible_scar or possible_death:
                    for condition in injuries:
                        self.history.add_possible_history(
                            injured_cat,
                            condition,
                            scar_text=possible_scar,
                            death_text=possible_death,
                        )

        # get any possible interaction string out of this interaction
        interaction_str = choice(self.chosen_interaction.interactions)

        # prepare string for display
        interaction_str = self.adjust_interaction_string(interaction_str)

        effect = " (neutral effect)"
        if in_de_crease != "neutral" and positive:
            effect = f" ({intensity} positive effect)"
        if in_de_crease != "neutral" and not positive:
            effect = f" ({intensity} negative effect)"

        interaction_str = interaction_str + effect
        if self.cat_from.moons == 1:
            self.log.append(
                interaction_str
                + f" - {self.cat_from.name} was {self.cat_from.moons} moon old"
            )
        else:
            self.log.append(
                interaction_str
                + f" - {self.cat_from.name} was {self.cat_from.moons} moons old"
            )
        relevant_event_tabs = ["relation", "interaction"]
        if self.chosen_interaction.get_injuries:
            relevant_event_tabs.append("health")
        game.cur_events_list.append(
            Single_Event(
                interaction_str,
                ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID],
            )
        )

    def adjust_interaction_string(self, string):
        """Adjusts the string text for viewing"""

        cat_dict = {
            "m_c": (str(self.cat_from.name), choice(self.cat_from.pronouns)),
            "r_c": (str(self.cat_to.name), choice(self.cat_to.pronouns)),
        }

        return process_text(string, cat_dict)

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
            amount += game.config["relationship"]["compatibility_effect"]
        else:
            # negative compatibility
            amount -= game.config["relationship"]["compatibility_effect"]
        return amount

    def interaction_affect_relationships(
        self, in_de_crease: str, intensity: str, rel_type: str
    ) -> None:
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
        passive_buff = int(
            abs(amount / game.config["relationship"]["passive_influence_div"])
        )

        # influence the own relationship
        if rel_type == "romantic":
            self.complex_romantic(amount, passive_buff)
        elif rel_type == "platonic":
            self.complex_platonic(amount, passive_buff)
        elif rel_type == "dislike":
            self.complex_dislike(amount, passive_buff)
        elif rel_type == "admiration":
            self.complex_admiration(amount, passive_buff)
        elif rel_type == "comfortable":
            self.complex_comfortable(amount, passive_buff)
        elif rel_type == "jealousy":
            self.complex_jealousy(amount, passive_buff)
        elif rel_type == "trust":
            self.complex_trust(amount, passive_buff)

        # influence the opposite relationship
        if self.opposite_relationship is None:
            return

        rel_dict = self.chosen_interaction.reaction_random_cat
        if rel_dict:
            self.opposite_relationship.change_according_dictionary(rel_dict)

        rel_dict = self.chosen_interaction.also_influences
        if rel_dict:
            self.change_according_dictionary(rel_dict)

    def change_according_dictionary(self, dictionary: dict) -> None:
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
        list_to_choice += [True] * int(self.platonic_like / 10)
        list_to_choice += [False] * int(self.dislike / 10)

        return choice(list_to_choice)

    def get_interaction_type(self, positive: bool) -> str:
        """Returns the type of the interaction which should be made.

        Parameters
        ----------
        positive : bool
            if the event has a positive or negative impact of the relationship,
            this defines which weight will be used to get the type of the interaction

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
            "romantic": 1,
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
        mate_from_to = self.cat_from.is_potential_mate(
            self.cat_to, for_love_interest=True
        )
        mate_to_from = self.cat_to.is_potential_mate(
            self.cat_from, for_love_interest=True
        )
        if (not mate_from_to or not mate_to_from) and not self.mates:
            while "romantic" in types:
                types.remove("romantic")

        rel_type = choice(types)
        return rel_type

    def get_relevant_interactions(
        self,
        interactions: list,
        intensity: str,
        biome: str,
        season: str,
        game_mode: str,
    ) -> list:
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
            game_mode : str
                game mode of the clan

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
            in_tags = list(
                filter(
                    lambda interact_biome: interact_biome not in _biome, interact.biome
                )
            )
            if len(in_tags) > 0:
                continue

            in_tags = list(
                filter(
                    lambda interact_season: interact_season not in _season,
                    interact.season,
                )
            )
            if len(in_tags) > 0:
                continue

            if intensity is not None and interact.intensity != intensity:
                continue

            cats_fulfill_conditions = cats_fulfill_single_interaction_constraints(
                self.cat_from, self.cat_to, interact, game_mode
            )
            if not cats_fulfill_conditions:
                continue

            relationship_fulfill_conditions = rel_fulfill_rel_constraints(
                self, interact.relationship_constraint, interact.id
            )
            if not relationship_fulfill_conditions:
                continue

            filtered.append(interact)

        return filtered

    # ---------------------------------------------------------------------------- #
    #                            complex value addition                            #
    # ---------------------------------------------------------------------------- #

    # How increasing/decreasing one state influences another directly
    # (an increase of one state doesn't trigger a chain reaction)

    # increase romantic_love -> decreases: dislike | increases: like, comfortable
    # decrease romantic_love -> decreases: comfortable | increases: -

    # increase like -> decreases: dislike | increases: comfortable
    # decrease like -> increases: dislike | decreases: comfortable

    # increase dislike -> decreases: romantic_love, like | increases: -
    # decrease dislike -> increases: like, comfortable | decreases: -

    # increase admiration -> decreases: - | increases: trust
    # decrease admiration -> increases: dislike | decreases: trust

    # increase comfortable -> decreases: jealousy, dislike | increases: trust, like
    # decrease comfortable -> increases: jealousy, dislike | decreases: trust, like

    # increase jealousy -> decreases: - | increases: dislike
    # decrease jealousy -> increases: comfortable | decreases: -

    # increase trust -> decreases: dislike | increases: comfortable
    # decrease trust -> increases: dislike | decreases: comfortable

    def complex_romantic(self, value, buff):
        """Add the value to the romantic type and influence other value types as well."""
        self.romantic_love += value
        if value > 0:
            self.platonic_like += buff
            self.comfortable += buff
            self.dislike -= buff
        if value < 0:
            self.comfortable -= buff

    def complex_platonic(self, value, buff):
        """Add the value to the platonic type and influence other value types as well."""
        self.platonic_like += value
        if value > 0:
            self.comfortable += buff
            self.dislike -= buff
        if value < 0:
            self.comfortable -= buff
            self.dislike += buff

    def complex_dislike(self, value, buff):
        """Add the value to the dislike type and influence other value types as well."""
        self.dislike += value
        if value > 0:
            self.romantic_love -= buff
            self.platonic_like -= buff
        if value < 0:
            self.platonic_like += buff
            self.comfortable += buff

    def complex_admiration(self, value, buff):
        """Add the value to the admiration type and influence other value types as well."""
        self.admiration += value
        if value > 0:
            self.trust += buff
        if value < 0:
            self.trust -= buff
            self.dislike += buff

    def complex_comfortable(self, value, buff):
        """Add the value to the comfortable type and influence other value types as well."""
        self.comfortable += value
        if value > 0:
            self.trust += buff
            self.platonic_like += buff
            self.dislike -= buff
            self.jealousy -= buff
        if value < 0:
            self.trust -= buff
            self.platonic_like -= buff
            self.dislike += buff

    def complex_jealousy(self, value, buff):
        """Add the value to the jealousy type and influence other value types as well."""
        self.jealousy += value
        if value > 0:
            self.dislike += buff
        if value < 0:
            self.comfortable += buff

    def complex_trust(self, value, buff):
        """Add the value to the trust type and influence other value types as well."""
        self.trust += value
        if value > 0:
            self.comfortable += buff
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
