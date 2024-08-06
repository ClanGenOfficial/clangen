from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.screens.Screens import Screens

from math import floor
from typing import Optional, Tuple

import pygame
import pygame_gui

from scripts.game_structure.ui_manager import UIManager
from scripts.ui.generate_screen_scale_jsons import generate_screen_scale


offset = (0, 0)
screen_x = 800
screen_y = 700
screen_scale = 1
game_screen_size = (800, 700)
MANAGER: Optional[pygame_gui.UIManager] = None
screen = None
curr_variable_dict = {}


def set_display_mode(
    fullscreen=None,
    source_screen: Optional["Screens"] = None,
    show_confirm_dialog=True,
    ingame_switch=True,
):
    global offset
    global screen_x
    global screen_y
    global screen_scale
    global game_screen_size
    global screen
    global MANAGER
    global curr_variable_dict

    old_offset = offset
    old_scale = screen_scale
    mouse_pos = pygame.mouse.get_pos()

    from scripts.game_structure.game_essentials import game

    if fullscreen is None:
        fullscreen = game.settings["fullscreen"]

    if source_screen is not None:
        curr_variable_dict = source_screen.display_change_save()

    if fullscreen:
        display_size = pygame.display.get_desktop_sizes()[0]  # the primary monitor
        # display_size = [3840, 2160]

        x = display_size[0] // 200
        y = display_size[1] // 175

        # this means screen scales in multiples of 200 x 175 which has a reasonable tradeoff for crunch
        screen_scale = min(x, y) / 4
        screen_x = 800 * screen_scale
        screen_y = 700 * screen_scale

        screen = pygame.display.set_mode(
            display_size,
            pygame.FULLSCREEN,
        )
        offset = (
            floor((display_size[0] - screen_x) / 2),
            floor((display_size[1] - screen_y) / 2),
        )
        game_screen_size = (screen_x, screen_y)
    else:
        offset = (0, 0)
        screen_x = 800
        screen_y = 700
        screen_scale = 1
        game_screen_size = (800, 700)
        screen = pygame.display.set_mode((screen_x, screen_y))
    game_screen_size = (screen_x, screen_y)

    if source_screen is None:
        MANAGER = load_manager((screen_x, screen_y), offset, scale=screen_scale)

    # generate new theme
    origin = "resources/theme/master_screen_scale.json"
    theme_location = "resources/theme/generated/screen_scale.json"
    generate_screen_scale(origin, theme_location, screen_scale)
    MANAGER.get_theme().load_theme(theme_location)

    if source_screen is not None:
        from scripts.screens.all_screens import AllScreens
        import scripts.screens.screens_core.screens_core
        import scripts.debug_menu

        game.save_settings(currentscreen=source_screen)
        source_screen.exit_screen()

        if fullscreen:
            mouse_pos = (mouse_pos[0] * screen_scale) + offset[0], mouse_pos[
                1
            ] * screen_scale + offset[1]
        else:
            mouse_pos = (
                (mouse_pos[0] - old_offset[0]) / old_scale,
                (mouse_pos[1] - old_offset[1]) / old_scale,
            )

        MANAGER.clear_and_reset()
        MANAGER.set_window_resolution(game_screen_size)
        MANAGER.set_offset(offset)
        pygame.mouse.set_pos(mouse_pos)

        AllScreens.rebuild_all_screens()

        scripts.screens.screens_core.screens_core.rebuild_core()
        scripts.debug_menu.debugmode.rebuild_console()

        screen_name = source_screen.name.replace(" ", "_")
        new_screen: "Screens" = getattr(AllScreens, screen_name)
        new_screen.screen_switches()
        if ingame_switch:
            new_screen.display_change_load(curr_variable_dict)
    if curr_variable_dict is not None and show_confirm_dialog:
        from scripts.screens.all_screens import AllScreens

        new_screen: "Screens" = getattr(
            AllScreens, game.switches["cur_screen"].replace(" ", "_")
        )
        new_screen.display_change_load(curr_variable_dict)

    # preloading the associated fonts
    if not MANAGER.ui_theme.get_font_dictionary().check_font_preloaded(
        f"notosans_bold_aa_{floor(11 * screen_scale)}"
    ):
        MANAGER.preload_fonts(
            [
                {
                    "name": "notosans",
                    "point_size": floor(11 * screen_scale),
                    "style": "bold",
                },
                {
                    "name": "notosans",
                    "point_size": floor(13 * screen_scale),
                    "style": "bold",
                },
                {
                    "name": "notosans",
                    "point_size": floor(15 * screen_scale),
                    "style": "bold",
                },
                {
                    "name": "notosans",
                    "point_size": floor(13 * screen_scale),
                    "style": "italic",
                },
                {
                    "name": "notosans",
                    "point_size": floor(15 * screen_scale),
                    "style": "italic",
                },
                {
                    "name": "notosans",
                    "point_size": floor(17 * screen_scale),
                    "style": "bold",
                },  # this is only used on the allegiances screen?
                {
                    "name": "clangen",
                    "point_size": floor(18 * screen_scale),
                    "style": "regular",
                },
            ]
        )

    if source_screen is not None and show_confirm_dialog:
        from scripts.game_structure.windows import ConfirmDisplayChanges

        ConfirmDisplayChanges(source_screen=source_screen)


def toggle_fullscreen(
    fullscreen: Optional[bool] = None,
    source_screen: Optional["Screens"] = None,
    show_confirm_dialog: bool = True,
    ingame_switch: bool = True,
):
    """
    Swap between fullscreen modes. Wraps the necessary game save to store the new value.
    :param fullscreen: Can be used to override the toggle to an explicit value. Leave as None to simply toggle.
    :param source_screen: Screen requesting the fullscreen toggle.
    :param show_confirm_dialog: True to show the confirm changes dialog, default True. Does nothing if source_screen is None.
    :param ingame_switch: Whether this was triggered by a user. Default True
    :return:
    """
    from scripts.game_structure.game_essentials import game

    if fullscreen is None:
        fullscreen = not game.settings["fullscreen"]

    game.settings["fullscreen"] = fullscreen
    game.save_settings()

    set_display_mode(
        fullscreen=fullscreen,
        source_screen=source_screen,
        show_confirm_dialog=show_confirm_dialog,
        ingame_switch=ingame_switch,
    )


def load_manager(res: Tuple[int, int], screen_offset: Tuple[int, int], scale: float):
    global MANAGER
    if MANAGER is not None:
        MANAGER = None

    # initialize pygame_gui manager, and load themes
    manager = UIManager(
        res,
        screen_offset,
        scale,
        "resources/theme/all.json",
        enable_live_theme_updates=False,
    )
    manager.add_font_paths(
        font_name="notosans",
        regular_path="resources/fonts/NotoSans-Medium.ttf",
        bold_path="resources/fonts/NotoSans-ExtraBold.ttf",
        italic_path="resources/fonts/NotoSans-MediumItalic.ttf",
        bold_italic_path="resources/fonts/NotoSans-ExtraBoldItalic.ttf",
    )
    manager.add_font_paths(
        font_name="clangen", regular_path="resources/fonts/clangen.ttf"
    )

    manager.get_theme().load_theme("resources/theme/themes/dark.json")

    return manager
