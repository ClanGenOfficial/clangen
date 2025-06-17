import os
import traceback

import pygame
import ujson

from scripts.event_class import Single_Event
from scripts.game_structure import switches, constants
from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.screen_settings import toggle_fullscreen
from scripts.housekeeping.datadir import get_save_dir, get_temp_dir

pygame.init()


# G A M E
class Game:
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

    # down = pygame.image.load("resources/images/buttons/arrow_down.png").convert_alpha()
    # up = pygame.image.load("resources/images/buttons/arrow_up.png").convert_alpha()

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

    # store changing parts of the game that the user can toggle with buttons

    all_screens = {}

    # SETTINGS
    settings = {}
    settings["moon_and_seasons_open"] = False
    setting_lists = {}

    debug_settings = {
        "showcoords": False,
        "showbounds": False,
        "visualdebugmode": False,
        "showfps": False,
    }

    # Init Settings
    with open("resources/gamesettings.json", "r", encoding="utf-8") as read_file:
        _settings = ujson.loads(read_file.read())

    for setting, values in _settings["__other"].items():
        settings[setting] = values[0]
        setting_lists[setting] = values

    _ = []
    _.append(_settings["general"])

    for cat in _:  # Add all the settings to the settings dictionary
        for setting_name, inf in cat.items():
            settings[setting_name] = inf[2]
            setting_lists[setting_name] = [inf[2], not inf[2]]
    del _settings
    del _
    # End init settings

    settings_changed = False

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
        """DEPRECATED: use switches.[key] instead - WILL CRASH if you try and use this anyway"""
        import warnings

        # unfortunately there's no way to let this one fix itself, so we have to CTD.
        warnings.warn("Use switches.[key] instead", DeprecationWarning, 2)
        raise Exception(
            "game.switches has been deprecated, use switches.[key] instead. Unrecoverable."
        )

    def update_game(self):
        if self.current_screen != switches.cur_screen:
            self.current_screen = switches.cur_screen
            self.switch_screens = True
        self.clicked = False
        self.keyspressed = []

    def switch_setting(self, setting_name):
        """Call this function to change a setting given in the parameter by one to the right on it's list"""
        self.settings_changed = True

        # Give the index that the list is currently at
        list_index = self.setting_lists[setting_name].index(self.settings[setting_name])

        if (
            list_index == len(self.setting_lists[setting_name]) - 1
        ):  # The option is at the list's end, go back to 0
            self.settings[setting_name] = self.setting_lists[setting_name][0]
        else:
            # Else move on to the next item on the list
            self.settings[setting_name] = self.setting_lists[setting_name][
                list_index + 1
            ]

    def save_cats(self):
        """Save the cat data."""

        clanname = ""
        """ if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]"""
        if game.clan is not None:
            clanname = game.clan.name
        directory = get_save_dir() + "/" + clanname
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Delete all existing relationship files
        if not os.path.exists(directory + "/relationships"):
            os.makedirs(directory + "/relationships")
        for f in os.listdir(directory + "/relationships"):
            os.remove(os.path.join(directory + "/relationships", f))

        self.save_faded_cats(clanname)  # Fades cat and saves them, if needed

        clan_cats = []
        for inter_cat in self.cat_class.all_cats.values():
            cat_data = inter_cat.get_save_dict()
            clan_cats.append(cat_data)

            inter_cat.save_condition()

            if inter_cat.history:
                inter_cat.save_history(directory + "/history")
                # after saving, dump the history info
                inter_cat.history = None
            if not inter_cat.dead:
                inter_cat.save_relationship_of_cat(directory + "/relationships")

        safe_save(f"{get_save_dir()}/{clanname}/clan_cats.json", clan_cats)

    def save_faded_cats(self, clanname):
        """Deals with fades cats, if needed, adding them as faded"""
        if game.cat_to_fade:
            directory = get_save_dir() + "/" + clanname + "/faded_cats"
            if not os.path.exists(directory):
                os.makedirs(directory)

        copy_of_info = ""
        for cat in game.cat_to_fade:
            inter_cat = self.cat_class.all_cats[cat]

            # Add ID to list of faded cats.
            self.clan.faded_ids.append(cat)

            # If they have a mate, break it up
            if inter_cat.mate:
                for mate_id in inter_cat.mate:
                    if mate_id in self.cat_class.all_cats:
                        self.cat_class.all_cats[mate_id].unset_mate(inter_cat)

            # If they have parents, add them to their parents "faded offspring" list:
            for x in inter_cat.get_parents():
                if x in self.cat_class.all_cats:
                    self.cat_class.all_cats[x].faded_offspring.append(cat)
                else:
                    parent_faded = self.add_faded_offspring_to_faded_cat(x, cat)
                    if not parent_faded:
                        print(f"WARNING: Can't find parent {x} of {cat.name}")

            # Get a copy of info
            if game.clan.clan_settings["save_faded_copy"]:
                copy_of_info += (
                    ujson.dumps(inter_cat.get_save_dict(), indent=4)
                    + "\n--------------------------------------------------------------------------\n"
                )

            # SAVE TO ITS OWN LITTLE FILE. This is a trimmed-down version for relation keeping only.
            cat_data = inter_cat.get_save_dict(faded=True)

            safe_save(f"{get_save_dir()}/{clanname}/faded_cats/{cat}.json", cat_data)

            # Remove the cat from the active cats lists
            self.clan.remove_cat(cat)

        game.cat_to_fade = []

        # Save the copies, flush the file.
        if game.clan.clan_settings["save_faded_copy"]:
            with open(
                get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
                "a",
                encoding="utf-8",
            ) as write_file:
                if not os.path.exists(
                    get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt"
                ):
                    # Create the file if it doesn't exist
                    with open(
                        get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
                        "w",
                        encoding="utf-8",
                    ) as create_file:
                        pass

                with open(
                    get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
                    "a",
                    encoding="utf-8",
                ) as write_file:
                    write_file.write(copy_of_info)

                    write_file.flush()
                    os.fsync(write_file.fileno())

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
            # Grabs the modifer
            mod = constants.CONFIG
            for key in war_effected[args]:
                mod = mod[key]

            config_value -= mod

        return config_value


game: Game = Game()

pygame.display.set_caption("Clan Generator")

toggle_fullscreen(
    fullscreen=game.settings["fullscreen"],
    show_confirm_dialog=False,
    ingame_switch=False,
)
