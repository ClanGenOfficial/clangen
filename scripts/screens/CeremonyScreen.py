#!/usr/bin/env python3
# -*- coding: ascii -*-
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import UISurfaceImageButton
from scripts.utility import get_text_box_theme
from scripts.utility import ui_scale
from .Screens import Screens
from ..cat.history import History
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_button import ButtonStyles, get_button_dict
from ..ui.get_arrow import get_arrow


class CeremonyScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.text = None
        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None

    def screen_switches(self):
        super().screen_switches()
        self.hide_menu_buttons()
        self.show_mute_buttons()

        self.the_cat = Cat.all_cats.get(game.switches["cat"])
        if self.the_cat.status.is_leader():
            self.header = pygame_gui.elements.UITextBox(
                str(self.the_cat.name) + "'s Leadership Ceremony",
                ui_scale(pygame.Rect((100, 90), (600, -1))),
                object_id=get_text_box_theme(),
                manager=MANAGER,
            )
        else:
            self.header = pygame_gui.elements.UITextBox(
                str(self.the_cat.name) + " has no ceremonies to view.",
                ui_scale(pygame.Rect((100, 90), (600, -1))),
                object_id=get_text_box_theme(),
                manager=MANAGER,
            )
        if self.the_cat.status.is_leader() and not self.the_cat.dead:
            self.life_text = History.get_lead_ceremony(self.the_cat)

        else:
            self.life_text = ""

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((50, 150), (700, 500))),
            allow_scroll_x=False,
            manager=MANAGER,
        )
        self.text = pygame_gui.elements.UITextBox(
            self.life_text,
            ui_scale(pygame.Rect((0, 0), (650, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            container=self.scroll_container,
            manager=MANAGER,
        )
        self.text.disable()
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.scroll_container.set_scrollable_area_dimensions(
            (
                self.scroll_container.get_relative_rect()[2],
                self.text.rect[3],
            )
        )

    def exit_screen(self):
        self.header.kill()
        del self.header
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button

    def on_use(self):
        super().on_use()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            else:
                self.mute_button_pressed(event)

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if event.key == pygame.K_ESCAPE:
                self.change_screen("profile screen")
        return
