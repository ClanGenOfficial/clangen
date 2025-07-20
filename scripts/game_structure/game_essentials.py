from typing import Optional, TYPE_CHECKING

import pygame
import ujson

from scripts.event_class import Single_Event
from scripts.game_structure import constants
from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.screen_settings import toggle_fullscreen
from scripts.housekeeping.datadir import get_save_dir

pygame.init()

if TYPE_CHECKING:
    from scripts.clan import Clan


# G A M E
class Game:
    event_editing = False
    max_name_length = 10
    # max_events_displayed = 10
    # event_scroll_ct = 0
    # max_allegiance_displayed = 17
    # allegiance_scroll_ct = 0
    # max_relation_events_displayed = 10
    # relation_scroll_ct = 0

    mediated = []  # Keep track of which couples have been mediated this moon.
    just_died = []  # keeps track of which cats died this moon via die()

    cur_events_list = []
    ceremony_events_list = []
    birth_death_events_list = []
    relation_events_list = []
    health_events_list = []
    other_clans_events_list = []
    misc_events_list = []
    herb_events_list = []
    freshkill_event_list = []

    # Keeping track of various last screen for various purposes
    last_screen_forupdate = "start screen"
    last_screen_forProfile = "list screen"
    last_list_forProfile = None

    choose_cats = {}
    """cat_buttons = {
        'cat0': None,
        'cat1': None,
        'cat2': None,
        'cat3': None,
        'cat4': None,
        'cat5': None,
        'cat6': None,
        'cat7': None,
        'cat8': None,
        'cat9': None,
        'cat10': None,
        'cat11': None
    }"""
    patrol_cats = {}
    patrolled = []

    outsider_reps = ["welcoming", "neutral", "hostile"]
    other_clan_reps = ["ally", "neutral", "hostile"]

    BIOME_TYPES = ["Forest", "Plains", "Mountainous", "Beach", "Wetlands", "Desert"]

    # store changing parts of the game that the user can toggle with buttons

    all_screens = {}

    debug_settings = {
        "showcoords": False,
        "showbounds": False,
        "visualdebugmode": False,
        "showfps": False,
    }

    # CLAN
    clan = None
    cat_class = None
    prey_config = {}

    rpc = None

    is_close_menu_open = False

    def __init__(self, current_screen="start screen"):
        self.current_screen = current_screen
        self.clicked = False
        self.keyspressed = []
        self.switch_screens = False

        self.clan: Optional["Clan"] = None

        with open(f"resources/prey_config.json", "r", encoding="utf-8") as read_file:
            self.prey_config = ujson.loads(read_file.read())

    @property
    def config(self):
        """DEPRECATED: use constants.CONFIG instead"""
        import warnings

        warnings.warn("Use constants.CONFIG instead", DeprecationWarning, 2)
        return constants.CONFIG

    @property
    def switches(self):
        """DEPRECATED: use get_switch(), set_switch(), or helpers instead - WILL CRASH if you try and use this anyway"""
        import warnings

        # unfortunately there's no way to let this one fix itself, so we have to CTD.
        warnings.warn(
            "Use get_switch(), set_switch(), or helpers instead", DeprecationWarning, 2
        )
        raise Exception(
            "game.switches has been deprecated; use get_switch(), set_switch(), or helpers instead. Unrecoverable."
        )

    @property
    def settings(self):
        """DEPRECATED: use get_game_setting() and set_game_setting() or helpers instead.
        WILL CRASH if you try and use this anyway."""
        import warnings

        warnings.warn(
            "Use get_game_setting() and set_game_setting() or helpers instead. WILL CRASH if you try and use this anyway.",
            DeprecationWarning,
            2,
        )
        raise Exception(
            "game.settings has been deprecated, use get_game_setting() and set_game_setting() or helpers instead. Unrecoverable."
        )

    def update_game(self):
        if self.current_screen != switch_get_value(Switch.cur_screen):
            self.current_screen = switch_get_value(Switch.cur_screen)
            self.switch_screens = True
        self.clicked = False
        self.keyspressed = []

    def save_events(self):
        """
        Save current events list to events.json
        """
        events_list = []
        for event in game.cur_events_list:
            events_list.append(event.to_dict())
        safe_save(f"{get_save_dir()}/{game.clan.name}/events.json", events_list)

    def add_faded_offspring_to_faded_cat(self, parent, offspring):
        """In order to siblings to work correctly, and not to lose relation info on fading, we have to keep track of
        both active and faded cat's faded offpsring. This will add a faded offspring to a faded parents file.
        """
        try:
            with open(
                get_save_dir()
                + "/"
                + self.clan.name
                + "/faded_cats/"
                + parent
                + ".json",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_info = ujson.loads(read_file.read())
        except:
            print("ERROR: loading faded cat")
            return False

        cat_info["faded_offspring"].append(offspring)

        safe_save(
            f"{get_save_dir()}/{self.clan.name}/faded_cats/{parent}.json", cat_info
        )

        return True

    def load_events(self):
        """
        Load events from events.json and place into game.cur_events_list.
        """

        clanname = self.clan.name
        events_path = f"{get_save_dir()}/{clanname}/events.json"
        events_list = []
        try:
            with open(events_path, "r", encoding="utf-8") as f:
                events_list = ujson.loads(f.read())
            for event_dict in events_list:
                event_obj = Single_Event.from_dict(event_dict, game.cat_class)
                if event_obj:
                    game.cur_events_list.append(event_obj)
        except FileNotFoundError:
            pass

    def get_config_value(self, *args):
        """Fetches a value from the config dictionary. Pass each key as a
        separate argument, in the same order you would access the dictionary.
        This function will apply war modifiers if the clan is currently at war."""

        war_effected = {
            ("death_related", "leader_death_chance"): (
                "death_related",
                "war_death_modifier_leader",
            ),
            ("death_related", "classic_death_chance"): (
                "death_related",
                "war_death_modifier",
            ),
            ("death_related", "expanded_death_chance"): (
                "death_related",
                "war_death_modifier",
            ),
            ("death_related", "cruel season_death_chance"): (
                "death_related",
                "war_death_modifier",
            ),
            ("condition_related", "classic_injury_chance"): (
                "condition_related",
                "war_injury_modifier",
            ),
            ("condition_related", "expanded_injury_chance"): (
                "condition_related",
                "war_injury_modifier",
            ),
            ("condition_related", "cruel season_injury_chance"): (
                "condition_related",
                "war_injury_modifier",
            ),
        }

        # Get Value
        config_value = constants.CONFIG
        for key in args:
            config_value = config_value[key]

        # Apply war if needed
        if self.clan and self.clan.war.get("at_war", False) and args in war_effected:
            rel_change_type = switch_get_value(Switch.war_rel_change_type)
            # if the war was positively affected this moon, we don't apply war modifier
            # this way we only see increased death/injury when the war is going badly or is neutral
            if rel_change_type != "rel_up":
                # Grabs the modifier
                mod = constants.CONFIG
                for key in war_effected[args]:
                    mod = mod[key]

                config_value -= mod

        return config_value


game: Game = Game()

pygame.display.set_caption("Clan Generator")

toggle_fullscreen(
    fullscreen=game_setting_get("fullscreen"),
    show_confirm_dialog=False,
    ingame_switch=False,
)
