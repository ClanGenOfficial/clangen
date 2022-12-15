import re
from random import choice
import pygame_gui

from .base_screens import Screens, draw_menu_buttons, cat_profiles

from scripts.events import events_class
from scripts.patrol import patrol
from scripts.utility import draw, get_text_box_theme
from scripts.game_structure.buttons import buttons
from scripts.game_structure.text import *
from scripts.game_structure.image_button import UIImageButton

class SingleEventScreen(Screens):

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

            #Change the type of events displayed
            elif event.ui_element == self.relationship_events_button:
                self.event_display_type = "relationship events"
                self.clan_events_button.enable()
                self.relationship_events_button.disable()
                #Update Display
                self.display_events = self.relation_events
                self.update_events_display()
            elif event.ui_element == self.clan_events_button:
                self.event_display_type = "clan events"
                self.clan_events_button.disable()
                self.relationship_events_button.enable()
                #Update Display
                self.display_events = self.clan_events
                self.update_events_display()
            else:
                self.menu_button_pressed(event) 

    def screen_switches(self):
        cat_profiles()

        self.heading = pygame_gui.elements.UITextBox("Check this page to which event are currently happening in the "
                                                     "Clan",
                                                     pygame.Rect((100,110), (600, 40)),
                                                     object_id=get_text_box_theme())
        self.season = pygame_gui.elements.UITextBox(f'Current season: {str(game.clan.current_season)}',
                                                    pygame.Rect((100 ,140), (600, 40)),
                                                    object_id=get_text_box_theme())
        self.clan_age = pygame_gui.elements.UITextBox("",
                                                    pygame.Rect((100, 170), (600, 40)),
                                                      object_id=get_text_box_theme())
        # Set text for clan age
        if game.clan.age == 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moon')
        if game.clan.age != 1:
            self.clan_age.set_text(f'Clan age: {str(game.clan.age)} moons')

        self.timeskip_button = UIImageButton(pygame.Rect((310, 205),(180, 30)), "", object_id = "#timeskip_button")
        if game.clan.closed_borders == True:
            self.toggle_borders_button = pygame_gui.elements.UIButton(pygame.Rect((500,210),(200, 30)), "Open Clan orders")
        else:
            self.toggle_borders_button = pygame_gui.elements.UIButton(pygame.Rect((500,210),(200, 30)), "Close Clan Borders")
        
        #Sets up the buttons to switch between the event types. 
        self.clan_events_button = UIImageButton(pygame.Rect((224, 245),(176, 30)), "", object_id = "#clan_events_button")
        self.relationship_events_button = UIImageButton(pygame.Rect((400, 245),(176, 30)), "", object_id = "#relationship_events_button")
        if self.event_display_type == "clan events":
            self.clan_events_button.disable() 
        elif self.event_display_type == "relationship events":
            self.relationship_events_button.disable() 

        self.events_list_box = pygame_gui.elements.UITextBox(self.display_events, pygame.Rect((100,290),(600,400)),
                                                             object_id=get_text_box_theme())

        # Display text
        #self.explain_text = pygame_gui.elements.UITextBox(self.display_text, pygame.Rect((25,110),(750,40)))

        #Draw and disable the correct menu buttons. 
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


class PatrolEventScreen(Screens):

    def handle_event(self, event):
        # random_options = []
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_9:
                for u in range(12):
                    i_max = len(game.patrol_cats)
                    if u < i_max:
                        game.switches['current_patrol'].append(
                            game.patrol_cats[u])

    event_bg = pygame.image.load("resources/images/patrol_event_frame.png").convert_alpha()
    info_bg = pygame.image.load("resources/images/patrol_info.png").convert_alpha()
    image_frame = pygame.image.load("resources/images/patrol_sprite_frame.png").convert_alpha()

    def get_list_text(self, patrol_list):
        if not patrol_list:
            return "None"
        # Removes duplicates.
        patrol_set = list(patrol_list)
        return ", ".join(patrol_set)

    def text_adjust(self, text, size=1):
        """
        set text parameter to whichever patrol text you want to change (i.e. intro_text, success_text, ect.)
        always set size to patrol_size
        """
        vowels = ['A', 'E', 'I', 'O', 'U']
        if size == 1:
            text = text.replace('Your patrol',
                                            str(patrol.patrol_leader.name))
            text = text.replace('The patrol',
                                            str(patrol.patrol_leader.name))
        text = text.replace('r_c', str(patrol.patrol_random_cat.name))
        text = text.replace('p_l', str(patrol.patrol_leader.name))
        text = text.replace('app1', str(patrol.app1_name))
        text = text.replace('app2', str(patrol.app2_name))

        if patrol.patrol_stat_cat is not None:
            text = text.replace('s_c', str(patrol.patrol_stat_cat.name))

        other_clan_name = patrol.other_clan.name
        s = 0
        text = re.sub(r".,'?!", '', text)
        for x in range(text.count('o_c_n')):
            index = text.index('o_c_n', s)
            for y in vowels:
                if str(other_clan_name).startswith(y):
                    modify = text.split()
                    pos = modify.index('o_c_n')
                    if modify[pos-1] == 'a':
                        modify.remove('a')
                        modify.insert(pos-1, 'an')
                    text = " ".join(modify)
                    break
            s += index + 3

        text = text.replace('o_c_n', str(other_clan_name) + 'Clan')

        clan_name = game.clan.name
        s = 0
        pos = 0
        for x in range(text.count('c_n')):
            index = text.index('c_n', s)
            for y in vowels:
                if str(clan_name).startswith(y):
                    modify = text.split()
                    if 'c_n' in modify:
                        pos = modify.index('c_n')
                    elif "c_n's" in modify:
                        pos = modify.index("c_n's")
                    if 'c_n.' in modify:
                        pos = modify.index('c_n.')
                    if modify[pos-1] == 'a':
                        modify.remove('a')
                        modify.insert(pos-1, 'an')
                    text = " ".join(modify)
                    break
            s += index + 3

        text = text.replace('c_n', str(game.clan.name) + 'Clan')


        return text

    def on_use(self):
        # USER INTERFACE
        draw_clan_name()
        screen.blit(PatrolEventScreen.event_bg, (381, 165))
        screen.blit(PatrolEventScreen.info_bg, (90, 456))
        screen.blit(PatrolEventScreen.image_frame, (65, 140))

        if game.switches['event'] == 0:
            patrol.add_patrol_cats()
            possible_events = patrol.get_possible_patrols(
                game.clan.current_season.lower(),
                game.clan.biome.lower(),
                game.clan.all_clans,
                game.switches['patrol_chosen'],
                game.settings.get('disasters')
            )
            print(len(possible_events))
            patrol.patrol_event = choice(possible_events)

            game.switches['event'] = -1

        if game.switches['event'] == -1:
            intro_text = patrol.patrol_event.intro_text
            patrol_size = len(patrol.patrol_cats)

            # adjusting text for solo patrols
            intro_text = self.text_adjust(intro_text, patrol_size)

            verdana_dark.blit_text(intro_text,
                              (390, 185),
                              x_limit=715)

            if game.switches['patrol_done'] is False:
                buttons.draw_button((550, 433),
                                    image='buttons/proceed',
                                    text='Proceed',
                                    patrol_done=True,
                                    event=-2)
                buttons.draw_button((550, 461),
                                    image='buttons/do_not_proceed',
                                    text='Do Not Proceed',
                                    patrol_done=True,
                                    event=2)

                if patrol.patrol_event.antagonize_text != None:
                    buttons.draw_button((550, 491),
                                        image='buttons/antagonize',
                                        text='Antagonize',
                                        patrol_done=True,
                                        event=3)

        if game.switches['event'] == -2:
            patrol.calculate_success()
            game.switches['event'] = 1

        elif game.switches['event'] == 3:
            patrol.calculate_success(antagonize=True)
            game.switches['event'] = 4

        if game.switches['event'] > 0:
            if game.switches['event'] == 1:
                if patrol.success:
                    success_text = patrol.final_success
                    patrol_size = len(patrol.patrol_cats)
                    success_text = self.text_adjust(success_text, patrol_size)

                    verdana_dark.blit_text(success_text,
                                      (390, 185),
                                      x_limit=715)

                else:
                    fail_text = patrol.final_fail
                    patrol_size = len(patrol.patrol_cats)
                    fail_text = self.text_adjust(fail_text, patrol_size)

                    verdana_dark.blit_text(fail_text,
                                      (390, 185),
                                      x_limit=715)

            elif game.switches['event'] == 2:
                decline_text = patrol.patrol_event.decline_text
                patrol_size = len(patrol.patrol_cats)
                decline_text = self.text_adjust(decline_text, patrol_size)

                verdana_dark.blit_text(decline_text,
                                  (390, 185),
                                  x_limit=715)

            elif game.switches['event'] == 4:
                antagonize_text = patrol.patrol_event.antagonize_text
                patrol_size = len(patrol.patrol_cats)

                if patrol.success:
                    antagonize_text = self.text_adjust(antagonize_text, patrol_size)
                else:
                    antagonize_fail_text = patrol.patrol_event.antagonize_fail_text
                    antagonize_text = self.text_adjust(antagonize_fail_text, patrol_size)

                verdana_dark.blit_text(antagonize_text,
                                  (390, 185),
                                  x_limit=715)

            if game.switches['patrol_done'] is True:
                buttons.draw_image_button((400, 137),
                                          button_name='back_to_clan',
                                          text='Return to Clan',
                                          size=(162, 30),
                                          cur_screen='clan screen',
                                          patrol_done=False)
                buttons.draw_image_button((560, 137),
                                          button_name='patrol_again',
                                          text='Patrol Again',
                                          size=(162, 30),
                                          cur_screen='patrol screen',
                                          patrol_done=False)

                buttons.draw_button((550, 433),
                                    image='buttons/proceed',
                                    text='Proceed',
                                    patrol_done=True,
                                    available=False,
                                    event=-2)
                buttons.draw_button((550, 461),
                                    image='buttons/do_not_proceed',
                                    text='Do Not Proceed',
                                    patrol_done=True,
                                    available=False,
                                    event=2)
        pos_x = 0
        pos_y = 0
        for u in range(6):
            if u < len(patrol.patrol_cats):
                draw(patrol.patrol_cats[u],
                     (400 + pos_x, 475 + pos_y))
                pos_x += 50
                if pos_x > 50:
                    pos_y += 50
                    pos_x = 0

        # TEXT CATEGORIES AND CHECKING FOR REPEATS
        members = []
        skills = []
        traits = []
        for x in patrol.patrol_names:
            if x not in patrol.patrol_leader_name:
                members.append(x)
        for x in patrol.patrol_skills:
            if x not in skills:
                skills.append(x)
        for x in patrol.patrol_traits:
            if x not in traits:
                traits.append(x)


        verdana_small_dark.blit_text(
                                f'patrol leader: {patrol.patrol_leader_name} \n'
                                f'patrol members: {self.get_list_text(members)} \n'
                                f'patrol skills: {self.get_list_text(skills)} \n'
                                f'patrol traits: {self.get_list_text(traits)}',
                                (105, 460),
                                x_limit=345,
                                line_break=25)

        draw_menu_buttons()

    def screen_switches(self):
        game.switches['event'] = 0
        game.switches['patrol_done'] = False
        if game.switches['patrol_chosen'] == 'med':
            game.switches['patrol_chosen'] = 'general'
        cat_profiles()

