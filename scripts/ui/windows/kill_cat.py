from random import choice
from re import sub

import i18n
import pygame
import pygame_gui

from scripts.config import get_config
from scripts.events_module.consequences import check_stolen_vitality
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.cat.sprites.display_sprites import update_sprite
from scripts.events_module.text_adjust import process_text
from scripts.ui.scale import ui_scale


class KillCat(GameWindow):
    """This window allows the user to kill the selected cat"""

    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((300, 200), (450, 200))),
        )

        self.the_cat = cat
        self.result_text: str = ""

        cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
        self.heading = pygame_gui.elements.UITextBox(
            "windows.kill_cat_method",
            ui_scale(pygame.Rect((10, 10), (300, -1))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

        self.all_lives_check = UICheckbox(
            (25, 150),
            tool_tip_text=process_text(
                i18n.t("windows.all_lives_leader_tooltip"),
                cat_dict,
            ),
            manager=MANAGER,
            container=self,
        )
        self.all_lives_check.check()

        self.initial = i18n.t("windows.default_death_pronounless")
        self.prompt = None

        if not cat.status.is_leader:
            self.all_lives_check.hide()

        self.death_entry_box = pygame_gui.elements.UITextEntryBox(
            ui_scale(pygame.Rect((25, 55), (400, 75))),
            initial_text=self.initial,
            object_id="text_entry_line",
            manager=MANAGER,
            container=self,
        )

        self.done_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((186, 152), (77, 30))),
            "buttons.done_lower",
            get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
        )

    def show_result(self):
        self.heading.kill()
        self.death_entry_box.kill()
        self.all_lives_check.kill()
        self.done_button.kill()

        self.death_entry_box = pygame_gui.elements.UITextBox(
            self.result_text,
            ui_scale(pygame.Rect((0, 20), (400, -1))),
            object_id="#text_box_30_horizcenter",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                death_message = sub(
                    r"[^A-Za-z0-9<>/.()*'&#!?,| _-]+",
                    "",
                    self.death_entry_box.get_text(),
                )
                if not death_message:
                    death_message = self.initial
                if self.the_cat.status.is_leader:
                    if self.take_all:
                        lives_lost = game.clan.leader_lives

                    else:
                        lives_lost = 1

                    game.clan.leader_lives -= lives_lost
                    for i in range(lives_lost):
                        self.the_cat.history.add_death(death_message)

                    if extra_text := check_stolen_vitality(self.the_cat, lives_lost):
                        self.result_text = extra_text

                if self.the_cat.status.alive_in_player_clan:
                    self.the_cat.die()
                else:
                    self.the_cat.die(grief_allowed=False)

                if not self.the_cat.status.is_leader:  # leader already got history
                    self.the_cat.history.add_death(death_message)
                update_sprite(self.the_cat)
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
                if not self.result_text:
                    self.kill()
                else:
                    self.show_result()
            elif event.ui_element == self.all_lives_check:
                if self.all_lives_check.checked:
                    self.all_lives_check.uncheck()
                else:
                    self.all_lives_check.check()
            elif event.ui_element == self.back_button:
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()

        return super().process_event(event)

    @property
    def take_all(self):
        return self.all_lives_check.checked
