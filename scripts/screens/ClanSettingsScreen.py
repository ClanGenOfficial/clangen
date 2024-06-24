# pylint: disable=line-too-long
import logging
import os
import platform
import subprocess

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER

from scripts.game_structure.ui_elements import UIImageButton
from scripts.utility import (
    get_text_box_theme,
    scale,
)  # pylint: disable=redefined-builtin
from .Screens import Screens
from ..housekeeping.datadir import get_data_dir
from ..housekeeping.version import get_version_info

logger = logging.getLogger(__name__)

with open("resources/clansettings.json", "r", encoding="utf-8") as f:
    settings_dict = ujson.load(f)


class ClanSettingsScreen(Screens):
    """
    Screen handles all Clan-specific settings
    """

    text_size = {
        "0": "small",
        "1": "medium",
        "2": "big",
    }  # How text sizes will show up on the screen
    bool = {True: "Yes", False: "No", None: "None"}
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
            if event.ui_element == self.open_data_directory_button:
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", "-R", get_data_dir()])
                elif platform.system() == "Windows":
                    os.startfile(get_data_dir())  # pylint: disable=no-member
                elif platform.system() == "Linux":
                    try:
                        subprocess.Popen(["xdg-open", get_data_dir()])
                    except OSError:
                        logger.exception("Failed to call to xdg-open.")
                return
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
                    game.clan.switch_setting(key)
                    self.settings_changed = True
                    # self.update_save_button()

                    opens = {
                        "general": self.open_general_settings,
                        "relation": self.open_relation_settings,
                        "role": self.open_roles_settings,
                        "stats": self.open_clan_stats,
                    }

                    scroll_pos = None
                    if (
                        "container_general" in self.checkboxes_text
                        and self.checkboxes_text["container_general"].vert_scroll_bar
                    ):
                        scroll_pos = self.checkboxes_text[
                            "container_general"
                        ].vert_scroll_bar.start_percentage

                    if self.sub_menu in opens:
                        opens[self.sub_menu]()

                    if scroll_pos is not None:
                        self.checkboxes_text[
                            "container_general"
                        ].vert_scroll_bar.set_scroll_from_start_percentage(scroll_pos)

                    break

    def screen_switches(self):
        """
        TODO: DOCS
        """
        self.settings_changed = False
        self.show_menu_buttons()
        self.show_mute_buttons()
        self.set_disabled_menu_buttons(["stats"])

        self.general_settings_button = UIImageButton(
            scale(pygame.Rect((200, 280), (300, 60))),
            "",
            object_id="#general_settings_button",
            manager=MANAGER,
        )
        self.relation_settings_button = UIImageButton(
            scale(pygame.Rect((500, 280), (300, 60))),
            "",
            object_id="#relation_settings_button",
            manager=MANAGER,
        )
        self.role_settings_button = UIImageButton(
            scale(pygame.Rect((800, 280), (300, 60))),
            "",
            object_id="#role_settings_button",
            manager=MANAGER,
        )
        self.clan_stats_button = UIImageButton(
            scale(pygame.Rect((1100, 280), (300, 60))),
            "",
            object_id="#clan_stats_button",
            manager=MANAGER,
        )

        self.open_data_directory_button = UIImageButton(
            scale(pygame.Rect((50, 1290), (356, 60))),
            "",
            object_id="#open_data_directory_button",
            manager=MANAGER,
            tool_tip_text="Opens the data directory. "
            "This is where save files "
            "and logs are stored.",
        )

        if get_version_info().is_sandboxed:
            self.open_data_directory_button.hide()

        self.sub_menu = "general"
        self.open_general_settings()
        self.refresh_checkboxes()

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

    def open_general_settings(self):
        """Opens and draws general_settings"""
        self.enable_all_menu_buttons()
        self.general_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "general"

        self.checkboxes_text["container_general"] = (
            pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((0, 490), (1400, 600))),
                allow_scroll_x=False,
                manager=MANAGER,
            )
        )

        n = 0
        for code, desc in settings_dict["general"].items():
            x_val = 450
            if len(desc) == 4 and isinstance(desc[3], list):
                x_val += 50

            self.checkboxes_text[code] = pygame_gui.elements.UITextBox(
                desc[0],
                scale(pygame.Rect((x_val, n * 78), (1000, 78))),
                container=self.checkboxes_text["container_general"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
            )
            self.checkboxes_text[code].disable()
            n += 1

        self.checkboxes_text["container_general"].set_scrollable_area_dimensions(
            (1360 / 1600 * screen_x, (n * 78 + 80) / 1400 * screen_y)
        )

        self.checkboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "Change the general Clan-specific settings",
            scale(pygame.Rect((200, 370), (1200, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        # This is where the actual checkboxes are created. I don't like
        #   how this is separated from the text boxes, but I've spent too much time to rewrite it.
        #   It has to separated because the checkboxes must be updated when settings are changed.
        #   Fix if you want. - keyraven
        self.refresh_checkboxes()

    def open_roles_settings(self):
        """Opens and draws relation_settings"""
        self.enable_all_menu_buttons()
        self.role_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "role"

        self.checkboxes_text["container_role"] = (
            pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((0, 490), (1400, 600))),
                allow_scroll_x=False,
                manager=MANAGER,
            )
        )

        n = 0
        for code, desc in settings_dict["role"].items():
            # Handle nested
            x_val = 450
            if len(desc) == 4 and isinstance(desc[3], list):
                x_val += 50

            self.checkboxes_text[code] = pygame_gui.elements.UITextBox(
                desc[0],
                scale(pygame.Rect((x_val, n * 78), (1000, 78))),
                container=self.checkboxes_text["container_role"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
            )
            self.checkboxes_text[code].disable()
            n += 1

        self.checkboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "Change Clan-specific settings regarding cat roles",
            scale(pygame.Rect((200, 370), (1200, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        self.refresh_checkboxes()

    def open_relation_settings(self):
        """Opens and draws relation_settings"""
        self.enable_all_menu_buttons()
        self.relation_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "relation"

        self.checkboxes_text["container_relation"] = (
            pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((0, 490), (1400, 600))),
                allow_scroll_x=False,
                manager=MANAGER,
            )
        )

        n = 0
        for code, desc in settings_dict["relation"].items():
            x_val = 450
            if len(desc) == 4 and isinstance(desc[3], list):
                x_val += 50

            self.checkboxes_text[code] = pygame_gui.elements.UITextBox(
                desc[0],
                scale(pygame.Rect((x_val, n * 78), (1000, 78))),
                container=self.checkboxes_text["container_relation"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
            )
            self.checkboxes_text[code].disable()
            n += 1

        self.checkboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "Change Clan-specific settings regarding cat relationships",
            scale(pygame.Rect((200, 370), (1200, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        self.refresh_checkboxes()

    def open_clan_stats(self):
        self.enable_all_menu_buttons()
        self.clan_stats_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = "stats"

        # Stats determination time.
        faded_cats = len(game.clan.faded_ids)
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
                if cat.df:
                    df += 1
                elif cat.outside:
                    ur += 1
                else:
                    starclan += 1
                continue

            if cat.outside:
                cats_outside += 1
                continue

            living_cats += 1
            if cat.status == "medicine cat":
                med_cats += 1
            elif cat.status == "medicine cat apprentice":
                med_cat_apprentices += 1
            elif cat.status == "warrior":
                warriors += 1
            elif cat.status == "apprentice":
                warrior_apprentices += 1
            elif cat.status == "mediator apprentice":
                mediator_apprentices += 1
            elif cat.status == "mediator":
                mediators += 1
            elif cat.status == "elder":
                elders += 1
            elif cat.status in ("newborn", "kitten"):
                kits += 1

        text = (
            f"Living Clan Cats: {living_cats}\n"
            f"StarClan Cats: {starclan}\n"
            f"Dark Forest Cats: {df}\n"
            f"Unknown Residence Cats: {ur}\n"
            f"Medicine Cats: {med_cats}\n"
            f"Medicine Cat Apprentices: {med_cat_apprentices}\n"
            f"Warriors: {warriors}\n"
            f"Warrior Apprentices: {warrior_apprentices}\n"
            f"Mediators: {mediators}\n"
            f"Mediators Apprentices: {mediator_apprentices}\n"
            f"Elders: {elders}\n"
            f"Kittens and Newborns: {kits}\n"
            f"Faded Cats: {faded_cats}"
        )

        self.checkboxes_text["stat_box"] = pygame_gui.elements.UITextBox(
            text,
            scale(pygame.Rect((300, 400, 1060, 690))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
        )

    def refresh_checkboxes(self):
        """
        TODO: DOCS
        """
        # Kill the checkboxes. No mercy here.
        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}

        n = 0
        for code, desc in settings_dict[self.sub_menu].items():
            if game.clan.clan_settings[code]:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"

            # Handle nested
            disabled = False
            x_val = 340
            if len(desc) == 4 and isinstance(desc[3], list):
                x_val += 50
                disabled = (
                    game.clan.clan_settings.get(desc[3][0], not desc[3][1])
                    != desc[3][1]
                )

            self.checkboxes[code] = UIImageButton(
                scale(pygame.Rect((x_val, n * 78), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container_" + self.sub_menu],
                tool_tip_text=desc[1],
            )

            if disabled:
                self.checkboxes[code].disable()

            n += 1

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
