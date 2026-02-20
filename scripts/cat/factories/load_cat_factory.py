from typing import Dict, Tuple, Optional, List, TYPE_CHECKING

import ujson

from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.factories.base_factory import BaseCatFactory
from scripts.cat.factories.cat_mapper import CatMapper
from scripts.cat.history import History
from scripts.cat.names import Name
from scripts.cat.skills import CatSkills

if TYPE_CHECKING:
    from random import Random


class LoadCatFactory(BaseCatFactory):
    cat_id = None

    with open(
        f"resources/dicts/conversion_dict.json", "r", encoding="utf-8"
    ) as read_file:
        CONVERT = ujson.loads(read_file.read())

    def __init__(self, rng: "Random", mapper: CatMapper = CatMapper()):
        self.rng = rng  # needed for converting skills from old format
        self.mapper = (
            mapper  # typehinted atm as the pure Mapper but can become a Protocol later
        )

    def create_cat(
        self,
        ID: str,
        name_prefix: str,
        name_suffix: str,
        specsuffix_hidden: bool,
        gender: str,
        gender_align: str,
        pronouns: Dict,
        birth_cooldown: int,
        status: Dict,
        dark_forest_affinity: int,
        starclan_affinity: int,
        backstory: str,
        moons: int,
        trait: str,
        facets: str,
        parent1: Optional[str],
        parent2: Optional[str],
        adoptive_parents: List,
        mentor: Optional[str],
        former_mentor: List,
        patrol_with_mentor: int,
        mate: List,
        previous_mates: List,
        paralyzed: bool,
        no_kits: bool,
        no_retire: bool,
        no_mates: bool,
        pelt_name: str,
        pelt_color: str,
        pelt_length: str,
        sprite_newborn: str,
        sprite_kitten: str,
        sprite_adolescent: str,
        sprite_adult: str,
        sprite_senior: str,
        sprite_para_adult: str,
        eye_colour: str,
        eye_colour2: Optional[str],
        reverse: bool,
        white_patches: Optional[str],
        vitiligo: Optional[str],
        points: Optional[str],
        white_patches_tint: Optional[str],
        tortie_marking: Optional[str],
        tortie_base: Optional[str],
        tortie_color: Optional[str],
        tortie_pattern: Optional[str],
        skin: str,
        tint: str,
        skill_dict: Dict,
        scars: List,
        accessory: List,
        experience: int,
        current_apprentice: List,
        former_apprentices: List,
        faded_offspring: List,
        opacity: int,
        prevent_fading: bool,
        favourite: bool,
        **kwargs,
    ) -> Cat:
        """
        Takes a dict from save data & constructs the cat
        :return:
        """
        if not ID:
            raise KeyError("Cat ID missing!")
        if not isinstance(ID, str) or not ID.isdigit():
            raise ValueError(f"Cat ID '{ID}' is not a numerical string!")
        self.cat_id = ID

        cat = Cat(
            **self.mapper.map(
                ID,
                name_prefix,
                name_suffix,
                specsuffix_hidden,
                gender,
                gender_align,
                pronouns,
                birth_cooldown,
                status,
                dark_forest_affinity,
                starclan_affinity,
                backstory,
                moons,
                trait,
                facets,
                parent1,
                parent2,
                adoptive_parents,
                mentor,
                former_mentor,
                patrol_with_mentor,
                mate,
                previous_mates,
                paralyzed,
                no_kits,
                no_retire,
                no_mates,
                pelt_name,
                pelt_color,
                pelt_length,
                sprite_newborn,
                sprite_kitten,
                sprite_adolescent,
                sprite_adult,
                sprite_senior,
                sprite_para_adult,
                eye_colour,
                eye_colour2,
                reverse,
                white_patches,
                vitiligo,
                points,
                white_patches_tint,
                tortie_marking,
                tortie_base,
                tortie_color,
                tortie_pattern,
                skin,
                tint,
                skill_dict,
                scars,
                accessory,
                experience,
                current_apprentice,
                former_apprentices,
                faded_offspring,
                opacity,
                prevent_fading,
                favourite,
            )
        )
        cat.name = Name(
            prefix=name_prefix,
            suffix=name_suffix,
            specsuffix_hidden=specsuffix_hidden,
            load_existing_name=True,
            cat=cat,
        )
        print(f"WARNING: Unused kwargs: {[c for c in kwargs.keys()]}")
        return cat

    # @staticmethod
    # def _convert_backstory(backstory) -> str:
    #     """
    #     Convert an old-style backstory to the new version
    #     :param backstory:
    #     :return: the new-style backstory
    #     """
    #     # if the key isn't found, return it as the value (no need to convert
    #     return BACKSTORIES["conversion"].get(backstory, backstory)
    #
    # def _convert_skill(
    #     self, skill_dict, skill, backstory, rank, age
    # ) -> Tuple[CatSkills, str]:
    #     """
    #     Handle conversion of some *very old* skills & backstories
    #     :param skill_dict: modern skill dict
    #     :param skill: skill string
    #     :param backstory: backstory string
    #     :param rank: needed to generate new skills
    #     :param age: needed to generate new skills
    #     :return:
    #     """
    #     if skill_dict:
    #         return CatSkills(skill_dict), backstory
    #     if skill:
    #         if backstory is not None:
    #             if skill == "formerly a loner":
    #                 backstory = self.rng.choice(BACKSTORIES["loner_backstories"])
    #             elif skill == "formerly a kittypet":
    #                 backstory = self.rng.choice(BACKSTORIES["kittypet_backstories"])
    #             else:
    #                 backstory = "clanborn"
    #         return CatSkills.get_skills_from_old(skill, rank, age), backstory
    #     else:
    #         raise Exception(f"No skill data provided for cat ID: {self.cat_id}")
    #
    # def _convert_history(self, died_by, scar_events, cat) -> History:
    #     """
    #     Unfortunately, this has to be handled *after* the creation of the cat
    #     because of the horrible nested cat. fixme.
    #     :param died_by:
    #     :param scar_events:
    #     :param cat:
    #     :return:
    #     """
    #     deaths = []
    #     if died_by:
    #         deaths.extend(
    #             {"involved": None, "text": death, "moon": "?"} for death in died_by
    #         )
    #     scars = []
    #     if scar_events:
    #         scars.extend(
    #             {"involved": None, "text": scar, "moon": "?"} for scar in scar_events
    #         )
    #     return History(died_by=deaths, scar_events=scars, cat=cat)
