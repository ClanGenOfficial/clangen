import logging

import pygame
import pygame_gui

from scripts.clan import Clan
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.ui_elements import UIImageButton
from scripts.game_structure.windows import DeleteCheck
from scripts.utility import get_text_box_theme, scale  # pylint: disable=redefined-builtin
from .Screens import Screens

logger = logging.getLogger(__name__)

class SwitchClanScreen(Screens):
    """
    TODO: DOCS
    """

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

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
        self.show_mute_buttons()
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
            scale(pygame.Rect((680, 1080), (220, 70))),
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