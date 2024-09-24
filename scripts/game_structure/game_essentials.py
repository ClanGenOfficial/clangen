import os
from ast import literal_eval
from shutil import move as shutil_move

import pygame
import pygame_gui
import ujson

from scripts.event_class import Single_Event
from scripts.housekeeping.datadir import get_save_dir, get_temp_dir

pygame.init()


# G A M E
class Game:
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

    allegiance_list = []
    language = {}
    game_mode = ""
    language_list = ["english", "spanish", "german"]
    game_mode_list = ["classic", "expanded", "cruel season"]

    cat_to_fade = []
    sub_tab_list = ["life events", "user notes"]

    # Keeping track of various last screen for various purposes
    last_screen_forupdate = "start screen"
    last_screen_forProfile = "list screen"
    last_list_forProfile = None

    # down = pygame.image.load("resources/images/buttons/arrow_down.png").convert_alpha()
    # up = pygame.image.load("resources/images/buttons/arrow_up.png").convert_alpha()

    # Sort-type
    sort_type = "rank"

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
    switches = {
        "cat": None,
        "clan_name": "",
        "leader": None,
        "deputy": None,
        "medicine_cat": None,
        "members": [],
        "re_roll": False,
        "roll_count": 0,
        "event": None,
        "cur_screen": "start screen",
        "naming_text": "",
        "timeskip": False,
        "mate": None,
        "choosing_mate": False,
        "mentor": None,
        "setting": None,
        "save_settings": False,
        "list_page": 1,
        "last_screen": "start screen",
        "events_left": 0,
        "save_clan": False,
        "saved_clan": False,
        "new_leader": False,
        "apprentice_switch": False,
        "deputy_switch": False,
        "clan_list": "",
        "switch_clan": False,
        "read_clans": False,
        "kill_cat": False,
        "current_patrol": [],
        "patrol_remove": False,
        "cat_remove": False,
        "fill_patrol": False,
        "patrol_done": False,
        "error_message": "",
        "traceback": "",
        "apprentice": None,
        "change_name": "",
        "change_suffix": "",
        "name_cat": None,
        "biome": None,
        "camp_bg": None,
        "language": "english",
        "options_tab": None,
        "profile_tab_group": None,
        "sub_tab_group": None,
        "gender_align": None,
        "show_details": False,
        "chosen_cat": None,
        "game_mode": "",
        "set_game_mode": False,
        "broke_up": False,
        "show_info": False,
        "patrol_chosen": "general",
        "favorite_sub_tab": None,
        "root_cat": None,
        "window_open": False,
        "skip_conditions": [],
        "show_history_moons": False,
        "fps": 30,
        "war_rel_change_type": "neutral",
        "disallowed_symbol_tags": [],
        "audio_mute": False,
        "saved_scroll_positions": {},
        "moon&season_open": False,
    }
    all_screens = {}
    cur_events = {}
    map_info = {}

    # SETTINGS
    settings = {}
    settings["moon&season_open"] = False
    setting_lists = {}

    debug_settings = {
        "showcoords": False,
        "showbounds": False,
        "visualdebugmode": False,
        "showfps": False,
    }

    # Init Settings
    with open("resources/gamesettings.json", "r") as read_file:
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
    config = {}
    prey_config = {}

    rpc = None

    is_close_menu_open = False

    def __init__(self, current_screen="start screen"):
        self.current_screen = current_screen
        self.clicked = False
        self.keyspressed = []
        self.switch_screens = False

        with open(f"resources/game_config.json", "r") as read_file:
            self.config = ujson.loads(read_file.read())

        with open(f"resources/prey_config.json", "r") as read_file:
            self.prey_config = ujson.loads(read_file.read())

        if self.config["fun"]["april_fools"]:
            self.config["fun"]["newborns_can_roam"] = True
            self.config["fun"]["newborns_can_patrol"] = True

    def update_game(self):
        if self.current_screen != self.switches["cur_screen"]:
            self.current_screen = self.switches["cur_screen"]
            self.switch_screens = True
        self.clicked = False
        self.keyspressed = []


    @staticmethod
    def safe_save(path: str, write_data, check_integrity=False, max_attempts: int = 15):
        """If write_data is not a string, assumes you want this
        in json format. If check_integrity is true, it will read back the file
        to check that the correct data has been written to the file.
        If not, it will simply write the data to the file with no other
        checks."""

        # If write_data is not a string,
        if type(write_data) is not str:
            _data = ujson.dumps(write_data, indent=4)
        else:
            _data = write_data

        dir_name, file_name = os.path.split(path)

        if check_integrity:
            if not file_name:
                raise RuntimeError(f"Safe_Save: No file name was found in {path}")

            temp_file_path = get_temp_dir() + "/" + file_name + ".tmp"
            i = 0
            while True:
                # Attempt to write to temp file
                with open(temp_file_path, "w") as write_file:
                    write_file.write(_data)
                    write_file.flush()
                    os.fsync(write_file.fileno())

                # Read the entire file back in
                with open(temp_file_path, "r") as read_file:
                    _read_data = read_file.read()

                if _data != _read_data:
                    i += 1
                    if i > max_attempts:
                        print(
                            f"Safe_Save ERROR: {file_name} was unable to properly save {i} times. Saving Failed."
                        )
                        raise RuntimeError(
                            f"Safe_Save: {file_name} was unable to properly save {i} times!"
                        )
                    print(
                        f"Safe_Save: {file_name} was incorrectly saved. Trying again."
                    )
                    continue

                # This section is reached is the file was not nullied. Move the file and return True

                shutil_move(temp_file_path, path)
                return
        else:
            os.makedirs(dir_name, exist_ok=True)
            with open(path, "w") as write_file:
                write_file.write(_data)
                write_file.flush()
                os.fsync(write_file.fileno())

    def read_clans(self):
        """with open(get_save_dir() + '/clanlist.txt', 'r') as read_file:
            clan_list = read_file.read()
            if_clans = len(clan_list)
        if if_clans > 0:
            clan_list = clan_list.split('\n')
            clan_list = [i.strip() for i in clan_list if i]  # Remove empty and whitespace
            return clan_list
        else:
            return None"""
        # All of the above is old code
        # Now, we want clanlist.txt to contain ONLY the name of the Clan that is currently loaded
        # We will get the list of clans from the saves folder
        # each Clan has its own folder, and the name of the folder is the name of the clan
        # so we can just get a list of all the folders in the saves folder

        # First, we need to make sure the saves folder exists
        if not os.path.exists(get_save_dir()):
            os.makedirs(get_save_dir())
            print("Created saves folder")
            return None

        # Now we can get a list of all the folders in the saves folder
        clan_list = [f.name for f in os.scandir(get_save_dir()) if f.is_dir()]

        # the Clan specified in saves/clanlist.txt should be first in the list
        # so we can load it automatically

        if os.path.exists(get_save_dir() + "/clanlist.txt"):
            with open(get_save_dir() + "/clanlist.txt", "r") as f:
                loaded_clan = f.read().strip().splitlines()
                if loaded_clan:
                    loaded_clan = loaded_clan[0]
                else:
                    loaded_clan = None
            os.remove(get_save_dir() + "/clanlist.txt")
            if loaded_clan:
                self.safe_save(get_save_dir() + "/currentclan.txt", loaded_clan)
        elif os.path.exists(get_save_dir() + "/currentclan.txt"):
            with open(get_save_dir() + "/currentclan.txt", "r") as f:
                loaded_clan = f.read().strip()
        else:
            loaded_clan = None

        if loaded_clan and loaded_clan in clan_list:
            clan_list.remove(loaded_clan)
            clan_list.insert(0, loaded_clan)

        # Now we can return the list of clans
        if not clan_list:
            print("No clans found")
            return None
        return clan_list

    def save_clanlist(self, loaded_clan=None):
        """clans = []
        if loaded_clan:
            clans.append(f"{loaded_clan}\n")

        for clan_name in self.switches['clan_list']:
            if clan_name and clan_name != loaded_clan:
                clans.append(f"{clan_name}\n")

        if clans:
            with open(get_save_dir() + '/clanlist.txt', 'w') as f:
                f.writelines(clans)"""
        if loaded_clan:
            if os.path.exists(get_save_dir() + "/clanlist.txt"):
                # we don't need clanlist.txt anymore
                os.remove(get_save_dir() + "/clanlist.txt")
            game.safe_save(f"{get_save_dir()}/currentclan.txt", loaded_clan)
        else:
            if os.path.exists(get_save_dir() + "/currentclan.txt"):
                os.remove(get_save_dir() + "/currentclan.txt")

    def save_settings(self):
        """Save user settings for later use"""
        if os.path.exists(get_save_dir() + "/settings.txt"):
            os.remove(get_save_dir() + "/settings.txt")

        self.settings_changed = False
        game.safe_save(get_save_dir() + "/settings.json", self.settings)

    def load_settings(self):
        """Load settings that user has saved from previous use"""

        try:
            with open(get_save_dir() + "/settings.json", "r") as read_file:
                settings_data = ujson.loads(read_file.read())
        except FileNotFoundError:
            return

        for key, value in settings_data.items():
            if key in self.settings:
                self.settings[key] = value

        self.switches["language"] = self.settings["language"]
        if self.settings["language"] != "english":
            self.switch_language()

    def switch_language(self):
        # add translation information here
        if os.path.exists("languages/" + game.settings["language"] + ".txt"):
            with open(
                "languages/" + game.settings["language"] + ".txt", "r"
            ) as read_file:
                raw_language = read_file.read()
            game.language = literal_eval(raw_language)

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

        self.safe_save(f"{get_save_dir()}/{clanname}/clan_cats.json", clan_cats)

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

            # SAVE TO IT'S OWN LITTLE FILE. This is a trimmed-down version for relation keeping only.
            cat_data = inter_cat.get_save_dict(faded=True)

            self.safe_save(
                f"{get_save_dir()}/{clanname}/faded_cats/{cat}.json", cat_data
            )

            # Remove the cat from the active cats lists
            self.clan.remove_cat(cat)

        game.cat_to_fade = []

        # Save the copies, flush the file.
        if game.clan.clan_settings["save_faded_copy"]:
            with open(
                get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt", "a"
            ) as write_file:

                if not os.path.exists(
                    get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt"
                ):
                    # Create the file if it doesn't exist
                    with open(
                        get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
                        "w",
                    ) as create_file:
                        pass

                with open(
                    get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt", "a"
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
        game.safe_save(f"{get_save_dir()}/{game.clan.name}/events.json", events_list)

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
            ) as read_file:
                cat_info = ujson.loads(read_file.read())
        except:
            print("ERROR: loading faded cat")
            return False

        cat_info["faded_offspring"].append(offspring)

        self.safe_save(
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
            with open(events_path, "r") as f:
                events_list = ujson.loads(f.read())
            for event_dict in events_list:
                event_obj = Single_Event.from_dict(event_dict)
                if event_obj:
                    game.cur_events_list.append(event_obj)
        except FileNotFoundError:
            pass

    def get_config_value(self, *args):
        """Fetches a value from the self.config dictionary. Pass each key as a
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
        config_value = self.config
        for key in args:
            config_value = config_value[key]

        # Apply war if needed
        if self.clan and self.clan.war.get("at_war", False) and args in war_effected:
            # Grabs the modifer
            mod = self.config
            for key in war_effected[args]:
                mod = mod[key]

            config_value -= mod

        return config_value


game = Game()

if not os.path.exists(get_save_dir() + "/settings.txt"):
    os.makedirs(get_save_dir(), exist_ok=True)
    with open(get_save_dir() + "/settings.txt", "w") as write_file:
        write_file.write("")
game.load_settings()

pygame.display.set_caption("Clan Generator")

if game.settings["fullscreen"]:
    screen_x, screen_y = 1600, 1400
    screen = pygame.display.set_mode(
        (screen_x, screen_y), pygame.FULLSCREEN | pygame.SCALED
    )
else:
    screen_x, screen_y = 800, 700
    screen = pygame.display.set_mode((screen_x, screen_y))


def load_manager(res: tuple):
    # initialize pygame_gui manager, and load themes
    manager = pygame_gui.ui_manager.UIManager(
        res, "resources/theme/defaults.json", enable_live_theme_updates=False
    )
    manager.add_font_paths(
        font_name="notosans",
        regular_path="resources/fonts/NotoSans-Medium.ttf",
        bold_path="resources/fonts/NotoSans-ExtraBold.ttf",
        italic_path="resources/fonts/NotoSans-MediumItalic.ttf",
        bold_italic_path="resources/fonts/NotoSans-ExtraBoldItalic.ttf",
    )

    if res[0] > 800:
        manager.get_theme().load_theme("resources/theme/defaults.json")
        manager.get_theme().load_theme("resources/theme/buttons.json")
        manager.get_theme().load_theme("resources/theme/text_boxes.json")
        manager.get_theme().load_theme("resources/theme/text_boxes_dark.json")
        manager.get_theme().load_theme("resources/theme/vertical_scroll_bar.json")
        manager.get_theme().load_theme("resources/theme/horizontal_scroll_bar.json")
        manager.get_theme().load_theme("resources/theme/window_base.json")
        manager.get_theme().load_theme("resources/theme/tool_tips.json")

        manager.preload_fonts(
            [
                {"name": "notosans", "point_size": 30, "style": "italic"},
                {"name": "notosans", "point_size": 26, "style": "italic"},
                {"name": "notosans", "point_size": 30, "style": "bold"},
                {"name": "notosans", "point_size": 26, "style": "bold"},
                {"name": "notosans", "point_size": 22, "style": "bold"},
            ]
        )

    else:
        manager.get_theme().load_theme("resources/theme/defaults_small.json")
        manager.get_theme().load_theme("resources/theme/buttons_small.json")
        manager.get_theme().load_theme("resources/theme/text_boxes_small.json")
        manager.get_theme().load_theme("resources/theme/text_boxes_dark_small.json")
        manager.get_theme().load_theme("resources/theme/vertical_scroll_bar_small.json")
        manager.get_theme().load_theme(
            "resources/theme/horizontal_scroll_bar_small.json"
        )
        manager.get_theme().load_theme("resources/theme/window_base_small.json")
        manager.get_theme().load_theme("resources/theme/tool_tips_small.json")
        manager.get_theme().load_theme("resources/theme/horizontal_slider.json")

        manager.preload_fonts(
            [
                {"name": "notosans", "point_size": 11, "style": "bold"},
                {"name": "notosans", "point_size": 13, "style": "bold"},
                {"name": "notosans", "point_size": 15, "style": "bold"},
                {"name": "notosans", "point_size": 13, "style": "italic"},
                {"name": "notosans", "point_size": 15, "style": "italic"},
            ]
        )

    manager.get_theme().load_theme("resources/theme/windows.json")
    manager.get_theme().load_theme("resources/theme/image_buttons.json")

    return manager


MANAGER = load_manager((screen_x, screen_y))
