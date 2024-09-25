"""
Module that handles the name generation for all cats.
"""

import os
import random

import ujson

from scripts.game_structure.game_essentials import game
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
                str(get_save_dir() + "/prefixlist.txt", "r"), encoding="utf-8"
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
                str(get_save_dir() + "/suffixlist.txt", "r"), encoding="utf-8"
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
        status="warrior",
        prefix=None,
        suffix=None,
        colour=None,
        eyes=None,
        pelt=None,
        tortiepattern=None,
        biome=None,
        specsuffix_hidden=False,
        load_existing_name=False,
    ):
        self.status = status
        self.prefix = prefix
        self.suffix = suffix
        self.specsuffix_hidden = specsuffix_hidden

        name_fixpref = False
        # Set prefix
        if prefix is None:
            self.give_prefix(eyes, colour, biome)
            # needed for random dice when we're changing the Prefix
            name_fixpref = True

        # Set suffix
        if self.suffix is None:
            self.give_suffix(pelt, biome, tortiepattern)
            if name_fixpref and self.prefix is None:
                # needed for random dice when we're changing the Prefix
                name_fixpref = False

        if self.suffix and not load_existing_name:
            # Prevent triple letter names from joining prefix and suffix from occurring (ex. Beeeye)
            triple_letter = False
            possible_three_letter = (
                self.prefix[-2:] + self.suffix[0],
                self.prefix[-1] + self.suffix[:2],
            )
            if all(
                i == possible_three_letter[0][0] for i in possible_three_letter[0]
            ) or all(
                i == possible_three_letter[1][0] for i in possible_three_letter[1]
            ):
                triple_letter = True
            # Prevent double animal names (ex. Spiderfalcon)
            double_animal = False
            if (
                self.prefix in self.names_dict["animal_prefixes"]
                and self.suffix in self.names_dict["animal_suffixes"]
            ):
                double_animal = True
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
                    self.give_prefix(eyes, colour, biome)
                else:
                    self.give_suffix(pelt, biome, tortiepattern)

                nono_name = self.prefix + self.suffix
                possible_three_letter = (
                    self.prefix[-2:] + self.suffix[0],
                    self.prefix[-1] + self.suffix[:2],
                )
                if not (
                    all(
                        i == possible_three_letter[0][0]
                        for i in possible_three_letter[0]
                    )
                    or all(
                        i == possible_three_letter[1][0]
                        for i in possible_three_letter[1]
                    )
                ):
                    triple_letter = False
                if not (
                    self.prefix in self.names_dict["animal_prefixes"]
                    and self.suffix in self.names_dict["animal_suffixes"]
                ):
                    double_animal = False
                i += 1

    # Generate possible prefix
    def give_prefix(self, eyes, colour, biome):
        """Generate possible prefix."""
        # decided in game config: cat_name_controls
        if game.config["cat_name_controls"]["always_name_after_appearance"]:
            named_after_appearance = True
        else:
            named_after_appearance = not random.getrandbits(
                2
            )  # Chance for True is '1/4'

        named_after_biome_ = not random.getrandbits(3)  # chance for True is 1/8

        # Add possible prefix categories to list.
        possible_prefix_categories = []
        if game.config["cat_name_controls"][
            "allow_eye_names"
        ]:  # game config: cat_name_controls
            if eyes in self.names_dict["eye_prefixes"]:
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
        ):
            prefix_category = random.choice(possible_prefix_categories)
            self.prefix = random.choice(prefix_category)
        elif named_after_biome_ and possible_prefix_categories:
            prefix_category = random.choice(possible_prefix_categories)
            self.prefix = random.choice(prefix_category)
        else:
            self.prefix = random.choice(self.names_dict["normal_prefixes"])

        # This thing prevents any prefix duplications from happening.
        # Try statement stops this form running when initailizing.
        try:
            if self.prefix in names.prefix_history:
                # do this recurively until a name that isn't on the history list is chosses.
                self.give_prefix(eyes, colour, biome)
                # prevent infinite recursion
                if len(names.prefix_history) > 0:
                    names.prefix_history.pop(0)
            else:
                names.prefix_history.append(self.prefix)
            # Set the maximun lenth to 8 just to be sure
            if len(names.prefix_history) > 8:
                # removing at zero so the oldest gets removed
                names.prefix_history.pop(0)
        except NameError:
            pass

    # Generate possible suffix
    def give_suffix(self, pelt, biome, tortiepattern):
        """Generate possible suffix."""
        if pelt is None or pelt == "SingleColour":
            self.suffix = random.choice(self.names_dict["normal_suffixes"])
        else:
            named_after_pelt = not random.getrandbits(2)  # Chance for True is '1/8'.
            named_after_biome = not random.getrandbits(3)  # 1/8
            # Pelt name only gets used if there's an associated suffix.
            if named_after_pelt:
                if (
                    pelt in ["Tortie", "Calico"]
                    and tortiepattern in self.names_dict["tortie_pelt_suffixes"]
                ):
                    self.suffix = random.choice(
                        self.names_dict["tortie_pelt_suffixes"][tortiepattern]
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
        if (
            self.status in self.names_dict["special_suffixes"]
            and not self.specsuffix_hidden
        ):
            return self.prefix + self.names_dict["special_suffixes"][self.status]
        if game.config["fun"]["april_fools"]:
            return self.prefix + "egg"
        return self.prefix + self.suffix


names = Name()
names.prefix_history = []
