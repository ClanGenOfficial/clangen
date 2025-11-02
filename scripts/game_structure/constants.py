import tomllib

from pygame import Cursor, image, SYSTEM_CURSOR_ARROW
import ujson

# these scripts don't import any clangen scripts into themselves, so it's okay for them to be imported here
from scripts.clan_resources.herb.herb import HERBS
from scripts.clan_resources.supply import Supply

from scripts.screens.enums import GameScreen

# this is just to make referencing main menu screens as a whole easier,
# note that the clan creation screen is included and the clan settings screen is excluded. this is intended.
MENU_SCREENS = [
    GameScreen.SETTINGS,
    GameScreen.START,
    GameScreen.SWITCH_CLAN,
    GameScreen.MAKE_CLAN,
]

BIOME_TYPES = ["Forest", "Plains", "Mountainous", "Beach", "Wetlands", "Desert"]

SEASONS = ["Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare"]
SEASON_CALENDAR = [
    "Newleaf",
    "Newleaf",
    "Newleaf",
    "Greenleaf",
    "Greenleaf",
    "Greenleaf",
    "Leaf-fall",
    "Leaf-fall",
    "Leaf-fall",
    "Leaf-bare",
    "Leaf-bare",
    "Leaf-bare",
]

TEMPERAMENT_DICT = {
    "low_social": ["cunning", "proud", "bloodthirsty"],
    "mid_social": ["amiable", "stoic", "wary"],
    "high_social": ["gracious", "mellow", "logical"],
}

OUTSIDER_REPS = ("welcoming", "neutral", "hostile")
OTHER_CLAN_REPS = ("ally", "neutral", "hostile")

INJURY_GROUPS = {
    "battle_injury": [
        "claw-wound",
        "mangled leg",
        "mangled tail",
        "torn pelt",
        "cat bite",
    ],
    "minor_injury": ["sprain", "sore", "bruises", "scrapes"],
    "blunt_force_injury": ["broken bone", "broken back", "head damage", "broken jaw"],
    "hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
    "cold_injury": ["shivering", "frostbite"],
    "big_bite_injury": [
        "bite-wound",
        "broken bone",
        "torn pelt",
        "mangled leg",
        "mangled tail",
    ],
    "small_bite_injury": ["bite-wound", "torn ear", "torn pelt", "scrapes"],
    "beak_bite": ["beak bite", "torn ear", "scrapes"],
    "rat_bite": ["rat bite", "torn ear", "torn pelt"],
    "sickness": ["greencough", "redcough", "whitecough", "yellowcough"],
}

EVENT_ALLOWED_CONDITIONS = [
    "tick bites",
    "claw-wound",
    "bite-wound",
    "cat bite",
    "beak bite",
    "snake bite",
    "quilled by a porcupine",
    "rat bite",
    "mangled leg",
    "mangled tail",
    "broken jaw",
    "broken bone",
    "sore",
    "bruises",
    "scrapes",
    "cracked pads",
    "small cut",
    "sprain",
    "bee sting",
    "joint pain",
    "dislocated joint",
    "torn pelt",
    "torn ear",
    "water in their lungs",
    "shivering",
    "frostbite",
    "burn",
    "severe burn",
    "shock",
    "dehydrated",
    "head damage",
    "damaged eyes",
    "broken back",
    "poisoned",
    "headache",
    "severe headache",
    "fleas",
    "seizure",
    "diarrhea",
    "running nose",
    "kittencough",
    "whitecough",
    "greencough",
    "yellowcough",
    "redcough",
    "carrionplace disease",
    "heat stroke",
    "heat exhaustion",
    "stomachache",
    "constant nightmares",
]

SUPPLY_TYPES = ["fresh_kill", "all_herb", "any_herb"]
SUPPLY_TYPES.extend(HERBS)

SUPPLY_TRIGGERS = ["always", *Supply]

SUPPLY_ADJUSTMENTS = [
    "reduce_eighth",
    "reduce_quarter",
    "reduce_half",
    "reduce_full",
    "increase_#",
]

with open("resources/game_config.toml", "r", encoding="utf-8") as read_file:
    CONFIG = tomllib.loads(read_file.read())

with open("resources/placements.json", "r", encoding="utf-8") as read_file:
    LAYOUTS = ujson.loads(read_file.read())

CUSTOM_CURSOR = Cursor((9, 0), image.load("resources/images/cursor.png"))
DEFAULT_CURSOR = Cursor(SYSTEM_CURSOR_ARROW)
