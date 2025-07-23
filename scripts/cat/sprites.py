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
        self, spritesheet, pos, name, sprites_x=3, sprites_y=7, no_index=False
    ):  # pos = ex. (2, 3), no single pixels
        """
        Divide sprites on a spritesheet into groups of sprites that are easily accessible
        :param spritesheet: Name of spritesheet file
        :param pos: (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites
        :param name: Name of group being made
        :param sprites_x: default 3, number of sprites horizontally
        :param sprites_y: default 3, number of sprites vertically
        :param no_index: default False, set True if sprite name does not require cat pose index
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

                self.sprites[full_name] = new_sprite
                i += 1

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
            "eyes2",
            "skin",
            "scars",
            "missingscars",
            "medcatherbs",
            "wild",
            "collars",
            "bellcollars",
            "bowcollars",
            "nyloncollars",
            "singlecolours",
            "speckledcolours",
            "tabbycolours",
            "bengalcolours",
            "marbledcolours",
            "rosettecolours",
            "smokecolours",
            "tickedcolours",
            "mackerelcolours",
            "classiccolours",
            "sokokecolours",
            "agouticolours",
            "singlestripecolours",
            "maskedcolours",
            "shadersnewwhite",
            "lightingnew",
            "whitepatches",
            "tortiepatchesmasks",
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

        # Define eye colors
        eye_colors = [
            [
                "YELLOW",
                "AMBER",
                "HAZEL",
                "PALEGREEN",
                "GREEN",
                "BLUE",
                "DARKBLUE",
                "GREY",
                "CYAN",
                "EMERALD",
                "HEATHERBLUE",
                "SUNLITICE",
            ],
            [
                "COPPER",
                "SAGE",
                "COBALT",
                "PALEBLUE",
                "BRONZE",
                "SILVER",
                "PALEYELLOW",
                "GOLD",
                "GREENYELLOW",
                "ORANGE",
            ],
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("eyes", (col, row), f"eyes{color}")
                self.make_group("eyes2", (col, row), f"eyes2{color}")

        # Define white patches
        white_patches = [
            [
                "FULLWHITE",
                "ANY",
                "TUXEDO",
                "LITTLE",
                "COLOURPOINT",
                "VAN",
                "ANYTWO",
                "MOON",
                "PHANTOM",
                "POWDER",
                "BLEACHED",
                "SAVANNAH",
                "FADESPOTS",
                "PEBBLESHINE",
            ],
            [
                "EXTRA",
                "ONEEAR",
                "BROKEN",
                "LIGHTTUXEDO",
                "BUZZARDFANG",
                "RAGDOLL",
                "LIGHTSONG",
                "VITILIGO",
                "BLACKSTAR",
                "PIEBALD",
                "CURVED",
                "PETAL",
                "SHIBAINU",
                "OWL",
            ],
            [
                "TIP",
                "FANCY",
                "FRECKLES",
                "RINGTAIL",
                "HALFFACE",
                "PANTSTWO",
                "GOATEE",
                "VITILIGOTWO",
                "PAWS",
                "MITAINE",
                "BROKENBLAZE",
                "SCOURGE",
                "DIVA",
                "BEARD",
            ],
            [
                "TAIL",
                "BLAZE",
                "PRINCE",
                "BIB",
                "VEE",
                "UNDERS",
                "HONEY",
                "FAROFA",
                "DAMIEN",
                "MISTER",
                "BELLY",
                "TAILTIP",
                "TOES",
                "TOPCOVER",
            ],
            [
                "APRON",
                "CAPSADDLE",
                "MASKMANTLE",
                "SQUEAKS",
                "STAR",
                "TOESTAIL",
                "RAVENPAW",
                "PANTS",
                "REVERSEPANTS",
                "SKUNK",
                "KARPATI",
                "HALFWHITE",
                "APPALOOSA",
                "DAPPLEPAW",
            ],
            [
                "HEART",
                "LILTWO",
                "GLASS",
                "MOORISH",
                "SEPIAPOINT",
                "MINKPOINT",
                "SEALPOINT",
                "MAO",
                "LUNA",
                "CHESTSPECK",
                "WINGS",
                "PAINTED",
                "HEARTTWO",
                "WOODPECKER",
            ],
            [
                "BOOTS",
                "MISS",
                "COW",
                "COWTWO",
                "BUB",
                "BOWTIE",
                "MUSTACHE",
                "REVERSEHEART",
                "SPARROW",
                "VEST",
                "LOVEBUG",
                "TRIXIE",
                "SAMMY",
                "SPARKLE",
            ],
            [
                "RIGHTEAR",
                "LEFTEAR",
                "ESTRELLA",
                "SHOOTINGSTAR",
                "EYESPOT",
                "REVERSEEYE",
                "FADEBELLY",
                "FRONT",
                "BLOSSOMSTEP",
                "PEBBLE",
                "TAILTWO",
                "BUDDY",
                "BACKSPOT",
                "EYEBAGS",
            ],
            [
                "BULLSEYE",
                "FINN",
                "DIGIT",
                "KROPKA",
                "FCTWO",
                "FCONE",
                "MIA",
                "SCAR",
                "BUSTER",
                "SMOKEY",
                "HAWKBLAZE",
                "CAKE",
                "ROSINA",
                "PRINCESS",
            ],
            ["LOCKET", "BLAZEMASK", "TEARS", "DOUGIE"],
        ]

        for row, patches in enumerate(white_patches):
            for col, patch in enumerate(patches):
                self.make_group("whitepatches", (col, row), f"white{patch}")

        # Define colors and categories
        color_categories = [
            ["WHITE", "PALEGREY", "SILVER", "GREY", "DARKGREY", "GHOST", "BLACK"],
            ["CREAM", "PALEGINGER", "GOLDEN", "GINGER", "DARKGINGER", "SIENNA"],
            ["LIGHTBROWN", "LILAC", "BROWN", "GOLDEN-BROWN", "DARKBROWN", "CHOCOLATE"],
        ]

        color_types = [
            "singlecolours",
            "tabbycolours",
            "marbledcolours",
            "rosettecolours",
            "smokecolours",
            "tickedcolours",
            "speckledcolours",
            "bengalcolours",
            "mackerelcolours",
            "classiccolours",
            "sokokecolours",
            "agouticolours",
            "singlestripecolours",
            "maskedcolours",
        ]

        for row, colors in enumerate(color_categories):
            for col, color in enumerate(colors):
                for color_type in color_types:
                    self.make_group(color_type, (col, row), f"{color_type[:-7]}{color}")

        # tortiepatchesmasks
        tortiepatchesmasks = [
            [
                "ONE",
                "TWO",
                "THREE",
                "FOUR",
                "REDTAIL",
                "DELILAH",
                "HALF",
                "STREAK",
                "MASK",
                "SMOKE",
            ],
            [
                "MINIMALONE",
                "MINIMALTWO",
                "MINIMALTHREE",
                "MINIMALFOUR",
                "OREO",
                "SWOOP",
                "CHIMERA",
                "CHEST",
                "ARMTAIL",
                "GRUMPYFACE",
            ],
            [
                "MOTTLED",
                "SIDEMASK",
                "EYEDOT",
                "BANDANA",
                "PACMAN",
                "STREAMSTRIKE",
                "SMUDGED",
                "DAUB",
                "EMBER",
                "BRIE",
            ],
            [
                "ORIOLE",
                "ROBIN",
                "BRINDLE",
                "PAIGE",
                "ROSETAIL",
                "SAFI",
                "DAPPLENIGHT",
                "BLANKET",
                "BELOVED",
                "BODY",
            ],
            ["SHILOH", "FRECKLED", "HEARTBEAT"],
        ]

        for row, masks in enumerate(tortiepatchesmasks):
            for col, mask in enumerate(masks):
                self.make_group("tortiepatchesmasks", (col, row), f"tortiemask{mask}")

        # Define skin colors
        skin_colors = [
            ["BLACK", "RED", "PINK", "DARKBROWN", "BROWN", "LIGHTBROWN"],
            ["DARK", "DARKGREY", "GREY", "DARKSALMON", "SALMON", "PEACH"],
            ["DARKMARBLED", "MARBLED", "LIGHTMARBLED", "DARKBLUE", "BLUE", "LIGHTBLUE"],
        ]

        for row, colors in enumerate(skin_colors):
            for col, color in enumerate(colors):
                self.make_group("skin", (col, row), f"skin{color}")

        self.load_scars()
        self.load_symbols()

    def load_scars(self):
        """
        Loads scar sprites and puts them into groups.
        """

        # Define scars
        scars_data = [
            [
                "ONE",
                "TWO",
                "THREE",
                "MANLEG",
                "BRIGHTHEART",
                "MANTAIL",
                "BRIDGE",
                "RIGHTBLIND",
                "LEFTBLIND",
                "BOTHBLIND",
                "BURNPAWS",
                "BURNTAIL",
            ],
            [
                "BURNBELLY",
                "BEAKCHEEK",
                "BEAKLOWER",
                "BURNRUMP",
                "CATBITE",
                "RATBITE",
                "FROSTFACE",
                "FROSTTAIL",
                "FROSTMITT",
                "FROSTSOCK",
                "QUILLCHUNK",
                "QUILLSCRATCH",
            ],
            [
                "TAILSCAR",
                "SNOUT",
                "CHEEK",
                "SIDE",
                "THROAT",
                "TAILBASE",
                "BELLY",
                "TOETRAP",
                "SNAKE",
                "LEGBITE",
                "NECKBITE",
                "FACE",
            ],
            [
                "HINDLEG",
                "BACK",
                "QUILLSIDE",
                "SCRATCHSIDE",
                "TOE",
                "BEAKSIDE",
                "CATBITETWO",
                "SNAKETWO",
                "FOUR",
            ],
        ]

        # define missing parts
        missing_parts_data = [
            [
                "LEFTEAR",
                "RIGHTEAR",
                "NOTAIL",
                "NOLEFTEAR",
                "NORIGHTEAR",
                "NOEAR",
                "HALFTAIL",
                "NOPAW",
            ]
        ]

        # scars
        for row, scars in enumerate(scars_data):
            for col, scar in enumerate(scars):
                self.make_group("scars", (col, row), f"scars{scar}")

        # missing parts
        for row, missing_parts in enumerate(missing_parts_data):
            for col, missing_part in enumerate(missing_parts):
                self.make_group("missingscars", (col, row), f"scars{missing_part}")

        # accessories
        # to my beloved modders, im very sorry for reordering everything <333 -clay
        medcatherbs_data = [
            [
                "MAPLE LEAF",
                "HOLLY",
                "BLUE BERRIES",
                "FORGET ME NOTS",
                "RYE STALK",
                "CATTAIL",
                "POPPY",
                "ORANGE POPPY",
                "CYAN POPPY",
                "WHITE POPPY",
                "PINK POPPY",
            ],
            [
                "BLUEBELLS",
                "LILY OF THE VALLEY",
                "SNAPDRAGON",
                "HERBS",
                "PETALS",
                "NETTLE",
                "HEATHER",
                "GORSE",
                "JUNIPER",
                "RASPBERRY",
                "LAVENDER",
            ],
            [
                "OAK LEAVES",
                "CATMINT",
                "MAPLE SEED",
                "LAUREL",
                "BULB WHITE",
                "BULB YELLOW",
                "BULB ORANGE",
                "BULB PINK",
                "BULB BLUE",
                "CLOVER",
                "DAISY",
            ],
            [
                "WISTERIA",
                "ROSE MALLOW",
                "PICKLEWEED",
                "GOLDEN CREEPING JENNY",
                "DESERT WILLOW",
                "CACTUS FLOWER",
                "PRAIRIE FIRE",
                "VERBENA EAR",
                "VERBENA PELT",
            ],
        ]
        dryherbs_data = [["DRY HERBS", "DRY CATMINT", "DRY NETTLES", "DRY LAURELS"]]
        wild_data = [
            [
                "RED FEATHERS",
                "BLUE FEATHERS",
                "JAY FEATHERS",
                "GULL FEATHERS",
                "SPARROW FEATHERS",
                "MOTH WINGS",
                "ROSY MOTH WINGS",
                "MORPHO BUTTERFLY",
                "MONARCH BUTTERFLY",
                "CICADA WINGS",
                "BLACK CICADA",
            ],
            [
                "ROAD RUNNER FEATHER",
            ],
        ]

        collars_data = [
            ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"],
            ["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"],
            ["PINK", "PURPLE", "MULTI", "INDIGO"],
        ]

        bellcollars_data = [
            [
                "CRIMSONBELL",
                "BLUEBELL",
                "YELLOWBELL",
                "CYANBELL",
                "REDBELL",
                "LIMEBELL",
            ],
            ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"],
            ["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"],
        ]

        bowcollars_data = [
            ["CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW"],
            ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"],
            ["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"],
        ]

        nyloncollars_data = [
            [
                "CRIMSONNYLON",
                "BLUENYLON",
                "YELLOWNYLON",
                "CYANNYLON",
                "REDNYLON",
                "LIMENYLON",
            ],
            ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"],
            ["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"],
        ]

        # medcatherbs
        for row, herbs in enumerate(medcatherbs_data):
            for col, herb in enumerate(herbs):
                self.make_group("medcatherbs", (col, row), f"acc_herbs{herb}")
        # dryherbs
        for row, dry in enumerate(dryherbs_data):
            for col, dryherbs in enumerate(dry):
                self.make_group("medcatherbs", (col, 4), f"acc_herbs{dryherbs}")
        # wild
        for row, wilds in enumerate(wild_data):
            for col, wild in enumerate(wilds):
                self.make_group("wild", (col, row), f"acc_wild{wild}")

        # collars
        for row, collars in enumerate(collars_data):
            for col, collar in enumerate(collars):
                self.make_group("collars", (col, row), f"collars{collar}")

        # bellcollars
        for row, bellcollars in enumerate(bellcollars_data):
            for col, bellcollar in enumerate(bellcollars):
                self.make_group("bellcollars", (col, row), f"collars{bellcollar}")

        # bowcollars
        for row, bowcollars in enumerate(bowcollars_data):
            for col, bowcollar in enumerate(bowcollars):
                self.make_group("bowcollars", (col, row), f"collars{bowcollar}")

        # nyloncollars
        for row, nyloncollars in enumerate(nyloncollars_data):
            for col, nyloncollar in enumerate(nyloncollars):
                self.make_group("nyloncollars", (col, row), f"collars{nyloncollar}")

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
