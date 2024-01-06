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
        self.active_code = None
        self.original_focus_code = None
        self.focus_information = {}

    def handle_event(self, event):
        """
        Here are button presses / events are handled.
        """
        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('camp screen')
            if event.ui_element in self.focus_boxes.values():
                for code, value in self.focus_boxes.items():
                    if value == event.ui_element and value.object_ids[1] == "#unchecked_checkbox":
                        # un-switch the old checkbox
                        game.clan.switch_setting(self.active_code)
                        # switch the new checkbox
                        game.clan.switch_setting(code)
                        self.active_code = code
                        # only enable the save button if a focus switch is possible
                        if not game.clan.last_focus_change or\
                            game.clan.last_focus_change + game.config["focus"]["duration"] <= game.clan.age:
                            self.save_button.enable()
                        # deactivate save button if the focus didn't change
                        if self.active_code == self.original_focus_code and self.save_button.enable:
                            self.save_button.disable()
                        self.refresh_checkboxes()
                        self.create_side_info()
                        break

            elif event.ui_element == self.save_button:
                game.clan.last_focus_change = game.clan.age
                self.original_focus_code = self.active_code
                self.save_button.disable()
                self.refresh_checkboxes()
                self.create_top_info()

    def screen_switches(self):
        """
        Handle everything when it is switched to that screen.
        """
        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.save_button = UIImageButton(scale(pygame.Rect((150, 1250), (228, 60))), "", object_id="#save_button"
                                         , manager=MANAGER)
        self.save_button.disable()
        self.create_checkboxes()
        self.create_top_info()
        self.create_side_info()

    def exit_screen(self):
        """
        Handles to delete everything when the screen is switched to another one.
        """
        self.back_button.kill()
        self.save_button.kill()
        self.delete_checkboxes()
        for ele in self.focus_information:
            self.focus_information[ele].kill()
        self.focus_information = {}
        # if the focus wasn't changed, reset to the previous focus
        if self.original_focus_code != self.active_code:
            for code in settings_dict["clan_focus"].keys():
                if code == self.original_focus_code:
                    game.clan.clan_settings[code] = True
                else:
                    game.clan.clan_settings[code] = False

    def delete_checkboxes(self):
        """
        Delete all checkboxes and their associated text.
        """
        for checkbox in self.focus_boxes.values():
            checkbox.kill()
        self.focus_boxes = {}
        for text in self.focus.values():
            text.kill()
        self.focus = {}

    def create_checkboxes(self):
        """
        Create the checkboxes for the different focuses.
        """
        # create container for checkboxes
        self.focus["checkbox_container"] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((150, 520), (600, 800))), manager=MANAGER
        )

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
                self.active_code = code
            else:
                box_type = "#unchecked_checkbox"
            self.focus_boxes[code] = UIImageButton(scale(pygame.Rect((0, n * 70), (68, 68))),
                "",
                object_id=box_type,
                container=self.focus["checkbox_container"],
                tool_tip_text=desc[1])
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

    def create_top_info(self):
        """
        Create the top display text.
        """
        # delete previous created text if possible
        if "current_focus" in self.focus_information:
            self.focus_information["current_focus"].kill()
        if "time" in self.focus_information:
            self.focus_information["time"].kill()

        # create the new info text
        self.focus_information["current_focus"] = pygame_gui.elements.UITextBox(
            f"<b>Current Focus:</b> {self.active_code}<br>" + settings_dict["clan_focus"][self.active_code][1],
            scale(pygame.Rect((150, 145), (800, 80))),
            wrap_to_height=True,
            object_id=get_text_box_theme("#text_box_30"),
            manager=MANAGER
        )
        last_change_text = "unknown"
        next_change = "0 moons"
        if game.clan.last_focus_change:
            last_change_text = "moon " + str(game.clan.last_focus_change)
            moons = game.clan.last_focus_change + game.config["focus"]["duration"] - game.clan.age
            if moons == 1:
                next_change = f"{moons} moon"
            else:
                next_change = f"{moons} moons"
        self.focus_information["time"] = pygame_gui.elements.UITextBox(
            f"<b>Last Change:</b><br>{last_change_text} (next change in {next_change})",
            scale(pygame.Rect((150, 375), (600, 80))),
            wrap_to_height=True,
            object_id=get_text_box_theme("#text_box_30"),
            manager=MANAGER
        )

    def create_side_info(self):
        """
        Creates the side information text.
        """
        # delete previous created text if possible
        if "side_text" in self.focus_information:
            self.focus_information["side_text"].kill()
        
        # create the new info text
        self.focus_information["side_text"] = pygame_gui.elements.UITextBox(
            f"<b>Selected information:</b><br>" + settings_dict["clan_focus"][self.active_code][1],
            scale(pygame.Rect((750, 1000), (800, 80))),
            wrap_to_height=True,
            object_id=get_text_box_theme("#text_box_30"),
            manager=MANAGER
        )
