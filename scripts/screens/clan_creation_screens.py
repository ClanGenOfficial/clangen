import pygame
from random import choice, randrange
import pygame_gui

from .base_screens import Screens

from scripts.utility import get_text_box_theme, scale
from scripts.clan import Clan
from scripts.cat.cats import create_example_cats, Cat
from scripts.cat.names import names
from re import sub
from scripts.game_structure import image_cache
# from scripts.world import World, save_map
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton
from scripts.game_structure.game_essentials import game, MANAGER


class MakeClanScreen(Screens):
    # UI images
    clan_frame_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_name_frame.png').convert_alpha(), (432, 100))
    name_clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha(), (1600, 1400))
    leader_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/leader_light.png').convert_alpha(), (1600, 1400))
    deputy_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/deputy_light.png').convert_alpha(), (1600, 1400))
    medic_img = pygame.transform.scale( pygame.image.load(
        'resources/images/pick_clan_screen/med_light.png').convert_alpha(), (1600, 1400))
    clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_light.png').convert_alpha(), (1600, 1400))
    bg_preview_border = pygame.transform.scale(
        pygame.image.load("resources/images/bg_preview_border.png").convert_alpha(), (466, 416))

    classic_mode_text = "This mode is Clan Generator at it's most basic. " \
                        "The player will not be expected to manage the minutia of Clan life. <br><br>" \
                        "Perfect for a relaxing game session or for focusing on storytelling. <br><br>" \
                        "With this mode you are the eye in the sky, watching the Clan as their story unfolds. "

    expanded_mode_text = "A more hands-on experience. " \
                         "This mode has everything in Classic Mode as well as more management-focused features.<br><br>" \
                         "New features include:<br>" \
                         "- Illnesses, Injuries, and Permanent Conditions<br>" \
                         "- Herb gathering and treatment<br>" \
                         "- Ability to choose patrol type<br><br>" \
                         "With this mode you'll be making the important clan-life decisions."

    cruel_mode_text = "This mode has all the features of Expanded mode, but is significantly more difficult. If " \
                      "you'd like a challenge with a bit of brutality, then this mode is for you.<br><br>" \
                      "You heard the warnings... a Cruel Season is coming. Will you survive?" \
                      "<br> <br>" \
                      "-COMING SOON-"

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
    tabs = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.rolls_left = 3
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
            scale(pygame.Rect((50, 50), (1200, -1))),
            object_id=get_text_box_theme("#cat_profile_info_box"), manager=MANAGER
        )
        self.main_menu = UIImageButton(scale(pygame.Rect((50, 100), (306, 60))), "", object_id="#main_menu_button"
                                       , manager=MANAGER)
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
            new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [clan.casefold() for clan in game.switches['clan_list']]:
                self.elements["error"].set_text("A clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.open_game_mode()

    def handle_choose_leader_event(self, event):
        if event.ui_element in [self.elements['roll1'], self.elements['roll2'], self.elements['roll3']]:
            event.ui_element.disable()
            self.elements['select_cat'].hide()
            create_example_cats()  # create new cats
            self.selected_cat = None  # Your selected cat now no longer exists. Sad. They go away.
            self.refresh_cat_images_and_info()  # Refresh all the images.
            self.rolls_left -= 1
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
            if event.ui_element.return_cat_object():
                print(self.med_cat)
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
            if event.ui_element.return_cat_object():
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
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['plains_biome']:
            self.biome_selected = "Plains"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['beach_biome']:
            self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["tab1"]:
            self.selected_camp_tab = 1
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab2"]:
            self.selected_camp_tab = 2
            self.refresh_selected_camp()
        elif self.biome_selected == 'Forest' and event.ui_element == self.tabs["tab3"]:
            self.selected_camp_tab = 3
            self.refresh_selected_camp()
        elif event.ui_element == self.elements["random_background"]:
            # Select a random biome and background
            old_biome = self.biome_selected
            possible_biomes = ['Forest', 'Mountainous', 'Plains', 'Beach']
            # ensuring that the new random camp will not be the same one
            if old_biome is not None:
                possible_biomes.remove(old_biome)
            self.biome_selected = choice(possible_biomes)
            if self.biome_selected == "Forest":
                self.selected_camp_tab = randrange(1, 4)
            else:
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
        self.rolls_left = 3
        return super().exit_screen()

    def on_use(self):

        # Don't allow someone to enter no name for their clan
        if self.sub_screen == 'name clan':
            if self.elements["name_entry"].get_text() == "":
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Clan names cannot start with a space.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().casefold() in [clan.casefold() for clan in game.switches['clan_list']]:
                self.elements["error"].set_text("A clan with that name already exists.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
                return
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()

    def clear_all_page(self):
        """Clears the entire page, including layout images"""
        for image in self.elements:
            self.elements[image].kill()
        for tab in self.tabs:
            self.tabs[tab].kill()
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
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_none_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif len(self.members) == 1:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_one_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif len(self.members) == 2:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_two_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif len(self.members) == 3:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_three_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif 4 <= len(self.members) <= 6:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_four_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].enable()
                # In order for the "previous step" to work properly, we must enable this button, just in case it
                # was disabled in the next step.
                self.elements["select_cat"].enable()
            elif len(self.members) == 7:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_full_light.png").convert_alpha(),
                        (1600, 1400)))
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
        for tab in self.tabs:
            self.tabs[tab].kill()
        if self.biome_selected == 'Forest':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((190, 360), (308, 60))), "", object_id="#classic_tab"
                                                  , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((216, 430), (308, 60))), "", object_id="#gully_tab"
                                                  , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((190, 500), (308, 60))), "", object_id="#grotto_tab"
                                                  , manager=MANAGER)
        elif self.biome_selected == 'Mountainous':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((222, 360), (308, 60))), "", object_id="#cliff_tab"
                                                  , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((180, 430), (308, 60))), "", object_id="#cave_tab"
                                                  , manager=MANAGER)

        elif self.biome_selected == 'Plains':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((128, 360), (308, 60))), "", object_id="#grasslands_tab"
                                                  , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((178, 430), (308, 60))), "", object_id="#tunnel_tab"
                                                  , manager=MANAGER)
        elif self.biome_selected == 'Beach':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((152, 360), (308, 60))), "", object_id="#tidepool_tab"
                                                  , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((130, 430), (308, 60))), "", object_id="#tidal_cave_tab"
                                                  , manager=MANAGER)

        if self.selected_camp_tab == 1:
            self.tabs["tab1"].disable()
            self.tabs["tab2"].enable()
            if self.biome_selected == 'Forest':
                self.tabs["tab3"].enable()
        elif self.selected_camp_tab == 2:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].disable()
            if self.biome_selected == 'Forest':
                self.tabs["tab3"].enable()
        elif self.selected_camp_tab == 3:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            if self.biome_selected == 'Forest':
                self.tabs["tab3"].disable()
        else:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            if self.biome_selected == 'Forest':
                self.tabs["tab3"].enable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        self.elements["camp_art"] = pygame_gui.elements.UIImage(scale(pygame.Rect((350, 340), (900, 800))),
                                                                pygame.transform.scale(
                                                                    pygame.image.load(
                                                                    self.get_camp_art_path(self.selected_camp_tab)).convert_alpha(),
                                                                    (900, 800)), manager=MANAGER)
        self.elements['art_frame'].kill()
        self.elements['art_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect(((334, 324), (932, 832)))),
                                                                 pygame.transform.scale(
                                                                 pygame.image.load(
                                                                     "resources/images/bg_preview_border.png").convert_alpha(),
                                                                     (932, 832)), manager=MANAGER)

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

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 400), (300, 300))), pygame.transform.scale(game.choose_cats[u].large_sprite, (300, 300)),
                    cat_object=game.choose_cats[u])
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = UISpriteButton(scale(pygame.Rect((1300, 250 + 100 * u), (100, 100))),
                                                               game.choose_cats[u].big_sprite,
                                                               cat_object=game.choose_cats[u], manager=MANAGER)
                self.elements["cat" + str(u)].disable()
            else:
                self.elements["cat" + str(u)] = UISpriteButton(scale(pygame.Rect((column_poss[0], 260 + 100 * u), (100, 100))),
                                                               game.choose_cats[u].big_sprite,
                                                               cat_object=game.choose_cats[u], manager=MANAGER)
        for u in range(6, 12):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 400), (300, 300))), pygame.transform.scale(game.choose_cats[u].big_sprite, (300, 300)),
                    cat_object=game.choose_cats[u], manager=MANAGER)
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = UISpriteButton(scale(pygame.Rect((1400, 250 + 100 * (u - 6)), (100, 100))),
                                                               game.choose_cats[u].big_sprite,
                                                               cat_object=game.choose_cats[u], manager=MANAGER)
                self.elements["cat" + str(u)].disable()
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((column_poss[1], 260 + 100 * (u - 6)), (100, 100))), game.choose_cats[u].large_sprite,
                    cat_object=game.choose_cats[u], manager=MANAGER)

    def open_game_mode(self):
        # Clear previous screen
        self.clear_all_page()
        self.sub_screen = 'game mode'

        text_box = image_cache.load_image(
            'resources/images/game_mode_text_box.png').convert_alpha()

        self.elements['game_mode_background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((650, 260), (798, 922))),
                                                                            pygame.transform.scale(text_box, (798, 922))
                                                                            , manager=MANAGER)
        self.elements['permi_warning'] = pygame_gui.elements.UITextBox(
            "Your clan's game mode is permanent and cannot be changed after Clan creation.",
            scale(pygame.Rect((200, 1162), (1200, 80))),
            object_id=get_text_box_theme(), manager=MANAGER
        )

        # Create all the elements.
        self.elements['classic_mode_button'] = UIImageButton(scale(pygame.Rect((218, 480), (264, 60))), "",
                                                             object_id="#classic_mode_button", manager=MANAGER)
        self.elements['expanded_mode_button'] = UIImageButton(scale(pygame.Rect((188, 640), (324, 68))), "",
                                                              object_id="#expanded_mode_button", manager=MANAGER)
        self.elements['cruel_mode_button'] = UIImageButton(scale(pygame.Rect((200, 800), (300, 60))), "",
                                                           object_id="#cruel_mode_button", manager=MANAGER)
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1240), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['previous_step'].disable()
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1240), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['mode_details'] = UITextBoxTweaked("", scale(pygame.Rect((650, 320), (810, 922))),
                                                         object_id="#game_mode_details", manager=MANAGER)
        self.elements['mode_name'] = UITextBoxTweaked("", scale(pygame.Rect((850, 270), (400, 100))),
                                                      object_id="#clan_header_text_box", manager=MANAGER)

        self.refresh_text_and_buttons()

    def open_name_clan(self):
        """Opens the name clan screen"""
        self.clear_all_page()
        self.sub_screen = 'name clan'

        # Create all the elements.
        self.elements["background"] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (1600, 1400))),
                                                                  pygame.transform.scale(MakeClanScreen.name_clan_img,
                                                                                         (1600, 1400))
                                                                  , manager=MANAGER)
        self.elements["random"] = UIImageButton(scale(pygame.Rect((448, 1190), (68, 68))), "", object_id="#random_dice_button"
                                                , manager=MANAGER)

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1310), (596, -1))), manager=MANAGER,
                                                               object_id="#default_dark", visible=False)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1270), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1270), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((530, 1195), (280, 58)))
                                                                          , manager=MANAGER)
        self.elements["name_entry"].set_allowed_characters(list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "))
        self.elements["name_entry"].set_text_length_limit(11)
        self.elements["clan"] = pygame_gui.elements.UITextBox("<font color='#FFFFFF'>-Clan</font>",
                                                              scale(pygame.Rect((750, 1200), (200, 50))), manager=MANAGER)
        self.elements["reset_name"] = UIImageButton(scale(pygame.Rect((910, 1190), (268, 60))), "",
                                                    object_id="#reset_name_button", manager=MANAGER)

    def open_choose_leader(self):
        """Set up the screen for the choose leader phase. """
        self.clear_all_page()
        self.sub_screen = 'choose leader'

        self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 828), (1600, 572))),
                                                                  MakeClanScreen.leader_img, manager=MANAGER)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(scale(pygame.Rect((584, 200), (432, 100))),
                                                                     MakeClanScreen.clan_frame_img, manager=MANAGER)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   scale(pygame.Rect((585, 220), (432, 100))),
                                                                   object_id="#clan_header_text_box", manager=MANAGER)

        # Roll_buttons
        x_pos = 310
        y_pos = 470
        self.elements['roll1'] = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (68, 68))), "",
                                               object_id="#random_dice_button", manager=MANAGER)
        y_pos += 80
        self.elements['roll2'] = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (68, 68))), "",
                                               object_id="#random_dice_button", manager=MANAGER)
        y_pos += 80
        self.elements['roll3'] = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (68, 68))), "",
                                               object_id="#random_dice_button", manager=MANAGER)

        if self.rolls_left <= 2:
            self.elements['roll1'].disable()
        if self.rolls_left <= 1:
            self.elements['roll2'].disable()
        if self.rolls_left == 0:
            self.elements['roll3'].disable()

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", scale(pygame.Rect((880, 520), (200, 200))), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95, manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((300, 350), (1000, 110))), visible=False,
                                                                  object_id=get_text_box_theme(), manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((468, 696), (664, 104))), "",
                                                    object_id="#nine_lives_button", visible=False, manager=MANAGER)
        # Error message, to appear if you can't choose that cat.
        self.elements['error_message'] = pygame_gui.elements.UITextBox(
            "<font color='#FF0000'> Too young to become leader </font>", scale(pygame.Rect((300, 706), (1000, 110))),
            visible=False, manager=MANAGER)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 800), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 800), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_choose_deputy(self):
        """Open sub-page to select deputy."""
        self.clear_all_page()
        self.sub_screen = 'choose deputy'

        self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 828), (1600, 572))),
                                                                  MakeClanScreen.deputy_img, manager=MANAGER)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(scale(pygame.Rect((584, 200), (432, 100))),
                                                                     MakeClanScreen.clan_frame_img, manager=MANAGER)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   scale(pygame.Rect((585, 220), (432, 100))),
                                                                   object_id="#clan_header_text_box", manager=MANAGER)

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", scale(pygame.Rect((880, 520), (200, 200))), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95, manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((300, 350), (1000, 110))), visible=False,
                                                                  object_id=get_text_box_theme(), manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((418, 696), (768, 104))), "",
                                                    object_id="#support_leader_button", visible=False, manager=MANAGER)
        # Error message, to appear if you can't choose that cat.
        self.elements['error_message'] = pygame_gui.elements.UITextBox(
            "<font color='#FF0000'> Too young to become deputy </font>", scale(pygame.Rect((300, 706), (1000, 110))),
            visible=False, manager=MANAGER)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 800), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 800), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_choose_med_cat(self):
        self.clear_all_page()
        self.sub_screen = 'choose med cat'

        self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 828), (1600, 572))),
                                                                  MakeClanScreen.medic_img, manager=MANAGER)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(scale(pygame.Rect((584, 200), (432, 100))),
                                                                     MakeClanScreen.clan_frame_img, manager=MANAGER)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   scale(pygame.Rect((585, 220), (432, 100))),
                                                                   object_id="#clan_header_text_box", manager=MANAGER)

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", scale(pygame.Rect((880, 520), (200, 200))), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95, manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((300, 350), (1000, 110))),
                                                                  visible=False,
                                                                  object_id=get_text_box_theme(), manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((520, 684), (612, 116))), "",
                                                    object_id="#aid_clan_button", visible=False, manager=MANAGER)
        # Error message, to appear if you can't choose that cat.
        self.elements['error_message'] = pygame_gui.elements.UITextBox(
            "<font color='#FF0000'> Too young to become a medicine cat </font>", scale(pygame.Rect((300, 706), (1000, 110))),
            visible=False, manager=MANAGER)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 800), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 800), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_choose_members(self):
        self.clear_all_page()
        self.sub_screen = 'choose members'

        self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 828), (1600, 572))),
                                                                  pygame.transform.scale(
                                                                  pygame.image.load(
                                                                      "resources/images/pick_clan_screen/clan_none_light.png").convert_alpha(),
                                                                      (1600, 1400)), manager=MANAGER)
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(scale(pygame.Rect((584, 200), (432, 100))),
                                                                     MakeClanScreen.clan_frame_img, manager=MANAGER)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   scale(pygame.Rect((585, 220), (432, 100))),
                                                                   object_id="#clan_header_text_box", manager=MANAGER)

        # info for chosen cats:
        self.elements['cat_info'] = UITextBoxTweaked("", scale(pygame.Rect((880, 520), (200, 200))), visible=False,
                                                     object_id=get_text_box_theme("#cat_profile_info_box"),
                                                     line_spacing=0.95, manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((300, 350), (1000, 110))),
                                                                  visible=False,
                                                                  object_id=get_text_box_theme(), manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((706, 720), (190, 60))), "", object_id="#recruit_button",
                                                    visible=False, manager=MANAGER)

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 800), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 800), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

        # This is doing the same thing again, but it's needed to make the "last step button work"
        self.refresh_cat_images_and_info()
        self.refresh_text_and_buttons()

    def open_choose_background(self):
        # clear screen
        self.clear_all_page()
        self.sub_screen = 'choose camp'

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements["done_button"] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                     object_id="#done_arrow_button", manager=MANAGER)
        self.elements['done_button'].disable()

        # Biome buttons
        self.elements['forest_biome'] = UIImageButton(scale(pygame.Rect((392, 200), (200, 92))), "",
                                                      object_id="#forest_biome_button", manager=MANAGER)
        self.elements['mountain_biome'] = UIImageButton(scale(pygame.Rect((608, 200), (212, 92))), "",
                                                        object_id="#mountain_biome_button", manager=MANAGER)
        self.elements['plains_biome'] = UIImageButton(scale(pygame.Rect((848, 200), (172, 92))), "",
                                                      object_id="#plains_biome_button", manager=MANAGER)
        self.elements['beach_biome'] = UIImageButton(scale(pygame.Rect((1040, 200), (164, 92))), "",
                                                     object_id="#beach_biome_button", manager=MANAGER)

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                              visible=False, manager=MANAGER)
        self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                              visible=False, manager=MANAGER)

        # Random background
        self.elements["random_background"] = UIImageButton(scale(pygame.Rect((510, 1190), (580, 60))), "",
                                                           object_id="#random_background_button", manager=MANAGER)

        # art frame
        self.elements['art_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect(((334, 324), (932, 832)))),
                                                                 pygame.transform.scale(
                                                                     pygame.image.load(
                                                                         "resources/images/bg_preview_border.png").convert_alpha(),
                                                                     (932, 832)), manager=MANAGER)

        # camp art self.elements["camp_art"] = pygame_gui.elements.UIImage(scale(pygame.Rect((175,170),(450, 400))),
        # pygame.image.load(self.get_camp_art_path(1)).convert_alpha(), visible=False)

    def open_clan_saved_screen(self):
        self.clear_all_page()
        self.sub_screen = 'saved screen'

        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((700, 240), (200, 200))),
                                                                    pygame.transform.scale(
                                                                        game.clan.leader.large_sprite,
                                                                        (200, 200)), manager=MANAGER)
        self.elements["continue"] = UIImageButton(scale(pygame.Rect((692, 500), (204, 60))), "",
                                                  object_id="#continue_button_small")
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox('Your Clan has been created and saved!',
                                                                      scale(pygame.Rect((200, 140), (1200, 60))),
                                                                      object_id=get_text_box_theme(), manager=MANAGER)

    def save_clan(self):
        convert_camp = {1: 'camp1', 2: 'camp2', 3: 'camp3'}
        game.clan = Clan(self.clan_name,
                         self.leader,
                         self.deputy,
                         self.med_cat,
                         self.biome_selected, game.switches['world_seed'],
                         game.switches['camp_site'], convert_camp[self.selected_camp_tab],
                         self.game_mode, self.members)
        game.clan.create_clan()
        game.mediated.clear()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        Cat.sort_cats()

    def get_camp_art_path(self, campnum):
        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = "newleaf"
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        biome = self.biome_selected.lower()

        if campnum:
            return f'{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png'
        else:
            return None
