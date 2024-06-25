import pygame
import pygame_gui

from scripts.game_structure.game_essentials import game
from scripts.screens.Screens import Screens
from scripts.screens.classes.keybinds.customkeybinds import CustomKeybinds

MAIN_SCREENS = ["events screen",
                "camp screen",
                "list screen",
                "patrol screen"]

CAMP_CHILDREN = ["leader den screen", "med den screen", "clearing screen", "warrior den screen"]

PROFILE_CHILDREN = ["choose mate screen", "choose mentor screen", "choose adoptive parent screen",
                    "relationship screen", "see kits screen", "mediation screen", "change gender screen"]

NUMBER_SCREENS = ["events screen", "camp screen", "list screen", "patrol screen", "leader den screen",
                  "med den screen", "clearing screen", "warrior den screen"]


class Keybinds:

    @staticmethod
    def handle_navigation(screen: Screens, key):
        # only run this if keybinds are enabled :)
        if not game.settings['keybinds']:
            return
        screen_name = screen.name

        # handle moving through screens in the top bar
        if screen_name in MAIN_SCREENS and key in CustomKeybinds.BIND_LEFT + CustomKeybinds.BIND_RIGHT:
            idx = MAIN_SCREENS.index(screen_name)
            try:
                if key in CustomKeybinds.BIND_LEFT and idx > 0:
                    screen.change_screen(MAIN_SCREENS[idx - 1])
                elif key in CustomKeybinds.BIND_RIGHT and idx < len(MAIN_SCREENS):
                    screen.change_screen(MAIN_SCREENS[idx + 1])
            except IndexError:
                return

        # handle jumping to screens in the top bar
        elif key in CustomKeybinds.BIND_NUMBERS:
            if key == pygame.K_1:
                screen.change_screen(NUMBER_SCREENS[0])
            elif key == pygame.K_2:
                screen.change_screen(NUMBER_SCREENS[1])
            elif key == pygame.K_3:
                screen.change_screen(NUMBER_SCREENS[2])
            elif key == pygame.K_4:
                screen.change_screen(NUMBER_SCREENS[3])
            elif key == pygame.K_5:
                screen.change_screen(NUMBER_SCREENS[4])
            elif key == pygame.K_6:
                screen.change_screen(NUMBER_SCREENS[5])
            elif key == pygame.K_7:
                screen.change_screen(NUMBER_SCREENS[6])
            elif key == pygame.K_8:
                screen.change_screen(NUMBER_SCREENS[7])
        # handle "esc" button pressed
        elif key == pygame.K_ESCAPE:
            if screen_name == "events screen":
                # open the quit menu button (by pretending the user clicked it lmao)
                event = pygame.event.Event(pygame_gui.UI_BUTTON_START_PRESS,
                                           ui_element=screen.menu_buttons["main_menu"])
                pygame.event.post(event)
            elif screen_name in MAIN_SCREENS:
                # send us to the Shadow Realm (the events screen)
                screen.change_screen("events screen")
            elif screen_name in CAMP_CHILDREN:
                screen.change_screen("camp screen")
            elif screen_name in PROFILE_CHILDREN:
                screen.change_screen("profile screen")
