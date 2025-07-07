import random
from random import choice
from typing import Optional

import i18n

import scripts.cat_relations.interaction as interactions
from scripts.cat.history import History
from scripts.cat_relations.interaction import (
    cats_fulfill_single_interaction_constraints,
    rebuild_relationship_dicts,
)
from scripts.cat_relations.enums import ValueLevel, RelValue
from scripts.event_class import Single_Event
from scripts.events_module.event_filters import event_for_location, event_for_season
from scripts.game_structure.game_essentials import game
from scripts.utility import get_personality_compatibility, process_text


# ---------------------------------------------------------------------------- #
#                           START Relationship class                           #
# ---------------------------------------------------------------------------- #


class Relationship:
    used_interaction_ids = []
    currently_loaded_lang = None

    def __init__(
        self,
        cat_from,
        cat_to,
        mates: bool = False,
        family: bool = False,
        romance: int = 0,
        like: int = 0,
        respect: int = 0,
        trust: int = 0,
        comfort: int = 0,
        log: list = None,
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

        # romance operates on a 0-100 scale, 0 is no romantic interest and 100 is full romantic interest
        self.romance = romance

        # each stat can go from -100 to 100
        # negative numbers are the negative state while positive is the positive state
        self.like = like
        self.respect = respect
        self.trust = trust
        self.comfort = comfort

    def to_dict(self):
        return {
            "cat_from_id": self.cat_from.ID,
            "cat_to_id": self.cat_to.ID,
            "mates": self.mates,
            "family": self.family,
            "romance": self.romance,
            "like": self.like,
            "respect": self.respect,
            "comfort": self.comfort,
            "trust": self.trust,
            "log": self.log,
        }

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
        if self.cat_from.ID == self.cat_to.ID:
            return

        if self.currently_loaded_lang != i18n.config.get("locale"):
            Relationship.currently_loaded_lang = i18n.config.get("locale")
            rebuild_relationship_dicts()

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
        value_change = "increase" if positive else "decrease"

        # choose any type of intensity
        intensity = random.choices(("low", "medium", "high"), weights=[4, 3, 2])[0]

        all_interactions = interactions.INTERACTION_MASTER_DICT[rel_type][
            value_change
        ].copy()

        possible_interactions = self.get_relevant_interactions(
            all_interactions, intensity
        )

        # return if there are no possible interactions.
        if not possible_interactions:
            print(
                "WARNING: No interaction with this conditions.",
                rel_type,
                value_change,
                intensity,
            )
            return

        # check if the current interaction id is already used and use another if so
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

        self.interaction_affect_relationships(value_change, intensity, rel_type)
        # give cats injuries
        # TODO: the moment we can include more than 3 cats in a short event, this should get removed
        # it only exists for one rel event, iirc, and that event is far more suited to being an injury short event
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

        effect = ""
        if value_change == "increase":
            effect = i18n.t(f"relationships.positive_postscript_{intensity}")
        elif value_change == "decrease":
            effect = i18n.t(f"relationships.negative_postscript_{intensity}")

        interaction_str = interaction_str + effect
        self.log.append(
            interaction_str
            + i18n.t(
                "relationships.age_postscript",
                name=str(self.cat_from.name),
                count=self.cat_from.moons,
            )
        )
        relevant_event_tabs = ["relation", "interaction"]
        if self.chosen_interaction.get_injuries:
            relevant_event_tabs.append("health")
        game.cur_events_list.append(
            Single_Event(
                interaction_str,
                ["relation", "interaction"],
                cat_dict={"m_c": self.cat_to, "r_c": self.cat_from},
            )
        )

    def adjust_interaction_string(self, string):
        """Adjusts the string text for viewing"""

        cat_dict = {
            "m_c": (str(self.cat_from.name), choice(self.cat_from.pronouns)),
            "r_c": (str(self.cat_to.name), choice(self.cat_to.pronouns)),
        }

        return process_text(string, cat_dict)

    def get_value_change_amount(self, value_change: str, intensity: str) -> int:
        """Calculates the amount of such an interaction.

        Parameters
        ----------
        value_change : str
            if the relationship value is increasing or decreasing the value
        intensity : str
            the intensity of the affect

        Returns
        -------
        amount : int
            the amount (negative or positive) for the given parameter
        """
        # get the normal amount
        amount = game.config["relationship"]["value_change_amount"][intensity]
        if value_change == "decrease":
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
        self, value_change: str, intensity: str, rel_type: str
    ) -> None:
        """Affects the relationship according to the chosen types.

        Parameters
        ----------
        value_change : str
            if the relationship value is increasing or decreasing the value
        intensity : str
            the intensity of the affect
        rel_type : str
            relationship value type which needs to be affected

        Returns
        -------
        """
        amount = self.get_value_change_amount(value_change, intensity)
        passive_buff = int(
            amount / game.config["relationship"]["passive_influence_div"]
        )
        # just adding a teeny bit of variety
        buffs = [passive_buff - 1, passive_buff, passive_buff + 1]

        # the passive buff creates a cascade affect
        # so a negative interaction will affect all values to a negative degree
        # and a positive interaction will affect all values to a positive degree

        if rel_type != RelValue.LIKE:
            self.like += choice(buffs)
        else:
            self.like += amount

        if rel_type != RelValue.RESPECT:
            self.respect += choice(buffs)
        else:
            self.respect += amount

        if rel_type != RelValue.TRUST:
            self.trust += choice(buffs)
        else:
            self.trust += amount

        if rel_type != RelValue.COMFORT:
            self.comfort += choice(buffs)
        else:
            self.comfort += amount

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
            amount = self.get_value_change_amount(value, "low")

            if key == RelValue.ROMANCE:
                self.romance += amount
            elif key == RelValue.LIKE:
                self.like += amount
            elif key == RelValue.RESPECT:
                self.respect += amount
            elif key == RelValue.COMFORT:
                self.comfort += amount
            elif key == RelValue.TRUST:
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
        # base for non-existing like
        bool_ballot = [True, True, False]

        # take personality in count
        comp = get_personality_compatibility(self.cat_from, self.cat_to)
        if comp is not None:
            bool_ballot.append(comp)

        # further influence the partition based on the relationship
        for value in (self.like, self.respect, self.comfort, self.trust):
            # each 10th above 100 adds another True
            if value > 0:
                bool_ballot += [True] * int(value / 10)
            # each 10th below 100
            else:
                bool_ballot += [False] * int(abs(value) / 10)

        return choice(bool_ballot)

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

        value_weights = {v: 1 for v in [*RelValue]}

        # change the weights according if the interaction should be positive or negative
        # existing rel values determine the weight added
        if positive:
            if self.like > 0:
                value_weights[RelValue.LIKE] += int(self.like / 10)
            if self.respect > 0:
                value_weights[RelValue.RESPECT] += int(self.respect / 10)
            if self.comfort > 0:
                value_weights[RelValue.COMFORT] += int(self.comfort / 10)
            if self.trust > 0:
                value_weights[RelValue.TRUST] += int(self.trust / 10)
            if self.romance > 0:
                value_weights[RelValue.ROMANCE] += int(self.romance / 10)
        else:
            if self.like < 0:
                value_weights[RelValue.LIKE] += int(abs(self.like) / 10)
            if self.respect < 0:
                value_weights[RelValue.RESPECT] += int(abs(self.respect) / 10)
            if self.comfort < 0:
                value_weights[RelValue.COMFORT] += int(abs(self.comfort) / 10)
            if self.trust < 0:
                value_weights[RelValue.TRUST] += int(abs(self.trust) / 10)

        # increase the chance of a romance interaction if they are already mates
        if self.mates:
            value_weights[RelValue.ROMANCE] += 1

        # if a romance relationship is not possible, remove this type, mut only if there are no mates
        # if there already mates (set up by the user for example), don't remove this type
        mate_from_to = self.cat_from.is_potential_mate(
            self.cat_to, for_love_interest=True
        )
        mate_to_from = self.cat_to.is_potential_mate(
            self.cat_from, for_love_interest=True
        )
        if (not mate_from_to or not mate_to_from) and not self.mates:
            while RelValue.ROMANCE in value_weights:
                value_weights.pop(RelValue.ROMANCE)

        # if cats have no romance relationship already, don't allow romance decrease
        if (
            not positive
            and RelValue.ROMANCE in value_weights
            and not self.cat_from.relationships[self.cat_to.ID].romance
        ):
            value_weights.pop(RelValue.ROMANCE)

        chosen_type = random.choices(
            [value for value in value_weights.keys()],
            [weight for weight in value_weights.values()],
        )[0]
        return chosen_type

    def get_relevant_interactions(
        self,
        possible_interactions: list,
        intensity: str = None,
    ) -> list:
        """
        Filter interactions based on the status and other constraints.

            Parameters
            ----------
            possible_interactions : list
                the interactions which need to be filtered
            intensity : str
                the intensity of the interactions

            Returns
            -------
            filtered : list
                a list of interactions, which fulfill the criteria
        """
        filtered = []
        # if there are no loaded interactions, return empty list
        if not possible_interactions:
            return filtered

        for interact in possible_interactions:
            if not event_for_location(interact.biome):
                continue

            if not event_for_season(interact.season):
                continue

            if intensity is not None and interact.intensity != intensity:
                continue

            cats_fulfill_conditions = cats_fulfill_single_interaction_constraints(
                self.cat_from, self.cat_to, interact
            )
            if not cats_fulfill_conditions:
                continue

            filtered.append(interact)

        return filtered

    def get_amount_of_value(self, value_enum: RelValue) -> Optional[int]:
        if value_enum == RelValue.ROMANCE:
            return self.romance
        elif value_enum == RelValue.LIKE:
            return self.like
        elif value_enum == RelValue.RESPECT:
            return self.respect
        elif value_enum == RelValue.COMFORT:
            return self.comfort
        elif value_enum == RelValue.TRUST:
            return self.trust
        else:
            return None

    def get_value_levels(self) -> list[ValueLevel]:
        """
        Returns a list of all current value level strings
        """
        return [
            self.romance_level,
            self.like_level,
            self.trust_level,
            self.comfort_level,
            self.respect_level,
        ]

    def total_value_amount(self) -> int:
        """
        Returns the total int of all relationship values.
        """
        return self.romance + self.like + self.respect + self.comfort + self.trust

    def has_extreme_negative(self) -> bool:
        """
        Returns True if the relationship has an extreme negative value.
        """
        if [l for l in self.get_value_levels() if l.is_extreme_neg()]:
            return True

        return False

    def has_extreme_positive(self) -> bool:
        """
        Returns True if the relationship has an extreme positive value.
        """
        if [l for l in self.get_value_levels() if l.is_extreme_pos()]:
            return True

        return False

    def is_empty(self) -> bool:
        return (
            self.romance_level.is_neutral()
            and self.trust_level.is_neutral()
            and self.like_level.is_neutral()
            and self.comfort_level.is_neutral()
            and self.respect_level.is_neutral()
        )

    @property
    def romance(self) -> int:
        """0-100 scale, 0 is no romantic interest and 100 is full romantic interest"""
        return self._romance

    @romance.setter
    def romance(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._romance = value

    @property
    def romance_level(self) -> Optional[ValueLevel]:
        group = self._get_level_group(self.romance)

        if group == "neutral":
            return ValueLevel.UNINTERESTED
        elif group == "low_pos":
            return ValueLevel.FANCIES
        elif group == "mid_pos":
            return ValueLevel.ADORES
        elif group == "extreme_pos":
            return ValueLevel.LOVES
        else:
            return None

    @property
    def like(self) -> int:
        return self._like

    @like.setter
    def like(self, value):
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        self._like = value

    @property
    def like_level(self) -> Optional[ValueLevel]:
        group = self._get_level_group(self.like)

        if group == "extreme_neg":
            return ValueLevel.LOATHES
        elif group == "mid_neg":
            return ValueLevel.HATES
        elif group == "low_neg":
            return ValueLevel.DISLIKES
        elif group == "neutral":
            return ValueLevel.KNOWS_OF
        elif group == "low_pos":
            return ValueLevel.LIKES
        elif group == "mid_pos":
            return ValueLevel.ENJOYS
        elif group == "extreme_pos":
            return ValueLevel.CHERISHES
        else:
            return None

    @property
    def respect(self) -> int:
        return self._respect

    @respect.setter
    def respect(self, value):
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        self._respect = value

    @property
    def respect_level(self) -> Optional[ValueLevel]:
        group = self._get_level_group(self.respect)

        if group == "extreme_neg":
            return ValueLevel.RESENTS
        elif group == "mid_neg":
            return ValueLevel.ENVIES
        elif group == "low_neg":
            return ValueLevel.BEGRUDGES
        elif group == "neutral":
            return ValueLevel.ACKNOWLEDGES
        elif group == "low_pos":
            return ValueLevel.PRAISES
        elif group == "mid_pos":
            return ValueLevel.RESPECTS
        elif group == "extreme_pos":
            return ValueLevel.ADMIRES
        else:
            return None

    @property
    def comfort(self) -> int:
        return self._comfort

    @comfort.setter
    def comfort(self, value):
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        self._comfort = value

    @property
    def comfort_level(self) -> Optional[ValueLevel]:
        group = self._get_level_group(self.comfort)

        if group == "extreme_neg":
            return ValueLevel.RUNS_FROM
        elif group == "mid_neg":
            return ValueLevel.FEARS
        elif group == "low_neg":
            return ValueLevel.AVOIDS
        elif group == "neutral":
            return ValueLevel.CONSIDERS
        elif group == "low_pos":
            return ValueLevel.RELATES_TO
        elif group == "mid_pos":
            return ValueLevel.UNDERSTANDS
        elif group == "extreme_pos":
            return ValueLevel.KNOWS_DEEPLY
        else:
            return None

    @property
    def trust(self) -> int:
        return self._trust

    @trust.setter
    def trust(self, value):
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        self._trust = value

    @property
    def trust_level(self) -> Optional[ValueLevel]:
        group = self._get_level_group(self.trust)

        if group == "extreme_neg":
            return ValueLevel.LOATHES
        elif group == "mid_neg":
            return ValueLevel.DISTRUSTS
        elif group == "low_neg":
            return ValueLevel.DOUBTS
        elif group == "neutral":
            return ValueLevel.OBSERVES
        elif group == "low_pos":
            return ValueLevel.LISTENS_TO
        elif group == "mid_pos":
            return ValueLevel.TRUSTS
        elif group == "extreme_pos":
            return ValueLevel.CONFIDES_IN
        else:
            return None

    @staticmethod
    def _get_level_group(value) -> str:
        """
        Returns the level group for the given value.
        """
        found_group = None
        for group, interval in game.config["relationship"]["value_intervals"].items():
            if value <= interval:
                found_group = group
                break
        return found_group
