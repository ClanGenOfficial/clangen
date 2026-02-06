from threading import current_thread
from typing import Dict, Optional, Union

import pygame
import pygame_gui
import ujson

import scripts.game_structure.screen_settings
import scripts.screens.screens_core.screens_core
from scripts.game_structure import constants
from scripts.cat.enums import CatGroup
from scripts.game_structure.audio import music_manager
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import (
    switch_set_value,
    switch_get_value,
    Switch,
)
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.game_structure.screen_settings import (
    screen,
)
from scripts.screens.screens_core.screens_core import rebuild_moon_n_season_indicator
from scripts.ui.windows.freshkill import FreshkillManagementWindow
from scripts.ui.windows.herbs import HerbManagementWindow
from scripts.ui.windows.save_check import SaveCheckWindow
from scripts.ui.event_load_animation import EventLoadingAnimation
from scripts.screens.enums import GameScreen
from scripts.ui.scale import ui_scale_blit
from scripts.game_structure import game


class Screens:
    name = None
    game_screen = screen
    last_screen = ""

    # Looking for the shared assets across all screens (game frame, menu buttons etc.)?
    # Due to fullscreen shenanigans, this now lives here:
    # scripts/ui/screen_core/screen_core.py

    menu_buttons = scripts.screens.screens_core.screens_core.menu_buttons
    game_frame = scripts.screens.screens_core.screens_core.game_frame

    active_bg: Optional[str] = None

    def change_screen(self, new_screen):
        """Use this function when switching screens.
        It will handle keeping track of the last screen and cur screen.
        Last screen must be tracked to ensure a clear transition between screens."""

        music_manager.check_music(new_screen)
        # self.exit_screen()
        game.last_screen_forupdate = self.name

        # This keeps track of the last list-like screen for the back button on cat profiles
        if self.name in [GameScreen.CAMP, GameScreen.LIST, GameScreen.EVENTS]:
            game.last_screen_forProfile = self.name

        if new_screen not in [
            GameScreen.LIST,
            GameScreen.PROFILE,
            GameScreen.SPRITE_INSPECT,
            GameScreen.CEREMONY,
            GameScreen.CHANGE_ROLE,
            GameScreen.CHOOSE_MATE,
            GameScreen.CHOOSE_MENTOR,
            GameScreen.CHOOSE_ADOPTIVE_PARENT,
            GameScreen.RELATIONSHIP,
            GameScreen.MEDIATION,
            GameScreen.CHANGE_GENDER,
            GameScreen.FAMILY_TREE,
        ]:
            game.last_list_forProfile = None
            self.current_group = "your_clan"
            self.death_status = "living"
            self.current_page = 1

        switch_set_value(Switch.cur_screen, new_screen)
        game.switch_screens = True
        game.rpc.update_rpc.set()

    def __init__(self, name=None):
        self.active_blur_bg = None
        self.previous_season = ""
        self.bg_transition = False
        self.bg_transition_time = 5
        self.name = name
        if name is not None:
            game.all_screens[name] = self

        # Place to store the loading window(s)
        self.loading_window = {}

        # Dictionary of work done, keyed by the target function name
        self.work_done = {}

        bg = pygame.Surface(scripts.game_structure.screen_settings.game_screen_size)
        bg.fill(constants.CONFIG["theme"]["light_mode_background"])
        bg_dark = pygame.Surface(
            scripts.game_structure.screen_settings.game_screen_size
        )
        bg_dark.fill(constants.CONFIG["theme"]["dark_mode_background"])

        self.game_bgs = {}
        self.fullscreen_bgs = {}

    def loading_screen_start_work(
        self, target: callable, thread_name: str = "work_thread", args: tuple = tuple()
    ) -> PropagatingThread:
        """Creates and starts the work_thread.
        Returns the started thread."""

        work_thread = PropagatingThread(
            target=self._work_target, args=(target, args), name=thread_name, daemon=True
        )

        work_thread.start()

        return work_thread

    def _work_target(self, target, args):
        exp = None
        try:
            target(*args)
        except Exception as e:
            exp = e

        self.work_done[current_thread().name] = True
        if exp:
            raise exp

    def loading_screen_on_use(
        self,
        work_thread: PropagatingThread,
        final_actions: callable,
        loading_screen_pos: tuple = None,
        delay: float = 0.7,
    ) -> None:
        """Handles all actions that must be run every frame for the loading window to work.
        Also handles creating and killing the loading window.
        """

        if not isinstance(work_thread, PropagatingThread):
            return

        # Handled the loading animation, both creating and killing it.
        if (
            not self.loading_window.get(work_thread.name)
            and work_thread.is_alive()
            and work_thread.get_time_from_start() > delay
        ):
            self.loading_window[work_thread.name] = EventLoadingAnimation(
                loading_screen_pos
            )
        elif self.loading_window.get(work_thread.name) and not work_thread.is_alive():
            self.loading_window[work_thread.name].kill()
            self.loading_window.pop(work_thread.name)

        # Handles displaying the events once timeskip is done.
        if self.work_done.get(work_thread.name, False):
            # By this time, the thread should have already finished.
            # This line allows exceptions in the work thread to be
            # passed to the main thread, so issues in the work thread are not
            # silent failures.
            work_thread.join()

            self.work_done.pop(work_thread.name)

            final_actions()

        return

    def on_use(self):
        """Runs every frame this screen is used."""
        self.show_bg()

    def screen_switches(self):
        """Runs when this screen is switched to."""
        Screens.hide_mute_buttons()
        Screens.hide_menu_buttons()
        Screens.menu_buttons = scripts.screens.screens_core.screens_core.menu_buttons
        Screens.game_frame = scripts.screens.screens_core.screens_core.game_frame
        try:
            Screens.update_heading_text(game.clan.displayname + "Clan")
        except AttributeError:
            Screens.update_heading_text("DebugClan")
        if self.active_bg is None or "default" in self.active_bg:
            self.set_bg(None)
        self.bg_transition = True

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here."""
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            out = self.mute_button_pressed(event)
            if out:
                return

    def exit_screen(self):
        """Runs when screen exits"""
        pass

    # Functions to deal with the menu and mute button.
    #   The menu is used very often, so I don't want to keep
    #   recreating and killing it. Lots of chances for bugs there.

    @classmethod
    def hide_menu_buttons(cls):
        """This hides the menu buttons, so they are no longer visible
        or interact-able. It does not delete the buttons from memory."""
        for name, button in cls.menu_buttons.items():
            button.hide()

    @classmethod
    def show_menu_buttons(cls):
        """This shows all menu buttons, and makes them interact-able."""
        rebuild_moon_n_season_indicator()

        for name, button in cls.menu_buttons.items():
            if name in [
                "mute_button",
                "unmute_button",
            ]:
                continue
            else:
                button.show()

    @classmethod
    def hide_mute_buttons(cls):
        """this hides the mute buttons, so they are no longer visible
        or interact-able. It does not delete the buttons from memory."""

        Screens.menu_buttons["mute_button"].hide()
        Screens.menu_buttons["unmute_button"].hide()

    @classmethod
    def show_mute_buttons(cls):
        """This shows all mute buttons, and makes them interact-able."""

        if music_manager.muted or music_manager.audio_disabled:
            cls.menu_buttons["unmute_button"].show()
            cls.menu_buttons["mute_button"].hide()
        else:
            cls.menu_buttons["unmute_button"].hide()
            cls.menu_buttons["mute_button"].show()

    def mute_button_pressed(self, event):
        """This is a short-up to deal with mute button presses.
        This will fail if event.type != pygame_gui.UI_BUTTON_START_PRESS"""
        if event.ui_element == Screens.menu_buttons["mute_button"]:
            music_manager.mute_music()
            Screens.show_mute_buttons()
            return True
        elif event.ui_element == Screens.menu_buttons["unmute_button"]:
            out = music_manager.unmute_music(self.name)
            Screens.show_mute_buttons()
            return out
        else:
            return False

    @classmethod
    def set_mute_button_position(cls, position: str):
        scripts.screens.screens_core.screens_core.rebuild_mute(position)

    @classmethod
    def set_disabled_menu_buttons(cls, disabled_buttons=()):
        """This sets all menu buttons as interact-able, except buttons listed in disabled_buttons."""
        for name, button in cls.menu_buttons.items():
            button.disable() if name in disabled_buttons or name == "season_indicator" else button.enable()

    def menu_button_pressed(self, event):
        """This is a short-up to deal with menu button presses.
        This will fail if event.type != pygame_gui.UI_BUTTON_START_PRESS"""

        # VIEW EVENTS
        if event.ui_element == Screens.menu_buttons["events"]:
            self.change_screen(GameScreen.EVENTS)
        # OPEN FRESHKILL
        elif (
            Screens.menu_buttons.get("supplies")
            and event.ui_element
            == Screens.menu_buttons["supplies"].child_button_dicts[
                "screens.core.freshkill"
            ]
        ):
            FreshkillManagementWindow()
        # OPEN HERB
        elif (
            Screens.menu_buttons.get("supplies")
            and event.ui_element
            == Screens.menu_buttons["supplies"].child_button_dicts["screens.core.herbs"]
        ):
            HerbManagementWindow()
        # OPEN LEADER
        elif (
            event.ui_element
            == Screens.menu_buttons["dens"].child_button_dicts[
                "screens.core.leader_den"
            ]
        ):
            self.change_screen(GameScreen.LEADER_DEN)
        # OPEN MEDICINE
        elif (
            event.ui_element
            == Screens.menu_buttons["dens"].child_button_dicts[
                "screens.core.medicine_cat_den"
            ]
        ):
            self.change_screen(GameScreen.MED_DEN)
        # OPEN WARRIOR
        elif (
            event.ui_element
            == Screens.menu_buttons["dens"].child_button_dicts[
                "screens.core.warriors_den"
            ]
        ):
            self.change_screen(GameScreen.WARRIOR_DEN)
        # OPEN CLEARING/MEDIATOR
        elif (
            event.ui_element
            == Screens.menu_buttons["dens"].child_button_dicts["screens.core.clearing"]
        ):
            self.change_screen(GameScreen.MEDIATION)
        # GO TO CAMP
        elif event.ui_element in (
            Screens.menu_buttons["back_to_camp"],
            Screens.menu_buttons["heading"],
        ):
            self.change_screen(GameScreen.CAMP)
        # VIEW CATS
        elif event.ui_element == Screens.menu_buttons["cats"]:
            self.change_screen(GameScreen.LIST)
        # PATROL
        elif event.ui_element == Screens.menu_buttons["patrols"]:
            self.change_screen(GameScreen.PATROL)
        # MAIN MENU
        elif event.ui_element == Screens.menu_buttons["main_menu"]:
            SaveCheckWindow(
                switch_get_value(Switch.cur_screen),
                True,
                Screens.menu_buttons["main_menu"],
            )
        # ALLEGIANCES
        elif event.ui_element == Screens.menu_buttons["allegiances"]:
            self.change_screen(GameScreen.ALLEGIANCES)
        # CLAN SETTINGS
        elif event.ui_element == Screens.menu_buttons["clan_settings"]:
            self.change_screen(GameScreen.CLAN_SETTINGS)

    @classmethod
    def update_heading_text(cls, text, text_kwargs=None):
        """Updates the menu heading text"""
        cls.menu_buttons["heading"].set_text(text, text_kwargs=text_kwargs)

    def add_bgs(
        self,
        bgs: Dict[str, pygame.Surface],
        blur_bgs: Dict[str, Union[pygame.Surface, None]] = None,
        radius: int = 5,
        vignette_alpha: int = None,
    ):
        """
        Add custom backgrounds to the Screen.
        :param bgs: A dictionary of names and Surfaces representing the game window background
        :param blur_bgs: A dictionary of names and Surfaces/None representing the fullscreen backdrop.
        If a key is supplied with a None value, the default clan season background will be used.
        If no matching key is supplied, the input bg will be appropriately scaled and blurred to fit. Optional.
        :param radius: If a bg is missing a corresponding blur_bg value, this value determines how much
        to blur the bg to make the background. Default 10.
        :param vignette_alpha: Change the strength of the vignette. Value must be between 0 and 255. Default 0 (disabled/none).
        :return: None
        """

        # intialise the vignette strength
        vignette = scripts.screens.screens_core.screens_core.vignette
        if vignette_alpha is None:
            vignette_alpha = constants.CONFIG["theme"]["fullscreen_background"][
                "dark" if game_setting_get("dark mode") else "light"
            ]["vignette_alpha"]
        if not (0 <= vignette_alpha <= 255):
            raise Exception("Vignette alpha out of range. Permitted values: 0-255.")
        vignette.set_alpha(vignette_alpha)

        # add the bg to the game bgs.
        for name, bg in bgs.items():
            self.game_bgs[name] = pygame.transform.scale(
                bg, scripts.game_structure.screen_settings.game_screen_size
            )

            # if blur_bgs exists
            if blur_bgs is not None and name in blur_bgs:
                if blur_bgs[name] is None:
                    self.fullscreen_bgs[name] = "default"
                    continue

                # there's an input blur_bg here, so scale it
                self.fullscreen_bgs[
                    name
                ] = scripts.screens.screens_core.screens_core.process_blur_bg(
                    blur_bgs[name], blur_radius=0, vignette_strength=vignette_alpha
                )
                continue

            # no blur_bg, so blur the input bg to become the fullscreen backing
            # also blit the vignette & game frame over the top of that for performance
            self.fullscreen_bgs[
                name
            ] = scripts.screens.screens_core.screens_core.process_blur_bg(
                bg, blur_radius=radius, vignette_strength=vignette_alpha
            )

    def set_bg(self, bg: Optional[str] = None, blur_bg: Optional[str] = None):
        """
        Set the currently active background for a screen.
        :param bg: "default", or a key in either the game_bgs or default_game_bgs dictionaries.
        :return: None
        """

        # if the input is default, select the right default for the display mode
        if bg is None:
            self.active_bg = "default"
        elif (
            bg in self.game_bgs
            or bg
            in scripts.screens.screens_core.screens_core.default_game_bgs[self.theme]
        ):
            self.active_bg = bg
        else:
            raise Exception(f"Unidentified background requested: '{bg}'")

        if blur_bg is None:
            self.active_blur_bg = self.active_bg
        elif (
            blur_bg in self.fullscreen_bgs
            or blur_bg
            in scripts.screens.screens_core.screens_core.default_fullscreen_bgs[
                self.theme
            ]
        ):
            self.active_blur_bg = blur_bg
        else:
            raise Exception(
                f"Unidentified fullscreen background requested: '{blur_bg}'"
            )

        # enable the transition to get that sweet, sweet fullscreen fade.
        self.bg_transition = True

    def show_bg(self, theme=None):
        """Blit the currently selected blur_bg and bg. Must be called somewhere in on_use.
        :param theme: Allows overriding the displayed theme (dark/light mode).
        """

        if theme is None:
            theme = self.theme

        # make the right string to pull the correct camp image
        try:
            season = game.clan.current_season
            season_bg = (
                scripts.screens.screens_core.screens_core.default_fullscreen_bgs[theme][
                    season
                ]
            )
        except (
            AttributeError
        ):  # We haven't initialised a clan (fresh install) so there's no current season.
            season = "Newleaf"
            season_bg = (
                scripts.screens.screens_core.screens_core.default_fullscreen_bgs[theme][
                    "Newleaf"
                ]
            )

        # handle custom screen backgrounds (non-default)
        if self.active_bg in self.game_bgs:
            bg = self.game_bgs[self.active_bg]
        # handle default screen backgrounds
        elif (
            self.active_bg
            in scripts.screens.screens_core.screens_core.default_game_bgs[theme]
        ):
            bg = scripts.screens.screens_core.screens_core.default_game_bgs[theme][
                self.active_bg
            ]
        else:
            raise Exception(
                f"Selected game background not recognised! '{self.active_bg}' not in default or custom bgs"
            )

        if self.active_blur_bg == "default" or self.active_blur_bg == season:
            blur_bg = season_bg
        elif self.name in [
            GameScreen.START,
            GameScreen.SETTINGS,
            GameScreen.SWITCH_CLAN,
        ]:
            # if we're in the main menu levels, display the main menu bg
            blur_bg = scripts.screens.screens_core.screens_core.default_fullscreen_bgs[
                theme
            ]["mainmenu_bg"]
        elif self.active_blur_bg in self.fullscreen_bgs:
            blur_bg = self.fullscreen_bgs[self.active_blur_bg]
        elif (
            self.active_blur_bg
            in scripts.screens.screens_core.screens_core.default_fullscreen_bgs[theme]
        ):
            blur_bg = scripts.screens.screens_core.screens_core.default_fullscreen_bgs[
                theme
            ][self.active_blur_bg]
        else:
            raise Exception(
                f"Selected fullscreen background not recognised! '{self.active_blur_bg}' not in default or custom bgs"
            )

        if (
            self.previous_season != season
            and self.active_blur_bg == "default"
            or self.active_blur_bg == season
        ):
            self.bg_transition_time = 10  # doubled transition time for the Vibes
            self.previous_season = season
        # onto the actual blitting
        # handle the blur bg
        if (
            scripts.game_structure.screen_settings.game_screen_size
            != scripts.game_structure.screen_settings.screen.get_size()
        ):
            # enable the transition if required
            if self.bg_transition:
                # this determines how many frames the fade can show for
                # in order to remove visual artifacts
                self.bg_transition_time = 5
                self.bg_transition = False

            # actually run the transition
            if self.bg_transition_time > 0:
                temp = blur_bg.copy()
                temp.set_alpha(
                    255 // self.bg_transition_time
                )  # this determines the actual fade rate
                scripts.game_structure.screen_settings.screen.blit(temp, (0, 0))
                self.bg_transition_time -= 1
            else:
                # if we've done the transition, just blit the full-alpha version on top to remove artifacts.
                scripts.game_structure.screen_settings.screen.blit(blur_bg, (0, 0))
        # now blit the foreground.
        scripts.game_structure.screen_settings.screen.blit(bg, ui_scale_blit((0, 0)))

    def set_cat_location_bg(self, cat, bg: str = "default"):
        if cat.dead and not cat.faded:
            if cat.status.group == CatGroup.STARCLAN:
                blur_bg = "starclan"
            elif cat.status.group == CatGroup.DARK_FOREST:
                blur_bg = "darkforest"
            else:
                blur_bg = "unknown_residence"
            self.set_bg(bg=bg, blur_bg=blur_bg)
        else:
            self.set_bg(bg=bg)

    def display_change_save(self) -> Dict:
        """
        Used to save a dictionary of data to help rebuild the screen the way it was when we return.
        :return: A dictionary of data to be used later to rebuild the screen
        """
        return {
            "heading": scripts.screens.screens_core.screens_core.menu_buttons[
                "heading"
            ].text
        }

    def display_change_load(self, variable_dict: Dict):
        """
        Used to load the screen back to how it was following a display change.
        :return: None
        """
        try:
            scripts.screens.screens_core.screens_core.menu_buttons["heading"].set_text(
                variable_dict.pop("heading")
            )
        except KeyError:
            pass

    @property
    def theme(self) -> str:
        try:
            return "dark" if game_setting_get("dark mode") else "light"
        except AttributeError:
            with open(
                "resources/gamesettings.json", "r", encoding="utf-8"
            ) as read_file:
                _settings = ujson.loads(read_file.read())
                return "dark" if _settings["dark mode"] else "light"

    # pragma pylint: disable=no-member
    # noinspection PyUnresolvedReferences
    def update_previous_next_cat_buttons(self):
        """Updates disabled status of previous and next cat buttons. Does nothing if the screen does not have both previous and next cat buttons."""
        if not hasattr(self, "previous_cat_button") or not hasattr(
            self, "next_cat_button"
        ):
            return

        self.previous_cat_button.enable() if hasattr(
            self, "previous_cat"
        ) and self.previous_cat else self.previous_cat_button.disable()

        self.next_cat_button.enable() if hasattr(
            self, "next_cat"
        ) and self.next_cat else self.next_cat_button.disable()

    # pragma pylint: enable=no-member

    @staticmethod
    def chunks(L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
