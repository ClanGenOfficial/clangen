import pygame
import pygame_gui
from math import ceil
from scripts.game_structure.image_button import UISpriteButton, UIImageButton
from .base_screens import Screens, cat_profiles

from .base_screens import Screens

from scripts.game_structure.game_essentials import *
from scripts.cat.cats import Cat
import scripts.game_structure.image_cache as image_cache
from ..utility import get_text_box_theme, update_sprite


#from scripts.world import load_map

class OutsideClanScreen(Screens):

    list_page = 1  # Holds the current page
    display_cats = []  # Holds the cat sprite objects
    cat_names = []  # Holds the cat name text-box objects

    search_bar_image = pygame.transform.scale(pygame.image.load(
        "resources/images/search_bar.png").convert_alpha(), (228, 34))
    previous_search_text = ""

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.your_clan_button:
                self.change_screen("list screen")
            elif event.ui_element in self.display_cats:
                game.switches["cat"] = event.ui_element.return_cat_id()
                self.change_screen('profile screen')
            elif event.ui_element == self.next_page_button:
                self.list_page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.list_page -= 1
                self.update_page()
            elif event.ui_element == self.filter_by_closed:
                self.filter_by_closed.hide()
                self.filter_by_open.show()
                self.filter_rank.show()
                self.filter_age.show()
            elif event.ui_element == self.filter_by_open:
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_options_visible = False
                self.filter_rank.hide()
                self.filter_age.hide()
            elif event.ui_element == self.filter_age:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "reverse_age"
                Cat.sort_cats()
                self.get_living_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_rank:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "rank"
                Cat.sort_cats()
                self.get_living_cats()
                self.update_search_cats(self.search_bar.get_text())
            else:
                self.menu_button_pressed(event)

    def get_living_cats(self):
        self.living_cats = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and the_cat.outside:
                self.living_cats.append(the_cat)

    def screen_switches(self):
        # Determine the living, exiled cats.
        self.get_living_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((421, 142), (147, 23)),
                                                              object_id="#search_entry_box")

        self.your_clan_button = UIImageButton(pygame.Rect((115, 135), (34, 34)), "", object_id="#your_clan_button")
        self.outside_clan_button = UIImageButton(pygame.Rect((149, 135),(34, 34)), "", object_id="#outside_clan_button")
        self.outside_clan_button.disable()
        self.next_page_button = UIImageButton(pygame.Rect((456, 595), (34, 34)), "", object_id="#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595), (34, 34)), "", object_id="#arrow_left_button")

        # Text will be filled in later
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((340, 595),(110, 30)))

        self.set_disabled_menu_buttons(["list_screen"])
        self.update_heading_text('<font size=4.0>Cats Outside The Clan</font>')
        self.show_menu_buttons()

        self.update_search_cats("") # This will list all the cats, and create the button objects.

        # set up the filter buttons
        x_pos = 576
        y_pos = 135
        self.filter_by_closed = UIImageButton(
            pygame.Rect((x_pos, y_pos), (98, 34)),
            "",
            object_id="#filter_by_closed_button",
            tool_tip_text="By default, cats are sorted by rank."
        )
        self.filter_by_open = UIImageButton(
            pygame.Rect((x_pos, y_pos), (98, 34)),
            "",
            object_id="#filter_by_open_button",
        )
        self.filter_by_open.hide()
        y_pos -= 29

        self.filter_rank = UIImageButton(
            pygame.Rect((x_pos - 2, y_pos), (102, 29)),
            "",
            object_id="#filter_rank_button",
            starting_height=1
        )
        self.filter_rank.hide()
        y_pos -= 29
        self.filter_age = UIImageButton(
            pygame.Rect((x_pos - 2, y_pos), (102, 29)),
            "",
            object_id="#filter_age_button",
            starting_height=1
        )
        self.filter_age.hide()

        cat_profiles()
    
    def exit_screen(self):
        self.hide_menu_buttons()
        self.your_clan_button.kill()
        self.outside_clan_button.kill()
        self.next_page_button.kill()
        self.previous_page_button.kill()
        self.page_number.kill()
        self.search_bar.kill()
        self.filter_by_closed.kill()
        self.filter_by_open.kill()
        self.filter_rank.kill()
        self.filter_age.kill()

        # Remove currently displayed cats and cat names.
        for cat in self.display_cats:
            cat.kill()
        self.display_cats = []

        for name in self.cat_names:
            name.kill()
        self.cat_names = []
        

    def update_search_cats(self, search_text):
        """ Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        search_text = search_text.strip()
        if search_text != '':
            for cat in self.living_cats:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.living_cats.copy()

        self.all_pages = int(ceil(len(self.current_listed_cats) /
                             20.0)) if len(self.current_listed_cats) > 20 else 1

        self.update_page()

        
    def update_page(self):
        """Run this function when page changes."""
        
        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.list_page > self.all_pages:
            self.list_page = self.all_pages

        # Handle which next buttons are clickable.
        if self.all_pages <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.list_page >= self.all_pages:
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.list_page == 1 and self.all_pages > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()

        self.page_number.kill()
        self.page_number = pygame_gui.elements.UITextBox("<font color='#000000'>" +str(self.list_page) + "/" + 
                                                        str(self.all_pages) + "</font>",
                                                            pygame.Rect((340,595),(110,30)))

        # Remove the images for currently listed cats
        for cat in self.display_cats:
            cat.kill()
        self.display_cats = []

        for name in self.cat_names:
            name.kill()
        self.cat_names = []

        # Generate object for the current cats
        pos_x = 0
        pos_y = 0
        # print(self.current_listed_cats)
        if self.current_listed_cats != []:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y),(50,50)),
                                                        cat.sprite, cat.ID))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox(name,
                                                                    pygame.Rect((80 + pos_x, 230 + pos_y), (150, 30)),
                                                                    object_id=get_text_box_theme()))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(self.search_bar_image, (348, 135))

    def chunks(self, L, n): return [L[x: x+n] for x in range(0, len(L), n)]


class UnknownResScreen(Screens):
    list_page = 1
    display_cats = []
    cat_names = []
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.filter_id = None
        self.page_number = None
        self.previous_page_button = None
        self.next_page_button = None
        self.dark_forest_button = None
        self.unknown_residence_button = None
        self.starclan_button = None
        self.dead_cats = None
        self.filter_age = None
        self.filter_rank = None
        self.filter_by_open = None
        self.filter_by_closed = None
        self.search_bar_image = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.dark_forest_button:
                self.change_screen('dark forest screen')
            elif event.ui_element == self.starclan_button:
                self.change_screen('starclan screen')
            elif event.ui_element == self.next_page_button:
                self.list_page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.list_page -= 1
                self.update_page()
            elif event.ui_element == self.filter_by_closed:
                self.filter_by_closed.hide()
                self.filter_by_open.show()
                self.filter_rank.show()
                self.filter_age.show()
                self.filter_id.show()
            elif event.ui_element == self.filter_by_open:
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_id.hide()
                self.filter_rank.hide()
                self.filter_age.hide()
            elif event.ui_element == self.filter_age:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_id.hide()
                game.sort_type = "reverse_age"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_rank:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_id.hide()
                game.sort_type = "rank"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_id:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_id.hide()
                game.sort_type = "id"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element in self.display_cats:
                # print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                # print(event.ui_element.return_cat_id())
                self.change_screen('profile screen')
            else:
                self.menu_button_pressed(event)

    def exit_screen(self):
        self.hide_menu_buttons()
        self.starclan_button.kill()
        self.unknown_residence_button.kill()
        self.dark_forest_button.kill()
        self.next_page_button.kill()
        self.previous_page_button.kill()
        self.page_number.kill()
        self.search_bar.kill()
        self.filter_by_closed.kill()
        self.filter_by_open.kill()
        self.filter_rank.kill()
        self.filter_age.kill()
        self.filter_id.kill()

        # Remove currently displayed cats and cat names.
        for cat in self.display_cats:
            cat.kill()
        self.display_cats = []

        for name in self.cat_names:
            name.kill()
        self.cat_names = []

    def get_dead_cats(self):
        self.dead_cats = []
        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.faded \
                    and (the_cat.outside or the_cat.exiled):
                self.dead_cats.append(the_cat)

    def screen_switches(self):
        # Determine the dead, non-exiled cats.
        cat_profiles()
        self.get_dead_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((421, 142), (147, 23)),
                                                              object_id="#search_entry_box")

        self.starclan_button = UIImageButton(pygame.Rect((115, 135), (34, 34)), "", object_id="#starclan_button")
        self.unknown_residence_button = UIImageButton(pygame.Rect((149, 135), (34, 34)), "",
                                                      object_id="#unknown_residence_button")
        self.unknown_residence_button.disable()
        self.dark_forest_button = UIImageButton(pygame.Rect((183, 135), (34, 34)), "", object_id="#dark_forest_button")
        self.next_page_button = UIImageButton(pygame.Rect((456, 595), (34, 34)), "", object_id="#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595), (34, 34)), "", object_id="#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((340, 595),
                                                                         (110, 30)))  # Text will be filled in later

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("Unknown Residence")
        self.show_menu_buttons()

        self.update_search_cats("")  # This will list all the cats, and create the button objects.

        x_pos = 576
        y_pos = 135
        self.filter_by_closed = UIImageButton(
            pygame.Rect((x_pos, y_pos), (98, 34)),
            "",
            object_id="#filter_by_closed_button",
            tool_tip_text="By default, cats are sorted by rank."
        )
        self.filter_by_open = UIImageButton(
            pygame.Rect((x_pos, y_pos), (98, 34)),
            "",
            object_id="#filter_by_open_button",
        )
        self.filter_by_open.hide()
        y_pos += 34

        self.filter_rank = UIImageButton(
            pygame.Rect((x_pos - 2, y_pos), (102, 29)),
            "",
            object_id="#filter_rank_button",
            starting_height=2
        )
        self.filter_rank.hide()
        y_pos += 29
        self.filter_age = UIImageButton(
            pygame.Rect((x_pos - 2, y_pos), (102, 29)),
            "",
            object_id="#filter_age_button",
            starting_height=2
        )
        self.filter_age.hide()
        y_pos += 29
        self.filter_id = UIImageButton(
            pygame.Rect((x_pos - 2, y_pos), (102, 29)),
            "",
            object_id="#filter_ID_button",
            starting_height=2
        )
        self.filter_id.hide()

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        search_text = search_text.strip()
        if search_text != '':
            for cat in self.dead_cats:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.dead_cats.copy()

        self.all_pages = int(ceil(len(self.current_listed_cats) /
                                  20.0)) if len(self.current_listed_cats) > 20 else 1

        self.update_page()

    def update_page(self):
        """Run this function when page changes."""

        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.list_page > self.all_pages:
            self.list_page = self.all_pages

        # Handle which next buttons are clickable.
        if self.all_pages <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.list_page >= self.all_pages:
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.list_page == 1 and self.all_pages > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()

        self.page_number.kill()
        self.page_number = pygame_gui.elements.UITextBox(str(self.list_page) + "/" +
                                                         str(self.all_pages),
                                                         pygame.Rect((340, 595), (110, 30)),
                                                         object_id=get_text_box_theme())

        # Remove the images for currently listed cats
        for cat in self.display_cats:
            cat.kill()
        self.display_cats = []

        for name in self.cat_names:
            name.kill()
        self.cat_names = []

        # Generate object for the current cats
        pos_x = 0
        pos_y = 0
        # print(self.current_listed_cats)
        if self.current_listed_cats:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(
                    UISpriteButton(pygame.Rect
                                   ((130 + pos_x, 180 + pos_y), (50, 50)),
                                   cat.sprite,
                                   cat.ID,
                                   starting_height=1))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox(name,
                                                                    pygame.Rect((80 + pos_x, 230 + pos_y), (150, 30)),
                                                                    object_id=get_text_box_theme()))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):
        # Only update the positions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(OutsideClanScreen.search_bar_image, (348, 135))
    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]