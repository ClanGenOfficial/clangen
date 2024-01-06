import pygame
import pygame_gui
import ujson

from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER

from scripts.utility import scale, get_text_box_theme

with open('resources/clansettings.json', 'r', encoding='utf-8') as f:
    settings_dict = ujson.load(f)

class WarriorDenScreen(Screens):
    """
    The screen to change the focus of the Clan, which gives bonuses.
    """

    def __init__(self, name=None):
        super().__init__(name)
        self.focus_boxes = {}
        self.focus = {}
        self.back_button = None
        self.save_button = None
        self.original_focus_code = None
        self.focus_changed = False

    def handle_event(self, event):
        """
        Here are button presses / events are handled.
        """
        active_key = None
        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('camp screen')
            if event.ui_element in self.focus_boxes.values():
                for key, value in self.focus_boxes.items():
                    if value == event.ui_element and value.object_ids[1] == "#unchecked_checkbox":
                        game.clan.switch_setting(key)
                        active_key = key
                        self.save_button.enable()
                        self.refresh_checkboxes()
                        break
                # un-switch all other keys
                for key, value in self.focus_boxes.items():
                    if active_key and key != active_key and value.object_ids[1] == "#checked_checkbox":
                        game.clan.switch_setting(key)
                        self.refresh_checkboxes()
                        break

            elif event.ui_element == self.save_button:
                game.clan.last_focus_change = game.clan.age
                self.focus_changed = True
                self.save_button.disable()
                self.refresh_checkboxes()

    def screen_switches(self):
        """
        Handle everything when it is switched to that screen.
        """
        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.save_button = UIImageButton(scale(pygame.Rect((150, 1200), (228, 60))), "", object_id="#save_button"
                                         , manager=MANAGER)
        self.save_button.disable()
        self.create_checkboxes()

    def exit_screen(self):
        """
        Handles to delete everything when the screen is switched to another one.
        """
        self.back_button.kill()
        self.save_button.kill()
        self.delete_checkboxes()
        # if the focus wasn't changed, reset to the previous focus
        if not self.focus_changed:
            for code in settings_dict["clan_focus"].keys():
                if code == self.original_focus_code:
                    game.clan.clan_settings[code] = True
                else:
                    game.clan.clan_settings[code] = False

    def delete_checkboxes(self):
        for checkbox in self.focus_boxes.values():
            checkbox.kill()
        self.focus_boxes = {}
        for text in self.focus.values():
            text.kill()
        self.focus = {}

    def create_checkboxes(self):
        # create container for checkboxes
        self.focus["checkbox_container"] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((150, 450), (600, 800))), manager=MANAGER
        )

        enable = False
        if not game.clan.last_focus_change or game.clan.last_focus_change + game.config["focus"]["duration"] <= game.clan.age:
            enable = True

        n = 0
        for code, desc in settings_dict["clan_focus"].items():
            # create text next to checkboxes
            x_val = 110
            self.focus[code] = pygame_gui.elements.UITextBox(
                desc[0],
                scale(pygame.Rect((x_val, n * 70), (300, 90))),
                container=self.focus["checkbox_container"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER)

            # create the checkboxes itself
            if game.clan.clan_settings[code]:
                box_type = "#checked_checkbox"
                self.original_focus_code = code
            else:
                box_type = "#unchecked_checkbox"
            self.focus_boxes[code] = UIImageButton(scale(pygame.Rect((0, n * 70), (68, 68))),
                "",
                object_id=box_type,
                container=self.focus["checkbox_container"],
                tool_tip_text=desc[1])

            if not enable:
                self.focus_boxes[code].disable()

            n += 1

        # create scrollbar
        self.focus["checkbox_container"].set_scrollable_area_dimensions(
            (450 / 1600 * screen_x, (n * 72 + x_val) / 1600 * screen_y)
        )

    def refresh_checkboxes(self):
        """
        Handles the checkboxes, which focus is selected.
        """
        # Kill the checkboxes. No mercy here.
        for checkbox in self.focus_boxes.values():
            checkbox.kill()
        self.focus_boxes = {}

        enable = False
        if not game.clan.last_focus_change or game.clan.last_focus_change + game.config["focus"]["duration"] <= game.clan.age:
            enable = True

        n = 0
        for code, desc in settings_dict["clan_focus"].items():
            if game.clan.clan_settings[code]:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"

            self.focus_boxes[code] = UIImageButton(scale(pygame.Rect((0, n * 70), (68, 68))),
                "",
                object_id=box_type,
                container=self.focus["checkbox_container"],
                tool_tip_text=desc[1])
            n += 1

            if not enable:
                self.focus_boxes[code].disable()
