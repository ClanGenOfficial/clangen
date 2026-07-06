from typing import Optional


from scripts.game_structure import constants
from scripts.cat_relations.enums import RelTier, RelType


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

        self.no_longer_neutral = []
        """
        List of rel types that made it out of the neutral tier (ROMANCE is not included). This list is used to indicate which types should not return to a neutral state.
        """

        # romance operates on a 0-100 scale, 0 is no romantic interest and 100 is full romantic interest
        self._romance = min(max(romance, 0), 100)

        # each stat can go from -100 to 100
        # negative numbers are the negative state while positive is the positive state
        self._like = min(max(like, -100), 100)
        self._respect = min(max(respect, -100), 100)
        self._trust = min(max(trust, -100), 100)
        self._comfort = min(max(comfort, -100), 100)

    def to_dict(self):
        return {
            "cat_from_id": self.cat_from.ID,
            "cat_to_id": self.cat_to.ID,
            "family": self.family,
            "romance": self.romance,
            "like": self.like,
            "respect": self.respect,
            "comfort": self.comfort,
            "trust": self.trust,
            "log": self.log,
            "no_longer_neutral": self.no_longer_neutral,
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
    def total_abs_relationship_value(self) -> int:
        """
        Returns the sum of the absolute values of all relationship types.
        """
        return (
            abs(self.romance)
            + abs(self.like)
            + abs(self.respect)
            + abs(self.comfort)
            + abs(self.trust)
        )

    @property
    def has_extreme_negative(self) -> bool:
        """
        Returns True if the relationship has an extreme negative value.
        """
        return any(tier for tier in self.get_reltype_tiers() if tier.is_extreme_neg)

    @property
    def has_mid_negative(self) -> bool:
        """
        Returns True if the relationship has a mid negative value.
        """
        return any(tier for tier in self.get_reltype_tiers() if tier.is_mid_neg)

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

        if RelType.LIKE in self.no_longer_neutral and self.like_tier.is_neutral:
            self._like = self._get_neutral_adjusted_value(self._like)

        if RelType.LIKE not in self.no_longer_neutral and not self.like_tier.is_neutral:
            self.no_longer_neutral.append(RelType.LIKE)

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

        if RelType.RESPECT in self.no_longer_neutral and self.respect_tier.is_neutral:
            self._respect = self._get_neutral_adjusted_value(self._respect)

        if (
            RelType.RESPECT not in self.no_longer_neutral
            and not self.respect_tier.is_neutral
        ):
            self.no_longer_neutral.append(RelType.RESPECT)

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

        if RelType.COMFORT in self.no_longer_neutral and self.comfort_tier.is_neutral:
            self._comfort = self._get_neutral_adjusted_value(self._comfort)

        if (
            RelType.COMFORT not in self.no_longer_neutral
            and not self.comfort_tier.is_neutral
        ):
            self.no_longer_neutral.append(RelType.COMFORT)

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

        if RelType.TRUST in self.no_longer_neutral and self.trust_tier.is_neutral:
            self._trust = self._get_neutral_adjusted_value(self._trust)

        if (
            RelType.TRUST not in self.no_longer_neutral
            and not self.trust_tier.is_neutral
        ):
            self.no_longer_neutral.append(RelType.TRUST)

    @property
    def trust_tier(self) -> Optional[RelTier]:
        group = self._get_tier_group(self.trust)

        if group == "extreme_neg":
            return RelTier.DISCREDITS
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

    @staticmethod
    def _get_neutral_adjusted_value(value: int):
        value_intervals = constants.CONFIG["relationship"]["value_intervals"]
        neutral_start = value_intervals["low_neg"]
        neutral_end = value_intervals["neutral"]

        if neutral_start < value <= neutral_end:  # if value is neutral
            # find which end of the neutral range we're closest too
            if abs(value - neutral_start) < abs(neutral_end - value):
                # if closest to neg side, return negative tier value
                return neutral_start - 1
            else:
                # if closest to pos side, return positive tier value
                return neutral_end + 1
        else:
            return value
