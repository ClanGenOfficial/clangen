"""
Module that handles the name generation for all cats.
"""

import contextlib
import os
import random

import ujson

from scripts.game_structure import constants
from scripts.cat.enums import CatRank, CatGroup
from scripts.housekeeping.datadir import get_save_dir


class Name:
    """
    Stores & handles name generation.
    """

    if os.path.exists("resources/dicts/names/names.json"):
        with open("resources/dicts/names/names.json", encoding="utf-8") as read_file:
            names_dict = ujson.loads(read_file.read())

        if os.path.exists(get_save_dir() + "/prefixlist.txt"):
            with open(
                str(get_save_dir() + "/prefixlist.txt"), "r", encoding="utf-8"
            ) as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split("\n")
                for new_name in new_names:
                    if new_name != "":
                        if new_name.startswith("-"):
                            while new_name[1:] in names_dict["normal_prefixes"]:
                                names_dict["normal_prefixes"].remove(new_name[1:])
                        else:
                            names_dict["normal_prefixes"].append(new_name)

        if os.path.exists(get_save_dir() + "/suffixlist.txt"):
            with open(
                str(get_save_dir() + "/suffixlist.txt"), "r", encoding="utf-8"
            ) as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split("\n")
                for new_name in new_names:
                    if new_name != "":
                        if new_name.startswith("-"):
                            while new_name[1:] in names_dict["normal_suffixes"]:
                                names_dict["normal_suffixes"].remove(new_name[1:])
                        else:
                            names_dict["normal_suffixes"].append(new_name)

        if os.path.exists(get_save_dir() + "/specialsuffixes.txt"):
            with open(
                str(get_save_dir() + "/specialsuffixes.txt", "r"), encoding="utf-8"
            ) as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split("\n")
                for new_name in new_names:
                    if new_name != "":
                        if new_name.startswith("-"):
                            del names_dict["special_suffixes"][new_name[1:]]
                        elif ":" in new_name:
                            _tmp = new_name.split(":")
                            names_dict["special_suffixes"][_tmp[0]] = _tmp[1]

    def __init__(
        self,
        prefix=None,
        suffix=None,
        biome=None,
        specsuffix_hidden=False,
        load_existing_name=False,
        cat=None,
    ):
        self.prefix = prefix
        self.suffix = suffix
        self.specsuffix_hidden = specsuffix_hidden

        self.cat = cat

        try:
            color = cat.pelt.colour
            eyes = cat.pelt.eye_colour
            pelt = cat.pelt.name
            tortie_pattern = cat.pelt.tortie_pattern
        except AttributeError:
            color = None
            eyes = None
            pelt = None
            tortie_pattern = None

        name_fixpref = False
        # Set prefix
        if prefix is None:
            self.give_prefix(eyes, color, biome)
            # needed for random dice when we're changing the Prefix
            name_fixpref = True

        # Set suffix
        if self.suffix is None:
            self.give_suffix(pelt, biome, tortie_pattern)
            if name_fixpref and self.prefix is None:
                # needed for random dice when we're changing the Prefix
                name_fixpref = False

        if self.suffix and not load_existing_name:
            # Prevent triple letter names from joining prefix and suffix from occurring (ex. Beeeye)
            possible_three_letter = (
                self.prefix[-2:] + self.suffix[0],
                self.prefix[-1] + self.suffix[:2],
            )
            triple_letter = all(
                i == possible_three_letter[0][0] for i in possible_three_letter[0]
            ) or all(
                i == possible_three_letter[1][0]
                for i in possible_three_letter[1]
                # Prevent double animal names (ex. Spiderfalcon)
            )
            double_animal = (
                self.prefix in self.names_dict["animal_prefixes"]
                and self.suffix in self.names_dict["animal_suffixes"]
            )
            # Prevent the inappropriate names
            nono_name = self.prefix + self.suffix
            # Prevent double names (ex. Iceice)
            # Prevent suffixes containing the prefix (ex. Butterflyfly)

            i = 0
            while (
                nono_name.lower() in self.names_dict["inappropriate_names"]
                or triple_letter
                or double_animal
                or (
                    self.prefix.lower() in self.suffix.lower()
                    and str(self.prefix) != ""
                )
                or (
                    self.suffix.lower() in self.prefix.lower()
                    and str(self.suffix) != ""
                )
            ):
                # check if random die was for prefix
                if name_fixpref:
                    self.give_prefix(eyes, color, biome)
                else:
                    self.give_suffix(pelt, biome, tortie_pattern)

                nono_name = self.prefix + self.suffix
                possible_three_letter = (
                    self.prefix[-2:] + self.suffix[0],
                    self.prefix[-1] + self.suffix[:2],
                )
                if any(
                    i != possible_three_letter[0][0] for i in possible_three_letter[0]
                ) and any(
                    i != possible_three_letter[1][0] for i in possible_three_letter[1]
                ):
                    triple_letter = False
                if (
                    self.prefix not in self.names_dict["animal_prefixes"]
                    or self.suffix not in self.names_dict["animal_suffixes"]
                ):
                    double_animal = False
                i += 1

    def __str__(self):
        return self.__repr__()

    # Generate possible prefix
    def give_prefix(self, eyes, colour, biome):
        """Generate possible prefix."""
        # decided in constants.CONFIG: cat_name_controls
        if constants.CONFIG["cat_name_controls"]["always_name_after_appearance"]:
            named_after_appearance = True
        else:
            named_after_appearance = not random.getrandbits(
                2
            )  # Chance for True is '1/4'

        named_after_biome_ = not random.getrandbits(3)  # chance for True is 1/8

        # Add possible prefix categories to list.
        possible_prefix_categories = []
        if (
            eyes in self.names_dict["eye_prefixes"]
            and constants.CONFIG["cat_name_controls"]["allow_eye_names"]
        ):
            possible_prefix_categories.append(self.names_dict["eye_prefixes"][eyes])
        if colour in self.names_dict["colour_prefixes"]:
            possible_prefix_categories.append(
                self.names_dict["colour_prefixes"][colour]
            )
        if biome is not None and biome in self.names_dict["biome_prefixes"]:
            possible_prefix_categories.append(self.names_dict["biome_prefixes"][biome])

        # Choose appearance-based prefix if possible and named_after_appearance because True.
        if (
            named_after_appearance
            and possible_prefix_categories
            and not named_after_biome_
            or named_after_biome_
            and possible_prefix_categories
        ):
            prefix_category = random.choice(possible_prefix_categories)
            self.prefix = random.choice(prefix_category)
        else:
            self.prefix = random.choice(self.names_dict["normal_prefixes"])

        # This thing prevents any prefix duplications from happening.
        # Try statement stops this form running when initializing.
        with contextlib.suppress(NameError):
            if self.prefix in names.prefix_history:
                # do this recursively until a name that isn't on the history list.
                self.give_prefix(eyes, colour, biome)
                # prevent infinite recursion
                if len(names.prefix_history) > 0:
                    names.prefix_history.pop(0)
            else:
                names.prefix_history.append(self.prefix)
            # Set the maximin length to 8 just to be sure
            if len(names.prefix_history) > 8:
                # removing at zero so the oldest gets removed
                names.prefix_history.pop(0)

    # Generate possible suffix
    def give_suffix(self, pelt, biome, tortie_pattern):
        """Generate possible suffix."""
        if pelt is None or pelt == "SingleColour":
            self.suffix = random.choice(self.names_dict["normal_suffixes"])
        else:
            named_after_pelt = not random.getrandbits(2)  # Chance for True is '1/8'.
            named_after_biome = not random.getrandbits(3)  # 1/8
            # Pelt name only gets used if there's an associated suffix.
            if named_after_pelt:
                if (
                    pelt in ("Tortie", "Calico")
                    and tortie_pattern in self.names_dict["tortie_pelt_suffixes"]
                ):
                    self.suffix = random.choice(
                        self.names_dict["tortie_pelt_suffixes"][tortie_pattern]
                    )
                elif pelt in self.names_dict["pelt_suffixes"]:
                    self.suffix = random.choice(self.names_dict["pelt_suffixes"][pelt])
                else:
                    self.suffix = random.choice(self.names_dict["normal_suffixes"])
            elif named_after_biome:
                if biome in self.names_dict["biome_suffixes"]:
                    self.suffix = random.choice(
                        self.names_dict["biome_suffixes"][biome]
                    )
                else:
                    self.suffix = random.choice(self.names_dict["normal_suffixes"])
            else:
                self.suffix = random.choice(self.names_dict["normal_suffixes"])

    def __repr__(self):
        # Handles predefined suffixes (such as newborns being kit),
        # then suffixes based on ages (fixes #2004, just trust me)

        # Handles suffix assignment with outside cats
        if self.cat.status.is_former_clancat:
            old_rank = self.cat.status.find_prior_clan_rank()

            if (
                old_rank in self.names_dict["special_suffixes"]
                and not self.specsuffix_hidden
            ):
                return self.prefix + self.names_dict["special_suffixes"][old_rank]

        if (
            self.cat.status.rank in self.names_dict["special_suffixes"]
            and not self.specsuffix_hidden
        ):
            return (
                self.prefix + self.names_dict["special_suffixes"][self.cat.status.rank]
            )
        if constants.CONFIG["fun"]["april_fools"]:
            return f"{self.prefix}egg"
        return self.prefix + self.suffix


names = Name()
names.prefix_history = []
