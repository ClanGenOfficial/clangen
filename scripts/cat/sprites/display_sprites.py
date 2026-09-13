import logging
import traceback

import pygame
from copy import deepcopy

from scripts.cat.enums import CatAge, CatGroup
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure import constants, image_cache
from scripts.game_structure.game import game_setting_get
from scripts.ui.scale import ui_scale_dimensions

logger = logging.getLogger(__name__)


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
    poses: list = sprites.POSE_DATA["poses"]
    sprite_poses = {x: str(poses.index(x)) for x in poses}

    if life_state is not None:
        age = life_state
    else:
        age = cat.age

    if always_living:
        dead = False
    else:
        dead = cat.dead

    # setting the cat_sprite (bc this makes things much easier)
    cat_sprite = ""
    # sick sprites
    if (
        not disable_sick_sprite
        and cat.not_working()
        and age != CatAge.NEWBORN
        and constants.CONFIG["cat_sprites"]["sick_sprites"]
    ):
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            # check if we should default to the old young sprite (this is to be kind to modders)
            old_young_sprite = "sick_young0" in sprite_poses
            if old_young_sprite:
                cat_sprite = "sick_young0"
            # otherwise we use the age specific ones
            elif age == CatAge.KITTEN:
                cat_sprite = sprite_poses["sick_kitten0"]
            elif age == CatAge.ADOLESCENT:
                cat_sprite = sprite_poses["sick_adolescent0"]
        elif age == CatAge.SENIOR:
            # again, being kind to modders and defaulting to the sick adult if there's no senior
            cat_sprite = (
                sprite_poses["sick_adult0"]
                if "sick_senior0" not in sprite_poses
                else sprite_poses["sick_senior0"]
            )
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

    # generating the sprite
    try:
        new_sprite = _draw_sprite(cat, cat_sprite, scars_hidden, dead, acc_hidden)
    except:
        traceback.print_exc()
        logger.exception("Failed to load sprite")

        # Placeholder image
        new_sprite = image_cache.load_image(
            f"sprites/error_placeholder.png"
        ).convert_alpha()

    return new_sprite


# ------------------------------------------------------------------------------------------------------
#  generate_sprites() Helper Functions
# ------------------------------------------------------------------------------------------------------


def _draw_sprite(
    cat, cat_sprite: int, scars_hidden: bool, dead: bool, acc_hidden: bool
):
    # new_sprite = pygame.Surface(
    #        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    #    )

    pelt_recipe = _get_pelt_recipe(cat.pelt.name)
    new_sprite = _build_pelt(cat, pelt_recipe, cat.pelt.colour, cat_sprite)

    # TINTS
    if cat.pelt.tint is not None and cat.pelt.tint in sprites.cat_tints["tint_colours"]:
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
        patch = cat.pelt.white_patches
        if patch in cat.pelt.mostly_white or patch == "FULLWHITE":
            spritesheet = sprites.WHITE_MOSTLY_DATA["spritesheet"]
        elif patch in cat.pelt.high_white:
            spritesheet = sprites.WHITE_HIGH_DATA["spritesheet"]
        elif patch in cat.pelt.mid_white:
            spritesheet = sprites.WHITE_MID_DATA["spritesheet"]
        else:
            spritesheet = sprites.WHITE_LITTLE_DATA["spritesheet"]

        sprite_name = f"{spritesheet}{patch}{cat_sprite}"
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
            f"{sprites.WHITE_POINT_DATA['spritesheet']}{cat.pelt.points}{cat_sprite}"
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
        sprite_name = f"{sprites.WHITE_VITILIGO_DATA['spritesheet']}{cat.pelt.vitiligo}{cat_sprite}"

        new_sprite.blit(
            sprites.sprites[sprite_name],
            (0, 0),
        )

    # draw eyes & scars1
    sprite_name = (
        f"{sprites.EYE_DATA['spritesheet'][0]}{cat.pelt.eye_colour}{cat_sprite}"
    )
    eyes = sprites.sprites[sprite_name].copy()
    new_sprite.blit(eyes, (0, 0))
    if cat.pelt.eye_colour2 != None:
        heterochromia_name = (
            f"{sprites.EYE_DATA['spritesheet'][0]}{cat.pelt.eye_colour2}{cat_sprite}"
        )
        eyes2 = sprites.sprites[heterochromia_name].copy()
        eyes2.blit(
            sprites.sprites["heterochromiamask" + cat_sprite],
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )

        # Add eye onto cat
        new_sprite.blit(eyes2, (0, 0))

    if not scars_hidden:
        for scar in cat.pelt.scars:
            if scar in cat.pelt.general_scars:
                sprite_name = f"{sprites.SCAR_DATA['spritesheet']}{scar}{cat_sprite}"
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
                sprite_name = (
                    f"{sprites.SCAR_MISSING_PART_DATA['spritesheet']}{scar}{cat_sprite}"
                )
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
            "paw_accessories",
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
                        sprite_name = (
                            f"{sprites.WILD_DATA['spritesheet']}{accessory}{cat_sprite}"
                        )
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
                sprites.sprites["line_ur_underlay" + cat_sprite],
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

    return new_sprite


def _build_pelt(cat, pelt_recipe: dict, colour: str, sprite: int) -> pygame.Surface:
    """Builds a image out of a pelt_recipe and colour"""

    pelt_recipe = _apply_recipe_exceptions(pelt_recipe, colour, sprite)
    surface, blendmode, opacity = _build_layers(
        cat, pelt_recipe.get("layer_order"), pelt_recipe.get("layers"), colour, sprite
    )

    return surface


def _build_layers(
    cat, current_layer, layer_dict: dict, colour: str, sprite: int
) -> tuple[pygame.Surface, str, int]:
    """Builds layers for a pelt."""

    if type(current_layer) == list:
        # Defining the surface here is not ideal, but due to recursion, I can't just re-use the same
        # surface over and over.
        layer_surface = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )

        # For Compound Laters, blendmode and opacity can be given in the final
        # entry (must start with a +)
        group_blendmode = "normal"
        group_opacity = 100
        if type(current_layer[-1]) is str and current_layer[-1].startswith("+"):
            params = current_layer[-1][1:].split(",")
            for subParam in params:
                subParam = subParam.split(":")

                if len(subParam) != 2:
                    print(f"Something wrong with group para: {subParam}")
                    continue

                if subParam[0] == "blend_mode":
                    group_blendmode = subParam[1]
                elif subParam[0] == "opacity":
                    group_opacity = int(subParam[1])
                else:
                    print(f"GroupSubParam Not Recongized: {subParam}")

            current_layer = current_layer[
                :-1
            ]  # Remove the last entry - the one with the params

        # Build the compound layer.
        for subLayer in current_layer:
            temp, blend_mode, opacity = _build_layers(
                cat, subLayer, layer_dict, colour, sprite
            )
            blit_with_opacity(
                layer_surface, temp, opacity, special_flags=_get_blend_flags(blend_mode)
            )

        return (layer_surface, group_blendmode, group_opacity)

    # Base case, for non-compound layers.
    layer_info = layer_dict.get(current_layer)
    return _build_single_layer(cat, layer_info, colour, sprite)


def _build_single_layer(
    cat, layer_info, colour: str, sprite: int
) -> tuple[pygame.Surface, str, int]:
    """Builds a single layer of a pelt."""

    # A single layer can be a whole new pelt recipe. If so, return back up to
    # _build_pelt().
    if "pelt_name" in layer_info:
        pelt_recipe = _get_pelt_recipe(
            _find_cat_pelt_value(layer_info["pelt_name"], cat)
        )
        palette = _find_cat_pelt_value(layer_info.get("palette"), cat)

        return (
            _build_pelt(cat, pelt_recipe, palette, sprite),
            layer_info.get("blendmode"),
            layer_info.get("opacity", 100),
        )

    # If not calling for a whole pelt, find the single asset needed,
    groupName = _find_cat_pelt_value(layer_info.get("group_name"), cat)
    recolour = _find_cat_pelt_value(layer_info.get("color"), cat)
    spritesheet = layer_info.get("spritesheet", "pelt_parts_masks")

    temp = sprites.sprites[f"{spritesheet}{groupName}{sprite}"]

    palette_dict = sprites.PELT_COLOR_PALETTES[colour]
    if recolour:
        new_colour = palette_dict[recolour]
        recolour_surface = layer_surface = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )
        recolour_surface.fill(new_colour)
        recolour_surface.blit(temp, special_flags=pygame.BLEND_RGBA_MULT)
        temp = recolour_surface

    return temp, layer_info.get("blend_mode"), layer_info.get("opacity", 100)


def blit_with_opacity(
    target: pygame.Surface,
    source: pygame.Surface,
    opacity: int = 100,
    special_flags: int = 0,
):
    """Blit source onto target with global opacity."""

    # No need to create a copy if opacity is 100. Blit directly.
    if opacity == 100:
        target.blit(source, special_flags=special_flags)
        return

    temp = source.copy()
    alpha = (opacity / 100) * 255
    temp.set_alpha(alpha)

    target.blit(temp, special_flags=special_flags)


def _get_blend_flags(mode: str):
    """Translate the blend_mode string, as used in the pelt recipes, to the pygame blend flag."""

    blend_modes = {
        "mask": pygame.BLEND_RGBA_MULT,
        "multiply": pygame.BLEND_RGB_MULT,
        "normal": 0,
    }

    return blend_modes.get(mode, 0)


def _find_cat_pelt_value(value: str, cat):
    """Looks up a value in a cat's Pelt, if needed. Otherwise, return value.
    Pelt recipes can refer to some value stored in the cat's Pelt, via curly brackets.
    This checks for that, and looks up the value."""

    if type(value) is str and value.startswith("{") and value.endswith("}"):
        value = value[1:-1]  # Strip the curly brackets.
        return getattr(cat.pelt, value)

    return value


def _get_pelt_recipe(pelt_name: str):
    """Get the pelt recipe dictionary."""

    # Pelt Names are always captialized.
    # However, for some older tortie recipes (generated before
    # sprites changed to a layer and mask based system), the tortie_base and
    # tortie_pattern values are lowercase. This handles that by capitalizing the first
    # letter. Again, this should only be required for torties generated before the
    # layer-and-mask based sprite system rewrite.
    if type(pelt_name) is str:
        pelt_name = pelt_name[:1].upper() + pelt_name[1:]

    pelt_recipe_name = sprites.PELT_TO_RECIPE.get(pelt_name)
    if pelt_recipe_name == None:
        raise ValueError(f"No Pelt Reciple Mapping for {pelt_name}")

    pelt_recipe = sprites.PELT_RECIPES.get(pelt_recipe_name)
    if pelt_recipe == None:
        raise ValueError(f"No Pelt Recipe Found for {pelt_recipe_name}")

    return pelt_recipe


def _apply_recipe_exceptions(pelt_recipe: dict, colour: str, sprite: int) -> dict:
    """Some pelts have special rules for certain colors and/or poses. This checks to see if that's the case, and applies the rule."""
    MAX_MATCHES = 2

    exceptions = pelt_recipe.get("exceptions", None)

    # We want to find the best match - that exception were we meet the most conditions.
    curr_match = None
    curr_match_num = 0
    for one_ex in exceptions:
        match_num = 0
        # How many matches are needed to meet requriments.
        needed_matches = 0

        # Check to see if it matches at least one color condition.
        color_conditions = one_ex.get("colors")
        if color_conditions:
            needed_matches += 1
            if (
                type(color_conditions) is list and colour in color_conditions
            ) or color_conditions == colour:
                match_num += 1

        pose = sprites.POSE_DATA["poses"][int(sprite)]
        pose_conditions = one_ex.get("poses")
        if pose_conditions:
            needed_matches += 1
            if (
                type(pose_conditions) is list and pose in pose_conditions
            ) or pose_conditions == pose:
                match_num += 1

        if match_num == needed_matches and match_num >= curr_match_num:
            curr_match = one_ex
            curr_match_num = match_num

        if curr_match_num == MAX_MATCHES:
            break

    if curr_match:
        # If we reached here, the exception applies
        except_recipe = deepcopy(pelt_recipe)
        # Remove the exceptions, just so there we don't apply an exception again.
        except_recipe.pop("exceptions")

        if "layer_order" in curr_match:
            except_recipe["layer_order"] = curr_match["layer_order"]

        if "layers" in curr_match:
            for key, value in curr_match["layers"].items():
                except_recipe["layers"][key] = (
                    except_recipe["layers"].get(key, {}) | value
                )

        return except_recipe

    return pelt_recipe


# ------------------------------------------------------------------------------------------------------
#  Other Sprite Functions
# ------------------------------------------------------------------------------------------------------


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
