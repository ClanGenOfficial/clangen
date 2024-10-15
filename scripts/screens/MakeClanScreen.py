from random import choice, randrange
from re import sub
from typing import Optional

import pygame
import pygame_gui
from pygame_gui.core import ObjectID

import scripts.screens.screens_core.screens_core
from scripts.cat.cats import create_example_cats, create_cat, Cat
from scripts.cat.names import names
from scripts.clan import Clan
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.patrol.patrol import Patrol
from scripts.utility import get_text_box_theme, ui_scale, ui_scale_blit
from scripts.utility import ui_scale_dimensions
from .Screens import Screens
from ..cat.sprites import sprites
from ..game_structure.screen_settings import MANAGER, screen
from ..game_structure.windows import SymbolFilterWindow
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import ButtonStyles, get_button_dict
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon


class MakeClanScreen(Screens):
    # UI images
    ui_images = {
        "clan_frame": pygame.image.load(
            "resources/images/pick_clan_screen/clan_name_frame.png"
        ).convert_alpha(),
        "name_clan": pygame.image.load(
            "resources/images/pick_clan_screen/name_clan_light.png"
        ).convert_alpha(),
        "leader": pygame.image.load(
            "resources/images/pick_clan_screen/leader_light.png"
        ).convert_alpha(),
        "deputy": pygame.image.load(
            "resources/images/pick_clan_screen/deputy_light.png"
        ).convert_alpha(),
        "medic": pygame.image.load(
            "resources/images/pick_clan_screen/med_light.png"
        ).convert_alpha(),
        "pick_clan": pygame.image.load(
            "resources/images/pick_clan_screen/clan_light.png"
        ).convert_alpha(),
    }

    classic_mode_text = (
        "This mode is Clan Generator at it's most basic. "
        "The player will not be expected to manage the minutia of Clan life. <br><br>"
        "Perfect for a relaxing game session or for focusing on storytelling. <br><br>"
        "With this mode you are the eye in the sky, watching the Clan as their story unfolds. "
    )

    expanded_mode_text = (
        "A more hands-on experience. "
        "This mode has everything in Classic Mode as well as more management-focused features.<br><br>"
        "Additional include:<br>"
        "- Illnesses, Injuries, and Permanent Conditions<br>"
        "- Herb gathering and treatment<br>"
        "- Fresh-kill pile and nutrition system<br><br>"
        "With this mode you'll be making the important Clan-life decisions."
    )

    cruel_mode_text = (
        "This mode has all the features of Expanded mode, but is significantly more difficult. If "
        "you'd like a challenge with a bit of brutality, then this mode is for you.<br><br>"
        "You heard the warnings... a Cruel Season is coming. Will you survive?"
        "<br> <br>"
        "-COMING SOON-"
    )

    # This section holds all the information needed
    game_mode = "classic"  # To save the users selection before conformation.
    clan_name = ""  # To store the Clan name before conformation
    leader = None  # To store the Clan leader before conformation
    deputy = None
    med_cat = None
    members = []
    elected_camp = None

    # holds the symbol we have selected
    symbol_selected = None
    tag_list_len = 0
    # Holds biome we have selected
    biome_selected = None
    selected_camp_tab = 1
    selected_season = None
    # Camp number selected
    camp_num = "1"
    # Holds the cat we have currently selected.
    selected_cat = None
    # Hold which sub-screen we are on
    sub_screen = "game mode"
    # To hold the images for the sections. Makes it easier to kill them
    elements = {}
    tabs = {}
    symbol_buttons = {}

    # used in symbol screen only - parent container is in element dict
    text = {}

    def __init__(self, name="make_clan_screen"):
        super().__init__(name)
        # current page for symbol choosing
        self.current_page = 1

        self.rolls_left = game.config["clan_creation"]["rerolls"]
        self.menu_warning = None

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        self.set_bg("default", "mainmenu_bg")

        self.clan_frame_img = pygame.transform.scale(
            self.ui_images["clan_frame"],
            ui_scale_dimensions((216, 50)),
        )
        self.name_clan_img = pygame.transform.scale(
            self.ui_images["name_clan"],
            ui_scale_dimensions((800, 700)),
        )
        self.leader_img = pygame.transform.scale(
            self.ui_images["leader"],
            ui_scale_dimensions((800, 700)),
        )
        self.deputy_img = pygame.transform.scale(
            self.ui_images["deputy"],
            ui_scale_dimensions((800, 700)),
        )
        self.medic_img = pygame.transform.scale(
            self.ui_images["medic"],
            ui_scale_dimensions((800, 700)),
        )
        self.clan_img = pygame.transform.scale(
            self.ui_images["pick_clan"],
            ui_scale_dimensions((800, 700)),
        )

        # Reset variables
        self.game_mode: str = "classic"
        self.clan_name: str = ""
        self.selected_camp_tab: int = 1
        self.biome_selected: Optional[str] = None
        self.selected_season: str = "Newleaf"
        self.symbol_selected = None
        self.leader = None  # To store the Clan leader before confirmation
        self.deputy = None
        self.med_cat = None
        self.members = []

        # Buttons that appear on every screen.
        self.menu_warning = pygame_gui.elements.UITextBox(
            "Note: going back to main menu resets the generated cats.",
            ui_scale(pygame.Rect((25, 25), (600, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
        )
        self.main_menu = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 50), (153, 30))),
            get_arrow(3) + " Main Menu",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_squoval",
            starting_height=1,
        )
        create_example_cats()
        # self.worldseed = randrange(10000)
        self.open_game_mode()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)
            self.mute_button_pressed(event)

            if event.ui_element == self.main_menu:
                self.change_screen("start screen")
            if self.sub_screen == "game mode":
                self.handle_game_mode_event(event)
            elif self.sub_screen == "name clan":
                self.handle_name_clan_event(event)
            elif self.sub_screen == "choose leader":
                self.handle_choose_leader_event(event)
            elif self.sub_screen == "choose deputy":
                self.handle_choose_deputy_event(event)
            elif self.sub_screen == "choose med cat":
                self.handle_choose_med_event(event)
            elif self.sub_screen == "choose members":
                self.handle_choose_members_event(event)
            elif self.sub_screen == "choose camp":
                self.handle_choose_background_event(event)
            elif self.sub_screen == "choose symbol":
                self.handle_choose_symbol_event(event)
            elif self.sub_screen == "saved screen":
                self.handle_saved_clan_event(event)

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if self.sub_screen == "game mode":
                self.handle_game_mode_key(event)
            elif self.sub_screen == "name clan":
                self.handle_name_clan_key(event)
            elif self.sub_screen == "choose camp":
                self.handle_choose_background_key(event)
            elif self.sub_screen == "saved screen" and (
                event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT
            ):
                self.change_screen("start screen")

    def handle_game_mode_event(self, event):
        """Handle events for the game mode screen"""
        # Game mode selection buttons
        if event.ui_element == self.elements["classic_mode_button"]:
            self.game_mode = "classic"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["expanded_mode_button"]:
            self.game_mode = "expanded"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["cruel_mode_button"]:
            self.game_mode = "cruel season"
            self.refresh_text_and_buttons()

        # Logic for when to quick-start clan
        elif event.ui_element == self.elements["next_step"]:
            game.settings["game_mode"] = self.game_mode
            if "@checked_checkbox" in self.elements["random_clan_checkbox"].object_ids:
                self.random_quick_start()
                self.save_clan()
                self.open_clan_saved_screen()
            else:
                self.open_name_clan()
        elif event.ui_element == self.elements["random_clan_checkbox"]:
            if "@checked_checkbox" in self.elements["random_clan_checkbox"].object_ids:
                self.elements["random_clan_checkbox"].change_object_id(
                    "@unchecked_checkbox"
                )
            else:
                self.elements["random_clan_checkbox"].change_object_id(
                    "@checked_checkbox"
                )

    def handle_game_mode_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.change_screen("start screen")
        elif event.key == pygame.K_DOWN:
            if self.game_mode == "classic":
                self.game_mode = "expanded"
            elif self.game_mode == "expanded":
                self.game_mode = "cruel season"
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_UP:
            if self.game_mode == "cruel season":
                self.game_mode = "expanded"
            elif self.game_mode == "expanded":
                self.game_mode = "classic"
            self.refresh_text_and_buttons()

        elif event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
            if self.elements["next_step"].is_enabled:
                game.settings["game_mode"] = self.game_mode
                self.open_name_clan()

    def handle_name_clan_event(self, event):
        if event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(self.random_clan_name())
        elif event.ui_element == self.elements["reset_name"]:
            self.elements["name_entry"].set_text("")
        elif event.ui_element == self.elements["next_step"]:
            new_name = sub(
                r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
            ).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()
        elif event.ui_element == self.elements["previous_step"]:
            self.clan_name = ""
            self.open_game_mode()

    def handle_name_clan_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.change_screen("start screen")
        elif event.key == pygame.K_LEFT:
            if not self.elements["name_entry"].is_focused:
                self.clan_name = ""
                self.open_game_mode()
        elif event.key == pygame.K_RIGHT:
            if not self.elements["name_entry"].is_focused:
                new_name = sub(
                    r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
                ).strip()
                if not new_name:
                    self.elements["error"].set_text("Your Clan's name cannot be empty")
                    self.elements["error"].show()
                    return
                if new_name.casefold() in [
                    clan.casefold() for clan in game.switches["clan_list"]
                ]:
                    self.elements["error"].set_text(
                        "A Clan with that name already exists."
                    )
                    self.elements["error"].show()
                    return
                self.clan_name = new_name
                self.open_choose_leader()
        elif event.key == pygame.K_RETURN:
            new_name = sub(
                r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
            ).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()

    def handle_choose_leader_event(self, event):
        if event.ui_element in [
            self.elements["roll1"],
            self.elements["roll2"],
            self.elements["roll3"],
            self.elements["dice"],
        ]:
            self.elements["select_cat"].hide()
            create_example_cats()  # create new cats
            self.selected_cat = (
                None  # Your selected cat now no longer exists. Sad. They go away.
            )
            if self.elements["error_message"]:
                self.elements["error_message"].hide()
            self.refresh_cat_images_and_info()  # Refresh all the images.
            self.rolls_left -= 1
            if game.config["clan_creation"]["rerolls"] == 3:
                event.ui_element.disable()
            else:
                self.elements["reroll_count"].set_text(str(self.rolls_left))
                if self.rolls_left == 0:
                    event.ui_element.disable()

        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                clicked_cat = event.ui_element.return_cat_object()
                if clicked_cat.age not in ["newborn", "kitten", "adolescent"]:
                    self.leader = clicked_cat
                    self.selected_cat = None
                    self.open_choose_deputy()
            else:
                self.selected_cat = event.ui_element.return_cat_object()
                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["select_cat"]:
            self.leader = self.selected_cat
            self.selected_cat = None
            self.open_choose_deputy()
        elif event.ui_element == self.elements["previous_step"]:
            self.clan_name = ""
            self.open_name_clan()

    def handle_choose_deputy_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
            self.leader = None
            self.selected_cat = None
            self.open_choose_leader()
        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                clicked_cat = event.ui_element.return_cat_object()
                if clicked_cat.age not in ["newborn", "kitten", "adolescent"]:
                    self.deputy = clicked_cat
                    self.selected_cat = None
                    self.open_choose_med_cat()
            elif event.ui_element.return_cat_object() != self.leader:
                self.selected_cat = event.ui_element.return_cat_object()
                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["select_cat"]:
            self.deputy = self.selected_cat
            self.selected_cat = None
            self.open_choose_med_cat()

    def handle_choose_med_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
            self.deputy = None
            self.selected_cat = None
            self.open_choose_deputy()
        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                clicked_cat = event.ui_element.return_cat_object()
                if clicked_cat.age not in ["newborn", "kitten", "adolescent"]:
                    self.med_cat = clicked_cat
                    self.selected_cat = None
                    self.open_choose_members()
            elif event.ui_element.return_cat_object():
                self.selected_cat = event.ui_element.return_cat_object()
                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["select_cat"]:
            self.med_cat = self.selected_cat
            self.selected_cat = None
            self.open_choose_members()

    def handle_choose_members_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
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
                if pygame.key.get_mods() & pygame.KMOD_SHIFT and len(self.members) < 7:
                    clicked_cat = event.ui_element.return_cat_object()
                    self.members.append(clicked_cat)
                    self.selected_cat = None
                    self.refresh_cat_images_and_info(None)
                    self.refresh_text_and_buttons()
                else:
                    self.selected_cat = event.ui_element.return_cat_object()
                    self.refresh_cat_images_and_info(self.selected_cat)
                    self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["select_cat"]:
            self.members.append(self.selected_cat)
            self.selected_cat = None
            self.refresh_cat_images_and_info(None)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["next_step"]:
            self.selected_cat = None
            self.open_choose_background()

    def handle_choose_background_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
            self.set_bg(None)
            self.open_choose_members()
        elif event.ui_element == self.elements["forest_biome"]:
            self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["mountain_biome"]:
            self.biome_selected = "Mountainous"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["plains_biome"]:
            self.biome_selected = "Plains"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["beach_biome"]:
            self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["tab1"]:
            self.selected_camp_tab = 1
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab2"]:
            self.selected_camp_tab = 2
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab3"]:
            self.selected_camp_tab = 3
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab4"]:
            self.selected_camp_tab = 4
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["newleaf_tab"]:
            self.selected_season = "Newleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["greenleaf_tab"]:
            self.selected_season = "Greenleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leaffall_tab"]:
            self.selected_season = "Leaf-fall"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leafbare_tab"]:
            self.selected_season = "Leaf-bare"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["random_background"]:
            # Select a random biome and background
            self.biome_selected = self.random_biome_selection()
            if self.biome_selected in ["Forest", "Mountainous"]:
                self.selected_camp_tab = randrange(1, 5)
            else:
                self.selected_camp_tab = randrange(1, 4)
            self.refresh_selected_camp()
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["next_step"]:
            self.open_choose_symbol()

    def handle_choose_background_key(self, event):
        if event.key == pygame.K_RIGHT:
            if self.biome_selected is None:
                self.biome_selected = "Forest"
            elif self.biome_selected == "Forest":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_LEFT:
            if self.biome_selected is None:
                self.biome_selected = "Beach"
            elif self.biome_selected == "Beach":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_UP and self.biome_selected is not None:
            if self.selected_camp_tab > 1:
                self.selected_camp_tab -= 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_DOWN and self.biome_selected is not None:
            if self.selected_camp_tab < 4:
                self.selected_camp_tab += 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_RETURN:
            self.save_clan()
            self.open_clan_saved_screen()

    def handle_choose_symbol_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
            self.open_choose_background()
        elif event.ui_element == self.elements["page_right"]:
            self.current_page += 1
            self.refresh_symbol_list()
        elif event.ui_element == self.elements["page_left"]:
            self.current_page -= 1
            self.refresh_symbol_list()
        elif event.ui_element == self.elements["done_button"]:
            self.save_clan()
            self.open_clan_saved_screen()
        elif event.ui_element == self.elements["random_symbol_button"]:
            if self.symbol_selected:
                if self.symbol_selected in self.symbol_buttons:
                    self.symbol_buttons[self.symbol_selected].enable()
            self.symbol_selected = choice(sprites.clan_symbols)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["filters_tab"]:
            SymbolFilterWindow()
        else:
            for symbol_id, element in self.symbol_buttons.items():
                if event.ui_element == element:
                    if self.symbol_selected:
                        if self.symbol_selected in self.symbol_buttons:
                            self.symbol_buttons[self.symbol_selected].enable()
                    self.symbol_selected = symbol_id
                    self.refresh_text_and_buttons()

    def handle_saved_clan_event(self, event):
        if event.ui_element == self.elements["continue"]:
            self.change_screen("camp screen")

    def exit_screen(self):
        self.main_menu.kill()
        self.menu_warning.kill()
        self.clear_all_page()
        self.rolls_left = game.config["clan_creation"]["rerolls"]
        self.fullscreen_bgs = {}
        self.game_bgs = {}
        return super().exit_screen()

    def on_use(self):
        super().on_use()

        # Don't allow someone to enter no name for their clan
        if self.sub_screen == "name clan":
            if self.elements["name_entry"].get_text() == "":
                self.elements["next_step"].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Clan names cannot start with a space.")
                self.elements["error"].show()
                self.elements["next_step"].disable()
            elif self.elements["name_entry"].get_text().casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                self.elements["next_step"].disable()
            else:
                self.elements["error"].hide()
                self.elements["next_step"].enable()

            # Set the background for the name clan page - done here to avoid GUI layering issues
            screen.blit(self.name_clan_img, ui_scale_blit((0, 0)))

        # refreshes symbol list when filters are changed
        # - done here bc refresh_symbol_list cannot be called from windows.py
        if self.sub_screen == "choose symbol":
            if len(game.switches["disallowed_symbol_tags"]) != self.tag_list_len:
                self.tag_list_len = len(game.switches["disallowed_symbol_tags"])
                self.refresh_symbol_list()

    def clear_all_page(self):
        """Clears the entire page, including layout images"""
        for image in self.elements:
            self.elements[image].kill()
        for tab in self.tabs:
            self.tabs[tab].kill()
        for button in self.symbol_buttons:
            self.symbol_buttons[button].kill()
        self.elements = {}

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        if self.sub_screen == "game mode":
            # Set the mode explanation text
            if self.game_mode == "classic":
                display_text = self.classic_mode_text
                display_name = "Classic Mode"
            elif self.game_mode == "expanded":
                display_text = self.expanded_mode_text
                display_name = "Expanded Mode"
            elif self.game_mode == "cruel season":
                display_text = self.cruel_mode_text
                display_name = "Cruel Season"
            else:
                display_text = ""
                display_name = "ERROR"
            self.elements["mode_details"].set_text(display_text)
            self.elements["mode_name"].set_text(display_name)

            # Update the enabled buttons for the game selection to disable the
            # buttons for the mode currently selected. Mostly for aesthetics, and it
            # make it very clear which mode is selected.
            if self.game_mode == "classic":
                self.elements["classic_mode_button"].disable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].enable()
            elif self.game_mode == "expanded":
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].disable()
                self.elements["cruel_mode_button"].enable()
            elif self.game_mode == "cruel season":
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].disable()
            else:
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].enable()

            # Don't let the player go forwards with cruel mode, it's not done yet.
            if self.game_mode == "cruel season":
                self.elements["next_step"].disable()
            else:
                self.elements["next_step"].enable()
        # Show the error message if you try to choose a child for leader, deputy, or med cat.
        elif self.sub_screen in ["choose leader", "choose deputy", "choose med cat"]:
            if self.selected_cat.age in ["newborn", "kitten", "adolescent"]:
                self.elements["select_cat"].hide()
                self.elements["error_message"].show()
            else:
                self.elements["select_cat"].show()
                self.elements["error_message"].hide()
        # Refresh the choose-members background to match number of cat's chosen.
        elif self.sub_screen == "choose members":
            if len(self.members) == 0:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_none_light.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((800, 700)),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 1:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_one_light.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((800, 700)),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 2:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_two_light.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((800, 700)),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 3:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_three_light.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((800, 700)),
                    )
                )
                self.elements["next_step"].disable()
            elif 4 <= len(self.members) <= 6:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_four_light.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((800, 700)),
                    )
                )
                self.elements["next_step"].enable()
                # In order for the "previous step" to work properly, we must enable this button, just in case it
                # was disabled in the next step.
                self.elements["select_cat"].enable()
            elif len(self.members) == 7:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_full_light.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((800, 700)),
                    )
                )
                self.elements["select_cat"].disable()
                self.elements["next_step"].enable()

            # Hide the recruit cat button if no cat is selected.
            if self.selected_cat is not None:
                self.elements["select_cat"].show()
            else:
                self.elements["select_cat"].hide()

        elif self.sub_screen == "choose camp":
            # Enable/disable biome buttons
            if self.biome_selected == "Forest":
                self.elements["forest_biome"].disable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Mountainous":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].disable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Plains":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].disable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Beach":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].disable()

            if self.selected_season == "Newleaf":
                self.tabs["newleaf_tab"].disable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Greenleaf":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].disable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Leaf-fall":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].disable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Leaf-bare":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].disable()

            if self.biome_selected and self.selected_camp_tab:
                self.elements["next_step"].enable()

            # Deal with tab and shown camp image:
            self.refresh_selected_camp()
        elif self.sub_screen == "choose symbol":
            if self.symbol_selected:
                if self.symbol_selected in self.symbol_buttons:
                    self.symbol_buttons[self.symbol_selected].disable()
                # refresh selected symbol image
                self.elements["selected_symbol"].set_image(
                    pygame.transform.scale(
                        sprites.sprites[self.symbol_selected],
                        ui_scale_dimensions((100, 100)),
                    ).convert_alpha()
                )
                symbol_name = self.symbol_selected.replace("symbol", "")
                self.text["selected"].set_text(f"Selected Symbol: {symbol_name}")
                self.elements["selected_symbol"].show()
                self.elements["done_button"].enable()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""
        self.tabs["tab1"].kill()
        self.tabs["tab2"].kill()
        self.tabs["tab3"].kill()
        self.tabs["tab4"].kill()

        if self.biome_selected == "Forest":
            self.tabs["tab1"] = UIImageButton(
                ui_scale(pygame.Rect((95, 180), (154, 30))),
                "",
                object_id="#classic_tab",
                manager=MANAGER,
            )
            self.tabs["tab2"] = UIImageButton(
                ui_scale(pygame.Rect((108, 215), (154, 30))),
                "",
                object_id="#gully_tab",
                manager=MANAGER,
            )
            self.tabs["tab3"] = UIImageButton(
                ui_scale(pygame.Rect((95, 250), (154, 30))),
                "",
                object_id="#grotto_tab",
                manager=MANAGER,
            )
            self.tabs["tab4"] = UIImageButton(
                ui_scale(pygame.Rect((85, 285), (154, 30))),
                "",
                object_id="#lakeside_tab",
                manager=MANAGER,
            )
        elif self.biome_selected == "Mountainous":
            self.tabs["tab1"] = UIImageButton(
                ui_scale(pygame.Rect((111, 180), (154, 30))),
                "",
                object_id="#cliff_tab",
                manager=MANAGER,
            )
            self.tabs["tab2"] = UIImageButton(
                ui_scale(pygame.Rect((90, 215), (154, 30))),
                "",
                object_id="#cave_tab",
                manager=MANAGER,
            )
            self.tabs["tab3"] = UIImageButton(
                ui_scale(pygame.Rect((42, 250), (179, 30))),
                "",
                object_id="#crystal_tab",
                manager=MANAGER,
            )
            self.tabs["tab4"] = UIImageButton(
                ui_scale(pygame.Rect((107, 285), (154, 30))),
                "",
                object_id="#ruins_tab",
                manager=MANAGER,
            )
        elif self.biome_selected == "Plains":
            self.tabs["tab1"] = UIImageButton(
                ui_scale(pygame.Rect((64, 180), (154, 30))),
                "",
                object_id="#grasslands_tab",
                manager=MANAGER,
            )
            self.tabs["tab2"] = UIImageButton(
                ui_scale(pygame.Rect((89, 215), (154, 30))),
                "",
                object_id="#tunnel_tab",
                manager=MANAGER,
            )
            self.tabs["tab3"] = UIImageButton(
                ui_scale(pygame.Rect((64, 250), (154, 30))),
                "",
                object_id="#wasteland_tab",
                manager=MANAGER,
            )
        elif self.biome_selected == "Beach":
            self.tabs["tab1"] = UIImageButton(
                ui_scale(pygame.Rect((76, 180), (154, 30))),
                "",
                object_id="#tidepool_tab",
                manager=MANAGER,
            )
            self.tabs["tab2"] = UIImageButton(
                ui_scale(pygame.Rect((65, 215), (154, 30))),
                "",
                object_id="#tidal_cave_tab",
                manager=MANAGER,
            )
            self.tabs["tab3"] = UIImageButton(
                ui_scale(pygame.Rect((70, 250), (154, 30))),
                "",
                object_id="#shipwreck_tab",
                manager=MANAGER,
            )

        self.tabs["tab1"].disable() if self.selected_camp_tab == 1 else self.tabs[
            "tab1"
        ].enable()
        self.tabs["tab2"].disable() if self.selected_camp_tab == 2 else self.tabs[
            "tab2"
        ].enable()
        self.tabs["tab3"].disable() if self.selected_camp_tab == 3 else self.tabs[
            "tab3"
        ].enable()
        self.tabs["tab4"].disable() if self.selected_camp_tab == 4 else self.tabs[
            "tab4"
        ].enable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        if self.biome_selected:
            src = pygame.image.load(
                self.get_camp_art_path(self.selected_camp_tab)
            ).convert_alpha()
            self.elements["camp_art"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((175, 170), (450, 400))),
                pygame.transform.scale(
                    src.copy(),
                    ui_scale_dimensions((450, 400)),
                ),
                manager=MANAGER,
            )
            self.get_camp_bg(src)

        self.draw_art_frame()

    def get_camp_bg(self, src=None):
        if src is None:
            src = pygame.image.load(
                self.get_camp_art_path(self.selected_camp_tab)
            ).convert_alpha()

        name = "_".join(
            [
                str(self.biome_selected),
                str(self.selected_camp_tab),
                self.selected_season,
            ]
        )
        if name not in self.game_bgs:
            self.game_bgs[
                name
            ] = scripts.screens.screens_core.screens_core.default_game_bgs[self.theme][
                "default"
            ]
            self.fullscreen_bgs[
                name
            ] = scripts.screens.screens_core.screens_core.process_blur_bg(src)

        self.set_bg(name)

    def refresh_selected_cat_info(self, selected=None):
        # SELECTED CAT INFO
        if selected is not None:
            if self.sub_screen == "choose leader":
                self.elements["cat_name"].set_text(
                    str(selected.name) + " --> " + selected.name.prefix + "star"
                )
            else:
                self.elements["cat_name"].set_text(str(selected.name))
            self.elements["cat_name"].show()
            self.elements["cat_info"].set_text(
                selected.genderalign
                + "\n"
                + str(
                    selected.age
                    + "\n"
                    + str(selected.personality.trait)
                    + "\n"
                    + str(selected.skills.skill_string())
                )
            )
            self.elements["cat_info"].show()
        else:
            self.elements["next_step"].disable()
            self.elements["cat_info"].hide()
            self.elements["cat_name"].hide()

    def refresh_cat_images_and_info(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats."""

        column_poss = [50, 100]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements[
                    "cat" + str(u)
                ] = UISpriteButton(
                    ui_scale(pygame.Rect((270, 200), (150, 150))),
                    pygame.transform.scale(
                        game.choose_cats[u].sprite, ui_scale_dimensions((150, 150))
                    ),
                    cat_object=game.choose_cats[u],
                )
            elif (
                game.choose_cats[u]
                in [self.leader, self.deputy, self.med_cat] + self.members
            ):
                self.elements["cat" + str(u)] = UISpriteButton(
                    ui_scale(pygame.Rect((650, 130 + 50 * u), (50, 50))),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u],
                    manager=MANAGER,
                )
                self.elements["cat" + str(u)].disable()
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    ui_scale(pygame.Rect((column_poss[0], 130 + 50 * u), (50, 50))),
                    game.choose_cats[u].sprite,
                    tool_tip_text=self._get_cat_tooltip_string(game.choose_cats[u]),
                    cat_object=game.choose_cats[u],
                    manager=MANAGER,
                )
        for u in range(6, 12):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements[
                    "cat" + str(u)
                ] = UISpriteButton(
                    ui_scale(pygame.Rect((270, 200), (150, 150))),
                    pygame.transform.scale(
                        game.choose_cats[u].sprite, ui_scale_dimensions((150, 150))
                    ),
                    cat_object=game.choose_cats[u],
                    manager=MANAGER,
                )
            elif (
                game.choose_cats[u]
                in [self.leader, self.deputy, self.med_cat] + self.members
            ):
                self.elements["cat" + str(u)] = UISpriteButton(
                    ui_scale(pygame.Rect((700, 130 + 50 * (u - 6)), (50, 50))),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u],
                    manager=MANAGER,
                )
                self.elements["cat" + str(u)].disable()
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    ui_scale(
                        pygame.Rect((column_poss[1], 130 + 50 * (u - 6)), (50, 50))
                    ),
                    game.choose_cats[u].sprite,
                    tool_tip_text=self._get_cat_tooltip_string(game.choose_cats[u]),
                    cat_object=game.choose_cats[u],
                    manager=MANAGER,
                )

    def refresh_symbol_list(self):
        # get symbol list
        symbol_list = sprites.clan_symbols.copy()
        symbol_attributes = sprites.symbol_dict

        # filtering out tagged symbols
        for symbol in sprites.clan_symbols:
            index = symbol[-1]
            name = symbol.strip("symbol1234567890")
            tags = symbol_attributes[name.capitalize()][f"tags{index}"]
            for tag in tags:
                if tag in game.switches["disallowed_symbol_tags"]:
                    if symbol in symbol_list:
                        symbol_list.remove(symbol)

        # separate list into chunks for pages
        symbol_chunks = self.chunks(symbol_list, 45)

        # clamp current page to a valid page number
        self.current_page = max(1, min(self.current_page, len(symbol_chunks)))

        # handles which arrow buttons are clickable
        if len(symbol_chunks) <= 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].disable()
        elif self.current_page >= len(symbol_chunks):
            self.elements["page_left"].enable()
            self.elements["page_right"].disable()
        elif self.current_page == 1 and len(symbol_chunks) > 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].enable()
        else:
            self.elements["page_left"].enable()
            self.elements["page_right"].enable()

        display_symbols = []
        if symbol_chunks:
            display_symbols = symbol_chunks[self.current_page - 1]

        # Kill all currently displayed symbols
        symbol_images = [ele for ele in self.elements if ele in sprites.clan_symbols]
        for ele in symbol_images:
            self.elements[ele].kill()
            if self.symbol_buttons:
                self.symbol_buttons[ele].kill()

        x_pos = 96
        y_pos = 270
        for symbol in display_symbols:
            self.elements[f"{symbol}"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, y_pos), (50, 50))),
                sprites.sprites[symbol],
                object_id=f"#{symbol}",
                starting_height=3,
                manager=MANAGER,
            )
            self.symbol_buttons[f"{symbol}"] = UIImageButton(
                ui_scale(pygame.Rect((x_pos - 12, y_pos - 12), (74, 74))),
                "",
                object_id=f"#symbol_select_button",
                starting_height=4,
                manager=MANAGER,
            )
            x_pos += 70
            if x_pos >= 715:
                x_pos = 96
                y_pos += 70

        if self.symbol_selected in self.symbol_buttons:
            self.symbol_buttons[self.symbol_selected].disable()

    def random_quick_start(self):
        self.clan_name = self.random_clan_name()
        self.biome_selected = self.random_biome_selection()
        if self.biome_selected in ["Forest", "Mountainous"]:
            self.selected_camp_tab = randrange(1, 5)
        else:
            self.selected_camp_tab = randrange(1, 4)
        if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
            # Use recommended symbol if it exists
            self.symbol_selected = f"symbol{self.clan_name.upper()}0"
        else:
            self.symbol_selected = choice(sprites.clan_symbols)
        self.leader = create_cat(status="warrior")
        self.deputy = create_cat(status="warrior")
        self.med_cat = create_cat(status="warrior")
        for _ in range(randrange(4, 8)):
            random_status = choice(
                ["kitten", "apprentice", "warrior", "warrior", "elder"]
            )
            self.members.append(create_cat(status=random_status))

    def random_clan_name(self):
        clan_names = (
            names.names_dict["normal_prefixes"] + names.names_dict["clan_prefixes"]
        )
        while True:
            chosen_name = choice(clan_names)
            if chosen_name.casefold() not in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                return chosen_name
            print("Generated clan name was already in use! Rerolling...")

    def random_biome_selection(self):
        # Select a random biome and background
        old_biome = self.biome_selected
        possible_biomes = ["Forest", "Mountainous", "Plains", "Beach"]
        # ensuring that the new random camp will not be the same one
        if old_biome is not None:
            possible_biomes.remove(old_biome)
        chosen_biome = choice(possible_biomes)
        return chosen_biome

    def _get_cat_tooltip_string(self, cat: Cat):
        """Get tooltip for cat. Tooltip displays name, sex, age group, and trait."""

        return f"<b>{cat.name}</b><br>{cat.genderalign}<br>{cat.age}<br>{cat.personality.trait}"

    def open_game_mode(self):
        # Clear previous screen
        self.clear_all_page()
        self.sub_screen = "game mode"

        text_box = image_cache.load_image(
            "resources/images/game_mode_text_box.png"
        ).convert_alpha()

        self.elements["game_mode_background"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((325, 130), (399, 461))),
            pygame.transform.scale(text_box, ui_scale_dimensions((399, 461))),
            manager=MANAGER,
        )
        self.elements["permi_warning"] = pygame_gui.elements.UITextBox(
            "Your Clan's game mode is permanent and cannot be changed after Clan creation.",
            ui_scale(pygame.Rect((100, 581), (600, 40))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        # Create all the elements.

        self.elements["classic_mode_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((109, 240), (132, 30))),
            "Classic Mode",
            get_button_dict(ButtonStyles.SQUOVAL, (132, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.elements["expanded_mode_button"] = UIImageButton(
            ui_scale(pygame.Rect((94, 320), (162, 34))),
            "",
            object_id="#expanded_mode_button",
            manager=MANAGER,
        )
        self.elements["cruel_mode_button"] = UIImageButton(
            ui_scale(pygame.Rect((100, 400), (150, 30))),
            "",
            object_id="#cruel_mode_button",
            manager=MANAGER,
        )
        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 620), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["previous_step"].disable()
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 620), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["random_clan_checkbox"] = UIImageButton(
            ui_scale(pygame.Rect((560, -32), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            manager=MANAGER,
            tool_tip_text="When checked, a completely random Clan starting in Newleaf will be generated.",
            anchors={"top_target": self.elements["previous_step"]},
        )

        self.elements["random_clan_checkbox_label"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((5, -28), (-1, -1))),
            "Quick Start",
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            anchors={
                "left_target": self.elements["random_clan_checkbox"],
                "top_target": self.elements["random_clan_checkbox"],
                "centerx": self.elements["random_clan_checkbox"],
            },
        )
        self.elements["mode_details"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((325, 160), (405, 461))),
            object_id="#text_box_30_horizleft_pad_40_40",
            manager=MANAGER,
        )
        self.elements["mode_details"].padding = (40, 40)

        self.elements["mode_name"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((425, 135), (200, 27))),
            object_id="#text_box_30_horizcenter_light",
            manager=MANAGER,
        )

        self.refresh_text_and_buttons()

    def open_name_clan(self):
        """Opens the name Clan screen"""
        self.clear_all_page()
        self.sub_screen = "name clan"

        # Create all the elements.
        self.elements["random"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((224, 595), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )

        self.elements["error"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((506, 1310), (596, -1))),
            manager=MANAGER,
            object_id="#default_dark",
            visible=False,
        )

        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 635), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 635), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((265, 597), (140, 29))),
            manager=MANAGER,
        )
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- ")
        )
        self.elements["name_entry"].set_text_length_limit(11)
        self.elements["clan"] = pygame_gui.elements.UITextBox(
            "-Clan",
            ui_scale(pygame.Rect((375, 600), (100, 25))),
            object_id="#text_box_30_horizcenter_light",
            manager=MANAGER,
        )
        self.elements["reset_name"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((455, 595), (134, 30))),
            "reset name",
            get_button_dict(ButtonStyles.SQUOVAL, (134, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

    def clan_name_header(self):
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((292, 100), (216, 50))),
            self.clan_frame_img,
            manager=MANAGER,
        )
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(
            self.clan_name + "Clan",
            ui_scale(pygame.Rect((292, 100), (216, 50))),
            object_id=ObjectID("#text_box_30_horizcenter_vertcenter", "#dark"),
            manager=MANAGER,
        )

    def open_choose_leader(self):
        """Set up the screen for the choose leader phase."""
        self.clear_all_page()
        self.sub_screen = "choose leader"

        self.elements["background"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 414), (800, 286))),
            self.leader_img,
            manager=MANAGER,
        )

        self.elements["background"].disable()
        self.clan_name_header()

        # Roll_buttons
        x_pos = 155
        y_pos = 235
        self.elements["roll1"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((x_pos, y_pos), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        y_pos += 40
        self.elements["roll2"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((x_pos, y_pos), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        y_pos += 40
        self.elements["roll3"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((x_pos, y_pos), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )

        _tmp = 80
        if self.rolls_left == -1:
            _tmp += 5
        self.elements["dice"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((_tmp, 435), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        del _tmp
        self.elements["reroll_count"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((100, 440), (50, 25))),
            str(self.rolls_left),
            object_id=get_text_box_theme(""),
            manager=MANAGER,
        )

        if game.config["clan_creation"]["rerolls"] == 3:
            if self.rolls_left <= 2:
                self.elements["roll1"].disable()
            if self.rolls_left <= 1:
                self.elements["roll2"].disable()
            if self.rolls_left == 0:
                self.elements["roll3"].disable()
            self.elements["dice"].hide()
            self.elements["reroll_count"].hide()
        else:
            if self.rolls_left == 0:
                self.elements["dice"].disable()
            elif self.rolls_left == -1:
                self.elements["reroll_count"].hide()
            self.elements["roll1"].hide()
            self.elements["roll2"].hide()
            self.elements["roll3"].hide()

        self.create_cat_info()

        self.elements["select_cat"] = UIImageButton(
            ui_scale(pygame.Rect((234, 348), (332, 52))),
            "",
            object_id="#nine_lives_button",
            starting_height=2,
            visible=False,
            manager=MANAGER,
        )
        # Error message, to appear if you can't choose that cat.
        self.elements["error_message"] = pygame_gui.elements.UITextBox(
            "Too young to become leader",
            ui_scale(pygame.Rect((150, 353), (500, 55))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_red"),
            visible=False,
            manager=MANAGER,
        )

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 400), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 400), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_choose_deputy(self):
        """Open sub-page to select deputy."""
        self.clear_all_page()
        self.sub_screen = "choose deputy"

        self.elements["background"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 414), (800, 286))),
            self.deputy_img,
            manager=MANAGER,
        )
        self.elements["background"].disable()
        self.clan_name_header()

        self.create_cat_info()

        self.elements["select_cat"] = UIImageButton(
            ui_scale(pygame.Rect((209, 348), (384, 52))),
            "",
            object_id="#support_leader_button",
            starting_height=2,
            visible=False,
            manager=MANAGER,
        )
        # Error message, to appear if you can't choose that cat.
        self.elements["error_message"] = pygame_gui.elements.UITextBox(
            "Too young to become deputy",
            ui_scale(pygame.Rect((150, 353), (500, 55))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_red"),
            visible=False,
            manager=MANAGER,
        )

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 400), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 400), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_choose_med_cat(self):
        self.clear_all_page()
        self.sub_screen = "choose med cat"

        self.elements["background"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 414), (800, 286))),
            self.medic_img,
            manager=MANAGER,
        )
        self.clan_name_header()

        self.create_cat_info()

        self.elements["select_cat"] = UIImageButton(
            ui_scale(pygame.Rect((260, 342), (306, 58))),
            "",
            object_id="#aid_clan_button",
            starting_height=2,
            visible=False,
            manager=MANAGER,
        )
        # Error message, to appear if you can't choose that cat.
        self.elements["error_message"] = pygame_gui.elements.UITextBox(
            "Too young to become a medicine cat",
            ui_scale(pygame.Rect((150, 353), (500, 55))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_red"),
            visible=False,
            manager=MANAGER,
        )

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 400), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 400), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_choose_members(self):
        self.clear_all_page()
        self.sub_screen = "choose members"

        self.elements["background"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 414), (800, 286))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/pick_clan_screen/clan_none_light.png"
                ).convert_alpha(),
                ui_scale_dimensions((800, 700)),
            ),
            manager=MANAGER,
        )
        self.elements["background"].disable()
        self.clan_name_header()

        self.create_cat_info()

        self.elements["select_cat"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((353, 360), (95, 30))),
            "Recruit",
            get_button_dict(ButtonStyles.SQUOVAL, (95, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=2,
            visible=False,
            manager=MANAGER,
        )

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 400), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 400), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

        # draw cats to choose from
        self.refresh_cat_images_and_info()

        # This is doing the same thing again, but it's needed to make the "last step button work"
        self.refresh_cat_images_and_info()
        self.refresh_text_and_buttons()

    def open_choose_background(self):
        # clear screen
        self.clear_all_page()
        self.sub_screen = "choose camp"

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 645), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 645), (147, 30))),
            "Next Step " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

        # Biome buttons
        self.elements["forest_biome"] = UIImageButton(
            ui_scale(pygame.Rect((196, 100), (100, 46))),
            "",
            object_id="#forest_biome_button",
            manager=MANAGER,
        )
        self.elements["mountain_biome"] = UIImageButton(
            ui_scale(pygame.Rect((304, 100), (106, 46))),
            "",
            object_id="#mountain_biome_button",
            manager=MANAGER,
        )
        self.elements["plains_biome"] = UIImageButton(
            ui_scale(pygame.Rect((424, 100), (88, 46))),
            "",
            object_id="#plains_biome_button",
            manager=MANAGER,
        )
        self.elements["beach_biome"] = UIImageButton(
            ui_scale(pygame.Rect((520, 100), (82, 46))),
            "",
            object_id="#beach_biome_button",
            manager=MANAGER,
        )

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        self.tabs["tab1"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (0, 0))), "", visible=False, manager=MANAGER
        )
        self.tabs["tab2"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (0, 0))), "", visible=False, manager=MANAGER
        )
        self.tabs["tab3"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (0, 0))), "", visible=False, manager=MANAGER
        )
        self.tabs["tab4"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (0, 0))), "", visible=False, manager=MANAGER
        )

        self.tabs["newleaf_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 275), (39, 34))),
            Icon.NEWLEAF,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="Switch starting season to Newleaf.",
        )
        self.tabs["greenleaf_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 25), (39, 34))),
            Icon.GREENLEAF,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="Switch starting season to Greenleaf.",
            anchors={"top_target": self.tabs["newleaf_tab"]},
        )
        self.tabs["leaffall_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 25), (39, 34))),
            Icon.LEAFFALL,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="Switch starting season to Leaf-fall.",
            anchors={"top_target": self.tabs["greenleaf_tab"]},
        )
        self.tabs["leafbare_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 25), (39, 34))),
            Icon.LEAFBARE,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="Switch starting season to Leaf-bare.",
            anchors={"top_target": self.tabs["leaffall_tab"]},
        )
        # Random background
        self.elements["random_background"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((255, 595), (290, 30))),
            "choose a random background",
            get_button_dict(ButtonStyles.SQUOVAL, (290, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # art frame
        self.draw_art_frame()

    def open_choose_symbol(self):
        # clear screen
        self.clear_all_page()

        # set basics
        self.sub_screen = "choose symbol"

        self.elements["previous_step"] = UIImageButton(
            ui_scale(pygame.Rect((253, 645), (147, 30))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["done_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 645), (147, 30))),
            "Done " + get_arrow(5, arrow_left=False),
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["done_button"].disable()

        # create screen specific elements
        self.elements["text_container"] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((85, 105), (0, 0))),
            object_id="text_container",
            starting_height=1,
            manager=MANAGER,
        )
        self.text["clan_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 0), (-1, -1))),
            text=f"{self.clan_name}Clan",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_40"),
            manager=MANAGER,
            anchors={"left": "left"},
        )
        self.text["biome"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (-1, -1))),
            text=f"{self.biome_selected}",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            anchors={
                "top_target": self.text["clan_name"],
            },
        )
        self.text["leader"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (-1, -1))),
            text=f"Leader name: {self.leader.name.prefix}star",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            anchors={
                "top_target": self.text["biome"],
            },
        )
        self.text["recommend"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (-1, -1))),
            text=f"Recommended Symbol: N/A",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            anchors={
                "top_target": self.text["leader"],
            },
        )
        self.text["selected"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 15), (-1, -1))),
            text=f"Selected Symbol: N/A",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            anchors={
                "top_target": self.text["recommend"],
            },
        )

        self.elements["random_symbol_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((496, 206), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )

        self.elements["symbol_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((540, 90), (169, 166))),
            get_box(BoxStyles.FRAME, (169, 166), sides=(True, True, False, True)),
            object_id="@boxstyles_frame",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["page_left"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((47, 414), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["page_right"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((719, 414), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["filters_tab"] = UIImageButton(
            ui_scale(pygame.Rect((100, 619), (78, 30))),
            "",
            object_id="#filters_tab_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["symbol_list_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((76, 250), (650, 370))),
            get_box(BoxStyles.ROUNDED_BOX, (650, 370)),
            object_id="#symbol_list_frame",
            starting_height=2,
            manager=MANAGER,
        )

        if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
            self.text["recommend"].set_text(
                f"Recommended Symbol: {self.clan_name.upper()}0"
            )

        if not self.symbol_selected:
            if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
                self.symbol_selected = f"symbol{self.clan_name.upper()}0"

                self.text["selected"].set_text(
                    f"Selected Symbol: {self.clan_name.upper()}0"
                )

        if self.symbol_selected:
            symbol_name = self.symbol_selected.replace("symbol", "")
            self.text["selected"].set_text(f"Selected Symbol: {symbol_name}")

            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((573, 127), (100, 100))),
                pygame.transform.scale(
                    sprites.sprites[self.symbol_selected],
                    ui_scale_dimensions((100, 100)),
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
            )
            self.refresh_symbol_list()
            while self.symbol_selected not in self.symbol_buttons:
                self.current_page += 1
                self.refresh_symbol_list()
            self.elements["done_button"].enable()
        else:
            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((573, 127), (100, 100))),
                pygame.transform.scale(
                    sprites.sprites["symbolADDER0"],
                    ui_scale_dimensions((100, 100)),
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
                visible=False,
            )
            self.refresh_symbol_list()

    def open_clan_saved_screen(self):
        self.clear_all_page()
        self.sub_screen = "saved screen"

        self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((350, 105), (100, 100))),
            pygame.transform.scale(
                sprites.dark_mode_symbol(sprites.sprites[self.symbol_selected])
                if game.settings["dark mode"]
                else sprites.sprites[self.symbol_selected],
                ui_scale_dimensions((100, 100)),
            ).convert_alpha(),
            object_id="#selected_symbol",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["leader_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((350, 125), (100, 100))),
            pygame.transform.scale(
                game.clan.leader.sprite, ui_scale_dimensions((100, 100))
            ),
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["continue"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((346, 250), (102, 30))),
            "continue",
            get_button_dict(ButtonStyles.SQUOVAL, (102, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="save",
        )
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox(
            "Your Clan has been created and saved!",
            ui_scale(pygame.Rect((100, 70), (600, 30))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        self.get_camp_bg()

        scripts.screens.screens_core.screens_core.rebuild_bgs()

    def save_clan(self):
        game.mediated.clear()
        game.patrolled.clear()
        game.cat_to_fade.clear()
        Cat.outside_cats.clear()
        Patrol.used_patrols.clear()
        convert_camp = {1: "camp1", 2: "camp2", 3: "camp3", 4: "camp4"}
        game.clan = Clan(
            name=self.clan_name,
            leader=self.leader,
            deputy=self.deputy,
            medicine_cat=self.med_cat,
            biome=self.biome_selected,
            camp_bg=convert_camp[self.selected_camp_tab],
            symbol=self.symbol_selected,
            game_mode=self.game_mode,
            starting_members=self.members,
            starting_season=self.selected_season,
        )
        game.clan.create_clan()
        # game.clan.starclan_cats.clear()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        Cat.grief_strings.clear()
        Cat.sort_cats()

    def get_camp_art_path(self, campnum) -> Optional[str]:
        if not campnum:
            return None

        leaf = self.selected_season.replace("-", "")

        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = leaf.casefold()
        light_dark = "dark" if game.settings["dark mode"] else "light"

        biome = self.biome_selected.lower()

        return (
            f"{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png"
        )

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    def draw_art_frame(self):
        if "art_frame" in self.elements:
            self.elements["art_frame"].kill()
        self.elements["art_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect(((0, 20), (466, 416)))),
            get_box(BoxStyles.FRAME, (466, 416)),
            manager=MANAGER,
            anchors={"center": "center"},
        )

    def create_cat_info(self):
        self.elements["cat_name"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 10), (250, 60))),
            visible=False,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["name_backdrop"],
                "centerx": "centerx",
            },
        )

        # info for chosen cats:
        self.elements["cat_info"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((440, 220), (175, 125))),
            visible=False,
            object_id=get_text_box_theme("#text_box_26_horizcenter"),
            manager=MANAGER,
        )


make_clan_screen = MakeClanScreen()
