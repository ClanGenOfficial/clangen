from typing import TYPE_CHECKING, Optional, List, Dict

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

# This is set up in this way so that IDEs are forced to import the entire switches module rather than make a local copy
# of just one switch.

__switches = {
    "cat": "",
    "clan_name": "",
    "cur_screen": "start screen",
    "saved_clan": False,
    "clan_list": [],
    "error_message": "",
    "traceback": None,
    "biome": "",
    "camp_bg": "",
    "game_mode": "",
    "favorite_sub_tab": None,
    "root_cat": None,
    "skip_conditions": [],
    "show_history_moons": False,
    "fps": 30,
    "war_rel_change_type": "neutral",
    "disallowed_symbol_tags": [],
    "saved_scroll_positions": {},
    "moon_and_seasons_open": False,
    "sort_type": "rank",
}

clan_name: str = ""
cur_screen: str = "start screen"
saved_clan: bool = False
clan_list: List = []
error_message: str = ""
traceback: Optional[BaseException] = None
biome: str = (
    ""  # even though this is used in ONE PLACE and I think it's actually broken
)
camp_bg: str = ""  # same with this
game_mode: str = ""  # and this
favorite_sub_tab: Optional[str] = None
root_cat: Optional["Cat"] = None
skip_conditions: List[str] = []
show_history_moons: bool = False
fps: int = 30
war_rel_change_type: str = "neutral"
disallowed_symbol_tags: List = []
saved_scroll_positions: Dict = {}
moon_and_seasons_open: bool = False
sort_type: str = "rank"


def get_switch(name: str):
    return __switches[name]


def set_switch(name: str, value):
    __switches[name] = value


def reset_switches():
    global cat, clan_name, cur_screen, saved_clan, clan_list, error_message, traceback, biome, camp_bg, game_mode, favorite_sub_tab, root_cat, skip_conditions, show_history_moons, fps, war_rel_change_type, disallowed_symbol_tags, saved_scroll_positions, moon_and_seasons_open, sort_type

    cat = ""
    clan_name = ""
    cur_screen = "start screen"
    saved_clan = False
    clan_list = []
    error_message = ""
    traceback = None

    # even though these are used in just one place and I think they're actually broken
    biome = ""
    camp_bg = ""
    game_mode = ""

    favorite_sub_tab = None
    root_cat = None
    skip_conditions = []
    show_history_moons = False
    fps = 30
    war_rel_change_type = "neutral"
    disallowed_symbol_tags = []
    saved_scroll_positions = {}
    moon_and_seasons_open = False
    sort_type = "rank"
