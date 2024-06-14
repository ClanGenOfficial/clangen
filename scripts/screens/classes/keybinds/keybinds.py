import pygame
import pygame_gui

from scripts.game_structure.game_essentials import game
from scripts.game_structure.windows import SaveCheck
from scripts.screens.Screens import Screens


class Keybinds:
    MAIN_SCREENS = ["events screen",
                    "camp screen",
                    "list screen",
                    "patrol screen"]

    BIND_LEFT = [pygame.K_a, pygame.K_LEFT]
    BIND_RIGHT = [pygame.K_d, pygame.K_RIGHT]
    BIND_UP = [pygame.K_w, pygame.K_UP]
    BIND_DOWN = [pygame.K_s, pygame.K_DOWN]

    def handle_navigation(self, screen: Screens, key):
        # only run this if keybinds are enabled :)
        if not game.settings['keybinds']:
            return
        screen_name = screen.name

        # handle moving through screens in the top bar
        if screen_name in self.MAIN_SCREENS and key in self.BIND_LEFT + self.BIND_RIGHT:
            idx = self.MAIN_SCREENS.index(screen_name)
            try:
                if key in self.BIND_LEFT and idx > 0:
                    screen.change_screen(self.MAIN_SCREENS[idx - 1])
                elif key in self.BIND_RIGHT and idx < len(self.MAIN_SCREENS):
                    screen.change_screen(self.MAIN_SCREENS[idx + 1])
            except IndexError:
                return

        # handle "esc" button pressed
        if key == pygame.K_ESCAPE:
            if screen_name in ["events screen"]:
                pass
                # open the quit menu button
                event = pygame.event.Event(pygame_gui.UI_BUTTON_START_PRESS,
                                           ui_element=screen.menu_buttons["main_menu"])
                pygame.event.post(event)
            elif screen_name in self.MAIN_SCREENS:
                # send us to the Shadow Realm (the events screen)
                screen.change_screen("events screen")
