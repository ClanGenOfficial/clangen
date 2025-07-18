# pylint: disable=line-too-long
import logging
import os
import platform
import subprocess
from math import floor

import i18n
import pygame
import pygame_gui
import ujson

from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.game_structure.game.settings import (
    game_settings_save,
    game_setting_toggle,
    game_setting_get,
    game_setting_set,
)

# please don't do this. we have to.
import scripts.game_structure.game.settings.settings as all_settings
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISurfaceImageButton,
    UIImageHorizontalSlider,
    UIModifiedScrollingContainer,
)
from scripts.housekeeping.datadir import open_data_dir
from scripts.utility import get_text_box_theme, ui_scale, ui_scale_dimensions
from .Screens import Screens
from ..game_structure import constants
from ..game_structure.audio import music_manager, sound_manager
from ..game_structure.screen_settings import (
    MANAGER,
    set_display_mode,
)
from ..housekeeping.version import get_version_info
from ..ui.generate_button import get_button_dict, ButtonStyles

logger = logging.getLogger(__name__)
with open("resources/gamesettings.json", "r", encoding="utf-8") as f:
    settings_dict = ujson.load(f)


class SettingsScreen(Screens):
    """
    TODO: DOCS
    """

    sub_menu = "general"

    # This is set to the current settings when the screen is opened.
    # All edits are made directly to game.settings, however, when you
    #  leave the screen,game.settings will be reverted based on this variable
    #   However, if settings are saved, edits will also be made to this variable.
    settings_at_open = {}

    # Have the settings been changed since the page was open or since settings were saved?
    settings_changed = False

    # Contains the checkboxes
    checkboxes = {}
    # Contains the text for the checkboxes.
    checkboxes_text = {}

    # Contains the volume elements
    volume_elements = {}

    # contains the tooltips for contributors
    tooltip = {}

    info_text = {
        "welcome": "",
        "ogs": "",
        "contribs": [],
        "thanks": "",
        "music": "",
        "licensing": "",
    }
    tooltip_text = []
    info_text_index = "welcome"
    contributors_start = 0
    with open("resources/credits_text.json", "r", encoding="utf-8") as f:
        credits_text = ujson.load(f)
    for string in credits_text["text"]:
        if string == "{credits}":
            info_text_index = "ogs"
        elif string == "{contrib}":
            # removing the previous newline
            info_text[info_text_index] = info_text[info_text_index][:-2]
            info_text_index = "contribs"
            for i, contributor in enumerate(credits_text["contrib"]):
                if contributor == "<SENIORS>":
                    continue
                elif contributor == "<CONTRIBUTORS>":
                    contributors_start = (
                        i - 1
                    )  # to account for the seniors and contributors tags we skip

                    continue
                info_text[info_text_index].append(contributor)
                tooltip_text.append(credits_text["contrib"][contributor])
            info_text_index = "thanks"
        elif string == "{music}":
            info_text_index = "music"
        elif string == "{licensing}":
            info_text_index = "licensing"
        else:
            info_text[info_text_index] += string + "\n"

    def __init__(self, name="settings_screen"):
        super().__init__(name)
        self.prev_setting = None
        self.toggled_theme = "dark" if game_setting_get("dark mode") else "light"

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if hasattr(event, "ui_element"):
                if event.ui_element == self.volume_elements["music_volume_slider"]:
                    self.update_music_volume_indicator()
                    music_manager.change_volume(event.value)
                    self.settings_changed = True
                    self.update_save_button()
                elif event.ui_element == self.volume_elements["sound_volume_slider"]:
                    self.update_sound_volume_indicator()
                    sound_manager.change_volume(event.value)
                    self.settings_changed = True
                    self.update_save_button()

        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", "-u", event.link_target])
            elif platform.system() == "Windows":
                os.system(f'start "" {event.link_target}')
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", event.link_target])
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.main_menu_button:
                self.change_screen("start screen")
                return
            if event.ui_element == self.fullscreen_toggle:
                game_setting_toggle("fullscreen")
                self.save_settings()
                game_settings_save(self)
                set_display_mode(
                    fullscreen=game_setting_get("fullscreen"), source_screen=self
                )
            elif event.ui_element == self.open_data_directory_button:
                open_data_dir()
                return
            elif event.ui_element == self.save_settings_button:
                self.save_settings()
                game_settings_save(self)
                self.settings_changed = False
                self.update_save_button()
                return
            elif event.ui_element == self.general_settings_button:
                self.open_general_settings()
                return
            elif event.ui_element == self.audio_settings_button:
                self.open_audio_settings()
            elif event.ui_element == self.info_button:
                self.open_info_screen()
                return
            elif event.ui_element == self.language_button:
                self.open_lang_settings()
            if self.sub_menu in ("general", "relation", "language"):
                self.handle_checkbox_events(event)

        elif event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            if event.key == pygame.K_ESCAPE:
                self.change_screen("start screen")
            elif event.key == pygame.K_RIGHT:
                if self.sub_menu == "general":
                    self.open_info_screen()
                elif self.sub_menu == "info":
                    self.open_lang_settings()
            elif event.key == pygame.K_LEFT:
                if self.sub_menu == "info":
                    self.open_general_settings()
                elif self.sub_menu == "language":
                    self.open_info_screen()

    def handle_checkbox_events(self, event):
        """
        TODO: DOCS
        """
        if event.ui_element in self.checkboxes.values():
            for key, value in self.checkboxes.items():
                if value == event.ui_element:
                    if self.sub_menu == "language":
                        self.checkboxes[MANAGER.get_locale()].enable()
                        MANAGER.set_locale(key)
                        i18n.config.set("locale", key)
                        self.checkboxes[key].disable()
                        game_setting_set("language", key)
                    else:
                        game_setting_toggle(key)
                        value.change_object_id(
                            "@checked_checkbox"
                            if game_setting_get(key)
                            else "@unchecked_checkbox"
                        )
                    self.settings_changed = True
                    self.update_save_button()

                    if (
                        self.sub_menu == "general"
                        and event.ui_element is self.checkboxes["dark mode"]
                    ):
                        # has to be done manually since we haven't saved the new mode yet.
                        self.toggled_theme = (
                            "dark"
                            if "@checked_checkbox"
                            in self.checkboxes["dark mode"].get_object_ids()
                            else "light"
                        )
                        self.set_bg("default", "mainmenu_bg")
                        self.open_general_settings()

                    if (
                        self.sub_menu == "general"
                        and event.ui_element is self.checkboxes["discord"]
                    ):
                        if game_setting_get("discord"):
                            print("Starting Discord RPC")
                            game.rpc = _DiscordRPC("1076277970060185701", daemon=True)
                            game.rpc.start()
                            game.rpc.start_rpc.set()
                        else:
                            print("Stopping Discord RPC")
                            game.rpc.close()

                    break

    def screen_switches(self):
        """
        TODO: DOCS
        """
        super().screen_switches()
        self.show_mute_buttons()
        self.settings_changed = False

        self.general_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((100, 100), (150, 30))),
            "screens.settings.general",
            get_button_dict(ButtonStyles.MENU_LEFT, (150, 30)),
            object_id="@buttonstyles_menu_left",
            manager=MANAGER,
        )
        self.audio_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 100), (150, 30))),
            "screens.settings.audio",
            get_button_dict(ButtonStyles.MENU_MIDDLE, (150, 30)),
            object_id="@buttonstyles_menu_middle",
            manager=MANAGER,
            anchors={"left_target": self.general_settings_button},
        )
        self.info_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 100), (150, 30))),
            "screens.settings.info",
            get_button_dict(ButtonStyles.MENU_MIDDLE, (150, 30)),
            object_id="@buttonstyles_menu_middle",
            manager=MANAGER,
            anchors={"left_target": self.audio_settings_button},
        )
        self.language_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 100), (150, 30))),
            "screens.settings.language",
            get_button_dict(ButtonStyles.MENU_RIGHT, (150, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            anchors={"left_target": self.info_button},
        )
        self.save_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 550), (150, 30))),
            "buttons.save_settings",
            get_button_dict(ButtonStyles.SQUOVAL, (150, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.fullscreen_toggle = UIImageButton(
            ui_scale(pygame.Rect((617, 25), (158, 36))),
            "buttons.toggle_fullscreen",
            object_id="#toggle_fullscreen_button",
            manager=MANAGER,
            tool_tip_text=(
                "buttons.toggle_fullscreen_windowed"
                if game_setting_get("fullscreen")
                else "buttons.toggle_fullscreen_fullscreen"
            ),
            tool_tip_text_kwargs={
                "screentext": (
                    "windowed" if game_setting_get("fullscreen") else "fullscreen"
                )
            },
        )

        self.open_data_directory_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 645), (178, 30))),
            "buttons.open_data_directory",
            get_button_dict(ButtonStyles.SQUOVAL, (178, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            tool_tip_text="buttons.open_data_directory_tooltip",
        )

        if get_version_info().is_sandboxed:
            self.open_data_directory_button.hide()

        self.update_save_button()
        self.main_menu_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (152, 30))),
            "buttons.main_menu",
            get_button_dict(ButtonStyles.SQUOVAL, (152, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_squoval",
            starting_height=1,
        )
        self.sub_menu = "general"
        self.open_general_settings()

        self.set_bg("default", "mainmenu_bg")

        self.settings_at_open = (
            all_settings.settings
        )  # please don't do this anywhere else.

        self.refresh_checkboxes()

    def update_save_button(self):
        """
        Updates the disabled state the save button
        """
        if not self.settings_changed:
            self.save_settings_button.disable()
        else:
            self.save_settings_button.enable()

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.clear_sub_settings_buttons_and_text()
        self.general_settings_button.kill()
        del self.general_settings_button
        self.audio_settings_button.kill()
        del self.audio_settings_button
        self.info_button.kill()
        del self.info_button
        self.language_button.kill()
        del self.language_button
        self.save_settings_button.kill()
        del self.save_settings_button
        self.main_menu_button.kill()
        del self.main_menu_button
        self.fullscreen_toggle.kill()
        del self.fullscreen_toggle
        self.open_data_directory_button.kill()
        del self.open_data_directory_button

        self.settings_at_open = all_settings.settings
        self.toggled_theme = "dark" if game_setting_get("dark mode") else "light"

    def save_settings(self):
        """Saves the settings, ensuring that they will be retained when the screen changes."""
        self.settings_at_open = all_settings.settings.copy()
        MANAGER.set_active_cursor(
            constants.CUSTOM_CURSOR
            if game_setting_get("custom cursor")
            else constants.DEFAULT_CURSOR
        )

    def open_general_settings(self):
        """Opens and draws general_settings"""
        self.enable_all_menu_buttons()
        self.general_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "general"
        self.save_settings_button.show()

        self.checkboxes_text["container_general"] = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((0, 220), (700, 300))),
            allow_scroll_x=False,
            allow_scroll_y=True,
            manager=MANAGER,
        )

        for i, (code, desc) in enumerate(settings_dict["general"].items()):
            self.checkboxes_text[code] = pygame_gui.elements.UITextBox(
                f"settings.{code}",
                ui_scale(pygame.Rect((225, 34 if i < 0 else 0), (500, 34))),
                container=self.checkboxes_text["container_general"],
                object_id=get_text_box_theme("#text_box_30_horizleft_vertcenter"),
                manager=MANAGER,
                anchors=(
                    {"top_target": self.checkboxes_text[list(self.checkboxes_text)[-1]]}
                    if i > 0
                    else None
                ),
            )
            self.checkboxes_text[code].disable()

        self.checkboxes_text["container_general"].set_scrollable_area_dimensions(
            ui_scale_dimensions((680, (len(settings_dict["general"].keys()) * 39 + 40)))
        )

        self.checkboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "screens.settings.general_info",
            ui_scale(pygame.Rect((100, 160), (600, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        # This is where the actual checkboxes are created. I don't like
        #   how this is separated from the text boxes, but I've spent too much time to rewrite it.
        #   It has to separated because the checkboxes must be updated when settings are changed.
        #   Fix if you want. - keyraven
        self.refresh_checkboxes()

    def open_audio_settings(self):
        self.enable_all_menu_buttons()
        self.audio_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "audio"
        self.save_settings_button.show()

        self.volume_elements["audio_settings_info"] = pygame_gui.elements.UITextBox(
            "screens.settings.audio_info",
            ui_scale(pygame.Rect((0, 160), (600, 50))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.volume_elements["music_volume_text"] = pygame_gui.elements.UITextBox(
            "screens.settings.music_volume",
            ui_scale(pygame.Rect((175, 250), (200, 30))),
            object_id=get_text_box_theme("#text_box_30"),
            manager=MANAGER,
        )

        self.volume_elements["music_volume_slider"] = UIImageHorizontalSlider(
            ui_scale(pygame.Rect((0, 250), (200, 30))),
            start_value=int(music_manager.volume * 100),
            value_range=(0, 100),
            click_increment=1,
            object_id="horizontal_slider",
            manager=MANAGER,
            anchors={"left_target": self.volume_elements["music_volume_text"]},
        )

        self.volume_elements["music_volume_indicator"] = pygame_gui.elements.UITextBox(
            f"{self.volume_elements['music_volume_slider'].get_current_value()}",
            ui_scale(pygame.Rect((-8, 250), (50, 30))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={"left_target": self.volume_elements["music_volume_slider"]},
        )

        self.volume_elements["sound_volume_text"] = pygame_gui.elements.UITextBox(
            "screens.settings.sfx_volume",
            ui_scale(pygame.Rect((175, 15), (200, 30))),
            object_id=get_text_box_theme("#text_box_30"),
            manager=MANAGER,
            anchors={"top_target": self.volume_elements["music_volume_text"]},
        )

        self.volume_elements["sound_volume_slider"] = UIImageHorizontalSlider(
            ui_scale(pygame.Rect((0, 15), (200, 30))),
            start_value=int(sound_manager.volume * 100),
            value_range=(0, 100),
            click_increment=1,
            object_id="horizontal_slider",
            manager=MANAGER,
            anchors={
                "top_target": self.volume_elements["music_volume_slider"],
                "left_target": self.volume_elements["sound_volume_text"],
            },
        )

        self.volume_elements["sound_volume_indicator"] = pygame_gui.elements.UITextBox(
            f"{self.volume_elements['sound_volume_slider'].get_current_value()}",
            ui_scale(pygame.Rect((-8, 15), (50, 30))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={
                "top_target": self.volume_elements["music_volume_indicator"],
                "left_target": self.volume_elements["sound_volume_slider"],
            },
        )

    def update_music_volume_indicator(self):
        self.volume_elements["music_volume_indicator"].set_text(
            f"{self.volume_elements['music_volume_slider'].get_current_value()}"
        )

    def update_sound_volume_indicator(self):
        self.volume_elements["sound_volume_indicator"].set_text(
            f"{self.volume_elements['sound_volume_slider'].get_current_value()}"
        )

    def open_info_screen(self):
        """Open's info screen"""
        self.enable_all_menu_buttons()
        self.info_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "info"
        self.save_settings_button.hide()

        self.checkboxes_text["info_container"] = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((0, 150), (600, 500))),
            allow_scroll_x=False,
            allow_scroll_y=True,
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.checkboxes_text["info_text_box"] = pygame_gui.elements.UITextBox(
            self.info_text["welcome"].strip("\n"),
            ui_scale(pygame.Rect((0, 0), (575, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )
        self.checkboxes_text["info_text_credits"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (400, 40))),
            "Credits",
            {"normal": get_button_dict(ButtonStyles.ROUNDED_RECT, (400, 40))["normal"]},
            object_id="@buttonstyles_icon",
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_box"],
            },
        )
        self.checkboxes_text["info_text_original"] = pygame_gui.elements.UITextBox(
            self.info_text["ogs"].strip("\n"),
            ui_scale(pygame.Rect((0, 0), (575, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_credits"],
            },
        )

        self.checkboxes_text["info_text_seniors"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (400, 30))),
            "Current + Former Senior Developers",
            {"normal": get_button_dict(ButtonStyles.ROUNDED_RECT, (300, 30))["normal"]},
            object_id="@buttonstyles_rounded_rect",
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_original"],
            },
        )
        self.checkboxes_text["info_text_seniors"].disable()

        self.checkboxes_text["info_text_box"].disable()
        rows = [-200, 0, 200]
        contributors_block = False
        contributors_index = 0
        final_row_seniors = self.contributors_start % 3
        final_row_contribs = (len(self.tooltip_text) - self.contributors_start) % 3
        for i, tooltip in enumerate(self.tooltip_text):
            # determine position
            if contributors_block:
                position = (
                    (
                        0
                        if final_row_contribs == 1 and i == len(self.tooltip_text) - 1
                        else rows[contributors_index % 3]
                    ),
                    # y-axis
                    (
                        10
                        if contributors_index
                        < 3  # first rows have a bit of space below the header
                        else 0
                    ),
                )
            else:
                position = (
                    (
                        0
                        if final_row_seniors == 1 and (i == self.contributors_start - 1)
                        else rows[i % 3]
                    ),
                    (
                        10
                        if i < 3  # first rows have a bit of space below the header
                        else 0
                    ),
                )
            self.tooltip[f"tip{i}"] = UIImageButton(
                ui_scale(
                    pygame.Rect(
                        position,
                        (200, 26),
                    )
                ),
                self.info_text["contribs"][i],
                object_id=(
                    "#blank_button_dark"
                    if self.toggled_theme == "dark"
                    else "#blank_button"
                ),
                container=self.checkboxes_text["info_container"],
                manager=MANAGER,
                tool_tip_text=tooltip if tooltip else None,
                starting_height=2,
                sound_id=None,
                anchors={
                    "centerx": "centerx",
                    "top_target": (
                        self.checkboxes_text["info_text_seniors"]  # seniors first row
                        if i < 3
                        else (
                            self.tooltip[
                                f"tip{(floor(i / 3) * 3) - 1}"
                            ]  # seniors other rows
                            if not contributors_block
                            # contributor block
                            else (
                                self.checkboxes_text[
                                    "info_text_contributors"
                                ]  # contributors first row
                                if contributors_index < 3
                                else self.tooltip[f"tip{i - 3}"]
                            )
                        )
                    ),  # contributors other rows
                },
            )

            if contributors_block:
                contributors_index += 1
            elif i == self.contributors_start - 1:
                self.checkboxes_text["info_text_contributors"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, 20), (300, 30))),
                    "Contributors",
                    {
                        "normal": get_button_dict(ButtonStyles.ROUNDED_RECT, (300, 30))[
                            "normal"
                        ]
                    },
                    object_id="@buttonstyles_rounded_rect",
                    container=self.checkboxes_text["info_container"],
                    manager=MANAGER,
                    anchors={
                        "centerx": "centerx",
                        "top_target": self.tooltip[f"tip{self.contributors_start - 1}"],
                    },
                )
                contributors_block = True

        self.checkboxes_text["info_text_thanks"] = pygame_gui.elements.UITextBox(
            self.info_text["thanks"].strip(),
            ui_scale(pygame.Rect((0, 10), (575, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.tooltip[list(self.tooltip.keys())[-1]],
            },
        )
        self.checkboxes_text["info_text_thanks"].disable()

        self.checkboxes_text["info_text_music_title"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (300, 30))),
            "Music",
            {"normal": get_button_dict(ButtonStyles.ROUNDED_RECT, (300, 30))["normal"]},
            object_id="@buttonstyles_rounded_rect",
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_thanks"],
            },
        )

        self.checkboxes_text["info_text_music"] = pygame_gui.elements.UITextBox(
            self.info_text["music"].strip(),
            ui_scale(pygame.Rect((0, 10), (575, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_music_title"],
            },
        )

        self.checkboxes_text["info_text_licensing_title"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (300, 30))),
            "Licensing",
            {"normal": get_button_dict(ButtonStyles.ROUNDED_RECT, (300, 30))["normal"]},
            object_id="@buttonstyles_rounded_rect",
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_music"],
            },
        )

        self.checkboxes_text["info_text_licensing"] = pygame_gui.elements.UITextBox(
            self.info_text["licensing"],
            ui_scale(pygame.Rect((0, 10), (575, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text["info_container"],
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.checkboxes_text["info_text_licensing_title"],
            },
        )

    def open_lang_settings(self):
        """Open Language Settings"""
        self.enable_all_menu_buttons()
        self.language_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "language"
        self.save_settings_button.show()

        self.checkboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "screens.settings.language_info",
            ui_scale(pygame.Rect((100, 160), (600, 50))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        self.refresh_checkboxes()

    def refresh_checkboxes(self):
        """
        TODO: DOCS
        """
        # Kill the checkboxes. No mercy here.
        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}

        # CHECKBOXES (ehhh) FOR LANGUAGES
        if self.sub_menu == "language":
            self.checkboxes["en"] = UIImageButton(
                ui_scale(pygame.Rect((310, 200), (180, 51))),
                "",
                object_id="#english_lang_button",
                manager=MANAGER,
            )
            self.checkboxes["es"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((310, 0), (180, 37))),
                "español",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (180, 37)),
                object_id="@buttonstyles_ladder_middle",
                manager=MANAGER,
                anchors={"top_target": self.checkboxes["en"]},
            )
            self.checkboxes["de"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((310, 0), (180, 37))),
                "deutsch",
                get_button_dict(ButtonStyles.LADDER_BOTTOM, (180, 37)),
                object_id="@buttonstyles_ladder_bottom",
                manager=MANAGER,
                anchors={"top_target": self.checkboxes["es"]},
            )
            language = MANAGER.get_locale()
            if language == "en":  # English
                self.checkboxes["en"].disable()
            elif language == "es":  # Spanish
                self.checkboxes["es"].disable()
            elif language == "de":  # German
                self.checkboxes["de"].disable()

        else:
            for i, (code, desc) in enumerate(settings_dict[self.sub_menu].items()):
                if game_setting_get(code):
                    box_type = "@checked_checkbox"
                else:
                    box_type = "@unchecked_checkbox"
                self.checkboxes[code] = UIImageButton(
                    ui_scale(pygame.Rect((170, 34 if i < 0 else 0), (34, 34))),
                    "",
                    object_id=box_type,
                    container=self.checkboxes_text["container_" + self.sub_menu],
                    tool_tip_text=f"settings.{code}_tooltip",
                    anchors=(
                        {"top_target": self.checkboxes_text[list(self.checkboxes)[-1]]}
                        if i > 0
                        else None
                    ),
                )

    def clear_sub_settings_buttons_and_text(self):
        """
        TODO: DOCS
        """
        if "info_container" in self.checkboxes_text:
            self.checkboxes_text["info_container"].kill()

        if "container_general" in self.checkboxes_text:
            self.checkboxes_text["container_general"].kill()

        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}
        for text in self.checkboxes_text.values():
            text.kill()
        self.checkboxes_text = {}
        for item in self.volume_elements.values():
            item.kill()
        self.volume_elements = {}

    def enable_all_menu_buttons(self):
        """
        TODO: DOCS
        """
        self.general_settings_button.enable()
        self.info_button.enable()
        self.language_button.enable()
        self.audio_settings_button.enable()

    def on_use(self):
        """
        TODO: DOCS
        """
        # super().on_use()
        self.show_bg(theme=self.toggled_theme)
