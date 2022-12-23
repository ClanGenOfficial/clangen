import re
from random import choice
import pygame_gui

from .base_screens import Screens, cat_profiles
import pygame
from scripts.events import events_class
from scripts.utility import draw, get_text_box_theme, get_living_cat_count
# from scripts.game_structure.text import *
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import *
from ..cat.cats import Cat
from ..game_structure import image_cache


class EventsScreen(Screens):
    event_display_type = "all events"
    all_events = ""
    ceremony_events = ""
    birth_death_events = ""
    relation_events = ""
    health_events = ""
    other_clans_events = ""
    misc_events = ""
    display_text = "<center> Check this page to see which events are currently happening at the Clan.</center>"
    display_events = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.misc_alert = None
        self.other_clans_alert = None
        self.health_alert = None
        self.relation_alert = None
        self.birth_death_alert = None
        self.ceremony_alert = None
        self.misc_events_button = None
        self.other_clans_events_button = None
        self.health_events_button = None
        self.birth_death_events_button = None
        self.ceremonies_events_button = None
        self.all_events_button = None
        self.relationship_events_button = None
        self.events_list_box = None
        self.toggle_borders_button = None
        self.timeskip_button = None
        self.events_frame = None
        self.clan_age = None
        self.season = None
        self.heading = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.timeskip_button:
                events_class.one_moon()
                if get_living_cat_count(Cat) == 0:
                    GameOver('events screen')

                # print(get_living_cat_count(Cat))
                self.all_events = ""
                self.event_display_type = 'all events'
                self.all_events_button.disable()
                if game.cur_events_list is not None and game.cur_events_list != []:
                    for i in range(len(game.cur_events_list)):
                        if not isinstance(game.cur_events_list[i], str):
                            game.cur_events_list.remove(game.cur_events_list[i])
                            break
                    self.all_events = '\n\n'.join(game.cur_events_list)
                else:
                    self.all_events = "Nothing significant happened this moon"

                self.ceremony_events = ""
                self.ceremonies_events_button.enable()
                if self.ceremony_alert:
                    self.ceremony_alert.kill()
                if game.ceremony_events_list is not None and game.ceremony_events_list != []:
                    for i in range(len(game.ceremony_events_list)):
                        if not isinstance(game.ceremony_events_list[i], str):
                            game.ceremony_events_list.remove(game.ceremony_events_list[i])
                            break
                    self.ceremony_events = '\n\n'.join(game.ceremony_events_list)

                    self.ceremony_alert = pygame_gui.elements.UIImage(pygame.Rect((44, 340), (4, 22)),
                                                                      image_cache.load_image(
                                                                          "resources/images/alert_mark.png"
                                                                      ))

                self.birth_death_events = ""
                if self.birth_death_alert:
                    self.birth_death_alert.kill()
                self.birth_death_events_button.enable()
                if game.birth_death_events_list is not None and game.birth_death_events_list != []:
                    for i in range(len(game.birth_death_events_list)):
                        if not isinstance(game.birth_death_events_list[i], str):
                            game.birth_death_events_list.remove(game.birth_death_events_list[i])
                            break
                    self.birth_death_events = '\n\n'.join(game.birth_death_events_list)
                    self.birth_death_alert = pygame_gui.elements.UIImage(pygame.Rect((44, 390), (4, 22)),
                                                                         image_cache.load_image(
                                                                             "resources/images/alert_mark.png"
                                                                         ))

                self.relation_events = ""
                if self.relation_alert:
                    self.relation_alert.kill()
                self.relationship_events_button.enable()
                if game.relation_events_list is not None and game.relation_events_list != []:
                    for i in range(len(game.relation_events_list)):
                        if not isinstance(game.relation_events_list[i], str):
                            game.relation_events_list.remove(game.relation_events_list[i])
                            break
                    self.relation_events = '\n\n'.join(game.relation_events_list)
                    self.relation_alert = pygame_gui.elements.UIImage(pygame.Rect((44, 440), (4, 22)),
                                                                      image_cache.load_image(
                                                                          "resources/images/alert_mark.png"
                                                                      ))

                self.health_events = ""
                if self.health_alert:
                    self.health_alert.kill()
                self.health_events_button.enable()
                if game.health_events_list is not None and game.health_events_list != []:
                    for i in range(len(game.health_events_list)):
                        if not isinstance(game.health_events_list[i], str):
                            game.health_events_list.remove(game.health_events_list[i])
                            break
                    self.health_events = '\n\n'.join(game.health_events_list)
                    self.health_alert = pygame_gui.elements.UIImage(pygame.Rect((44, 490), (4, 22)),
                                                                    image_cache.load_image(
                                                                        "resources/images/alert_mark.png"
                                                                    ))

                self.other_clans_events = ""
                if self.other_clans_alert:
                    self.other_clans_alert.kill()
                self.other_clans_events_button.enable()
                if game.other_clans_events_list is not None and game.other_clans_events_list != []:
                    for i in range(len(game.other_clans_events_list)):
                        if not isinstance(game.other_clans_events_list[i], str):
                            game.other_clans_events_list.remove(game.other_clans_events_list[i])
                            break
                    self.other_clans_events = '\n\n'.join(game.other_clans_events_list)
                    self.other_clans_alert = pygame_gui.elements.UIImage(pygame.Rect((44, 540), (4, 22)),
                                                                         image_cache.load_image(
                                                                             "resources/images/alert_mark.png"
                                                                         ))

                self.misc_events = ""
                if self.misc_alert:
                    self.misc_alert.kill()
                self.misc_events_button.enable()
                if game.misc_events_list is not None and game.misc_events_list != []:
                    for i in range(len(game.misc_events_list)):
                        if not isinstance(game.misc_events_list[i], str):
                            game.misc_events_list.remove(game.misc_events_list[i])
                            break
                    self.misc_events = '\n\n'.join(game.misc_events_list)
                    self.misc_alert = pygame_gui.elements.UIImage(pygame.Rect((44, 590), (4, 22)),
                                                                  image_cache.load_image(
                                                                      "resources/images/alert_mark.png"
                                                                  ))

                if self.event_display_type == "all events":
                    self.display_events = self.all_events
                elif self.event_display_type == "ceremony events":
                    self.display_events = self.ceremony_events
                elif self.event_display_type == "birth death events":
                    self.display_events = self.birth_death_events
                elif self.event_display_type == "relationship events":
                    self.display_events = self.relation_events
                elif self.event_display_type == "health events":
                    self.display_events = self.health_events
                elif self.event_display_type == "other clans events":
                    self.display_events = self.other_clans_events
                elif self.event_display_type == "misc events":
                    self.display_events = self.misc_events

                self.update_events_display()

            elif event.ui_element == self.toggle_borders_button:
                if game.clan.closed_borders:
                    game.clan.closed_borders = False
                    self.toggle_borders_button.set_text("Close Clan Borders")
                else:
                    game.clan.closed_borders = True
                    self.toggle_borders_button.set_text("Open Clan Borders")

            # Change the type of events displayed
            elif event.ui_element == self.all_events_button:
                self.event_display_type = "all events"
                # Update Display
                self.update_list_buttons(self.all_events_button)
                self.display_events = self.all_events
                self.update_events_display()
            elif event.ui_element == self.ceremonies_events_button:
                self.event_display_type = "ceremony events"
                self.ceremonies_events_button.disable()
                # Update Display
                self.update_list_buttons(self.ceremonies_events_button, self.ceremony_alert)
                self.display_events = self.ceremony_events
                self.update_events_display()
            elif event.ui_element == self.birth_death_events_button:
                self.event_display_type = "birth death events"
                self.birth_death_events_button.enable()
                # Update Display
                self.update_list_buttons(self.birth_death_events_button, self.birth_death_alert)
                self.display_events = self.birth_death_events
                self.update_events_display()
            elif event.ui_element == self.relationship_events_button:
                self.event_display_type = "relationship events"
                self.relationship_events_button.enable()
                # Update Display
                self.update_list_buttons(self.relationship_events_button, self.relation_alert)
                self.display_events = self.relation_events
                self.update_events_display()
            elif event.ui_element == self.health_events_button:
                self.event_display_type = "health events"
                self.health_events_button.disable()
                # Update Display
                self.update_list_buttons(self.health_events_button, self.health_alert)
                self.display_events = self.health_events
                self.update_events_display()
            elif event.ui_element == self.other_clans_events_button:
                self.event_display_type = "other clans events"
                self.other_clans_events_button.disable()
                # Update Display
                self.update_list_buttons(self.other_clans_events_button, self.other_clans_alert)
                self.display_events = self.other_clans_events
                self.update_events_display()
            elif event.ui_element == self.misc_events_button:
                self.event_display_type = "misc events"
                self.misc_events_button.disable()
                # Update Display
                self.update_list_buttons(self.misc_events_button, self.misc_alert)
                self.display_events = self.misc_events
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
        self.events_frame = pygame_gui.elements.UIImage(pygame.Rect((206, 266), (534, 370)),
                                                        image_cache.load_image(
                                                            "resources/images/event_page_frame.png").convert_alpha())
        self.events_frame.disable()
        # Set text for clan age
        if game.clan.age == 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moon')
        if game.clan.age != 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moons')

        self.timeskip_button = UIImageButton(pygame.Rect((310, 205), (180, 30)), "", object_id="#timeskip_button")
        if game.clan.closed_borders:
            self.toggle_borders_button = pygame_gui.elements.UIButton(pygame.Rect((500, 210), (200, 30)),
                                                                      "Open Clan Borders")
        else:
            self.toggle_borders_button = pygame_gui.elements.UIButton(pygame.Rect((500, 210), (200, 30)),
                                                                      "Close Clan Borders")

        # Sets up the buttons to switch between the event types.
        self.all_events_button = UIImageButton(
            pygame.Rect((60, 286,), (150, 30)),
            "",
            object_id="#all_events_button")
        self.ceremonies_events_button = UIImageButton(
            pygame.Rect((60, 336), (150, 30)),
            "",
            object_id="#ceremony_events_button")
        self.birth_death_events_button = UIImageButton(
            pygame.Rect((60, 386), (150, 30)),
            "",
            object_id="#birth_death_events_button")
        self.relationship_events_button = UIImageButton(
            pygame.Rect((60, 436), (150, 30)),
            "",
            object_id="#relationship_events_button")
        self.health_events_button = UIImageButton(
            pygame.Rect((60, 486), (150, 30)),
            "",
            object_id="#health_events_button")
        self.other_clans_events_button = UIImageButton(
            pygame.Rect((60, 536), (150, 30)),
            "",
            object_id="#other_clans_events_button")
        self.misc_events_button = UIImageButton(
            pygame.Rect((60, 586), (150, 30)),
            "",
            object_id="#misc_events_button")

        if self.event_display_type == "all events":
            self.all_events_button.disable()
        elif self.event_display_type == "ceremony events":
            self.ceremonies_events_button.disable()
        elif self.event_display_type == "birth death events":
            self.birth_death_events_button.disable()
        elif self.event_display_type == "relationship events":
            self.relationship_events_button.disable()
        elif self.event_display_type == "health events":
            self.health_events_button.disable()
        elif self.event_display_type == "other clans events":
            self.other_clans_events_button.disable()
        elif self.event_display_type == "misc events":
            self.misc_events_button.disable()

        self.misc_alert = None
        self.other_clans_alert = None
        self.health_alert = None
        self.relation_alert = None
        self.birth_death_alert = None
        self.ceremony_alert = None

        self.events_list_box = pygame_gui.elements.UITextBox(
            self.display_events,
            pygame.Rect((218, 271), (514, 360)),
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
        self.all_events_button.kill()
        del self.all_events_button
        self.ceremonies_events_button.kill()
        del self.ceremonies_events_button
        if self.ceremony_alert:
            self.ceremony_alert.kill()
            del self.ceremony_alert
        self.birth_death_events_button.kill()
        del self.birth_death_events_button
        if self.birth_death_alert:
            self.birth_death_alert.kill()
            del self.birth_death_alert
        self.relationship_events_button.kill()
        del self.relationship_events_button
        if self.relation_alert:
            self.relation_alert.kill()
            del self.relation_alert
        self.health_events_button.kill()
        del self.health_events_button
        if self.health_alert:
            self.health_alert.kill()
            del self.health_alert
        self.other_clans_events_button.kill()
        del self.other_clans_events_button
        if self.other_clans_alert:
            self.other_clans_alert.kill()
            del self.other_clans_alert
        self.misc_events_button.kill()
        del self.misc_events_button
        if self.misc_alert:
            self.misc_alert.kill()
            del self.misc_alert
        self.events_frame.kill()
        del self.events_frame
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

    def update_list_buttons(self, current_list, current_alert=None):
        """ handles the disabling and enabling of the list buttons """

        # enable all the buttons
        self.all_events_button.enable()
        self.ceremonies_events_button.enable()
        self.birth_death_events_button.enable()
        self.relationship_events_button.enable()
        self.health_events_button.enable()
        self.other_clans_events_button.enable()
        self.misc_events_button.enable()

        # disable the current button
        current_list.disable()
        if current_alert:
            current_alert.kill()

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
