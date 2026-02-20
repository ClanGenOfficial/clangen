from typing import Optional, Dict, List

from scripts.cat.enums import CatAge
from scripts.cat.factories.typed_dicts import (
    InheritanceDict,
    MentorshipDict,
    CatTogglesDict,
    AfterlifeAffinityDict,
    GenderDict,
)
from scripts.cat.pelts import Pelt
from scripts.cat.personality import Personality
from scripts.cat.skills import CatSkills
from scripts.cat.status import Status


class CatMapper:
    """
    Save mapping for the latest save ver (4) to Cat object.
    """

    @staticmethod
    def map(
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
    ):
        if facets is None:
            print(f"WARNING: no facets found for cat ID: {ID}")
            personality = Personality(
                trait=trait, kit_trait=CatAge.get_from_moons(moons).is_baby()
            )
        else:
            facets = [int(i) for i in facets.split(",")]
            personality = Personality(
                trait=trait,
                kit_trait=CatAge.get_from_moons(moons).is_baby(),
                lawful=facets[0],
                social=facets[1],
                aggress=facets[2],
                stable=facets[3],
            )

        return {
            "ID": ID,
            "name": {
                "prefix": name_prefix,
                "suffix": name_suffix,
                "specsuffix_hidden": specsuffix_hidden,
            },
            "gender_dict": GenderDict(
                sex=gender,
                genderalign=gender_align,
                pronouns=pronouns,
            ),
            "pelt": Pelt(
                **{
                    "name": pelt_name,
                    "length": pelt_length,
                    "colour": pelt_color,
                    "eye_color": eye_colour,
                    "eye_colour2": eye_colour2,
                    "paralyzed": paralyzed,
                    "newborn_sprite": sprite_newborn,
                    "kitten_sprite": sprite_kitten,
                    "adol_sprite": sprite_adolescent,
                    "adult_sprite": sprite_adult,
                    "senior_sprite": sprite_senior,
                    "para_adult_sprite": sprite_para_adult,
                    "reverse": reverse,
                    "vitiligo": vitiligo,
                    "points": points,
                    "white_patches_tint": white_patches_tint,
                    "white_patches": white_patches,
                    "tortie_base": tortie_base,
                    "tortie_colour": tortie_color,
                    "tortie_pattern": tortie_pattern,
                    "tortie_marking": tortie_marking,
                    "skin": skin,
                    "tint": tint,
                    "scars": scars,
                    "accessory": tuple(
                        accessory,
                    ),
                    "opacity": opacity,
                }
            ),
            "moons": moons,
            "status": Status(**status),
            "backstory": backstory,
            "catskills": CatSkills(skill_dict),
            "personality": personality,
            "mentorship": MentorshipDict(
                mentor=mentor,
                former_mentor=former_mentor,
                patrol_with_mentor=patrol_with_mentor,
                apprentice=current_apprentice,
                former_apprentices=former_apprentices,
            ),
            "inheritance": InheritanceDict(
                parent1=parent1,
                parent2=parent2,
                adoptive_parents=adoptive_parents,
                faded_offspring=faded_offspring,
                mate=mate,
                previous_mates=previous_mates,
            ),
            "affinity": AfterlifeAffinityDict(
                starclan=starclan_affinity, dark_forest=dark_forest_affinity
            ),
            "toggles": CatTogglesDict(
                no_kits=no_kits,
                no_mates=no_mates,
                no_retire=no_retire,
                prevent_fading=prevent_fading,
                favourite=favourite,
            ),
            "experience": experience,
            "birth_cooldown": birth_cooldown,
            "specsuffix_hidden": specsuffix_hidden,
        }
