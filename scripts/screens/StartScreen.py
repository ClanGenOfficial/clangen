# pylint: disable=line-too-long
"""

This file contains:
  The start screen,
  The switch clan screen,
  The settings screen,
  And the statistics screen.



"""  # pylint: enable=line-too-long

import logging
import os
import platform
import subprocess
import traceback
from html import escape

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from requests.exceptions import RequestException, Timeout

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.audio import music_manager
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import UIImageButton, UISurfaceImageButton
from scripts.game_structure.windows import UpdateAvailablePopup, ChangelogPopup
from scripts.utility import ui_scale, quit, ui_scale_dimensions
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..housekeeping.datadir import get_data_dir, get_cache_dir
from ..housekeeping.update import has_update, UpdateChannel, get_latest_version_number
from ..housekeeping.version import get_version_info
from ..ui.generate_button import get_button_dict, ButtonStyles

logger = logging.getLogger(__name__)
has_checked_for_update = False
update_available = False


class StartScreen(Screens):
    """
    TODO: DOCS
    """

    def __init__(self, name=None):
        super().__init__(name)
        self.warning_label = None

        self.social_buttons = {}

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here."""
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", "-u", event.link_target])
            elif platform.system() == "Windows":
                os.system(f'start "" {event.link_target}')
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", event.link_target])
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)
            screens = {
                self.continue_button: "camp screen",
                self.switch_clan_button: "switch clan screen",
                self.new_clan_button: "make clan screen",
                self.settings_button: "settings screen",
            }
            if event.ui_element in screens:
                self.change_screen(screens[event.ui_element])
            elif event.ui_element == self.open_data_directory_button:
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", "-R", get_data_dir()])
                elif platform.system() == "Windows":
                    os.startfile(get_data_dir())  # pylint: disable=no-member
                elif platform.system() == "Linux":
                    subprocess.Popen(["xdg-open", get_data_dir()])
                return
            elif event.ui_element == self.closebtn:
                self.error_box.kill()
                self.error_label.kill()
                self.error_gethelp.kill()
                self.closebtn.kill()
                self.open_data_directory_button.kill()
                # game.switches['error_message'] = ''
                # game.switches['traceback'] = ''
            elif event.ui_element == self.update_button:
                UpdateAvailablePopup(game.switches["last_screen"])
            elif event.ui_element == self.quit:
                quit(savesettings=False, clearevents=False)
            elif event.ui_element == self.social_buttons["discord_button"]:
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", "-u", "https://discord.gg/clangen"])
                elif platform.system() == "Windows":
                    os.system(f"start \"\" {'https://discord.gg/clangen'}")
                elif platform.system() == "Linux":
                    subprocess.Popen(["xdg-open", "https://discord.gg/clangen"])
            elif event.ui_element == self.social_buttons["tumblr_button"]:
                if platform.system() == "Darwin":
                    subprocess.Popen(
                        ["open", "-u", "https://officialclangen.tumblr.com/"]
                    )
                elif platform.system() == "Windows":
                    os.system(f"start \"\" {'https://officialclangen.tumblr.com/'}")
                elif platform.system() == "Linux":
                    subprocess.Popen(
                        ["xdg-open", "https://officialclangen.tumblr.com/"]
                    )
            elif event.ui_element == self.social_buttons["twitter_button"]:
                if platform.system() == "Darwin":
                    subprocess.Popen(
                        ["open", "-u", "https://twitter.com/OfficialClangen"]
                    )
                elif platform.system() == "Windows":
                    os.system(f"start \"\" {'https://twitter.com/OfficialClangen'}")
                elif platform.system() == "Linux":
                    subprocess.Popen(
                        ["xdg-open", "https://twitter.com/OfficialClangen"]
                    )
        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if (
                event.key == pygame.K_RETURN or event.key == pygame.K_SPACE
            ) and self.continue_button.is_enabled:
                self.change_screen("camp screen")

    # def on_use(self):
    #     """
    #     TODO: DOCS
    #     """
    #     super().on_use()

    def exit_screen(self):
        """
        TODO: DOCS
        """
        # Button murder time.
        self.continue_button.kill()
        self.switch_clan_button.kill()
        self.new_clan_button.kill()
        self.settings_button.kill()
        self.error_label.kill()
        self.warning_label.kill()
        self.update_button.kill()
        self.quit.kill()
        self.closebtn.kill()
        for btn in self.social_buttons:
            self.social_buttons[btn].kill()

    def screen_switches(self):
        """
        TODO: DOCS
        """

        super().screen_switches()

        # start menu music if it isn't already playing
        # this is the only screen that has to check its own music, other screens handle that in the screen change
        music_manager.check_music("start screen")

        bg = pygame.image.load("resources/images/menu.png").convert()
        if game.settings["dark mode"]:
            bg.fill(
                game.config["theme"]["fullscreen_background"]["dark"]["mainmenu_tint"],
                bg.get_rect(),
                pygame.BLEND_MULT,
            )
        self.add_bgs(
            {"mainmenu_bg": bg},
        )
        self.set_bg("mainmenu_bg")

        # Make those unslightly menu button hide away
        self.hide_menu_buttons()
        Screens.show_mute_buttons()

        # Create buttons

        self.continue_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((70, 310), (200, 30))),
            "continue",
            image_dict=get_button_dict(ButtonStyles.MAINMENU, (200, 30)),
            object_id="@buttonstyles_mainmenu",
            manager=MANAGER,
        )
        self.switch_clan_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((70, 15), (200, 30))),
            "switch clan",
            image_dict=get_button_dict(ButtonStyles.MAINMENU, (200, 30)),
            object_id="@buttonstyles_mainmenu",
            manager=MANAGER,
            anchors={"top_target": self.continue_button},
        )
        self.new_clan_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((70, 15), (200, 30))),
            "new clan",
            image_dict=get_button_dict(ButtonStyles.MAINMENU, (200, 30)),
            object_id="@buttonstyles_mainmenu",
            manager=MANAGER,
            anchors={"top_target": self.switch_clan_button},
        )
        self.settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((70, 15), (200, 30))),
            "settings + info",
            image_dict=get_button_dict(ButtonStyles.MAINMENU, (200, 30)),
            object_id="@buttonstyles_mainmenu",
            manager=MANAGER,
            anchors={"top_target": self.new_clan_button},
        )
        self.quit = UISurfaceImageButton(
            ui_scale(pygame.Rect((70, 15), (200, 30))),
            "quit",
            image_dict=get_button_dict(ButtonStyles.MAINMENU, (200, 30)),
            object_id="@buttonstyles_mainmenu",
            manager=MANAGER,
            anchors={"top_target": self.settings_button},
        )

        self.social_buttons["twitter_button"] = UIImageButton(
            ui_scale(pygame.Rect((12, 647), (40, 40))),
            "",
            object_id="#twitter_button",
            manager=MANAGER,
            tool_tip_text="Check out our Twitter!",
        )
        self.social_buttons["tumblr_button"] = UIImageButton(
            ui_scale(pygame.Rect((5, 647), (40, 40))),
            "",
            object_id="#tumblr_button",
            manager=MANAGER,
            tool_tip_text="Check out our Tumblr!",
            anchors={"left_target": self.social_buttons["twitter_button"]},
        )

        self.social_buttons["discord_button"] = UIImageButton(
            ui_scale(pygame.Rect((7, 647), (40, 40))),
            "",
            object_id="#discord_button",
            manager=MANAGER,
            tool_tip_text="Join our Discord!",
            anchors={"left_target": self.social_buttons["tumblr_button"]},
        )
        errorimg = image_cache.load_image(
            "resources/images/errormsg.png"
        ).convert_alpha()

        self.error_box = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((130, 150), (590, 400))),
            pygame.transform.scale(errorimg, ui_scale_dimensions((590, 400))),
            manager=MANAGER,
        )

        self.error_box.disable()

        self.error_label = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((137, 185), (385, 360))),
            object_id="#text_box_22_horizleft",
            starting_height=1,
            manager=MANAGER,
        )

        self.error_gethelp = pygame_gui.elements.UITextBox(
            "Please join the Discord server and ask for technical support. "
            "We'll be happy to help! Please include the error message and the traceback below (if available). "
            '<br><a href="https://discord.gg/clangen">Discord</a>',  # pylint: disable=line-too-long
            ui_scale(pygame.Rect((527, 215), (175, 300))),
            object_id="#text_box_22_horizleft",
            starting_height=3,
            manager=MANAGER,
        )

        self.open_data_directory_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((527, 511), (178, 30))),
            "Open Data Directory",
            get_button_dict(ButtonStyles.SQUOVAL, (178, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            starting_height=2,  # Layer 2 and repositioned so hover affect works.
            tool_tip_text="Opens the data directory. "
            "This is where save files "
            "and logs are stored.",
        )

        self.closebtn = UIImageButton(
            ui_scale(pygame.Rect((693, 215), (22, 22))),
            "",
            starting_height=2,  # Hover affect works, and now allows it to be clicked more easily.
            object_id="#exit_window_button",
            manager=MANAGER,
        )

        self.error_box.hide()
        self.error_label.hide()
        self.error_gethelp.hide()
        self.open_data_directory_button.hide()
        self.closebtn.hide()

        self.update_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((577, 25), (153, 30))),
            "Update Available!",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.update_button.visible = 0

        try:
            global has_checked_for_update
            global update_available
            if (
                not get_version_info().is_source_build
                and not get_version_info().is_itch
                and get_version_info().upstream.lower()
                == "ClanGenOfficial/clangen".lower()
                and game.settings["check_for_updates"]
                and not has_checked_for_update
            ):
                if has_update(UpdateChannel(get_version_info().release_channel)):
                    update_available = True
                    show_popup = True
                    if os.path.exists(f"{get_cache_dir()}/suppress_update_popup"):
                        with open(
                            f"{get_cache_dir()}/suppress_update_popup", "r"
                        ) as read_file:
                            if read_file.readline() == get_latest_version_number():
                                show_popup = False

                    if show_popup:
                        UpdateAvailablePopup(
                            game.switches["last_screen"], show_checkbox=True
                        )

                has_checked_for_update = True

            if update_available:
                self.update_button.visible = 1
        except (RequestException, Timeout):
            logger.exception("Failed to check for update")
            has_checked_for_update = True

        if game.settings["show_changelog"]:
            show_changelog = True
            lastCommit = "0000000000000000000000000000000000000000"
            if os.path.exists(f"{get_cache_dir()}/changelog_popup_shown"):
                with open(f"{get_cache_dir()}/changelog_popup_shown") as read_file:
                    lastCommit = read_file.readline()
                    if lastCommit == get_version_info().version_number:
                        show_changelog = False

            if show_changelog:
                ChangelogPopup(game.switches["last_screen"])
                with open(
                    f"{get_cache_dir()}/changelog_popup_shown", "w"
                ) as write_file:
                    write_file.write(get_version_info().version_number)

        self.warning_label = pygame_gui.elements.UITextBox(
            "Warning: This game contains mild depictions of gore, canon-typical violence and animal abuse.",
            ui_scale(pygame.Rect((0, 600), (800, 40))),
            object_id=ObjectID("#text_box_30_horizcenter", "#dark"),
            manager=MANAGER,
            anchors={
                "left": "left",
                "right": "right",
            },
        )
        self.warning_label.text_horiz_alignment = "center"
        self.warning_label.rebuild()

        if game.clan is not None and game.switches["error_message"] == "":
            self.continue_button.enable()
        else:
            self.continue_button.disable()

        if len(game.switches["clan_list"]) > 1:
            self.switch_clan_button.enable()
        else:
            self.switch_clan_button.disable()

        if game.switches["error_message"]:
            error_text = (
                f"There was an error loading the game: {game.switches['error_message']}"
            )
            if game.switches["traceback"]:
                print("Traceback:")
                print(game.switches["traceback"])
                error_text += "<br><br>" + escape(
                    "".join(
                        traceback.format_exception(
                            game.switches["traceback"],
                            game.switches["traceback"],
                            game.switches["traceback"].__traceback__,
                        )
                    )
                )  # pylint: disable=line-too-long
            self.error_label.set_text(error_text)
            self.error_box.show()
            self.error_label.show()
            self.error_gethelp.show()
            self.open_data_directory_button.show()

            if get_version_info().is_sandboxed:
                self.open_data_directory_button.hide()

            self.closebtn.show()

        if game.clan is not None:
            key_copy = tuple(Cat.all_cats.keys())
            for x in key_copy:
                if x not in game.clan.clan_cats:
                    game.clan.remove_cat(x)

        # LOAD settings
        game.load_settings()
