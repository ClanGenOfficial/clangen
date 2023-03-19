import os
import shutil
import threading
import time

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow

from scripts.datadir import get_save_dir
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.progress_bar_updater import UIUpdateProgressBar
from scripts.update import self_update
from scripts.utility import scale, quit


class SaveCheck(UIWindow):
    def __init__(self, last_screen, isMainMenu, mm_btn):
        print("Save Check Window Opened")
        if game.is_close_menu_open:
            print("Save Check Window already open")
            return
        game.is_close_menu_open = True
        super().__init__(scale(pygame.Rect((500, 400), (600, 400))),
                         window_display_title='Save Check',
                         object_id='#save_check_window',
                         resizable=False)

        self.clan_name = "UndefinedClan"
        if game.clan:
            self.clan_name = f"{game.clan.name}Clan"
        self.last_screen = last_screen
        self.isMainMenu = isMainMenu
        self.mm_btn = mm_btn

        if (self.isMainMenu):
            self.mm_btn.disable()
            self.main_menu_button = UIImageButton(
                scale(pygame.Rect((146, 310), (305, 60))),
                "",
                object_id="#main_menu_button",
                container=self
            )
            self.message = f"Would you like to save your game before exiting to the Main Menu? If you don't, progress may be lost!"
        else:
            self.main_menu_button = UIImageButton(
                scale(pygame.Rect((146, 310), (305, 60))),
                "",
                object_id="#smallquit_button",
                container=self
            )
            self.message = f"Would you like to save your game before exiting? If you don't, progress may be lost!"

        self.game_over_message = UITextBoxTweaked(
            self.message,
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self
        )

        self.save_button = UIImageButton(scale(pygame.Rect((186, 230), (228, 60))),
                                         "",
                                         object_id="#save_button",
                                         container=self
                                         )
        self.save_button_saved_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((186, 230), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/save_clan_saved.png'),
                (228, 60)),
            container=self)
        self.save_button_saved_state.hide()
        self.save_button_saving_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((186, 230), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/save_clan_saving.png'),
                (228, 60)),
            container=self)
        self.save_button_saving_state.hide()

        self.back_button = UIImageButton(
            scale(pygame.Rect((540, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )

        self.back_button.enable()
        self.main_menu_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu_button:
                if self.isMainMenu:
                    game.is_close_menu_open = False
                    self.mm_btn.enable()
                    game.last_screen_forupdate = game.switches['cur_screen']
                    game.switches['cur_screen'] = 'start screen'
                    game.switch_screens = True
                    self.kill()
                else:
                    game.is_close_menu_open = False
                    quit(savesettings=False, clearevents=False)
            elif event.ui_element == self.save_button:
                if game.clan is not None:
                    self.save_button_saving_state.show()
                    self.save_button.disable()
                    game.save_cats()
                    game.clan.save_clan()
                    game.clan.save_pregnancy(game.clan)
                    self.save_button_saving_state.hide()
                    self.save_button_saved_state.show()
            elif event.ui_element == self.back_button:
                game.is_close_menu_open = False
                self.kill()
                if self.isMainMenu:
                    self.mm_btn.enable()

                # only allow one instance of this window


class DeleteCheck(UIWindow):
    def __init__(self, reloadscreen, clan_name):
        super().__init__(scale(pygame.Rect((500, 400), (600, 360))),
                         window_display_title='Delete Check',
                         object_id='#delete_check_window',
                         resizable=False)
        self.clan_name = clan_name
        self.reloadscreen = reloadscreen

        self.delete_check_message = UITextBoxTweaked(
            f"Do you wish to delete {str(self.clan_name + 'Clan')}? This is permanent and cannot be undone.",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self
        )

        self.delete_it_button = UIImageButton(
            scale(pygame.Rect((142, 200), (306, 60))),
            "delete",
            object_id="#delete_it_button",
            container=self
        )
        self.go_back_button = UIImageButton(
            scale(pygame.Rect((142, 270), (306, 60))),
            "go back",
            object_id="#go_back_button",
            container=self
        )

        self.back_button = UIImageButton(
            scale(pygame.Rect((540, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )

        self.back_button.enable()

        self.go_back_button.enable()
        self.delete_it_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.delete_it_button:
                print("delete")
                rempath = get_save_dir() + "/" + self.clan_name
                shutil.rmtree(rempath)
                if os.path.exists(rempath + 'clan.json'):
                    os.remove(rempath + "clan.json")
                elif os.path.exists(rempath + 'clan.txt'):
                    os.remove(rempath + "clan.txt")
                else:
                    print("No clan.json/txt???? clan prolly wasnt initalized kekw")


                self.kill()

                self.reloadscreen('switch clan screen')

            elif event.ui_element == self.go_back_button:
                self.kill()
            elif event.ui_element == self.back_button:
                game.is_close_menu_open = False
                self.kill()


class GameOver(UIWindow):
    def __init__(self, last_screen):
        super().__init__(scale(pygame.Rect((500, 400), (600, 360))),
                         window_display_title='Game Over',
                         object_id='#game_over_window',
                         resizable=False)
        self.clan_name = str(game.clan.name + 'Clan')
        self.last_screen = last_screen
        self.game_over_message = UITextBoxTweaked(
            f"{self.clan_name} has died out. For now, this is where their story ends. Perhaps it's time to tell a new "
            f"tale?",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self
        )

        self.game_over_message = UITextBoxTweaked(
            f"(leaving will not erase the save file)",
            scale(pygame.Rect((40, 310), (520, -1))),
            line_spacing=.8,
            object_id="#cat_patrol_info_box",
            container=self
        )

        self.begin_anew_button = UIImageButton(
            scale(pygame.Rect((50, 230), (222, 60))),
            "",
            object_id="#begin_anew_button",
            container=self
        )
        self.not_yet_button = UIImageButton(
            scale(pygame.Rect((318, 230), (222, 60))),
            "",
            object_id="#not_yet_button",
            container=self
        )

        self.not_yet_button.enable()
        self.begin_anew_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.begin_anew_button:
                game.last_screen_forupdate = game.switches['cur_screen']
                game.switches['cur_screen'] = 'start screen'
                game.switch_screens = True
                self.kill()
            elif event.ui_element == self.not_yet_button:

                self.kill()


class UpdateWindow(UIWindow):
    def __init__(self, last_screen, asdf):
        super().__init__(scale(pygame.Rect((500, 400), (600, 320))),
                         window_display_title='Game Over',
                         object_id='#game_over_window',
                         resizable=False)
        self.clan_name = str(game.clan.name + 'Clan')
        self.last_screen = last_screen
        self.update_message = UITextBoxTweaked(
            f"Update in progress.",
            scale(pygame.Rect((40, 20), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self
        )
        self.asdf = asdf

        self.step_text = UITextBoxTweaked(
            f"Downloading update...",
            scale(pygame.Rect((40, 80), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self
        )

        self.progress_bar = UIUpdateProgressBar(
            scale(pygame.Rect((40, 130), (520, 70))),
            self.step_text,
            object_id="progress_bar",
            container=self,
        )

        x = threading.Thread(target=self_update, daemon=True, args=('development-test', self.progress_bar, self.step_text, asdf))
        x.start()

        self.not_yet_button = UIImageButton(
            scale(pygame.Rect((318, 230), (222, 60))),
            "",
            object_id="#not_yet_button",
            container=self
        )

        self.not_yet_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.not_yet_button:
                self.kill()


class AnnounceRestart(UIWindow):
    def __init__(self, last_screen):
        super().__init__(scale(pygame.Rect((500, 400), (600, 180))),
                         window_display_title='Game Over',
                         object_id='#game_over_window',
                         resizable=False)
        self.clan_name = str(game.clan.name + 'Clan')
        self.last_screen = last_screen
        self.announce_message = UITextBoxTweaked(
            f"The game will automatically restart in 3...",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self
        )

        threading.Thread(target=self.update_text, daemon=True).start()

    def update_text(self):
        for i in range(2, 0, -1):
            time.sleep(1)
            self.announce_message.set_text(f"The game will automatically restart in {i}...")
