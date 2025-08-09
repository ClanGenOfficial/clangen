from random import choice
from re import sub

import i18n
import pygame
import pygame_gui

from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIImageButton,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale, process_text, update_sprite


class KillCat(GameWindow):
    """This window allows the user to kill the selected cat"""

    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((300, 200), (450, 200))),
            window_display_title="Kill Cat",
            object_id="#kill_cat_window",
        )

        self.the_cat = cat
        self.take_all = False

        cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
        self.heading = pygame_gui.elements.UITextBox(
            "windows.kill_cat_method",
            ui_scale(pygame.Rect((10, 10), (300, -1))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

        self.one_life_check = UIImageButton(
            ui_scale(pygame.Rect((25, 150), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            tool_tip_text=process_text(
                i18n.t("windows.all_lives_leader_tooltip"),
                cat_dict,
            ),
            manager=MANAGER,
            container=self,
        )
        self.all_lives_check = UIImageButton(
            ui_scale(pygame.Rect((25, 150), (34, 34))),
            "",
            object_id="@checked_checkbox",
            tool_tip_text=process_text(
                i18n.t("windows.all_lives_leader_tooltip"),
                cat_dict,
            ),
            manager=MANAGER,
            container=self,
        )

        if self.the_cat.status.is_leader:
            self.done_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((347, 152), (77, 30))),
                "buttons.done_lower",
                get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                container=self,
            )

            self.prompt = process_text(i18n.t("windows.death_prompt"), cat_dict)
            self.initial = process_text(i18n.t("windows.default_death"), cat_dict)

            self.all_lives_check.hide()
            self.life_text = pygame_gui.elements.UITextBox(
                "windows.all_lives_leader",
                ui_scale(pygame.Rect((60, 147), (130, -1))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
            self.beginning_prompt = pygame_gui.elements.UITextBox(
                self.prompt,
                ui_scale(pygame.Rect((25, 30), (450, 40))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(
                ui_scale(pygame.Rect((25, 65), (400, 75))),
                initial_text=self.initial,
                object_id="text_entry_line",
                manager=MANAGER,
                container=self,
            )

        elif self.the_cat.history.get_death_or_scars(death=True):
            # This should only occur for retired leaders.

            self.prompt = process_text(i18n.t("windows.death_prompt"), cat_dict)
            self.initial = process_text(
                i18n.t("windows.default_leader_death"), cat_dict
            )
            self.all_lives_check.hide()
            self.one_life_check.hide()

            self.beginning_prompt = pygame_gui.elements.UITextBox(
                self.prompt,
                ui_scale(pygame.Rect((25, 30), (200, -1))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(
                ui_scale(pygame.Rect((25, 65), (400, 75))),
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
        else:
            self.initial = i18n.t("windows.default_death_pronounless")
            self.prompt = None
            self.all_lives_check.hide()
            self.one_life_check.hide()

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

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                death_message = sub(
                    r"[^A-Za-z0-9<->/.()*'&#!?,| _]+",
                    "",
                    self.death_entry_box.get_text(),
                )
                if self.the_cat.status.is_leader:
                    if death_message.startswith("was"):
                        death_message = death_message.replace(
                            "was", "{VERB/m_c/were/was}", 1
                        )
                    elif death_message.startswith("were"):
                        death_message = death_message.replace(
                            "were", "{VERB/m_c/were/was}", 1
                        )

                    if self.take_all:
                        game.clan.leader_lives = 0
                    else:
                        game.clan.leader_lives -= 1

                self.the_cat.die()
                self.the_cat.history.add_death(death_message)
                update_sprite(self.the_cat)
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
                self.kill()
            elif event.ui_element == self.all_lives_check:
                self.take_all = False
                self.all_lives_check.hide()
                self.one_life_check.show()
            elif event.ui_element == self.one_life_check:
                self.take_all = True
                self.all_lives_check.show()
                self.one_life_check.hide()
            elif event.ui_element == self.back_button:
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()

        return super().process_event(event)
