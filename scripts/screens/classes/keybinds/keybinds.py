import pygame

MAIN_SCREENS = ["events screen",
                "camp screen",
                "list screen",
                "patrol screen"]

BIND_LEFT = [pygame.K_a, pygame.K_LEFT]
BIND_RIGHT = [pygame.K_d, pygame.K_RIGHT]
BIND_UP = [pygame.K_w, pygame.K_UP]
BIND_DOWN = [pygame.K_s, pygame.K_DOWN]


def handle_keypress(screen, key):
    screen_name = screen.name

    # handle main navigation
    if screen_name in MAIN_SCREENS and key in BIND_LEFT + BIND_RIGHT:
        idx = MAIN_SCREENS.index(screen_name)
        try:
            if key in BIND_LEFT:
                screen.change_screen(MAIN_SCREENS[idx - 1])
            elif key in BIND_RIGHT:
                screen.change_screen(MAIN_SCREENS[idx + 1])
        except IndexError:
            return

    # handle "esc" button pressed
