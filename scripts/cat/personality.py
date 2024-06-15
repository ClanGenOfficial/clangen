from __future__ import annotations

from random import randint, choice, choices

import ujson


class Personality:
    """Hold personality information for a cat, and functions to deal with it"""

    facet_types = ["lawfulness", "sociability", "aggression", "stability"]
    facet_range = [0, 16]

    with open(
            "resources/dicts/traits/trait_ranges.json", "r", encoding="utf-8"
    ) as read_file:
        trait_ranges = ujson.loads(read_file.read())

    def __init__(
            self,
            trait: str = None,
            kit_trait: bool = False,
            lawful: int = None,
            social: int = None,
            aggress: int = None,
            stable: int = None,
    ):
        """If trait is given, it will randomize facets within the range of the trait. It will ignore any facets given.
        If facets are given and no trait, it will find a trait that matches the facets. NOTE: you can give
        only some facets: It will randomize any you don't specify.
        If both facets and trait are given, it will use the trait if it matched the facets. Otherwise, it will
        find a new trait."""
        self._law = 0
        self._social = 0
        self._aggress = 0
        self._stable = 0
        self.trait = None
        self.kit = kit_trait  # If true, use kit trait. If False, use normal traits.

        if self.kit:
            trait_type_dict = Personality.trait_ranges["kit_traits"]
        else:
            trait_type_dict = Personality.trait_ranges["normal_traits"]

        _tr = None
        if trait and trait in trait_type_dict:
            # Trait-given init
            self.trait = trait
            _tr = trait_type_dict[self.trait]

        # Set Facet Values
        # The priority of is:
        # (1) Given value, from parameter.
        # (2) If a trait range is assigned, pick from trait range
        # (3) Totally random.
        if lawful is not None:
            self._law = Personality.adjust_to_range(lawful)
        elif _tr:
            self._law = randint(_tr["lawfulness"][0], _tr["lawfulness"][1])
        else:
            self._law = randint(Personality.facet_range[0], Personality.facet_range[1])

        if social is not None:
            self._social = Personality.adjust_to_range(social)
        elif _tr:
            self._social = randint(_tr["sociability"][0], _tr["sociability"][1])
        else:
            self._social = randint(
                Personality.facet_range[0], Personality.facet_range[1]
            )

        if aggress is not None:
            self._aggress = Personality.adjust_to_range(aggress)
        elif _tr:
            self._aggress = randint(_tr["aggression"][0], _tr["aggression"][1])
        else:
            self._aggress = randint(
                Personality.facet_range[0], Personality.facet_range[1]
            )

        if stable is not None:
            self._stable = Personality.adjust_to_range(stable)
        elif _tr:
            self._stable = randint(_tr["stability"][0], _tr["stability"][1])
        else:
            self._stable = randint(
                Personality.facet_range[0], Personality.facet_range[1]
            )

        # If trait is still empty, or if the trait is not valid with the facets, change it.
        if not self.trait or not self.is_trait_valid():
            self.choose_trait()

    def __repr__(self) -> str:
        """For debugging"""
        return (
            f"{self.trait}: "
            f"lawfulness {self.lawfulness}, "
            f"aggression {self.aggression}, "
            f"sociability {self.sociability}, "
            f"stability {self.stability}"
        )

    def get_facet_string(self):
        """For saving the facets to file."""
        return (
            f"{self.lawfulness},{self.sociability},{self.aggression},{self.stability}"
        )

    def __getitem__(self, key):
        """Alongside __setitem__, Allows you to treat this like a dictionary if you want."""
        return getattr(self, key)

    def __setitem__(self, key, newval):
        """Alongside __getitem__, Allows you to treat this like a dictionary if you want."""
        setattr(self, key, newval)

    # ---------------------------------------------------------------------------- #
    #                               PROPERTIES                                     #
    # ---------------------------------------------------------------------------- #

    @property
    def lawfulness(self):
        return self._law

    @lawfulness.setter
    def lawfulness(self, new_val):
        """Do not use property in init"""
        self._law = Personality.adjust_to_range(new_val)
        if not self.is_trait_valid():
            self.choose_trait()

    @property
    def sociability(self):
        return self._social

    @sociability.setter
    def sociability(self, new_val):
        """Do not use property in init"""
        self._social = Personality.adjust_to_range(new_val)
        if not self.is_trait_valid():
            self.choose_trait()

    @property
    def aggression(self):
        return self._aggress

    @aggression.setter
    def aggression(self, new_val):
        """Do not use property in init"""
        self._aggress = Personality.adjust_to_range(new_val)
        if not self.is_trait_valid():
            self.choose_trait()

    @property
    def stability(self):
        return self._stable

    @stability.setter
    def stability(self, new_val):
        """Do not use property in init"""
        self._stable = Personality.adjust_to_range(new_val)
        if not self.is_trait_valid():
            self.choose_trait()

    # ---------------------------------------------------------------------------- #
    #                               METHODS                                        #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def adjust_to_range(val: int) -> int:
        """Take an integer and adjust it to be in the trait-range"""

        if val < Personality.facet_range[0]:
            val = Personality.facet_range[0]
        elif val > Personality.facet_range[1]:
            val = Personality.facet_range[1]

        return val

    def set_kit(self, kit: bool):
        """Switch the trait-type. True for kit, False for normal"""
        self.kit = kit
        if not self.is_trait_valid():
            self.choose_trait()

    def is_trait_valid(self) -> bool:
        """Return True if the current facets fit the trait ranges, false
        if it doesn't. Also returns false if the trait is not in the trait dict."""

        if self.kit:
            trait_type_dict = Personality.trait_ranges["kit_traits"]
        else:
            trait_type_dict = Personality.trait_ranges["normal_traits"]

        if self.trait not in trait_type_dict:
            return False

        trait_range = trait_type_dict[self.trait]

        if not (
                trait_range["lawfulness"][0]
                <= self.lawfulness
                <= trait_range["lawfulness"][1]
        ):
            return False
        if not (
                trait_range["sociability"][0]
                <= self.sociability
                <= trait_range["sociability"][1]
        ):
            return False
        if not (
                trait_range["aggression"][0]
                <= self.aggression
                <= trait_range["aggression"][1]
        ):
            return False
        if not (
                trait_range["stability"][0] <= self.stability <= trait_range["stability"][1]
        ):
            return False

        return True

    def choose_trait(self):
        """Chooses trait based on the facets"""

        if self.kit:
            trait_type_dict = Personality.trait_ranges["kit_traits"]
        else:
            trait_type_dict = Personality.trait_ranges["normal_traits"]

        possible_traits = []
        for trait, fac in trait_type_dict.items():
            if not (fac["lawfulness"][0] <= self.lawfulness <= fac["lawfulness"][1]):
                continue
            if not (fac["sociability"][0] <= self.sociability <= fac["sociability"][1]):
                continue
            if not (fac["aggression"][0] <= self.aggression <= fac["aggression"][1]):
                continue
            if not (fac["stability"][0] <= self.stability <= fac["stability"][1]):
                continue

            possible_traits.append(trait)

        if possible_traits:
            self.trait = choice(possible_traits)
        else:
            print("No possible traits! Using 'strange'")
            self.trait = "strange"

    def facet_wobble(self, facet_max=5):
        """Makes a small adjustment to all the facets, and redetermines trait if needed."""
        self.lawfulness += randint(-facet_max, facet_max)
        self.stability += randint(-facet_max, facet_max)
        self.aggression += randint(-facet_max, facet_max)
        self.sociability += randint(-facet_max, facet_max)

    def mentor_influence(self, mentor_personality: Personality):
        """applies mentor influence after the pair go on a patrol together
        returns history information in the form (facet_affected, amount_affected)
        """

        # Get possible facet values
        possible_facets = {
            i: mentor_personality[i] - self[i]
            for i in Personality.facet_types
            if mentor_personality[i] - self[i] != 0
        }

        if possible_facets:
            # Choice trait to effect, weighted by the abs of the difference (higher difference = more likely to effect)
            facet_affected = choices(
                [i for i in possible_facets],
                weights=[abs(i) for i in possible_facets.values()],
                k=1,
            )[0]
            # stupid python with no sign() function by default.
            amount_affected = int(
                possible_facets[facet_affected]
                / abs(possible_facets[facet_affected])
                * randint(1, 2)
            )
            self[facet_affected] += amount_affected
            return facet_affected, amount_affected
        else:
            # This will only trigger if they have the same personality.
            return None
