import pygame
from math import ceil
from random import choice, randint
import pygame_gui

from .base_screens import Screens, cat_profiles

from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UISpriteButton, UIImageButton
from scripts.utility import get_text_box_theme, update_sprite, get_living_cat_count, get_med_cats
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import *
from .cat_screens import ProfileScreen
from ..conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled


class ClanScreen(Screens):
    max_sprites_displayed = 400  # we don't want 100,000 sprites rendering at once. 400 is enough.
    cat_buttons = []

    def __init__(self, name=None):
        super().__init__(name)
        self.show_den_text = None
        self.label_toggle = None
        self.app_den_label = None
        self.clearing_label = None
        self.nursery_label = None
        self.elder_den_label = None
        self.med_den_label = None
        self.leader_den_label = None
        self.warrior_den_label = None

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
            if event.ui_element == self.med_den_label:
                self.change_screen('med den screen')
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
        self.warrior_den_label = pygame_gui.elements.UIImage(
            pygame.Rect(game.clan.cur_layout["warrior den"], (121, 28)),
            image_cache.load_image('resources/images/warrior_den.png'))
        self.leader_den_label = pygame_gui.elements.UIImage(pygame.Rect(game.clan.cur_layout["leader den"], (112, 28)),
                                                            image_cache.load_image('resources/images/leader_den.png'))
        self.med_den_label = UIImageButton(pygame.Rect(
            game.clan.cur_layout["medicine den"], (151, 28)),
            "",
            object_id="#med_den_button"
        )
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

        # We have to convert the positions to something pygame_gui buttons will understand
        # This should be a temp solution. We should change the code that determines positions.
        i = 0
        for x in game.clan.clan_cats:
            if not Cat.all_cats[x].dead and Cat.all_cats[x].in_camp and \
                    not Cat.all_cats[x].exiled and not Cat.all_cats[x].outside:

                i += 1
                if i > self.max_sprites_displayed:
                    break

                try:
                    self.cat_buttons.append(
                        UISpriteButton(pygame.Rect(tuple(Cat.all_cats[x].placement), (50, 50)), Cat.all_cats[x].sprite,
                                       cat_id=x)
                    )
                except:
                    print(f"Error placing {str(Cat.all_cats[x].name)}\'s sprite on Clan page")

        self.save_button = UIImageButton(pygame.Rect(((343, 625), (114, 30))), "", object_id="#save_button")

        self.save_text = pygame_gui.elements.UITextBox("", pygame.Rect(320, 660, 160, 20),
                                                       object_id="#save_text_box")
        self.update_buttons_and_text()

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
        """Determines the postions of cat on the clan screen."""
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
        if self.current_listed_cats:
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


class MedDenScreen(Screens):
    cat_buttons = {}
    conditions_hover = {}
    cat_names = []

    def __init__(self, name=None):
        super().__init__(name)
        self.log_box = None
        self.log_title = None
        self.log_tab = None
        self.cats_tab = None
        self.hurt_sick_title = None
        self.display_med = None
        self.med_cat = None
        self.minor_tab = None
        self.out_den_tab = None
        self.in_den_tab = None
        self.injured_and_sick_cats = None
        self.minor_cats = None
        self.out_den_cats = None
        self.in_den_cats = None
        self.meds_messages = None
        self.current_med = None
        self.cat_bg = None
        self.last_page = None
        self.next_page = None
        self.last_med = None
        self.next_med = None
        self.den_base = None
        self.med_info = None
        self.med_name = None
        self.current_page = None
        self.meds = None
        self.back_button = None
        self.profile_screen = ProfileScreen()

        self.tab_showing = self.in_den_tab
        self.tab_list = self.in_den_cats

        self.herbs = {}

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('clan screen')
            elif event.ui_element == self.next_med:
                self.current_med += 1
                self.update_med_cat()
            elif event.ui_element == self.last_med:
                self.current_med -= 1
                self.update_med_cat()
            elif event.ui_element == self.next_page:
                self.current_page += 1
                self.update_sick_cats()
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                self.update_sick_cats()
            elif event.ui_element == self.in_den_tab:
                self.in_den_tab.disable()
                self.tab_showing.enable()
                self.tab_list = self.in_den_cats
                self.tab_showing = self.in_den_tab
                self.update_sick_cats()
            elif event.ui_element == self.out_den_tab:
                self.tab_showing.enable()
                self.tab_list = self.out_den_cats
                self.tab_showing = self.out_den_tab
                self.out_den_tab.disable()
                self.update_sick_cats()
            elif event.ui_element == self.minor_tab:
                self.tab_showing.enable()
                self.tab_list = self.minor_cats
                self.tab_showing = self.minor_tab
                self.minor_tab.disable()
                self.update_sick_cats()
            elif event.ui_element in self.cat_buttons.values():
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen('profile screen')
            elif event.ui_element == self.med_cat:
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen('profile screen')
            elif event.ui_element == self.cats_tab:
                self.open_tab = "cats"
                self.cats_tab.disable()
                self.log_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.log_tab:
                self.open_tab = "log"
                self.log_tab.disable()
                self.cats_tab.enable()
                self.handle_tab_toggles()

    def screen_switches(self):
        self.hide_menu_buttons()
        self.back_button = UIImageButton(pygame.Rect((25, 25), (105, 30)), "", object_id="#back_button")
        self.next_med = UIImageButton(pygame.Rect((645, 278), (34, 34)), "", object_id="#arrow_right_button")
        self.last_med = UIImageButton(pygame.Rect((600, 278), (34, 34)), "", object_id="#arrow_left_button")

        if game.clan.game_mode != 'classic':
            self.last_page = UIImageButton(pygame.Rect((330, 636), (34, 34)), "", object_id="#arrow_left_button")
            self.next_page = UIImageButton(pygame.Rect((476, 636), (34, 34)), "", object_id="#arrow_right_button")

            self.hurt_sick_title = pygame_gui.elements.UITextBox(
                "Hurt & Sick Cats",
                pygame.Rect((140, 410), (200, 30)),
                object_id=get_text_box_theme("#cat_profile_name_box")
            )
            self.log_title = pygame_gui.elements.UITextBox(
                "Medicine Den Log",
                pygame.Rect((140, 410), (200, 30)),
                object_id=get_text_box_theme("#cat_profile_name_box")
            )
            self.log_title.hide()
            self.cat_bg = pygame_gui.elements.UIImage(pygame.Rect
                                                      ((140, 440), (560, 200)),
                                                      pygame.image.load(
                                                          "resources/images/sick_hurt_bg.png").convert_alpha())
            self.cat_bg.disable()
            log_text = game.herb_events_list.copy()
            img_path = "resources/images/spacer.png"
            self.log_box = pygame_gui.elements.UITextBox(
                f"{f'<br><img src={img_path}><br>'.join(log_text)}<br>",
                pygame.Rect
                ((150, 450), (540, 180)),
                object_id="#med_den_log_box",
            )
            self.log_box.hide()
            self.cats_tab = UIImageButton(pygame.Rect
                                          ((109, 462), (35, 75)),
                                          "",
                                          object_id="#hurt_sick_cats_button"
                                          )
            self.cats_tab.disable()
            self.log_tab = UIImageButton(pygame.Rect
                                         ((109, 552), (35, 64)),
                                         "",
                                         object_id="#med_den_log_button"
                                         )
            self.in_den_tab = UIImageButton(pygame.Rect
                                            ((370, 409), (75, 35)),
                                            "",
                                            object_id="#in_den_tab")
            self.in_den_tab.disable()
            self.out_den_tab = UIImageButton(pygame.Rect
                                             ((460, 409), (112, 35)),
                                             "",
                                             object_id="#out_den_tab")
            self.minor_tab = UIImageButton(pygame.Rect
                                           ((587, 409), (70, 35)),
                                           "",
                                           object_id="#minor_tab")
            self.tab_showing = self.in_den_tab

            self.in_den_cats = []
            self.out_den_cats = []
            self.minor_cats = []
            self.injured_and_sick_cats = []
            for the_cat in Cat.all_cats_list:
                if not the_cat.dead and not the_cat.outside and (the_cat.injuries or the_cat.illnesses):
                    self.injured_and_sick_cats.append(the_cat)
            for cat in self.injured_and_sick_cats:
                if cat.injuries:
                    for injury in cat.injuries:
                        print(cat.name, injury)
                        if cat.injuries[injury]["severity"] != 'minor' and injury not in ['recovering from birth', "sprain", "lingering shock"]:
                            self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif injury in ['recovering from birth', "sprain", "lingering shock"]:
                            self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        else:
                            self.minor_cats.append(cat)
                if cat.illnesses:
                    for illness in cat.illnesses:
                        if cat.illnesses[illness]["severity"] != 'minor' and illness != 'grief stricken':
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif illness == 'grief stricken':
                            if cat not in self.in_den_cats:
                                if cat not in self.out_den_cats:
                                    self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        else:
                            if cat not in (self.in_den_cats and self.out_den_cats):
                                if cat not in self.in_den_cats and cat not in self.out_den_cats:
                                    self.minor_cats.append(cat)
            self.tab_list = self.in_den_cats
            self.current_page = 1
            self.update_sick_cats()

        self.current_med = 1

        self.draw_med_den()
        self.update_med_cat()

        self.meds_messages = UITextBoxTweaked(
            "",
            pygame.Rect((108, 320), (600, 80)),
            object_id=get_text_box_theme("#med_messages_box"),
            line_spacing=1
        )

        if self.meds:
            med_messages = []

            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            number = medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med,
                                                      give_clanmembers_covered=True)
            if len(self.meds) == 1:
                insert = 'medicine cat'
            else:
                insert = 'medicine cats'
            meds_cover = f"Your {insert} can care for a Clan of up to {number} members, including themselves."

            if len(self.meds) >= 1 and number == 0:
                meds_cover = f"You have no medicine cats who are able to work. Your clan will be at a higher risk of death and disease."

            herb_amount = sum(game.clan.herbs.values())
            med_concern = f"This should not appear."
            if herb_amount == 0:
                med_concern = f"The herb stores are empty and bare, this does not bode well."
            elif 0 < herb_amount <= 8:
                if len(self.meds) == 1:
                    med_concern = f"The medicine cat worries over the herb stores, they don't have nearly enough for the Clan."
                else:
                    med_concern = f"The medicine cats worry over the herb stores, they don't have nearly enough for the Clan."
            elif 8 < herb_amount <= 20:
                med_concern = f"The herb stores are small, but it's enough for now."
            elif 20 < herb_amount <= 30:
                if len(self.meds) == 1:
                    med_concern = f"The medicine cat is content with how many herbs they have stocked up."
                else:
                    med_concern = f"The medicine cats are content with how many herbs they have stocked up."
            elif 30 < herb_amount <= 50:
                if len(self.meds) == 1:
                    med_concern = f"The herb stores are overflowing and the medicine cat has little worry."
                else:
                    med_concern = f"The herb stores are overflowing and the medicine cats have little worry."
            elif 50 < herb_amount:
                if len(self.meds) == 1:
                    med_concern = f"StarClan has blessed them with plentiful herbs and the medicine cat sends their thanks to Silverpelt."
                else:
                    med_concern = f"StarClan has blessed them with plentiful herbs and the medicine cats send their thanks to Silverpelt."

            med_messages.append(meds_cover)
            med_messages.append(med_concern)
            self.meds_messages.set_text("<br>".join(med_messages))

        else:
            meds_cover = f"You have no medicine cats, your clan will be at higher risk of death and sickness."
            self.meds_messages.set_text(meds_cover)

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.log_title.hide()
            self.log_box.hide()

            self.hurt_sick_title.show()
            self.last_page.show()
            self.next_page.show()
            self.in_den_tab.show()
            self.out_den_tab.show()
            self.minor_tab.show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
        elif self.open_tab == "log":
            self.hurt_sick_title.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.in_den_tab.hide()
            self.out_den_tab.hide()
            self.minor_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.log_title.show()
            self.log_box.show()

    def update_med_cat(self):
        if self.med_cat:
            self.med_cat.kill()
        if self.med_info:
            self.med_info.kill()
        if self.med_name:
            self.med_name.kill()

        # get the med cats
        self.meds = get_med_cats(Cat, working=False)

        if not self.meds:
            all_pages = []
        else:
            all_pages = self.chunks(self.meds, 1)

        if self.current_med > len(all_pages):
            if len(all_pages) == 0:
                self.current_med = 1
            else:
                self.current_med = len(all_pages)

        if all_pages:
            self.display_med = all_pages[self.current_med - 1]
        else:
            self.display_med = []

        if len(all_pages) <= 1:
            self.next_med.disable()
            self.last_med.disable()
        else:
            if self.current_med >= len(all_pages):
                self.next_med.disable()
            else:
                self.next_med.enable()

            if self.current_med <= 1:
                self.last_med.disable()
            else:
                self.last_med.enable()

        for cat in self.display_med:
            self.med_cat = UISpriteButton(pygame.Rect
                                          ((435, 165), (150, 150)),
                                          cat.sprite,
                                          cat_object=cat)
            name = str(cat.name)
            if len(name) >= 20:
                short_name = str(cat.name)[0:18]
                name = short_name + '...'
            self.med_name = pygame_gui.elements.ui_label.UILabel(pygame.Rect
                                                                 ((590, 155), (100, 30)),
                                                                 name,
                                                                 object_id=get_text_box_theme()
                                                                 )
            self.med_info = UITextBoxTweaked(
                "",
                pygame.Rect((580, 185), (120, 120)),
                object_id=get_text_box_theme("#cat_patrol_info_box"),
                line_spacing=1
            )
            med_skill = cat.skill
            med_exp = f"experience: {cat.experience_level}"
            med_working = True
            if cat.not_working():
                med_working = False
            if med_working is True:
                work_status = "This cat can work"
            else:
                work_status = "This cat isn't able to work"
            info_list = [med_skill, med_exp, work_status]
            self.med_info.set_text("<br>".join(info_list))

    def update_sick_cats(self):
        """
        set tab showing as either self.in_den_cats, self.out_den_cats, or self.minor_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        tab_list = self.tab_list

        if not tab_list:
            all_pages = []
        else:
            all_pages = self.chunks(tab_list, 10)

        if self.current_page > len(all_pages):
            if len(all_pages) == 0:
                self.current_page = 1
            else:
                self.current_page = len(all_pages)

        # Check for empty list (no cats)
        if all_pages:
            self.display_cats = all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.next_page.disable()
            self.last_page.disable()
        else:
            if self.current_page >= len(all_pages):
                self.next_page.disable()
            else:
                self.next_page.enable()

            if self.current_page <= 1:
                self.last_page.disable()
            else:
                self.last_page.enable()

        pos_x = 175
        pos_y = 460
        i = 0
        for cat in self.display_cats:
            condition_list = []
            if cat.injuries:
                condition_list.extend(cat.injuries.keys())
            if cat.illnesses:
                condition_list.extend(cat.illnesses.keys())
            if cat.permanent_condition:
                condition_list.extend(cat.permanent_condition.keys())
            conditions = ",<br>".join(condition_list)

            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(pygame.Rect
                                                                   ((pos_x, pos_y), (50, 50)),
                                                                   cat.sprite,
                                                                   cat_object=cat)

            self.conditions_hover["able_cat" + str(i)] = UIImageButton(pygame.Rect
                                                                       ((pos_x - 30, pos_y + 50), (110, 30)),
                                                                       "",
                                                                       object_id="#blank_button",
                                                                       tool_tip_text=conditions)
            name = str(cat.name)
            if len(name) >= 10:
                short_name = str(cat.name)[0:9]
                name = short_name + '...'
            self.cat_names.append(pygame_gui.elements.UITextBox(name,
                                                                pygame.Rect((pos_x - 30, pos_y + 50), (110, 30)),
                                                                object_id="text_box"))

            pos_x += 100
            if pos_x >= 670:
                pos_x = 175
                pos_y += 80
            i += 1

    def draw_med_den(self):
        sorted_dict = dict(sorted(game.clan.herbs.items()))
        herbs_stored = sorted_dict.items()
        herb_list = []
        for herb in herbs_stored:
            amount = str(herb[1])
            type = str(herb[0].replace("_", " "))
            herb_list.append(f"{amount} {type}")
        if not herbs_stored:
            herb_list.append("Empty")
        if len(herb_list) <= 10:
            herb_display = "<br>".join(sorted(herb_list))

            self.den_base = UIImageButton(pygame.Rect
                                          ((108, 95), (396, 224)),
                                          "",
                                          object_id="#med_cat_den_hover",
                                          tool_tip_text=herb_display
                                          )
        else:
            count = 1
            holding_pairs = []
            pair = []
            added = False
            for y in range(len(herb_list)):
                if (count % 2) == 0:  # checking if count is an even number
                    count += 1
                    pair.append(herb_list[y])
                    holding_pairs.append("   -   ".join(pair))
                    pair.clear()
                    added = True
                    continue
                else:
                    pair.append(herb_list[y])
                    count += 1
                    added = False
            if added is False:
                holding_pairs.extend(pair)

            herb_display = "<br>".join(holding_pairs)
            self.den_base = UIImageButton(pygame.Rect
                                          ((108, 95), (396, 224)),
                                          "",
                                          object_id="#med_cat_den_hover_big",
                                          tool_tip_text=herb_display
                                          )

        herbs = game.clan.herbs
        for herb in herbs:
            if herb == 'cobwebs':
                self.herbs["cobweb1"] = pygame_gui.elements.UIImage(pygame.Rect
                                                                    ((108, 95), (396, 224)),
                                                                    pygame.image.load(
                                                                        "resources/images/med_cat_den/cobweb1.png").convert_alpha()
                                                                    )
                if herbs["cobwebs"] > 1:
                    self.herbs["cobweb2"] = pygame_gui.elements.UIImage(pygame.Rect
                                                                        ((108, 95), (396, 224)),
                                                                        pygame.image.load(
                                                                            "resources/images/med_cat_den/cobweb2.png").convert_alpha()
                                                                        )
                continue
            self.herbs[herb] = pygame_gui.elements.UIImage(pygame.Rect
                                                           ((108, 95), (396, 224)),
                                                           pygame.image.load(
                                                               f"resources/images/med_cat_den/{herb}.png").convert_alpha()
                                                           )

    def exit_screen(self):
        self.meds_messages.kill()
        self.last_med.kill()
        self.next_med.kill()
        self.den_base.kill()
        for herb in self.herbs:
            self.herbs[herb].kill()
        self.herbs = {}
        if self.med_info:
            self.med_info.kill()
        if self.med_name:
            self.med_name.kill()
        self.back_button.kill()
        if game.clan.game_mode != 'classic':
            self.cat_bg.kill()
            self.last_page.kill()
            self.next_page.kill()
            self.in_den_tab.kill()
            self.out_den_tab.kill()
            self.minor_tab.kill()
            self.clear_cat_buttons()
            self.hurt_sick_title.kill()
            self.cats_tab.kill()
            self.log_tab.kill()
            self.log_title.kill()
            self.log_box.kill()
        if self.med_cat:
            self.med_cat.kill()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        for button in self.conditions_hover:
            self.conditions_hover[button].kill()
        for x in range(len(self.cat_names)):
            self.cat_names[x].kill()

        self.cat_names = []
        self.cat_buttons = {}
