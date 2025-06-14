import dataclasses
from typing import TYPE_CHECKING, Optional, List, Dict

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

cat: Optional["Cat"] = None
clan_name: str = ""
cur_screen: str = "start screen"
saved_clan: bool = False
clan_list: List = dataclasses.field(default_factory=lambda: [])
error_message: str = ""
traceback: Optional[BaseException] = None
biome: str = (
    ""  # even though this is used in ONE PLACE and I think it's actually broken
)
camp_bg: str = ""  # same with this
game_mode: str = ""  # and this
favorite_sub_tab: Optional[str] = None
root_cat: Optional["Cat"] = None
skip_conditions: List[str] = dataclasses.field(default_factory=lambda: [])
show_history_moons: bool = False
fps: int = 30
war_rel_change_type: str = "neutral"
disallowed_symbol_tags: List = dataclasses.field(default_factory=lambda: [])
saved_scroll_positions: Dict = dataclasses.field(default_factory=lambda: {})
moon_and_seasons_open: bool = False
