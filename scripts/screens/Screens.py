from threading import current_thread
from typing import Dict, Optional

import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import (
    game,
    screen,
    MANAGER,
    game_screen_size,
    screen_scale,
    get_offset,
)
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.game_structure.ui_elements import UIImageButton, UISurfaceImageButton
from scripts.game_structure.windows import SaveCheck, EventLoading
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.utility import update_sprite, ui_scale, ui_scale_value, ui_scale_dimensions


def _menu_button_init():
    # menu buttons are used very often, so they are generated here.
    menu_buttons = dict()

    # they have to be added individually as some of them rely on others in anchors
    menu_buttons["events_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((246, 60), (82, 30))),
        "Events",
        get_button_dict(ButtonStyles.MENU_LEFT, (82, 30)),
        visible=False,
        manager=MANAGER,
        object_id=ObjectID(
            class_id="@buttonstyles_menu_left", object_id="#events_menu_button"
        ),
        starting_height=5,
    )
    menu_buttons["camp_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((0, 60), (58, 30))),
        "Camp",
        get_button_dict(ButtonStyles.MENU_MIDDLE, (58, 30)),
        visible=False,
        manager=MANAGER,
        object_id=ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"left": "left", "left_target": menu_buttons["events_screen"]},
    )
    menu_buttons["catlist_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((0, 60), (88, 30))),
        "Cat List",
        get_button_dict(ButtonStyles.MENU_MIDDLE, (88, 30)),
        visible=False,
        object_id=ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"left": "left", "left_target": menu_buttons["camp_screen"]},
    )
    menu_buttons["patrol_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((0, 60), (80, 30))),
        "Patrol",
        get_button_dict(ButtonStyles.MENU_RIGHT, (80, 30)),
        visible=False,
        manager=MANAGER,
        object_id=ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"left": "left", "left_target": menu_buttons["catlist_screen"]},
    )
    menu_buttons["main_menu"] = UIImageButton(
        ui_scale(pygame.Rect((25, 25), (153, 30))),
        "",
        visible=False,
        manager=MANAGER,
        object_id="#main_menu_button",
        starting_height=5,
    )

    # used so we can anchor to the right with numbers that make sense
    scale_rect = ui_scale(pygame.Rect((0, 0), (118, 30)))
    scale_rect.topright = ui_scale_dimensions((-25, 25))
    menu_buttons["allegiances"] = UISurfaceImageButton(
        scale_rect,
        "Allegiances",
        get_button_dict(ButtonStyles.SQUOVAL, (118, 30)),
        visible=False,
        manager=MANAGER,
        object_id=ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"right": "right"},
    )

    # used so we can anchor to the right with numbers that make sense
    scale_rect = ui_scale(pygame.Rect((0, 0), (85, 30)))
    scale_rect.topright = ui_scale_dimensions((-25, 5))
    menu_buttons["clan_settings"] = UISurfaceImageButton(
        scale_rect,
        "Settings",
        get_button_dict(ButtonStyles.SQUOVAL, (85, 30)),
        visible=False,
        manager=MANAGER,
        object_id=ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"top_target": menu_buttons["allegiances"], "right": "right"},
    )
    del scale_rect

    heading_rect = ui_scale(pygame.Rect((0, 0), (190, 35)))
    heading_rect.bottomleft = ui_scale_dimensions((0, 0))
    menu_buttons["name_background"] = pygame_gui.elements.UIImage(
        heading_rect,
        pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(),
            ui_scale_dimensions((190, 35)),
        ),
        visible=False,
        manager=MANAGER,
        starting_height=5,
        anchors={
            "bottom": "bottom",
            "bottom_target": menu_buttons["camp_screen"],
            "centerx": "centerx",
        },
    )
    menu_buttons["moons_n_seasons"] = pygame_gui.elements.UIScrollingContainer(
        ui_scale(pygame.Rect((25, 60), (153, 75))),
        visible=False,
        allow_scroll_x=False,
        manager=MANAGER,
        starting_height=5,
    )
    menu_buttons["moons_n_seasons_arrow"] = UIImageButton(
        ui_scale(pygame.Rect((174, 80), (22, 34))),
        "",
        visible=False,
        manager=MANAGER,
        object_id="#arrow_mns_button",
        starting_height=5,
    )
    menu_buttons["dens_bar"] = pygame_gui.elements.UIImage(
        ui_scale(pygame.Rect((40, 60), (10, 160))),
        pygame.transform.scale(
            image_cache.load_image("resources/images/vertical_bar.png").convert_alpha(),
            ui_scale_dimensions((380, 70)),
        ),
        visible=False,
        starting_height=5,
        manager=MANAGER,
    )
    menu_buttons["dens"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((25, 5), (71, 30))),
        "Dens",
        get_button_dict(ButtonStyles.SQUOVAL, (71, 30)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_squoval",
        starting_height=6,
        anchors={"top_target": menu_buttons["main_menu"]},
    )
    menu_buttons["lead_den"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((25, 100), (112, 28))),
        "leader's den",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (112, 28)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_rounded_rect",
        starting_height=6,
    )
    menu_buttons["med_cat_den"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((25, 140), (151, 28))),
        "medicine cat den",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (151, 28)),
        object_id="@buttonstyles_rounded_rect",
        visible=False,
        manager=MANAGER,
        starting_height=6,
    )
    menu_buttons["warrior_den"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((25, 180), (121, 28))),
        "warriors' den",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (121, 28)),
        object_id="@buttonstyles_rounded_rect",
        visible=False,
        manager=MANAGER,
        starting_height=6,
    )
    menu_buttons["clearing"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((25, 220), (81, 28))),
        "clearing",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (81, 28)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_rounded_rect",
        starting_height=6,
    )
    heading_rect = ui_scale(pygame.Rect((0, 0), (195, 35)))
    heading_rect.bottomleft = ui_scale_dimensions((0, 0))
    menu_buttons["heading"] = pygame_gui.elements.UITextBox(
        "",
        heading_rect,
        visible=False,
        manager=MANAGER,
        object_id="#text_box_34_horizcenter_light",
        starting_height=5,
        anchors={
            "bottom": "bottom",
            "bottom_target": menu_buttons["camp_screen"],
            "centerx": "centerx",
        },
    )
    del heading_rect
    return menu_buttons


class Screens:
    game_screen = screen
    last_screen = ""

    # the size has to be increased by 20 to account for the fact that we want the inner dimension to be
    # game_screen_size
    game_frame: pygame.Surface = pygame.image.load_sized_svg(
        "resources/images/border_gamescreen.svg",
        (
            game_screen_size[0] + ui_scale_value(20),
            game_screen_size[1] + ui_scale_value(20),
        ),
    )

    menu_buttons = _menu_button_init()

    def change_screen(self, new_screen):
        """Use this function when switching screens.
        It will handle keeping track of the last screen and cur screen.
        Last screen must be tracked to ensure a clear transition between screens."""
        # self.exit_screen()
        game.last_screen_forupdate = self.name

        # This keeps track of the last list-like screen for the back button on cat profiles
        if self.name in ["camp screen", "list screen", "events screen"]:
            game.last_screen_forProfile = self.name

        elif self.name not in [
            "list screen",
            "profile screen",
            "sprite inspect screen",
        ]:
            game.last_list_forProfile = None

        game.switches["cur_screen"] = new_screen
        game.switch_screens = True
        game.rpc.update_rpc.set()

    def __init__(self, name=None):
        self.game_frame: pygame.Surface = pygame.image.load_sized_svg(
            "resources/images/border_gamescreen.svg",
            (
                game_screen_size[0] + ui_scale_value(20),
                game_screen_size[1] + ui_scale_value(20),
            ),
        )
        self.name = name
        if name is not None:
            game.all_screens[name] = self
        else:
            Screens.menu_buttons = _menu_button_init()

        # Place to store the loading window(s)
        self.loading_window = {}

        # Dictionary of work done, keyed by the target function name
        self.work_done = {}

        bg = pygame.Surface(game_screen_size)
        bg.fill(game.config["theme"]["light_mode_background"])
        bg_dark = pygame.Surface(game_screen_size)
        bg_dark.fill(game.config["theme"]["dark_mode_background"])

        self.bgs = {"default_light": bg, "default_dark": bg_dark}
        self.blur_bgs = {
            "default_light": pygame.transform.scale(bg, screen.get_size()),
            "default_dark": pygame.transform.scale(bg_dark, screen.get_size()),
        }
        self.active_bg: Optional[pygame.Surface] = None

    def loading_screen_start_work(
        self, target: callable, thread_name: str = "work_thread", args: tuple = tuple()
    ) -> PropagatingThread:
        """Creates and starts the work_thread.
        Returns the started thread."""

        work_thread = PropagatingThread(
            target=self._work_target, args=(target, args), name=thread_name, daemon=True
        )

        game.switches["window_open"] = True
        work_thread.start()

        return work_thread

    def _work_target(self, target, args):
        exp = None
        try:
            target(*args)
        except Exception as e:
            exp = e

        self.work_done[current_thread().name] = True
        if exp:
            raise exp

    def loading_screen_on_use(
        self,
        work_thread: PropagatingThread,
        final_actions: callable,
        loading_screen_pos: tuple = None,
        delay: float = 0.7,
    ) -> None:
        """Handles all actions that must be run every frame for the loading window to work.
        Also handles creating and killing the loading window.
        """

        if not isinstance(work_thread, PropagatingThread):
            return

        # Handled the loading animation, both creating and killing it.
        if (
            not self.loading_window.get(work_thread.name)
            and work_thread.is_alive()
            and work_thread.get_time_from_start() > delay
        ):
            self.loading_window[work_thread.name] = EventLoading(loading_screen_pos)
        elif self.loading_window.get(work_thread.name) and not work_thread.is_alive():
            self.loading_window[work_thread.name].kill()
            self.loading_window.pop(work_thread.name)

        # Handles displaying the events once timeskip is done.
        if self.work_done.get(work_thread.name, False):
            # By this time, the thread should have already finished.
            # This line allows exceptions in the work thread to be
            # passed to the main thread, so issues in the work thread are not
            # silent failures.
            work_thread.join()

            self.work_done.pop(work_thread.name)

            final_actions()
            game.switches["window_open"] = False

        return

    def fill(self, tuple):
        pygame.Surface.fill(self.game_screen, color=tuple)

    def on_use(self):
        """Runs every frame this screen is used."""
        self.show_bg()

    def screen_switches(self):
        """Runs when this screen is switched to."""
        self.set_bg("default")

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here."""
        pass

    def exit_screen(self):
        """Runs when screen exits"""
        pass

    # Functions to deal with the menu.
    #   The menu is used very often, so I don't want to keep
    #   recreating and killing it. Lots of changes for bugs there.
    #

    def hide_menu_buttons(self):
        """This hides the menu buttons, so they are no longer visible
        or interact-able. It does not delete the buttons from memory."""
        for button in self.menu_buttons.values():
            button.hide()

    def show_menu_buttons(self):
        """This shows all menu buttons, and makes them interact-able."""
        # Check if the setting for moons and seasons UI is on so stats button can be moved
        self.update_mns()
        for name, button in self.menu_buttons.items():
            if name == "dens":
                if (
                    game.clan.clan_settings["moons and seasons"]
                    and game.switches["cur_screen"] == "events screen"
                ):
                    button.show()
                elif (
                    not game.clan.clan_settings["moons and seasons"]
                    and game.switches["cur_screen"] != "camp screen"
                ):
                    button.show()
            if name in [
                "moons_n_seasons",
                "moons_n_seasons_arrow",
                "dens",
                "med_cat_den",
                "lead_den",
                "clearing",
                "warrior_den",
                "dens_bar",
            ]:
                continue
            else:
                button.show()

    # Enables all menu buttons but the ones passed in.
    # Sloppy, but works. Consider making it nicer.
    def set_disabled_menu_buttons(self, disabled_buttons=()):
        """This sets all menu buttons as interact-able, except buttons listed in disabled_buttons."""
        for button in self.menu_buttons.values():
            button.enable()

        for button_id in disabled_buttons:
            if button_id in self.menu_buttons:
                self.menu_buttons[button_id].disable()

    def menu_button_pressed(self, event):
        """This is a short-up to deal with menu button presses.
        This will fail if event.type != pygame_gui.UI_BUTTON_START_PRESS"""
        if game.switches["window_open"]:
            pass
        elif event.ui_element == self.menu_buttons["events_screen"]:
            self.change_screen("events screen")
        elif event.ui_element == self.menu_buttons["camp_screen"]:
            self.change_screen("camp screen")
        elif event.ui_element == self.menu_buttons["catlist_screen"]:
            self.change_screen("list screen")
        elif event.ui_element == self.menu_buttons["patrol_screen"]:
            self.change_screen("patrol screen")
        elif event.ui_element == self.menu_buttons["main_menu"]:
            SaveCheck(game.switches["cur_screen"], True, self.menu_buttons["main_menu"])
        elif event.ui_element == self.menu_buttons["allegiances"]:
            self.change_screen("allegiances screen")
        elif event.ui_element == self.menu_buttons["clan_settings"]:
            self.change_screen("clan settings screen")
        elif event.ui_element == self.menu_buttons["moons_n_seasons_arrow"]:
            if game.settings["mns open"]:
                game.settings["mns open"] = False
            else:
                game.settings["mns open"] = True
            self.update_mns()
        elif event.ui_element == self.menu_buttons["dens"]:
            self.update_dens()
        elif event.ui_element == self.menu_buttons["lead_den"]:
            self.change_screen("leader den screen")
        elif event.ui_element == self.menu_buttons["clearing"]:
            self.change_screen("clearing screen")
        elif event.ui_element == self.menu_buttons["med_cat_den"]:
            self.change_screen("med den screen")
        elif event.ui_element == self.menu_buttons["warrior_den"]:
            self.change_screen("warrior den screen")

    def update_dens(self):
        dens = [
            "dens_bar",
            "lead_den",
            "med_cat_den",
            "warrior_den",
            "clearing",
        ]

        for den in dens:
            # if dropdown is visible, hide
            if self.menu_buttons[den].visible:
                self.menu_buttons[den].hide()
            else:  # else, show
                if game.clan.game_mode != "classic":
                    self.menu_buttons[den].show()
                else:  # classic doesn't get access to clearing, so we can't show its button here
                    if den == "clearing":
                        # redraw this to be shorter
                        self.menu_buttons["dens_bar"].kill()
                        self.menu_buttons.update(
                            {
                                "dens_bar": pygame_gui.elements.UIImage(
                                    ui_scale(pygame.Rect((40, 60), (10, 125))),
                                    pygame.transform.scale(
                                        image_cache.load_image(
                                            "resources/images/vertical_bar.png"
                                        ).convert_alpha(),
                                        ui_scale_dimensions((10, 125)),
                                    ),
                                    visible=True,
                                    starting_height=1,
                                    manager=MANAGER,
                                )
                            }
                        )
                    else:
                        self.menu_buttons[den].show()

    def update_heading_text(self, text):
        """Updates the menu heading text"""
        self.menu_buttons["heading"].set_text(text)

        # Update if moons and seasons UI is on

    def update_mns(self):
        if (
            game.clan.clan_settings["moons and seasons"]
            and game.switches["cur_screen"] != "events screen"
        ):
            self.menu_buttons["moons_n_seasons_arrow"].kill()
            self.menu_buttons["moons_n_seasons"].kill()
            if game.settings["mns open"]:
                if self.name == "events screen":
                    self.mns_close()
                else:
                    self.mns_open()
            else:
                self.mns_close()
        else:
            self.menu_buttons["moons_n_seasons"].hide()
            self.menu_buttons["moons_n_seasons_arrow"].hide()

    # open moons and seasons UI (AKA wide version)
    def mns_open(self):
        self.menu_buttons["moons_n_seasons_arrow"] = UIImageButton(
            ui_scale(pygame.Rect((174, 80), (22, 34))),
            "",
            manager=MANAGER,
            object_id="#arrow_mns_button",
        )
        self.menu_buttons["moons_n_seasons"] = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((25, 60), (153, 75))),
            allow_scroll_x=False,
            manager=MANAGER,
        )
        self.moons_n_seasons_bg = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (153, 75))),
            "",
            manager=MANAGER,
            object_id="#mns_bg",
            container=self.menu_buttons["moons_n_seasons"],
        )

        if game.clan.age == 1:
            moons_text = "moon"
        else:
            moons_text = "moons"

        self.moons_n_seasons_moon = UIImageButton(
            ui_scale(pygame.Rect((14, 10), (24, 24))),
            "",
            manager=MANAGER,
            object_id=ObjectID(class_id="@mns_image", object_id="#moon"),
            container=self.menu_buttons["moons_n_seasons"],
        )
        self.moons_n_seasons_text = pygame_gui.elements.UITextBox(
            f"{game.clan.age} {moons_text}",
            ui_scale(pygame.Rect((42, 6), (100, 30))),
            container=self.menu_buttons["moons_n_seasons"],
            manager=MANAGER,
            object_id="#text_box_30_horizleft_light",
        )

        if game.clan.current_season == "Newleaf":
            season_image_id = "#mns_image_newleaf"
        elif game.clan.current_season == "Greenleaf":
            season_image_id = "#mns_image_greenleaf"
        elif game.clan.current_season == "Leaf-bare":
            season_image_id = "#mns_image_leafbare"
        elif game.clan.current_season == "Leaf-fall":
            season_image_id = "#mns_image_leaffall"

        self.moons_n_seasons_season = UIImageButton(
            ui_scale(pygame.Rect((14, 41), (24, 24))),
            "",
            manager=MANAGER,
            object_id=season_image_id,
            container=self.menu_buttons["moons_n_seasons"],
        )
        self.moons_n_seasons_text2 = pygame_gui.elements.UITextBox(
            f"{game.clan.current_season}",
            ui_scale(pygame.Rect((42, 36), (100, 30))),
            container=self.menu_buttons["moons_n_seasons"],
            manager=MANAGER,
            object_id="#text_box_30_horizleft_dark",
        )

    # close moons and seasons UI (AKA narrow version)
    def mns_close(self):
        self.menu_buttons["moons_n_seasons_arrow"] = UIImageButton(
            ui_scale(pygame.Rect((71, 80), (22, 34))),
            "",
            object_id="#arrow_mns_closed_button",
        )
        if self.name == "events screen":
            self.menu_buttons["moons_n_seasons_arrow"].kill()

        self.menu_buttons["moons_n_seasons"] = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((25, 60), (50, 75))),
            allow_scroll_x=False,
            manager=MANAGER,
        )
        self.moons_n_seasons_bg = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (50, 75))),
            "",
            manager=MANAGER,
            object_id="#mns_bg_closed",
            container=self.menu_buttons["moons_n_seasons"],
        )

        if game.clan.age == 1:
            moons_text = "moon"
        else:
            moons_text = "moons"

        self.moons_n_seasons_moon = UIImageButton(
            ui_scale(pygame.Rect((14, 10), (24, 24))),
            "",
            manager=MANAGER,
            object_id="#mns_image_moon",
            container=self.menu_buttons["moons_n_seasons"],
            starting_height=2,
            tool_tip_text=f"{game.clan.age} {moons_text}",
        )

        if game.clan.current_season == "Newleaf":
            season_image_id = ObjectID(class_id="@mns_image", object_id="#newleaf")
        elif game.clan.current_season == "Greenleaf":
            season_image_id = ObjectID(class_id="@mns_image", object_id="#greenleaf")
        elif game.clan.current_season == "Leaf-bare":
            season_image_id = ObjectID(class_id="@mns_image", object_id="#leafbare")
        elif game.clan.current_season == "Leaf-fall":
            season_image_id = ObjectID(class_id="@mns_image", object_id="#leaffall")

        self.moons_n_seasons_season = UIImageButton(
            ui_scale(pygame.Rect((14, 41), (24, 24))),
            "",
            manager=MANAGER,
            object_id=season_image_id,
            container=self.menu_buttons["moons_n_seasons"],
            starting_height=2,
            tool_tip_text=f"{game.clan.current_season}",
        )

    def add_bgs(
        self,
        bgs: Dict[str, pygame.Surface],
        blur_bgs: Dict[str, pygame.Surface] = None,
        radius: int = 5,
    ):
        for name, bg in bgs.items():
            self.bgs[name] = pygame.transform.scale(bg, game_screen_size)
            if blur_bgs is not None and name in blur_bgs:
                self.blur_bgs[name] = pygame.transform.scale(
                    blur_bgs[name], screen.get_size()
                )
                continue
            self.blur_bgs[name] = pygame.transform.scale(
                pygame.transform.box_blur(bg, radius), screen.get_size()
            )

    def set_bg(self, bg: Optional[str]):
        if bg == "default":
            self.active_bg = (
                "default_dark" if game.settings["dark mode"] else "default_light"
            )
        if bg in self.bgs:
            self.active_bg = bg
        if bg is None:
            self.active_bg = None

    def show_bg(self):
        """Blit the currently selected blur_bg and bg."""
        if self.active_bg is None:
            self.active_bg = (
                "default_dark" if game.settings["dark mode"] else "default_light"
            )
        offset = get_offset()
        if game.settings["fullscreen"]:
            screen.blit(self.blur_bgs[self.active_bg], (0, 0))
            screen.blit(
                self.game_frame,
                (offset[0] - (10 * screen_scale), offset[1] - (10 * screen_scale)),
            )
        screen.blit(self.bgs[self.active_bg], offset)


# CAT PROFILES
def cat_profiles():
    """Updates every cat's sprites"""
    game.choose_cats.clear()

    for x in Cat.all_cats:
        update_sprite(Cat.all_cats[x])
