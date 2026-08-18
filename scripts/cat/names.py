"""
Module that handles the name generation for all cats.
"""

import contextlib
import os
import random

import i18n
import ujson

from scripts.game_structure import constants
from scripts.cat.enums import CatRank, CatGroup, CatAge, CatSocial
from scripts.game_structure.localization import load_lang_resource
from scripts.housekeeping.datadir import get_save_dir


class Name:
    """
    Stores & handles name generation.
    """

    current_save_dir = None
    currently_loaded_lang = None
    names_dict = {}
    prefix_history = []

    def __init__(
        self,
        prefix=None,
        suffix=None,
        biome=None,
        specsuffix_hidden=False,
        load_existing_name=False,
        cat=None,
    ):
        self.load_localized_names()
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
            # check if random die was for prefix
            if name_fixpref:
                self.give_prefix(eyes, color, biome)
            else:
                self.give_suffix(pelt, biome, tortie_pattern)

    @classmethod
    def _usable_name(cls, prefix, suffix):
        if prefix is None or suffix is None:
            return True

        name = prefix + suffix

        # Prevent triple letter names from joining prefix and suffix from occurring (ex. Beeeye)
        # Prevent crash on empty prefix or suffix (e.g. empty-suffix loner names)
        if not prefix or not suffix:
            triple_letter = False
        else:
            possible_three_letter = (
                prefix[-2:] + suffix[0],
                prefix[-1] + suffix[:2],
            )
            triple_letter = all(
                i == possible_three_letter[0][0] for i in possible_three_letter[0]
            ) or all(i == possible_three_letter[1][0] for i in possible_three_letter[1])

        # Prevent double animal names (ex. Spiderfalcon)
        double_animal = (
            prefix in cls.names_dict["animal_prefixes"]
            and suffix in cls.names_dict["animal_suffixes"]
        )

        # Prevent double names (ex. Iceice)
        # Prevent suffixes containing the prefix (ex. Butterflyfly)
        double_name = (prefix.lower() in suffix.lower() and str(prefix) != "") or (
            suffix.lower() in prefix.lower() and str(suffix) != ""
        )

        return not (
            # Prevent the inappropriate names
            name.lower() in cls.names_dict["inappropriate_names"]
            or triple_letter
            or double_animal
            or double_name
        )

    @classmethod
    def load_localized_names(cls):
        """
        Loads the correct names for the given language. Includes override for always using English names, in case localization wants to be ignored
        :return: None
        """

        # allowing the user to override the localized language names if desired
        if always_english := constants.CONFIG["cat_name_controls"][
            "always_use_english"
        ]:
            lang = "en"
        else:
            lang = i18n.config.get("locale")

        if cls.current_save_dir == get_save_dir() and cls.currently_loaded_lang == lang:
            # nothing to do here, all good
            return

        if always_english:
            with open("resources/lang/en/names.json", encoding="utf-8") as read_file:
                names_dict = ujson.loads(read_file.read())
        else:
            names_dict = load_lang_resource("names.json")

        save_dir = get_save_dir()

        # here onwards is copied wholesale from the original Name class

        if os.path.exists(save_dir + "/prefixlist.txt"):
            with open(
                str(save_dir + "/prefixlist.txt"), "r", encoding="utf-8"
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

        if os.path.exists(save_dir + "/suffixlist.txt"):
            with open(
                str(save_dir + "/suffixlist.txt"), "r", encoding="utf-8"
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

        if os.path.exists(save_dir + "/specialsuffixes.txt"):
            with open(
                str(save_dir + "/specialsuffixes.txt", "r"), encoding="utf-8"
            ) as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if len(name_list) > 0:
                new_names = name_list.split("\n")
                for new_name in new_names:
                    if new_name != "":
                        if new_name.startswith("-"):
                            del names_dict["special_suffixes"][new_name[1:]]
                        elif ":" in new_name:
                            _tmp = new_name.split(":")
                            names_dict["special_suffixes"][_tmp[0]] = _tmp[1]

        cls.names_dict = names_dict
        cls.current_save_dir = save_dir
        cls.currently_loaded_lang = lang

    def __str__(self):
        return self.__repr__()

    def find_outsider_name(self, social: CatSocial):
        if social == CatSocial.CLANCAT:
            return

        # if it ain't a clancat, give it a non-clancat name
        name_categories = [
            "silly_names",
            "human_names",
            "loner_names",
            "normal_prefixes",
        ]
        # defaults in case of error
        weights = [1, 1, 1, 1]
        # give kittypets a kittypet name
        weights = constants.CONFIG["cat_name_controls"][str(social)]

        selected_category = random.choices(name_categories, weights, k=1)[0]
        name = random.choice(self.names_dict[selected_category])
        self.cat.change_name(new_prefix=name, new_suffix="")

    # Generate possible prefix
    def give_prefix(self, eyes, colour, biome):
        """Generate possible prefix."""
        self.load_localized_names()

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

        while True:
            # decided in constants.CONFIG: cat_name_controls
            if constants.CONFIG["cat_name_controls"]["always_name_after_appearance"]:
                named_after_appearance = True
            else:
                named_after_appearance = not random.getrandbits(
                    2
                )  # Chance for True is '1/4'

            named_after_biome = not random.getrandbits(3)  # chance for True is 1/8
            # Choose appearance-based prefix if possible and named_after_appearance because True.
            if (
                named_after_appearance
                and possible_prefix_categories
                and not named_after_biome
                or named_after_biome
                and possible_prefix_categories
            ):
                prefix_category = random.choice(possible_prefix_categories)
                self.prefix = random.choice(prefix_category)
            else:
                self.prefix = random.choice(self.names_dict["normal_prefixes"])

            # prevent prefix duplications from happening
            if self.prefix in self.prefix_history or not self._usable_name(
                self.prefix, self.suffix
            ):
                continue
            else:
                self.prefix_history.append(self.prefix)
                # Set the maximin length to 8 just to be sure
                if len(self.prefix_history) > 8:
                    # removing at zero so the oldest gets removed
                    self.prefix_history.pop(0)
                return

    # Generate possible suffix
    def give_suffix(self, pelt, biome, tortie_pattern):
        """Generate possible suffix."""
        self.load_localized_names()

        while True:
            pool = self.names_dict["normal_suffixes"]

            if pelt is not None or pelt != "SingleColour":
                named_after_pelt = not random.getrandbits(
                    2
                )  # Chance for True is '1/8'.
                named_after_biome = not random.getrandbits(3)  # 1/8
                # Pelt name only gets used if there's an associated suffix.
                if named_after_pelt:
                    if (
                        pelt in ("Tortie", "Calico")
                        and tortie_pattern in self.names_dict["tortie_pelt_suffixes"]
                    ):
                        pool = self.names_dict["tortie_pelt_suffixes"][tortie_pattern]
                    elif pelt in self.names_dict["pelt_suffixes"]:
                        pool = self.names_dict["pelt_suffixes"][pelt]
                    else:
                        pool = self.names_dict["normal_suffixes"]
                elif named_after_biome:
                    if biome in self.names_dict["biome_suffixes"]:
                        pool = self.names_dict["biome_suffixes"][biome]
                    else:
                        pool = self.names_dict["normal_suffixes"]
                else:
                    pool = self.names_dict["normal_suffixes"]
            self.suffix = random.choice(pool)
            if self._usable_name(self.prefix, self.suffix):
                return

    def get_specsuffix_name(self, rank: CatRank = CatRank.LEADER):
        """
        Return the cat's name with the appropriate special suffix. If no specsuffix is given for that rank, returns
        default prefix + suffix. If specsuffix_hidden is true, return default prefix + suffix.
        :param rank: CatRank matching
        :return: Cat's name string
        """
        self.load_localized_names()

        if rank in self.names_dict["special_suffixes"] and not self.specsuffix_hidden:
            return self.prefix + self.names_dict["special_suffixes"][rank]

        return self.prefix + self.suffix

    def __repr__(self):
        # Handles predefined suffixes (such as newborns being kit),
        # then suffixes based on ages (fixes #2004, just trust me)
        self.load_localized_names()

        # Handles suffix assignment with outside cats
        if (
            self.cat.status.is_lost(CatGroup.PLAYER_CLAN_ID)
            and not self.cat.status.is_former_clancat
            and self.suffix
        ):
            # these are cats who were born to a parent who'd been lost frm their clan, and who's parent decided to keep with traditional naming
            age_to_rank = {
                CatAge.NEWBORN: CatRank.NEWBORN,
                CatAge.KITTEN: CatRank.KITTEN,
                CatAge.ADOLESCENT: CatRank.APPRENTICE,
            }
            if self.cat.age in age_to_rank:
                rank = age_to_rank[self.cat.age]
                return self.prefix + self.names_dict["special_suffixes"][rank]
            else:
                return self.prefix + self.suffix

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


Name.load_localized_names()
