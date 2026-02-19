from __future__ import annotations

from random import randint, sample, choice

from scripts.cat.enums import CatRank, CatAge
from scripts.cat.factories.cat_factory import CatFactory
from scripts.cat.factories.enums import CatType
from scripts.cat.pelts import Pelt
from scripts.game_structure import game


def create_cat(rank, moons=None, biome=None, cat_type: CatType = CatType.TEST):
    status_dict = {"rank": rank}

    new_cat = CatFactory.create_cat(cat_type, status_dict=status_dict, biome=biome)

    if moons is not None:
        new_cat.moons = moons
    elif new_cat.moons >= 160:
        new_cat.moons = randint(120, 155)
    elif new_cat.moons == 0:
        new_cat.moons = randint(1, 5)

    not_allowed_scars = [
        "NOPAW",
        "NOTAIL",
        "HALFTAIL",
        "NOEAR",
        "BOTHBLIND",
        "RIGHTBLIND",
        "LEFTBLIND",
        "BRIGHTHEART",
        "NOLEFTEAR",
        "NORIGHTEAR",
        "MANLEG",
    ]

    new_cat.pelt.scars = tuple(
        scar for scar in new_cat.pelt.scars if scar not in not_allowed_scars
    )

    return new_cat


def create_example_cats():
    warrior_indices = sample(range(12), 3)

    for cat_index in range(12):
        if cat_index in warrior_indices:
            game.choose_cats[cat_index] = create_cat(
                cat_type=CatType.NEW, rank=CatRank.WARRIOR
            )
        else:
            random_rank = choice(
                [
                    CatRank.KITTEN,
                    CatRank.APPRENTICE,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.ELDER,
                ]
            )
            game.choose_cats[cat_index] = create_cat(
                cat_type=CatType.NEW, rank=random_rank
            )


def create_option_preview_cat(scar: str = None, acc: str = None):
    """
    Creates a cat with the specified scar
    """
    new_cat = CatFactory.create_cat(
        CatType.TEST,
        loading_cat=True,
        pelt=Pelt(
            name="SingleColour",
            colour="WHITE",
            length="medium",
            eye_color="SAGE",
            reverse=False,
            white_patches=None,
            vitiligo=None,
            points=None,
            tortie_marking=None,
            tortie_base=None,
            tortie_pattern=None,
            tortie_colour=None,
            tint="gray",
            skin="BLUE",
            scars=[scar] if scar else [],
            adult_sprite="8",
            accessory=[acc] if acc else [],
        ),
    )
    new_cat.age = CatAge.ADULT

    return new_cat
