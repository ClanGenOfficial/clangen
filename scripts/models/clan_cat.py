from schema import Schema, Or, Optional, SchemaError,SchemaUnexpectedTypeError
import traceback
from ..game_structure.game_essentials import game
clan_cat_schema = Schema(
    {
    "ID": str,
    "name_prefix": str,
    "name_suffix": str,
    "specsuffix_hidden": bool,
    "gender": str,
    "gender_align": str,
    Optional("birth_cooldown", default=0): int,
    "status": str,
    Optional("backstory", default="clan_founder"): str,
    "moons": int,
    "trait": str,
    "facets": str,
    Optional("parent1", default=None): Or(str, None),
    Optional("parent2", default=None): Or(str, None),
    Optional("adoptive_parents", default=[]): list,
    Optional("mentor", default=None): Or(str, None),
    Optional("former_mentor", default=[]): list,
    Optional("patrol_with_mentor", default=0): int,
    Optional("mate", default=[]): list,
    Optional("previous_mates", default=[]): list,
    Optional("dead", default=True): bool,
    Optional("paralyzed", default=False): bool,
    Optional("no_kits", default=False): bool,
    Optional("no_retire", default=False): bool,
    Optional("no_mates", default=False): bool,
    Optional("exiled", default=False): bool,
    "pelt_name": str,
    "pelt_color": str,
    "pelt_length": str,
    "sprite_kitten": int,
    "sprite_adolescent": int,
    "sprite_adult": int,
    "sprite_senior": int,
    "sprite_para_adult": int,
    "eye_colour": str,
    Optional("eye_colour2", default=None): Or(str, None),
    "reverse": bool,
    "white_patches": Or(str, None),
    Optional("vitiligo", default=None): Or(str, None),
    Optional("points", default=None): Or(str, None),
    "white_patches_tint": str,
    Optional("pattern", default=None): Or(str, None),
    Optional("tortie_base", default=None): Or(str, None),
    Optional("tortie_color", default=None): Or(str, None),
    Optional("tortie_pattern", default=None): Or(str, None),
    "skin": str,
    "tint": str,
    "skill_dict": {
        Optional("primary", default=None): Or(str, None),
        Optional("secondary", default=None): Or(str, None),
        Optional("hidden", default=None): Or(str, None),
    },
    Optional("scars", default=[]): list,
    Optional("accessory", default=None): Or(str, None),
    "experience": int,
    Optional("dead_moons", default=0): int,
    Optional("current_apprentice", default=[]): list,
    Optional("former_apprentices", default=[]): list,
    Optional("df", default=False): bool,
    Optional("outside", default=False): bool,
    Optional("faded_offspring", default=[]): list,
    Optional("opacity", default=100): int,
    Optional("prevent_fading", default=False): bool,
    Optional("favourite", default=False): bool,
    }
)


def get_validated_clan_cat_data(cat: dict):
    data = clan_cat_schema.validate(cat)
    return data

def get_all_validated_clan_cats_data(catData: list) -> dict:
    data = []
    for cat in catData:
        data.append(clan_cat_schema.validate(cat))
    return data