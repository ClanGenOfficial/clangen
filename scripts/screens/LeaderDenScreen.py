import random

import pygame
import pygame_gui

from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.history import History
from scripts.clan import OtherClan
from scripts.events_module.generate_events import generate_events
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.image_button import UIImageButton, UISpriteButton
from scripts.game_structure.windows import NotificationWindow
from scripts.screens.Screens import Screens
from scripts.utility import scale, get_text_box_theme, get_other_clan_relation, get_other_clan, \
    clan_symbol_sprite, shorten_text_to_fit, event_text_adjust, history_text_adjust, get_med_cats


class LeaderDenScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.helper_cat = None
        self.no_gathering = False
        self.helper_name = None
        self.current_page = 1
        self.help_button = None
        self.back_button = None

        self.focus_cat = None
        self.focus_clan = None
        self.deputy_name = None
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
        self.focus_button = {}

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
            elif event.ui_element in self.focus_button.values():
                result = self.handle_outsider_interaction(event.ui_element.get_object_ids()[3])
                self.update_outsider_cats()
                NotificationWindow(result)

    def screen_switches(self):
        """
        Handle creating new elements when switching to this screen
        """
        # no menu header allowed
        self.hide_menu_buttons()

        # BACK AND HELP
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))),
                                         "",
                                         object_id="#back_button",
                                         manager=MANAGER)
        self.help_button = UIImageButton(scale(pygame.Rect(
            (1450, 50), (68, 68))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="This screen allows you to check on the other cats who live nearby, both Outsiders and "
                          "other Clan cats.  You can control how the leader of your Clan will treat other leaders at "
                          "Gatherings, but keep in mind that you can only determine one interaction each moon!  "
                          "Likewise, you can consider whether to drive out or invite in Outsider cats.  If you drive "
                          "out a cat, they will no longer appear in the Cats Outside the Clans list.  If you invite "
                          "in a cat, they might join your Clan!",
        )

        # LEADER DEN BG AND LEADER SPRITE
        try:
            self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((0, 0), (1400, 900))),
                pygame.image.load(
                    f"resources/images/lead_den_bg/{game.clan.biome.lower()}/{game.clan.camp_bg.lower()}.png").convert_alpha(),
                object_id="#lead_den_bg",
                starting_height=1,
                manager=MANAGER)
        except FileNotFoundError:
            self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((0, 0), (1400, 900))),
                pygame.image.load(
                    f"resources/images/lead_den_bg/{game.clan.biome.lower()}/camp1.png").convert_alpha(),
                object_id="#lead_den_bg",
                starting_height=1,
                manager=MANAGER)

        self.helper_cat = None
        if game.clan.leader.not_working:
            self.helper_cat = game.clan.deputy  # if lead is sick, dep helps
            if game.clan.deputy.not_working:  # if dep is sick, med cat helps
                meds = get_med_cats(Cat)
                if meds:
                    self.helper_cat = meds[0]
                else:  # if no meds, mediator helps
                    mediators = [i for i in Cat.all_cats.values() if
                                 not i.dead and not i.exiled and not i.outside and not i.not_working() and i.status in [
                                     "mediator", "mediator apprentice"]]
                    if mediators:
                        self.helper_cat = mediators[0]
                    else:
                        self.helper_cat = None
            if not self.helper_cat:  # if no meds or mediators available, literally anyone please anyone help
                adults = [i for i in Cat.all_cats.values() if
                          not i.dead and not i.exiled and not i.outside and i.status not in ["newborn", "kitten",
                                                                                             "apprentice"]]
                if adults:
                    self.helper_cat = random.choice(adults)

            if self.helper_cat:
                self.screen_elements["helper_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((520, 410), (300, 300))),
                    pygame.transform.scale(self.helper_cat.sprite, (300, 300)),
                    object_id="#helper_cat_image",
                    starting_height=2,
                    manager=MANAGER)

        self.screen_elements["lead_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((460, 460), (300, 300))),
            pygame.transform.scale(game.clan.leader.sprite, (300, 300)),
            object_id="#lead_cat_image",
            starting_height=3,
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

        if game.clan.leader.not_working and self.helper_cat:
            self.helper_name = self.helper_cat.name
            self.screen_elements["notice_text"] = pygame_gui.elements.UITextBox(
                relative_rect=scale(pygame.Rect((135, 750), (890, -1))),
                html_text=f" {self.leader_name} and {self.helper_name} are discussing how to handle the next Gathering. ",
                object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
                manager=MANAGER
            )
        elif game.clan.leader.not_working:
            self.no_gathering = True
            self.screen_elements["notice_text"] = pygame_gui.elements.UITextBox(
                relative_rect=scale(pygame.Rect((135, 750), (890, -1))),
                html_text=f" There is no one to attend the next Gathering. {self.leader_name} must hope to recover in time for the next one. ",
                object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
                manager=MANAGER
            )
        else:
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
            scale(pygame.Rect((1019, 122), (0, 0))),
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

        if self.no_gathering:
            self.focus_frame_elements["negative_interaction"].disable()
            self.focus_frame_elements["positive_interaction"].disable()

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

        self.handle_other_clan_interaction(interaction)

    def handle_other_clan_interaction(self, interaction_type: str):

        gathering_cat = game.clan.leader if not self.helper_cat else self.helper_cat

        success = False

        player_temper_int = self._find_temper_int(self.clan_temper)
        other_temper_int = self._find_temper_int(self.focus_clan.temperament)
        fail_chance = self._compare_temper(player_temper_int, other_temper_int)

        if gathering_cat != game.clan.leader:
            print("gathering cat isn't clan leader: fail_chance * 1.4")
            fail_chance = fail_chance * 1.4
        print(f"Clan Interaction Failure Chance: {fail_chance}")

        if random.random() >= fail_chance:
            success = True

        events = generate_events.possible_lead_den_events(cat=gathering_cat,
                                                          other_clan_temper=self.focus_clan.temperament,
                                                          player_clan_temper=self.clan_temper,
                                                          event_type="other_clan",
                                                          interaction_type=interaction_type,
                                                          success=success
                                                          )
        chosen_event = random.choice(events)
        event_text = chosen_event["event_text"]
        if success:
            event_text += f" ({interaction_type.capitalize()} o_c success! "
        else:
            event_text += f" ({interaction_type.capitalize()} o_c failure! "

        rel_change = chosen_event["rel_change"]
        if rel_change > 0:
            event_text += f"Clan relations improved.)"
        elif rel_change == 0:
            event_text += f"Clan relations unchanged.)"
        else:
            event_text += f"Clan relations worsened.)"

        self.focus_clan.relations += rel_change
        event_text = event_text_adjust(Cat, event_text, cat=gathering_cat,
                                       other_clan_name=f"{self.focus_clan.name}Clan", clan=game.clan)
        game.clan.clan_settings["lead_den_event"] = [event_text, gathering_cat.ID]
        print(game.clan.clan_settings["lead_den_event"])

    def _compare_temper(self, player_temper_int, other_temper_int) -> float:
        """
        compares two temper ints and finds the chance of failure between them, adds additional modifiers for distance
        between two tempers on the temperament chart.  returns percent chance of failure
        """
        # base equation for fail chance (temper_int - temper_int) / 10
        fail_chance = (abs(int(player_temper_int - other_temper_int))) / 10
        print(f"BASE FAIL CHANCE: {fail_chance} ({player_temper_int} - {other_temper_int})")

        temper_dict = game.clan.temperament_dict
        clan_index = 0
        clan_social = None
        other_index = 0
        other_social = None
        for row in temper_dict:
            if self.clan_temper in temper_dict[row]:
                clan_index = temper_dict[row].index(self.clan_temper)
                clan_social = row
            if self.focus_clan.temperament in temper_dict[row]:
                other_index = temper_dict[row].index(self.focus_clan.temperament)
                other_social = row

        # checks social distance between tempers and adds modifiers appropriately
        if clan_social != other_social:
            fail_chance += 0.05
            print("not in same social row +5%")
            if clan_social == "low social" and other_social == "high_social":
                fail_chance += 0.1
                print("opposite extremes of social temper +10%")
            elif other_social == "low social" and clan_social == "high_social":
                fail_chance += 0.1
                print("opposite extremes of social temper +10%")

        # checks aggression distance between tempers and adds modifiers appropriately
        if clan_index != other_index:
            fail_chance += 0.05
            print("not in same aggress column +5%")
            if clan_index == 0 and other_index == 2:
                fail_chance += 0.1
                print("opposite extremes of aggress temper +10%")
            elif other_index == 0 and clan_index == 2:
                fail_chance += 0.1
                print("opposite extremes of aggress temper +10%")

        return fail_chance

    @staticmethod
    def _find_temper_int(temper: str) -> int:
        """
        returns int value (social rank + aggression rank) of given temperament
        """
        temper_dict = game.clan.temperament_dict
        temper_int = 0

        if temper in temper_dict["low_social"]:
            temper_int += 1
            social_list = temper_dict["low_social"]
        elif temper in temper_dict["mid_social"]:
            temper_int += 3
            social_list = temper_dict["mid_social"]
        else:
            temper_int += 5
            social_list = temper_dict["high_social"]

        temper_int += int(social_list.index(temper)) + 1

        return temper_int

    def update_outsider_focus(self):

        # clearing so we can reset
        if self.focus_outsider_container:
            for ele in self.focus_outsider_elements:
                self.focus_outsider_elements[ele].kill()
            self.focus_outsider_elements = {}
        else:
            self.focus_outsider_container = pygame_gui.elements.UIAutoResizingContainer(
                scale(pygame.Rect((0, 0), (0, 0))),
                object_id="#focus_outsider_container",
                container=self.focus_frame_container,
                starting_height=1,
                manager=MANAGER
            )

        self.focus_outsider_elements["cat_sprite"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((90, 50), (300, 300))),
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
            text=f"Skills: {self.focus_cat.skills.skill_string(short=True)}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER
        )

        if self.focus_outsider_button_container:
            self.focus_outsider_button_container.clear()
        else:
            self.focus_outsider_button_container = pygame_gui.elements.UIAutoResizingContainer(
                scale(pygame.Rect((118, 505), (0, 0))),
                object_id="#focus_outsider_button_container",
                container=self.focus_outsider_container,
                starting_height=1,
                manager=MANAGER
            )

        # for some reason this container gets divorced from its parent container sometimes
        # so this is here to ensure it's attached to its container
        self.focus_outsider_container.add_element(self.focus_outsider_button_container)

        y_pos = 0
        self.focus_button["hunt_down"] = UIImageButton(
            scale(pygame.Rect((0, y_pos), (242, 60))),
            "",
            object_id="#outsider_hunt",
            tool_tip_text="This cat will be killed if found.",
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
        )
        y_pos += 70
        self.focus_button["drive_off"] = UIImageButton(
            scale(pygame.Rect((0, y_pos), (242, 60))),
            "",
            object_id="#outsider_drive",
            tool_tip_text="This cat will be driven out of the area if found (they will no longer be accessible in "
                          "game.)",
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
        )
        y_pos += 70
        self.focus_button["invite_in"] = UIImageButton(
            scale(pygame.Rect((0, y_pos), (242, 60))),
            "",
            object_id="#outsider_invite",
            tool_tip_text="This cat will join the Clan if found.",
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
            visible=False
        )

        if self.focus_cat.outside and not self.focus_cat.exiled and self.focus_cat.status not in ['kittypet', 'loner',
                                                                                                  'rogue',
                                                                                                  'former Clancat',
                                                                                                  'driven off']:
            self.focus_button["invite_in"].change_object_id("#outsider_search")
        else:
            self.focus_button["invite_in"].change_object_id("#outsider_invite")

        self.focus_button["invite_in"].show()

        if "outsider_interaction" in game.clan.clan_settings:
            if game.clan.clan_settings["outsider_interaction"]:
                print("outsider buttons disabled")
                self.focus_outsider_button_container.disable()

    def update_outsider_cats(self):
        """
        handles finding and displaying outsider cats
        """
        # get cats for list
        outsiders = [i for i in Cat.all_cats.values() if i.outside and not i.dead and not i.driven_out]

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

    def handle_outsider_interaction(self, object_id):
        """
        handles determining the outcome of an outsider interaction, returns result text
        :param object_id: the object id of the interaction button pressed
        """
        result_text = None
        thought = None

        game.clan.clan_settings["outsider_interaction"] = True

        # percentage of success
        success = False
        success_chance = int(game.clan.reputation) / 100
        if game.clan.leader.not_working:
            success_chance = success_chance / 1.2
        print(f"CHANCE: {success_chance}")
        if random.random() < success_chance:
            success = True
            print("INTERACTION SUCCESS")
        else:
            print("INTERACTION FAIL")

        if not success:
            thought = "Heard rumors that c_n was searching for them"
            result_text = "m_c could not be found by the Clan."
        else:
            if object_id == "#outsider_hunt":
                History.add_death(self.focus_cat, death_text=history_text_adjust("m_c was killed by c_n.",
                                                                                 other_clan_name=None,
                                                                                 clan=game.clan))
                self.focus_cat.die()
                result_text = "m_c was found and killed by a search party. c_n's reputation among Outsiders has " \
                              "greatly lowered. "
                game.clan.reputation += -30

            elif object_id == "#outsider_drive":
                self.focus_cat.status = "exiled"
                self.focus_cat.exiled = True
                self.focus_cat.driven_out = True
                result_text = "m_c was found and driven out of the area. c_n's reputation among Outsiders has lowered."
                game.clan.reputation += -10

            elif object_id == "#outsider_invite":
                result_text = "m_c was found and invited into the Clan. c_n's reputation among Outsiders has improved."
                game.clan.reputation += 20

                if self.focus_cat.exiled:
                    thought = "Is surprised c_n has welcomed {PRONOUN/m_c/object} back"
                else:
                    thought = "Is curious about the Clan that sought {PRONOUN/m_c/object} out"

                # adds to clan and also checks for accompanying kits
                additional_cats = self.focus_cat.add_to_clan()
                if additional_cats:
                    result_text += "m_c brings along {PRONOUN/m_c/poss} "
                    if len(additional_cats) > 1:
                        result_text += str(len(additional_cats)) + " children."
                    else:
                        result_text += "child"

                additional_cats.append(self.focus_cat.ID)
                # clan_setting will check ceremonies on timeskip
                game.clan.clan_settings["found_lost_cat_ID"] = additional_cats

            elif object_id == "#outsider_search":
                self.focus_cat.add_to_clan()
                thought = "Is ecstatic that c_n found {PRONOUN/m_c/object}!"

                result_text = "m_c was found and brought back to the Clan. c_n's reputation among Outsiders has " \
                              "improved. "
                game.clan.reputation += 20

                # adds to clan and also checks for accompanying kits
                additional_cats = self.focus_cat.add_to_clan()
                if additional_cats:
                    result_text += "m_c brings along {PRONOUN/m_c/poss} "
                    if len(additional_cats) > 1:
                        result_text += str(len(additional_cats)) + " children."
                    else:
                        result_text += "child"

                additional_cats.append(self.focus_cat.ID)
                # clan_setting will check ceremonies on timeskip
                game.clan.clan_settings["found_lost_cat_ID"] = additional_cats

        # set status
        if not self.focus_cat.dead and self.focus_cat.status.lower() in ["kittypet", "loner", "rogue", "former clancat",
                                                                         "exiled"]:
            if self.focus_cat.backstory in BACKSTORIES["backstory_categories"]["healer_backstories"]:
                self.focus_cat.status = "medicine cat"
            elif self.focus_cat.age in ["newborn", "kitten"]:
                self.focus_cat.status = self.focus_cat.age
            elif self.focus_cat.age == "senior":
                self.focus_cat.status = "elder"
            elif self.focus_cat.age == "adolescent":
                self.focus_cat.status = "apprentice"
                self.focus_cat.update_mentor()
            else:
                self.focus_cat.status = "warrior"

        # only one interaction allowed per moon
        self.focus_outsider_button_container.disable()

        # adjust text
        result_text = event_text_adjust(Cat, result_text, self.focus_cat, clan=game.clan)

        # set thought
        if thought:
            self.focus_cat.thought = event_text_adjust(Cat, thought, self.focus_cat, clan=game.clan)

        # check reputation value
        print(f"New Rep: {int(game.clan.reputation)}")
        if game.clan.reputation < 0:
            game.clan.reputation = 0
        elif game.clan.reputation > 100:
            game.clan.reputation = 100

        return result_text

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
