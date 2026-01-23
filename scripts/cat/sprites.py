import logging
import os
import traceback
from copy import copy

import pygame
import ujson

from scripts.cat.enums import CatGroup, CatAge
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure import constants, image_cache
from scripts.game_structure.game import game_setting_get
from scripts.game_structure.game.settings import game_setting_get
from scripts.special_dates import SpecialDate, is_today
from scripts.ui.scale import ui_scale_dimensions

logger = logging.getLogger(__name__)


class Sprites:
    cat_tints = {}
    white_patches_tints = {}
    clan_symbols = []

    with open(
        "sprites/dicts/pose_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        POSE_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/collar_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        COLLAR_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/wild_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        WILD_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/plant_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        PLANT_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/scar_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        SCAR_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/scar_missing_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        SCAR_MISSING_PART_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/skin_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        SKIN_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/tortie_patches_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        TORTIE_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/pelt_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        PELT_DATA = ujson.loads(read_file.read())

    with open("sprites/dicts/eye_sprite_data.json", "r", encoding="utf-8") as read_file:
        EYE_DATA = ujson.loads(read_file.read())

    with open(
        "sprites/dicts/white_patches_sprite_data.json", "r", encoding="utf-8"
    ) as read_file:
        WHITE_DATA = ujson.loads(read_file.read())

    def __init__(self):
        """Class that handles and hold all spritesheets.
        Size is normally automatically determined by the size
        of the lineart. If a size is passed, it will override
        this value."""
        self.symbol_dict = None
        self.size = None
        self.spritesheets = {}
        self.images = {}
        self.sprites = {}

        # Shared empty sprite for placeholders
        self.blank_sprite = None

        self.load_tints()

        self.sheet_layout = self.POSE_DATA["sheet_layout"]

    def load_tints(self):
        try:
            with open("sprites/dicts/tint.json", "r", encoding="utf-8") as read_file:
                self.cat_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading Tints")

        try:
            with open(
                "sprites/dicts/white_patches_tint.json", "r", encoding="utf-8"
            ) as read_file:
                self.white_patches_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading White Patches Tints")

    def spritesheet(self, a_file, name):
        """
        Add spritesheet called name from a_file.

        Parameters:
        a_file -- Path to the file to create a spritesheet from.
        name -- Name to call the new spritesheet.
        """
        self.spritesheets[name] = pygame.image.load(a_file).convert_alpha()

    def make_group(
        self,
        spritesheet,
        pos,
        name,
        sprites_x=None,
        sprites_y=None,
        no_index=False,
        palettes: list = None,
    ):  # pos = ex. (2, 3), no single pixels
        """
        Divide sprites on a spritesheet into groups of sprites that are easily accessible
        :param spritesheet: Name of spritesheet file
        :param pos: (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites
        :param name: Name of group being made
        :param sprites_x: default 3, number of sprites horizontally
        :param sprites_y: default 7, number of sprites vertically
        :param no_index: default False, set True if sprite name does not require cat pose index:
        :param palettes: list of palette names
        """
        # pulls the defaults from the pose_sprite_data.json file
        if not sprites_x:
            sprites_x = self.sheet_layout[0]
        if not sprites_y:
            sprites_y = self.sheet_layout[1]

        group_x_ofs = pos[0] * sprites_x * self.size
        group_y_ofs = pos[1] * sprites_y * self.size
        i = 0

        # splitting group into singular sprites and storing into self.sprites section
        for y in range(sprites_y):
            for x in range(sprites_x):
                if no_index:
                    full_name = f"{name}"
                else:
                    full_name = f"{name}{i}"

                try:
                    new_sprite = pygame.Surface.subsurface(
                        self.spritesheets[spritesheet],
                        group_x_ofs + x * self.size,
                        group_y_ofs + y * self.size,
                        self.size,
                        self.size,
                    )

                except ValueError:
                    # Fallback for non-existent sprites
                    print(f"WARNING: nonexistent sprite - {full_name}")
                    if not self.blank_sprite:
                        self.blank_sprite = pygame.Surface(
                            (self.size, self.size), pygame.HWSURFACE | pygame.SRCALPHA
                        )
                    new_sprite = self.blank_sprite

                if palettes:
                    self.apply_palettes(i, name, new_sprite, palettes)
                else:
                    self.sprites[full_name] = new_sprite
                i += 1

    def apply_palettes(
        self, sprite_index: int, name: str, new_sprite, palette_names: list
    ):
        """
        Creates sprites for each color palette variation
        :param sprite_index: index of sprite
        :param name: name of sprite
        :param new_sprite: the sprite object to create variations of
        :param palette_names: list of palette names
        """
        # first we create an array of our palette map
        full_map = pygame.image.load(f"sprites/palettes/{name}_palette.png")
        map_array = pygame.PixelArray(full_map)
        # then create a dictionary associating the palette name with its row of the array
        color_palettes = {}
        palette_names = palette_names.copy()
        palette_names.insert(0, "BASE")
        for row in range(
            0, map_array.shape[1]  # pylint: disable=unsubscriptable-object
        ):
            color_name = palette_names[row]
            color_palettes.update(
                {color_name: [full_map.unmap_rgb(px) for px in map_array[::, row]]}
            )

        base_palette = color_palettes["BASE"]

        # now we recolor the sprite
        for color_name, palette in color_palettes.items():
            if color_name == "BASE":
                continue
            recolor_sprite = pygame.PixelArray(new_sprite.copy())
            # we replace each base_palette color with it's matching index from the color_palette
            for color_i, color in enumerate(palette):
                recolor_sprite.replace(base_palette[color_i], color)
            # convert back into a surface
            _sprite = recolor_sprite.make_surface()
            # add it to our sprite dict!
            self.sprites[f"{name}_{color_name}{sprite_index}"] = _sprite
            # close the pixel array now that we're done
            recolor_sprite.close()

        map_array.close()

    def load_all(self):
        # get the width and height of the spritesheet
        lineart = pygame.image.load("sprites/lineart.png")
        width, height = lineart.get_size()
        del lineart  # unneeded

        # if anyone changes lineart for whatever reason update this
        if isinstance(self.size, int):
            pass
        elif width / self.sheet_layout[0] == height / self.sheet_layout[1]:
            self.size = width / self.sheet_layout[0]
        else:
            self.size = 50  # default, what base clangen uses
            print(
                f"lineart.png is not {self.sheet_layout}, falling back to {self.size}"
            )
            print(
                f"if you are a modder, please update sheet_layout in sprites/dicts/pose_sprite_data.json"
            )

        del width, height  # unneeded

        data_jsons = (
            self.EYE_DATA,
            self.PELT_DATA,
            self.WHITE_DATA,
            self.TORTIE_DATA,
            self.SKIN_DATA,
            self.SCAR_DATA,
            self.SCAR_MISSING_PART_DATA,
            self.PLANT_DATA,
            self.WILD_DATA,
            self.COLLAR_DATA,
        )

        # data jsons that have multiple associated spritesheets
        multi_sheet_data = [
            x for x in data_jsons if isinstance(x["spritesheet"], (list, dict))
        ]

        # COMPILING SPRITESHEETS
        spritesheets = [
            "fademask",
            "fadestarclan",
            "fadedarkforest",
            "fadeunknownresidence",
            "symbols",
        ]

        # separate from data_json list bc we need to handle it differently later
        spritesheets.extend(self.POSE_DATA["spritesheet"])

        for data in data_jsons:
            if data in multi_sheet_data:
                spritesheets.extend(data["spritesheet"])
            else:
                spritesheets.append(data["spritesheet"])

        for x in spritesheets:
            if "lineart" in x and (
                constants.CONFIG["fun"]["april_fools"]
                or is_today(SpecialDate.APRIL_FOOLS)
            ):
                self.spritesheet(f"sprites/{x}_aprilfools.png", x)
            else:
                self.spritesheet(f"sprites/{x}.png", x)

        # Line art
        for sheet in self.POSE_DATA["spritesheet"]:
            self.make_group(sheet, (0, 0), sheet)

        # Fading Fog
        for i in range(0, 3):
            self.make_group("fademask", (i, 0), f"fademask{i}")
            self.make_group("fadestarclan", (i, 0), f"fadestarclan{i}")
            self.make_group("fadedarkforest", (i, 0), f"fadedf{i}")
            self.make_group("fadeunknownresidence", (i, 0), f"fadeur{i}")

        for data in data_jsons:
            # collar accs
            # this guy is special since it uses palette mapping
            if data == self.COLLAR_DATA and self.COLLAR_DATA["palette_map"]:
                spritesheet = self.COLLAR_DATA["spritesheet"]
                for row, style_type in enumerate(self.COLLAR_DATA["style_data"]):
                    for col, style in enumerate(style_type):
                        self.make_group(
                            spritesheet=spritesheet,
                            pos=(col, row),
                            name=f"{spritesheet}{style}",
                            palettes=style_type[style],
                        )

            # these have multiple sprite sheets, so are handled differently from the others
            elif data in multi_sheet_data:
                for spritesheet in data["spritesheet"]:
                    self.load_sheet(spritesheet, data["sprite_list"])

            # everything else
            else:
                self.load_sheet(data["spritesheet"], data["sprite_list"])

        self.load_symbols()

    def load_sheet(self, spritesheet: str, sprite_names: list[list[str]]):
        """
        Loads sheet data and creates sprite groups.
        :param spritesheet: name of the spritesheet
        :param sprite_names: list containing lists of sprite names for this spritesheet, each list is a single row of the sheet
        """
        for row, sprite_names in enumerate(sprite_names):
            for col, sprite in enumerate(sprite_names):
                self.make_group(
                    spritesheet=spritesheet,
                    pos=(col, row),
                    name=f"{spritesheet}{sprite}",
                )

    def load_symbols(self):
        """
        loads clan symbols
        """

        if os.path.exists("resources/dicts/clan_symbols.json"):
            with open(
                "resources/dicts/clan_symbols.json", encoding="utf-8"
            ) as read_file:
                self.symbol_dict = ujson.loads(read_file.read())

        # U and X omitted from letter list due to having no prefixes
        letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "V",
            "W",
            "Y",
            "Z",
        ]

        # sprite names will format as "symbol{PREFIX}{INDEX}", ex. "symbolSPRING0"
        y_pos = 1
        for letter in letters:
            x_mod = 0
            for i, symbol in enumerate(
                [
                    symbol
                    for symbol in self.symbol_dict
                    if letter in symbol and self.symbol_dict[symbol]["variants"]
                ]
            ):
                if self.symbol_dict[symbol]["variants"] > 1 and x_mod > 0:
                    x_mod += -1
                for variant_index in range(self.symbol_dict[symbol]["variants"]):
                    x_pos = i + x_mod

                    if self.symbol_dict[symbol]["variants"] > 1:
                        x_mod += 1
                    elif x_mod > 0:
                        x_pos += -1

                    self.clan_symbols.append(f"symbol{symbol.upper()}{variant_index}")
                    self.make_group(
                        "symbols",
                        (x_pos, y_pos),
                        f"symbol{symbol.upper()}{variant_index}",
                        sprites_x=1,
                        sprites_y=1,
                        no_index=True,
                    )

            y_pos += 1

    def get_symbol(self, symbol: str, force_light=False):
        """Change the color of the symbol to match the requested theme, then return it
        :param Surface symbol: The clan symbol to convert
        :param force_light: Use to ignore dark mode and always display the light mode color
        """
        symbol = self.sprites.get(symbol)
        if symbol is None:
            logger.warning("%s is not a known Clan symbol! Using default.")
            symbol = self.sprites[self.clan_symbols[0]]

        recolored_symbol = copy(symbol)
        var = pygame.PixelArray(recolored_symbol)
        var.replace(
            (87, 76, 45),
            (
                pygame.Color(constants.CONFIG["theme"]["dark_mode_clan_symbols"])
                if not force_light and game_setting_get("dark mode")
                else pygame.Color(constants.CONFIG["theme"]["light_mode_clan_symbols"])
            ),
            distance=0,
        )
        del var

        return recolored_symbol

    @staticmethod
    def get_platform(biome, season, show_nest, group: CatGroup) -> pygame.Surface:
        """
        Returns the relevant platform
        :param biome: The current game biome
        :param season: The current game season
        :param show_nest: If true, displays the nest
        :param group: Used to determine appropriate afterlife platform
        :return: pygame.Surface containing the desired platform
        """
        offset = 0 if game_setting_get("dark mode") else 80
        """Used to choose the dark mode version of platforms"""

        available_biome = ["Forest", "Mountainous", "Plains", "Beach"]

        if biome not in available_biome:
            biome = available_biome[0]
        if show_nest:
            biome = "nest"

        biome = biome.lower()

        platformsheet = image_cache.load_image(
            "resources/images/platforms.png"
        ).convert_alpha()

        order = ["beach", "forest", "mountainous", "nest", "plains", "dead"]

        if group and group.is_afterlife():
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index("dead") * 70, 640, 70)
            )

            if group == CatGroup.DARK_FOREST:
                return biome_platforms.subsurface(pygame.Rect(0 + offset, 0, 80, 70))
            elif group == CatGroup.STARCLAN:
                return biome_platforms.subsurface(pygame.Rect(160 + offset, 0, 80, 70))
            elif group == CatGroup.UNKNOWN_RESIDENCE:
                return biome_platforms.subsurface(pygame.Rect(320 + offset, 0, 80, 70))

        biome_platforms = platformsheet.subsurface(
            pygame.Rect(0, order.index(biome) * 70, 640, 70)
        ).convert_alpha()
        season_x = {
            "greenleaf": 0 + offset,
            "leaf-bare": 160 + offset,
            "leaf-fall": 320 + offset,
            "newleaf": 480 + offset,
        }

        return biome_platforms.subsurface(
            pygame.Rect(
                season_x[season.lower()],
                0,
                80,
                70,
            )
        )


# CREATE INSTANCE
sprites = Sprites()


def subtract_lineart(surface, mask_surf, bg_color):
    """
    Though I doubt there will be a use-case for this in the future, this is a helper function I wrote to extract the
    semitransparent layer of sparkles from our original StarClan sprites. It requires a mask to work but could probably
    be altered to remove the need. honestly, I just want this in here so that we have it in at least one commit if
    we turn out to need something like this again lol it was AWFUL to figure out
    """
    width, height = surface.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)

    bg_r, bg_g, bg_b = bg_color.r, bg_color.g, bg_color.b

    surface.lock()
    overlay.lock()

    for y in range(height):
        for x in range(width):
            r, g, b, a = surface.get_at((x, y))

            # If fully transparent, skip
            if a == 0 or mask_surf.get_at((x, y)).a < 120:
                overlay.set_at((x, y), (r, g, b, a))
                continue

            best_error = float("inf")
            best_color = (0, 0, 0)
            best_alpha = 0

            alpha_steps = 255
            # do a heinous process where we eyeball the alpha
            for step in range(1, alpha_steps + 1):
                alpha = step / alpha_steps

                try:
                    # Recover overlay color for this alpha
                    o_r = (r - (1 - alpha) * bg_r) / alpha
                    o_g = (g - (1 - alpha) * bg_g) / alpha
                    o_b = (b - (1 - alpha) * bg_b) / alpha
                except ZeroDivisionError:
                    continue

                # if it makes no sense, skip
                if not (0 <= o_r <= 255 and 0 <= o_g <= 255 and 0 <= o_b <= 255):
                    continue

                # Simulate the blend & compare
                sim_r = o_r * alpha + bg_r * (1 - alpha)
                sim_g = o_g * alpha + bg_g * (1 - alpha)
                sim_b = o_b * alpha + bg_b * (1 - alpha)

                error = abs(sim_r - r) + abs(sim_g - g) + abs(sim_b - b)

                if error < best_error:
                    best_error = error
                    best_color = (int(round(o_r)), int(round(o_g)), int(round(o_b)))
                    best_alpha = int(round(alpha * 255))

            # Set recovered overlay color
            overlay.set_at((x, y), (*best_color, best_alpha))

    surface.unlock()
    overlay.unlock()
    return overlay


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
