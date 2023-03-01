import pygame
from math import ceil
from random import choice, randint
import pygame_gui

from .base_screens import Screens, cat_profiles

from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UISpriteButton, UIImageButton, UITextBoxTweaked
from scripts.utility import get_text_box_theme, update_sprite, scale, get_alive_clan_queens, get_med_cats
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from .cat_screens import ProfileScreen
from ..conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled


class ClanScreen(Screens):
    max_sprites_displayed = 400  # we don't want 100,000 sprites rendering at once. 400 is enough.
    cat_buttons = []

    def __init__(self, name=None):
        super().__init__(name)
        self.show_den_labels = None
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

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.save_button:
                self.save_button_saving_state.show()
                self.save_button.disable()
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_settings()
                game.switches['saved_clan'] = True
                self.update_buttons_and_text()
            if event.ui_element in self.cat_buttons:
                game.switches["cat"] = event.ui_element.return_cat_id()
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
                        UISpriteButton(scale(pygame.Rect(tuple(Cat.all_cats[x].placement), (100, 100))),
                                       Cat.all_cats[x].big_sprite,
                                       cat_id=x,
                                       starting_height=1)
                    )
                except:
                    print(f"ERROR: placing {Cat.all_cats[x].name}\'s sprite on Clan page")

        # Den Labels
        # Redo the locations, so that it uses layout on the clan page
        self.warrior_den_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(game.clan.cur_layout["warrior den"], (242, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/warrior_den.png'),
                (242, 56)))
        self.leader_den_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(game.clan.cur_layout["leader den"], (224, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/leader_den.png'),
                (224, 56)))
        self.med_den_label = UIImageButton(scale(pygame.Rect(
            game.clan.cur_layout["medicine den"], (302, 56))),
            "",
            object_id="#med_den_button",
            starting_height=2
        )
        self.elder_den_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(game.clan.cur_layout["elder den"], (206, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/elder_den.png'),
                (206, 56)),
            )
        self.nursery_label = pygame_gui.elements.UIImage(scale(pygame.Rect(game.clan.cur_layout['nursery'], (160, 56))),
                                                         pygame.transform.scale(
                                                             image_cache.load_image('resources/images/nursery_den.png'),
                                                             (160, 56)))
        self.clearing_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(game.clan.cur_layout['clearing'], (162, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/clearing.png'),
                (162, 56)))
        self.app_den_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(game.clan.cur_layout['apprentice den'], (294, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/app_den.png'),
                (294, 56)))

        # Draw the toggle and text
        self.show_den_labels = pygame_gui.elements.UIImage(scale(pygame.Rect((50, 1282), (334, 68))),
                                                           pygame.transform.scale(
                                                               image_cache.load_image(
                                                                   'resources/images/show_den_labels.png'),
                                                               (334, 68)))
        self.show_den_labels.disable()
        self.label_toggle = UIImageButton(scale(pygame.Rect((50, 1282), (64, 64))), "", object_id="#checked_checkbox")

        self.save_button = UIImageButton(scale(pygame.Rect(((686, 1286), (228, 60)))), "", object_id="#save_button")
        self.save_button_saved_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((686, 1286), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/save_clan_saved.png'),
                (228, 60)))
        self.save_button_saved_state.hide()
        self.save_button_saving_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((686, 1286), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/save_clan_saving.png'),
                (228, 60)))
        self.save_button_saving_state.hide()

        self.update_buttons_and_text()

    def exit_screen(self):
        # removes the cat sprites.
        for button in self.cat_buttons:
            button.kill()
        self.cat_buttons = []

        # Kill all other elements, and destroy the reference so they aren't hanging around
        self.save_button.kill()
        del self.save_button
        self.save_button_saved_state.kill()
        del self.save_button_saved_state
        self.save_button_saving_state.kill()
        del self.save_button_saving_state
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
        self.show_den_labels.kill()
        del self.show_den_labels

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
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))

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
            if Cat.all_cats[x].status in ['apprentice', 'mediator apprentice']:
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
            elif Cat.all_cats[x].status in ['warrior', 'mediator']:
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
            self.save_button_saving_state.hide()
            self.save_button_saved_state.show()
            self.save_button.disable()
        else:
            self.save_button.enable()

        self.label_toggle.kill()
        if game.settings['den labels']:
            self.label_toggle = UIImageButton(scale(pygame.Rect((50, 1282), (68, 68))), "",
                                              object_id="#checked_checkbox")
            self.warrior_den_label.show()
            self.clearing_label.show()
            self.nursery_label.show()
            self.app_den_label.show()
            self.leader_den_label.show()
            self.med_den_label.show()
            self.elder_den_label.show()
        else:
            self.label_toggle = UIImageButton(scale(pygame.Rect((50, 1282), (68, 68))), "",
                                              object_id="#unchecked_checkbox")
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
        self.filter_id = None
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
            (screen_x, screen_y))
        self.search_bar_image = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (456, 68))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (380, 70))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.dark_forest_button:
                self.change_screen('dark forest screen')
            elif event.ui_element == self.unknown_residence_button:
                self.change_screen('unknown residence screen')
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
                game.switches["cat"] = event.ui_element.return_cat_id()
                self.change_screen('profile screen')
            else:
                self.menu_button_pressed(event)

    def exit_screen(self):
        self.hide_menu_buttons()
        self.starclan_button.kill()
        self.dark_forest_button.kill()
        self.unknown_residence_button.kill()
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
        self.dead_cats = [game.clan.instructor] if not game.clan.instructor.df else []
        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.outside and not the_cat.df and \
                    not the_cat.faded and not the_cat.status in ['kittypet', 'loner', 'rogue']:
                self.dead_cats.append(the_cat)

    def screen_switches(self):
        # Determine the dead, non-exiled cats.
        cat_profiles()
        self.get_dead_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((845, 284), (294, 46))),
                                                              object_id="#search_entry_box", manager=MANAGER)

        self.starclan_button = UIImageButton(scale(pygame.Rect((230, 270), (68, 68))), "", object_id="#starclan_button"
                                             , manager=MANAGER)
        self.starclan_button.disable()
        self.unknown_residence_button = UIImageButton(scale(pygame.Rect((298, 270), (68, 68))), "",
                                                      object_id="#unknown_residence_button", manager=MANAGER)
        self.dark_forest_button = UIImageButton(scale(pygame.Rect((366, 270), (68, 68))), "",
                                                object_id="#dark_forest_button"
                                                , manager=MANAGER)
        self.next_page_button = UIImageButton(scale(pygame.Rect((912, 1190), (68, 68))), "",
                                              object_id="#arrow_right_button"
                                              , manager=MANAGER)
        self.previous_page_button = UIImageButton(scale(pygame.Rect((620, 1190), (68, 68))), "",
                                                  object_id="#arrow_left_button"
                                                  , manager=MANAGER)
        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((680, 1190),
                                                                               (220, 60))),
                                                         manager=MANAGER)  # Text will be filled in later

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("StarClan")
        self.show_menu_buttons()

        self.update_search_cats("")  # This will list all the cats, and create the button objects.

        x_pos = 1152
        y_pos = 270
        self.filter_by_closed = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (196, 68))),
            "",
            object_id="#filter_by_closed_button",
            tool_tip_text="By default, cats are sorted by rank.", manager=MANAGER
        )
        self.filter_by_open = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (196, 68))),
            "",
            object_id="#filter_by_open_button", manager=MANAGER
        )
        self.filter_by_open.hide()
        y_pos += 68

        self.filter_rank = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_rank_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_rank.hide()
        y_pos += 58
        self.filter_age = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_age_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_age.hide()
        y_pos += 58
        self.filter_id = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_ID_button",
            starting_height=2, manager=MANAGER
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

        self.page_number.set_text("<font color='#FFFFFF'>" + str(self.list_page) + "/" +
                                  str(self.all_pages) + "</font>")

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
        if self.current_listed_cats:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(
                    UISpriteButton(scale(pygame.Rect
                                         ((260 + pos_x, 360 + pos_y), (100, 100))),
                                   cat.big_sprite,
                                   cat.ID,
                                   starting_height=1, manager=MANAGER))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + name + "</font>"
                                                                    ,
                                                                    scale(pygame.Rect((160 + pos_x, 460 + pos_y),
                                                                                      (300, 60)))
                                                                    , manager=MANAGER))
                pos_x += 240
                if pos_x >= 1200:
                    pos_x = 0
                    pos_y += 200

    def on_use(self):
        bg = self.starclan_bg

        # Only update the positions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(bg, (0, 0))

        screen.blit(ListScreen.search_bar, (696 / 1600 * screen_x, 270 / 1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class DFScreen(Screens):
    list_page = 1
    display_cats = []
    cat_names = []
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.filter_id = None
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
            (screen_x, screen_y))
        self.search_bar_image = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (int(456 / 1600 * screen_x),
                                                                                   int(68 / 1400 * screen_x)))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (int(380 / 1600 * screen_x),
                                                                                          int(68 / 1400 * screen_y)))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.starclan_button:
                self.change_screen('starclan screen')
            elif event.ui_element == self.unknown_residence_button:
                self.change_screen('unknown residence screen')
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
                self.filter_id.show()
                self.filter_age.show()
            elif event.ui_element == self.filter_by_open:
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_options_visible = False
                self.filter_rank.hide()
                self.filter_id.hide()
                self.filter_age.hide()
            elif event.ui_element == self.filter_age:
                self.filter_id.hide()
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
                self.filter_id.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "rank"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_id:
                self.filter_age.hide()
                self.filter_id.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "id"
                Cat.sort_cats()
                self.get_dead_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element in self.display_cats:
                game.switches["cat"] = event.ui_element.return_cat_id()
                self.change_screen('profile screen')
            else:
                self.menu_button_pressed(event)

    def exit_screen(self):
        self.hide_menu_buttons()
        self.starclan_button.kill()
        self.dark_forest_button.kill()
        self.unknown_residence_button.kill()
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
        self.dead_cats = [game.clan.instructor] if game.clan.instructor.df else []

        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.exiled and the_cat.df and \
                    not the_cat.faded:
                self.dead_cats.append(the_cat)

    def screen_switches(self):
        # Determine the dead, non-exiled cats.
        cat_profiles()
        self.get_dead_cats()

        self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((845, 284), (294, 46))),
                                                              object_id="#search_entry_box"
                                                              , manager=MANAGER)

        self.starclan_button = UIImageButton(scale(pygame.Rect((230, 270), (68, 68))), "", object_id="#starclan_button")
        self.unknown_residence_button = UIImageButton(scale(pygame.Rect((298, 270), (68, 68))), "",
                                                      object_id="#unknown_residence_button", manager=MANAGER)
        self.dark_forest_button = UIImageButton(scale(pygame.Rect((366, 270), (68, 68))), "",
                                                object_id="#dark_forest_button"
                                                , manager=MANAGER)
        self.dark_forest_button.disable()
        self.next_page_button = UIImageButton(scale(pygame.Rect((912, 1190), (68, 68))), "",
                                              object_id="#arrow_right_button"
                                              , manager=MANAGER)
        self.previous_page_button = UIImageButton(scale(pygame.Rect((620, 1190), (68, 68))), "",
                                                  object_id="#arrow_left_button", manager=MANAGER)
        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((680, 1190),
                                                                               (220, 60))), manager=MANAGER)

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("Dark Forest")
        self.show_menu_buttons()

        self.update_search_cats("")  # This will list all the cats, and create the button objects.

        x_pos = 1152
        y_pos = 270
        self.filter_by_closed = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (196, 68))),
            "",
            object_id="#filter_by_closed_button",
            tool_tip_text="By default, cats are sorted by rank.", manager=MANAGER
        )
        self.filter_by_open = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (196, 68))),
            "",
            object_id="#filter_by_open_button", manager=MANAGER
        )
        self.filter_by_open.hide()
        y_pos += 68

        self.filter_rank = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_rank_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_rank.hide()
        y_pos += 58
        self.filter_age = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_age_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_age.hide()
        y_pos += 58
        self.filter_id = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_ID_button",
            starting_height=2, manager=MANAGER
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

        self.page_number.set_text("<font color='#FFFFFF'>" + str(self.list_page) + "/" +
                                  str(self.all_pages) + "</font>")

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
        if self.current_listed_cats:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(
                    UISpriteButton(scale(pygame.Rect
                                         ((260 + pos_x, 360 + pos_y), (100, 100))),
                                   cat.big_sprite,
                                   cat.ID,
                                   starting_height=1))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + name + "</font>"
                                                                    ,
                                                                    scale(pygame.Rect((160 + pos_x, 460 + pos_y),
                                                                                      (300, 60)))
                                                                    , manager=MANAGER))
                pos_x += 240
                if pos_x >= 1200:
                    pos_x = 0
                    pos_y += 200

    def on_use(self):
        bg = self.df_bg
        screen.blit(bg, (0, 0))

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(bg, (0, 0))

        screen.blit(ListScreen.search_bar, (696 / 1600 * screen_x, 270 / 1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class ListScreen(Screens):
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20
    list_page = 1
    display_cats = []
    cat_names = []

    search_bar = pygame.transform.scale(pygame.image.load("resources/images/search_bar.png").convert_alpha(),
                                        (456 / 1600 * screen_x, 68 / 1400 * screen_y))
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.filter_age = None
        self.filter_id = None
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
                self.filter_id.show()
                self.filter_age.show()
            elif event.ui_element == self.filter_by_open:
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                self.filter_options_visible = False
                self.filter_id.hide()
                self.filter_rank.hide()
                self.filter_age.hide()
            elif event.ui_element == self.filter_age:
                self.filter_id.hide()
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "reverse_age"
                Cat.sort_cats()
                self.get_living_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_rank:
                self.filter_id.hide()
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "rank"
                Cat.sort_cats()
                self.get_living_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_id:
                self.filter_id.hide()
                self.filter_age.hide()
                self.filter_rank.hide()
                self.filter_by_open.hide()
                self.filter_by_closed.show()
                game.sort_type = "id"
                Cat.sort_cats()
                self.get_living_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element in self.display_cats:
                game.switches["cat"] = event.ui_element.return_cat_id()
                self.change_screen('profile screen')
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

        self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((845, 284), (294, 46))),
                                                              object_id="#search_entry_box", manager=MANAGER)

        self.your_clan_button = UIImageButton(scale(pygame.Rect((230, 270), (68, 68))), "",
                                              object_id="#your_clan_button"
                                              , manager=MANAGER)
        self.your_clan_button.disable()
        self.outside_clan_button = UIImageButton(scale(pygame.Rect((298, 270), (68, 68))), "",
                                                 object_id="#outside_clan_button", manager=MANAGER)
        self.next_page_button = UIImageButton(scale(pygame.Rect((912, 1190), (68, 68))), "",
                                              object_id="#arrow_right_button"
                                              , manager=MANAGER)
        self.previous_page_button = UIImageButton(scale(pygame.Rect((620, 1190), (68, 68))), "",
                                                  object_id="#arrow_left_button", manager=MANAGER)
        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((680, 1190), (220, 60))),
                                                         object_id=get_text_box_theme()
                                                         , manager=MANAGER)  # Text will be filled in later

        self.set_disabled_menu_buttons(["list_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_menu_buttons()
        self.update_search_cats("")  # This will list all the cats, and create the button objects.

        x_pos = 1152
        y_pos = 270
        self.filter_by_closed = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (196, 68))),
            "",
            object_id="#filter_by_closed_button",
            tool_tip_text="By default, cats are sorted by rank.", manager=MANAGER
        )
        self.filter_by_open = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (196, 68))),
            "",
            object_id="#filter_by_open_button", manager=MANAGER
        )
        self.filter_by_open.hide()
        y_pos += 68

        self.filter_rank = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_rank_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_rank.hide()
        y_pos += 58
        self.filter_age = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_age_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_age.hide()
        y_pos += 58
        self.filter_id = UIImageButton(
            scale(pygame.Rect((x_pos - 2, y_pos), (204, 58))),
            "",
            object_id="#filter_ID_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_id.hide()

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
        self.filter_id.kill()

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
        if self.current_listed_cats:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(
                    UISpriteButton(scale(pygame.Rect
                                         ((260 + pos_x, 360 + pos_y), (100, 100))),
                                   cat.big_sprite,
                                   cat.ID,
                                   starting_height=1, manager=MANAGER))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox(name,
                                                                    scale(pygame.Rect((160 + pos_x, 460 + pos_y),
                                                                                      (300, 60))),
                                                                    object_id=get_text_box_theme(), manager=MANAGER))
                pos_x += 240
                if pos_x >= 1200:
                    pos_x = 0
                    pos_y += 200

    def on_use(self):

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(ListScreen.search_bar, (696 / 1600 * screen_x, 270 / 1400 * screen_y))

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
                                                     scale(pygame.Rect((60, 220), (800, 80))),
                                                     object_id=get_text_box_theme("#allegiances_header_text_box")
                                                     , manager=MANAGER)

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
        for the_cat in living_cats:
            if the_cat.status == 'medicine cat':
                living_meds.append(the_cat)
        living_mediators = []
        for the_cat in living_cats:
            if the_cat.status == 'mediator':
                living_mediators.append(the_cat)

        # Pull the clan leaders
        leader = []
        if game.clan.leader is not None:
            if not game.clan.leader.dead and not game.clan.leader.outside:
                self.allegiance_list.append([
                    '<b><u>LEADER</u></b>',
                    f"{game.clan.leader.name} - a {game.clan.leader.describe_cat()}"
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
                f"{game.clan.deputy.name} - a {game.clan.deputy.describe_cat()}"
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

        if living_mediators:
            self._extracted_from_screen_switches_24(
                living_cats, 'mediator', '<b><u>MEDIATORS</u></b>')

        queens = get_alive_clan_queens(Cat.all_cats)
        queens = [cat.ID for cat in queens]
        cat_count = 0
        for living_cat__ in living_cats:
            if str(
                    living_cat__.status
            ) == 'warrior' and living_cat__.ID not in queens and not living_cat__.outside:
                if not cat_count:
                    self.allegiance_list.append([
                        '<b><u>WARRIORS</u></b>',
                        f"{living_cat__.name} - a {living_cat__.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{living_cat__.name} - a {living_cat__.describe_cat()}"
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
                'apprentice', 'medicine cat apprentice', 'mediator apprentice'
            ]:
                if cat_count == 0:
                    self.allegiance_list.append([
                        '<b><u>APPRENTICES</u></b>',
                        f"{living_cat___.name} - a {living_cat___.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{living_cat___.name} - a {living_cat___.describe_cat()}"
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
                        f"{living_cat____.name} - a {living_cat____.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{living_cat____.name} - a {living_cat____.describe_cat()}"
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

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((100, 300), (1400, 1000)))
                                                                         , manager=MANAGER)
        self.cat_names_box = pygame_gui.elements.UITextBox("\n".join([i[1] for i in self.allegiance_list]),
                                                           scale(pygame.Rect((300, 0), (1100, -1))),
                                                           object_id=get_text_box_theme("#allegiances_box"),
                                                           container=self.scroll_container, manager=MANAGER)

        self.ranks_box = pygame_gui.elements.UITextBox("\n".join([i[0] for i in self.allegiance_list]),
                                                       scale(pygame.Rect((0, 0), (300, -1))),
                                                       object_id=get_text_box_theme("#allegiances_box"),
                                                       container=self.scroll_container, manager=MANAGER)

        self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, self.cat_names_box.rect[3]))

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
                        f"{living_cat.name} - a {living_cat.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        "",
                        f"{living_cat.name} - a {living_cat.describe_cat()}"
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
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.next_med = UIImageButton(scale(pygame.Rect((1290, 556), (68, 68))), "", object_id="#arrow_right_button"
                                      , manager=MANAGER)
        self.last_med = UIImageButton(scale(pygame.Rect((1200, 556), (68, 68))), "", object_id="#arrow_left_button"
                                      , manager=MANAGER)

        if game.clan.game_mode != 'classic':
            self.last_page = UIImageButton(scale(pygame.Rect((660, 1272), (68, 68))), "", object_id="#arrow_left_button"
                                           , manager=MANAGER)
            self.next_page = UIImageButton(scale(pygame.Rect((952, 1272), (68, 68))), "",
                                           object_id="#arrow_right_button"
                                           , manager=MANAGER)

            self.hurt_sick_title = pygame_gui.elements.UITextBox(
                "Hurt & Sick Cats",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#cat_profile_name_box"), manager=MANAGER
            )
            self.log_title = pygame_gui.elements.UITextBox(
                "Medicine Den Log",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#cat_profile_name_box"), manager=MANAGER
            )
            self.log_title.hide()
            self.cat_bg = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                            ((280, 880), (1120, 400))),
                                                      pygame.image.load(
                                                          "resources/images/sick_hurt_bg.png").convert_alpha()
                                                      , manager=MANAGER)
            self.cat_bg.disable()
            log_text = game.herb_events_list.copy()
            if game.settings["fullscreen"]:
                img_path = "resources/images/spacer.png"
            else:
                img_path = "resources/images/spacer_small.png"
            self.log_box = pygame_gui.elements.UITextBox(
                f"{f'<br><img src={img_path}><br>'.join(log_text)}<br>",
                scale(pygame.Rect
                      ((300, 900), (1080, 360))),
                object_id="#med_den_log_box", manager=MANAGER
            )
            self.log_box.hide()
            self.cats_tab = UIImageButton(scale(pygame.Rect
                                                ((218, 924), (68, 150))),
                                          "",
                                          object_id="#hurt_sick_cats_button", manager=MANAGER
                                          )
            self.cats_tab.disable()
            self.log_tab = UIImageButton(scale(pygame.Rect
                                               ((218, 1104), (68, 128))),
                                         "",
                                         object_id="#med_den_log_button", manager=MANAGER
                                         )
            self.in_den_tab = UIImageButton(scale(pygame.Rect
                                                  ((740, 818), (150, 70))),
                                            "",
                                            object_id="#in_den_tab", manager=MANAGER)
            self.in_den_tab.disable()
            self.out_den_tab = UIImageButton(scale(pygame.Rect
                                                   ((920, 818), (224, 70))),
                                             "",
                                             object_id="#out_den_tab", manager=MANAGER)
            self.minor_tab = UIImageButton(scale(pygame.Rect
                                                 ((1174, 818), (140, 70))),
                                           "",
                                           object_id="#minor_tab", manager=MANAGER)
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
                        if cat.injuries[injury]["severity"] != 'minor' and injury not in ['recovering from birth',
                                                                                          "sprain", "lingering shock"]:
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
                            if cat not in self.minor_cats:
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
                            if cat not in (self.in_den_cats and self.out_den_cats and self.minor_cats):
                                self.minor_cats.append(cat)
            self.tab_list = self.in_den_cats
            self.current_page = 1
            self.update_sick_cats()

        self.current_med = 1

        self.draw_med_den()
        self.update_med_cat()

        self.meds_messages = UITextBoxTweaked(
            "",
            scale(pygame.Rect((216, 620), (1200, 160))),
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
            self.med_cat = UISpriteButton(scale(pygame.Rect
                                                ((870, 330), (300, 300))),
                                          cat.large_sprite,
                                          cat_object=cat, manager=MANAGER)
            name = str(cat.name)
            if len(name) >= 20:
                short_name = str(cat.name)[0:18]
                name = short_name + '...'
            self.med_name = pygame_gui.elements.ui_label.UILabel(scale(pygame.Rect
                                                                       ((1180, 310), (200, 60))),
                                                                 name,
                                                                 object_id=get_text_box_theme(), manager=MANAGER
                                                                 )
            self.med_info = UITextBoxTweaked(
                "",
                scale(pygame.Rect((1160, 370), (240, 240))),
                object_id=get_text_box_theme("#cat_patrol_info_box"),
                line_spacing=1, manager=MANAGER
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

        pos_x = 350
        pos_y = 920
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

            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(scale(pygame.Rect
                                                                         ((pos_x, pos_y), (100, 100))),
                                                                   cat.big_sprite,
                                                                   cat_object=cat, manager=MANAGER)

            self.conditions_hover["able_cat" + str(i)] = UIImageButton(scale(pygame.Rect
                                                                             ((pos_x - 60, pos_y + 100), (220, 60))),
                                                                       "",
                                                                       object_id="#blank_button",
                                                                       tool_tip_text=conditions, manager=MANAGER)
            name = str(cat.name)
            if len(name) >= 10:
                short_name = str(cat.name)[0:9]
                name = short_name + '...'
            self.cat_names.append(pygame_gui.elements.UITextBox(name,
                                                                scale(
                                                                    pygame.Rect((pos_x - 60, pos_y + 100), (220, 60))),
                                                                object_id="text_box", manager=MANAGER))

            pos_x += 200
            if pos_x >= 1340:
                pos_x = 350
                pos_y += 160
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

            self.den_base = UIImageButton(scale(pygame.Rect
                                                ((216, 190), (792, 448))),
                                          "",
                                          object_id="#med_cat_den_hover",
                                          tool_tip_text=herb_display, manager=MANAGER
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
            self.den_base = UIImageButton(scale(pygame.Rect
                                                ((216, 190), (792, 448))),
                                          "",
                                          object_id="#med_cat_den_hover_big",
                                          tool_tip_text=herb_display, manager=MANAGER
                                          )

        herbs = game.clan.herbs
        for herb in herbs:
            if herb == 'cobwebs':
                self.herbs["cobweb1"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                          ((216, 190), (792, 448))),
                                                                    pygame.transform.scale(
                                                                        pygame.image.load(
                                                                            "resources/images/med_cat_den/cobweb1.png").convert_alpha(),
                                                                        (792, 448)
                                                                    ), manager=MANAGER)
                if herbs["cobwebs"] > 1:
                    self.herbs["cobweb2"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                              ((216, 190), (792, 448))),
                                                                        pygame.transform.scale(
                                                                            pygame.image.load(
                                                                                "resources/images/med_cat_den/cobweb2.png").convert_alpha(),
                                                                            (792, 448)
                                                                        ), manager=MANAGER)
                continue
            self.herbs[herb] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                 ((216, 190), (792, 448))),
                                                           pygame.transform.scale(
                                                               pygame.image.load(
                                                                   f"resources/images/med_cat_den/{herb}.png").convert_alpha(),
                                                               (792, 448)
                                                           ), manager=MANAGER)

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
