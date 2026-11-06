from random import Random
from typing import Dict, Tuple, Optional, Union, List

import ujson

from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.enums import CatAge, CatGroup
from scripts.cat.factories.base_factory import BaseCatFactory
from scripts.cat.factories.typed_dicts import (
    MentorshipDict,
    CatTogglesDict,
    GenderDict,
    InheritanceDict,
    AfterlifeAffinityDict,
)
from scripts.cat.history import History
from scripts.cat.names import Name
from scripts.cat.pelts import Pelt
from scripts.cat.personality import Personality
from scripts.cat.skills import CatSkills
from scripts.cat.status import Status


class LoadCatFactory(BaseCatFactory):
    cat_id = None
    rng = Random()

    with open(
        f"resources/dicts/conversion_dict.json", "r", encoding="utf-8"
    ) as read_file:
        CONVERT = ujson.loads(read_file.read())

    @classmethod
    def create_cat(cls, **kwargs) -> Cat:
        """
        Takes a dict from save data & constructs the cat
        :param kwargs: save file dict
        :return:
        """
        if "ID" not in kwargs:
            raise KeyError("Cat ID missing!")
        cls.cat_id = kwargs["ID"]

        pelt = cls._build_pelt(kwargs=kwargs)

        gender = GenderDict(
            sex=kwargs["gender"],
            genderalign=kwargs.get("gender_align", kwargs["gender"]),
            pronouns=kwargs.get("pronouns"),
        )

        mate = kwargs.get("mate", [])
        inheritance = InheritanceDict(
            parent1=kwargs["parent1"],
            parent2=kwargs["parent2"],
            adoptive_parents=kwargs.get("adoptive_parents", []),
            faded_offspring=kwargs.get("faded_offspring", []),
            mate=mate if isinstance(mate, list) else [mate],
            previous_mates=kwargs.get("previous_mates", []),
        )

        mentorship = MentorshipDict(
            mentor=kwargs["mentor"],
            former_mentor=kwargs.get("former_mentor", []),
            patrol_with_mentor=kwargs.get("patrol_with_mentor", 0),
            apprentice=kwargs["current_apprentice"],
            former_apprentices=kwargs["former_apprentices"],
        )

        toggles = CatTogglesDict(
            no_kits=kwargs.get("no_kits", False),
            no_mates=kwargs.get("no_mates", False),
            no_retire=kwargs.get("no_retire", False),
            prevent_fading=kwargs.get("prevent_fading", False),
            favourite=kwargs.get("favourite", False),
        )

        status = cls._convert_status(
            kwargs.get("status"),
            kwargs.get("moons"),
            old_bools=[
                kwargs.get("dead"),
                kwargs.get("df"),
                kwargs.get("driven_out"),
                kwargs.get("exiled"),
                kwargs.get("outside"),
            ],
        )

        backstory = cls._convert_backstory(kwargs.get("backstory"))
        skills, backstory = cls._convert_skill_and_backstory(
            kwargs.get("skill_dict"),
            kwargs.get("skill"),
            backstory,
            status.rank,
            CatAge.get_from_moons(kwargs["moons"]),
        )

        affinity = AfterlifeAffinityDict(
            starclan=kwargs.get("starclan_affinity", 0),
            dark_forest=kwargs.get("dark_forest_affinity", 0),
        )

        cat_params = {
            "ID": cls.cat_id,
            "gender_dict": gender,
            "pelt": pelt,
            "moons": kwargs["moons"],
            "status": status,
            "backstory": backstory,
            "skills": skills,
            "personality": cls._build_personality(
                kwargs.get("facets"),
                kwargs["trait"],
                CatAge.get_from_moons(kwargs["moons"]).is_baby(),
            ),
            "mentorship": mentorship,
            "inheritance": inheritance,
            "affinity": affinity,
            "toggles": toggles,
            "experience": kwargs.get("experience"),
            "birth_cooldown": kwargs.get("birth_cooldown", 0),
            "specsuffix_hidden": kwargs.get("specsuffix_hidden", False),
        }

        cat = Cat(**cat_params)

        # Unfortunately, these two have to be handled *after* the creation of the cat
        # because of the horrible nested cat. fixme.
        if "died_by" in kwargs or "scar_event" in kwargs:
            cat.history = cls._convert_history(
                kwargs.get("died_by", []), kwargs.get("scar_event", []), cat=cat
            )
        cat.name = Name(
            prefix=kwargs["name_prefix"],
            suffix=kwargs["name_suffix"],
            specsuffix_hidden=kwargs.get("specsuffix_hidden", False),
            load_existing_name=True,
            cat=cat,
        )
        return cat

    @classmethod
    def _convert_status(
        cls,
        status_dict: Optional[Union[Dict, str]],
        moons: int,
        old_bools: List[Optional[bool]],
    ) -> Status:
        """
        Check & convert status to new Status
        :param status_dict: Possible status_dict
        :param moons: age in moons
        :param old_bools: old-style status bools in a list
        :return: valid status
        """
        if status_dict is None:
            raise TypeError(f"Status is None for cat ID: {cls.cat_id}")
        if moons is None:
            raise TypeError(f"Moons is None for cat ID: {cls.cat_id}")

        if isinstance(status_dict, str):
            age = CatAge.get_from_moons(moons)
            status = Status(rank=status_dict, age=age)
        else:
            status = Status(**status_dict)

        if not any(old_bools):
            # either they're not present or all False
            return status

        dead, df, driven_out, exiled, outside = old_bools

        if dead and not status.group.is_afterlife():
            if df:
                status.send_to_afterlife(target_ID=CatGroup.DARK_FOREST_ID)
            elif outside:
                status.send_to_afterlife(target_ID=CatGroup.UNKNOWN_RESIDENCE_ID)
            else:
                status.send_to_afterlife(target_ID=CatGroup.STARCLAN_ID)
        elif exiled:
            status.exile_from_group()
        elif outside and not status.is_outsider:
            status.become_lost()

        if driven_out:
            status.change_group_nearness(CatGroup.PLAYER_CLAN_ID)

        return status

    @staticmethod
    def _convert_eye_color(eye_color, eye_color2) -> Tuple[str, Optional[str]]:
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

    @classmethod
    def _build_pelt(cls, kwargs) -> Pelt:
        """
        Handles some check & convert functionality for pelts
        :param kwargs: Everything we've ever passed into the factory
        :return: A dict of the keys needed to build the pelt
        """
        eye_colour, eye_colour2 = cls._convert_eye_color(
            kwargs["eye_colour"], kwargs.get("eye_colour2")
        )

        if isinstance(kwargs.get("tint"), str) and kwargs.get("tint").lower() == "none":
            kwargs["tint"] = None
        if (
            isinstance(kwargs.get("white_patches_tint"), str)
            and kwargs.get("white_patches_tint").lower() == "none"
        ):
            kwargs["white_patches_tint"] = None
            # this then gets set to "offwhite" later

        if "pattern" in kwargs:
            kwargs["tortie_marking"] = kwargs["pattern"]
            del kwargs["pattern"]

        # just to be sure that scars exists as a list
        kwargs["scars"] = kwargs.get("scars", [])

        for specialty in ("specialty", "specialty2"):
            if old_scars := kwargs.get(specialty):
                kwargs["scars"] = tuple([*kwargs["scars"], old_scars])

        pelt = Pelt(
            **{
                "name": kwargs["pelt_name"],
                "length": kwargs["pelt_length"],
                "colour": kwargs.get("pelt_color"),
                "eye_color": eye_colour,
                "eye_colour2": eye_colour2,
                "paralyzed": kwargs["paralyzed"],
                "newborn_sprite": kwargs.get("sprite_newborn"),
                "kitten_sprite": kwargs.get(
                    "sprite_kitten", kwargs.get("spirit_kitten")
                ),
                "adol_sprite": kwargs.get(
                    "sprite_adolescent", kwargs.get("spirit_adolescent")
                ),
                "adult_sprite": kwargs.get("sprite_adult", kwargs.get("spirit_adult")),
                "senior_sprite": kwargs.get(
                    "sprite_senior", kwargs.get("spirit_senior")
                ),
                "para_adult_sprite": kwargs.get("sprite_para_adult"),
                "reverse": kwargs["reverse"],
                "vitiligo": kwargs.get("vitiligo"),
                "points": kwargs.get("points"),
                "white_patches_tint": kwargs.get("white_patches_tint", "offwhite"),
                "white_patches": kwargs["white_patches"],
                "tortie_base": kwargs["tortie_base"],
                "tortie_colour": kwargs["tortie_color"],
                "tortie_pattern": kwargs["tortie_pattern"],
                "tortie_marking": kwargs["tortie_marking"],
                "skin": kwargs.get("skin"),
                "tint": kwargs.get("tint"),
                "scars": kwargs["scars"],
                "accessory": kwargs.get("accessory", []),
                "opacity": kwargs.get("opacity", 100),
            }
        )
        pelt.check_and_convert(convert_dict=cls.CONVERT)

        return pelt

    @staticmethod
    def _convert_backstory(backstory) -> str:
        """
        Convert an old-style backstory to the new version
        :param backstory:
        :return: the new-style backstory
        """
        # if the key isn't found, return it as the value (no need to convert)
        return BACKSTORIES["conversion"].get(backstory, backstory)

    @classmethod
    def _build_personality(
        cls, facets: str, trait: str, is_kit_trait: bool
    ) -> Personality:
        """
        Builds the personality object from the inputs provided
        :param facets: Cat's facet string
        :param trait: Provided trait
        :param is_kit_trait: True if the cat is kit-aged, False otherwise
        :return: Personality object
        """
        if facets is not None:
            facets = [int(i) for i in facets.split(",")]
            return Personality(
                trait=trait,
                kit_trait=is_kit_trait,
                lawful=facets[0],
                social=facets[1],
                aggress=facets[2],
                stable=facets[3],
            )
        else:
            print(f"WARNING: no facets found for cat ID: {cls.cat_id}")
            return Personality(trait=trait, kit_trait=is_kit_trait)

    @classmethod
    def _convert_skill_and_backstory(
        cls, skill_dict, skill, backstory, rank, age
    ) -> Tuple[CatSkills, str]:
        """
        Handle conversion of some *very old* skills & backstories
        :param skill_dict: modern skill dict
        :param skill: skill string
        :param backstory: backstory string
        :param rank: needed to generate new skills
        :param age: needed to generate new skills
        :return:
        """
        if skill_dict:
            return CatSkills(skill_dict), backstory
        if skill:
            if backstory is not None:
                if skill == "formerly a loner":
                    backstory = cls.rng.choice(BACKSTORIES["loner_backstories"])
                elif skill == "formerly a kittypet":
                    backstory = cls.rng.choice(BACKSTORIES["kittypet_backstories"])
                else:
                    backstory = "clanborn"
            return CatSkills.get_skills_from_old(skill, rank, age), backstory
        else:
            raise Exception(f"No skill data provided for cat ID: {cls.cat_id}")

    @staticmethod
    def _convert_history(died_by, scar_events, cat) -> History:
        """
        Converts some very, very old saves to modern ClanGen
        :param died_by: What killed this cat
        :param scar_events: What happened when they got scarred
        :param cat: The cat in question
        :return: A new History object that describes the cat
        """
        deaths = []
        if died_by:
            deaths.extend(
                {"involved": None, "text": death, "moon": "?"} for death in died_by
            )
        scars = []
        if scar_events:
            scars.extend(
                {"involved": None, "text": scar, "moon": "?"} for scar in scar_events
            )
        return History(died_by=deaths, scar_events=scars, cat=cat)
