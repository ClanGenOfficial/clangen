import pygame
from math import ceil
from random import choice, randint
import pygame_gui

from .base_screens import Screens, cat_profiles

from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UISpriteButton, UIImageButton
from scripts.utility import get_text_box_theme, update_sprite, get_living_cat_count
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import *


class ClanScreen(Screens):
    max_sprites_displayed = 400  # we don't want 100,000 sprites rendering at once. 400 is enough.
    cat_buttons = []

    def on_use(self):
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))

        '''verdana.text("Leader\'s Den", game.clan.cur_layout['leader den'])
        verdana.text('Medicine Cat Den', game.clan.cur_layout['medicine den'])
        verdana.text('Nursery', game.clan.cur_layout['nursery'])
        verdana.text('Clearing', game.clan.cur_layout['clearing'])
        verdana.text("Apprentices\' Den",
                     game.clan.cur_layout['apprentice den'])
        verdana.text("Warriors\' Den", game.clan.cur_layout['warrior den'])
        verdana.text("Elders\' Den", game.clan.cur_layout['elder den'])'''

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.save_button:
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_settings()
                game.switches['saved_clan'] = True
                self.update_buttons_and_text()
            if event.ui_element in self.cat_buttons:
                # print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                # print(game.switches["cat"])
                # print(game.switches["cat"])
                # print(event.ui_element.return_cat_id())
                self.change_screen('profile screen')
            if event.ui_element == self.label_toggle:
                if game.settings['den labels']:
                    game.settings['den labels'] = False
                else:
                    game.settings['den labels'] = True
                self.update_buttons_and_text()
            else:
                self.menu_button_pressed(event)

    def screen_switches(self):
        cat_profiles()
        self.update_camp_bg()
        game.switches['cat'] = None
        self.choose_cat_postions()

        self.set_disabled_menu_buttons(["clan_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_menu_buttons()

        # Den Labels
        # Redo the locations, so that it uses layout on the clan page
        self.warrior_den_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout["warrior den"], (121, 28)),
                                                             image_cache.load_image('resources/images/warrior_den.png'))
        self.leader_den_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout["leader den"], (112, 28)),
                                                            image_cache.load_image('resources/images/leader_den.png'))
        self.med_den_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout["medicine den"], (151, 28)),
                                                         image_cache.load_image('resources/images/med_den.png'))
        self.elder_den_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout["elder den"], (103, 28)),
                                                           image_cache.load_image('resources/images/elder_den.png'))
        self.nursery_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout['nursery'], (80, 28)),
                                                         image_cache.load_image('resources/images/nursery_den.png'))
        self.clearing_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout['clearing'], (81, 28)),
                                                          image_cache.load_image('resources/images/clearing.png'))
        self.app_den_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout['apprentice den'], (147, 28)),
                                                         image_cache.load_image('resources/images/app_den.png'))

        # Draw the toggle and text
        self.label_toggle = UIImageButton(pygame.Rect((25, 641), (34, 34)), "", object_id="#checked_checkbox")
        self.show_den_text = pygame_gui.elements.UITextBox("<font color=#000000>Show Den Labels</font>",
                                                           pygame.Rect((60, 647), (145, 25)),
                                                           object_id="#save_text_box")

        # Creates and places the cat sprites.
        self.cat_buttons = []  # To contain all the buttons.

        # We have to convert the postions to something pygame_gui buttons will understand
        # This should be a temp solution. We should change the code that determines postions.
        i = 0
        for x in game.clan.clan_cats:
            if not Cat.all_cats[x].dead and Cat.all_cats[x].in_camp and \
                    not Cat.all_cats[x].exiled and not Cat.all_cats[x].outside:

                i += 1
                if i > self.max_sprites_displayed:
                    break

                self.cat_buttons.append(
                    UISpriteButton(pygame.Rect(tuple(Cat.all_cats[x].placement), (50, 50)), Cat.all_cats[x].sprite,
                                   cat_id=x)
                )

        self.save_button = UIImageButton(pygame.Rect(((343, 625), (114, 30))), "", object_id="#save_button")

        self.save_text = pygame_gui.elements.UITextBox("", pygame.Rect(320, 660, 160, 20),
                                                       object_id="#save_text_box")
        self.update_buttons_and_text()

        if get_living_cat_count(Cat) == 0:
            GameOver('events screen')

    def exit_screen(self):
        # removes the cat sprites.
        for button in self.cat_buttons:
            button.kill()
        self.cat_buttons = []

        # Kill all other elements, and destroy the reference so they aren't hanging around
        self.save_button.kill()
        del self.save_button
        self.save_text.kill()
        del self.save_text
        self.warrior_den_label.kill()
        del self.warrior_den_label
        self.leader_den_label.kill()
        del self.leader_den_label
        self.med_den_label.kill()
        del self.med_den_label
        self.elder_den_label.kill()
        del self.elder_den_label
        self.nursery_label.kill()
        del self.nursery_label
        self.clearing_label.kill()
        del self.clearing_label
        self.app_den_label.kill()
        del self.app_den_label
        self.label_toggle.kill()
        del self.label_toggle
        self.show_den_text.kill()
        del self.show_den_text

    def update_camp_bg(self):
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        camp_bg_base_dir = 'resources/images/camp_bg/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        camp_nr = game.clan.camp_bg

        if camp_nr is None:
            camp_nr = 'camp1'
            game.clan.camp_bg = camp_nr

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:
            platform_dir = f'{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png'
            all_backgrounds.append(platform_dir)

        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[0]).convert(), (800, 700))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (800, 700))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (800, 700))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (800, 700))

    def choose_cat_postions(self):
        '''Determines the postions of cat on the clan screen.'''
        p = game.clan.cur_layout
        if game.clan.leader:
            game.clan.leader.placement = choice(p['leader place'])
        # prevent error if the clan has no medicine cat (last medicine cat is now a warrior)
        if game.clan.medicine_cat:
            game.clan.medicine_cat.placement = choice(p['medicine place'])
        for x in game.clan.clan_cats:
            i = randint(0, 20)
            if Cat.all_cats[x].status == 'apprentice':
                if i < 13:
                    Cat.all_cats[x].placement = choice([
                        choice(p['apprentice place']),
                        choice(p['clearing place'])
                    ])

                elif i >= 19:
                    Cat.all_cats[x].placement = choice(p['leader place'])
                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['warrior place']),
                        choice(p['elder place']),
                        choice(p['medicine place'])
                    ])

            elif Cat.all_cats[x].status == 'deputy':
                if i < 17:
                    Cat.all_cats[x].placement = choice([
                        choice(p['warrior place']),
                        choice(p['leader place']),
                        choice(p['clearing place'])
                    ])

                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['leader place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

            elif Cat.all_cats[x].status == 'elder':
                Cat.all_cats[x].placement = choice(p['elder place'])
            elif Cat.all_cats[x].status == 'kitten':
                if i < 13:
                    Cat.all_cats[x].placement = choice(
                        p['nursery place'])
                elif i == 19:
                    Cat.all_cats[x].placement = choice(p['leader place'])
                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['clearing place']),
                        choice(p['warrior place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

            elif Cat.all_cats[x].status in [
                'medicine cat apprentice', 'medicine cat'
            ]:
                Cat.all_cats[x].placement = choice(p['medicine place'])
            elif Cat.all_cats[x].status == 'warrior':
                if i < 15:
                    Cat.all_cats[x].placement = choice([
                        choice(p['warrior place']),
                        choice(p['clearing place'])
                    ])

                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['leader place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

    def update_buttons_and_text(self):
        if game.switches['saved_clan']:
            self.save_text.set_text("<font color=#006600>Saved!</font>")
        else:
            self.save_text.set_text("Remember to save!")

        self.label_toggle.kill()
        if game.settings['den labels']:
            self.label_toggle = UIImageButton(pygame.Rect((25, 641), (34, 34)), "", object_id="#checked_checkbox")
            self.warrior_den_label.show()
            self.clearing_label.show()
            self.nursery_label.show()
            self.app_den_label.show()
            self.leader_den_label.show()
            self.med_den_label.show()
            self.elder_den_label.show()
        else:
            self.label_toggle = UIImageButton(pygame.Rect((25, 641), (34, 34)), "", object_id="#unchecked_checkbox")
            self.warrior_den_label.hide()
            self.clearing_label.hide()
            self.nursery_label.hide()
            self.app_den_label.hide()
            self.leader_den_label.hide()
            self.med_den_label.hide()
            self.elder_den_label.hide()


class StarClanScreen(Screens):
    list_page = 1
    display_cats = []
    cat_names = []
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.page_number = None
        self.previous_page_button = None
        self.next_page_button = None
        self.dark_forest_button = None
        self.starclan_button = None
        self.dead_cats = None
        self.filter_age = None
        self.filter_rank = None
        self.filter_by_open = None
        self.filter_by_closed = None
        self.starclan_bg = pygame.transform.scale(
            pygame.image.load("resources/images/starclanbg.png").convert(),
            (800, 700))
        self.search_bar_image = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.dark_forest_button:
                self.change_screen('dark forest screen')
            elif event.ui_element in self.display_cats:
                # print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                # print(event.ui_element.return_cat_id())
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
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_rank:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "rank"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            else:
                self.menu_button_pressed(event)

    def exit_screen(self):
        self.hide_menu_buttons()
        self.starclan_button.kill()
        self.dark_forest_button.kill()
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

    def get_dead_cats(self):
        self.dead_cats = [game.clan.instructor] if not game.clan.instructor.df else []
        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.outside and not the_cat.df and \
                    not the_cat.faded:
                self.dead_cats.append(the_cat)

    def screen_switches(self):
        # Determine the dead, non-exiled cats.
        cat_profiles()
        self.get_dead_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((421, 142), (147, 23)),
                                                              object_id="#search_entry_box")

        self.starclan_button = UIImageButton(pygame.Rect((150, 135), (34, 34)), "", object_id="#starclan_button")
        self.starclan_button.disable()
        self.dark_forest_button = UIImageButton(pygame.Rect((115, 135), (34, 34)), "", object_id="#dark_forest_button")
        self.next_page_button = UIImageButton(pygame.Rect((456, 595), (34, 34)), "", object_id="#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595), (34, 34)), "", object_id="#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((340, 595),
                                                                         (110, 30)))  # Text will be filled in later

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("StarClan")
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
        self.page_number = pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + str(self.list_page) + "/" +
                                                         str(self.all_pages) + "</font>",
                                                         pygame.Rect((340, 595), (110, 30)))

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
                    UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y), (50, 50)), cat.sprite, cat.ID))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + name + "</font>"
                                                                    ,
                                                                    pygame.Rect((80 + pos_x, 230 + pos_y), (150, 30))))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):
        bg = self.starclan_bg

        # Only update the positions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(bg, (0, 0))

        screen.blit(ListScreen.search_bar, (348, 135))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class DFScreen(Screens):
    list_page = 1
    display_cats = []
    cat_names = []
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.all_pages = None
        self.current_listed_cats = None
        self.page_number = None
        self.previous_page_button = None
        self.next_page_button = None
        self.dark_forest_button = None
        self.starclan_button = None
        self.dead_cats = None
        self.filter_age = None
        self.filter_rank = None
        self.filter_by_open = None
        self.filter_by_closed = None
        self.df_bg = pygame.transform.scale(
            pygame.image.load("resources/images/darkforestbg.png").convert(),
            (800, 700))
        self.search_bar_image = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.starclan_button:
                self.change_screen('starclan screen')
            elif event.ui_element in self.display_cats:
                # print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                # print(event.ui_element.return_cat_id())
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
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_rank:
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "rank"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            else:
                self.menu_button_pressed(event)

    def exit_screen(self):
        self.hide_menu_buttons()
        self.starclan_button.kill()
        self.dark_forest_button.kill()
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

    def get_dead_cats(self):
        self.dead_cats = [game.clan.instructor] if game.clan.instructor.df else []

        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.exiled and the_cat.df and \
                    not the_cat.faded:
                self.dead_cats.append(the_cat)

    def screen_switches(self):
        # Determine the dead, non-exiled cats.
        cat_profiles()
        self.get_dead_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((421, 142), (147, 23)),
                                                              object_id="#search_entry_box")

        self.starclan_button = UIImageButton(pygame.Rect((150, 135), (34, 34)), "", object_id="#starclan_button")
        self.dark_forest_button = UIImageButton(pygame.Rect((115, 135), (34, 34)), "", object_id="#dark_forest_button")
        self.dark_forest_button.disable()
        self.next_page_button = UIImageButton(pygame.Rect((456, 595), (34, 34)), "", object_id="#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595), (34, 34)), "", object_id="#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((340, 595),
                                                                         (110, 30)))  # Text will be filled in later

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("Dark Forest")
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
        self.page_number = pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + str(self.list_page) + "/" +
                                                         str(self.all_pages) + "</font>",
                                                         pygame.Rect((340, 595), (110, 30)))

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
                self.display_cats.append(
                    UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y), (50, 50)), cat.sprite, cat.ID))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + name + "</font>"
                                                                    ,
                                                                    pygame.Rect((80 + pos_x, 230 + pos_y), (150, 30))))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):
        bg = self.df_bg
        screen.blit(bg, (0, 0))

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(bg, (0, 0))

        screen.blit(ListScreen.search_bar, (348, 135))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class ListScreen(Screens):
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20
    list_page = 1
    display_cats = []
    cat_names = []

    search_bar = pygame.transform.scale(pygame.image.load("resources/images/search_bar.png").convert_alpha(),
                                        (228, 34))
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.filter_age = None
        self.filter_rank = None
        self.filter_by_open = None
        self.filter_by_closed = None
        self.page_number = None
        self.previous_page_button = None
        self.next_page_button = None
        self.outside_clan_button = None
        self.your_clan_button = None
        self.filter_container = None
        self.living_cats = None
        self.all_pages = None
        self.current_listed_cats = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.outside_clan_button:
                self.change_screen("other screen")
            elif event.ui_element in self.display_cats:
                # print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                # print(event.ui_element.return_cat_id())
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
            if not the_cat.dead and not the_cat.outside:
                self.living_cats.append(the_cat)

    def screen_switches(self):
        # Determine the living, non-exiled cats.
        cat_profiles()
        self.get_living_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((421, 142), (147, 23)),
                                                              object_id="#search_entry_box")

        self.your_clan_button = UIImageButton(pygame.Rect((115, 135), (34, 34)), "", object_id="#your_clan_button")
        self.your_clan_button.disable()
        self.outside_clan_button = UIImageButton(pygame.Rect((149, 135), (34, 34)), "",
                                                 object_id="#outside_clan_button")
        self.next_page_button = UIImageButton(pygame.Rect((456, 595), (34, 34)), "", object_id="#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595), (34, 34)), "", object_id="#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((340, 595), (110, 30)),
                                                         object_id=get_text_box_theme())  # Text will be filled in later

        self.set_disabled_menu_buttons(["list_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_menu_buttons()
        self.update_search_cats("")  # This will list all the cats, and create the button objects.

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
        """Run this function when the search text changes, or when the screen is switched to."""
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

        self.page_number.set_text(str(self.list_page) + "/" + str(self.all_pages))

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
                self.display_cats.append(
                    UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y), (50, 50)),
                                   cat.sprite,
                                   cat.ID,
                                   starting_height=0))

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

        screen.blit(ListScreen.search_bar, (348, 135))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class AllegiancesScreen(Screens):
    allegiance_list = []

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        pass

    def screen_switches(self):
        # Heading
        self.heading = pygame_gui.elements.UITextBox(f'{game.clan.name}Clan Allegiances',
                                                     pygame.Rect((30, 110), (400, 40)),
                                                     object_id=get_text_box_theme("#allegiances_header_text_box"))

        # Set Menu Buttons.
        self.show_menu_buttons()
        self.set_disabled_menu_buttons(["allegiances"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.allegiance_list = []

        living_cats = []
        # Determine the living cats.
        for the_cat in Cat.all_cats.values():
            if not the_cat.dead and not the_cat.outside:
                living_cats.append(the_cat)
        living_meds = []
        for the_cat in Cat.all_cats.values():
            if the_cat.status == 'medicine cat' and not the_cat.dead \
                    and not the_cat.outside:
                living_meds.append(the_cat)

        # Pull the clan leaders
        leader = []
        if game.clan.leader is not None:
            if not game.clan.leader.dead and not game.clan.leader.outside:
                self.allegiance_list.append([
                    '<b><u>LEADER</u></b>',
                    f"{str(game.clan.leader.name)} - a {game.clan.leader.describe_cat()}"
                ])

                if len(game.clan.leader.apprentice) > 0:
                    if len(game.clan.leader.apprentice) == 1:
                        self.allegiance_list.append([
                            '', '      Apprentice: ' +
                                str(Cat.fetch_cat(game.clan.leader.apprentice[0]).name)
                        ])
                    else:
                        app_names = ''
                        for app in game.clan.leader.apprentice:
                            app_names += str(Cat.fetch_cat(app).name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        # deputy
        if game.clan.deputy is not None and not game.clan.deputy.dead and not game.clan.deputy.outside:
            self.allegiance_list.append([
                '<b><u>DEPUTY</u></b>',
                f"{str(game.clan.deputy.name)} - a {game.clan.deputy.describe_cat()}"
            ])

            if len(game.clan.deputy.apprentice) > 0:
                if len(game.clan.deputy.apprentice) == 1:
                    self.allegiance_list.append([
                        '', '      Apprentice: ' +
                            str(Cat.fetch_cat(game.clan.deputy.apprentice[0]).name)
                    ])
                else:
                    app_names = ''
                    for app in game.clan.deputy.apprentice:
                        app_names += str(Cat.fetch_cat(app).name) + ', '
                    self.allegiance_list.append(
                        ['', '      Apprentices: ' + app_names[:-2]])
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'medicine cat', '<b><u>MEDICINE CATS</u></b>')
        queens = []
        for living_cat_ in living_cats:
            if str(living_cat_.status
                   ) == 'kitten' and living_cat_.parent1 is not None:
                if Cat.all_cats[living_cat_.parent1].gender == 'male':
                    if living_cat_.parent2 is None or Cat.all_cats[
                        living_cat_.parent2].gender == 'male':
                        queens.append(living_cat_.parent1)
                else:
                    queens.append(living_cat_.parent1)
        cat_count = 0
        for living_cat__ in living_cats:
            if str(
                    living_cat__.status
            ) == 'warrior' and living_cat__.ID not in queens and not living_cat__.outside:
                if not cat_count:
                    self.allegiance_list.append([
                        '<b><u>WARRIORS</u></b>',
                        f"{str(living_cat__.name)} - a {living_cat__.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{str(living_cat__.name)} - a {living_cat__.describe_cat()}"
                    ])
                if len(living_cat__.apprentice) >= 1:
                    if len(living_cat__.apprentice) == 1:
                        self.allegiance_list.append([
                            '', '      Apprentice: ' +
                                str(Cat.fetch_cat(living_cat__.apprentice[0]).name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat__.apprentice:
                            app_names += str(Cat.fetch_cat(app).name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
                cat_count += 1
        if not cat_count:
            self.allegiance_list.append(['<b><u>WARRIORS</u></b>', ''])
        cat_count = 0
        for living_cat___ in living_cats:
            if str(living_cat___.status) in [
                'apprentice', 'medicine cat apprentice'
            ]:
                if cat_count == 0:
                    self.allegiance_list.append([
                        '<b><u>APPRENTICES</u></b>',
                        f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"
                    ])
                cat_count += 1
        if not cat_count:
            self.allegiance_list.append(['<b><u>APPRENTICES</u></b>', ''])
        cat_count = 0
        for living_cat____ in living_cats:
            if living_cat____.ID in queens:
                if cat_count == 0:
                    self.allegiance_list.append([
                        '<b><u>QUEENS</u></b>',
                        f"{str(living_cat____.name)} - a {living_cat____.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{str(living_cat____.name)} - a {living_cat____.describe_cat()}"
                    ])
                cat_count += 1
                if len(living_cat____.apprentice) > 0:
                    if len(living_cat____.apprentice) == 1:
                        self.allegiance_list.append([
                            '', '      Apprentice: ' +
                                str(Cat.fetch_cat(living_cat____.apprentice[0]).name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat____.apprentice:
                            app_names += str(Cat.fetch_cat(app).name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if not cat_count:
            self.allegiance_list.append(['<b><u>QUEENS</u></b>', ''])
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'elder', '<b><u>ELDERS</u></b>')
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'kitten', '<b><u>KITS</u></b>')

        # print(self.allegiance_list)

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(pygame.Rect((50, 150), (700, 500)))
        self.ranks_box = pygame_gui.elements.UITextBox("\n".join([i[0] for i in self.allegiance_list]),
                                                       pygame.Rect((0, 0), (150, -1)),
                                                       object_id=get_text_box_theme("#allegiances_box"),
                                                       container=self.scroll_container)
        self.cat_names_box = pygame_gui.elements.UITextBox("\n".join([i[1] for i in self.allegiance_list]),
                                                           pygame.Rect((150, 0), (550, -1)),
                                                           object_id=get_text_box_theme("#allegiances_box"),
                                                           container=self.scroll_container)
        self.scroll_container.set_scrollable_area_dimensions((680, self.cat_names_box.rect[3]))

        self.ranks_box.disable()
        self.cat_names_box.disable()

    def exit_screen(self):
        self.ranks_box.kill()
        self.cat_names_box.kill()
        self.scroll_container.kill()
        del self.ranks_box
        del self.cat_names_box
        del self.scroll_container
        self.heading.kill()
        del self.heading

    # TODO Rename this here and in `screen_switches`
    def _extracted_from_screen_switches_24(self, living_cats, arg1, arg2):
        result = 0
        for living_cat in living_cats:
            if str(living_cat.status) == arg1 and not living_cat.outside:
                if result == 0:
                    self.allegiance_list.append([
                        arg2,
                        f"{str(living_cat.name)} - a {living_cat.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        "",
                        f"{str(living_cat.name)} - a {living_cat.describe_cat()}"
                    ])
                result += 1
                if len(living_cat.apprentice) > 0:
                    if len(living_cat.apprentice) == 1:
                        self.allegiance_list.append([
                            '', '      Apprentice: ' +
                                str(Cat.fetch_cat(living_cat.apprentice[0]).name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat.apprentice:
                            app_names += str(Cat.fetch_cat(app).name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if not result:
            self.allegiance_list.append([arg2, ''])
        return result

# template for dark forest
