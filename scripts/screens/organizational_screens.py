import pygame
import os
import shutil

from .base_screens import Screens
from sys import exit

from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UIImageButton
# from scripts.world import save_map
from scripts.utility import get_text_box_theme, scale
import pygame_gui
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import DeleteCheck


class StartScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.warning_label = None
        self.bg = pygame.image.load("resources/images/menu.png").convert()
        self.bg = pygame.transform.scale(self.bg, (screen_x, screen_y))

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.continue_button:
                self.change_screen('clan screen')
            elif event.ui_element == self.switch_clan_button:
                self.change_screen('switch clan screen')
            elif event.ui_element == self.new_clan_button:
                self.change_screen('make clan screen')
            elif event.ui_element == self.settings_button:
                self.change_screen('settings screen')
            elif event.ui_element == self.quit:
                #game.rpc.close()
                pygame.display.quit()
                pygame.quit()
                exit()

    def on_use(self):
        # have to blit this manually or else hover input doesn't get read properly
        screen.blit(self.bg, (0, 0))

    def exit_screen(self):
        # Button murder time.
        self.continue_button.kill()
        self.switch_clan_button.kill()
        self.new_clan_button.kill()
        self.settings_button.kill()
        self.error_label.kill()
        self.warning_label.kill()
        self.quit.kill()

    def screen_switches(self):
        # Make those unslightly menu button hide away
        self.hide_menu_buttons()
        # Create buttons

        self.continue_button = UIImageButton(scale(pygame.Rect((140, 620), (384, 70))), "",
                                             object_id="#continue_button", manager=MANAGER)
        self.switch_clan_button = UIImageButton(scale(pygame.Rect((140, 710), (384, 70))), "",
                                                object_id="#switch_clan_button", manager=MANAGER)
        self.new_clan_button = UIImageButton(scale(pygame.Rect((140, 800), (384, 70))), "",
                                             object_id="#new_clan_button", manager=MANAGER)
        self.settings_button = UIImageButton(scale(pygame.Rect((140, 890), (384, 70))), "",
                                             object_id="#settings_button", manager=MANAGER)
        self.quit = UIImageButton(scale(pygame.Rect((140, 980), (384, 70))), "",
                                  object_id="#quit_button", manager=MANAGER)

        self.error_label = pygame_gui.elements.UILabel(scale(pygame.Rect(100, 100, 1400, -1)), "",
                                                       object_id="#save_text_box", manager=MANAGER)
        self.error_label.hide()

        self.warning_label = pygame_gui.elements.UITextBox(
            "Warning: this game includes some mild descriptions of gore.",
            scale(pygame.Rect((100, 1244), (1400, 60))),
            object_id="#default_dark", manager=MANAGER
        )

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
            # TODO: Switch to another kind of ui element here
            error_text = f"There was an error loading the game: {game.switches['error_message']}"
            self.error_label.set_text(error_text)
            self.error_label.show()

        if game.clan is not None:
            key_copy = tuple(Cat.all_cats.keys())
            for x in key_copy:
                if x not in game.clan.clan_cats:
                    game.clan.remove_cat(x)

        # LOAD settings
        game.load_settings()


class SwitchClanScreen(Screens):

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu:
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
                        DeleteCheck(self.change_screen, self.clan_name[self.page][page.index(event.ui_element)])

                        return

                for page in self.clan_buttons:
                    if event.ui_element in page:
                        game.clan.switch_clans(self.clan_name[self.page][page.index(event.ui_element)])
                

    def exit_screen(self):
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
                del button
        
        for page in self.delete_buttons:
            for button in page:
                button.kill()
                del button

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
        self.screen = pygame.transform.scale(pygame.image.load("resources/images/clan_saves_frame.png").convert_alpha(),
                                             (440 / 1600 * screen_x, 750 / 1400 * screen_y))
        self.main_menu = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                       object_id="#main_menu_button", manager=MANAGER)
        self.info = pygame_gui.elements.UITextBox(
            'Note: This will close the game.\n When you open it next, it should have the new clan.',
            scale(pygame.Rect((200, 1200), (1200, 140))), object_id=get_text_box_theme(), manager=MANAGER)

        self.current_clan = pygame_gui.elements.UITextBox("", scale(pygame.Rect((200, 200), (1200, 140))),
                                                          object_id=get_text_box_theme(), manager=MANAGER)
        if game.clan:
            self.current_clan.set_text(f"The currently loaded clan is {game.clan.name}Clan")
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
                pygame_gui.elements.UIButton(scale(pygame.Rect((600, y_pos), (400, 78))), clan + "Clan",
                                             object_id="#saved_clan", manager=MANAGER))
            self.delete_buttons[-1].append(
                UIImageButton(scale(pygame.Rect((940, y_pos + 17), (44, 44))), "",
                              object_id="#exit_window_button", manager=MANAGER, starting_height=2))

            y_pos += 82
            i += 1
            if i >= 8:
                self.clan_buttons.append([])
                self.clan_name.append([])
                self.delete_buttons.append([])
                i = 0
                y_pos = 378

        self.next_page_button = UIImageButton(scale(pygame.Rect((912, 1080), (68, 68))), "", object_id="#arrow_right_button"
                                              , manager=MANAGER)
        self.previous_page_button = UIImageButton(scale(pygame.Rect((620, 1080), (68, 68))), "",
                                                  object_id="#arrow_left_button", manager=MANAGER)
        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((680, 1080), (220, 60))),
                                                         object_id=get_text_box_theme()
                                                         , manager=MANAGER) 
        self.page = 0

        
        self.update_page()

        return super().screen_switches()

    def update_page(self):

        if self.page == 0:
            self.previous_page_button.disable()
        else:
            self.previous_page_button.enable()

        if self.page >= len(self.clan_buttons) - 1:
            self.next_page_button.disable()
        else:
            self.next_page_button.enable()

        self.page_number.set_text(f"Page {self.page + 1} of {len(self.clan_buttons)}")

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
        screen.blit(self.screen, (580 / 1600 * screen_x, 300 / 1400 * screen_y))
        pass


class SettingsScreen(Screens):
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

    info_text = "<b>Welcome to Warrior Cats clan generator!</b><br><br>" \
                "This is a fan-made generator for the Warrior Cats -book series by Erin Hunter.<br><br>" \
                "You're welcome to use the characters and sprites generated in this program, " \
                "as long as you don't claim the sprites as your own creations or sell them for any reason.<br><br>" \
                "<b>Original creator:</b> <i>just-some-cat.tumblr.com (anju)</i><br><br>" \
                "<b>Fan edit made by:</b> <i>SableSteel</i><br>" \
                "<b>With contributions from:</b><br><i>" \
                "Blackfur<br>" \
                "coffee<br>" \
                "Desmond The Furry<br>" \
                "ikethefifth<br>" \
                "Lixxis<br>" \
                "Ryos<br>" \
                "clayteeth<br>" \
                "CrumbsDeluxe<br>" \
                "Hatsune Miku<br>" \
                "keyraven (key)<br>" \
                "larkgz<br>" \
                "ozzie<br>" \
                "sami(RAYTRAC3R)<br>" \
                "scribble<br>" \
                "Shou<br>" \
                "Tanukigami<br>" \
                "Tiri<br>" \
                "Tybaxel<br>" \
                "MathKangaroo (Victor)<br>" \
                "ZtheCorgi (Zabe)<br>" \
                "Charlie<br>" \
                "green?<br>" \
                "Owanora<br>" \
                "Salix<br>" \
                "Silverstar<br>" \
                "Thrae<br>" \
                "Chase<br>" \
                "wood pank<br>" \
                "grif<br>" \
                "beejeans<br>" \
                "Irony-Dragon<br>" \
                "Kassi (Sophia)<br>" \
                "milly!<br>" \
                "coyotedawn<br>" \
                "paradigox<br>" \
                "Fruit Punk<br>" \
                "ImLvna (Luna)<br>" \
                "clownthoughts<br>" \
                "thyfrankie<br>" \
                "Perrio<br>" \
                "anonn (Nicole)<br>" \
                "catastrophe<br>" \
                "Kittenvy<br>" \
                "SunlitFable<br>" \
                "Hobohime<br></i>" \
                "Thank you to the beta testers and all those who have helped with development.<br><br>" \
                "<b>Thank you for playing!!</b><br><br>" \
                "Code is licensed under <a href=https://www.mozilla.org/en-US/MPL/2.0/>Mozilla Public License Version 2.0</a><br>" \
                "Art is licensed under <a href=https://creativecommons.org/licenses/by-nc/4.0/legalcode>CC-BY-NC 4.0</a> "

    def handle_event(self, event):
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            os.system(f"start \"\" {event.link_target}")
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu_button:
                self.change_screen('start screen')
                return
            if event.ui_element == self.fullscreen_toggle:
                game.switch_setting('fullscreen')
                game.save_settings()
                #game.rpc.close()
                pygame.display.quit()
                pygame.quit()
                exit()
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
            if self.sub_menu == 'general':
                self.handle_general_events(event)
            elif self.sub_menu == 'relation':
                self.handle_relation_events(event)
            elif self.sub_menu == 'language':
                self.handle_lang_events(event)

    def handle_relation_events(self, event):
        if event.ui_element == self.checkboxes['random relation']:
            game.switch_setting('random relation')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['affair']:
            game.switch_setting('affair')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['no gendered breeding']:
            game.switch_setting('no gendered breeding')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['no unknown fathers']:
            game.switch_setting('no unknown fathers')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['romantic with former mentor']:
            game.switch_setting('romantic with former mentor')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['first_cousin_mates']:
            game.switch_setting('first_cousin_mates')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()

    def handle_general_events(self, event):
        if event.ui_element == self.checkboxes['dark mode']:
            game.switch_setting('dark mode')
            self.settings_changed = True
            self.update_save_button()
            self.open_general_settings()
        elif event.ui_element == self.checkboxes['backgrounds']:
            game.switch_setting('backgrounds')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['autosave']:
            game.switch_setting('autosave')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['disasters']:
            game.switch_setting('disasters')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['retirement']:
            game.switch_setting('retirement')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['shaders']:
            game.switch_setting('shaders')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['hotkey display']:
            game.switch_setting('hotkey display')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['deputy']:
            game.switch_setting('deputy')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['fading']:
            game.switch_setting('fading')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['save_faded_copy']:
            game.switch_setting('save_faded_copy')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['gore']:
            game.switch_setting('gore')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['become_mediator']:
            game.switch_setting('become_mediator')
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()

    def handle_lang_events(self, event):
        if event.ui_element == self.checkboxes['english']:
            game.settings['language'] = 'english'
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['spanish']:
            game.settings['language'] = 'spanish'
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()
        elif event.ui_element == self.checkboxes['german']:
            game.settings['language'] = 'german'
            self.settings_changed = True
            self.update_save_button()
            self.refresh_checkboxes()

    def screen_switches(self):
        self.settings_changed = False

        self.general_settings_button = UIImageButton(scale(pygame.Rect((200, 200), (300, 60))),
                                                     "", object_id="#general_settings_button", manager=MANAGER)
        self.relation_settings_button = UIImageButton(scale(pygame.Rect((500, 200), (300, 60))),
                                                      "", object_id="#relation_settings_button", manager=MANAGER)
        self.info_button = UIImageButton(scale(pygame.Rect((800, 200), (300, 60))),
                                         "", object_id="#info_settings_button", manager=MANAGER)
        self.language_button = UIImageButton(scale(pygame.Rect((1100, 200), (300, 60))),
                                             "", object_id="#lang_settings_button", manager=MANAGER)
        self.save_settings_button = UIImageButton(scale(pygame.Rect((654, 1100), (292, 60))),
                                                  "", object_id="#save_settings_button", manager=MANAGER)

        self.fullscreen_toggle = UIImageButton(scale(pygame.Rect((1234, 50), (316, 72))),
                                               "",
                                               object_id="#toggle_fullscreen_button",
                                               manager=MANAGER,
                                               tool_tip_text="This will close the game. "
                                                             "When you reopen, fullscreen"
                                                             " will be toggled. ")

        self.update_save_button()
        self.main_menu_button = UIImageButton(scale(pygame.Rect((50, 50), (305, 60))),
                                              "", object_id="#main_menu_button", manager=MANAGER)
        self.sub_menu = 'general'
        self.open_general_settings()

        self.settings_at_open = game.settings.copy()

        self.refresh_checkboxes()

    def update_save_button(self):
        """Updates the disabled state the save button"""
        if not self.settings_changed:
            self.save_settings_button.disable()
        else:
            self.save_settings_button.enable()

    def exit_screen(self):
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

        # Text_boxes:
        # For consistency's sake, use the name of the setting as the key for the
        #   checkbox text and checkbox
        x_value = 450
        y_spacing = 78
        n = 0

        self.checkboxes_text["container"] = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((0, 440),
                                                                                                       (1400, 600))),
                                                                                     manager=MANAGER)

        self.checkboxes_text['dark mode'] = pygame_gui.elements.UITextBox(
            "Dark Mode", scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['backgrounds'] = pygame_gui.elements.UITextBox(
            "Enable Clan page background", scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['autosave'] = pygame_gui.elements.UITextBox(
            "Automatically save every five moons", scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['disasters'] = pygame_gui.elements.UITextBox(
            "Allow mass extinction events", scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['retirement'] = pygame_gui.elements.UITextBox(
            "Cats will never retire due to a permanent condition",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['shaders'] = pygame_gui.elements.UITextBox(
            "Enable Shaders", scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['hotkey display'] = pygame_gui.elements.UITextBox(
            "Display hotkeys on text buttons -- NOT IMPLEMENTED",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        n += 1
        self.checkboxes_text['deputy'] = pygame_gui.elements.UITextBox(
            "Allow leaders to automatically choose a new deputy",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )

        n += 1
        self.checkboxes_text['fading'] = pygame_gui.elements.UITextBox(
            "Allow dead cats to fade away",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )

        n += 1
        self.checkboxes_text['fade_copy'] = pygame_gui.elements.UITextBox(
            "Save a complete copy of faded cats information",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )

        n += 1
        self.checkboxes_text['become_mediator'] = pygame_gui.elements.UITextBox(
            "Allow warriors and elders to choose to become mediators",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )

        n += 1
        self.checkboxes_text['gore'] = pygame_gui.elements.UITextBox(
            "Allow mild gore and blood in patrol artwork",
            scale(pygame.Rect((x_value, n * y_spacing), (1000, 78))),
            container=self.checkboxes_text["container"],
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )

        # This makes sure scrolling works properly.
        for box in self.checkboxes_text:
            if box != "container":
                self.checkboxes_text[box].disable()

        self.checkboxes_text["container"].set_scrollable_area_dimensions(
            (1360 / 1600 * screen_x, (n * y_spacing + 80) / 1400 * screen_y))

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Change the general settings of your game here", scale(pygame.Rect((200, 320), (1200, 100))),
            object_id=get_text_box_theme(), manager=MANAGER)

        # This is where the acual checkboxes are created. I don't like
        #   how this is seperated from the text boxes, but I've spent too much time to rewrite it. 
        #   It has to seperated becuase the checkboxes must be updated when settings are changed. 
        #   Fix if you want. - keyraven
        self.refresh_checkboxes()

    def open_relation_settings(self):
        """Opens and draws relation_settings"""
        self.enable_all_menu_buttons()
        self.relation_settings_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'relation'
        self.save_settings_button.show()

        x_value = 450
        self.checkboxes_text['random relation'] = pygame_gui.elements.UITextBox(
            "Randomize relationship values when creating clan",
            scale(pygame.Rect((x_value, 440), (1000, 100))),
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        self.checkboxes_text['affair'] = pygame_gui.elements.UITextBox(
            "Allow affairs and mate switches based on relationships",
            scale(pygame.Rect((x_value, 518), (1000, 100))),
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        self.checkboxes_text['no gendered breeding'] = pygame_gui.elements.UITextBox(
            "Allow couples to birth kittens despite same-sex status",
            scale(pygame.Rect((x_value, 596), (1200, 100))),
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        self.checkboxes_text['no unknown fathers'] = pygame_gui.elements.UITextBox(
            "Allow unmated cats to have offspring",
            scale(pygame.Rect((x_value, 674), (1000, 100))),
            object_id=get_text_box_theme("#setting_text_box"), manager=MANAGER
        )
        self.checkboxes_text['romantic with former mentor'] = pygame_gui.elements.UITextBox(
            "Allow romantic interactions with former apprentices/mentor",
            scale(pygame.Rect((x_value, 752), (1000, 100))), object_id=get_text_box_theme("#setting_text_box"),
            manager=MANAGER
        )
        self.checkboxes_text['first_cousin_mates'] = pygame_gui.elements.UITextBox(
            "Allow first cousins to become mates/have romantic interactions",
            scale(pygame.Rect((x_value, 830), (1000, 100))), object_id=get_text_box_theme("#setting_text_box"),
            manager=MANAGER
        )

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Change the relationship settings of your game here",
            scale(pygame.Rect((200, 320), (1200, 100))), object_id=get_text_box_theme(), manager=MANAGER)

        self.refresh_checkboxes()

    def open_info_screen(self):
        """Open's info screen"""
        self.enable_all_menu_buttons()
        self.info_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'info'
        self.save_settings_button.hide()

        self.checkboxes_text['info_text_box'] = pygame_gui.elements.UITextBox(self.info_text,
                                                                              scale(pygame.Rect((200, 300),
                                                                                                (1200, 1000))),
                                                                              object_id=get_text_box_theme(),
                                                                              manager=MANAGER)

    def open_lang_settings(self):
        """Open Language Settings"""
        self.enable_all_menu_buttons()
        self.language_button.disable()
        self.clear_sub_settings_buttons_and_text()
        self.sub_menu = 'language'
        self.save_settings_button.show()

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Change the language of the game here. This has not been implemented yet.",
            scale(pygame.Rect((200, 320), (1200, 100))), object_id=get_text_box_theme(), manager=MANAGER)

        self.refresh_checkboxes()

    def refresh_checkboxes(self):

        # Kill the checkboxes. No mercy here.
        for checkbox in self.checkboxes:
            self.checkboxes[checkbox].kill()
        self.checkboxes = {}

        # Checkboxes for GENERAL SETTINGS #############################################
        if self.sub_menu == 'general':
            # Dark mode
            x_value = 340
            y_spacing = 78
            n = 0

            if game.settings['dark mode']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['dark mode'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text='Camp backgrounds will match with the mode: '
                              'nighttime for Dark mode and daytime for Light mode.'
            )
            n += 1
            # Enable clan page background
            if game.settings['backgrounds']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['backgrounds'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text='Even with this off, the camp you choose will still affect the events you encounter.'
            )

            n += 1
            # Automatically save every five moons
            if game.settings['autosave']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['autosave'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                container=self.checkboxes_text["container"], manager=MANAGER,
                object_id=box_type
            )

            n += 1
            # Allow mass extinction events
            if game.settings['disasters']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['disasters'] = UIImageButton \
                (scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                 "",
                 object_id=box_type,
                 container=self.checkboxes_text["container"], manager=MANAGER,
                 tool_tip_text='This may result in up to 1/3rd of your Clan dying in one moon.'
                 )

            n += 1
            # Cats will never retire due to a permanent condition
            if game.settings['retirement']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['retirement'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text='When this setting is off, cats with permanent conditions will choose whether or not '
                              'they want to retire. '
            )

            n += 1
            # Enable Shaders
            if game.settings['shaders']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['shaders'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text='This will add a shading layer onto the cat sprites.'
            )

            n += 1
            # Display hotkeys on text buttons -- NOT IMPLEMENTED
            if game.settings['hotkey display']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['hotkey display'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                container=self.checkboxes_text["container"], manager=MANAGER,
                object_id=box_type,
            )

            n += 1
            # Allow leaders to automatically choose a new deputy
            if game.settings['deputy']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['deputy'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text="The warrior code rules will be taken into account when choosing a deputy."
            )

            n += 1
            # Allow cats to fade
            if game.settings['fading']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['fading'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text="After 202 moons, dead cats will be unloaded, and saved separately. "
                              "No family relations will be lost."
            )

            n += 1
            # Allow cats to fade
            if game.settings['save_faded_copy']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['save_faded_copy'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text="A complete copy of faded cat save info will be saved in plain-text."
            )

            n += 1
            # Allow cats to become mediators
            if game.settings['become_mediator']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['become_mediator'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"], manager=MANAGER,
                tool_tip_text="Warriors and elders will have a chance to become mediators upon timeskip."
            )

            n += 1
            # Allow gorey patrol images
            if game.settings['gore']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['gore'] = UIImageButton(
                scale(pygame.Rect((x_value, n * y_spacing), (68, 68))),
                "",
                object_id=box_type,
                container=self.checkboxes_text["container"],
                tool_tip_text="Mild gore and blood will be allowed in the artwork displayed alongside patrols."
            )


        # CHECKBOXES FOR RELATION SETTINGS #################################################################
        elif self.sub_menu == 'relation':
            x_value = 340
            # Randomize relationship values when creating clan
            if game.settings['random relation']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['random relation'] = UIImageButton(
                scale(pygame.Rect((x_value, 440), (68, 68))),
                "",
                object_id=box_type, manager=MANAGER,
                tool_tip_text="Clan founder cats will start the game with established relationships."
            )
            # Allow affairs and mate switches based on relationship
            if game.settings['affair']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['affair'] = UIImageButton(
                scale(pygame.Rect((x_value, 518), (68, 68))),
                "",
                object_id=box_type, manager=MANAGER,
                tool_tip_text="Cats may have kits before mating regardless of the Un-mated Cat Offspring setting."
            )

            # Allow couples to have kittens despite same-sex status
            if game.settings['no gendered breeding']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['no gendered breeding'] = UIImageButton(
                scale(pygame.Rect((x_value, 596), (68, 68))),
                "",
                object_id=box_type, manager=MANAGER,
                tool_tip_text="A cat's biological sex will no longer be a constraining factor for pregnancies."
            )
            # Allow unmated cats to have offspring
            if game.settings['no unknown fathers']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['no unknown fathers'] = UIImageButton(
                scale(pygame.Rect((x_value, 674), (68, 68))),
                "",
                object_id=box_type, manager=MANAGER,
                tool_tip_text="This setting will not affect the Affairs setting."
            )
            # Allow romantic interactions with former apprentices/mentor
            if game.settings['romantic with former mentor']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['romantic with former mentor'] = UIImageButton(scale(pygame.Rect((x_value, 752), (68, 68))),
                                                                           "",
                                                                           object_id=box_type, manager=MANAGER)
            # Allow romantic interations with first cousins:
            if game.settings['first_cousin_mates']:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"
            self.checkboxes['first_cousin_mates'] = UIImageButton(scale(pygame.Rect((x_value, 830), (68, 68))), "",
                                                                  object_id=box_type, manager=MANAGER)

        # CHECKBOXES (ehhh) FOR LANGUAGES
        elif self.sub_menu == 'language':
            self.checkboxes['english'] = UIImageButton(scale(pygame.Rect((620, 400), (360, 102))), "",
                                                       object_id="#english_lang_button", manager=MANAGER)
            self.checkboxes['spanish'] = UIImageButton(scale(pygame.Rect((620, 502), (360, 74))), "",
                                                       object_id="#spanish_lang_button", manager=MANAGER)
            self.checkboxes['german'] = UIImageButton(scale(pygame.Rect((620, 576), (360, 74))), "",
                                                      object_id="#german_lang_button", manager=MANAGER)

            if game.settings['language'] == 'english':
                self.checkboxes['english'].disable()
            elif game.settings['language'] == 'spanish':
                self.checkboxes['spanish'].disable()
            elif game.settings['language'] == 'german':
                self.checkboxes['german'].disable()

    def clear_sub_settings_buttons_and_text(self):
        for checkbox in self.checkboxes:
            self.checkboxes[checkbox].kill()
        self.checkboxes = {}
        for text in self.checkboxes_text:
            self.checkboxes_text[text].kill()
        self.checkboxes_text = {}

    def enable_all_menu_buttons(self):
        self.general_settings_button.enable()
        self.relation_settings_button.enable()
        self.info_button.enable()
        self.language_button.enable()

    def on_use(self):
        pass


class StatsScreen(Screens):

    def screen_switches(self):
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
            elif (cat.status in ['kittypet', 'loner', 'rogue'] or cat.outside) and not cat.dead:
                other_num+=1
            else:
                starclan_num += 1

        stats_text = "Number of Living Cats: " + str(living_num) + "\n\n" + \
                     "Number of Med. Cats: " + str(medcat_num) + "\n\n" + \
                     "Number of Warriors: " + str(warriors_num) + "\n\n" + \
                     "Number of Apprentices: " + str(app_num) + "\n\n" + \
                     "Number of Kits: " + str(kit_num) + "\n\n" + \
                     "Number of Elders: " + str(elder_num) + "\n\n" + \
                     "Number of Cats Outside the Clans: " + str(other_num) + "\n\n" + \
                     "Number of Dead Cats: " + str(starclan_num)

        self.stats_box = pygame_gui.elements.UITextBox(stats_text, scale(pygame.Rect((200, 300), (1200, 1000))),
                                                       manager=MANAGER,
                                                       object_id=get_text_box_theme())

    def exit_screen(self):
        self.stats_box.kill()
        del self.stats_box

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        pass
