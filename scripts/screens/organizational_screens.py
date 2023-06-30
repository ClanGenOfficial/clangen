# pylint: disable=line-too-long
"""

This file contains:
  The start screen,
  The switch clan screen,
  The settings screen,
  And the statistics screen.



"""  # pylint: enable=line-too-long

import logging
import os
import platform
import subprocess
import traceback
from html import escape

import pygame
import pygame_gui
import ujson
from requests.exceptions import RequestException, Timeout

from scripts.cat.cats import Cat
from scripts.clan import Clan
from scripts.game_structure import image_cache
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.windows import DeleteCheck, UpdateAvailablePopup, ChangelogPopup, SaveError
from scripts.utility import get_text_box_theme, scale, quit  # pylint: disable=redefined-builtin
from .base_screens import Screens
from ..housekeeping.datadir import get_data_dir, get_cache_dir
from ..housekeeping.update import has_update, UpdateChannel, get_latest_version_number
from ..housekeeping.version import get_version_info

logger = logging.getLogger(__name__)
has_checked_for_update = False
update_available = False


class StartScreen(Screens):
    """
    TODO: DOCS
    """

    def __init__(self, name=None):
        super().__init__(name)
        self.warning_label = None
        self.bg = pygame.image.load("resources/images/menu.png").convert()
        self.bg = pygame.transform.scale(self.bg, (screen_x, screen_y))
        self.social_buttons = {}

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
                self.continue_button: 'camp screen',
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
                #game.switches['error_message'] = ''
                #game.switches['traceback'] = ''
            elif event.ui_element == self.update_button:
                UpdateAvailablePopup(game.switches['last_screen'])
            elif event.ui_element == self.quit:
                quit(savesettings=False, clearevents=False)
            elif event.ui_element == self.social_buttons['discord_button']:
                if platform.system() == 'Darwin':
                    subprocess.Popen(["open", "-u", "https://discord.gg/clangen"])
                elif platform.system() == 'Windows':
                    os.system(f"start \"\" {'https://discord.gg/clangen'}")
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', "https://discord.gg/clangen"])
            elif event.ui_element == self.social_buttons['tumblr_button']:
                if platform.system() == 'Darwin':
                    subprocess.Popen(["open", "-u", "https://officialclangen.tumblr.com/"])
                elif platform.system() == 'Windows':
                    os.system(f"start \"\" {'https://officialclangen.tumblr.com/'}")
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', "https://officialclangen.tumblr.com/"])
            elif event.ui_element == self.social_buttons['twitter_button']:
                if platform.system() == 'Darwin':
                    subprocess.Popen(["open", "-u", "https://twitter.com/OfficialClangen"])
                elif platform.system() == 'Windows':
                    os.system(f"start \"\" {'https://twitter.com/OfficialClangen'}")
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', "https://twitter.com/OfficialClangen"])
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE) and self.continue_button.is_enabled:
                self.change_screen('camp screen')

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
        self.update_button.kill()
        self.quit.kill()
        self.closebtn.kill()
        for btn in self.social_buttons:
            self.social_buttons[btn].kill()

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

        self.social_buttons["twitter_button"] = UIImageButton(scale(pygame.Rect((25, 1295), (80, 80))),
                                                              "",
                                                              object_id="#twitter_button",
                                                              manager=MANAGER,
                                                              tool_tip_text='Check out our Twitter!')
        self.social_buttons["tumblr_button"] = UIImageButton(scale(pygame.Rect((115, 1295), (80, 80))),
                                                             "",
                                                             object_id="#tumblr_button",
                                                             manager=MANAGER,
                                                             tool_tip_text='Check out our Tumblr!')

        self.social_buttons["discord_button"] = UIImageButton(scale(pygame.Rect((205, 1295), (80, 80))),
                                                              "",
                                                              object_id="#discord_button",
                                                              manager=MANAGER,
                                                              tool_tip_text='Join our Discord!')
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
            starting_height=3)

        self.error_gethelp = pygame_gui.elements.UITextBox(
            "Please join the Discord server and ask for technical support. "
            "We\'ll be happy to help! Please include the error message and the traceback below (if available). "
            '<br><a href="https://discord.gg/clangen">Discord</a>',  # pylint: disable=line-too-long
            scale(pygame.Rect((1055, 430), (350, 600))),
            object_id="#text_box_22_horizleft",
            starting_height=3,
            manager=MANAGER
        )

        self.open_data_directory_button = UIImageButton(
            scale(pygame.Rect((1040, 1020), (356, 60))),
            "",
            object_id="#open_data_directory_button",
            manager=MANAGER,
            starting_height=0,  # Layer 0 so it's behind the error box
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

        self.update_button = UIImageButton(scale(pygame.Rect((1154, 50), (382.5, 75))), "",
                                           object_id="#update_button", manager=MANAGER)
        self.update_button.visible = 0

        try:
            global has_checked_for_update
            global update_available
            if not get_version_info().is_source_build and not get_version_info().is_itch and get_version_info().upstream.lower() == "Thlumyn/clangen".lower() and \
                    game.settings['check_for_updates'] and not has_checked_for_update:
                if has_update(UpdateChannel(get_version_info().release_channel)):
                    update_available = True
                    show_popup = True
                    if os.path.exists(f"{get_cache_dir()}/suppress_update_popup"):
                        with open(f"{get_cache_dir()}/suppress_update_popup", 'r') as read_file:
                            if read_file.readline() == get_latest_version_number():
                                show_popup = False

                    if show_popup:
                        UpdateAvailablePopup(game.switches['last_screen'], show_checkbox=True)

                has_checked_for_update = True

            if update_available:
                self.update_button.visible = 1
        except (RequestException, Timeout):
            logger.exception("Failed to check for update")
            has_checked_for_update = True

        if game.settings['show_changelog']:
            show_changelog = True
            if os.path.exists(f"{get_cache_dir()}/changelog_popup_shown"):
                with open(f"{get_cache_dir()}/changelog_popup_shown") as read_file:
                    if read_file.readline() == get_version_info().version_number:
                        show_changelog = False

            if show_changelog:
                with open(f"{get_cache_dir()}/changelog_popup_shown", 'w') as write_file:
                    write_file.write(get_version_info().version_number)
                ChangelogPopup(game.switches['last_screen'])

        self.warning_label = pygame_gui.elements.UITextBox(
            "Warning: this game includes some mild descriptions of gore, violence, and animal abuse",
            scale(pygame.Rect((100, 1244), (1400, 60))),
            object_id="#default_dark",
            manager=MANAGER)

        
        if game.clan is not None and game.switches['error_message'] == '':
            self.continue_button.enable()
        else:
            self.continue_button.disable()
        
        if len(game.switches['clan_list']) > 1:
            self.switch_clan_button.enable()
        else:
            self.switch_clan_button.disable()

        if game.switches['error_message']:
            error_text = f"There was an error loading the game: {game.switches['error_message']}"
            if game.switches['traceback']:
                print("Traceback:")
                print(game.switches['traceback'])
                error_text += "<br><br>" + escape("".join(
                    traceback.format_exception(game.switches['traceback'], game.switches['traceback'], game.switches[
                        'traceback'].__traceback__)))  # pylint: disable=line-too-long
            self.error_label.set_text(error_text)
            self.error_box.show()
            self.error_label.show()
            self.error_gethelp.show()
            self.open_data_directory_button.show()

            if get_version_info().is_sandboxed:
                self.open_data_directory_button.hide()

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
                        Clan.switch_clans(
                            self.clan_name[self.page][page.index(
                                event.ui_element)])
                        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('start screen')

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
            'Note: This will close the game.\n When you open it next, it should have the new Clan.',
            # pylint: disable=line-too-long
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
                f"The currently loaded Clan is {game.clan.name}Clan")
        else:
            self.current_clan.set_text("There is no Clan currently loaded.")

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

    # contains the tooltips for contributors
    tooltip = {}

    info_text = ""
    tooltip_text = []
    with open('resources/credits_text.json', 'r', encoding='utf-8') as f:
        credits_text = ujson.load(f)
    for string in credits_text["text"]:
        if string == "{contrib}":
            for contributor in credits_text["contrib"]:
                info_text += contributor + "<br>"
                tooltip_text.append(credits_text["contrib"][contributor])
        else:
            info_text += string
            info_text += "<br>"

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
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
                try:
                    game.save_settings()
                except:
                    SaveError(traceback.format_exc())
                    self.change_screen("start screen")
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
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('start screen')
            elif event.key == pygame.K_RIGHT:
                if self.sub_menu == 'general':
                    self.open_relation_settings()
                elif self.sub_menu == 'relation':
                    self.open_info_screen()
                elif self.sub_menu == 'info':
                    self.open_lang_settings()
            elif event.key == pygame.K_LEFT:
                if self.sub_menu == 'relation':
                    self.open_general_settings()
                elif self.sub_menu == 'info':
                    self.open_relation_settings()
                elif self.sub_menu == 'language':
                    self.open_info_screen()

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

                    opens = {
                        "general": self.open_general_settings,
                        "language": self.open_lang_settings,
                        "relation": self.open_relation_settings
                    }

                    scroll_pos = None
                    if "container_general" in self.checkboxes_text and \
                            self.checkboxes_text["container_general"].vert_scroll_bar:
                        scroll_pos = self.checkboxes_text["container_general"].vert_scroll_bar.start_percentage

                    if self.sub_menu in opens:
                        opens[self.sub_menu]()

                    if scroll_pos is not None:
                        self.checkboxes_text["container_general"].vert_scroll_bar.set_scroll_from_start_percentage(
                            scroll_pos)

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

        if game.settings['fullscreen']:
            self.fullscreen_toggle = UIImageButton(
                scale(pygame.Rect((1234, 50), (316, 72))),
                "",
                object_id="#toggle_fullscreen_button",
                manager=MANAGER,
                tool_tip_text="This will close the game. "
                            "When you reopen, the game"
                            " will be windowed. ")
        else:
            self.fullscreen_toggle = UIImageButton(
                scale(pygame.Rect((1234, 50), (316, 72))),
                "",
                object_id="#toggle_fullscreen_button",
                manager=MANAGER,
                tool_tip_text="This will close the game. "
                            "When you reopen, the game"
                            " will be fullscreen. ")

        self.open_data_directory_button = UIImageButton(
            scale(pygame.Rect((50, 1290), (356, 60))),
            "",
            object_id="#open_data_directory_button",
            manager=MANAGER,
            tool_tip_text="Opens the data directory. "
                          "This is where save files "
                          "and logs are stored.")

        if get_version_info().is_sandboxed:
            self.open_data_directory_button.hide()

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

        self.checkboxes_text["info_container"] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((200, 300), (1200, 1000))),
            manager=MANAGER
        )

        self.checkboxes_text['info_text_box'] = pygame_gui.elements.UITextBox(
            self.info_text,
            scale(pygame.Rect((0, 0), (1150, 8000))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.checkboxes_text["info_container"],
            manager=MANAGER)

        self.checkboxes_text['info_text_box'].disable()

        i = 0
        y_pos = 731
        for tooltip in self.tooltip_text:
            if not tooltip:
                self.tooltip[f'tip{i}'] = UIImageButton(
                    scale(pygame.Rect((400, i * 56 + y_pos), (400, 56))),
                    "",
                    object_id="#blank_button",
                    container=self.checkboxes_text["info_container"],
                    manager=MANAGER,
                    starting_height=2
                ),
            else:
                self.tooltip[f'tip{i}'] = UIImageButton(
                    scale(pygame.Rect((400, i * 56 + y_pos), (400, 56))),
                    "",
                    object_id="#blank_button",
                    container=self.checkboxes_text["info_container"],
                    manager=MANAGER,
                    tool_tip_text=tooltip,
                    starting_height=2
                ),

            i += 1
        self.checkboxes_text["info_container"].set_scrollable_area_dimensions(
            (1150 / 1600 * screen_x, (i * 56 + y_pos + 550) / 1400 * screen_y))

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