import os
import shutil

import ujson
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
from scripts.game_structure.game_essentials import game, MANAGER, screen_y, screen_x


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
                                                  tool_tip_text=f"Temporarily remove the cat's special suffix, so "
                                                                f"that you can change the hidden suffix beneath",
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


class AdvancedSettings(UIWindow):
    """This window allows the user to access settings within game_config"""

    def __init__(self):
        super().__init__(scale(pygame.Rect((300, 100), (1000, 1200))),
                         window_display_title='Advanced Settings',
                         object_id='#advanced_settings_window',
                         resizable=False)

        self.entry_line2 = None
        self.entry_line1 = None
        self.settings_changed = None
        self.number_of_settings = 0
        self.x_diff = 150

        self.settings_group = {}
        self.checkboxes = {}
        self.settings_text = {}

        game.switches['window_open'] = True

        self.back_button = UIImageButton(
            scale(pygame.Rect((-60, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self
        )
        self.heading = pygame_gui.elements.UITextBox(f"-Advanced Settings!-",
                                                     scale(pygame.Rect((20, 20), (760, 150))),
                                                     object_id="#text_box_30_horizcenter_spacing_95",
                                                     manager=MANAGER,
                                                     container=self)
        self.heading = pygame_gui.elements.UITextBox(f"Please be aware that changing these settings may change the "
                                                     f"game in unpredictable ways. Inputting incorrect information "
                                                     f"could cause the game to crash. If you mess with these "
                                                     f"settings, please do not report any problems you experience as "
                                                     f"a bug. Some of these settings are not given explanation, trial "
                                                     f"and error may be the best way to discover what they do!",
                                                     scale(pygame.Rect((20, 80), (760, 150))),
                                                     object_id="#text_box_30_horizcenter_spacing_95",
                                                     manager=MANAGER,
                                                     container=self)
        self.gender_changed = pygame_gui.elements.UITextBox("Settings Changed!",
                                                            scale(pygame.Rect((490, 260), (800, 80))),
                                                            visible=False,
                                                            object_id="#text_box_30_horizleft",
                                                            manager=MANAGER,
                                                            container=self)

        self.save_settings_button = UIImageButton(
            scale(pygame.Rect((300, -100), (292, 60))),
            "",
            object_id="#save_settings_button",
            manager=MANAGER)

        self.settings_container = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((100, 150), (800, 1000))),
            manager=MANAGER,
            container=self
        )
        with open(r'C:\Users\tkdbl\Documents\GitHub\clangen\resources\game_config.json', 'r', encoding='utf-8') as f:
            game_config = ujson.load(f)

        for value in self.dict_generator(game_config):
            print(value)
            self.create_setting_groups(value)

        for setting_group in self.settings_group:
            group = self.settings_group[setting_group]
            for setting in group:
                self.setting_name_creation(setting)
                if 'True' in group[setting] or 'False' in group[setting]:
                    self.checkbox_creation(setting, group[setting][0])
                elif len(group[setting]) > 2:
                    self.text_entry_box_creation()
                else:
                    self.text_entry_line_creation(setting, group[setting])

        self.settings_container.set_scrollable_area_dimensions(
            (800 / 1600 * screen_x, (self.number_of_settings * 150) / 1400 * screen_y))

        self.set_blocking(True)

    def create_setting_groups(self, setting_list):
        sections = len(setting_list)

        # the biggest group the setting is part of will be the setting group name
        setting_name = setting_list[0]

        # then we need to get the name of the setting itself, we have to account for nested dicts here
        if sections > 3:
            setting_info = " - ".join(setting_list[1:-2])
        else:
            setting_info = setting_list[1]

        # we store this in a dict so that we can generate our UI from it later
        # should generate as something like "setting_group": {"setting_name": ["option1", "option2"]}
        if setting_info not in self.settings_group[setting_name]:
            self.settings_group[setting_name] = {setting_info: [setting_list[-1]]}
        else:
            self.settings_group[setting_name][setting_info].append(setting_list[-1])

    def dict_generator(self, indict, pre=None):
        """
        this is grabbing the game_config dict and separating it all out into lists,
        since the game_config can get pretty deep with nested dicts, this seems the
        best way to gather all the info in an organized format
        :param indict: the dict to be separated
        :param pre: (I don't even know what this does but I haven't needed it
        yet, ngl I copy-pasted this off stack overflow lol)
        :return: a list for each value found
        """
        pre = pre[:] if pre else []
        if isinstance(indict, dict):
            for key, value in indict.items():
                if isinstance(value, dict):
                    for d in self.dict_generator(value, pre + [key]):
                        yield d
                elif isinstance(value, list) or isinstance(value, tuple):
                    for v in value:
                        for d in self.dict_generator(v, pre + [key]):
                            yield d
                else:
                    yield pre + [key, value]
        else:
            yield pre + [indict]

    def setting_name_creation(self, setting_name):
        self.settings_text[self.number_of_settings] = pygame_gui.elements.UITextBox(
            str(setting_name),
            scale(pygame.Rect((450, self.number_of_settings * self.x_diff), (700, 150))),
            container=self.settings_container,
            object_id="#text_box_30_horizleft_pad_0_8",
            manager=MANAGER)

    def checkbox_creation(self, setting_name, default):

        # set if checkbox starts as checked or not
        if default:
            box_type = "#checked_checkbox"
        else:
            box_type = "#unchecked_checkbox"

        # TODO: figure out how to handle comments as tooltips
        self.checkboxes[self.number_of_settings] = UIImageButton(
            scale(pygame.Rect((750, self.number_of_settings * self.x_diff), (68, 68))),
            "",
            object_id=box_type,
            container=self.settings_container)

        self.number_of_settings += 1

    def text_entry_line_creation(self, setting_name, default):
        # TODO: figure out how to handle comments as tooltips

        x_dim = 200

        # handles settings w tuples
        if len(default) > 1:
            x_dim = x_dim / 2

            self.entry_line1[self.number_of_settings] = pygame_gui.elements.UITextEntryLine(
                scale(pygame.Rect((750, self.number_of_settings * self.x_diff), (x_dim, 68))),
                placeholder_text=str(setting_name),
                container=self.settings_container)

            self.entry_line2[self.number_of_settings] = pygame_gui.elements.UITextEntryLine(
                scale(pygame.Rect((750 + x_dim + 5, self.number_of_settings * self.x_diff), (x_dim, 68))),
                placeholder_text=str(setting_name),
                container=self.settings_container)

        # handles settings w just one entry
        else:
            self.entry_line1[self.number_of_settings] = pygame_gui.elements.UITextEntryLine(
                scale(pygame.Rect((750, self.number_of_settings * self.x_diff), (x_dim, 68))),
                placeholder_text=str(setting_name),
                container=self.settings_container)

        self.number_of_settings += 1

    def text_entry_box_creation(self):
        pass

    def update_save_button(self):
        """
        Updates the disabled state the save button
        """
        if not self.settings_changed:
            self.save_settings_button.disable()
        else:
            self.save_settings_button.enable()

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


