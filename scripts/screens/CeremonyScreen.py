#!/usr/bin/env python3
# -*- coding: ascii -*-
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, screen_x, MANAGER
from scripts.game_structure.ui_elements import UIImageButton
from scripts.utility import get_text_box_theme
from scripts.utility import scale
from .Screens import Screens
from scripts.utility import get_text_box_theme
from scripts.cat.cats import Cat
import pygame_gui
from scripts.game_structure.ui_elements import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, MANAGER
from ..cat.history import History


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
        self.hide_menu_buttons()
        self.show_mute_buttons()

        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        if self.the_cat.status == 'leader':
            self.header = pygame_gui.elements.UITextBox(str(self.the_cat.name) + '\'s Leadership Ceremony',
                                                        scale(pygame.Rect((200, 180), (1200, -1))),
                                                        object_id=get_text_box_theme(), manager=MANAGER)
        else:
            self.header = pygame_gui.elements.UITextBox(str(self.the_cat.name) + ' has no ceremonies to view.',
                                                        scale(pygame.Rect((200, 180), (1200, -1))),
                                                        object_id=get_text_box_theme(), manager=MANAGER)
        if self.the_cat.status == 'leader' and not self.the_cat.dead:
            self.life_text = History.get_lead_ceremony(self.the_cat)

        else:
            self.life_text = ""

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((100, 300), (1400, 1000))),
                                                                         allow_scroll_x=False,
                                                                         manager=MANAGER)
        self.text = pygame_gui.elements.UITextBox(self.life_text,
                                                  scale(pygame.Rect((0, 0), (1100, -1))),
                                                  object_id=get_text_box_theme("#text_box_30_horizleft"),
                                                  container=self.scroll_container, manager=MANAGER)
        self.text.disable()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)
        self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, self.text.rect[3]))

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
        pass

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
            else:
                self.mute_button_pressed(event)


        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        return
