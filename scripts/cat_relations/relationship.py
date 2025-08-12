import random
from random import choice
from typing import Optional

import i18n

from scripts.game_structure import constants
from scripts.cat_relations.interaction import (
    cats_fulfill_single_interaction_constraints,
    rebuild_relationship_dicts,
)
from scripts.cat_relations.enums import RelTier, RelType
from scripts.event_class import Single_Event
from scripts.events_module.event_filters import event_for_location, event_for_season
from scripts.game_structure.game_essentials import game
from scripts.utility import get_personality_compatibility, process_text
import scripts.cat_relations.interaction as interactions


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
        if not self.cat_from.status.alive_in_player_clan:
            return
        if not self.cat_to.status.alive_in_player_clan:
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

        # choose any type of intensity
        intensity = random.choices(("low", "medium", "high"), weights=[4, 3, 2])[0]

        all_interactions = interactions.INTERACTION_MASTER_DICT[rel_type][
            "increase" if positive else "decrease"
        ].copy()

        possible_interactions = self.get_relevant_interactions(
            all_interactions, intensity
        )

        # return if there are no possible interactions.
        if not possible_interactions:
            print(
                "WARNING: No interaction with this conditions.",
                rel_type,
                positive,
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

        self.interaction_affect_relationships(positive, intensity, rel_type)
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
                if injured_cat.status.is_leader:
                    possible_death = (
                        self.adjust_interaction_string(injury_dict["death_leader_text"])
                        if "death_leader_text" in injury_dict
                        else None
                    )

                if possible_scar or possible_death:
                    for condition in injuries:
                        injured_cat.history.add_possible_history(
                            condition,
                            status=injured_cat.status,
                            scar_text=possible_scar,
                            death_text=possible_death,
                        )

        # get any possible interaction string out of this interaction
        interaction_str = choice(self.chosen_interaction.interactions)

        # prepare string for display
        interaction_str = self.adjust_interaction_string(interaction_str)

        effect = ""
        if positive:
            effect = i18n.t(f"relationships.positive_postscript_{intensity}")
        elif not positive:
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

    def get_value_change_amount(self, value_change: bool, intensity: str) -> int:
        """Finds and returns the int amount that the relationship type will change by according to given intensity and additional modifiers

        Parameters
        ----------
        value_change : bool
            True if the relationship value is positive, False if negative.
        intensity : str
            the intensity of the affect

        Returns
        -------
        amount : int
            the amount (negative or positive) for the given parameter
        """
        # get the normal amount
        amount = constants.CONFIG["relationship"]["value_change_amount"][intensity]
        if value_change == "decrease":
            amount = amount * -1

        # take compatibility into account
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            # neutral compatibility
            amount = amount
        elif compatibility:
            # positive compatibility
            amount += constants.CONFIG["relationship"]["compatibility_effect"]
        else:
            # negative compatibility
            amount -= constants.CONFIG["relationship"]["compatibility_effect"]
        return amount

    def interaction_affect_relationships(
        self, value_change: bool, intensity: str, rel_type: str
    ) -> None:
        """Affects the relationship according to the chosen types.

        Parameters
        ----------
        value_change : str
            if the relationship value is positive
        intensity : str
            the intensity of the affect
        rel_type : str
            relationship value type which needs to be affected

        Returns
        -------
        """
        amount = self.get_value_change_amount(value_change, intensity)

        buffs = []
        # only high intensity gives passive buffs
        if intensity == "high":
            passive_buff = int(
                amount / constants.CONFIG["relationship"][f"passive_influence_div"]
            )
            # just adding a teeny bit of variety
            buffs = [passive_buff - 1, passive_buff, passive_buff + 1]
            # the passive buff creates a cascade effect
            # so a negative interaction will affect all values to a negative degree
            # and a positive interaction will affect all values to a positive degree

            for rel_out in (
                RelType.LIKE,
                RelType.RESPECT,
                RelType.TRUST,
                RelType.COMFORT,
            ):
                setattr(self, rel_out, choice(buffs) if rel_type != rel_out else amount)

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

            setattr(self, key, getattr(self, key) + amount)

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
        if comp:
            bool_ballot.append(comp)

        # further influence the partition based on the relationship
        for value in (self.like, self.respect, self.comfort, self.trust):
            # each 10th above 0 adds another True
            if value > 0:
                bool_ballot += [True] * int(value / 10)
            # each 10th below 0
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

        value_weights = {v: 1 for v in [*RelType]}

        # change the weights according if the interaction should be positive or negative
        # existing rel values determine the weight added
        for attr, rel_type in zip([getattr(self, r) for r in [*RelType]], [*RelType]):
            if positive:
                if attr > 0:
                    value_weights[rel_type] += int(attr / 10)
            else:
                if rel_type == RelType.ROMANCE:
                    continue
                if attr > 0:
                    value_weights[rel_type] += int(abs(attr / 10))

        # increase the chance of a romance interaction if they are already mates
        if self.mates:
            value_weights[RelType.ROMANCE] += 1

        # if a romance relationship is not possible, remove this type, but only if there are no mates
        # if there already mates (set up by the user for example), don't remove this type
        mate_from_to = self.cat_from.is_potential_mate(
            self.cat_to, for_love_interest=True
        )
        mate_to_from = self.cat_to.is_potential_mate(
            self.cat_from, for_love_interest=True
        )
        if (not mate_from_to or not mate_to_from) and not self.mates:
            while RelType.ROMANCE in value_weights:
                value_weights.pop(RelType.ROMANCE)

        # if cats have no romance relationship already, don't allow romance decrease
        if (
            not positive
            and RelType.ROMANCE in value_weights
            and not self.cat_from.relationships[self.cat_to.ID].romance
        ):
            value_weights.pop(RelType.ROMANCE)

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
        # if there are no loaded interactions, raise error!
        if not possible_interactions:
            raise IndexError(
                f"No possible relationship interactions found for cat_from: {self.cat_from.ID} and cat_to: {self.cat_to.ID}"
            )

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

    def relationship_qualifies(self, qualifying_values: dict) -> bool:
        """
        Returns True if this relationship's rel_types are within the given value and the maximum possible values (-100 for negative values, 100 for positive values)
        :param qualifying_values: Dict of the needed values. Key should be the rel_type name and value should be the lowest required int (i.e. if you give a value of -40, the associated rel_type must be between -100 and -40. If you give a value of 40, the associated rel_type must be between 40 and 100.)
        """
        for rel_type, value in qualifying_values.items():
            if value == 0:
                continue
            if value > 0 and getattr(self, rel_type) < value:
                return False
            elif value < 0 and getattr(self, rel_type) > value:
                return False
        return True

    def get_amount_of_type(self, value_enum: RelType) -> Optional[int]:
        return getattr(self, value_enum) if hasattr(self, value_enum) else None

    def get_reltype_tiers(self) -> list[RelTier]:
        """
        Returns a list of all current rel_type tier strings
        """
        return [
            self.romance_tier,
            self.like_tier,
            self.trust_tier,
            self.comfort_tier,
            self.respect_tier,
        ]

    def get_rel_type_attributes(self, rel_type) -> (int, RelTier):
        """
        Returns a tuple of rel_type integer and tier
        """
        return getattr(self, rel_type), getattr(self, f"{rel_type}_tier")

    @property
    def total_relationship_value(self) -> int:
        """
        Returns the total int of all relationship types.
        """
        return self.romance + self.like + self.respect + self.comfort + self.trust

    @property
    def has_extreme_negative(self) -> bool:
        """
        Returns True if the relationship has an extreme negative value.
        """
        return any(tier for tier in self.get_reltype_tiers() if tier.is_extreme_neg)

    @property
    def has_extreme_positive(self) -> bool:
        """
        Returns True if the relationship has an extreme positive value.
        """
        return any(tier for tier in self.get_reltype_tiers() if tier.is_extreme_pos)

    @property
    def is_empty(self) -> bool:
        return (
            self.romance_tier.is_neutral
            and self.trust_tier.is_neutral
            and self.like_tier.is_neutral
            and self.comfort_tier.is_neutral
            and self.respect_tier.is_neutral
        )

    @property
    def romance(self) -> int:
        """0-100 scale, 0 is no romantic interest and 100 is full romantic interest"""
        return self._romance

    @romance.setter
    def romance(self, value):
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self._romance = value

    @property
    def romance_tier(self) -> Optional[RelTier]:
        group = self._get_tier_group(self.romance)

        if group == "neutral":
            return RelTier.UNINTERESTED
        elif group == "low_pos":
            return RelTier.FANCIES
        elif group == "mid_pos":
            return RelTier.ADORES
        else:
            return RelTier.LOVES

    @property
    def like(self) -> int:
        return self._like

    @like.setter
    def like(self, value):
        if value > 100:
            value = 100
        elif value < -100:
            value = -100
        self._like = value

    @property
    def like_tier(self) -> Optional[RelTier]:
        group = self._get_tier_group(self.like)

        if group == "extreme_neg":
            return RelTier.LOATHES
        elif group == "mid_neg":
            return RelTier.HATES
        elif group == "low_neg":
            return RelTier.DISLIKES
        elif group == "neutral":
            return RelTier.KNOWS_OF
        elif group == "low_pos":
            return RelTier.LIKES
        elif group == "mid_pos":
            return RelTier.ENJOYS
        else:
            return RelTier.CHERISHES

    @property
    def respect(self) -> int:
        return self._respect

    @respect.setter
    def respect(self, value):
        if value > 100:
            value = 100
        elif value < -100:
            value = -100
        self._respect = value

    @property
    def respect_tier(self) -> Optional[RelTier]:
        group = self._get_tier_group(self.respect)

        if group == "extreme_neg":
            return RelTier.RESENTS
        elif group == "mid_neg":
            return RelTier.ENVIES
        elif group == "low_neg":
            return RelTier.BEGRUDGES
        elif group == "neutral":
            return RelTier.ACKNOWLEDGES
        elif group == "low_pos":
            return RelTier.PRAISES
        elif group == "mid_pos":
            return RelTier.RESPECTS
        else:
            return RelTier.ADMIRES

    @property
    def comfort(self) -> int:
        return self._comfort

    @comfort.setter
    def comfort(self, value):
        if value > 100:
            value = 100
        elif value < -100:
            value = -100
        self._comfort = value

    @property
    def comfort_tier(self) -> Optional[RelTier]:
        group = self._get_tier_group(self.comfort)

        if group == "extreme_neg":
            return RelTier.RUNS_FROM
        elif group == "mid_neg":
            return RelTier.FEARS
        elif group == "low_neg":
            return RelTier.AVOIDS
        elif group == "neutral":
            return RelTier.CONSIDERS
        elif group == "low_pos":
            return RelTier.RELATES_TO
        elif group == "mid_pos":
            return RelTier.UNDERSTANDS
        else:
            return RelTier.KNOWS_DEEPLY

    @property
    def trust(self) -> int:
        return self._trust

    @trust.setter
    def trust(self, value):
        if value > 100:
            value = 100
        elif value < -100:
            value = -100
        self._trust = value

    @property
    def trust_tier(self) -> Optional[RelTier]:
        group = self._get_tier_group(self.trust)

        if group == "extreme_neg":
            return RelTier.LOATHES
        elif group == "mid_neg":
            return RelTier.DISTRUSTS
        elif group == "low_neg":
            return RelTier.DOUBTS
        elif group == "neutral":
            return RelTier.OBSERVES
        elif group == "low_pos":
            return RelTier.LISTENS_TO
        elif group == "mid_pos":
            return RelTier.TRUSTS
        else:
            return RelTier.CONFIDES_IN

    @staticmethod
    def _get_tier_group(rel_type) -> Optional[str]:
        """
        Returns the tier group for the given value.
        """
        for group, interval in constants.CONFIG["relationship"][
            "value_intervals"
        ].items():
            if rel_type <= interval:
                return group

        return None
