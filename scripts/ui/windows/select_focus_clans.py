import pygame
import pygame_gui

from scripts.game_structure import game
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale

from scripts.ui.elements.checkbox import UICheckbox
from scripts.game_structure.screen_settings import MANAGER


class SelectFocusClansWindow(GameWindow):
    """This window allows the user to select the clans to be sabotaged, aided or raided in the focus setting."""

    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((250, 120), (300, 260))),
        )
        self.save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((80, 210), (139, 30))),
            "windows.change_focus",
            get_button_dict(ButtonStyles.SQUOVAL, (139, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )
        self.save_button.disable()

        self.checkboxes = {}
        self.refresh_checkboxes()

        # Text
        self.texts = {}
        self.texts["prompt"] = pygame_gui.elements.UITextBox(
            "windows.focus_prompt",
            ui_scale(pygame.Rect((0, 5), (300, 35))),
            object_id="#text_box_30_horizcenter",
            container=self,
        )

        prev_element = None
        for clan in game.clan.all_other_clans:
            self.texts[clan.name] = pygame_gui.elements.UITextBox(
                clan.name,
                ui_scale(pygame.Rect(107, 0 if prev_element else 35, -1, 35)),
                object_id="#text_box_30_horizleft_pad_0_8",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.texts[clan.name]

    def refresh_checkboxes(self):
        for x in self.checkboxes.values():
            x.kill()
        self.checkboxes = {}

        prev_element = None
        for clan in game.clan.all_other_clans:
            self.checkboxes[clan.name] = UICheckbox(
                position=(75, 0 if prev_element else 35),
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
                manager=MANAGER,
                check=clan.name in game.clan.clans_in_focus,
            )
            prev_element = self.checkboxes[clan.name]

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.clan.clans_in_focus = []
                game.all_screens[GameScreen.WARRIOR_DEN].exit_screen()
                game.all_screens[GameScreen.WARRIOR_DEN].screen_switches()
            if event.ui_element == self.save_button:
                game.all_screens[GameScreen.WARRIOR_DEN].save_focus()
                game.all_screens[GameScreen.WARRIOR_DEN].exit_screen()
                game.all_screens[GameScreen.WARRIOR_DEN].screen_switches()
                self.kill()
            if event.ui_element in self.checkboxes.values():
                for clan_name, value in self.checkboxes.items():
                    if value == event.ui_element:
                        if self.checkboxes[clan_name].checked:
                            game.clan.clans_in_focus.remove(clan_name)
                            self.checkboxes[clan_name].uncheck()
                        else:
                            game.clan.clans_in_focus.append(clan_name)
                            self.checkboxes[clan_name].check()
                        self.refresh_checkboxes()
                if len(game.clan.clans_in_focus) < 1 and self.save_button.is_enabled:
                    self.save_button.disable()
                if (
                    len(game.clan.clans_in_focus) >= 1
                    and not self.save_button.is_enabled
                ):
                    self.save_button.enable()

        return super().process_event(event)
