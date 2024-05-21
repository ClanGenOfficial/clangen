import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.cat.sprites import sprites
from scripts.clan import OtherClan
from scripts.game_structure.windows import SelectFocusClans
from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton, UISpriteButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.utility import get_med_cats, scale, get_text_box_theme, get_other_clan_relation, get_other_clan, \
    clan_symbol_sprite, shorten_text_to_fit


class LeaderDenScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.current_page = 1
        self.help_button = None
        self.back_button = None

        self.focus_cat = None
        self.focus_clan = None
        self.leader_name = None
        self.clan_temper = None

        self.screen_elements = {}

        self.focus_frame_container = None
        self.focus_frame_elements = {}
        self.focus_clan_container = None
        self.focus_clan_elements = {}
        self.focus_outsider_container = None
        self.focus_outsider_button_container = None
        self.focus_outsider_elements = {}

        self.other_clan_selection_container = None
        self.other_clan_selection_elements = {}

        self.outsider_selection_container = None
        self.outsider_selection_elements = {}

        self.outsider_cat_list_container = None
        self.outsider_cat_buttons = {}

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
            elif event.ui_element in self.other_clan_selection_elements.values():
                for i in range(0, 5):
                    if f"button{i}" not in self.other_clan_selection_elements:
                        continue
                    if event.ui_element == self.other_clan_selection_elements[f"button{i}"]:
                        print("button press")
                        self.focus_clan = game.clan.all_clans[i]
                        self.update_other_clan_focus()
            elif event.ui_element == self.focus_frame_elements["negative_interaction"]:
                object_id = self.focus_frame_elements["negative_interaction"].get_object_ids()
                self.update_interaction_choice(object_id[2])
            elif event.ui_element == self.focus_frame_elements["positive_interaction"]:
                object_id = self.focus_frame_elements["positive_interaction"].get_object_ids()
                self.update_interaction_choice(object_id[2])
            elif event.ui_element == self.focus_frame_elements["clans_tab"]:
                self.open_clans_tab()
            elif event.ui_element == self.focus_frame_elements["outsiders_tab"]:
                self.open_outsiders_tab()
            elif event.ui_element in self.outsider_cat_buttons.values():
                self.focus_cat = event.ui_element.return_cat_object()
                self.update_outsider_focus()

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

        # LEADER DEN BG AND LEADER SPRITE
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

        # FOCUS FRAME - container and inner elements
        self.create_focus_frame()

        # OTHER CLAN SELECTION BOX - container and inner elements
        self.create_other_clan_selection_box()

        # OUTSIDER SELECTION - container and inner elements
        # this starts off invisible
        self.create_outsider_selection_box()

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

    def create_focus_frame(self):
        """
        handles the creation of focus_frame_container
        """
        self.focus_frame_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((1019, 122), (100, 100))),
            object_id="#focus_frame_container",
            starting_height=3,
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

        # TODO: create button images for Drive Off, Hunt Down, Search For, and Invite In

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

    def create_outsider_selection_box(self):
        self.outsider_selection_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((118, 910), (0, 0))),
            object_id="#outsider_selection_container",
            starting_height=1,
            manager=MANAGER,
            visible=False)
        self.outsider_selection_elements["page_left"] = UIImageButton(
            scale(pygame.Rect((0, 140), (68, 68))),
            "",
            object_id="#arrow_left_button",
            container=self.outsider_selection_container,
            starting_height=1,
            manager=MANAGER
        )
        self.outsider_selection_elements["page_right"] = UIImageButton(
            scale(pygame.Rect((1292, 140), (68, 68))),
            "",
            object_id="#arrow_right_button",
            container=self.outsider_selection_container,
            starting_height=1,
            manager=MANAGER)
        self.outsider_selection_elements["frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((56, 0), (1248, 348))),
            pygame.image.load(
                "resources/images/lead_den_outsider_frame.png").convert_alpha(),
            object_id="#lead_den_outsider_frame",
            container=self.outsider_selection_container,
            starting_height=2,
            manager=MANAGER)

        self.focus_outsider_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#focus_outsider_container",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER
        )

    def update_other_clan_focus(self):
        """
        handles changing the clan that is currently in focus
        """
        # killing so we can reset what's inside
        if self.focus_clan_container:
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

        self.focus_frame_elements["negative_interaction"] = UIImageButton(
            scale(pygame.Rect((118, 531), (242, 60))),
            "",
            object_id="#clan_befriend",
            container=self.focus_clan_container,
            starting_height=3,
            manager=MANAGER,
            visible=False)
        self.focus_frame_elements["positive_interaction"] = UIImageButton(
            scale(pygame.Rect((118, 611), (242, 60))),
            "",
            object_id="#clan_provoke",
            container=self.focus_clan_container,
            starting_height=3,
            manager=MANAGER,
            visible=False)

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

        self.screen_elements["notice_text"].set_text(
            f" {self.leader_name} has decided to {interaction} {other_clan}Clan.")

    def open_clans_tab(self):
        """
        handles opening clans tab and closing outsiders tab
        """
        self.outsider_selection_container.hide()
        self.focus_outsider_container.hide()

        self.focus_clan_container.show()
        self.other_clan_selection_container.show()

        self.focus_frame_elements["clans_tab"].disable()
        self.focus_frame_elements["outsiders_tab"].enable()

    def open_outsiders_tab(self):
        """
        handles opening outsiders tab and closing clans tab
        """
        self.other_clan_selection_container.hide()
        self.focus_clan_container.hide()

        self.outsider_selection_container.show()
        self.focus_outsider_container.show()
        self.update_outsider_cats()

        self.focus_frame_elements["outsiders_tab"].disable()
        self.focus_frame_elements["clans_tab"].enable()

    def update_outsider_cats(self):
        """
        handles finding and displaying outsider cats
        """
        # get cats for list
        outsiders = [i for i in Cat.all_cats.values() if i.outside and not i.dead]

        # separate them into chunks for the pages
        outsider_chunks = self.chunks(outsiders, 18)

        # clamp current page to a valid page number
        self.current_page = max(1, min(self.current_page, len(outsider_chunks)))

        # handles which arrow buttons are clickable
        if len(outsider_chunks) <= 1:
            self.outsider_selection_elements["page_left"].disable()
            self.outsider_selection_elements["page_right"].disable()
        elif self.current_page >= len(outsider_chunks):
            self.outsider_selection_elements["page_left"].enable()
            self.outsider_selection_elements["page_right"].disable()
        elif self.current_page == 1 and len(outsider_chunks) > 1:
            self.outsider_selection_elements["page_left"].disable()
            self.outsider_selection_elements["page_right"].enable()
        else:
            self.outsider_selection_elements["page_left"].enable()
            self.outsider_selection_elements["page_right"].enable()

        # CREATE DISPLAY
        display_cats = []
        if outsider_chunks:
            display_cats = outsider_chunks[self.current_page - 1]

        # container for all the cat sprites and names
        self.outsider_cat_list_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((112, 44), (0, 0))),
            container=self.outsider_selection_container,
            starting_height=3,
            object_id="#outsider_cat_list",
            manager=MANAGER
        )

        # Kill all currently displayed cats
        for ele in self.outsider_cat_buttons:
            self.outsider_cat_buttons[ele].kill()
        self.outsider_cat_buttons = {}

        pos_x = 0
        pos_y = 0
        i = 0
        for cat in display_cats:
            self.outsider_cat_buttons[f"sprite{str(i)}"] = UISpriteButton(
                scale(pygame.Rect((10 + pos_x, 0 + pos_y), (100, 100))),
                cat.sprite,
                cat_object=cat,
                container=self.outsider_cat_list_container,
                object_id=f"#sprite{str(i)}",
                tool_tip_text=str(cat.name),
                starting_height=2,
                manager=MANAGER
            )

            # changing pos
            pos_x += 120
            if pos_x >= 1140:  # checks if row is full
                pos_x = 0
                pos_y += 120

            i += 1

    def update_outsider_focus(self):

        # killing so we can reset
        if self.focus_outsider_container:
            self.focus_outsider_container.kill()

        self.focus_outsider_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#focus_outsider_container",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER
        )

        self.focus_outsider_elements["cat_sprite"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((90, 45), (300, 300))),
            pygame.transform.scale(self.focus_cat.sprite, (300, 300)),
            object_id="#focus_cat_sprite",
            container=self.focus_outsider_container,
            starting_height=1,
            manager=MANAGER
        )

        self.focus_outsider_elements["cat_name"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((18, 350), (440, -1))),
            text=shorten_text_to_fit(str(self.focus_cat.name), 440, 30),
            object_id="#text_box_30_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER
        )
        self.focus_outsider_elements["cat_status"] = pygame_gui.elements.UILabel(
            relative_rect=scale(pygame.Rect((20, 390), (436, -1))),
            text=f"{self.focus_cat.status}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER
        )
        self.focus_outsider_elements["cat_trait"] = pygame_gui.elements.UILabel(
            relative_rect=scale(pygame.Rect((20, 420), (436, -1))),
            text=f"{self.focus_cat.personality.trait}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER
        )
        self.focus_outsider_elements["cat_skills"] = pygame_gui.elements.UILabel(
            relative_rect=scale(pygame.Rect((20, 450), (436, -1))),
            text=f"{self.focus_cat.skills.skill_string(short=True)}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER
        )

        self.focus_outsider_button_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((118, 505), (0, 0))),
            object_id="#focus_outsider_button_container",
            container=self.focus_outsider_container,
            starting_height=1,
            manager=MANAGER
        )
        y_pos = 0
        self.focus_outsider_elements["hunt_down"] = UIImageButton(
            scale(pygame.Rect((0, y_pos), (242, 60))),
            "",
            object_id="#outsider_hunt",
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
        )
        y_pos += 70
        self.focus_outsider_elements["drive_off"] = UIImageButton(
            scale(pygame.Rect((0, y_pos), (242, 60))),
            "",
            object_id="#outsider_drive",
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
        )
        y_pos += 73
        self.focus_outsider_elements["invite_in"] = UIImageButton(
            scale(pygame.Rect((0, y_pos), (242, 60))),
            "",
            object_id="#outsider_invite",
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
            visible=False
        )
        if self.focus_cat.outside and not self.focus_cat.exiled and self.focus_cat.status not in ['kittypet', 'loner', 'rogue', 'former Clancat']:
            self.focus_outsider_elements["invite_in"].change_object_id("#outsider_search")

        self.focus_outsider_elements["invite_in"].show()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
