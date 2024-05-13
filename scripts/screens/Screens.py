import pygame

from scripts.utility import update_sprite, scale
from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure import image_cache
from scripts.game_structure.image_button import UIImageButton
import pygame_gui
from scripts.game_structure.windows import SaveCheck, EventLoading
from scripts.game_structure.propagating_thread import PropagatingThread
from threading import current_thread


class Screens():
    game_screen = screen
    game_x = screen_x
    game_y = screen_y
    last_screen = ''

    # menu buttons are used very often, so they are generated here.
    menu_buttons = {
        "events_screen": UIImageButton(
            scale(pygame.Rect((492, 120), (164, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#events_menu_button",
        ),
        "camp_screen": UIImageButton(
            scale(pygame.Rect((656, 120), (116, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#camp_menu_button"),
        "catlist_screen": UIImageButton(
            scale(pygame.Rect((772, 120), (176, 60))),
            "",
            visible=False,
            object_id="#catlist_menu_button"),
        "patrol_screen": UIImageButton(
            scale(pygame.Rect((948, 120), (160, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#patrol_menu_button"),
        "main_menu": UIImageButton(
            scale(pygame.Rect((50, 50), (306, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#main_menu_button"),
        "allegiances": UIImageButton(
            scale(pygame.Rect((1314, 50), (236, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#allegiances_button"),
        "clan_settings": UIImageButton(
            scale(pygame.Rect((1380, 120), (170, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#clan_settings_button"),
        "name_background": pygame_gui.elements.UIImage(
            scale(pygame.Rect((610, 50), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (380, 70)),
            visible=False,
            manager=MANAGER),
        "moons_n_seasons": pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((50, 120), (306, 150))),
            visible=False,
            manager=MANAGER),
        "moons_n_seasons_arrow": UIImageButton(
            scale(pygame.Rect((349, 161), (44, 68))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#arrow_mns_button"),
        "dens_bar": pygame_gui.elements.UIImage(
            scale(pygame.Rect((80, 120), (20, 280))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/vertical_bar.png").convert_alpha(),
                (380, 70)),
            visible=False,
            manager=MANAGER),
        "dens": UIImageButton(
            scale(pygame.Rect((50, 120), (142, 60))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#dens_button",
            starting_height=4),
        "med_cat_den": UIImageButton(
            scale(pygame.Rect((50, 200), (302, 56))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#med_den_button",
            starting_height=4),
        "warrior_den": UIImageButton(
            scale(pygame.Rect((50, 280), (242, 56))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#warrior_den_button",
            starting_height=4),
        "clearing": UIImageButton(
            scale(pygame.Rect((50, 360), (162, 56))),
            "",
            visible=False,
            manager=MANAGER,
            object_id="#clearing_button",
            starting_height=4
        ),

        "heading": pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((610, 54), (380, 70))),
            visible=False,
            manager=MANAGER,
            object_id="#text_box_34_horizcenter_light")
    }

    def change_screen(self, new_screen):
        """Use this function when switching screens.
            It will handle keeping track of the last screen and cur screen.
            Last screen must be tracked to ensure a clear transition between screens."""
        # self.exit_screen()
        game.last_screen_forupdate = self.name

        # This keeps track of the last list-like screen for the back button on cat profiles
        if self.name in ['camp screen', 'list screen', 'events screen']:
            game.last_screen_forProfile = self.name

        elif self.name not in ['list screen', 'profile screen', 'sprite inspect screen']:
            game.last_list_forProfile = None

        game.switches['cur_screen'] = new_screen
        game.switch_screens = True
        game.rpc.update_rpc.set()

    def __init__(self, name=None):
        self.name = name
        if name is not None:
            game.all_screens[name] = self

        # Place to store the loading window(s)
        self.loading_window = {}

        # Dictionary of work done, keyed by the target function name
        self.work_done = {}

    def loading_screen_start_work(self,
                                  target: callable,
                                  thread_name: str = "work_thread",
                                  args: tuple = tuple()) -> PropagatingThread:
        """Creates and starts the work_thread. 
            Returns the started thread. """

        work_thread = PropagatingThread(target=self._work_target, args=(target, args),
                                        name=thread_name, daemon=True)

        game.switches['window_open'] = True
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

    def loading_screen_on_use(self,
                              work_thread: PropagatingThread,
                              final_actions: callable,
                              loading_screen_pos: tuple = None,
                              delay: float = 0.7) -> None:
        """Handles all actions that must be run every frame for the loading window to work. 
        Also handles creating and killing the loading window. 
         """

        if not isinstance(work_thread, PropagatingThread):
            return

        # Handled the loading animation, both creating and killing it. 
        if not self.loading_window.get(work_thread.name) and work_thread.is_alive() \
                and work_thread.get_time_from_start() > delay:
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
            game.switches['window_open'] = False

        return

    def fill(self, tuple):
        pygame.Surface.fill(color=tuple)

    def on_use(self):
        """Runs every frame this screen is used."""
        pass

    def screen_switches(self):
        """Runs when this screen is switched to."""
        pass

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. """
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
        """This shows all menu buttons, and makes them interact-able. """
        # Check if the setting for moons and seasons UI is on so stats button can be moved
        self.update_mns()
        for name, button in self.menu_buttons.items():
            if name == 'dens':
                if game.clan.clan_settings["moons and seasons"] and game.switches['cur_screen'] == 'events screen':
                    button.show()
                elif not game.clan.clan_settings["moons and seasons"] and game.switches['cur_screen'] != 'camp screen':
                    button.show()
            if name in ['moons_n_seasons', 'moons_n_seasons_arrow', 'dens', 'med_cat_den', 'clearing', 'warrior_den',
                        'dens_bar']:
                continue
            else:
                button.show()

    # Enables all menu buttons but the ones passed in.
    # Sloppy, but works. Consider making it nicer.
    def set_disabled_menu_buttons(self, disabled_buttons=()):
        """This sets all menu buttons as interact-able, except buttons listed in disabled_buttons.  """
        for button in self.menu_buttons.values():
            button.enable()

        for button_id in disabled_buttons:
            if button_id in self.menu_buttons:
                self.menu_buttons[button_id].disable()

    def menu_button_pressed(self, event):
        """This is a short-up to deal with menu button presses.
            This will fail if event.type != pygame_gui.UI_BUTTON_START_PRESS"""
        if game.switches['window_open']:
            pass
        elif event.ui_element == self.menu_buttons["events_screen"]:
            self.change_screen('events screen')
        elif event.ui_element == self.menu_buttons["camp_screen"]:
            self.change_screen('camp screen')
        elif event.ui_element == self.menu_buttons["catlist_screen"]:
            self.change_screen('list screen')
        elif event.ui_element == self.menu_buttons["patrol_screen"]:
            self.change_screen('patrol screen')
        elif event.ui_element == self.menu_buttons["main_menu"]:
            SaveCheck(game.switches['cur_screen'], True, self.menu_buttons["main_menu"])
        elif event.ui_element == self.menu_buttons["allegiances"]:
            self.change_screen('allegiances screen')
        elif event.ui_element == self.menu_buttons["clan_settings"]:
            self.change_screen('clan settings screen')
        elif event.ui_element == self.menu_buttons["moons_n_seasons_arrow"]:
            if game.settings['mns open']:
                game.settings['mns open'] = False
            else:
                game.settings['mns open'] = True
            self.update_mns()
        elif event.ui_element == self.menu_buttons["dens"]:
            self.update_dens()
        elif event.ui_element == self.menu_buttons["clearing"]:
            self.change_screen('clearing screen')
        elif event.ui_element == self.menu_buttons["med_cat_den"]:
            self.change_screen('med den screen')
        elif event.ui_element == self.menu_buttons["warrior_den"]:
            self.change_screen('warrior den screen')

    def update_dens(self):
        dens = ["dens_bar", "med_cat_den", "warrior_den", "clearing", ]
        # this feels convoluted but its all i got, feel free to streamline
        for den in dens:
            # if the dropdown isn't visible, make it visible
            if not self.menu_buttons[den].visible:
                # if it's classic mode, don't show the clearing button and shorten the dens_bar
                if game.clan.game_mode == "classic" and den == "clearing":
                    if self.menu_buttons['med_cat_den'].visible:
                        self.menu_buttons["dens_bar"].kill()
                        self.menu_buttons.update({
                            "dens_bar": pygame_gui.elements.UIImage(
                                scale(pygame.Rect((80, 120), (20, 210))),
                                pygame.transform.scale(
                                    image_cache.load_image(
                                        "resources/images/vertical_bar.png").convert_alpha(),
                                    (380, 70)),
                                visible=True,
                                manager=MANAGER)})
                    else:
                        self.menu_buttons[den].hide()
                else:
                    self.menu_buttons[den].show()
            else:
                self.menu_buttons[den].hide()

    def update_heading_text(self, text):
        """Updates the menu heading text"""
        self.menu_buttons['heading'].set_text(text)

        # Update if moons and seasons UI is on

    def update_mns(self):
        if game.clan.clan_settings["moons and seasons"] and game.switches['cur_screen'] != 'events screen':
            self.menu_buttons['moons_n_seasons_arrow'].kill()
            self.menu_buttons['moons_n_seasons'].kill()
            if game.settings['mns open']:
                if self.name == 'events screen':
                    self.mns_close()
                else:
                    self.mns_open()
            else:
                self.mns_close()
        else:
            self.menu_buttons['moons_n_seasons'].hide()
            self.menu_buttons['moons_n_seasons_arrow'].hide()

    # open moons and seasons UI (AKA wide version)    
    def mns_open(self):
        self.menu_buttons['moons_n_seasons_arrow'] = UIImageButton(
            scale(pygame.Rect((349, 161), (44, 68))),
            "",
            manager=MANAGER,
            object_id="#arrow_mns_button")
        self.menu_buttons['moons_n_seasons'] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((50, 120), (306, 150))),
            manager=MANAGER)
        self.moons_n_seasons_bg = UIImageButton(
            scale(pygame.Rect((0, 0), (306, 150))),
            "",
            manager=MANAGER,
            object_id="#mns_bg",
            container=self.menu_buttons['moons_n_seasons'])

        if game.clan.age == 1:
            moons_text = "moon"
        else:
            moons_text = "moons"

        self.moons_n_seasons_moon = UIImageButton(
            scale(pygame.Rect((28, 21), (48, 48))),
            "",
            manager=MANAGER,
            object_id="#mns_image_moon",
            container=self.menu_buttons['moons_n_seasons'])
        self.moons_n_seasons_text = pygame_gui.elements.UITextBox(
            f'{game.clan.age} {moons_text}',
            scale(pygame.Rect((85, 13), (200, 60))),
            container=self.menu_buttons['moons_n_seasons'],
            manager=MANAGER,
            object_id="#text_box_30_horizleft_light")

        if game.clan.current_season == 'Newleaf':
            season_image_id = '#mns_image_newleaf'
        elif game.clan.current_season == 'Greenleaf':
            season_image_id = '#mns_image_greenleaf'
        elif game.clan.current_season == 'Leaf-bare':
            season_image_id = '#mns_image_leafbare'
        elif game.clan.current_season == 'Leaf-fall':
            season_image_id = '#mns_image_leaffall'

        self.moons_n_seasons_season = UIImageButton(
            scale(pygame.Rect((28, 82), (48, 48))),
            "",
            manager=MANAGER,
            object_id=season_image_id,
            container=self.menu_buttons['moons_n_seasons'])
        self.moons_n_seasons_text2 = pygame_gui.elements.UITextBox(
            f'{game.clan.current_season}',
            scale(pygame.Rect((85, 72), (200, 60))),
            container=self.menu_buttons['moons_n_seasons'],
            manager=MANAGER,
            object_id="#text_box_30_horizleft_dark")

    # close moons and seasons UI (AKA narrow version)
    def mns_close(self):
        self.menu_buttons['moons_n_seasons_arrow'] = UIImageButton(
            scale(pygame.Rect((143, 161), (44, 68))),
            "",
            object_id="#arrow_mns_closed_button")
        if self.name == 'events screen':
            self.menu_buttons['moons_n_seasons_arrow'].kill()

        self.menu_buttons['moons_n_seasons'] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((50, 120), (100, 150))),
            manager=MANAGER)
        self.moons_n_seasons_bg = UIImageButton(
            scale(pygame.Rect((0, 0), (100, 150))),
            "",
            manager=MANAGER,
            object_id="#mns_bg_closed",
            container=self.menu_buttons['moons_n_seasons'])

        if game.clan.age == 1:
            moons_text = "moon"
        else:
            moons_text = "moons"

        self.moons_n_seasons_moon = UIImageButton(
            scale(pygame.Rect((28, 21), (48, 48))),
            "",
            manager=MANAGER,
            object_id="#mns_image_moon",
            container=self.menu_buttons['moons_n_seasons'],
            starting_height=2,
            tool_tip_text=f'{game.clan.age} {moons_text}')

        if game.clan.current_season == 'Newleaf':
            season_image_id = '#mns_image_newleaf'
        elif game.clan.current_season == 'Greenleaf':
            season_image_id = '#mns_image_greenleaf'
        elif game.clan.current_season == 'Leaf-bare':
            season_image_id = '#mns_image_leafbare'
        elif game.clan.current_season == 'Leaf-fall':
            season_image_id = '#mns_image_leaffall'

        self.moons_n_seasons_season = UIImageButton(
            scale(pygame.Rect((28, 82), (48, 48))),
            "",
            manager=MANAGER,
            object_id=season_image_id,
            container=self.menu_buttons['moons_n_seasons'],
            starting_height=2,
            tool_tip_text=f'{game.clan.current_season}')


# CAT PROFILES
def cat_profiles():
    """Updates every cat's sprites"""
    game.choose_cats.clear()

    for x in Cat.all_cats:
        update_sprite(Cat.all_cats[x])
