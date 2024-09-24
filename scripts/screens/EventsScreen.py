import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.events import events_class
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import UIImageButton, UIModifiedScrollingContainer, IDImageButton
from scripts.game_structure.windows import GameOver
from scripts.screens.Screens import Screens
from scripts.utility import scale, clan_symbol_sprite, get_text_box_theme, shorten_text_to_fit, \
    get_living_clan_cat_count


class EventsScreen(Screens):
    current_display = "all"
    selected_display = "all"

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
    tabs = ["all", "ceremony", "birth_death", "relationship", "health", "other_clans", "misc"]

    def __init__(self, name):
        super().__init__(name)

        self.events_thread = None
        self.event_screen_container = None
        self.clan_info = {}
        self.timeskip_button = None

        self.full_event_display_container = None
        self.events_frame = None
        self.event_buttons = {}
        self.alert = {}

        self.event_display = None
        self.event_display_elements = {}
        self.cat_profile_buttons = {}
        self.involved_cat_container = None
        self.involved_cat_buttons = {}

        # Stores the involved cat button that currently has its cat profile buttons open
        self.open_involved_cat_button = None

        self.first_opened = False

    def handle_event(self, event):
        if game.switches["window_open"]:
            return

        # ON HOVER
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele in self.event_buttons:
                    if self.event_buttons[ele] == element:
                        x_pos = int(self.alert[ele].get_relative_rect()[0] - 10)
                        y_pos = self.alert[ele].get_relative_rect()[1]
                        self.alert[ele].set_relative_position((x_pos, y_pos))

        # ON UNHOVER
        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele in self.event_buttons:
                    if self.event_buttons[ele] == element:
                        x_pos = int(self.alert[ele].get_relative_rect()[0] + 10)
                        y_pos = self.alert[ele].get_relative_rect()[1]
                        self.alert[ele].set_relative_position((x_pos, y_pos))

        # ON START BUTTON PRESS
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:  # this happens on start press to prevent alert movement
            element = event.ui_element
            if element in self.event_buttons.values():
                for ele, val in self.event_buttons.items():
                    if val == element:
                        self.handle_tab_switch(ele)
                        break

        # ON FULL BUTTON PRESS
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:  # everything else on button press to prevent blinking
            element = event.ui_element
            if element == self.timeskip_button:
                self.events_thread = self.loading_screen_start_work(
                    events_class.one_moon
                )
            elif element in self.involved_cat_buttons.values():
                self.make_cat_buttons(element)
            elif element in self.cat_profile_buttons.values():
                self.save_scroll_position()
                game.switches["cat"] = element.ids
                self.change_screen("profile screen")
            else:
                self.save_scroll_position()
                self.menu_button_pressed(event)

        # KEYBIND CONTROLS
        elif game.settings["keybinds"]:
            # ON PRESSING A KEY
            if event.type == pygame.KEYDOWN:
                # LEFT ARROW
                if event.key == pygame.K_LEFT:
                    self.change_screen("patrol screen")
                # RIGHT ARROW
                elif event.key == pygame.K_RIGHT:
                    self.change_screen("camp screen")
                # DOWN AND UP ARROW
                elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    self.handle_tab_select(event.key)
                elif event.key == pygame.K_RETURN:
                    self.handle_tab_switch(self.selected_display)

    def save_scroll_position(self):
        """
        adds current event display vert scroll bar position to game.switches["saved_scroll_positions"] dict
        """
        if self.event_display.vert_scroll_bar:
            game.switches["saved_scroll_positions"][self.current_display] = (
                    self.event_display.vert_scroll_bar.scroll_position
                    / self.event_display.vert_scroll_bar.scrollable_height
            )

    def handle_tab_select(self, event):

        # find next tab based on current tab
        current_index = self.tabs.index(self.selected_display)
        if event == pygame.K_DOWN:
            next_index = current_index + 1
            wrap_index = 0
        else:
            next_index = current_index - 1
            wrap_index = -1

        # unselect the currently selected display
        # unless it matches the current display, we don't want to mess with the state of that button
        if self.current_display != self.selected_display:
            self.event_buttons[self.selected_display].unselect()
            x_pos = int(self.alert[self.selected_display].get_relative_rect()[0] + 10)
            y_pos = self.alert[self.selected_display].get_relative_rect()[1]
            self.alert[self.selected_display].set_relative_position((x_pos, y_pos))

        # find the new selected display
        try:
            self.selected_display = self.tabs[next_index]
        except IndexError:
            self.selected_display = self.tabs[wrap_index]

        # select the new selected display
        # unless it matches the current display, we don't want to mess with the state of that button
        if self.current_display != self.selected_display:
            self.event_buttons[self.selected_display].select()
            x_pos = int(self.alert[self.selected_display].get_relative_rect()[0] - 10)
            y_pos = self.alert[self.selected_display].get_relative_rect()[1]
            self.alert[self.selected_display].set_relative_position((x_pos, y_pos))

    def handle_tab_switch(self, display_type):
        """
        saves current tab scroll position, removes alert, and then switches to the new tab
        """
        self.save_scroll_position()

        self.current_display = display_type
        self.update_list_buttons()

        if display_type == "all":
            self.display_events = self.all_events
        elif display_type == "ceremony":
            self.display_events = self.ceremony_events
        elif display_type == "birth_death":
            self.display_events = self.birth_death_events
        elif display_type == "relationship":
            self.display_events = self.relation_events
        elif display_type == "health":
            self.display_events = self.health_events
        elif display_type == "other_clans":
            self.display_events = self.other_clans_events
        elif display_type == "misc":
            self.display_events = self.misc_events

        self.alert[display_type].hide()

        self.update_events_display()

    def screen_switches(self):
        # On first open, update display events list
        self.show_mute_buttons()
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

        # Set text for Clan age
        if game.clan.age == 1:
            self.clan_info["age"].set_text(f"Clan age: {game.clan.age} moon")
        if game.clan.age != 1:
            self.clan_info["age"].set_text(f"Clan age: {game.clan.age} moons")

        self.timeskip_button = UIImageButton(
            scale(pygame.Rect((620, 436), (360, 60))),
            "",
            object_id="#timeskip_button",
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER,
            sound_id="timeskip",
        )

        self.full_event_display_container = pygame_gui.core.UIContainer(
            scale(pygame.Rect((90, 532), (1400, 1400))),
            object_id="#event_display_container",
            starting_height=1,
            container=self.event_screen_container,
            manager=MANAGER
        )
        self.events_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((322, 0), (1068, 740))),
            image_cache.load_image(
                "resources/images/event_page_frame.png"
            ).convert_alpha(),
            object_id="#events_frame",
            starting_height=2,
            container=self.full_event_display_container,
            manager=MANAGER,
        )

        y_pos = 0
        for event_type in self.tabs:
            self.event_buttons[f"{event_type}"] = UIImageButton(
                scale(pygame.Rect((30, 38 + y_pos), (300, 60))),
                "",
                object_id=f"#{event_type}_events_button",
                starting_height=1,
                container=self.full_event_display_container,
                manager=MANAGER
            )

            if event_type:
                self.alert[f"{event_type}"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((20, 48 + y_pos), (8, 44))),
                    pygame.transform.scale(
                        image_cache.load_image("resources/images/alert_mark.png"), (8, 44)
                    ),
                    container=self.full_event_display_container,
                    object_id=f"alert_mark_{event_type}",
                    manager=MANAGER,
                    visible=False
                )

            y_pos += 100

        self.event_buttons[self.current_display].disable()

        self.make_event_scrolling_container()
        self.open_involved_cat_button = None
        self.update_events_display()

        # Draw and disable the correct menu buttons.
        self.set_disabled_menu_buttons(["events_screen"])
        self.update_heading_text(f"{game.clan.name}Clan")
        self.show_menu_buttons()

    def make_event_scrolling_container(self):
        """
        kills and recreates the self.event_display container
        """
        if self.event_display:
            self.event_display.kill()

        self.event_display = UIModifiedScrollingContainer(
            scale(pygame.Rect((432, 552), (1080, 700))),
            object_id="#event_display",
            starting_height=3,
            manager=MANAGER,
            allow_scroll_y=True
        )

    def make_cat_buttons(self, button_pressed):
        """Makes the buttons that take you to the profile."""

        # Check if the button you pressed doesn't have its cat profile buttons currently displayed.
        # if it does, clear the cat profile buttons
        if self.open_involved_cat_button == button_pressed:
            self.open_involved_cat_button = None
            for ele in self.cat_profile_buttons:
                self.cat_profile_buttons[ele].kill()
            self.cat_profile_buttons = {}
            return

        # If it doesn't have its buttons displayed, set the current open involved_cat_button to the pressed button,
        # clear all other buttons, and open the cat profile buttons.
        self.open_involved_cat_button = button_pressed
        if self.involved_cat_container:
            self.involved_cat_container.kill()

        x_pos = 655
        if game.settings["fullscreen"]:
            y_pos = button_pressed.get_relative_rect()[1]
        else:
            y_pos = button_pressed.get_relative_rect()[1] * 2

        self.involved_cat_container = UIModifiedScrollingContainer(
            scale(pygame.Rect((20, y_pos), (890, 108))),
            starting_height=3,
            object_id="#involved_cat_container",
            container=self.event_display,
            manager=MANAGER,
            allow_scroll_x=True
        )

        if game.settings["fullscreen"]:
            fullscreen_modifier = 0
        else:
            fullscreen_modifier = 1

        for i, cat_id in enumerate(button_pressed.ids):
            cat_ob = Cat.fetch_cat(cat_id)
            if cat_ob:
                # Shorten name if needed
                name = str(cat_ob.name)
                short_name = shorten_text_to_fit(name, 195, 26)

                self.cat_profile_buttons[f"profile_button{i}"] = IDImageButton(
                    scale(pygame.Rect((x_pos, 4), (232, 60))),
                    text=short_name,
                    ids=cat_id,
                    container=self.involved_cat_container,
                    object_id="#events_cat_profile_button",
                    layer_starting_height=1,
                    manager=MANAGER,
                )

                x_pos += -255
                if x_pos < 0:
                    x_pos += 54 * fullscreen_modifier
                    if i > 2:
                        x_pos += 73 * fullscreen_modifier

        self.involved_cat_container.set_view_container_dimensions(
            (self.involved_cat_container.get_relative_rect()[2], self.event_display.get_relative_rect()[3]))

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
        """
        Kills and recreates the event display, updates the clan info, sets the event display scroll position if it was
        previously saved
        """

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

            if game.settings["fullscreen"]:
                text_box_len = self.event_display_elements[f"event{i}"].get_relative_rect()[3]
            else:
                text_box_len = self.event_display_elements[f"event{i}"].get_relative_rect()[3] * 2

            # SHADING
            if i % 2 == 0:
                image_path = "resources/images/shading"
                if game.settings["dark mode"]:
                    image_path += "_dark.png"
                else:
                    image_path += ".png"

                if event_object.cats_involved:
                    y_len = text_box_len + 125
                else:
                    y_len = text_box_len + 45

                self.event_display_elements[f"shading{i}"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((0, y_pos), (1028, y_len))),
                    image_cache.load_image(image_path),
                    starting_height=1,
                    object_id=f"shading{i}",
                    container=self.event_display,
                    manager=MANAGER
                )
                self.event_display_elements[f"shading{i}"].disable()

            if event_object.cats_involved:
                # INVOLVED CAT BUTTON
                y_pos += text_box_len + 15

                self.involved_cat_buttons[f"cat_button{i}"] = IDImageButton(
                    scale(pygame.Rect((928, y_pos), (68, 68))),
                    ids=event_object.cats_involved,
                    layer_starting_height=3,
                    object_id="#events_cat_button",
                    container=self.event_display,
                    manager=MANAGER
                )

                y_pos += 110
            else:
                y_pos += text_box_len + 45

        # this HAS TO UPDATE before saved scroll position can be set
        self.event_display.scrollable_container.update(1)

        # don't ask me why we have to redefine these dimensions, we just do
        # otherwise the scroll position save will break
        self.event_display.set_dimensions(
            (self.event_display.get_relative_rect()[2], self.event_display.get_relative_rect()[3]))

        # set saved scroll position
        if game.switches["saved_scroll_positions"].get(self.current_display):
            self.event_display.vert_scroll_bar.set_scroll_from_start_percentage(
                game.switches["saved_scroll_positions"][self.current_display]
            )

    def update_list_buttons(self):
        """
        re-enable all event tab buttons, then disable the currently selected tab
        """
        for ele in self.event_buttons:
            self.event_buttons[ele].enable()

        self.event_buttons[self.current_display].disable()

    def on_use(self):
        self.loading_screen_on_use(self.events_thread, self.timeskip_done)
        pass

    def timeskip_done(self):
        """Various sorting and other tasks that must be done with the timeskip is over."""

        game.switches["saved_scroll_positions"] = {}

        if get_living_clan_cat_count(Cat) == 0:
            GameOver("events screen")

        self.update_display_events_lists()

        self.current_display = "all"
        self.event_buttons["all"].disable()

        for tab in self.event_buttons:
            if tab != "all":
                self.event_buttons[tab].enable()

        if not self.all_events:
            self.all_events.append(
                Single_Event("Nothing interesting happened this moon.")
            )

        self.display_events = self.all_events

        if self.ceremony_events:
            self.alert["ceremony"].show()
        else:
            self.alert["ceremony"].hide()

        if self.birth_death_events:
            self.alert["birth_death"].show()
        else:
            self.alert["birth_death"].hide()

        if self.relation_events:
            self.alert["relationship"].show()
        else:
            self.alert["relationship"].hide()

        if self.health_events:
            self.alert["health"].show()
        else:
            self.alert["health"].hide()

        if self.other_clans_events:
            self.alert["other_clans"].show()
        else:
            self.alert["other_clans"].hide()

        if self.misc_events:
            self.alert["misc"].show()
        else:
            self.alert["misc"].hide()

        self.update_events_display()
