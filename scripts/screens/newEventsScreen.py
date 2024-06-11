import pygame
import pygame_gui

from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, MANAGER, screen_y, screen_x
from scripts.game_structure.ui_elements import UIImageButton, UIModifiedScrollingContainer, IDImageButton
from scripts.screens.Screens import Screens
from scripts.utility import scale, clan_symbol_sprite, get_text_box_theme


class newEventsScreen(Screens):
    event_display_type = "all"
    all_events = ""
    ceremony_events = ""
    birth_death_events = ""
    relation_events = ""
    health_events = ""
    other_clans_events = ""
    misc_events = ""
    display_text = (
        "<center>See which events are currently happening in the Clan.</center>"
    )
    display_events = []

    def __init__(self, name):
        super().__init__(name)

        self.event_screen_container = None
        self.clan_info = {}

        self.full_event_display_container = None
        self.events_frame = None
        self.event_buttons = {}

        self.event_display = None
        self.event_display_elements = {}
        self.cat_profile_buttons = {}
        self.involved_cat_buttons = {}

        # Stores the involved cat button that currently has its cat profile buttons open
        self.open_involved_cat_button = None

        self.first_opened = False

    def handle_event(self, event):
        if game.switches["window_open"]:
            return

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele in self.event_buttons:
                    if self.event_buttons[ele] == element:
                        self.handle_tab_event(ele)
            elif element in self.involved_cat_buttons:
                pass
            elif element in self.cat_profile_buttons:
                pass
            else:
                self.menu_button_pressed(event)

    def handle_tab_event(self, display_type):
        self.event_display_type = display_type
        self.update_list_buttons()

        if display_type == "all":
            self.display_events = self.all_events
        elif display_type == "ceremony":
            self.display_events = self.ceremony_events
        elif display_type == "birth_death":
            self.display_events = self.birth_death_events
        elif display_type == "relationship":
            self.display_events = self.relation_events
        elif display_type == "other_clans":
            self.display_events = self.other_clans_events
        elif display_type == "misc":
            self.display_events = self.misc_events

        self.update_events_display()

    def screen_switches(self):
        # On first open, update display events list
        if not self.first_opened:
            self.first_opened = True
            self.update_display_events_lists()
            self.display_events = self.all_events

        self.event_screen_container = pygame_gui.core.UIContainer(
            scale(pygame.Rect((0, 0), (1600, 1400))),
            object_id="#event_screen_container",
            starting_height=1,
            manager=MANAGER
        )

        self.clan_info["symbol"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((455, 210), (200, 200))),
            pygame.transform.scale(clan_symbol_sprite(game.clan), (200, 200)),
            object_id=f"clan_symbol",
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )

        self.clan_info["heading"] = pygame_gui.elements.UITextBox(
            "Timeskip to progress your Clan's life.",
            scale(pygame.Rect((680, 310), (500, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_spacing_95"),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )

        self.clan_info["season"] = pygame_gui.elements.UITextBox(
            f"Current season: {game.clan.current_season}",
            scale(pygame.Rect((680, 205), (1200, 80))),
            object_id=get_text_box_theme("#text_box_30"),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )
        self.clan_info["age"] = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((680, 245), (1200, 80))),
            object_id=get_text_box_theme("#text_box_30"),
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
        )

        self.full_event_display_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((120, 532), (0, 0))),
            object_id="#event_display_container",
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER
        )
        self.events_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((292, 0), (1068, 740))),
            image_cache.load_image(
                "resources/images/event_page_frame.png"
            ).convert_alpha(),
            object_id="#events_frame",
            starting_height=2,
            container=self.full_event_display_container,
            manager=MANAGER,
        )

        y_pos = 0
        for event_type in ["all", "ceremony", "birth_death", "relationship", "health", "other_clans", "misc"]:
            self.event_buttons[f"{event_type}"] = UIImageButton(
                scale(pygame.Rect((0, 38 + y_pos), (300, 60))),
                "",
                object_id=f"#{event_type}_events_button",
                starting_height=1,
                container=self.full_event_display_container,
                manager=MANAGER
            )
            y_pos += 100

        self.event_buttons[self.event_display_type].disable()

        self.make_event_scrolling_container()

        self.open_involved_cat_button = None
        self.update_events_display()

    def make_event_scrolling_container(self):
        if self.event_display:
            self.event_display.kill()

        self.event_display = UIModifiedScrollingContainer(
            scale(pygame.Rect((432, 552), (1080, 700))),
            object_id="#event_display",
            starting_height=3,
            manager=MANAGER
        )

    def exit_screen(self):
        self.event_display.kill()  # event display isn't put in the screen container due to lag issues
        self.event_screen_container.kill()

    def update_display_events_lists(self):
        """
        Categorize events from game.cur_events_list into display categories for screen
        """

        self.all_events = [
            x for x in game.cur_events_list if "interaction" not in x.types
        ]
        self.ceremony_events = [
            x for x in game.cur_events_list if "ceremony" in x.types
        ]
        self.birth_death_events = [
            x for x in game.cur_events_list if "birth_death" in x.types
        ]
        self.relation_events = [
            x for x in game.cur_events_list if "relation" in x.types
        ]
        self.health_events = [
            x for x in game.cur_events_list if "health" in x.types
        ]
        self.other_clans_events = [
            x for x in game.cur_events_list if "other_clans" in x.types
        ]
        self.misc_events = [
            x for x in game.cur_events_list if "misc" in x.types
        ]

    def update_events_display(self):

        # UPDATE CLAN INFO
        self.clan_info["season"].set_text(f"Current season: {game.clan.current_season}")
        if game.clan.age == 1:
            self.clan_info["age"].set_text(f"Clan age: {game.clan.age} moon")
        else:
            self.clan_info["age"].set_text(f"Clan age: {game.clan.age} moons")

        self.make_event_scrolling_container()

        for ele in self.event_display_elements:
            self.event_display_elements[ele].kill()
        self.event_display_elements = {}

        for ele in self.cat_profile_buttons:
            self.cat_profile_buttons[ele].kill()
        self.cat_profile_buttons = {}

        for ele in self.involved_cat_buttons:
            self.involved_cat_buttons[ele].kill()
        self.involved_cat_buttons = {}

        # Stop if Clan is new, so that events from previously loaded Clan don't show up
        if game.clan.age == 0:
            return

        y_pos = 0

        for i, event_object in enumerate(self.display_events):
            # checking that text is a string
            if not isinstance(event_object.text, str):
                print(f"Incorrectly Formatted Event: {event_object.text}, {type(event_object)}")
                continue

            # TEXT BOX
            self.event_display_elements[f"event{i}"] = pygame_gui.elements.UITextBox(
                event_object.text,
                scale(pygame.Rect((0, y_pos), (1018, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"),
                starting_height=2,
                container=self.event_display,
                manager=MANAGER
            )

            # SHADING
            if i % 2 == 0:
                image_path = "resources/images/shading"
                if game.settings["dark mode"]:
                    image_path += "_dark.png"
                else:
                    image_path += ".png"

                y_len = self.event_display_elements[f"event{i}"].get_relative_rect()[3] + 100

                self.event_display_elements[f"shading{i}"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((0, y_pos), (1028, y_len))),
                    image_cache.load_image(image_path),
                    starting_height=1,
                    object_id=f"shading{i}",
                    container=self.event_display,
                    manager=MANAGER
                )

            # INVOLVED CAT BUTTON
            y_pos += self.event_display_elements[f"event{i}"].get_relative_rect()[3]

            self.involved_cat_buttons[f"cat_button{i}"] = IDImageButton(
                scale(pygame.Rect((948, y_pos + 10), (68, 68))),
                ids=event_object.cats_involved,
                layer_starting_height=3,
                object_id="#events_cat_button",
                container=self.event_display,
                manager=MANAGER
            )

            y_pos += 100

    def update_list_buttons(self):
        """
        re-enable all event tab buttons, then disable the currently selected tab
        """
        for ele in self.event_buttons:
            self.event_buttons[ele].enable()

        self.event_buttons[self.event_display_type].disable()

    def on_use(self):

        pass
