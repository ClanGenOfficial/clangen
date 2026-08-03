from __future__ import annotations

from random import randint, sample, choice

from scripts.cat.enums import CatRank, CatAge
from scripts.cat.factories.cat_factory import CatFactory
from scripts.cat.factories.enums import CatType
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.pelts import Pelt
from scripts.game_structure import game


def create_example_cats():
    """
    Creates the cats for MakeClanScreen
    :return: None
    """
    warrior_indices = sample(range(12), 3)

    for cat_index in range(12):
        if cat_index in warrior_indices:
            game.choose_cats[cat_index] = NewCatFactory.create_cat(
                rank=CatRank.WARRIOR, no_disabling_scars=True
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
            game.choose_cats[cat_index] = NewCatFactory.create_cat(
                rank=random_rank, no_disabling_scars=True
            )


def create_option_preview_cat(scar: str = None, acc: str = None):
    """
    Creates a cat with the specified scar and/or accessory.
    :param scar: Desired scar (only one)
    :param acc: Desired accessory (only one)
    """
    new_cat = TestCatFactory.create_cat(
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
