# pylint: disable=line-too-long
"""

This file contains:
  The start screen,
  The switch clan screen,
  The settings screen,
  And the statistics screen.



""" # pylint: enable=line-too-long

import platform
import subprocess
import pygame
import os
import traceback
import logging
from html import escape

from .base_screens import Screens

from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UIImageButton
from scripts.utility import get_text_box_theme, scale, quit  # pylint: disable=redefined-builtin
import pygame_gui
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import DeleteCheck
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.game_structure import image_cache
from ..datadir import get_data_dir

try:
    import ujson
except ImportError:
    import json as ujson

logger = logging.getLogger(__name__)

class StartScreen(Screens):
    """
    TODO: DOCS
    """

    def __init__(self, name=None):
        super().__init__(name)
        self.warning_label = None
        self.bg = pygame.image.load("resources/images/menu.png").convert()
        self.bg = pygame.transform.scale(self.bg, (screen_x, screen_y))

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. """
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if platform.system() == 'Darwin':
                subprocess.Popen(["open", "-u", event.link_target])
            elif platform.system() == 'Windows':
                os.system(f"start \"\" {event.link_target}")
            elif platform.system() == 'Linux':
                subprocess.Popen(['xdg-open', event.link_target])
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            screens = {
                self.continue_button: 'clan screen',
                self.switch_clan_button: 'switch clan screen',
                self.new_clan_button: 'make clan screen',
                self.settings_button: 'settings screen',
            }
            if event.ui_element in screens:
                self.change_screen(screens[event.ui_element])
            elif event.ui_element == self.open_data_directory_button:
                if platform.system() == 'Darwin':
                    subprocess.Popen(["open", "-R", get_data_dir()])
                elif platform.system() == 'Windows':
                    os.startfile(get_data_dir())  # pylint: disable=no-member
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', get_data_dir()])
                return
            elif event.ui_element == self.closebtn:
                self.error_box.kill()
                self.error_label.kill()
                self.error_gethelp.kill()
                self.closebtn.kill()
                self.open_data_directory_button.kill()
                game.switches['error_message'] = ''
                game.switches['traceback'] = ''
            elif event.ui_element == self.quit:
                quit(savesettings=False, clearevents=False)

    def on_use(self):
        """
        TODO: DOCS
        """
        # have to blit this manually or else hover input doesn't get read properly
        screen.blit(self.bg, (0, 0))

    def exit_screen(self):
        """
        TODO: DOCS
        """
        # Button murder time.
        self.continue_button.kill()
        self.switch_clan_button.kill()
        self.new_clan_button.kill()
        self.settings_button.kill()
        self.error_label.kill()
        self.warning_label.kill()
        self.quit.kill()
        self.closebtn.kill()

    def screen_switches(self):
        """
        TODO: DOCS
        """
        # Make those unslightly menu button hide away
        self.hide_menu_buttons()
        # Create buttons

        self.continue_button = UIImageButton(scale(
            pygame.Rect((140, 620), (384, 70))),
                                             "",
                                             object_id="#continue_button",
                                             manager=MANAGER)
        self.switch_clan_button = UIImageButton(
            scale(pygame.Rect((140, 710), (384, 70))),
            "",
            object_id="#switch_clan_button",
            manager=MANAGER)
        self.new_clan_button = UIImageButton(scale(
            pygame.Rect((140, 800), (384, 70))),
                                             "",
                                             object_id="#new_clan_button",
                                             manager=MANAGER)
        self.settings_button = UIImageButton(scale(
            pygame.Rect((140, 890), (384, 70))),
                                             "",
                                             object_id="#settings_button",
                                             manager=MANAGER)
        self.quit = UIImageButton(scale(pygame.Rect((140, 980), (384, 70))),
                                  "",
                                  object_id="#quit_button",
                                  manager=MANAGER)

        errorimg = image_cache.load_image(
            'resources/images/errormsg.png').convert_alpha()

        self.error_box = pygame_gui.elements.UIImage(
            scale(pygame.Rect((259, 300), (1180, 802))),
            pygame.transform.scale(errorimg, (1180, 802)),
            manager=MANAGER)

        self.error_box.disable()

        self.error_label = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((275, 370), (770, 720))),
            object_id="#text_box_22_horizleft",
            manager=MANAGER,
            layer_starting_height=3)


        self.error_gethelp = pygame_gui.elements.UITextBox(
            "Please join the Discord server and ask for technical support. " \
            "We\'ll be happy to help! Please include the error message and the traceback below (if available). " \
            '<br><a href="https://discord.gg/clangen">Discord</a>', # pylint: disable=line-too-long
            scale(pygame.Rect((1055, 430), (350, 600))),
            object_id="#text_box_22_horizleft",
            layer_starting_height=3,
            manager=MANAGER
        )

        self.open_data_directory_button = UIImageButton(
            scale(pygame.Rect((1040, 1020), (320, 60))),
            "",
            object_id="#open_data_directory_button",
            manager=MANAGER,
            starting_height=0, # Layer 0 so it's behind the error box
            tool_tip_text="Opens the data directory. "
            "This is where save files "
            "and logs are stored.")


        self.closebtn = UIImageButton(
            scale(pygame.Rect((1386, 430), (44, 44))),
            "",
            object_id="#exit_window_button",
            manager=MANAGER)

        self.error_box.hide()
        self.error_label.hide()
        self.error_gethelp.hide()
        self.open_data_directory_button.hide()
        self.closebtn.hide()

        self.warning_label = pygame_gui.elements.UITextBox(
            "Warning: this game includes some mild descriptions of gore.",
            scale(pygame.Rect((100, 1244), (1400, 60))),
            object_id="#default_dark",
            manager=MANAGER)

        if game.clan is not None and game.switches['error_message'] == '':
            self.continue_button.enable()
            if len(game.switches['clan_list']) > 1:
                self.switch_clan_button.enable()
            else:
                self.switch_clan_button.disable()
        elif game.clan is not None and game.switches['error_message']:
            self.continue_button.disable()
            self.switch_clan_button.enable()
        else:
            self.continue_button.disable()
            self.switch_clan_button.disable()


        if game.switches['error_message']:
            error_text = f"There was an error loading the game: {game.switches['error_message']}"
            if game.switches['traceback']:
                print("Traceback:")
                print(game.switches['traceback'])
                error_text += "<br><br>" + escape("".join(traceback.format_exception(game.switches['traceback'])))  # pylint: disable=line-too-long
            self.error_label.set_text(error_text)
            self.error_box.show()
            self.error_label.show()
            self.error_gethelp.show()
            self.open_data_directory_button.show()
            self.closebtn.show()

        if game.clan is not None:
            key_copy = tuple(Cat.all_cats.keys())
            for x in key_copy:
                if x not in game.clan.clan_cats:
                    game.clan.remove_cat(x)

        # LOAD settings
        game.load_settings()


class SwitchClanScreen(Screens):
    """
    TODO: DOCS
    """

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if game.switches['window_open']:
                pass
            elif event.ui_element == self.main_menu:
                self.change_screen('start screen')
            elif event.ui_element == self.next_page_button:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.page -= 1
                self.update_page()
            else:
                for page in self.delete_buttons:
                    if event.ui_element in page:
                        DeleteCheck(
                            self.change_screen,
                            self.clan_name[self.page][page.index(
                                event.ui_element)])

                        return

                for page in self.clan_buttons:
                    if event.ui_element in page:
                        game.clan.switch_clans(
                            self.clan_name[self.page][page.index(
                                event.ui_element)])

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.main_menu.kill()
        del self.main_menu
        self.info.kill()
        del self.info
        self.current_clan.kill()
        del self.current_clan

        # del self.screen  # No need to keep that in memory.

        for page in self.clan_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list

        for page in self.delete_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list

        self.next_page_button.kill()
        del self.next_page_button
        self.previous_page_button.kill()
        del self.previous_page_button
        self.page_number.kill()
        del self.page_number

        self.clan_buttons = [[]]
        self.delete_buttons = [[]]
        self.clan_name = [[]]

    def screen_switches(self):
        """
        TODO: DOCS
        """
        self.screen = pygame.transform.scale(
            pygame.image.load(
                "resources/images/clan_saves_frame.png").convert_alpha(),
            (440 / 1600 * screen_x, 750 / 1400 * screen_y))
        self.main_menu = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))),
                                       "",
                                       object_id="#main_menu_button",
                                       manager=MANAGER)
        self.info = pygame_gui.elements.UITextBox(
            'Note: This will close the game.\n When you open it next, it should have the new clan.',  # pylint: disable=line-too-long
            scale(pygame.Rect((200, 1200), (1200, 140))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)

        self.current_clan = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((200, 200), (1200, 140))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)
        if game.clan:
            self.current_clan.set_text(
                f"The currently loaded clan is {game.clan.name}Clan")
        else:
            self.current_clan.set_text("There is no clan currently loaded.")

        self.clan_list = game.read_clans()

        self.clan_buttons = [[]]
        self.clan_name = [[]]
        self.delete_buttons = [[]]

        i = 0
        y_pos = 378
        for clan in self.clan_list[1:]:
            self.clan_name[-1].append(clan)
            self.clan_buttons[-1].append(
                pygame_gui.elements.UIButton(scale(
                    pygame.Rect((600, y_pos), (400, 78))),
                                             clan + "Clan",
                                             object_id="#saved_clan",
                                             manager=MANAGER))
            self.delete_buttons[-1].append(
                UIImageButton(scale(pygame.Rect((940, y_pos + 17), (44, 44))),
                              "",
                              object_id="#exit_window_button",
                              manager=MANAGER,
                              starting_height=2))

            y_pos += 82
            i += 1
            if i >= 8:
                self.clan_buttons.append([])
                self.clan_name.append([])
                self.delete_buttons.append([])
                i = 0
                y_pos = 378

        self.next_page_button = UIImageButton(scale(
            pygame.Rect((912, 1080), (68, 68))),
                                              "",
                                              object_id="#arrow_right_button",
                                              manager=MANAGER)
        self.previous_page_button = UIImageButton(
            scale(pygame.Rect((620, 1080), (68, 68))),
            "",
            object_id="#arrow_left_button",
            manager=MANAGER)
        self.page_number = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((680, 1080), (220, 60))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)
        self.page = 0

        self.update_page()

        return super().screen_switches()

    def update_page(self):
        """
        TODO: DOCS
        """

        if self.page == 0:
            self.previous_page_button.disable()
        else:
            self.previous_page_button.enable()

        if self.page >= len(self.clan_buttons) - 1:
            self.next_page_button.disable()
        else:
            self.next_page_button.enable()

        self.page_number.set_text(
            f"Page {self.page + 1} of {len(self.clan_buttons)}")

        for page in self.clan_buttons:
            for button in page:
                button.hide()
        for page in self.delete_buttons:
            for button in page:
                button.hide()

        for button in self.clan_buttons[self.page]:
            button.show()

        for button in self.delete_buttons[self.page]:
            button.show()

    def on_use(self):
        """
        TODO: DOCS
        """
        screen.blit(self.screen,
                    (580 / 1600 * screen_x, 300 / 1400 * screen_y))


with open('resources/gamesettings.json', 'r', encoding='utf-8') as f:
    settings_dict = ujson.load(f)


class SettingsScreen(Screens):
    """
    TODO: DOCS
    """
    text_size = {
        '0': 'small',
        '1': 'medium',
        '2': 'big'
    }  # How text sizes will show up on the screen
    bool = {True: 'Yes', False: 'No', None: 'None'}
    sub_menu = 'general'

    # This is set to the current settings when the screen is opened.
    # All edits are made directly to game.settings, however, when you
    #  leave the screen,game.settings will be reverted based on this variable
    #   However, if settings are saved, edits will also be made to this variable.
    settings_at_open = {}

    # Have the settings been changed since the page was open or since settings were saved?
    settings_changed = False

    # Contains the checkboxes
    checkboxes = {}
    # Contains the text for the checkboxes.
    checkboxes_text = {}

    info_text = ""
    info_text_2 = ""
    with open('resources/credits_text.json', 'r', encoding='utf-8') as f:
        credits_text = ujson.load(f)
    
    after_contrib = False
    for string in credits_text["text"]:
        if string == "{contrib}":
            after_contrib = True
        else:
            if after_contrib:
                info_text_2 += string
                info_text_2 += "<br>"
            else:
                info_text += string
                info_text += "<br>"
    
    contributors_text = ""
    for contributor in credits_text["contrib"]:
        contributors_text += contributor + "<br>"

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if event.link_target == "__contributors":
                print("idfk if its just my vnc but this triggeres twice, remember to account for that")
            else:
                if platform.system() == 'Darwin':
                    subprocess.Popen(["open", "-u", event.link_target])
                elif platform.system() == 'Windows':
                    os.system(f"start \"\" {event.link_target}")
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', event.link_target])
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu_button:
                self.change_screen('start screen')
                return
            if event.ui_element == self.fullscreen_toggle:
                game.switch_setting('fullscreen')
                quit(savesettings=True, clearevents=False)
            elif event.ui_element == self.open_data_directory_button:
                if platform.system() == 'Darwin':
                    subprocess.Popen(["open", "-R", get_data_dir()])
                elif platform.system() == 'Windows':
                    os.startfile(get_data_dir())  # pylint: disable=no-member
                elif platform.system() == 'Linux':
                    try:
                        subprocess.Popen(['xdg-open', get_data_dir()])
                    except OSError:
                        logger.exception("Failed to call to xdg-open.")
                return
            elif event.ui_element == self.save_settings_button:
                self.save_settings()
                game.save_settings()
                self.settings_changed = False
                self.update_save_button()
                return
            elif event.ui_element == self.relation_settings_button:
                self.open_relation_settings()
                return
            elif event.ui_element == self.general_settings_button:
                self.open_general_settings()
                return
            elif event.ui_element == self.info_button:
                self.open_info_screen()
                return
            elif event.ui_element == self.language_button:
                self.open_lang_settings()
            if self.sub_menu in ['general', 'relation', 'language']:
                self.handle_checkbox_events(event)

    def handle_checkbox_events(self, event):
        """
        TODO: DOCS
        """
        if event.ui_element in self.checkboxes.values():
            for key, value in self.checkboxes.items():
                if value == event.ui_element:
                    if self.sub_menu == 'language':
                        game.settings['language'] = key
                    else:
                        game.switch_setting(key)
                    self.settings_changed = True
                    self.update_save_button()
                    self.refresh_checkboxes()
                    if self.sub_menu == 'general' and event.ui_element is self.checkboxes['discord']:
                        if game.settings['discord']:
                            print("Starting Discord RPC")
                            game.rpc = _DiscordRPC("1076277970060185701",
                                                   daemon=True)
                            game.rpc.start()
                            game.rpc.start_rpc.set()
                        else:
                            print("Stopping Discord RPC")
                            game.rpc.close()
                    break

    def screen_switches(self):
        """
        TODO: DOCS
        """
        self.settings_changed = False

        self.general_settings_button = UIImageButton(
            scale(pygame.Rect((200, 200), (300, 60))),
            "",
            object_id="#general_settings_button",
            manager=MANAGER)
        self.relation_settings_button = UIImageButton(
            scale(pygame.Rect((500, 200), (300, 60))),
            "",
            object_id="#relation_settings_button",
            manager=MANAGER)
        self.info_button = UIImageButton(scale(
            pygame.Rect((800, 200), (300, 60))),
                                         "",
                                         object_id="#info_settings_button",
                                         manager=MANAGER)
        self.language_button = UIImageButton(scale(
            pygame.Rect((1100, 200), (300, 60))),
                                             "",
                                             object_id="#lang_settings_button",
                                             manager=MANAGER)
        self.save_settings_button = UIImageButton(
            scale(pygame.Rect((654, 1100), (292, 60))),
            "",
            object_id="#save_settings_button",
            manager=MANAGER)

        self.fullscreen_toggle = UIImageButton(
            scale(pygame.Rect((1234, 50), (316, 72))),
            "",
            object_id="#toggle_fullscreen_button",
            manager=MANAGER,
            tool_tip_text="This will close the game. "
            "When you reopen, fullscreen"
            " will be toggled. ")

        self.open_data_directory_button = UIImageButton(
            scale(pygame.Rect((50, 1290), (356, 60))),
            "",
            object_id="#open_data_directory_button",
            manager=MANAGER,
            tool_tip_text="Opens the data directory. "
            "This is where save files "
            "and logs are stored.")

        self.update_save_button()
        self.main_menu_button = UIImageButton(scale(
            pygame.Rect((50, 50), (305, 60))),
                                              "",
                                              object_id="#main_menu_button",
                                              manager=MANAGER)
        self.sub_menu = 'general'
        self.open_general_settings()

        self.settings_at_open = game.settings.copy()

        self.refresh_checkboxes()

    def update_save_button(self):
        """
        Updates the disabled state the save button
        """
        if not self.settings_changed:
            self.save_settings_button.disable()
        else:
            self.save_settings_button.enable()

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.clear_sub_settings_buttons_and_text()
        self.general_settings_button.kill()
        del self.general_settings_button
        self.relation_settings_button.kill()
        del self.relation_settings_button
        self.info_button.kill()
        del self.info_button
        self.language_button.kill()
        del self.language_button
        self.save_settings_button.kill()
        del self.save_settings_button
        self.main_menu_button.kill()
        del self.main_menu_button
        self.fullscreen_toggle.kill()
        del self.fullscreen_toggle
        self.open_data_directory_button.kill()
        del self.open_data_directory_button

        game.settings = self.settings_at_open

    def save_settings(self):
        """Saves the settings, ensuring that they will be retained when the screen changes."""
        self.settings_at_open = game.settings.copy()

    def open_general_settings(self):
        """Opens and draws general_settings"""
        self.enable_all_menu_buttons()
        self.general_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'general'
        self.save_settings_button.show()

        self.checkboxes_text[
            "container_general"] = pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((0, 440), (1400, 600))), manager=MANAGER)

        n = 0
        for code, desc in settings_dict['general'].items():
            self.checkboxes_text[code] = pygame_gui.elements.UITextBox(
                desc[0],
                scale(pygame.Rect((450, n * 78), (1000, 78))),
                container=self.checkboxes_text["container_general"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER)
            self.checkboxes_text[code].disable()
            n += 1

        self.checkboxes_text[
            "container_general"].set_scrollable_area_dimensions(
                (1360 / 1600 * screen_x, (n * 78 + 80) / 1400 * screen_y))

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Change the general settings of your game here",
            scale(pygame.Rect((200, 320), (1200, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)

        # This is where the actual checkboxes are created. I don't like
        #   how this is separated from the text boxes, but I've spent too much time to rewrite it.
        #   It has to separated because the checkboxes must be updated when settings are changed.
        #   Fix if you want. - keyraven
        self.refresh_checkboxes()

    def open_relation_settings(self):
        """Opens and draws relation_settings"""
        self.enable_all_menu_buttons()
        self.relation_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'relation'
        self.save_settings_button.show()

        self.checkboxes_text[
            "container_relation"] = pygame_gui.elements.UIScrollingContainer(
                scale(pygame.Rect((0, 440), (1400, 600))), manager=MANAGER)

        n = 0
        for code, desc in settings_dict['relation'].items():
            self.checkboxes_text[code] = pygame_gui.elements.UITextBox(
                desc[0],
                scale(pygame.Rect((450, n * 78), (1000, 78))),
                container=self.checkboxes_text["container_relation"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER)
            self.checkboxes_text[code].disable()
            n += 1

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Change the relationship settings of your game here",
            scale(pygame.Rect((200, 320), (1200, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)

        self.refresh_checkboxes()

    def open_info_screen(self):
        """Open's info screen"""
        self.enable_all_menu_buttons()
        self.info_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'info'
        self.save_settings_button.hide()


        self.checkboxes_text['info_container'] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((200, 300), (1220, 1000))), manager=MANAGER)


        self.checkboxes_text['info_text_box'] = pygame_gui.elements.UITextBox(
            self.info_text,
            scale(pygame.Rect((0, 0), (1180, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text['info_container'],
            manager=MANAGER)
        info_rect = self.checkboxes_text['info_text_box'].get_relative_rect()
        self.checkboxes_text['info_text_box'].kill()
        self.checkboxes_text['info_text_box'] = pygame_gui.elements.UITextBox(
            self.info_text,
            info_rect,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text['info_container'],
            manager=MANAGER)

        print(info_rect.bottom)

        self.checkboxes_text['contributors_text_box'] = pygame_gui.elements.UITextBox(
            self.contributors_text,
            scale(pygame.Rect((0, info_rect.bottom*2), (1180, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_secret"),
            container=self.checkboxes_text['info_container'],
            manager=MANAGER)
        contributors_rect = self.checkboxes_text['contributors_text_box'].get_relative_rect()
        self.checkboxes_text['contributors_text_box'].kill()
        self.checkboxes_text['contributors_text_box'] = pygame_gui.elements.UITextBox(
            self.contributors_text,
            contributors_rect,
            object_id=get_text_box_theme("#text_box_30_horizcenter_secret"),
            container=self.checkboxes_text['info_container'],
            manager=MANAGER)
        

        self.checkboxes_text['info_text_box2'] = pygame_gui.elements.UITextBox(
            self.info_text_2,
            scale(pygame.Rect((0, contributors_rect.bottom * 2), (1180, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text['info_container'],
            manager=MANAGER)
        info_rect2 = self.checkboxes_text['info_text_box2'].get_relative_rect()
        self.checkboxes_text['info_text_box2'].kill()
        self.checkboxes_text['info_text_box2'] = pygame_gui.elements.UITextBox(
            self.info_text_2,
            info_rect2,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text['info_container'],
            manager=MANAGER)
        
        self.checkboxes_text['info_container'].set_scrollable_area_dimensions(
            (info_rect2.width, info_rect2.bottom))


    def open_lang_settings(self):
        """Open Language Settings"""
        self.enable_all_menu_buttons()
        self.language_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'language'
        self.save_settings_button.show()

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Change the language of the game here. This has not been implemented yet.",
            scale(pygame.Rect((200, 320), (1200, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)

        self.refresh_checkboxes()

    def refresh_checkboxes(self):
        """
        TODO: DOCS
        """
        # Kill the checkboxes. No mercy here.
        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}

        # CHECKBOXES (ehhh) FOR LANGUAGES
        if self.sub_menu == 'language':
            self.checkboxes['english'] = UIImageButton(
                scale(pygame.Rect((620, 400), (360, 102))),
                "",
                object_id="#english_lang_button",
                manager=MANAGER)
            self.checkboxes['spanish'] = UIImageButton(
                scale(pygame.Rect((620, 502), (360, 74))),
                "",
                object_id="#spanish_lang_button",
                manager=MANAGER)
            self.checkboxes['german'] = UIImageButton(
                scale(pygame.Rect((620, 576), (360, 74))),
                "",
                object_id="#german_lang_button",
                manager=MANAGER)

            if game.settings['language'] == 'english':
                self.checkboxes['english'].disable()
            elif game.settings['language'] == 'spanish':
                self.checkboxes['spanish'].disable()
            elif game.settings['language'] == 'german':
                self.checkboxes['german'].disable()

        else:
            n = 0
            for code, desc in settings_dict[self.sub_menu].items():
                if game.settings[code]:
                    box_type = "#checked_checkbox"
                else:
                    box_type = "#unchecked_checkbox"
                self.checkboxes[code] = UIImageButton(
                    scale(pygame.Rect((340, n * 78), (68, 68))),
                    "",
                    object_id=box_type,
                    container=self.checkboxes_text["container_" +
                                                   self.sub_menu],
                    tool_tip_text=desc[1])
                n += 1

    def clear_sub_settings_buttons_and_text(self):
        """
        TODO: DOCS
        """
        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}
        for text in self.checkboxes_text.values():
            text.kill()
        self.checkboxes_text = {}

    def enable_all_menu_buttons(self):
        """
        TODO: DOCS
        """
        self.general_settings_button.enable()
        self.relation_settings_button.enable()
        self.info_button.enable()
        self.language_button.enable()

    def on_use(self):
        """
        TODO: DOCS
        """


class StatsScreen(Screens):
    """
    TODO: DOCS
    """

    def screen_switches(self):
        """
        TODO: DOCS
        """
        self.set_disabled_menu_buttons(["stats"])
        self.show_menu_buttons()
        self.update_heading_text(f'{game.clan.name}Clan')

        # Determine stats
        living_num = 0
        warriors_num = 0
        app_num = 0
        kit_num = 0
        elder_num = 0
        starclan_num = 0
        medcat_num = 0
        other_num = 0
        for cat in Cat.all_cats.values():
            if not cat.dead and not (cat.outside or cat.exiled):
                living_num += 1
                if cat.status == 'warrior':
                    warriors_num += 1
                elif cat.status in ['apprentice', 'medicine cat apprentice']:
                    app_num += 1
                elif cat.status == 'kitten':
                    kit_num += 1
                elif cat.status == 'elder':
                    elder_num += 1
                elif cat.status == 'medicine cat':
                    medcat_num += 1
            elif (cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']
                  or cat.outside) and not cat.dead:
                other_num += 1
            else:
                starclan_num += 1

        stats_text = f"Number of Living Cats: {living_num}\n\n" + \
                     f"Number of Med. Cats: {medcat_num}\n\n" + \
                     f"Number of Warriors: {warriors_num}\n\n" + \
                     f"Number of Apprentices: {app_num}\n\n" + \
                     f"Number of Kits: {kit_num}\n\n" + \
                     f"Number of Elders: {elder_num}\n\n" + \
                     f"Number of Cats Outside the Clans: {other_num}\n\n" + \
                     f"Number of Dead Cats: {starclan_num}"

        self.stats_box = pygame_gui.elements.UITextBox(
            stats_text,
            scale(pygame.Rect((200, 300), (1200, 1000))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizcenter"))

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.stats_box.kill()
        del self.stats_box

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        """
        TODO: DOCS
        """
