import re
from random import choice
import pygame_gui

from .base_screens import Screens, cat_profiles
import pygame
from scripts.events import events_class
from scripts.utility import draw, get_text_box_theme
#from scripts.game_structure.text import *
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import *

class EventsScreen(Screens):
    event_display_type = "clan events"
    clan_events = ""
    relation_events = ""
    display_text = "<center> Check this page to see which events are currently happening at the Clan.</center>"
    display_events = ""

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.timeskip_button:
                events_class.one_moon()
                if game.cur_events_list is not None and game.cur_events_list != []:
                    for i in range(len(game.cur_events_list)):
                        if not isinstance(game.cur_events_list[i], str):
                            game.cur_events_list.remove(game.cur_events_list[i])
                            break
                    self.clan_events = '\n\n'.join(game.cur_events_list)
                else:
                    self.clan_events = "Nothing significant happened this moon"

                if game.relation_events_list is not None and game.relation_events_list != []:
                    for i in range(len(game.relation_events_list)):
                        if not isinstance(game.relation_events_list[i], str):
                            game.game.relation_events_list(game.relation_events_list[i])
                            break
                    self.relation_events = '\n'.join(game.relation_events_list)
                else:
                    self.relation_events = "Nothing significant happened this moon."

                if self.event_display_type == "clan events":
                    self.display_events = self.clan_events
                elif self.event_display_type == "relationship events":
                    self.display_events = self.relation_events

                self.update_events_display()

            elif event.ui_element == self.toggle_borders_button:
                if game.clan.closed_borders == True:
                    game.clan.closed_borders = False
                    self.toggle_borders_button.set_text("Close Clan Borders")
                else:
                    game.clan.closed_borders = True
                    self.toggle_borders_button.set_text("Open Clan Borders")

            # Change the type of events displayed
            elif event.ui_element == self.relationship_events_button:
                self.event_display_type = "relationship events"
                self.clan_events_button.enable()
                self.relationship_events_button.disable()
                # Update Display
                self.display_events = self.relation_events
                self.update_events_display()
            elif event.ui_element == self.clan_events_button:
                self.event_display_type = "clan events"
                self.clan_events_button.disable()
                self.relationship_events_button.enable()
                # Update Display
                self.display_events = self.clan_events
                self.update_events_display()
            else:
                self.menu_button_pressed(event)

    def screen_switches(self):
        cat_profiles()

        self.heading = pygame_gui.elements.UITextBox("Check this page to which event are currently happening in the "
                                                     "Clan",
                                                     pygame.Rect((100, 110), (600, 40)),
                                                     object_id=get_text_box_theme())
        self.season = pygame_gui.elements.UITextBox(f'Current season: {str(game.clan.current_season)}',
                                                    pygame.Rect((100, 140), (600, 40)),
                                                    object_id=get_text_box_theme())
        self.clan_age = pygame_gui.elements.UITextBox("",
                                                      pygame.Rect((100, 170), (600, 40)),
                                                      object_id=get_text_box_theme())
        # Set text for clan age
        if game.clan.age == 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moon')
        if game.clan.age != 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moons')

        self.timeskip_button = UIImageButton(pygame.Rect((310, 205), (180, 30)), "", object_id="#timeskip_button")
        if game.clan.closed_borders == True:
            self.toggle_borders_button = pygame_gui.elements.UIButton(pygame.Rect((500, 210), (200, 30)),
                                                                      "Open Clan orders")
        else:
            self.toggle_borders_button = pygame_gui.elements.UIButton(pygame.Rect((500, 210), (200, 30)),
                                                                      "Close Clan Borders")

        # Sets up the buttons to switch between the event types.
        self.clan_events_button = UIImageButton(pygame.Rect((224, 245), (176, 30)), "", object_id="#clan_events_button")
        self.relationship_events_button = UIImageButton(pygame.Rect((400, 245), (176, 30)), "",
                                                        object_id="#relationship_events_button")
        if self.event_display_type == "clan events":
            self.clan_events_button.disable()
        elif self.event_display_type == "relationship events":
            self.relationship_events_button.disable()

        self.events_list_box = pygame_gui.elements.UITextBox(self.display_events, pygame.Rect((100, 290), (600, 400)),
                                                             object_id=get_text_box_theme("#events_box"))

        # Display text
        # self.explain_text = pygame_gui.elements.UITextBox(self.display_text, pygame.Rect((25,110),(750,40)))

        # Draw and disable the correct menu buttons.
        self.set_disabled_menu_buttons(["events_screen"])
        self.show_menu_buttons()

    def exit_screen(self):
        self.timeskip_button.kill()
        del self.timeskip_button
        self.toggle_borders_button.kill()
        del self.toggle_borders_button
        self.clan_events_button.kill()
        del self.clan_events_button
        self.relationship_events_button.kill()
        del self.relationship_events_button
        self.events_list_box.kill()
        del self.events_list_box
        self.clan_age.kill()
        del self.clan_age
        self.heading.kill()
        del self.heading
        self.season.kill()
        del self.season
        # self.hide_menu_buttons()

    def on_use(self):
        # What does this do?
        if game.switches['events_left'] == 0:
            self.timeskip_button.enable()
        else:
            self.timeskip_button.disable()

    def update_events_display(self):
        self.events_list_box.set_text(self.display_events)
        self.season.set_text(f'Current season: {str(game.clan.current_season)}')
        if game.clan.age == 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moon')
        if game.clan.age != 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moons')


'''class SingleEventScreen(Screens):

    def on_use(self):
        # LAYOUT
        if game.switches['event'] is not None:
            events_class.all_events[game.switches['event']].page()

        # buttons
        buttons.draw_button(('center', -150),
                            text='Continue',
                            cur_screen='events screen')

    def screen_switches(self):
        pass
'''
