import pygame
import pygame_gui
from math import ceil
from scripts.game_structure.image_button import UISpriteButton, UIImageButton
from .base_screens import Screens, cat_profiles

from .base_screens import Screens

from scripts.game_structure.game_essentials import *
from scripts.cat.cats import Cat
from scripts.cat.sprites import tiles
import scripts.game_structure.image_cache as image_cache
from ..utility import get_text_box_theme


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
            else:
                self.menu_button_pressed(event)

    def screen_switches(self):
        # Determine the living, exiled cats.
        self.living_cats = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and the_cat.outside:
                self.living_cats.append(the_cat)

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((525, 142), (147, 23)),
                                                              object_id="#search_entry_box")

        self.your_clan_button = UIImageButton(pygame.Rect((115, 135), (34, 34)), "", object_id="#your_clan_button")
        self.outside_clan_button = UIImageButton(pygame.Rect((150, 135),(34, 34)), "", object_id="#outside_clan_button")
        self.outside_clan_button.disable()
        self.next_page_button = UIImageButton(pygame.Rect((456, 595), (34, 34)), "", object_id="#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595), (34, 34)), "", object_id="#arrow_left_button")

        # Text will be filled in later
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((340, 595),(110, 30)))

        self.set_disabled_menu_buttons(["list_screen"])
        self.update_heading_text('<font size=4.0>Cats Outside The Clan</font>')
        self.show_menu_buttons()

        self.update_search_cats("") # This will list all the cats, and create the button objects.

        cat_profiles()
    
    def exit_screen(self):
        self.hide_menu_buttons()
        self.your_clan_button.kill()
        self.outside_clan_button.kill()
        self.next_page_button.kill()
        self.previous_page_button.kill()
        self.page_number.kill()
        self.search_bar.kill()

        # Remove currently displayed cats and cat names.
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()
        

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

        for name in self.cat_names:
            name.kill()
        
        # Generate object for the current cats
        pos_x = 0
        pos_y = 0
        # print(self.current_listed_cats)
        if self.current_listed_cats != []:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                self.display_cats.append(UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y),(50,50)),cat.sprite, cat.ID))

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

        screen.blit(self.search_bar_image, (452, 135))
        clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/outside_clan_bg.png").convert_alpha(), (242, 35))

    def chunks(self, L, n): return [L[x: x+n] for x in range(0, len(L), n)]

"""
class MapScreen(Screens):

    def on_use(self):
        hunting_claim = str(game.clan.name) + 'Clan Hunting Grounds'
        territory_claim = str(game.clan.name) + 'Clan Territory'
        training_claim = str(game.clan.name) + 'Clan Training Grounds'
        for y in range(44):
            for x in range(40):
                biome = game.map_info[(x, y)][2]
                if biome == 'Desert':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain1'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Forest':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain3'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Plains':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain0'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Ocean':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain2'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Mountainous':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain5'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Beach':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain6'],
                                                     (16, 16)),
                        map_selection=(x, y))
                if (x, y) == game.clan.camp_site:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo0'],
                                            (16, 16)),
                                        map_selection=(x, y))
                    game.map_info[(x, y)] = [
                        x, y,
                        str(biome), game.clan.name + 'Clan Camp',
                        "Twoleg Activity: none", "Thunderpath Traffic: none",
                        "Prey Levels: low",
                        str(game.map_info[(x, y)][7])
                    ]
                if (x, y) == game.switches['map_selection']:
                    if str(game.map_info[(x, y)][3]) == territory_claim:
                        buttons.draw_button((-16, 450),
                                            text='Hunting Grounds',
                                            hunting_territory=(x, y))
                        buttons.draw_button((-16, 500),
                                            text='Training Grounds',
                                            training_territory=(x, y))
                if (x, y) == game.switches['hunting_territory']:
                    territory_biome = str(game.map_info[(x, y)][2])
                    territory_twolegs = str(game.map_info[(x, y)][4])
                    territory_thunderpath = str(game.map_info[(x, y)][5])
                    territory_prey = str(game.map_info[(x, y)][6])
                    territory_plants = str(game.map_info[(x, y)][7])
                    if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                        game.map_info[(x, y)] = [
                            x, y, territory_biome, hunting_claim,
                            territory_twolegs, territory_thunderpath,
                            territory_prey, territory_plants
                        ]
                elif (x, y) == game.switches['training_territory']:
                    territory_biome = str(game.map_info[(x, y)][2])
                    territory_twolegs = str(game.map_info[(x, y)][4])
                    territory_thunderpath = str(game.map_info[(x, y)][5])
                    territory_prey = str(game.map_info[(x, y)][6])
                    territory_plants = str(game.map_info[(x, y)][7])
                    if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                        game.map_info[(x, y)] = [
                            x, y, territory_biome, training_claim,
                            territory_twolegs, territory_thunderpath,
                            territory_prey, territory_plants
                        ]
                if game.map_info[(x, y)][3] == hunting_claim:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo1'],
                                            (16, 16)))
                    game.switches['hunting_territory'] = (x, y)
                elif game.map_info[(x, y)][3] == territory_claim:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo2'],
                                            (16, 16)))
                elif game.map_info[(x, y)][3] == training_claim:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo3'],
                                            (16, 16)))
                for clan in game.clan.all_clans:
                    camp_claim = str(clan) + " Camp"
                    other_territory = str(clan) + " Territory"
                    if game.map_info[(x, y)][3] == camp_claim:
                        if game.map_info[(x, y)][2] == "Ocean":
                            game.map_info[(x, y)] = [
                                x, y, game.map_info[(x, y)][2], "Unclaimable",
                                game.map_info[(x, y)][4],
                                game.map_info[(x, y)][5],
                                game.map_info[(x, y)][6],
                                game.map_info[(x, y)][7]
                            ]
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo4'],
                                                (16, 16)))
                    elif game.map_info[(x, y)][3] == other_territory:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo4'],
                                                (16, 16)))
        verdana_big.text('Map', (-16, 50))
        verdana.text(
            str(game.map_info[game.switches['map_selection']][0]) + ", " +
            str(game.map_info[game.switches['map_selection']][1]), (-16, 100))
        verdana.text(str(game.map_info[game.switches['map_selection']][2]),
                     (-16, 150))
        verdana.text(str(game.map_info[game.switches['map_selection']][3]),
                     (-16, 200))
        verdana.text(str(game.map_info[game.switches['map_selection']][4]),
                     (-16, 250))
        verdana.text(str(game.map_info[game.switches['map_selection']][5]),
                     (-16, 300))
        verdana.text(str(game.map_info[game.switches['map_selection']][6]),
                     (-16, 350))
        verdana.text(str(game.map_info[game.switches['map_selection']][7]),
                     (-16, 400))

        buttons.draw_button((-16, -56),
                            text='<< Back',
                            cur_screen=game.switches['last_screen'],
                            hotkey=[0])


    def screen_switches(self):
        try:
            game.map_info = load_map('saves/' + game.clan.name)
            print("Map loaded.")
        except:
            game.map_info = load_map("Fallback")
            print("Default map loaded.")
"""