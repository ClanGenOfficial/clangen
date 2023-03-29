
from .base_screens import Screens

import pygame_gui.elements
import pygame
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked

from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.utility import get_text_box_theme, scale

from scripts.mods.resources import pyg_img_load, mod_open
from scripts.mods.mods import modlist


class ModScreen(Screens):
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
                for page in self.moveup_buttons:
                    if event.ui_element in page:
                        modlist.move_up(self.mod_name[self.page][page.index(
                                event.ui_element)])
                        self.change_screen('mod screen')
                        return
                for page in self.movedown_buttons:
                    if event.ui_element in page:
                        modlist.move_down(self.mod_name[self.page][page.index(
                                event.ui_element)])

                        self.change_screen('mod screen')
                        return

                for page in self.mod_buttons:
                    if event.ui_element in page:
                        modlist.toggle_mod(
                            self.mod_name[self.page][page.index(
                                event.ui_element)])
                        self.change_screen('mod screen')

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.main_menu.kill()
        del self.main_menu
        self.info.kill()
        del self.info

        # del self.screen  # No need to keep that in memory.

        for page in self.mod_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list

        for page in self.moveup_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list
        
        for page in self.movedown_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list

        self.next_page_button.kill()
        del self.next_page_button
        self.previous_page_button.kill()
        del self.previous_page_button
        self.page_number.kill()
        del self.page_number

        self.mod_buttons = [[]]
        self.moveup_buttons = [[]]
        self.movedown_buttons = [[]]
        self.mod_name = [[]]

    def screen_switches(self):
        """
        TODO: DOCS
        """
        self.screen = pygame.transform.scale(
            pyg_img_load(
                "resources/images/yourmods.png").convert_alpha(),
            (440 / 1600 * screen_x, 750 / 1400 * screen_y))
        self.main_menu = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))),
                                       "",
                                       object_id="#main_menu_button",
                                       manager=MANAGER)
        self.info = pygame_gui.elements.UITextBox(
            'Note: The list of mods installed! You can change the priority here, and toggle them.',  # pylint: disable=line-too-long
            scale(pygame.Rect((200, 1200), (1200, 140))),
            object_id=get_text_box_theme(),
            manager=MANAGER)

        self.mod_buttons = [[]]
        self.mod_name = [[]]
        self.moveup_buttons = [[]]
        self.movedown_buttons = [[]]

        i = 0
        y_pos = 378
        for mod in modlist.mods:
            self.mod_name[-1].append(mod)
            if mod in modlist.get_mods():
                self.mod_buttons[-1].append(
                    pygame_gui.elements.UIButton(scale(
                        pygame.Rect((600, y_pos), (400, 78))),
                                                 mod,
                                                 object_id="#saved_clan",
                                                 manager=MANAGER))
            else:
                self.mod_buttons[-1].append(
                    pygame_gui.elements.UIButton(scale(
                        pygame.Rect((600, y_pos), (400, 78))),
                                                 mod[1:],
                                                 object_id="#disabled_mod",
                                                 manager=MANAGER))
            self.moveup_buttons[-1].append(
                UIImageButton(scale(pygame.Rect((940, y_pos), (50, 38))),
                              "",
                              object_id="#arrow_up",
                              manager=MANAGER,
                              starting_height=2))
            if modlist.mods.index(mod) == 0:
                self.moveup_buttons[-1][-1].disable()
            self.movedown_buttons[-1].append(
                UIImageButton(scale(pygame.Rect((940, y_pos + 40), (50, 38))),
                              "",
                              object_id="#arrow_down",
                              manager=MANAGER,
                              starting_height=3))
            if modlist.mods.index(mod) == len(modlist.mods) - 1:
                self.movedown_buttons[-1][-1].disable()

            y_pos += 82
            i += 1
            if i >= 8:
                self.mod_buttons.append([])
                self.mod_name.append([])
                self.moveup_buttons.append([])
                self.movedown_buttons.append([])
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
            object_id=get_text_box_theme(),
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

        if self.page >= len(self.mod_buttons) - 1:
            self.next_page_button.disable()
        else:
            self.next_page_button.enable()

        self.page_number.set_text(
            f"Page {self.page + 1} of {len(self.mod_buttons)}")

        for page in self.mod_buttons:
            for button in page:
                button.hide()
        for page in self.moveup_buttons:
            for button in page:
                button.hide()

        for button in self.mod_buttons[self.page]:
            button.show()

        for button in self.moveup_buttons[self.page]:
            button.show()

    def on_use(self):
        """
        TODO: DOCS
        """
        screen.blit(self.screen,
                    (580 / 1600 * screen_x, 300 / 1400 * screen_y))