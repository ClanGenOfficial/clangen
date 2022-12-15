import pygame
from math import ceil
from random import choice, randint
import pygame_gui

from .base_screens import Screens, cat_profiles

from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat
from scripts.game_structure.buttons import *
from scripts.game_structure.image_button import UISpriteButton, UIImageButton
from scripts.utility import get_text_box_theme


class ClanScreen(Screens):
    max_sprites_displayed = 400 #we don't want 100,000 sprites rendering at once. 


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

        verdana.text("Leader\'s Den", game.clan.cur_layout['leader den'])
        verdana.text('Medicine Cat Den', game.clan.cur_layout['medicine den'])
        verdana.text('Nursery', game.clan.cur_layout['nursery'])
        verdana.text('Clearing', game.clan.cur_layout['clearing'])
        verdana.text("Apprentices\' Den",
                     game.clan.cur_layout['apprentice den'])
        verdana.text("Warriors\' Den", game.clan.cur_layout['warrior den'])
        verdana.text("Elders\' Den", game.clan.cur_layout['elder den'])

        pygame.draw.rect(screen,
                         color='gray',
                         rect=pygame.Rect(320, 660, 160, 20))

        if game.switches['saved_clan']:
            verdana_green.text('Saved!', ('center', -20))
        else:
            verdana_red.text('Remember to save!', ('center', -20))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.save_button:
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.switches['saved_clan'] = True
            if event.ui_element in self.cat_buttons:
                #print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                print(game.switches["cat"])
                #print(event.ui_element.return_cat_id())
                self.change_screen('profile screen')
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

        #Creates and places the cat sprites. 
        self.cat_buttons = [] #To contain all the buttons. 

        #We have to convert the postions to something pygame_gui buttons will understand
        #This should be a temp solution. We should change the code that determines postions. 
        i = 0
        for x in game.clan.clan_cats: 
            i += 1
            if i > self.max_sprites_displayed:
                break
            if not Cat.all_cats[x].dead and Cat.all_cats[
                    x].in_camp and not Cat.all_cats[x].exiled:
                #print("Orginal location" + str(Cat.all_cats[x].placement))
                location = [0,0]
                if Cat.all_cats[x].placement[0] == "center":
                    #print("center - 0")
                    location[0] = 375
                else:
                    if Cat.all_cats[x].placement[0] < 0:
                        location[0] = -Cat.all_cats[x].placement[0] + 375
                    else:
                        location[0] = Cat.all_cats[x].placement[0] - 25

                if Cat.all_cats[x].placement[1] == "center":
                    #print("center - 1")
                    location[1] = 325
                else:
                    location[1] = Cat.all_cats[x].placement[1] - 5

                #print("Converted Location" + str(location))
                self.cat_buttons.append(UISpriteButton(pygame.Rect(tuple(location), (50,50)), Cat.all_cats[x].sprite, cat_id = x))

        self.save_button = UIImageButton(pygame.Rect(((343, 625),(114, 30))), "", object_id="#save_button")

    def exit_screen(self):
        #removes the cat sprites. 
        for button in self.cat_buttons:
            button.kill()
        self.cat_buttons = []

        self.save_button.kill() #kill the save button.

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

    
class StarClanScreen(Screens):
    list_page = 1
    display_cats = []
    cat_names = []
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.starclan_bg = pygame.transform.scale(
            pygame.image.load("resources/images/starclanbg.png").convert(),
            (800, 700))
        self.search_bar = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.dark_forest_button:
                self.change_screen('dark forest screen')
            elif event.ui_element in self.display_cats:
                #print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                #print(event.ui_element.return_cat_id())
                self.change_screen('profile screen')
            elif event.ui_element == self.next_page_button:
                self.list_page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.list_page -= 1
                self.update_page()
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

        #Remove currently displayed cats and cat names. 
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()

    def screen_switches(self):
        #Determine the dead, non-exiled cats. 
        self.dead_cats = [game.clan.instructor]
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.outside and not the_cat.df:
                self.dead_cats.append(the_cat)

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((525,142), (147,20)))

        self.starclan_button = UIImageButton(pygame.Rect((150,135),(34,34)),"",object_id = "#starclan_button")
        self.starclan_button.disable()
        self.dark_forest_button =  UIImageButton(pygame.Rect((115,135),(34,34)),"",object_id = "#dark_forest_button")
        self.next_page_button = UIImageButton(pygame.Rect((456, 595),(34, 34)), "", object_id = "#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595),(34, 34)), "", object_id = "#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("",pygame.Rect((340,595),(110,30))) #Text will be filled in later

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("Starclan")
        self.show_menu_buttons()

        self.update_search_cats("") #This will list all the cats, and create the button objects. 

        cat_profiles()

    def update_search_cats(self, search_text):
        '''Run this function when the search text changes, or when the screen is switched to.'''
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
        '''Run this function when page changes.'''
        
        #If the number of pages becomes smaller than the number of our current page, set 
        #   the current page to the last page
        if self.list_page > self.all_pages:
            self.list_page = self.all_pages

        #Handle which next buttons are clickable. 
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
        self.page_number = pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" +str(self.list_page) + "/" + 
                                                        str(self.all_pages) + "</font>",
                                                            pygame.Rect((340,595),(110,30)))

        #Remove the images for currently listed cats
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()
        
        #Generate object for the current cats
        pos_x = 0
        pos_y = 0
        #print(self.current_listed_cats)
        if self.current_listed_cats != []:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y),(50,50)),cat.sprite, cat.ID))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + name + "</font>"
                                                    ,pygame.Rect((80 + pos_x, 230 + pos_y),(150,30))))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):
        bg = self.starclan_bg

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(bg, (0, 0))

        screen.blit(ListScreen.search_bar, (452, 135))
    
    def chunks(self, L, n): return [L[x: x+n] for x in range(0, len(L), n)]


class ListScreen(Screens):
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20
    list_page = 1
    display_cats = []
    cat_names = []

    search_bar = pygame.transform.scale(pygame.image.load("resources/images/search_bar.png").convert_alpha(),
                                        (228, 34))
    previous_search_text = ""

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.outside_clan_button:
                self.change_screen("other screen")
            elif event.ui_element in self.display_cats:
                #print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                #print(event.ui_element.return_cat_id())
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
        #Determine the living, non-exiled cats. 
        self.living_cats = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and not the_cat.outside:
                self.living_cats.append(the_cat)

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((525,142), (147,20)))

        self.your_clan_button = UIImageButton(pygame.Rect((115,135),(34,34)),"",object_id = "#your_clan_button")
        self.your_clan_button.disable()
        self.outside_clan_button =  UIImageButton(pygame.Rect((150,135),(34,34)),"",object_id = "#outside_clan_button")
        self.next_page_button = UIImageButton(pygame.Rect((456, 595),(34, 34)), "", object_id = "#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595),(34, 34)), "", object_id = "#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("",pygame.Rect((340,595),(110,30)),
                                                         object_id=get_text_box_theme()) #Text will be filled in later

        self.set_disabled_menu_buttons(["list_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_menu_buttons()

        self.update_search_cats("") #This will list all the cats, and create the button objects. 

        cat_profiles()
    
    def exit_screen(self):
        self.hide_menu_buttons()
        self.your_clan_button.kill()
        self.outside_clan_button.kill()
        self.next_page_button.kill()
        self.previous_page_button.kill()
        self.page_number.kill()
        self.search_bar.kill()

        #Remove currently displayed cats and cat names. 
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()
        

    def update_search_cats(self, search_text):
        '''Run this function when the search text changes, or when the screen is switched to.'''
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
        '''Run this function when page changes.'''
        
        #If the number of pages becomes smaller than the number of our current page, set 
        #   the current page to the last page
        if self.list_page > self.all_pages:
            self.list_page = self.all_pages

        #Handle which next buttons are clickable. 
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

        #Remove the images for currently listed cats
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()
        
        #Generate object for the current cats
        pos_x = 0
        pos_y = 0
        #print(self.current_listed_cats)
        if self.current_listed_cats != []:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y),(50,50)),cat.sprite, cat.ID))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox(name,
                                                                    pygame.Rect((80 + pos_x, 230 + pos_y),(150,30)),
                                                                    object_id = get_text_box_theme()))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):

        #Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(ListScreen.search_bar, (452, 135))

    def chunks(self, L, n): return [L[x: x+n] for x in range(0, len(L), n)]

class AllegiancesScreen(Screens):
    allegiance_list = []

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        pass

    def screen_switches(self):
        #Heading
        self.heading = pygame_gui.elements.UITextBox(f'{game.clan.name}Clan Allegiances',
                                                     pygame.Rect((30, 110), (400, 40)),
                                                     object_id=get_text_box_theme("#allegiances_header_text_box"))

        #Set Menu Buttons. 
        self.show_menu_buttons()
        self.set_disabled_menu_buttons(["allegiances"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.allegiance_list = []

        living_cats = []
        #Determine the living cats. 
        for the_cat in Cat.all_cats.values():
            if not the_cat.dead and not the_cat.outside:
                living_cats.append(the_cat)

        #Pull the clan leaders 
        leader = []
        if game.clan.leader is not None:
            if not game.clan.leader.dead and not game.clan.leader.outside:
                self.allegiance_list.append([
                    'LEADER:',
                    f"{str(game.clan.leader.name)} - a {game.clan.leader.describe_cat()}"
                ])

                if len(game.clan.leader.apprentice) > 0:
                    if len(game.clan.leader.apprentice) == 1:
                        self.allegiance_list.append([
                            '', '      Apprentice: ' +
                            str(game.clan.leader.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in game.clan.leader.apprentice:
                            app_names += str(app.name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if game.clan.deputy != 0 and game.clan.deputy is not None and not game.clan.deputy.dead and not game.clan.deputy.outside:
            game.allegiance_list.append([
                'DEPUTY:',
                f"{str(game.clan.deputy.name)} - a {game.clan.deputy.describe_cat()}"
            ])

            if len(game.clan.deputy.apprentice) > 0:
                if len(game.clan.deputy.apprentice) == 1:
                    self.allegiance_list.append([
                        '', '      Apprentice: ' +
                        str(game.clan.deputy.apprentice[0].name)
                    ])
                else:
                    app_names = ''
                    for app in game.clan.deputy.apprentice:
                        app_names += str(app.name) + ', '
                    self.allegiance_list.append(
                        ['', '      Apprentices: ' + app_names[:-2]])
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'medicine cat', 'MEDICINE CAT:')
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
                        'WARRIORS:',
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
                            str(living_cat__.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat__.apprentice:
                            app_names += str(app.name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
                cat_count += 1
        if not cat_count:
            self.allegiance_list.append(['WARRIORS:', ''])
        cat_count = 0
        for living_cat___ in living_cats:
            if str(living_cat___.status) in [
                    'apprentice', 'medicine cat apprentice'
            ]:
                if cat_count == 0:
                    self.allegiance_list.append([
                        'APPRENTICES:',
                        f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"
                    ])
                else:
                    self.allegiance_list.append([
                        '',
                        f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"
                    ])
                cat_count += 1
        if not cat_count:
            self.allegiance_list.append(['APPRENTICES:', ''])
        cat_count = 0
        for living_cat____ in living_cats:
            if living_cat____.ID in queens:
                if cat_count == 0:
                    self.allegiance_list.append([
                        'QUEENS:',
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
                            str(living_cat____.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat____.apprentice:
                            app_names += str(app.name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if not cat_count:
            self.allegiance_list.append(['QUEENS:', ''])
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'elder', 'ELDERS:')
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'kitten', 'KITS:')

        #print(self.allegiance_list)

        self.allegiance_box = pygame_gui.elements.UITextBox("\n".join(["".join(i) for i in self.allegiance_list]),
                                                            pygame.Rect((50,150),(700,500)),
                                                            object_id= get_text_box_theme("#allegiances_box"))

    def exit_screen(self):
        self.allegiance_box.kill()
        del self.allegiance_box
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
                            str(living_cat.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat.apprentice:
                            app_names += str(app.name) + ', '
                        self.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if not result:
            self.allegiance_list.append([arg2, ''])
        return result

# template for dark forest
class DFScreen(Screens):

    list_page = 1
    display_cats = []
    cat_names = []
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.df_bg = pygame.transform.scale(
            pygame.image.load("resources/images/darkforestbg.png").convert(),
            (800, 700))
        self.search_bar = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.starclan_button:
                self.change_screen('starclan screen')
            elif event.ui_element in self.display_cats:
                #print("cat pressed")
                game.switches["cat"] = event.ui_element.return_cat_id()
                #print(event.ui_element.return_cat_id())
                self.change_screen('profile screen')
            elif event.ui_element == self.next_page_button:
                self.list_page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.list_page -= 1
                self.update_page()
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

        #Remove currently displayed cats and cat names. 
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()

    def screen_switches(self):
        #Determine the dead, non-exiled cats.
        if game.clan.instructor.df is True:
            self.dead_cats = [game.clan.instructor]
        else:
            self.dead_cats = []

        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.outside and the_cat.df:
                self.dead_cats.append(the_cat)

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((525,142), (147,20)))

        self.starclan_button = UIImageButton(pygame.Rect((150,135),(34,34)),"",object_id = "#starclan_button")
        self.dark_forest_button =  UIImageButton(pygame.Rect((115,135),(34,34)),"",object_id = "#dark_forest_button")
        self.dark_forest_button.disable()
        self.next_page_button = UIImageButton(pygame.Rect((456, 595),(34, 34)), "", object_id = "#arrow_right_button")
        self.previous_page_button = UIImageButton(pygame.Rect((310, 595),(34, 34)), "", object_id = "#arrow_left_button")
        self.page_number = pygame_gui.elements.UITextBox("",pygame.Rect((340,595),(110,30))) #Text will be filled in later

        self.set_disabled_menu_buttons(["starclan_screen"])
        self.update_heading_text("Dark Forest")
        self.show_menu_buttons()

        self.update_search_cats("") #This will list all the cats, and create the button objects. 

        cat_profiles()

    def update_search_cats(self, search_text):
        '''Run this function when the search text changes, or when the screen is switched to.'''
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
        '''Run this function when page changes.'''
        
        #If the number of pages becomes smaller than the number of our current page, set 
        #   the current page to the last page
        if self.list_page > self.all_pages:
            self.list_page = self.all_pages

        #Handle which next buttons are clickable. 
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
        self.page_number = pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" +str(self.list_page) + "/" + 
                                                        str(self.all_pages) + "</font>",
                                                            pygame.Rect((340,595),(110,30)))

        #Remove the images for currently listed cats
        for cat in self.display_cats:
            cat.kill()

        for name in self.cat_names:
            name.kill()
        
        #Generate object for the current cats
        pos_x = 0
        pos_y = 0
        #print(self.current_listed_cats)
        if self.current_listed_cats != []:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:
                update_sprite(cat)
                self.display_cats.append(UISpriteButton(pygame.Rect((130 + pos_x, 180 + pos_y),(50,50)),cat.sprite, cat.ID))

                name = str(cat.name)
                if len(name) >= 13:
                    short_name = str(cat.name)[0:12]
                    name = short_name + '...'
                self.cat_names.append(pygame_gui.elements.UITextBox("<font color='#FFFFFF'>" + name + "</font>"
                                                    ,pygame.Rect((80 + pos_x, 230 + pos_y),(150,30))))
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

    def on_use(self):
        bg = self.df_bg
        screen.blit(bg, (0, 0))

        #Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        screen.blit(bg, (0, 0))

        screen.blit(ListScreen.search_bar, (452, 135))
    
    def chunks(self, L, n): return [L[x: x+n] for x in range(0, len(L), n)]