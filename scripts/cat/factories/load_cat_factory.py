from typing import Dict, Tuple, Optional

from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.enums import CatAge
from scripts.cat.factories.base_factory import BaseCatFactory


class LoadCatFactory(BaseCatFactory):
    cat_id = None

    def __init__(self, rng):
        pass  # no need for RNG in cat loading

    def create_cat(self, **kwargs) -> Cat:
        """
        Takes a dict from save data & constructs the cat
        :param kwargs: save file dict
        :return:
        """
        if "ID" not in kwargs:
            raise KeyError("Cat ID missing!")
        self.cat_id = kwargs["ID"]

        pelt_params = self._build_pelt_dict(kwargs)

        gender = {
            "sex": kwargs["gender"],
            "genderalign": kwargs.get("gender_align", kwargs["gender"]),
            "pronouns": kwargs.get("pronouns")
        }

        inheritance = {
            "parent1": kwargs["parent1"],
            "parent2": kwargs["parent2"],
            "adoptive_parents": kwargs.get("adoptive_parents", [])
        }

        cat_params = {
            "ID": self.cat_id,
            "prefix": kwargs["name_prefix"],
            "suffix": kwargs["name_suffix"],
            "specsuffix_hidden": kwargs.get("specsuffix_hidden", False),
            "gender": gender,
            "status": self._convert_status(kwargs.get("status"), kwargs.get("moons")),
            "parent1": kwargs["parent1"],
            "parent2": kwargs["parent2"],
            "moons": kwargs["moons"],
            "eye_colour": pelt_params["eye_colour"],
            "loading_cat": True,
            "backstory": self._convert_backstory(kwargs.get("backstory"))
        }

    def _convert_status(self, status, moons) -> Dict:
        """
        Check & convert status
        :param status: Possible status
        :return: valid status
        """
        if status is None:
            raise TypeError(f"Status is None for cat ID: {self.cat_id}")
        if moons is None:
            raise TypeError(f"Moons is None for cat ID: {self.cat_id}")

        if isinstance(status, str):
            age = CatAge.get_from_moons(moons)
            return {"rank": status, "age": age}

        return status

    def _convert_eye_color(self, eye_color, eye_color2) -> Tuple[str, Optional[str]]:
        """
        Convert old eye colors to new format
        :param eye_color: Primary eye color
        :param eye_color2: Secondary eye color, if present
        :return: Primary eye color and secondary eye color / None if homochromia
        """
        if eye_color == "BLUE2":
            eye_color = "COBALT"
        if eye_color in ["BLUEYELLOW", "BLUEGREEN"]:
            # splits into BLUE and either YELLOW or GREEN
            return eye_color[:4], eye_color[4:]
        if eye_color2 == "BLUE2":
            eye_color2 = "COBALT"

        return eye_color, eye_color2

    def _build_pelt_dict(self, kwargs):
        """
        Handles some check & convert functionality for pelts
        :param kwargs: Everything we've ever passed into the factory
        :return: A dict of the keys needed to build the pelt
        """
        eye_colour, eye_colour2 = self._convert_eye_color(
            kwargs["eye_colour"], kwargs.get("eye_color2")
        )

        if kwargs.get("tint") == "none":
            kwargs["tint"] = None
        if kwargs.get("white_patches_tint") == "none":
            kwargs["white_patches_tint"] = None
            # this then gets set to "offwhite" later

        if pattern:= kwargs.get("pattern"):
            kwargs["tortie_pattern"] = pattern

        # just to be sure that scars exists as a list
        kwargs["scars"] = kwargs.get("scars", [])

        for specialty in ("specialty", "specialty2"):
            if old_scars := kwargs.get(specialty):
                kwargs["scars"] = [*kwargs["scars"], old_scars]

        return {
            "name": kwargs["pelt_name"],
            "length": kwargs["pelt_length"],
            "colour": kwargs["pelt_colour"],
            "eye_colour": eye_colour,
            "eye_colour2": eye_colour2,
            "paralyzed": kwargs["paralyzed"],
            "newborn_sprite": kwargs.get("sprite_newborn"),
            "kitten_sprite": kwargs.get("sprite_kitten", kwargs["spirit_kitten"]),
            "adol_sprite": kwargs.get("sprite_adolescent", kwargs["spirit_adolescent"]),
            "adult_sprite": kwargs.get("sprite_adult", kwargs["spirit_adult"]),
            "senior_sprite": kwargs.get("sprite_senior", kwargs["spirit_senior"]),
            "para_adult_sprite": kwargs.get("sprite_para_adult"),
            "reverse": kwargs["reverse"],
            "vitiligo": kwargs.get("vitiligo"),
            "points": kwargs.get("points"),
            "white_patches_tint": kwargs.get("white_patches_tint", "offwhite"),
            "white_patches": kwargs.get("white_patches"),
            "tortie_base": kwargs.get("tortie_base"),
            "tortie_colour": kwargs.get("tortie_colour"),
            "tortie_pattern": kwargs.get("tortie_pattern"),
            "tortie_marking": kwargs.get("tortie_marking"),
            "skin": kwargs.get("skin"),
            "tint": kwargs.get("tint"),
            "scars": kwargs["scars"],
            "accessory": kwargs.get("accessory", []),
            "opacity": kwargs.get("opacity", 100),
        }

    @staticmethod
    def _convert_backstory(backstory) -> str:
        """
        Convert an old-style backstory to the new version
        :param backstory:
        :return: the new-style backstory
        """
        # if the key isn't found, return it as the value (no need to convert
        return BACKSTORIES["conversion"].get(backstory, backstory)
