import os
import shutil
import threading
import time

import pygame
import pygame_gui
from sys import exit
from re import sub

from scripts.cat.history import History
from scripts.cat.names import Name
from pygame_gui.elements import UIWindow

from scripts.housekeeping.datadir import get_save_dir, get_cache_dir
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, screen_x, screen_y
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.housekeeping.progress_bar_updater import UIUpdateProgressBar
from scripts.housekeeping.update import self_update, UpdateChannel, get_latest_version_number
from scripts.utility import scale, quit, update_sprite
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.housekeeping.version import get_version_info


class SaveCheck(UIWindow):
    def __init__(self, last_screen, isMainMenu, mm_btn):
        game.switches['window_open'] = True
        if game.is_close_menu_open:
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
            object_id="#text_box_30_horizcenter",
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
        self.set_blocking(True)

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
                    game.switches['window_open'] = False
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
                game.switches['window_open'] = False
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
        self.set_blocking(True)
        game.switches['window_open'] = True
        self.clan_name = clan_name
        self.reloadscreen = reloadscreen

        self.delete_check_message = UITextBoxTweaked(
            f"Do you wish to delete {str(self.clan_name + 'Clan')}? This is permanent and cannot be undone.",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
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
                game.switches['window_open'] = False
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
                game.switches['window_open'] = False
                self.kill()
            elif event.ui_element == self.back_button:
                game.switches['window_open'] = False
                game.is_close_menu_open = False
                self.kill()


class GameOver(UIWindow):
    def __init__(self, last_screen):
        super().__init__(scale(pygame.Rect((500, 400), (600, 360))),
                         window_display_title='Game Over',
                         object_id='#game_over_window',
                         resizable=False)
        self.set_blocking(True)
        game.switches['window_open'] = True
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
            object_id="#text_box_22_horizcenter",
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
                game.switches['window_open'] = False
                self.kill()
            elif event.ui_element == self.not_yet_button:
                game.switches['window_open'] = False
                self.kill()


class ChangeCatName(UIWindow):
    """This window allows the user to change the cat's name"""

    def __init__(self, cat):
        super().__init__(scale(pygame.Rect((600, 430), (800, 370))),
                         window_display_title='Change Cat Name',
                         object_id='#change_cat_name_window',
                         resizable=False)
        game.switches['window_open'] = True
        self.the_cat = cat
        self.back_button = UIImageButton(
            scale(pygame.Rect((740, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )
        self.heading = pygame_gui.elements.UITextBox(f"-Change {self.the_cat.name}'s Name-",
                                                     scale(pygame.Rect((0, 20), (800, 80))),
                                                     object_id="#text_box_30_horizcenter",
                                                     manager=MANAGER,
                                                     container=self)

        self.name_changed = pygame_gui.elements.UITextBox("Name Changed!", scale(pygame.Rect((490, 260), (800, 80))),
                                                          visible=False,
                                                          object_id="#text_box_30_horizleft",
                                                          manager=MANAGER,
                                                          container=self)

        self.done_button = UIImageButton(scale(pygame.Rect((323, 270), (154, 60))), "",
                                         object_id="#done_button",
                                         manager=MANAGER,
                                         container=self)

        x_pos, y_pos = 75, 35

        self.prefix_entry_box = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((0 + x_pos, 100 + y_pos), (240, 60))),
            placeholder_text=self.the_cat.name.prefix,
            manager=MANAGER,
            container=self)

        self.random_prefix = UIImageButton(scale(pygame.Rect((245 + x_pos, 97 + y_pos), (68, 68))), "",
                                           object_id="#random_dice_button",
                                           manager=MANAGER,
                                           container=self,
                                           tool_tip_text='Randomize the prefix')

        self.random_suffix = UIImageButton(scale(pygame.Rect((563 + x_pos, 97 + y_pos), (68, 68))), "",
                                           object_id="#random_dice_button",
                                           manager=MANAGER,
                                           container=self,
                                           tool_tip_text='Randomize the suffix')

        # 636
        self.toggle_spec_block_on = UIImageButton(scale(pygame.Rect((405 + x_pos, 160 + y_pos), (68, 68))), "",
                                                  object_id="#unchecked_checkbox",
                                                  tool_tip_text=f"Remove the cat's special suffix",
                                                  manager=MANAGER,
                                                  container=self)

        self.toggle_spec_block_off = UIImageButton(scale(pygame.Rect((405 + x_pos, 160 + y_pos), (68, 68))), "",
                                                   object_id="#checked_checkbox",
                                                   tool_tip_text="Re-enable the cat's special suffix", manager=MANAGER,
                                                   container=self)

        if self.the_cat.name.status in self.the_cat.name.names_dict["special_suffixes"]:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(
                scale(pygame.Rect((318 + x_pos, 100 + y_pos), (240, 60))),
                placeholder_text=
                self.the_cat.name.names_dict["special_suffixes"]
                [self.the_cat.name.status]
                , manager=MANAGER,
                container=self)
            if not self.the_cat.name.specsuffix_hidden:
                self.toggle_spec_block_on.show()
                self.toggle_spec_block_on.enable()
                self.toggle_spec_block_off.hide()
                self.toggle_spec_block_off.disable()
                self.random_suffix.disable()
                self.suffix_entry_box.disable()
            else:
                self.toggle_spec_block_on.hide()
                self.toggle_spec_block_on.disable()
                self.toggle_spec_block_off.show()
                self.toggle_spec_block_off.enable()
                self.random_suffix.enable()
                self.suffix_entry_box.enable()
                self.suffix_entry_box.set_text(self.the_cat.name.suffix)


        else:
            self.toggle_spec_block_on.disable()
            self.toggle_spec_block_on.hide()
            self.toggle_spec_block_off.disable()
            self.toggle_spec_block_off.hide()
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(
                scale(pygame.Rect((318 + x_pos, 100 + y_pos), (240, 60))),
                placeholder_text=self.the_cat.name.suffix
                , manager=MANAGER,
                container=self)
        self.set_blocking(True)

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if sub(r'[^A-Za-z0-9 ]+', '', self.prefix_entry_box.get_text()) != '':
                    self.the_cat.name.prefix = sub(r'[^A-Za-z0-9 ]+', '', self.prefix_entry_box.get_text())
                    self.name_changed.show()

                if sub(r'[^A-Za-z0-9 ]+', '', self.suffix_entry_box.get_text()) != '':
                    self.the_cat.name.suffix = sub(r'[^A-Za-z0-9 ]+', '', self.suffix_entry_box.get_text())
                    self.name_changed.show()
                    self.the_cat.specsuffix_hidden = True
                    self.the_cat.name.specsuffix_hidden = True
                elif sub(r'[^A-Za-z0-9 ]+', '',
                         self.suffix_entry_box.get_text()) == '' and not self.the_cat.name.specsuffix_hidden:
                    self.name_changed.show()
                else:
                    self.the_cat.specsuffix_hidden = False
                    self.the_cat.name.specsuffix_hidden = False
                self.heading.set_text(f"-Change {self.the_cat.name}'s Name-")
            elif event.ui_element == self.random_prefix:
                if self.suffix_entry_box.text:
                    use_suffix = self.suffix_entry_box.text
                else:
                    use_suffix = self.the_cat.name.suffix
                self.prefix_entry_box.set_text(Name(self.the_cat.status,
                                                    None,
                                                    use_suffix,
                                                    self.the_cat.pelt.colour,
                                                    self.the_cat.eye_colour,
                                                    self.the_cat.pelt.name,
                                                    self.the_cat.tortiepattern,
                                                    specsuffix_hidden=
                                                    (self.the_cat.name.status in self.the_cat.name.names_dict[
                                                        "special_suffixes"])).prefix)
            elif event.ui_element == self.random_suffix:
                if self.prefix_entry_box.text:
                    use_prefix = self.prefix_entry_box.text
                else:
                    use_prefix = self.the_cat.name.prefix
                self.suffix_entry_box.set_text(Name(self.the_cat.status,
                                                    use_prefix,
                                                    None,
                                                    self.the_cat.pelt.colour,
                                                    self.the_cat.eye_colour,
                                                    self.the_cat.pelt.name,
                                                    self.the_cat.tortiepattern,
                                                    specsuffix_hidden=
                                                    (self.the_cat.name.status in self.the_cat.name.names_dict[
                                                        "special_suffixes"])).suffix)
            elif event.ui_element == self.toggle_spec_block_on:
                self.suffix_entry_box.enable()
                self.random_suffix.enable()
                self.toggle_spec_block_on.disable()
                self.toggle_spec_block_on.hide()
                self.toggle_spec_block_off.enable()
                self.toggle_spec_block_off.show()
                self.suffix_entry_box.set_text(self.the_cat.name.suffix)
            elif event.ui_element == self.toggle_spec_block_off:
                self.random_suffix.disable()
                self.toggle_spec_block_off.disable()
                self.toggle_spec_block_off.hide()
                self.toggle_spec_block_on.enable()
                self.toggle_spec_block_on.show()
                self.suffix_entry_box.set_text("")
                self.suffix_entry_box.rebuild()
                self.suffix_entry_box.disable()
            elif event.ui_element == self.back_button:
                game.switches['window_open'] = False
                game.all_screens['profile screen'].exit_screen()
                game.all_screens['profile screen'].screen_switches()
                self.kill()


class SpecifyCatGender(UIWindow):
    """This window allows the user to specify the cat's gender"""

    def __init__(self, cat):
        super().__init__(scale(pygame.Rect((600, 430), (800, 370))),
                         window_display_title='Change Cat Gender',
                         object_id='#change_cat_gender_window',
                         resizable=False)
        game.switches['window_open'] = True
        self.the_cat = cat
        self.back_button = UIImageButton(
            scale(pygame.Rect((740, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )
        self.heading = pygame_gui.elements.UITextBox(f"-Change {self.the_cat.name}'s Gender-"
                                                     f"<br> You can set this to anything! "
                                                     f"Gender alignment does not affect gameplay.",
                                                     scale(pygame.Rect((20, 20), (760, 150))),
                                                     object_id="#text_box_30_horizcenter_spacing_95",
                                                     manager=MANAGER,
                                                     container=self)

        self.gender_changed = pygame_gui.elements.UITextBox("Gender Changed!",
                                                            scale(pygame.Rect((490, 260), (800, 80))),
                                                            visible=False,
                                                            object_id="#text_box_30_horizleft",
                                                            manager=MANAGER,
                                                            container=self)

        self.done_button = UIImageButton(scale(pygame.Rect((323, 270), (154, 60))), "",
                                         object_id="#done_button",
                                         manager=MANAGER,
                                         container=self)

        self.gender_entry_box = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((200, 180), (400, 60))),
                                                                    placeholder_text=self.the_cat.genderalign,
                                                                    manager=MANAGER,
                                                                    container=self)
        self.set_blocking(True)

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if sub(r'[^A-Za-z0-9 ]+', "", self.gender_entry_box.get_text()) != "":
                    self.the_cat.genderalign = sub(r'[^A-Za-z0-9 ]+', "", self.gender_entry_box.get_text())
                    self.gender_changed.show()
            elif event.ui_element == self.back_button:
                game.switches['window_open'] = False
                game.all_screens['profile screen'].exit_screen()
                game.all_screens['profile screen'].screen_switches()
                self.kill()


class KillCat(UIWindow):
    """This window allows the user to specify the cat's gender"""

    def __init__(self, cat):
        super().__init__(scale(pygame.Rect((600, 400), (900, 400))),
                         window_display_title='Kill Cat',
                         object_id='#change_cat_gender_window',
                         resizable=False)
        self.history = History()
        game.switches['window_open'] = True
        self.the_cat = cat
        self.take_all = False
        self.back_button = UIImageButton(
            scale(pygame.Rect((840, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )
        self.heading = pygame_gui.elements.UITextBox(f"<b>-- How did this cat die? --</b>",
                                                     scale(pygame.Rect((20, 20), (860, 150))),
                                                     object_id="#text_box_30_horizcenter_spacing_95",
                                                     manager=MANAGER,
                                                     container=self)

        self.one_life_check = UIImageButton(scale(pygame.Rect(
            (50, 300), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            tool_tip_text='If this is checked, the leader will lose all their lives',
            manager=MANAGER,
            container=self
        )
        self.all_lives_check = UIImageButton(scale(pygame.Rect(
            (50, 300), (68, 68))),
            "",
            object_id="#checked_checkbox",
            tool_tip_text='If this is checked, the leader will lose all their lives',
            manager=MANAGER,
            container=self
        )

        if self.the_cat.status == 'leader':
            self.done_button = UIImageButton(scale(pygame.Rect((695, 305), (154, 60))), "",
                                             object_id="#done_button",
                                             manager=MANAGER,
                                             container=self)
            self.prompt = 'This cat died when they...'
            self.initial = 'were killed by something unknowable to even StarClan'

            self.all_lives_check.hide()
            self.life_text = pygame_gui.elements.UITextBox('Take all the leader\'s lives',
                                                           scale(pygame.Rect((120, 295), (900, 80))),
                                                           object_id="#text_box_30_horizleft",
                                                           manager=MANAGER,
                                                           container=self)
            self.beginning_prompt = pygame_gui.elements.UITextBox(self.prompt,
                                                                  scale(pygame.Rect((50, 60), (900, 80))),
                                                                  object_id="#text_box_30_horizleft",
                                                                  manager=MANAGER,
                                                                  container=self)

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(scale(pygame.Rect((50, 130), (800, 150))),
                                                                      initial_text=self.initial,
                                                                      object_id="text_entry_line",
                                                                      manager=MANAGER,
                                                                      container=self)

        else:
            self.initial = 'It was the will of something even mightier than StarClan that this cat died.'
            self.prompt = None
            self.all_lives_check.hide()
            self.one_life_check.hide()

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(scale(pygame.Rect((50, 110), (800, 150))),
                                                                      initial_text=self.initial,
                                                                      object_id="text_entry_line",
                                                                      manager=MANAGER,
                                                                      container=self)

            self.done_button = UIImageButton(scale(pygame.Rect((373, 305), (154, 60))), "",
                                             object_id="#done_button",
                                             manager=MANAGER,
                                             container=self)
        self.set_blocking(True)

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if self.the_cat.status == 'leader':
                    death_message = sub(r"[^A-Za-z0-9<->/()*'&#, ]+", "", self.death_entry_box.get_text())
                    if self.take_all:
                        game.clan.leader_lives -= 10
                    else:
                        game.clan.leader_lives -= 1
                else:
                    death_message = sub(r"[^A-Za-z0-9<->/.()*'&#!?,| ]+", "", self.death_entry_box.get_text())

                self.the_cat.die()
                self.history.add_death_or_scars(self.the_cat, text=death_message, death=True)
                update_sprite(self.the_cat)
                game.switches['window_open'] = False
                game.all_screens['profile screen'].exit_screen()
                game.all_screens['profile screen'].screen_switches()
                self.kill()
            elif event.ui_element == self.all_lives_check:
                self.take_all = False
                self.all_lives_check.hide()
                self.one_life_check.show()
            elif event.ui_element == self.one_life_check:
                self.take_all = True
                self.all_lives_check.show()
                self.one_life_check.hide()
            elif event.ui_element == self.back_button:
                game.switches['window_open'] = False
                game.all_screens['profile screen'].exit_screen()
                game.all_screens['profile screen'].screen_switches()
                self.kill()


class UpdateWindow(UIWindow):
    def __init__(self, last_screen, announce_restart_callback):
        super().__init__(scale(pygame.Rect((500, 400), (600, 320))),
                         window_display_title='Game Over',
                         object_id='#game_over_window',
                         resizable=False)
        self.last_screen = last_screen
        self.update_message = UITextBoxTweaked(
            f"Update in progress.",
            scale(pygame.Rect((40, 20), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self
        )
        self.announce_restart_callback = announce_restart_callback

        self.step_text = UITextBoxTweaked(
            f"Downloading update...",
            scale(pygame.Rect((40, 80), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self
        )

        self.progress_bar = UIUpdateProgressBar(
            scale(pygame.Rect((40, 130), (520, 70))),
            self.step_text,
            object_id="progress_bar",
            container=self,
        )

        self.update_thread = threading.Thread(target=self_update, daemon=True, args=(
            UpdateChannel(get_version_info().release_channel), self.progress_bar, announce_restart_callback))
        self.update_thread.start()

        self.cancel_button = UIImageButton(
            scale(pygame.Rect((400, 230), (156, 60))),
            "",
            object_id="#cancel_button",
            container=self
        )

        self.cancel_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.cancel_button:
                self.kill()


class AnnounceRestart(UIWindow):
    def __init__(self, last_screen):
        super().__init__(scale(pygame.Rect((500, 400), (600, 180))),
                         window_display_title='Game Over',
                         object_id='#game_over_window',
                         resizable=False)
        self.last_screen = last_screen
        self.announce_message = UITextBoxTweaked(
            f"The game will automatically restart in 3...",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self
        )

        threading.Thread(target=self.update_text, daemon=True).start()

    def update_text(self):
        for i in range(2, 0, -1):
            time.sleep(1)
            self.announce_message.set_text(f"The game will automatically restart in {i}...")


class UpdateAvailablePopup(UIWindow):
    def __init__(self, last_screen, show_checkbox: bool = False):
        super().__init__(scale(pygame.Rect((400, 400), (800, 460))),
                         window_display_title='Update available',
                         object_id='#game_over_window',
                         resizable=False)
        self.set_blocking(True)
        game.switches['window_open'] = True
        self.last_screen = last_screen

        self.begin_update_title = UIImageButton(
            scale(pygame.Rect((195, 30), (400, 81))),
            "",
            object_id="#new_update_button",
            container=self
        )

        latest_version_number = "{:.16}".format(get_latest_version_number())
        current_version_number = "{:.16}".format(get_version_info().version_number)

        self.game_over_message = UITextBoxTweaked(
            f"<strong>Update to ClanGen {latest_version_number}</strong>",
            scale(pygame.Rect((20, 160), (800, -1))),
            line_spacing=.8,
            object_id="#update_popup_title",
            container=self
        )

        self.game_over_message = UITextBoxTweaked(
            f"Your current version: {current_version_number}",
            scale(pygame.Rect((22, 200), (800, -1))),
            line_spacing=.8,
            object_id="#text_box_current_version",
            container=self
        )

        self.game_over_message = UITextBoxTweaked(
            f"Install update now?",
            scale(pygame.Rect((20, 262), (400, -1))),
            line_spacing=.8,
            object_id="#text_box_30",
            container=self
        )

        self.box_unchecked = UIImageButton(scale(pygame.Rect((15, 366), (68, 68))), "", object_id="#unchecked_checkbox",
                                           container=self)
        self.box_checked = UIImageButton(scale(pygame.Rect((15, 366), (68, 68))), "", object_id="#checked_checkbox",
                                         container=self)
        self.box_text = UITextBoxTweaked(
            f"Don't ask again",
            scale(pygame.Rect((78, 370), (250, -1))),
            line_spacing=.8,
            object_id="#text_box_30",
            container=self
        )

        self.continue_button = UIImageButton(
            scale(pygame.Rect((556, 370), (204, 60))),
            "",
            object_id="#continue_button_small",
            container=self
        )

        self.cancel_button = UIImageButton(
            scale(pygame.Rect((374, 370), (156, 60))),
            "",
            object_id="#cancel_button",
            container=self
        )

        self.close_button = UIImageButton(
            scale(pygame.Rect((740, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )

        if show_checkbox:
            self.box_unchecked.enable()
            self.box_checked.hide()
        else:
            self.box_checked.hide()
            self.box_unchecked.hide()
            self.box_text.hide()

        self.continue_button.enable()
        self.cancel_button.enable()
        self.close_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.continue_button:
                game.switches['window_open'] = False
                self.x = UpdateWindow(game.switches['cur_screen'], self.announce_restart_callback)
                self.kill()
            elif event.ui_element == self.close_button or event.ui_element == self.cancel_button:
                game.switches['window_open'] = False
                self.kill()
            elif event.ui_element == self.box_unchecked:
                self.box_unchecked.disable()
                self.box_unchecked.hide()
                self.box_checked.enable()
                self.box_checked.show()
                with open(f"{get_cache_dir()}/suppress_update_popup", 'w') as write_file:
                    write_file.write(get_latest_version_number())
            elif event.ui_element == self.box_checked:
                self.box_checked.disable()
                self.box_checked.hide()
                self.box_unchecked.enable()
                self.box_unchecked.show()
                if os.path.exists(f"{get_cache_dir()}/suppress_update_popup"):
                    os.remove(f"{get_cache_dir()}/suppress_update_popup")

    def announce_restart_callback(self):
        self.x.kill()
        y = AnnounceRestart(game.switches['cur_screen'])
        y.update(1)


class ChangelogPopup(UIWindow):
    def __init__(self, last_screen):
        super().__init__(scale(pygame.Rect((300, 300), (1000, 800))),
                         window_display_title='Changelog',
                         object_id='#game_over_window',
                         resizable=False)
        self.set_blocking(True)
        game.switches['window_open'] = True
        self.last_screen = last_screen
        self.changelog_popup_title = UITextBoxTweaked(
            f"<strong>What's New</strong>",
            scale(pygame.Rect((40, 20), (960, -1))),
            line_spacing=1,
            object_id="#changelog_popup_title",
            container=self
        )

        current_version_number = "{:.16}".format(get_version_info().version_number)

        self.changelog_popup_subtitle = UITextBoxTweaked(
            f"Version {current_version_number}",
            scale(pygame.Rect((40, 70), (960, -1))),
            line_spacing=1,
            object_id="#changelog_popup_subtitle",
            container=self
        )

        self.scrolling_container = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((20, 130), (960, 650))),
            container=self,
            manager=MANAGER)

        with open("changelog.txt", "r") as read_file:
            file_cont = read_file.read()

        self.changelog_text = UITextBoxTweaked(
            f"{file_cont}",
            scale(pygame.Rect((0, 0), (900, -1))),
            object_id="#text_box_30",
            line_spacing=.8,
            container=self.scrolling_container,
            manager=MANAGER)

        self.changelog_text.disable()

        self.close_button = UIImageButton(
            scale(pygame.Rect((940, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            starting_height=2,
            container=self
        )

        self.scrolling_container.set_scrollable_area_dimensions(
            (self.changelog_text.relative_rect.width, self.changelog_text.relative_rect.height))

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.close_button:
                game.switches['window_open'] = False
                self.kill()


class RelationshipLog(UIWindow):
    """This window allows the user to see the relationship log of a certain relationship."""

    def __init__(self, relationship, disable_button_list, hide_button_list):
        super().__init__(scale(pygame.Rect((546, 245), (1010, 1100))),
                         window_display_title='Relationship Log',
                         object_id='#relationship_log_window',
                         resizable=False)
        game.switches['window_open'] = True
        self.hide_button_list = hide_button_list
        for button in self.hide_button_list:
            button.hide()

        self.exit_button = UIImageButton(
            scale(pygame.Rect((940, 15), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        self.log_icon = UIImageButton(scale(pygame.Rect((445, 808), (68, 68))), "", object_id="#log_icon")
        self.closing_buttons = [self.exit_button, self.back_button, self.log_icon]

        self.disable_button_list = disable_button_list
        for button in self.disable_button_list:
            button.disable()

        if game.settings["fullscreen"]:
            img_path = "resources/images/spacer.png"
        else:
            img_path = "resources/images/spacer_small.png"

        opposite_log_string = None
        if not relationship.opposite_relationship:
            relationship.link_relationship()
        if relationship.opposite_relationship and len(relationship.opposite_relationship.log) > 0:
            opposite_log_string = f"{f'<br><img src={img_path}><br>'.join(relationship.opposite_relationship.log)}<br>"

        log_string = f"{f'<br><img src={img_path}><br>'.join(relationship.log)}<br>" if len(relationship.log) > 0 else\
            "There are no relationship logs."
        
        if not opposite_log_string:
            self.log = pygame_gui.elements.UITextBox(log_string,
                                                     scale(pygame.Rect((30, 70), (953, 850))),
                                                     object_id="#text_box_30_horizleft",
                                                     manager=MANAGER,
                                                     container=self)
        else:
            self.log = pygame_gui.elements.UITextBox(log_string,
                                                     scale(pygame.Rect((30, 70), (953, 500))),
                                                     object_id="#text_box_30_horizleft",
                                                     manager=MANAGER,
                                                     container=self)
            self.opp_heading = pygame_gui.elements.UITextBox("<u><b>OTHER PERSPECTIVE</b></u>",
                                                     scale(pygame.Rect((30, 550), (953, 560))),
                                                     object_id="#text_box_30_horizleft",
                                                     manager=MANAGER,
                                                     container=self)
            self.opp_heading.disable()
            self.opp_log = pygame_gui.elements.UITextBox(opposite_log_string,
                                                     scale(pygame.Rect((30, 610), (953, 465))),
                                                     object_id="#text_box_30_horizleft",
                                                     manager=MANAGER,
                                                     container=self)

        self.set_blocking(True)

    def closing_process(self):
        """Handles to enable and kill all processes when a exit button is clicked."""
        game.switches['window_open'] = False
        for button in self.disable_button_list:
            button.enable()
        for button in self.hide_button_list:
            button.show()
            button.enable()
        self.log_icon.kill()
        self.exit_button.kill()
        self.back_button.kill()
        self.kill()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.closing_buttons:
                self.closing_process()
                

class SaveError(UIWindow):
    def __init__(self, error_text):
        super().__init__(scale(pygame.Rect((300, 300), (1000, 800))),
                         window_display_title='Changelog',
                         object_id='#game_over_window',
                         resizable=False)
        self.set_blocking(True)
        game.switches['window_open'] = True
        self.changelog_popup_title = pygame_gui.elements.UITextBox(
            f"<strong>Saving Failed!</strong>\n\n{error_text}",
            scale(pygame.Rect((40, 20), (890, 750))),
            object_id="#text_box_30",
            container=self
        )

        self.close_button = UIImageButton(
            scale(pygame.Rect((940, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            starting_height=2,
            container=self
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.close_button:
                game.switches['window_open'] = False
                self.kill()