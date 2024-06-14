import pygame

from scripts.game_structure.game_essentials import game
from scripts.game_structure.windows import SaveCheck


class Keybinds:
    MAIN_SCREENS = ["events screen",
                    "camp screen",
                    "list screen",
                    "patrol screen"]

    BIND_LEFT = [pygame.K_a, pygame.K_LEFT]
    BIND_RIGHT = [pygame.K_d, pygame.K_RIGHT]
    BIND_UP = [pygame.K_w, pygame.K_UP]
    BIND_DOWN = [pygame.K_s, pygame.K_DOWN]

    def handle_navigation(self, screen, key):
        screen_name = screen.name

        # handle main navigation
        if screen_name in self.MAIN_SCREENS and key in self.BIND_LEFT + self.BIND_RIGHT:
            idx = self.MAIN_SCREENS.index(screen_name)
            try:
                if key in self.BIND_LEFT:
                    screen.change_screen(self.MAIN_SCREENS[idx - 1])
                elif key in self.BIND_RIGHT:
                    screen.change_screen(self.MAIN_SCREENS[idx + 1])
            except IndexError:
                return

        # handle "esc" button pressed
        if key == pygame.K_ESCAPE:
            if screen_name in ["events screen"]:
                # this should open the quit menu button
                SaveCheck(game.switches['cur_screen'], True, screen.menu_buttons["main_menu"])
