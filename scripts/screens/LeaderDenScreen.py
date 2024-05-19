import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.cat.sprites import sprites
from scripts.clan import OtherClan
from scripts.game_structure.windows import SelectFocusClans
from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.utility import get_med_cats, scale, get_text_box_theme, get_other_clan_relation, get_other_clan, \
    clan_symbol_sprite


class LeaderDenScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.back_button = None

        self.screen_elements = {}
        self.notice_text = None
        self.temper_text = None

        self.focus_frame_container = None
        self.focus_frame_elements = {}
        self.focus_clan_container = None
        self.focus_clan_elements = {}

        self.other_clan_selection_container = None
        self.other_clan_selection_elements = {}

        self.outsider_selection_container = None
        self.outsider_selection_elements = {}

        self.focus_clan = None
        self.leader_name = None
        self.clan_temper = None

    def handle_event(self, event):
        """
        Handles button presses / events
        """

        # prevent interaction if a window is open
        if game.switches['window_open']:
            pass

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.focus_frame_elements["negative_interaction"]:
                object_id = self.focus_frame_elements["negative_interaction"].get_object_ids()
                self.update_interaction_choice(object_id[1])
            elif event.ui_element == self.focus_frame_elements["positive_interaction"]:
                object_id = self.focus_frame_elements["positive_interaction"].get_object_ids()
                self.update_interaction_choice(object_id[1])
            elif event.ui_element == self.focus_frame_elements["clans_tab"]:
                self.open_clans_tab()
            elif event.ui_element == self.focus_frame_elements["outsiders_tab"]:
                self.open_outsiders_tab()
            for i in [0, 1, 2, 3, 4]:
                if f"button{i}" not in self.other_clan_selection_elements:
                    continue
                if event.ui_element == self.other_clan_selection_elements[f"button{i}"]:
                    print("button press")
                    self.focus_clan = game.clan.all_clans[i]
                    self.update_other_clan_focus()

    def screen_switches(self):
        """
        Handle creating new elements when switching to this screen
        """
        # no menu header allowed
        self.hide_menu_buttons()

        # BACK AND HELP
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.help_button = UIImageButton(scale(pygame.Rect(
            (1450, 50), (68, 68))),
            "",
            object_id="#help_button", manager=MANAGER,
            tool_tip_text="This screen allows you to check on the other cats who live nearby, both Outsiders and "
                          "other Clan cats.  You can control how the leader of your Clan will treat other leaders at "
                          "Gatherings, but keep in mind that you can only determine one interaction each moon!  "
                          "Likewise, you can consider whether to drive out or invite in Outsider cats.  If you drive "
                          "out a cat, they will no longer appear in the Cats Outside the Clans list.  If you invite "
                          "in a cat, they might join your Clan!",
        )

        # TODO: leader den BG image
        self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (1400, 900))),
            pygame.image.load(
                f"resources/images/lead_den_bg/{game.clan.biome.lower()}/{game.clan.camp_bg.lower()}.png").convert_alpha(),
            object_id="#lead_den_bg",
            starting_height=1,
            manager=MANAGER)

        self.screen_elements["lead_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((460, 460), (300, 300))),
            pygame.transform.scale(game.clan.leader.sprite, (300, 300)),
            object_id="#lead_cat_image",
            starting_height=2,
            manager=MANAGER)

        # TODO: leader cat sprite

        # FOCUS FRAME - container and inner elements
        self.create_focus_frame()

        # OTHER CLAN SELECTION BOX - container and inner elements
        self.create_other_clan_selection_box()

        # OUTSIDER SELECTION - container and inner elements
        # this starts off invisible
        self.outsider_selection_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((175, 910), (100, 100))),
            object_id="#outsider_selection_container",
            starting_height=2,
            manager=MANAGER,
            visible=False)

        self.outsider_selection_elements["frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (1248, 348))),
            pygame.image.load(
                "resources/images/lead_den_outsider_frame.png").convert_alpha(),
            object_id="#lead_den_outsider_frame",
            container=self.outsider_selection_container,
            starting_height=1,
            manager=MANAGER)

        # NOTICE TEXT - leader intention and other clan impressions
        self.leader_name = game.clan.leader.name
        self.clan_temper = game.clan.temperament

        self.screen_elements["notice_text"] = pygame_gui.elements.UITextBox(
            relative_rect=scale(pygame.Rect((135, 750), (890, -1))),
            html_text=f" {self.leader_name} is considering how to handle the next Gathering. ",
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER
        )
        self.screen_elements["temper_text"] = pygame_gui.elements.UITextBox(
            relative_rect=scale(pygame.Rect((135, 820), (890, -1))),
            html_text=f"The other Clans think {game.clan.name}Clan is {self.clan_temper}.",
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER
        )

        # INITIAL DISPLAY - display currently chosen interaction OR first clan in list
        if "clan_interaction" in game.clan.clan_settings:
            current_setting = game.clan.clan_settings["clan_interaction"]
            if current_setting:
                self.focus_clan = get_other_clan(current_setting[0])
                self.update_other_clan_focus()
                self.update_interaction_choice(current_setting[1])
        else:
            self.focus_clan = game.clan.all_clans[0]
            self.update_other_clan_focus()

    def create_other_clan_selection_box(self):
        """
        handles the creation of other_clan_selection_container
        """
        self.other_clan_selection_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((132, 902), (100, 100))),
            object_id="#other_clan_selection_container",
            starting_height=1,
            manager=MANAGER)
        self.other_clan_selection_elements["frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (1324, 388))),
            pygame.image.load(
                "resources/images/lead_den_clan_frame.png").convert_alpha(),
            object_id="#lead_den_clan_frame",
            container=self.other_clan_selection_container,
            starting_height=1,
            manager=MANAGER
        )
        for i, other_clan in enumerate(game.clan.all_clans):
            if other_clan.name == game.clan.name:
                continue
            print(f"index{i}")
            x_pos = 256
            self.other_clan_selection_elements[f"button{i}"] = UIImageButton(
                scale(pygame.Rect((17 + (x_pos * i), 20), (268, 348))),
                "",
                object_id="#other_clan_select_button",
                starting_height=2,
                container=self.other_clan_selection_container,
                manager=MANAGER
            )

            self.other_clan_selection_elements[f"clan_symbol{i}"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((100 + (x_pos * i), 70), (100, 100))),
                clan_symbol_sprite(other_clan),
                object_id=f"#clan_symbol{i}",
                starting_height=1,
                container=self.other_clan_selection_container,
                manager=MANAGER
            )

            self.other_clan_selection_elements[f"clan_name{i}"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((27 + (x_pos * i), 210), (244, -1))),
                text=f"{other_clan.name}Clan",
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                container=self.other_clan_selection_container,
                manager=MANAGER
            )
            self.other_clan_selection_elements[f"clan_temper{i}"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((27 + (x_pos * i), 260), (244, -1))),
                text=f"{other_clan.temperament.strip()}",
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                container=self.other_clan_selection_container,
                manager=MANAGER
            )
            self.other_clan_selection_elements[f"clan_rel{i}"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((27 + (x_pos * i), 290), (244, -1))),
                text=f"{get_other_clan_relation(other_clan.relations).strip()}",
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                container=self.other_clan_selection_container,
                manager=MANAGER
            )

    def create_focus_frame(self):
        """
        handles the creation of focus_frame_container
        """
        self.focus_frame_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((1019, 122), (100, 100))),
            object_id="#focus_frame_container",
            starting_height=2,
            manager=MANAGER)
        self.focus_frame_elements["frame"] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 63), (480, 728))),
                                                                         pygame.image.load(
                                                                             "resources/images/lead_den_focus_frame.png").convert_alpha(),
                                                                         object_id="#lead_den_focus_frame",
                                                                         container=self.focus_frame_container,
                                                                         starting_height=1,
                                                                         manager=MANAGER
                                                                         )
        self.focus_frame_elements["clans_tab"] = UIImageButton(scale(pygame.Rect((60, 4), (138, 68))),
                                                               "",
                                                               object_id="#clans_tab",
                                                               container=self.focus_frame_container,
                                                               starting_height=2,
                                                               manager=MANAGER)
        self.focus_frame_elements["clans_tab"].disable()
        self.focus_frame_elements["outsiders_tab"] = UIImageButton(scale(pygame.Rect((222, 4), (204, 68))),
                                                                   "",
                                                                   object_id="#outsiders_tab",
                                                                   container=self.focus_frame_container,
                                                                   starting_height=2,
                                                                   manager=MANAGER)
        self.focus_clan_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#focus_clan_container",
            container=self.focus_frame_container,
            manager=MANAGER
        )
        # TODO: create button images for Drive Off and Invite In
        self.focus_frame_elements["negative_interaction"] = UIImageButton(scale(pygame.Rect((118, 531), (242, 60))),
                                                                          "",
                                                                          object_id="#clan_befriend",
                                                                          container=self.focus_frame_container,
                                                                          starting_height=3,
                                                                          manager=MANAGER,
                                                                          visible=False)
        self.focus_frame_elements["positive_interaction"] = UIImageButton(scale(pygame.Rect((118, 611), (242, 60))),
                                                                          "",
                                                                          object_id="#clan_provoke",
                                                                          container=self.focus_frame_container,
                                                                          starting_height=3,
                                                                          manager=MANAGER,
                                                                          visible=False)

    def update_other_clan_focus(self):
        """
        handles changing the clan that is currently in focus
        """
        # killing so we can reset what's inside
        self.focus_clan_container.kill()
        self.focus_clan_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#focus_clan_container",
            container=self.focus_frame_container,
            manager=MANAGER
        )

        self.focus_clan_elements[f"clan_symbol"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((138, 134), (200, 200))),
            pygame.transform.scale(clan_symbol_sprite(self.focus_clan), (200, 200)),
            object_id="#clan_symbol",
            starting_height=1,
            container=self.focus_clan_container,
            manager=MANAGER
        )

        x_pos = 20
        y_pos = 367
        relation = get_other_clan_relation(self.focus_clan.relations)

        self.focus_clan_elements[f"clan_name"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((x_pos, y_pos), (439, -1))),
            text=f"{self.focus_clan.name}Clan",
            object_id="#text_box_30_horizcenter",
            container=self.focus_clan_container,
            manager=MANAGER
        )
        self.focus_clan_elements[f"clan_temper"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((x_pos, y_pos + 50), (439, -1))),
            text=f"{self.focus_clan.temperament.strip()}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_clan_container,
            manager=MANAGER
        )
        self.focus_clan_elements[f"clan_rel"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((x_pos, y_pos + 80), (439, -1))),
            text=f"{relation}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_clan_container,
            manager=MANAGER
        )

        interaction = OtherClan.interaction_dict[relation]
        self.focus_frame_elements["negative_interaction"].change_object_id(f"#clan_{interaction[0]}")
        self.focus_frame_elements["negative_interaction"].show()

        self.focus_frame_elements["positive_interaction"].change_object_id(f"#clan_{interaction[1]}")
        self.focus_frame_elements["positive_interaction"].show()

    def update_interaction_choice(self, object_id):
        """
        handles changing chosen clan interaction. updates clan_settings and notice text.
        :param object_id: the object ID of the interaction button
        """

        interaction = object_id.replace("#clan_", "")
        other_clan = self.focus_clan.name

        game.clan.clan_settings["clan_interaction"] = [other_clan, interaction]

        self.screen_elements["notice_text"].set_text(f" {self.leader_name} has decided to {interaction} {other_clan}Clan.")

    def open_clans_tab(self):
        """
        handles opening clans tab and closing outsiders tab
        """
        self.outsider_selection_container.hide()

        self.other_clan_selection_container.show()

    def open_outsiders_tab(self):
        """
        handles opening outsiders tab and closing clans tab
        """
        self.other_clan_selection_container.hide()

        self.outsider_selection_container.show()

    def display_outsider_cats(self):
        """
        handles finding and displaying outsider cats
        """

    def exit_screen(self):
        """
        Deletes all elements when this screen is closed
        """
        self.back_button.kill()
        self.help_button.kill()

        for ele in self.screen_elements:
            self.screen_elements[ele].kill()
            
        # killing containers kills all inner elements as well
        self.focus_frame_container.kill()
        self.other_clan_selection_container.kill()
        self.outsider_selection_container.kill()
