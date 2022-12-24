import pygame
from random import choice, randrange
import pygame_gui

from .base_screens import Screens

from scripts.utility import get_text_box_theme
from scripts.clan import Clan, map_available
from scripts.cat.cats import create_example_cats
from scripts.cat.names import names
from scripts.cat.sprites import tiles
from re import sub
import scripts.game_structure.image_cache as image_cache
# from scripts.world import World, save_map
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton
from scripts.game_structure.game_essentials import *
map_available = False


class MakeClanScreen(Screens):
    # UI images
    clan_frame_img = pygame.image.load(
        'resources/images/pick_clan_screen/clan_name_frame.png').convert_alpha()
    name_clan_img = pygame.image.load(
        'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha()
    leader_img = pygame.image.load(
        'resources/images/pick_clan_screen/leader_light.png').convert_alpha()
    deputy_img = pygame.image.load(
        'resources/images/pick_clan_screen/deputy_light.png').convert_alpha()
    medic_img = pygame.image.load(
        'resources/images/pick_clan_screen/med_light.png').convert_alpha()
    clan_img = pygame.image.load(
        'resources/images/pick_clan_screen/clan_light.png').convert_alpha()
    bg_preview_border = pygame.transform.scale(
        pygame.image.load("resources/images/bg_preview_border.png").convert_alpha(), (466, 416))

    classic_mode_text = "This mode is Clan Generator at it's most basic. " \
                        "The player will not be expected to manage the minutia of clan life. <br><br>" \
                        "Perfect for a relaxing game session or for focusing on storytelling. <br><br>" \
                        "With this mode you are the eye in the sky, watching the clan as their story unfolds. "

    expanded_mode_text = "A more hands-on experience. " \
                         "This mode has everything in Classic Mode as well as more management-focused features.<br><br>" \
                         "New features include:<br>" \
                         "- Illnesses, Injuries, and Permanent Conditions<br><br>" \
                         "- Ability to choose patrol type<br><br>" \
                         "With this mode you'll be making the important clan-life decisions."

    cruel_mode_text = "This mode has all the features of Expanded mode, but is significantly more difficult. If " \
                      "you'd like a challenge with a bit of brutality, then this mode is for you.<br><br>" \
                      "You heard the warnings... a Cruel Season is coming. Will you survive?"

    # This section holds all the information needed
    game_mode = 'classic'  # To save the users selection before conformation.
    clan_name = ""  # To store the clan name before conformation
    leader = None  # To store the clan leader before conformation
    deputy = None
    med_cat = None
    members = []
    elected_camp = None

    # Holds biome we have selected
    biome_selected = None
    selected_camp_tab = 1
    # Camp number selected
    camp_num = "1"
    # Holds the cat we have currently selected.
    selected_cat = None
    # Hold which sub-screen we are on
    sub_screen = 'game mode'
    # Holds which ranks we are currently selecting.
    choosing_rank = None
    # To hold the images for the sections. Makes it easier to kill them
    elements = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.menu_warning = None

    def screen_switches(self):
        # Reset variables
        self.game_mode = 'classic'
        self.clan_name = ""
        self.selected_camp_tab = 1
        self.biome_selected = None
        self.choosing_rank = None
        self.leader = None  # To store the clan leader before conformation
        self.deputy = None
        self.med_cat = None
        self.members = []

        # Buttons that appear on every screen.
        self.menu_warning = pygame_gui.elements.UITextBox(
            'Note: going back to main menu resets the generated cats.',
            pygame.Rect((25, 25), (600, -1)),
            object_id=get_text_box_theme("#cat_profile_info_box")
        )
        self.main_menu = UIImageButton(pygame.Rect((25, 50), (153, 30)), "", object_id="#main_menu_button")
        create_example_cats()
        # self.worldseed = randrange(10000)
        self.open_game_mode()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu:
                self.change_screen('start screen')
            if self.sub_screen == "game mode":
                self.handle_game_mode_event(event)
            elif self.sub_screen == 'name clan':
                self.handle_name_clan_event(event)
            elif self.sub_screen == 'choose leader':
                self.handle_choose_leader_event(event)
            elif self.sub_screen == 'choose deputy':
                self.handle_choose_deputy_event(event)
            elif self.sub_screen == 'choose med cat':
                self.handle_choose_med_event(event)
            elif self.sub_screen == 'choose members':
                self.handle_choose_members_event(event)
            elif self.sub_screen == 'choose camp':
                self.handle_choose_background_event(event)
            elif self.sub_screen == 'saved screen':
                self.handle_saved_clan_event(event)

    def handle_game_mode_event(self, event):
        """Handle events for the game mode screen"""
        # Game mode selection buttons
        if event.ui_element == self.elements['classic_mode_button']:
            self.game_mode = 'classic'
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['expanded_mode_button']:
            self.game_mode = 'expanded'
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['cruel_mode_button']:
            self.game_mode = 'cruel'
            self.refresh_text_and_buttons()
        # When the next_step button is pressed, go to the clan naming page.
        elif event.ui_element == self.elements['next_step']:
            game.settings['game_mode'] = self.game_mode
            self.open_name_clan()

    def handle_name_clan_event(self, event):
        if event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(choice(names.normal_prefixes))
        elif event.ui_element == self.elements["reset_name"]:
            self.elements["name_entry"].set_text("")
        elif event.ui_element == self.elements['next_step']:
            self.clan_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            self.open_choose_leader()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.open_game_mode()

    def handle_choose_leader_event(self, event):
        if event.ui_element in [self.elements['roll1'], self.elements['roll2'], self.elements['roll3']]:
            event.ui_element.disable()
            create_example_cats()  # create new cats
            self.selected_cat = None  # Your selected cat now no longer exists. Sad. They go away.
            self.refresh_cat_images_and_info()  # Refresh all the images.
        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            self.selected_cat = event.ui_element.return_cat_object()
            self.refresh_cat_images_and_info(self.selected_cat)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.leader = self.selected_cat
            self.selected_cat = None
            self.open_choose_deputy()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.open_name_clan()

    def handle_choose_deputy_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            self.leader = None
            self.selected_cat = None
            self.open_choose_leader()
        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            if event.ui_element.return_cat_object() != self.leader:
                self.selected_cat = event.ui_element.return_cat_object()
                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.deputy = self.selected_cat
            self.selected_cat = None
            self.open_choose_med_cat()

    def handle_choose_med_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            self.deputy = None
            self.selected_cat = None
            self.open_choose_deputy()
        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            if event.ui_element.return_cat_object() not in [self.leader, self.deputy]:
                self.selected_cat = event.ui_element.return_cat_object()
                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.med_cat = self.selected_cat
            self.selected_cat = None
            self.open_choose_members()

    def handle_choose_members_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            if not self.members:
                self.med_cat = None
                self.selected_cat = None
                self.open_choose_med_cat()
            else:
                self.members.pop()  # Delete the last cat added
                self.selected_cat = None
                self.refresh_cat_images_and_info()
                self.refresh_text_and_buttons()
        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            if event.ui_element.return_cat_object() not in [self.leader, self.deputy] + self.members:
                self.selected_cat = event.ui_element.return_cat_object()
                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.members.append(self.selected_cat)
            self.selected_cat = None
            self.refresh_cat_images_and_info(None)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['next_step']:
            self.selected_cat = None
            self.open_choose_background()

    def handle_choose_background_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            self.open_choose_members()
        elif event.ui_element == self.elements['forest_biome']:
            self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['mountain_biome']:
            self.biome_selected = "Mountainous"
            self.selected_camp_tab = 1
            print(self.biome_selected)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['plains_biome']:
            self.biome_selected = "Plains"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['beach_biome']:
            self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["tab1"]:
            self.selected_camp_tab = 1
            self.refresh_selected_camp()
        elif event.ui_element == self.elements["tab2"]:
            self.selected_camp_tab = 2
            self.refresh_selected_camp()
        elif event.ui_element == self.elements["random_background"]:
            # Select a random biome and background
            old_biome = self.biome_selected
            possible_biomes = ['Forest', 'Mountainous', 'Plains', 'Beach']
            # ensuring that the new random camp will not be the same one
            if old_biome is not None:
                possible_biomes.remove(old_biome)
            self.biome_selected = choice(possible_biomes)
            self.selected_camp_tab = randrange(1, 3)
            self.refresh_selected_camp()
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['done_button']:
            self.save_clan()
            self.open_clan_saved_screen()

    def handle_saved_clan_event(self, event):
        if event.ui_element == self.elements["continue"]:
            self.change_screen('clan screen')

    def exit_screen(self):
        self.main_menu.kill()
        self.menu_warning.kill()
        self.clear_all_page()
        return super().exit_screen()

    def on_use(self):

        # Don't allow someone to enter no name for their clan
        if self.sub_screen == 'name clan':
            if sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()) == "":
                self.elements['next_step'].disable()
            else:
                self.elements['next_step'].enable()

    def clear_all_page(self):
        """Clears the entire page, including layout images"""
        for image in self.elements:
            self.elements[image].kill()
        self.elements = {}

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        if self.sub_screen == "game mode":
            # Set the mode explanation text
            if self.game_mode == 'classic':
                display_text = self.classic_mode_text
                display_name = "Classic Mode"
            elif self.game_mode == 'expanded':
                display_text = self.expanded_mode_text
                display_name = "Expanded Mode"
            elif self.game_mode == 'cruel':
                display_text = self.cruel_mode_text
                display_name = "Cruel Season"
            else:
                display_text = ""
                display_name = "ERROR"
            self.elements['mode_details'].set_text(display_text)
            self.elements['mode_name'].set_text(display_name)

            # Update the enabled buttons for the game selection to disable the
            # buttons for the mode currently selected. Mostly for aesthetics, and it
            # make it very clear which mode is selected. 
            if self.game_mode == 'classic':
                self.elements['classic_mode_button'].disable()
                self.elements['expanded_mode_button'].enable()
                self.elements['cruel_mode_button'].enable()
            elif self.game_mode == 'expanded':
                self.elements['classic_mode_button'].enable()
                self.elements['expanded_mode_button'].disable()
                self.elements['cruel_mode_button'].enable()
            elif self.game_mode == 'cruel':
                self.elements['classic_mode_button'].enable()
                self.elements['expanded_mode_button'].enable()
                self.elements['cruel_mode_button'].disable()
            else:
                self.elements['classic_mode_button'].enable()
                self.elements['expanded_mode_button'].enable()
                self.elements['cruel_mode_button'].enable()

            # Don't let the player go forwards with cruel mode, it's not done yet.
            if self.game_mode == 'cruel':
                self.elements['next_step'].disable()
            else:
                self.elements['next_step'].enable()
        # Show the error message if you try to choose a child for leader, deputy, or med cat.
        elif self.sub_screen in ['choose leader', 'choose deputy', 'choose med cat']:
            if self.selected_cat.age in ["kitten", "adolescent"]:
                self.elements['select_cat'].hide()
                self.elements['error_message'].show()
            else:
                self.elements['select_cat'].show()
                self.elements['error_message'].hide()
        # Refresh the choose-members background to match number of cat's chosen.
        elif self.sub_screen == 'choose members':
            if len(self.members) == 0:
                self.elements["background"].set_image(
                    pygame.image.load("resources/images/pick_clan_screen/clan_none_light.png").convert_alpha())
                self.elements['next_step'].disable()
            elif len(self.members) == 1:
                self.elements["background"].set_image(
                    pygame.image.load("resources/images/pick_clan_screen/clan_one_light.png").convert_alpha())
                self.elements['next_step'].disable()
            elif len(self.members) == 2:
                self.elements["background"].set_image(
                    pygame.image.load("resources/images/pick_clan_screen/clan_two_light.png").convert_alpha())
                self.elements['next_step'].disable()
            elif len(self.members) == 3:
                self.elements["background"].set_image(
                    pygame.image.load("resources/images/pick_clan_screen/clan_three_light.png").convert_alpha())
                self.elements['next_step'].disable()
            elif 4 <= len(self.members) <= 6:
                self.elements["background"].set_image(
                    pygame.image.load("resources/images/pick_clan_screen/clan_four_light.png").convert_alpha())
                self.elements['next_step'].enable()
                # In order for the "previous step" to work properly, we must enable this button, just in case it
                # was disabled in the next step.
                self.elements["select_cat"].enable()
            elif len(self.members) == 7:
                self.elements["background"].set_image(
                    pygame.image.load("resources/images/pick_clan_screen/clan_full_light.png").convert_alpha())
                self.elements["select_cat"].disable()
                self.elements['next_step'].enable()

            # Hide the recruit cat button if no cat is selected.
            if self.selected_cat is not None:
                self.elements['select_cat'].show()
            else:
                self.elements['select_cat'].hide()

        elif self.sub_screen == 'choose camp':
            # Enable/disable biome buttons
            if self.biome_selected == 'Forest':
                self.elements['forest_biome'].disable()
                self.elements['mountain_biome'].enable()
                self.elements['plains_biome'].enable()
                self.elements['beach_biome'].enable()
            elif self.biome_selected == "Mountainous":
                self.elements['forest_biome'].enable()
                self.elements['mountain_biome'].disable()
                self.elements['plains_biome'].enable()
                self.elements['beach_biome'].enable()
            elif self.biome_selected == "Plains":
                self.elements['forest_biome'].enable()
                self.elements['mountain_biome'].enable()
                self.elements['plains_biome'].disable()
                self.elements['beach_biome'].enable()
            elif self.biome_selected == "Beach":
                self.elements['forest_biome'].enable()
                self.elements['mountain_biome'].enable()
                self.elements['plains_biome'].enable()
                self.elements['beach_biome'].disable()

            if self.biome_selected is not None and self.selected_camp_tab is not None:
                self.elements['done_button'].enable()

            # Deal with tab and shown camp image:
            self.refresh_selected_camp()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""
        self.elements["tab1"].kill()
        self.elements["tab2"].kill()
        if self.biome_selected == 'Forest':
            self.elements["tab1"] = UIImageButton(pygame.Rect((95, 180), (154, 30)), "", object_id="#classic_tab")
            self.elements["tab2"] = UIImageButton(pygame.Rect((108, 215), (154, 30)), "", object_id="#gully_tab")
        elif self.biome_selected == 'Mountainous':
            self.elements["tab1"] = UIImageButton(pygame.Rect((111, 180), (154, 30)), "", object_id="#cliff_tab")
            self.elements["tab2"] = UIImageButton(pygame.Rect((101, 215), (154, 30)), "", object_id="#cave_tab")
        elif self.biome_selected == 'Plains':
            self.elements["tab1"] = UIImageButton(pygame.Rect((64, 180), (154, 30)), "", object_id="#grasslands_tab")
            self.elements["tab2"] = UIImageButton(pygame.Rect((89, 215), (154, 30)), "", object_id="#tunnel_tab")
        elif self.biome_selected == 'Beach':
            self.elements["tab1"] = UIImageButton(pygame.Rect((76, 180), (154, 30)), "", object_id="#tidepool_tab")
            self.elements["tab2"] = UIImageButton(pygame.Rect((65, 215), (154, 30)), "", object_id="#tidal_cave_tab")

        if self.selected_camp_tab == 1:
            self.elements["tab1"].disable()
            self.elements["tab2"].enable()
        elif self.selected_camp_tab == 2:
            self.elements["tab1"].enable()
            self.elements["tab2"].disable()
        else:
            self.elements["tab1"].enable()
            self.elements["tab2"].enable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        self.elements["camp_art"] = pygame_gui.elements.UIImage(pygame.Rect((175, 170), (450, 400)), pygame.image.load(
            self.get_camp_art_path(self.selected_camp_tab)).convert_alpha())
        self.elements['art_frame'].kill()
        self.elements['art_frame'] = pygame_gui.elements.UIImage(pygame.Rect(((167, 162), (466, 416))),
                                                                 pygame.image.load(
                                                                     "resources/images/bg_preview_border.png").convert_alpha())

    def refresh_selected_cat_info(self, selected=None):
        # SELECTED CAT INFO
        if selected is not None:

            if self.sub_screen == 'choose leader':
                self.elements['cat_name'].set_text(str(selected.name) +
                                                   ' --> ' +
                                                   selected.name.prefix +
                                                   'star')
            else:
                self.elements['cat_name'].set_text(str(selected.name))
            self.elements['cat_name'].show()
            self.elements['cat_info'].set_text(selected.gender + "\n" +
                                               str(selected.age + "\n" +
                                                   str(selected.trait)))
            self.elements['cat_info'].show()
        else:
            self.elements['next_step'].disable()
            self.elements['cat_info'].hide()
            self.elements['cat_name'].hide()

    def refresh_cat_images_and_info(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats. """

        column_poss = [50, 100]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    pygame.Rect((270, 200), (150, 150)), game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u])
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((650, 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((column_poss[0], 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
        for u in range(6, 12):
            self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    pygame.Rect((270, 200), (150, 150)), game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u])
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((700, 130 + 50 * (u - 6)), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    pygame.Rect((column_poss[1], 130 + 50 * (u - 6)), (50, 50)), game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u])

    def open_game_mode(self):
        # Clear previous screen
        self.clear_all_page()
        self.sub_screen = 'game mode'

        text_box = image_cache.load_image(
            'resources/images/game_mode_text_box.png').convert_alpha()

        self.elements['game_mode_background'] = pygame_gui.elements.UIImage(pygame.Rect((325, 130), (399, 461)),
                                                                            text_box)
        self.elements['permi_warning'] = pygame_gui.elements.UITextBox(
            "Your clan's game mode in permanent and cannot be changed after clan creation.",
            pygame.Rect((100, 581), (600, 40)),
            object_id=get_text_box_theme()
        )

        # Create all the elements.
        self.elements['classic_mode_button'] = UIImageButton(pygame.Rect((109, 240), (132, 30)), "",
                                                             object_id="#classic_mode_button")
        self.elements['expanded_mode_button'] = UIImageButton(pygame.Rect((94, 320), (162, 34)), "",
                                                              object_id="#expanded_mode_button")
        self.elements['cruel_mode_button'] = UIImageButton(pygame.Rect((100, 400), (150, 30)), "",
                                                           object_id="#cruel_mode_button")
        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 620), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements['previous_step'].disable()
        self.elements['next_step'] = UIImageButton(pygame.Rect((400, 620), (147, 30)), "",
                                                   object_id="#next_step_button")
        self.elements['mode_details'] = UITextBoxTweaked("", pygame.Rect((325, 160), (405, 461)),
                                                         object_id="#game_mode_details")
        self.elements['mode_name'] = UITextBoxTweaked("", pygame.Rect((425, 130), (200, 50)),
                                                      object_id="#clan_header_text_box")

        self.refresh_text_and_buttons()

    def open_name_clan(self):
        """Opens the name clan screen"""
        self.clear_all_page()
        self.sub_screen = 'name clan'

        # Create all the elements.
        self.elements["background"] = pygame_gui.elements.UIImage(pygame.Rect((0, 0), (800, 700)),
                                                                  MakeClanScreen.name_clan_img)
        self.elements["random"] = UIImageButton(pygame.Rect((222, 593), (34, 34)), "", object_id="#random_dice_button")
        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 635), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements['next_step'] = UIImageButton(pygame.Rect((400, 635), (147, 30)), "",
                                                   object_id="#next_step_button")
        self.elements['next_step'].disable()
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(pygame.Rect((265, 600), (140, 25)))
        self.elements["clan"] = pygame_gui.elements.UITextBox("<font color='#FFFFFF'>-Clan</font>",
                                                              pygame.Rect((375, 600), (100, 25)))
        self.elements["reset_name"] = UIImageButton(pygame.Rect((455, 595), (134, 30)), "",
                                                    object_id="#reset_name_button")

    def open_choose_leader(self):
        """Set up the screen for the choose leader phase. """
        self.clear_all_page()
        self.sub_screen = 'choose leader'

        self.elements['background'] = pygame_gui.elements.UIImage(pygame.Rect((0, 414), (800, 286)),
                                                                  MakeClanScreen.leader_img)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(pygame.Rect((292, 100), (216, 50)),
                                                                     MakeClanScreen.clan_frame_img)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   pygame.Rect((292, 105), (216, 50)),
                                                                   object_id="#clan_header_text_box")

        # Roll_buttons
        x_pos = 155
        y_pos = 235
        self.elements['roll1'] = UIImageButton(pygame.Rect((x_pos, y_pos), (34, 34)), "",
                                               object_id="#random_dice_button")
        y_pos += 40
        self.elements['roll2'] = UIImageButton(pygame.Rect((x_pos, y_pos), (34, 34)), "",
                                               object_id="#random_dice_button")
        y_pos += 40
        self.elements['roll3'] = UIImageButton(pygame.Rect((x_pos, y_pos), (34, 34)), "",
                                               object_id="#random_dice_button")

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", pygame.Rect((440, 260), (100, 100)), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", pygame.Rect((150, 175), (500, 55)), visible=False,
                                                                  object_id=get_text_box_theme())

        self.elements['select_cat'] = UIImageButton(pygame.Rect((234, 348), (332, 52)), "",
                                                    object_id="#nine_lives_button", visible=False)
        # Error message, to appear if you can't choose that cat.
        self.elements['error_message'] = pygame_gui.elements.UITextBox(
            "<font color='#FF0000'> Too young to become leader </font>", pygame.Rect((150, 348), (500, 55)),
            visible=False)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 400), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements['next_step'] = UIImageButton(pygame.Rect((400, 400), (147, 30)), "",
                                                   object_id="#next_step_button")
        self.elements['next_step'].disable()

        # draw cats to choose from
        column_poss = [50, 100]

        for u in range(6):
            self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((column_poss[0], 130 + 50 * u), (50, 50)),
                                                           game.choose_cats[u].large_sprite,
                                                           cat_object=game.choose_cats[u])
        for u in range(6, 12):
            self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((column_poss[1], 130 + 50 * (u - 6)), (50, 50)),
                                                           game.choose_cats[u].large_sprite,
                                                           cat_object=game.choose_cats[u])

    def open_choose_deputy(self):
        """Open sub-page to select deputy."""
        self.clear_all_page()
        self.sub_screen = 'choose deputy'

        self.elements['background'] = pygame_gui.elements.UIImage(pygame.Rect((0, 414), (800, 286)),
                                                                  MakeClanScreen.deputy_img)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(pygame.Rect((292, 100), (216, 50)),
                                                                     MakeClanScreen.clan_frame_img)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   pygame.Rect((292, 105), (216, 50)),
                                                                   object_id="#clan_header_text_box")

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", pygame.Rect((440, 260), (100, 100)), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", pygame.Rect((150, 175), (500, 55)), visible=False,
                                                                  object_id=get_text_box_theme())

        self.elements['select_cat'] = UIImageButton(pygame.Rect((209, 348), (384, 52)), "",
                                                    object_id="#support_leader_button", visible=False)
        # Error message, to appear if you can't choose that cat.
        self.elements['error_message'] = pygame_gui.elements.UITextBox(
            "<font color='#FF0000'> Too young to become deputy </font>", pygame.Rect((150, 348), (500, 55)),
            visible=False)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 400), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements['next_step'] = UIImageButton(pygame.Rect((400, 400), (147, 30)), "",
                                                   object_id="#next_step_button")
        self.elements['next_step'].disable()

        # draw cats to choose from
        column_poss = [50, 100]

        for u in range(6):
            if game.choose_cats[u] == self.leader:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((650, 130 + 50 * u,), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((column_poss[0], 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
        for u in range(6, 12):
            if game.choose_cats[u] == self.leader:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((700, 130 + 50 * (u - 6)), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    pygame.Rect((column_poss[1], 130 + 50 * (u - 6)), (50, 50)),
                    game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u])

    def open_choose_med_cat(self):
        self.clear_all_page()
        self.sub_screen = 'choose med cat'

        self.elements['background'] = pygame_gui.elements.UIImage(pygame.Rect((0, 414), (800, 286)),
                                                                  MakeClanScreen.medic_img)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(pygame.Rect((292, 100), (216, 50)),
                                                                     MakeClanScreen.clan_frame_img)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   pygame.Rect((292, 105), (216, 50)),
                                                                   object_id="#clan_header_text_box")

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", pygame.Rect((440, 260), (100, 100)), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", pygame.Rect((150, 175), (500, 55)), visible=False,
                                                                  object_id=get_text_box_theme())

        self.elements['select_cat'] = UIImageButton(pygame.Rect((252, 342), (306, 58)), "",
                                                    object_id="#aid_clan_button", visible=False)
        # Error message, to appear if you can't choose that cat.
        self.elements['error_message'] = pygame_gui.elements.UITextBox(
            "<font color='#FF0000'> Too young to become a medicine cat </font>", pygame.Rect((150, 348), (500, 55)),
            visible=False)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 400), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements['next_step'] = UIImageButton(pygame.Rect((400, 400), (147, 30)), "",
                                                   object_id="#next_step_button")
        self.elements['next_step'].disable()

        # draw cats to choose from
        column_poss = [50, 100]

        for u in range(6):
            if game.choose_cats[u] in [self.leader, self.deputy]:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((650, 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((column_poss[0], 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
        for u in range(6, 12):
            if game.choose_cats[u] in [self.leader, self.deputy]:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((700, 130 + 50 * (u - 6)), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    pygame.Rect((column_poss[1], 130 + 50 * (u - 6)), (50, 50)),
                    game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u])

    def open_choose_members(self):
        self.clear_all_page()
        self.sub_screen = 'choose members'

        self.elements['background'] = pygame_gui.elements.UIImage(pygame.Rect((0, 414), (800, 286)),
                                                                  pygame.image.load(
                                                                      "resources/images/pick_clan_screen/clan_none_light.png").convert_alpha())
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(pygame.Rect((292, 100), (216, 50)),
                                                                     MakeClanScreen.clan_frame_img)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   pygame.Rect((292, 105), (216, 50)),
                                                                   object_id="#clan_header_text_box")

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", pygame.Rect((440, 260), (100, 100)), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", pygame.Rect((150, 175), (500, 55)), visible=False,
                                                                  object_id=get_text_box_theme())

        self.elements['select_cat'] = UIImageButton(pygame.Rect((353, 360), (95, 30)), "", object_id="#recruit_button",
                                                    visible=False)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 400), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements['next_step'] = UIImageButton(pygame.Rect((400, 400), (147, 30)), "",
                                                   object_id="#next_step_button")
        self.elements['next_step'].disable()

        # draw cats to choose from
        column_poss = [50, 100]

        for u in range(6):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat]:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((650, 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((column_poss[0], 130 + 50 * u), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
        for u in range(6, 12):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat]:
                self.elements["cat" + str(u)] = UISpriteButton(pygame.Rect((700, 130 + 50 * (u - 6)), (50, 50)),
                                                               game.choose_cats[u].large_sprite,
                                                               cat_object=game.choose_cats[u])
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    pygame.Rect((column_poss[1], 130 + 50 * (u - 6)), (50, 50)),
                    game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u])

        # This is doing the same thing again, but it's needed to make the "last step button work"
        self.refresh_cat_images_and_info()
        self.refresh_text_and_buttons()

    def open_choose_background(self):
        # clear screen
        self.clear_all_page()
        self.sub_screen = 'choose camp'

        self.elements['previous_step'] = UIImageButton(pygame.Rect((253, 645), (147, 30)), "",
                                                       object_id="#previous_step_button")
        self.elements["done_button"] = UIImageButton(pygame.Rect((400, 645), (147, 30)), "",
                                                     object_id="#done_arrow_button")
        self.elements['done_button'].disable()

        # Biome buttons
        self.elements['forest_biome'] = UIImageButton(pygame.Rect((196, 100), (100, 46)), "",
                                                      object_id="#forest_biome_button")
        self.elements['mountain_biome'] = UIImageButton(pygame.Rect((304, 100), (106, 46)), "",
                                                        object_id="#mountain_biome_button")
        self.elements['plains_biome'] = UIImageButton(pygame.Rect((424, 100), (88, 46)), "",
                                                      object_id="#plains_biome_button")
        self.elements['beach_biome'] = UIImageButton(pygame.Rect((520, 100), (82, 46)), "",
                                                     object_id="#beach_biome_button")

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        self.elements["tab1"] = UIImageButton(pygame.Rect((95, 180), (154, 30)), "",
                                              object_id="#classic_tab", visible=False)
        self.elements["tab2"] = UIImageButton(pygame.Rect((108, 215), (154, 30)), "",
                                              object_id="#gully_tab", visible=False)

        # Random background
        self.elements["random_background"] = UIImageButton(pygame.Rect((255, 595), (290, 30)), "",
                                                           object_id="#random_background_button")

        # art frame
        self.elements['art_frame'] = pygame_gui.elements.UIImage(pygame.Rect(((167, 162), (466, 416))),
                                                                 pygame.image.load(
                                                                     "resources/images/bg_preview_border.png").convert_alpha())

        # camp art self.elements["camp_art"] = pygame_gui.elements.UIImage(pygame.Rect((175,170),(450, 400)),
        # pygame.image.load(self.get_camp_art_path(1)).convert_alpha(), visible=False)

    def open_clan_saved_screen(self):
        self.clear_all_page()
        self.sub_screen = 'saved screen'
        self.elements["leader_image"] = pygame_gui.elements.UIImage(pygame.Rect((screen_x / 2 - 50, 120), (100, 100)),
                                                                    game.clan.leader.large_sprite)
        self.elements["continue"] = UIImageButton(pygame.Rect((349, 250), (102, 30)), "",
                                                  object_id="#continue_button_small")
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox('Your clan has been created and saved!',
                                                                      pygame.Rect((100, 70), (600, 30)),
                                                                      object_id=get_text_box_theme())

    def save_clan(self):
        convert_camp = {1: 'camp1', 2: 'camp2'}
        game.clan = Clan(self.clan_name,
                         self.leader,
                         self.deputy,
                         self.med_cat,
                         self.biome_selected, game.switches['world_seed'],
                         game.switches['camp_site'], convert_camp[self.selected_camp_tab],
                         self.game_mode, self.members)
        game.clan.create_clan()
        if map_available:
            territory_claim = str(game.clan.name) + 'Clan Territory'
            otherclan_campsite = {}
            for clan in game.clan.all_clans:
                x = randrange(40)
                y = randrange(44)
                clan_camp = self.choose_other_clan_territory(x, y)
                territory_biome = str(game.map_info[clan_camp][2])
                territory_twolegs = str(game.map_info[clan_camp][4])
                territory_thunderpath = str(game.map_info[clan_camp][5])
                territory_prey = str(game.map_info[clan_camp][6])
                territory_plants = str(game.map_info[clan_camp][7])
                game.map_info[clan_camp] = [
                    clan_camp[0], clan_camp[1], territory_biome,
                    str(clan) + " Camp", territory_twolegs,
                    territory_thunderpath, territory_prey, territory_plants
                ]
                otherclan_campsite[str(clan)] = clan_camp
            for y in range(44):
                for x in range(40):
                    if (x, y) == (game.switches['camp_site'][0] - 1,
                                  game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] - 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0] + 1,
                                    game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] + 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    for clan in game.clan.all_clans:
                        if (x, y) == (otherclan_campsite[str(clan)][0] - 1,
                                      otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] - 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0] + 1,
                                        otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] + 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
            # save_map(game.map_info, game.switches['clan_name'])

    #This is not currently in use.
    '''def sixth_phase(self):
        Not currently in use
        if map_available:
            for y in range(44):
                for x in range(40):
                    noise_value = self.world.check_noise_tile(x, y)
                    if noise_value > 0.1:
                        # buttons.draw_maptile_button((x*TILESIZE,y*TILESIZE),image=(pygame.transform.scale(terrain.images[1],(TILESIZE,TILESIZE))))
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain1'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Desert", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'low', 'low', 'medium', 'medium',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium', 'high']),
                            'Prey Levels: ' +
                            choice(['none', 'low', 'medium']),
                            'Plant Cover: ' +
                            choice(['none', 'low', 'medium'])
                        ]
                    elif noise_value < -0.015:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain3'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Forest", "Unclaimed",
                            'Twoleg Activity: ' + choice(
                                ['none', 'low', 'low', 'medium', 'high']),
                            'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium']),
                            'Prey Levels: ' +
                            choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['low', 'medium', 'high'])
                        ]
                    else:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain0'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Plains", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'low', 'medium', 'medium', 'high',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium', 'high']),
                            'Prey Levels: ' +
                            choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['low', 'medium', 'high'])
                        ]
            for y in range(44):
                for x in range(40):
                    height = self.world.check_heighttile(x, y)
                    if height < 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif x == 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif x == 39:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif y == 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif y == 43:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif height < 0.03:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain6'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Beach", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'low', 'medium', 'medium', 'high',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium']),
                            'Prey Levels: ' +
                            choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['none', 'low', 'medium'])
                        ]
                    elif height > 0.35:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain5'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Mountainous", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'none', 'low', 'low', 'medium', 'high'
                            ]), 'Thunderpath Traffic: ' + choice([
                                'none', 'none', 'low', 'low', 'medium',
                                'medium', 'high'
                            ]), 'Prey Levels: ' +
                            choice(['none', 'low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['none', 'low', 'medium', 'high'])
                        ]
                    if (x, y) == game.switches['map_selection']:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo0'],
                                                (16, 16)),
                                            camp_site=(x, y))
            verdana_big.text('Map', (-16, 50))
            verdana.text(
                str(game.map_info[game.switches['map_selection']][0]) + ", " +
                str(game.map_info[game.switches['map_selection']][1]),
                (-16, 100))
            verdana.text(str(game.map_info[game.switches['map_selection']][2]),
                         (-16, 150))
            verdana.text(str(game.map_info[game.switches['map_selection']][3]),
                         (-16, 200))
            verdana.text(str(game.switches['camp_site']), (-16, 250))

            if game.map_info[game.switches['map_selection']][3] == 'Unclaimed':

                # ensures a camp bg is chosen
                random_camp_options = ['camp1', 'camp2']
                random_camp = choice(random_camp_options)

                buttons.draw_button(
                    (-16, 300),
                    text='Done',
                    choosing_camp=False,
                    biome=game.map_info[game.switches['map_selection']][2],
                    world_seed=self.worldseed,
                    camp_bg=random_camp,
                    cur_screen='clan created screen')

            else:
                buttons.draw_button((-16, 300),
                                    text='Done',
                                    available=False)
        else:
            self.choose_camp()'''

    def get_camp_art_path(self, campnum):
        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = "newleaf"
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        biome = self.biome_selected.lower()

        if campnum:
            return f'{camp_bg_base_dir}/{biome}/{start_leave}_camp{str(campnum)}_{light_dark}.png'
        else:
            return None

#I will leave this here, but commented out. It has some ma code on it.
'''class ClanCreatedScreen(Screens):

    def on_use(self):
        # LAYOUT
        verdana.text('Your clan has been created and saved!', ('center', 50))
        draw_big(game.clan.leader, (screen_x / 2 - 50, 100))

        # buttons
        buttons.draw_image_button((349, 250),
                                  button_name='continue_small',
                                  text='Continue',
                                  cur_screen='clan screen',
                                  size=(102, 30),
                                  hotkey=[1])

    def screen_switches(self):
        game.clan = Clan(game.switches['clan_name'],
                         game.choose_cats[game.switches['leader']],
                         game.choose_cats[game.switches['deputy']],
                         game.choose_cats[game.switches['medicine_cat']],
                         game.switches['biome'], game.switches['world_seed'],
                         game.switches['camp_site'], game.switches['camp_bg'],
                         game.switches['game_mode'])
        game.clan.create_clan()


# commented out until we decide what to do with it
"""        if map_available:
            territory_claim = str(game.clan.name) + 'Clan Territory'
            otherclan_campsite = {}
            for clan in game.clan.all_clans:
                x = randrange(40)
                y = randrange(44)
                clan_camp = self.choose_other_clan_territory(x, y)
                territory_biome = str(game.map_info[clan_camp][2])
                territory_twolegs = str(game.map_info[clan_camp][4])
                territory_thunderpath = str(game.map_info[clan_camp][5])
                territory_prey = str(game.map_info[clan_camp][6])
                territory_plants = str(game.map_info[clan_camp][7])
                game.map_info[clan_camp] = [
                    clan_camp[0], clan_camp[1], territory_biome,
                    str(clan) + " Camp", territory_twolegs,
                    territory_thunderpath, territory_prey, territory_plants
                ]
                otherclan_campsite[str(clan)] = clan_camp
            for y in range(44):
                for x in range(40):
                    if (x, y) == (game.switches['camp_site'][0] - 1,
                                  game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] - 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0] + 1,
                                    game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] + 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    for clan in game.clan.all_clans:
                        if (x, y) == (otherclan_campsite[str(clan)][0] - 1,
                                      otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] - 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0] + 1,
                                        otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] + 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
            # save_map(game.map_info, game.switches['clan_name'])

    def choose_other_clan_territory(self, x, y):
        self.x = x
        self.y = y
        if game.map_info[(self.x, self.y)][3] != "Unclaimed":
            self.x = randrange(40)
            self.y = randrange(44)
            if game.map_info[(self.x, self.y)][3] == "Unclaimed":
                return self.x, self.y
            else:
                self.x = randrange(40)
                self.y = randrange(44)
                return self.x, self.y
        else:
            return self.x, self.y
    '''

