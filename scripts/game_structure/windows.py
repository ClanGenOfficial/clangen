import os
import shutil

from pygame_gui.elements import UIWindow
import pygame
import pygame_gui
from sys import exit
from re import sub

from scripts.cat.names import Name

from scripts.datadir import get_save_dir
from scripts.game_structure import image_cache
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.utility import scale, quit
from scripts.game_structure.game_essentials import game, MANAGER


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
                self.prefix_entry_box.set_text(Name(self.the_cat.status,
                                                    None,
                                                    self.the_cat.name.suffix,
                                                    self.the_cat.pelt.colour,
                                                    self.the_cat.eye_colour,
                                                    self.the_cat.pelt.name,
                                                    self.the_cat.tortiepattern,
                                                    specsuffix_hidden=
                                                    (self.the_cat.name.status in self.the_cat.name.names_dict[
                                                        "special_suffixes"])).prefix)
            elif event.ui_element == self.random_suffix:
                self.suffix_entry_box.set_text(Name(self.the_cat.status,
                                                    self.the_cat.name.prefix,
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
