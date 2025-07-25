import logging
import os
from copy import copy

import pygame
import ujson

from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.special_dates import SpecialDate, is_today

logger = logging.getLogger(__name__)


class Sprites:
    cat_tints = {}
    white_patches_tints = {}
    clan_symbols = []

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
        sprites_x=3,
        sprites_y=7,
        no_index=False,
        palettes: list = None,
    ):  # pos = ex. (2, 3), no single pixels
        """
        Divide sprites on a spritesheet into groups of sprites that are easily accessible
        :param spritesheet: Name of spritesheet file
        :param pos: (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites
        :param name: Name of group being made
        :param sprites_x: default 3, number of sprites horizontally
        :param sprites_y: default 3, number of sprites vertically
        :param no_index: default False, set True if sprite name does not require cat pose index:
        :param palettes: list of palette names
        """

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
        elif width / 3 == height / 7:
            self.size = width / 3
        else:
            self.size = 50  # default, what base clangen uses
            print(f"lineart.png is not 3x7, falling back to {self.size}")
            print(
                f"if you are a modder, please update scripts/cat/sprites.py and "
                f"do a search for 'if width / 3 == height / 7:'"
            )

        del width, height  # unneeded

        for x in (
            "lineart",
            "lineartdf",
            "lineartdead",
            "line_sc_overlay",
            "eyes",
            "eyes_right",
            "skin",
            "scars",
            "scars_missing_part",
            "acc_plants",
            "acc_wilds",
            "acc_collars",
            "colours_single",
            "colours_tabby",
            "colours_speckled",
            "colours_bengal",
            "colours_marbled",
            "colours_rosette",
            "colours_smoke",
            "colours_ticked",
            "colours_mackerel",
            "colours_classic",
            "colours_sokoke",
            "colours_agouti",
            "colours_singlestripe",
            "colours_masked",
            "shadersnewwhite",
            "lightingnew",
            "patches_white",
            "patches_tortie",
            "fademask",
            "fadestarclan",
            "fadedarkforest",
            "symbols",
        ):
            if "lineart" in x and (
                constants.CONFIG["fun"]["april_fools"]
                or is_today(SpecialDate.APRIL_FOOLS)
            ):
                self.spritesheet(f"sprites/aprilfools{x}.png", x)
            else:
                self.spritesheet(f"sprites/{x}.png", x)

        # Line art
        self.make_group("lineart", (0, 0), "lines")
        self.make_group("shadersnewwhite", (0, 0), "shaders")
        self.make_group("lightingnew", (0, 0), "lighting")

        self.make_group("lineartdead", (0, 0), "lineartdead")
        self.make_group("lineartdf", (0, 0), "lineartdf")
        self.make_group("line_sc_overlay", (0, 0), "sc_overlay")

        # Fading Fog
        for i in range(0, 3):
            self.make_group("fademask", (i, 0), f"fademask{i}")
            self.make_group("fadestarclan", (i, 0), f"fadestarclan{i}")
            self.make_group("fadedarkforest", (i, 0), f"fadedf{i}")

        # eye colours
        for spritesheet in self.EYE_DATA["spritesheets"]:
            self.load_sheet(spritesheet, self.EYE_DATA["sprite_list"])

        # Define white patches
        self.load_sheet(self.WHITE_DATA["spritesheet"], self.WHITE_DATA["sprite_list"])

        # pelts
        for spritesheet in self.PELT_DATA["spritesheets"]:
            self.load_sheet(spritesheet, self.PELT_DATA["sprite_list"])

        # tortie patches
        self.load_sheet(
            self.TORTIE_DATA["spritesheet"], self.TORTIE_DATA["sprite_list"]
        )

        # skin colors
        self.load_sheet(self.SKIN_DATA["spritesheet"], self.SKIN_DATA["sprite_list"])

        # scars
        self.load_sheet(self.SCAR_DATA["spritesheet"], self.SCAR_DATA["sprite_list"])

        # missing parts
        self.load_sheet(
            self.SCAR_MISSING_PART_DATA["spritesheet"],
            self.SCAR_MISSING_PART_DATA["sprite_list"],
        )

        # plant accs
        self.load_sheet(self.PLANT_DATA["spritesheet"], self.PLANT_DATA["sprite_list"])

        # wild accs
        self.load_sheet(self.WILD_DATA["spritesheet"], self.WILD_DATA["sprite_list"])

        # collar accs
        # this guy is special since it uses palette mapping
        spritesheet = self.COLLAR_DATA["spritesheet"]
        for row, style_type in enumerate(self.COLLAR_DATA["style_data"]):
            for col, style in enumerate(style_type):
                self.make_group(
                    spritesheet=spritesheet,
                    pos=(col, row),
                    name=f"{spritesheet}{style}",
                    palettes=style_type[style],
                )

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
