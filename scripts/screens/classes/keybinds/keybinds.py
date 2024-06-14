import pygame
import pygame_gui

from scripts.game_structure.game_essentials import game
from scripts.screens.Screens import Screens


class Keybinds:
    MAIN_SCREENS = ["events screen",
                    "camp screen",
                    "list screen",
                    "patrol screen"]

    CAMP_CHILDREN = ["leader den screen", "med den screen", "clearing screen", "warrior den screen"]

    PROFILE_CHILDREN = ["choose mate screen", "choose mentor screen", "choose adoptive parent screen",
                        "relationship screen", "see kits screen", "mediation screen", "change gender screen"]

    BIND_LEFT = [pygame.K_a, pygame.K_LEFT]
    BIND_RIGHT = [pygame.K_d, pygame.K_RIGHT]
    BIND_UP = [pygame.K_w, pygame.K_UP]
    BIND_DOWN = [pygame.K_s, pygame.K_DOWN]
    BIND_NUMBERS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]

    NUMBER_SCREENS = ["events screen", "camp screen", "list screen", "patrol screen", "leader den screen",
                      "med den screen", "clearing screen", "warrior den screen"]

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

        # handle jumping to screens in the top bar
        elif key in self.BIND_NUMBERS:
            if key == pygame.K_1:
                screen.change_screen(self.NUMBER_SCREENS[0])
            elif key == pygame.K_2:
                screen.change_screen(self.NUMBER_SCREENS[1])
            elif key == pygame.K_3:
                screen.change_screen(self.NUMBER_SCREENS[2])
            elif key == pygame.K_4:
                screen.change_screen(self.NUMBER_SCREENS[3])
            elif key == pygame.K_5:
                screen.change_screen(self.NUMBER_SCREENS[4])
            elif key == pygame.K_6:
                screen.change_screen(self.NUMBER_SCREENS[5])
            elif key == pygame.K_7:
                screen.change_screen(self.NUMBER_SCREENS[6])
            elif key == pygame.K_8:
                screen.change_screen(self.NUMBER_SCREENS[7])
        # handle "esc" button pressed
        elif key == pygame.K_ESCAPE:
            if screen_name == "events screen":
                # open the quit menu button (by pretending the user clicked it lmao)
                event = pygame.event.Event(pygame_gui.UI_BUTTON_START_PRESS,
                                           ui_element=screen.menu_buttons["main_menu"])
                pygame.event.post(event)
            elif screen_name in self.MAIN_SCREENS:
                # send us to the Shadow Realm (the events screen)
                screen.change_screen("events screen")
            elif screen_name in self.CAMP_CHILDREN:
                screen.change_screen("camp screen")
            elif screen_name in self.PROFILE_CHILDREN:
                screen.change_screen("profile screen")
