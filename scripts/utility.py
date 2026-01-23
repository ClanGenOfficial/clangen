# pylint: disable=line-too-long
"""

TODO: Docs


"""  # pylint: enable=line-too-long

import logging
import os
import traceback
from random import choice
from sys import exit as sys_exit
from typing import TYPE_CHECKING

import pygame
import ujson
from pygame_gui.core import ObjectID

from scripts.cat_relations.enums import RelType
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure.game.settings import game_settings_save, game_setting_get
from scripts.ui.scale import ui_scale_dimensions

logger = logging.getLogger(__name__)
from scripts.game_structure import image_cache, constants
from scripts.cat.enums import (
    CatAge,
    CatGroup,
)
from scripts.cat.sprites import sprites
from scripts.game_structure import game

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------- #
#                               Getting Cats                                   #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                          Handling Outside Factors                            #
# ---------------------------------------------------------------------------- #


def get_current_season():
    """
    function to handle the math for finding the Clan's current season
    :return: the Clan's current season
    """

    if constants.CONFIG["lock_season"]:
        game.clan.current_season = game.clan.starting_season
        return game.clan.starting_season

    modifiers = {"Newleaf": 0, "Greenleaf": 3, "Leaf-fall": 6, "Leaf-bare": 9}
    index = game.clan.age % 12 + modifiers[game.clan.starting_season]

    if index > 11:
        index = index - 12

    game.clan.current_season = constants.SEASON_CALENDAR[index]

    return game.clan.current_season


# ---------------------------------------------------------------------------- #
#                             Cat Relationships                                #
# ---------------------------------------------------------------------------- #


# todo: kill this function. with fire.
def get_num_of_cats_with_relation_amount_towards(cat, amount, all_cats):
    """
    Looks how many cats have the certain value
    :param cat: cat in question
    :param amount: amount of relationship value which has to be reached
    :param all_cats: list of cats which has to be checked
    """

    # collect all true or false if the value is reached for the cat or not
    # later count or sum can be used to get the amount of cats
    # this will be handled like this, because it is easier / shorter to check

    relation_dict = {v: [] for v in [*RelType]}

    for inter_cat in all_cats:
        if cat.ID in inter_cat.relationships:
            relation = inter_cat.relationships[cat.ID]
        else:
            continue

        for value in [*RelType]:
            if amount > 0:
                relation_dict[value].append(
                    relation.get_amount_of_type(value) >= amount
                )
            elif amount < 0:
                relation_dict[value].append(
                    relation.get_amount_of_type(value) <= amount
                )

    return_dict = {v: sum(relation_dict[v]) for v in [*RelType]}

    return return_dict


# ---------------------------------------------------------------------------- #
#                               Text Adjust                                    #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                                    Sprites                                   #
# ---------------------------------------------------------------------------- #


def update_sprite(cat):
    # First, check if the cat is faded.
    if cat.faded:
        # Don't update the sprite if the cat is faded.
        return

    # apply
    cat.sprite = generate_sprite(cat)
    # update class dictionary
    cat.all_cats[cat.ID] = cat


def update_mask(cat):
    if cat.faded or cat.dead:
        # should never need a mask since they can't appear on the Clan screen
        cat.sprite_mask = None
        return

    val = pygame.mask.from_surface(
        pygame.transform.scale(cat.sprite, ui_scale_dimensions((50, 50))), threshold=250
    )

    inflated_mask = pygame.Mask(
        (
            val.get_size()[0] + 10,
            val.get_size()[1] + 10,
        )
    )
    inflated_mask.draw(val, (5, 5))
    for _ in range(3):
        outline = inflated_mask.outline()
        for point in outline:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    try:
                        inflated_mask.set_at((point[0] + dx, point[1] + dy), 1)
                    except IndexError:
                        continue
    cat.sprite_mask = inflated_mask


def clan_symbol_sprite(clan, return_string=False, force_light=False):
    """
    returns the clan symbol for the given clan_name, if no symbol exists then random symbol is chosen
    :param clan: the clan object
    :param return_string: default False, set True if the sprite name string is required rather than the sprite image
    :param force_light: Set true if you want this sprite to override the dark/light mode changes with the light sprite
    """
    if not clan.chosen_symbol:
        possible_sprites = []
        for sprite in sprites.clan_symbols:
            name = sprite.strip("1234567890")
            if f"symbol{clan.name.upper()}" == name:
                possible_sprites.append(sprite)
        if possible_sprites:
            clan.chosen_symbol = choice(possible_sprites)
        else:
            # give random symbol if no matching symbol exists
            print(
                f"WARNING: attempted to return symbol, but there's no clan symbol for {clan.name.upper()}. "
                f"Random chosen."
            )
            clan.chosen_symbol = choice(sprites.clan_symbols)

    if return_string:
        return clan.chosen_symbol
    else:
        return sprites.get_symbol(clan.chosen_symbol, force_light=force_light)


def generate_sprite(
    cat,
    life_state=None,
    scars_hidden=False,
    acc_hidden=False,
    always_living=False,
    disable_sick_sprite=False,
) -> pygame.Surface:
    """
    Generates the sprite for a cat, with optional arguments that will override certain things.

    :param life_state: sets the age life_stage of the cat, overriding the one set by its age. Set to string.
    :param scars_hidden: If True, doesn't display the cat's scars. If False, display cat scars.
    :param acc_hidden: If True, hide the accessory. If false, show the accessory.
    :param always_living: If True, always show the cat with living lineart
    :param disable_sick_sprite: If true, never use the not_working lineart.
                    If false, use the cat.not_working() to determine the no_working art.
    """
    sprite_poses = sprites.POSE_DATA["poses"]

    if life_state is not None:
        age = life_state
    else:
        age = cat.age

    if always_living:
        dead = False
    else:
        dead = cat.dead

    # setting the cat_sprite (bc this makes things much easier)

    # sick sprites
    if (
        not disable_sick_sprite
        and cat.not_working()
        and age != CatAge.NEWBORN
        and constants.CONFIG["cat_sprites"]["sick_sprites"]
    ):
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            cat_sprite = sprite_poses["sick_young0"]
        else:
            cat_sprite = sprite_poses["sick_adult0"]

    # paralyzed sprites
    elif cat.pelt.paralyzed and age != CatAge.NEWBORN:
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            cat_sprite = sprite_poses["para_young0"]
        else:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites["para_adult"]]

    # default sprites
    else:
        if constants.CONFIG["fun"]["all_cats_are_newborn"]:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites["newborn"]]
        else:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites[age]]

    new_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    # generating the sprite
    try:
        if cat.pelt.name not in ["Tortie", "Calico"]:
            new_sprite.blit(
                sprites.sprites[
                    cat.pelt.get_sprites_name() + cat.pelt.colour + cat_sprite
                ],
                (0, 0),
            )
        else:
            # Base Coat
            sprite_name = f"colours_{cat.pelt.tortie_base}{cat.pelt.colour}{cat_sprite}"
            new_sprite.blit(
                sprites.sprites[sprite_name],
                (0, 0),
            )

            # Create the patch image
            if cat.pelt.tortie_pattern == "Single":
                tortie_pattern = "SingleColour"
            else:
                tortie_pattern = cat.pelt.tortie_pattern

            sprite_name = (
                f"colours_{tortie_pattern}{cat.pelt.tortie_colour}{cat_sprite}"
            )
            patches = sprites.sprites[sprite_name].copy()
            sprite_name = f"{sprites.TORTIE_DATA['spritesheet']}{cat.pelt.tortie_marking}{cat_sprite}"
            patches.blit(
                sprites.sprites[sprite_name],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            # Add patches onto cat.
            new_sprite.blit(patches, (0, 0))

        # TINTS
        if (
            cat.pelt.tint is not None
            and cat.pelt.tint in sprites.cat_tints["tint_colours"]
        ):
            # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
            # entire surface. To get around this, we first blit the tint onto a white background to dull it,
            # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        if (
            cat.pelt.tint is not None
            and cat.pelt.tint in sprites.cat_tints["dilute_tint_colours"]
        ):
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # draw white patches
        if cat.pelt.white_patches is not None:
            sprite_name = f"{sprites.WHITE_DATA['spritesheet']}{cat.pelt.white_patches}{cat_sprite}"
            white_patches = sprites.sprites[sprite_name].copy()

            # Apply tint to white patches.
            if (
                cat.pelt.white_patches_tint is not None
                and cat.pelt.white_patches_tint
                in sprites.white_patches_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(
                    tuple(
                        sprites.white_patches_tints["tint_colours"][
                            cat.pelt.white_patches_tint
                        ]
                    )
                )
                white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            new_sprite.blit(white_patches, (0, 0))

        # draw vit & points

        if cat.pelt.points:
            sprite_name = (
                f"{sprites.WHITE_DATA['spritesheet']}{cat.pelt.points}{cat_sprite}"
            )

            points = sprites.sprites[sprite_name].copy()
            if (
                cat.pelt.white_patches_tint is not None
                and cat.pelt.white_patches_tint
                in sprites.white_patches_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(
                    tuple(
                        sprites.white_patches_tints["tint_colours"][
                            cat.pelt.white_patches_tint
                        ]
                    )
                )
                points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            new_sprite.blit(points, (0, 0))

        if cat.pelt.vitiligo:
            sprite_name = (
                f"{sprites.WHITE_DATA['spritesheet']}{cat.pelt.vitiligo}{cat_sprite}"
            )

            new_sprite.blit(
                sprites.sprites[sprite_name],
                (0, 0),
            )

        # draw eyes & scars1
        sprite_name = (
            f"{sprites.EYE_DATA['spritesheet'][0]}{cat.pelt.eye_colour}{cat_sprite}"
        )
        eyes = sprites.sprites[sprite_name].copy()
        if cat.pelt.eye_colour2 != None:
            sprite_name = f"{sprites.EYE_DATA['spritesheet'][1]}{cat.pelt.eye_colour2}{cat_sprite}"
            eyes.blit(
                sprites.sprites[sprite_name],
                (0, 0),
            )
        new_sprite.blit(eyes, (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.general_scars:
                    sprite_name = (
                        f"{sprites.SCAR_DATA['spritesheet']}{scar}{cat_sprite}"
                    )
                    new_sprite.blit(
                        sprites.sprites[sprite_name],
                        (0, 0),
                    )

        # setting the lineart color to override on accessories & missing bits
        lineart_color = (
            pygame.Color(
                constants.CONFIG["cat_sprites"]["lineart_color_sc"]
                if cat.status.group == CatGroup.STARCLAN
                else constants.CONFIG["cat_sprites"]["lineart_color_df"]
            )
            if cat.status.group != CatGroup.UNKNOWN_RESIDENCE
            else None
        )

        gradient_surface = (
            sprites.sprites["line_ur_gradient" + cat_sprite]
            if dead and cat.status.group == CatGroup.UNKNOWN_RESIDENCE
            else None
        )

        def _recolor_lineart(
            sprite, color=None, source: pygame.Surface = None
        ) -> pygame.Surface:
            """
            Helper function to set the appropriate lineart color for the living status of the cat
            :param sprite: lineart to recolor
            :param color: color to apply to all pixels
            :param source: source surface of same size as sprite to use instead of color
            :return:
            """
            if not dead:
                return sprite

            if color is None and source is None:
                raise ValueError(
                    "Must provide either `color` or `source` for _recolor_lineart"
                )

            out = sprite.copy()
            if color:
                pixel_array = pygame.PixelArray(out)
                pixel_array.replace((0, 0, 0), color, distance=0)
                del pixel_array
                return out

            width, height = sprite.get_size()
            for x in range(width):
                for y in range(height):
                    if sprite.get_at((x, y)) == pygame.Color(0, 0, 0):
                        color = source.get_at((x, y))
                        sprite.set_at((x, y), color)
            return out

        # draw line art
        if game_setting_get("shaders") and not dead:
            new_sprite.blit(
                sprites.sprites["shader_mask" + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGB_MULT,
            )
            new_sprite.blit(sprites.sprites["shader_lighting" + cat_sprite], (0, 0))

        if not dead:
            new_sprite.blit(sprites.sprites["lineart" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
            new_sprite.blit(sprites.sprites["lineart_ur" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.DARK_FOREST:
            new_sprite.blit(sprites.sprites["lineart_df" + cat_sprite], (0, 0))
        elif dead:
            new_sprite.blit(sprites.sprites["lineart_sc" + cat_sprite], (0, 0))
        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        sprite_name = f"{sprites.SKIN_DATA['spritesheet']}{cat.pelt.skin}{cat_sprite}"
        new_sprite.blit(
            sprites.sprites[sprite_name],
            (0, 0),
        )

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.missing_part_scars:
                    sprite_name = f"{sprites.SCAR_MISSING_PART_DATA['spritesheet']}{scar}{cat_sprite}"
                    new_sprite.blit(
                        _recolor_lineart(
                            sprites.sprites[sprite_name],
                            lineart_color,
                            gradient_surface,
                        ),
                        (0, 0),
                        special_flags=blendmode,
                    )

        # draw accessories
        from scripts.cat.pelts import Pelt

        if not acc_hidden and cat.pelt.accessory:
            cat_accessories = cat.pelt.accessory
            categories = [
                "collar_accessories",
                "tail_accessories",
                "body_accessories",
                "head_accessories",
            ]
            for category in categories:
                for accessory in cat_accessories:
                    if accessory in getattr(Pelt, category):
                        if accessory in cat.pelt.plant_accessories:
                            sprite_name = f"{sprites.PLANT_DATA['spritesheet']}{accessory}{cat_sprite}"
                            new_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )
                        elif accessory in cat.pelt.wild_accessories:
                            sprite_name = f"{sprites.WILD_DATA['spritesheet']}{accessory}{cat_sprite}"
                            new_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )
                        elif accessory in cat.pelt.collar_accessories:
                            sprite_name = f"{sprites.COLLAR_DATA['spritesheet']}{accessory}{cat_sprite}"
                            new_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )

        # Apply fading fog
        if (
            cat.pelt.opacity <= 97
            and not cat.prevent_fading
            and get_clan_setting("fading")
            and dead
        ):
            stage = "0"
            if 80 >= cat.pelt.opacity > 45:
                # Stage 1
                stage = "1"
            elif cat.pelt.opacity <= 45:
                # Stage 2
                stage = "2"

            new_sprite.blit(
                sprites.sprites["fademask" + stage + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            if cat.status.group == CatGroup.STARCLAN:
                temp = sprites.sprites["fadestarclan" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
                temp = sprites.sprites["fadeur" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites["fadedf" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        # ok! we have the sprite! now, do some layer things if the cat's already dead
        if dead:
            temp_sprite = pygame.Surface(
                (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
            )

            if cat.status.group == CatGroup.STARCLAN:
                # no underlay

                # cat sprite
                temp_sprite.blit(new_sprite, (0, 0))

                # overlay
                temp_sprite.blit(
                    sprites.sprites["line_sc_overlay" + cat_sprite],
                    (0, 0),
                )
            elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
                # underlay
                temp_sprite.blit(
                    sprites.sprites["line_ur_overlay" + cat_sprite],
                    (0, 0),
                )

                # cat sprite
                temp_sprite.blit(new_sprite, (0, 0))

                # overlay
                temp_sprite.blit(
                    sprites.sprites["line_ur_overlay" + cat_sprite],
                    (0, 0),
                )
            elif cat.status.group == CatGroup.DARK_FOREST:
                # no underlay

                # cat sprite
                temp_sprite.blit(new_sprite, (0, 0))

                # no overlay

            new_sprite = temp_sprite

        # reverse, if assigned so
        if cat.pelt.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

    except (TypeError, KeyError):
        traceback.print_exc()
        logger.exception("Failed to load sprite")

        # Placeholder image
        new_sprite = image_cache.load_image(
            f"sprites/error_placeholder.png"
        ).convert_alpha()

    return new_sprite


# ---------------------------------------------------------------------------- #
#                                     OTHER                                    #
# ---------------------------------------------------------------------------- #


def chunks(L, n):
    return [L[x : x + n] for x in range(0, len(L), n)]


def clamp(value: float, minimum_value: float, maximum_value: float) -> float:
    """
    Takes a value and returns it constrained to a certain range
    :param value: The input value
    :param minimum_value: Lower bound
    :param maximum_value: Upper bound
    :return: Clamped float.
    """
    if value < minimum_value:
        return minimum_value
    elif value > maximum_value:
        return maximum_value
    return value


def is_iterable(y):
    try:
        0 in y
    except TypeError:
        return False


def get_text_box_theme(theme_name=None):
    """Updates the name of the theme based on dark or light mode"""
    if game_setting_get("dark mode"):
        return ObjectID("#dark", theme_name)
    else:
        return theme_name


def quit_game(savesettings=False, clearevents=False):
    """
    Quits the game, avoids a bunch of repeated lines
    """
    if savesettings:
        game_settings_save(None)
    if clearevents:
        game.cur_events_list.clear()
    game.rpc.close_rpc.set()
    game.rpc.update_rpc.set()
    pygame.display.quit()
    pygame.quit()
    if game.rpc.is_alive():
        game.rpc.join(1)
    sys_exit()


resource_directory = "resources/dicts/conditions/"
with open(
    os.path.normpath(f"{resource_directory}illnesses.json"), "r", encoding="utf-8"
) as read_file:
    ILLNESSES = ujson.loads(read_file.read())

with open(
    os.path.normpath(f"{resource_directory}injuries.json"), "r", encoding="utf-8"
) as read_file:
    INJURIES = ujson.loads(read_file.read())

with open(
    os.path.normpath(f"{resource_directory}permanent_conditions.json"),
    "r",
    encoding="utf-8",
) as read_file:
    PERMANENT = ujson.loads(read_file.read())

langs = {"snippet": None, "prey": None}

SNIPPETS = None
PREY_LISTS = None

with open(
    os.path.normpath("resources/dicts/backstories.json"), "r", encoding="utf-8"
) as read_file:
    BACKSTORIES = ujson.loads(read_file.read())
