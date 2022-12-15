from scripts.utility import update_sprite
from scripts.cat.cats import Cat
from scripts.game_structure.buttons import Button, buttons
from scripts.game_structure.game_essentials import *
from scripts.clan import map_available
from scripts.game_structure.text import *
import scripts.game_structure.image_cache as image_cache
from scripts.game_structure.image_button import UIImageButton
import pygame_gui


class Screens():
    game_screen = screen
    game_x = screen_x
    game_y = screen_y
    last_screen = ''

    menu_buttons = {
        "events_screen" : UIImageButton(pygame.Rect((246, 60),(82, 30)), "", visible = False, object_id = "#events_menu_button"),
        "clan_screen" : UIImageButton(pygame.Rect((328, 60),(58, 30)), "", visible = False, object_id = "#clan_menu_button"),
        "starclan_screen" : UIImageButton(pygame.Rect((386, 60),(88, 30)), "", visible = False, object_id = "#starclan_menu_button"),
        "patrol_screen" : UIImageButton(pygame.Rect((474, 60),(80, 30)), "", visible = False, object_id = "#patrol_menu_button"),
        "main_menu" : UIImageButton(pygame.Rect((25, 25),(153, 30)), "", visible = False, object_id = "#main_menu_button"),
        "list_screen" : UIImageButton(pygame.Rect((676, 60),(99, 30)), "", visible = False, object_id = "#list_button"),
        "allegiances" : UIImageButton(pygame.Rect((657, 25),(118, 30)), "", visible = False, object_id = "#allegiances_button"),
        "stats" : UIImageButton(pygame.Rect((25, 60),(81, 30)), "", visible = False, object_id = "#stats_button"),
        "name_background": pygame_gui.elements.UIImage(pygame.Rect((310,25),(180,35)), image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), visible= False),
        "heading": pygame_gui.elements.UITextBox("", pygame.Rect((310,27),(180,35)), visible=False, object_id=  "#menu_header_text_box")
        }


    def change_screen(self,new_screen):
        '''Use this function when switching screens. 
            It will handle keeping track of the last screen and cur screen. 
            Last screen must be tracked to ensure a clear transition between screens.'''
        #self.exit_screen()
        game.last_screen_forupdate = self.name
        
        #This keeps track of the last list-like screen for the back button on cat profiles
        if self.name in ['clan screen','list screen','starclan screen','dark forest screen']:
            game.last_screen_forProfile = self.name

        game.switches['cur_screen'] = new_screen
        game.switch_screens = True

    def __init__(self, name=None):
        self.name = name
        if name is not None:
            game.all_screens[name] = self

    def fill(self, tuple):
        pygame.Surface.fill(color=tuple)

    def on_use(self):
        """Runs every frame this screen is used."""
        pass

    def screen_switches(self):
        """Runs when this screen is switched to."""
        pass

    def handle_event(self, event):
        '''This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. '''
        pass

    def exit_screen(self):
        '''Runs when screen exits'''
        pass

    #Functions to deal with the menu.
    #   The menu is used very often, so I don't want to keep
    #   recreating and killing it. Lots of changes for bugs there. 
    #   

    def hide_menu_buttons(self):
        '''This hides the menu buttons, so they are no longer visable
            or interactable. It does not delete the buttons from memory.'''
        for button in self.menu_buttons:
            self.menu_buttons[button].hide()

    def show_menu_buttons(self):
        '''This shows all menu buttons, and makes them interactable. '''
        for button in self.menu_buttons:
            self.menu_buttons[button].show()
    
    #Enables all menu buttons but the ones passed in.
    #Sloppy, but works. Consiter making it nicer. 
    def set_disabled_menu_buttons(self, disabled_buttons = []):
        '''This sets all menu buttons as interactable, except buttons listed in disabled_buttons.  '''
        for button in self.menu_buttons:
            self.menu_buttons[button].enable()

        for button_id in disabled_buttons:
            if button_id in self.menu_buttons:
                self.menu_buttons[button_id].disable()

    def menu_button_pressed(self,event):
        '''This is a short-up to deal with menu button presses. 
            This will fail is event.type != pygame_gui.UI_BUTTON_START_PRESS'''
        if event.ui_element == self.menu_buttons["events_screen"]:
            self.change_screen('events screen')
        elif event.ui_element == self.menu_buttons["clan_screen"]:
            self.change_screen('clan screen')
        elif event.ui_element == self.menu_buttons["starclan_screen"]:
            self.change_screen('starclan screen')
        elif event.ui_element == self.menu_buttons["patrol_screen"]:
            self.change_screen('patrol screen')
        elif event.ui_element == self.menu_buttons["main_menu"]:
            self.change_screen('start screen')
        elif event.ui_element == self.menu_buttons["list_screen"]:
            self.change_screen('list screen')
        elif event.ui_element == self.menu_buttons["allegiances"]:
            self.change_screen('allegiances screen')
        elif event.ui_element == self.menu_buttons["stats"]:
            self.change_screen('stats screen')

    def update_heading_text(self, text):
        '''Updates the menu heading text'''
        self.menu_buttons['heading'].set_text(text)
        
 
# CAT PROFILES
def cat_profiles():
    game.choose_cats.clear()
    game.cat_buttons.clear()
    for x in game.clan.clan_cats:
        game.choose_cats[x] = Cat.all_cats[x]
        update_sprite(game.choose_cats[x])


# ---------------------------------------------------------------------------- #
#                               menu buttons                                   #
# ---------------------------------------------------------------------------- #
def draw_menu_buttons():
    buttons.draw_image_button((246, 60),
                              button_name='events',
                              text='EVENTS',
                              cur_screen='events screen',
                              size=(82, 30),
                              hotkey=[2])
    buttons.draw_image_button((328, 60),
                              button_name='clan',
                              text='CLAN',
                              cur_screen='clan screen',
                              size=(58, 30),
                              hotkey=[3])

    if game.clan.instructor.df is False:
        buttons.draw_image_button((386, 60),
                                  button_name='starclan',
                                  text='STARCLAN',
                                  cur_screen='starclan screen',
                                  size=(88, 30),
                                  hotkey=[4])
    else:
        buttons.draw_image_button((386, 60),
                                  button_name='starclan',
                                  text='STARCLAN',
                                  cur_screen='dark forest screen',
                                  size=(88, 30),
                                  hotkey=[4])

    buttons.draw_image_button((474, 60),
                              button_name='patrol',
                              text='PATROL',
                              cur_screen='patrol screen',
                              size=(80, 30),
                              hotkey=[5])
    buttons.draw_image_button((25, 25),
                              button_name='main_menu',
                              text='< Back to Main Menu',
                              cur_screen='start screen',
                              size=(153, 30),
                              hotkey=[0])
    buttons.draw_image_button((676, 60),
                              button_name='list_cats',
                              text='List Cats',
                              cur_screen='list screen',
                              size=(99, 30),
                              hotkey=[6])
    buttons.draw_image_button((657, 25),
                              button_name='allegiances',
                              text='Allegiances',
                              cur_screen='allegiances screen',
                              size=(118, 30),
                              hotkey=[7])
    buttons.draw_image_button((25, 60),
                              button_name='stats',
                              text='Stats',
                              cur_screen='stats screen',
                              size=(81, 30),
                              hotkey=[1])

# ---------------------------------------------------------------------------- #
#                    next and previous cat buttons                             #
# ---------------------------------------------------------------------------- #
def draw_next_prev_cat_buttons(the_cat):
    is_instructor = False
    if the_cat.dead and game.clan.instructor.ID == the_cat.ID:
        is_instructor = True

    previous_cat = 0
    next_cat = 0
    if the_cat.dead and not is_instructor and not the_cat.df:
        previous_cat = game.clan.instructor.ID

    if is_instructor:
        next_cat = 1

    for check_cat in Cat.all_cats:
        if Cat.all_cats[check_cat].ID == the_cat.ID:
            next_cat = 1

        if the_cat.outside or the_cat.exiled:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and (Cat.all_cats[
                                check_cat].outside or Cat.all_cats[
                                check_cat].exiled) and Cat.all_cats[check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and (Cat.all_cats[
                                check_cat].outside or Cat.all_cats[
                                check_cat].exiled) and Cat.all_cats[check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

        elif game.switches['apprentice'] is not None:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].outside and Cat.all_cats[check_cat].mentor is not None and Cat.all_cats[
                    check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].outside and Cat.all_cats[check_cat].mentor is not None and Cat.all_cats[
                    check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

        elif game.switches['choosing_mate'] is True:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].outside and Cat.all_cats[
                                    check_cat].status not in ['apprentice', 'medicine cat apprentice', 'kitten'] and Cat.all_cats[
                    check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].outside and Cat.all_cats[
                                    check_cat].status not in ['apprentice', 'medicine cat apprentice', 'kitten'] and Cat.all_cats[
                    check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

        else:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].outside and Cat.all_cats[
                    check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].outside and Cat.all_cats[
                    check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

    if next_cat == 1:
        next_cat = 0

# ---------------------------------------------------------------------------- #
#                               the buttons                                    #
# ---------------------------------------------------------------------------- #
    if next_cat != 0:
        buttons.draw_image_button((622, 25),
                                  button_name='next_cat',
                                  text='Next Cat',
                                  cat=next_cat,
                                  size=(153, 30),
                                  hotkey=[21],
                                  show_details=False,
                                  chosen_cat=None,
                                  mate=None
                                  )
    else:
        buttons.draw_image_button((622, 25),
                                  button_name='next_cat',
                                  text='Next Cat',
                                  cat=next_cat,
                                  size=(153, 30),
                                  hotkey=[21],
                                  show_details=False,
                                  available=False
                                  )
    if previous_cat != 0:
        buttons.draw_image_button((25, 25),
                                  button_name='previous_cat',
                                  text='Previous Cat',
                                  cat=previous_cat,
                                  size=(153, 30),
                                  hotkey=[23],
                                  show_details=False,
                                  mate=None
                                  )
    else:
        buttons.draw_image_button((25, 25),
                                  button_name='previous_cat',
                                  text='Previous Cat',
                                  cat=previous_cat,
                                  size=(153, 30),
                                  hotkey=[23],
                                  available=False
                                  )

