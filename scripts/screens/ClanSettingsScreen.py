# pylint: disable=line-too-long
import logging
import os
import platform
import subprocess
from typing import Dict

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISurfaceImageButton,
    UIModifiedScrollingContainer,
    UICheckbox,
)
from scripts.housekeeping.datadir import open_data_dir
from ..ui.theme import get_text_box_theme
from ..ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset
from .Screens import Screens
from .enums import GameScreen
from ..cat import save_load
from ..clan_package.settings import get_clan_setting, switch_clan_setting
from ..cat.enums import CatRank, CatGroup
from ..game_structure.screen_settings import MANAGER, toggle_fullscreen
from ..game_structure.constants import DISPLAY_SETTINGS
from ..housekeeping.version import get_version_info
from ..ui.generate_button import get_button_dict, ButtonStyles

logger = logging.getLogger(__name__)

settings_dict = DISPLAY_SETTINGS["clan"]


class ClanSettingsScreen(Screens):
    """
    Screen handles all Clan-specific settings
    """

    sub_menu = "general"

    # This is set to the current settings when the screen is opened.
    # All edits are made directly to settings, however, when you
    #  leave the screen, settings will be reverted based on this variable
    #   However, if settings are saved, edits will also be made to this variable.
    settings_at_open = {}

    # Have the settings been changed since the page was open or since settings were saved?
    settings_changed = False

    # Contains the checkboxes
    checkboxes = {}
    # Contains the text for the checkboxes.
    checkboxes_text = {}

    def __init__(self, name):
        super().__init__(name)
        self.opens = {
            "general": self.open_general_settings,
            "relation": self.open_relation_settings,
            "role": self.open_roles_settings,
            "stats": self.open_clan_stats,
        }

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", "-u", event.link_target])
            elif platform.system() == "Windows":
                os.system(f'start "" {event.link_target}')
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", event.link_target])
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.fullscreen_toggle:
                toggle_fullscreen(source_screen=self)
            elif event.ui_element == self.open_data_directory_button:
                open_data_dir()
                return
            elif event.ui_element == self.game_settings_button:
                self.change_screen(GameScreen.SETTINGS)
            elif event.ui_element == self.relation_settings_button:
                self.open_relation_settings()
                return
            elif event.ui_element == self.general_settings_button:
                self.open_general_settings()
                return
            elif event.ui_element == self.role_settings_button:
                self.open_roles_settings()
                return
            elif event.ui_element == self.clan_stats_button:
                self.open_clan_stats()
                return
            self.handle_checkbox_events(event)
            self.menu_button_pressed(event)
            self.mute_button_pressed(event)

    def handle_checkbox_events(self, event):
        """
        TODO: DOCS
        """
        if event.ui_element in self.checkboxes.values():
            for key, value in self.checkboxes.items():
                if value == event.ui_element:
                    switch_clan_setting(key)
                    if value.checked:
                        value.uncheck()
                    else:
                        value.check()
                    self.settings_changed = True
                    # self.update_save_button()

                    scroll_pos = None
                    if (
                        "container_general" in self.checkboxes_text
                        and self.checkboxes_text["container_general"].vert_scroll_bar
                    ):
                        scroll_pos = self.checkboxes_text[
                            "container_general"
                        ].vert_scroll_bar.start_percentage

                    if self.sub_menu in self.opens:
                        self.opens[self.sub_menu]()

                    if scroll_pos is not None:
                        self.checkboxes_text[
                            "container_general"
                        ].vert_scroll_bar.set_scroll_from_start_percentage(scroll_pos)

                    break

    def screen_switches(self):
        """
        TODO: DOCS
        """
        super().screen_switches()
        self.settings_changed = False
        self.show_menu_buttons()
        self.show_mute_buttons()
        self.set_disabled_menu_buttons(["clan_settings"])

        self.general_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((100, 140), (150, 30))),
            "screens.clan_settings.general",
            get_button_dict(ButtonStyles.MENU_LEFT, (150, 30)),
            object_id="@buttonstyles_menu_left",
            manager=MANAGER,
        )
        self.relation_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 140), (150, 30))),
            "screens.clan_settings.relation",
            get_button_dict(ButtonStyles.MENU_MIDDLE, (150, 30)),
            object_id="@buttonstyles_menu_middle",
            manager=MANAGER,
            anchors={"left_target": self.general_settings_button},
        )
        self.role_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 140), (150, 30))),
            "screens.clan_settings.role",
            get_button_dict(ButtonStyles.MENU_MIDDLE, (150, 30)),
            object_id="@buttonstyles_menu_middle",
            manager=MANAGER,
            anchors={"left_target": self.relation_settings_button},
        )
        self.clan_stats_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 140), (150, 30))),
            "screens.clan_settings.stats",
            get_button_dict(ButtonStyles.MENU_RIGHT, (150, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            anchors={"left_target": self.role_settings_button},
        )

        self.game_settings_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 600), (175, 30))),
            "screens.clan_settings.full_settings",
            get_button_dict(ButtonStyles.SQUOVAL, (175, 30)),
            tool_tip_text="screens.clan_settings.full_settings_info",
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.open_data_directory_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 645), (178, 30))),
            "buttons.open_data_directory",
            get_button_dict(ButtonStyles.SQUOVAL, (178, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            tool_tip_text="buttons.open_data_directory_tooltip",
        )

        rect = ui_scale(pygame.Rect((0, 0), (158, 36)))
        rect.bottomright = ui_scale_offset((-5, -25))
        self.fullscreen_toggle = UIImageButton(
            rect,
            "buttons.toggle_fullscreen",
            object_id="#toggle_fullscreen_button",
            manager=MANAGER,
            starting_height=2,
            tool_tip_text=(
                "buttons.toggle_fullscreen_windowed"
                if game_setting_get("fullscreen")
                else "buttons.toggle_fullscreen_fullscreen"
            ),
            anchors={
                "bottom": "bottom",
                "right": "right",
                "right_target": Screens.menu_buttons["mute_button"],
            },
        )
        del rect

        if get_version_info().is_sandboxed:
            self.open_data_directory_button.hide()

        self.sub_menu = "general"
        self.open_general_settings()

    def display_change_save(self) -> Dict:
        variable_dict = super().display_change_save()
        variable_dict["sub_menu"] = self.sub_menu
        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        for key, value in variable_dict.items():
            try:
                setattr(self, key, value)
            except KeyError:
                continue

        self.opens[self.sub_menu]()

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.clear_sub_settings_buttons_and_text()
        self.general_settings_button.kill()
        del self.general_settings_button
        self.relation_settings_button.kill()
        del self.relation_settings_button
        self.role_settings_button.kill()
        del self.role_settings_button
        self.open_data_directory_button.kill()
        del self.open_data_directory_button
        self.clan_stats_button.kill()
        del self.clan_stats_button
        self.hide_menu_buttons()
        self.fullscreen_toggle.kill()
        del self.fullscreen_toggle
        self.game_settings_button.kill()
        del self.game_settings_button

    def open_general_settings(self):
        """Opens and draws general_settings"""
        self.enable_all_menu_buttons()
        self.general_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "general"

        self.refresh_checkboxes()

    def open_roles_settings(self):
        """Opens and draws relation_settings"""
        self.enable_all_menu_buttons()
        self.role_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "role"

        self.refresh_checkboxes()

    def open_relation_settings(self):
        """Opens and draws relation_settings"""
        self.enable_all_menu_buttons()
        self.relation_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "relation"

        self.refresh_checkboxes()

    def open_clan_stats(self):
        self.enable_all_menu_buttons()
        self.clan_stats_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "stats"

        # Stats determination time.
        faded_cats = len(save_load.get_faded_ids())
        living_cats = 0
        med_cats = 0
        warriors = 0
        warrior_apprentices = 0
        med_cat_apprentices = 0
        mediator_apprentices = 0
        mediators = 0
        elders = 0
        kits = 0
        cats_outside = 0
        starclan = 0
        df = 0
        ur = 0
        for cat in Cat.all_cats_list:
            if cat.faded:
                faded_cats += 1
                continue

            if cat.dead:
                if cat.status.group == CatGroup.STARCLAN:
                    starclan += 1
                elif cat.status.group == CatGroup.DARK_FOREST:
                    df += 1
                else:
                    ur += 1
                continue

            if cat.status.is_outsider:
                cats_outside += 1
                continue

            living_cats += 1
            if cat.status.rank == CatRank.MEDICINE_CAT:
                med_cats += 1
            elif cat.status.rank == CatRank.MEDICINE_APPRENTICE:
                med_cat_apprentices += 1
            elif cat.status.rank == CatRank.WARRIOR:
                warriors += 1
            elif cat.status.rank == CatRank.APPRENTICE:
                warrior_apprentices += 1
            elif cat.status.rank == CatRank.MEDIATOR_APPRENTICE:
                mediator_apprentices += 1
            elif cat.status.rank == CatRank.MEDIATOR:
                mediators += 1
            elif cat.status.rank == CatRank.ELDER:
                elders += 1
            elif cat.status.rank.is_baby():
                kits += 1

        self.checkboxes_text["stat_box"] = pygame_gui.elements.UITextBox(
            "screens.clan_settings.stats_text",
            ui_scale(pygame.Rect((150, 200), (530, 345))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            text_kwargs={
                "living": str(living_cats),
                "starclan": str(starclan),
                "darkforest": str(df),
                "unknownresidence": str(ur),
                "medcats": str(med_cats),
                "medcatapps": str(med_cat_apprentices),
                "warriors": str(warriors),
                "apps": str(warrior_apprentices),
                "mediators": str(mediators),
                "mediatorapps": str(mediator_apprentices),
                "elders": str(elders),
                "kits": str(kits),
                "faded": str(faded_cats),
            },
        )

    def refresh_checkboxes(self):
        """
        TODO: DOCS
        """

        container_name = f"container_{self.sub_menu}"
        self.checkboxes_text[container_name] = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((0, 245), (700, 300))),
            allow_scroll_x=False,
            allow_scroll_y=True,
            manager=MANAGER,
        )

        nests = settings_dict["nests"].get(self.sub_menu)

        n = 0
        for name, _ in settings_dict[self.sub_menu].items():
            disabled = False
            text_x_val = 225
            check_x_val = 170
            if nests and nests.get(name):
                nested_settings = nests.get(name)
                text_x_val += 25
                check_x_val += 25
                disabled = not all(
                    required == get_clan_setting(setting, default=not required)
                    for setting, required in nested_settings.items()
                )

            self.checkboxes_text[name] = pygame_gui.elements.UITextBox(
                f"settings.{name}",
                ui_scale(pygame.Rect((text_x_val, n * 39), (500, 39))),
                container=self.checkboxes_text[container_name],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
            )
            self.checkboxes_text[name].disable()

            self.checkboxes[name] = UICheckbox(
                position=(check_x_val, n * 39),
                container=self.checkboxes_text[container_name],
                tool_tip_text=f"settings.{name}_tooltip",
                check=get_clan_setting(name),
                manager=MANAGER,
            )

            if disabled:
                self.checkboxes[name].disable()

            n += 1

        self.checkboxes_text["instr"] = pygame_gui.elements.UITextBox(
            f"screens.clan_settings.{self.sub_menu}_info",
            ui_scale(pygame.Rect((100, 185), (600, 50))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

    def clear_sub_settings_buttons_and_text(self):
        """
        TODO: DOCS
        """
        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}
        for text in self.checkboxes_text.values():
            text.kill()
        self.checkboxes_text = {}

    def enable_all_menu_buttons(self):
        """
        TODO: DOCS
        """
        self.general_settings_button.enable()
        self.relation_settings_button.enable()
        self.role_settings_button.enable()
        self.clan_stats_button.enable()

    def on_use(self):
        """
        TODO: DOCS
        """
        super().on_use()
