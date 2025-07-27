import random

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatGroup
from scripts.clan import OtherClan
from scripts.clan_package.settings.clan_settings import (
    set_clan_setting,
    get_clan_setting,
)
from scripts.game_structure import constants
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.screens.Screens import Screens
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import (
    ui_scale,
    get_text_box_theme,
    get_other_clan_relation,
    get_other_clan,
    clan_symbol_sprite,
    shorten_text_to_fit,
    find_alive_cats_with_rank,
    get_living_clan_cat_count,
    ui_scale_dimensions,
)


class LeaderDenScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)

        self.current_page = 1
        self.help_button = None
        self.back_button = None

        self.focus_clan = None
        self.focus_cat = None
        self.helper_cat = None
        self.helper_name = None
        self.deputy_name = None
        self.leader_name = None
        self.clan_temper = None
        self.clan_rep = None
        self.no_leader = False

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
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.outsider_selection_elements["page_right"]:
                self.current_page += 1
                self.update_outsider_cats()
            elif event.ui_element == self.outsider_selection_elements["page_left"]:
                self.current_page -= 1
                self.update_outsider_cats()
            elif event.ui_element in self.other_clan_selection_elements.values():
                for i in range(0, 5):
                    if f"button{i}" not in self.other_clan_selection_elements:
                        continue
                    if (
                        event.ui_element
                        == self.other_clan_selection_elements[f"button{i}"]
                    ):
                        self.focus_clan = game.clan.all_clans[i]
                        self.update_other_clan_focus()
            elif event.ui_element == self.focus_frame_elements["negative_interaction"]:
                text = self.focus_frame_elements["negative_interaction"].text.replace(
                    "screens.leader_den.", ""
                )
                self.update_clan_interaction_choice(text)
            elif event.ui_element == self.focus_frame_elements["positive_interaction"]:
                text = self.focus_frame_elements["positive_interaction"].text.replace(
                    "screens.leader_den.", ""
                )
                self.update_clan_interaction_choice(text)
            elif event.ui_element == self.focus_frame_elements["clans_tab"]:
                self.open_clans_tab()
            elif event.ui_element == self.focus_frame_elements["outsiders_tab"]:
                self.open_outsiders_tab()
            elif event.ui_element in self.outsider_cat_buttons.values():
                self.focus_cat = event.ui_element.return_cat_object()
                self.update_outsider_focus()
            elif event.ui_element in self.focus_button.values():
                self.update_outsider_interaction_choice(
                    event.ui_element.text.replace("screens.leader_den.", "")
                )
                self.update_outsider_cats()

    def screen_switches(self):
        """
        Handle creating new elements when switching to this screen
        """
        super().screen_switches()
        # just making sure these are set up ahead of time
        if get_clan_setting("lead_den_clan_interaction") is None:
            set_clan_setting("lead_den_interaction", False)
        if get_clan_setting("lead_den_clan_event") is None:
            set_clan_setting("lead_den_clan_event", {})
        if get_clan_setting("lead_den_clan_event") is None:
            set_clan_setting("lead_den_outsider_event", {})

        # no menu header allowed
        self.hide_menu_buttons()

        # BACK AND HELP
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((725, 25), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="screens.leader_den.help_tooltip",
        )
        # This is here incase the leader comes back
        self.no_leader = False

        if not game.clan.leader or not game.clan.leader.status.alive_in_player_clan:
            self.no_leader = True

        # LEADER DEN BG AND LEADER SPRITE
        try:
            self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (700, 450))),
                pygame.image.load(
                    f"resources/images/lead_den_bg/{game.clan.biome.lower()}/{game.clan.camp_bg.lower()}.png"
                ).convert_alpha(),
                object_id="#lead_den_bg",
                starting_height=1,
                manager=MANAGER,
            )
        except FileNotFoundError:
            self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (700, 450))),
                pygame.image.load(
                    f"resources/images/lead_den_bg/{game.clan.biome.lower()}/camp1.png"
                ).convert_alpha(),
                object_id="#lead_den_bg",
                starting_height=1,
                manager=MANAGER,
            )

        if not self.no_leader:
            self.screen_elements["lead_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((230, 230), (150, 150))),
                pygame.transform.scale(
                    game.clan.leader.sprite, ui_scale_dimensions((150, 150))
                ),
                object_id="#lead_cat_image",
                starting_height=3,
                manager=MANAGER,
            )

        self.helper_cat = None
        if self.no_leader or game.clan.leader.not_working():
            if game.clan.deputy:
                if not game.clan.deputy.not_working() and not game.clan.deputy.dead:
                    self.helper_cat = game.clan.deputy  # if lead is sick, dep helps
            if not self.helper_cat:  # if dep is sick, med cat helps
                meds = find_alive_cats_with_rank(
                    Cat,
                    ranks=[CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE],
                    working=True,
                    sort=True,
                )
                if meds:
                    self.helper_cat = meds[0]
                else:  # if no meds, mediator helps
                    mediators = [
                        i
                        for i in Cat.all_cats.values()
                        if not i.dead
                        and not i.not_working()
                        and i.status.rank.is_any_mediator_rank()
                    ]
                    if mediators:
                        self.helper_cat = mediators[0]
                    else:
                        self.helper_cat = None
            if (
                not self.helper_cat
            ):  # if no meds or mediators available, literally anyone please anyone help
                adults = [
                    i
                    for i in Cat.all_cats.values()
                    if i.status.alive_in_player_clan
                    and i.status.rank
                    not in [CatRank.NEWBORN, CatRank.KITTEN, CatRank.LEADER]
                ]
                if adults:
                    self.helper_cat = random.choice(adults)

            if self.helper_cat:
                self.screen_elements["helper_image"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((260, 205), (150, 150))),
                    pygame.transform.scale(
                        self.helper_cat.sprite, ui_scale_dimensions((150, 150))
                    ),
                    object_id="#helper_cat_image",
                    starting_height=2,
                    manager=MANAGER,
                )

        # FOCUS FRAME - container and inner elements
        self.create_focus_frame()

        # OTHER CLAN SELECTION BOX - container and inner elements
        self.create_other_clan_selection_box()

        # OUTSIDER SELECTION - container and inner elements
        # this starts off invisible
        self.create_outsider_selection_box()

        # NOTICE TEXT - leader intention and other clan impressions
        self.leader_name = None if self.no_leader else game.clan.leader.name

        self.clan_temper = game.clan.temperament

        self.screen_elements["clan_notice_text"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((68, 375), (445, -1))),
            html_text="screens.leader_den.clan_notice_text",
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            visible=False,
            manager=MANAGER,
            text_kwargs={
                "m_c": game.clan.leader if not self.no_leader else None,
                "count": 1,
            },
        )
        self.screen_elements["outsider_notice_text"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((68, 375), (445, -1))),
            html_text=f"screens.leader_den.outsider_notice_text",
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            visible=False,
            manager=MANAGER,
            text_kwargs={
                "count": 1,
                "m_c": game.clan.leader if not self.no_leader else None,
            },
        )

        # if no one is alive, give a special notice
        if not get_living_clan_cat_count(Cat):
            self.no_leader = True
            self.screen_elements["clan_notice_text"].set_text(
                "screens.leader_den.no_cats_clan"
            )
            self.screen_elements["outsider_notice_text"].set_text(
                "screens.leader_den.no_cats_outsider"
            )
        # if leader is dead and no one new is leading, give special notice
        elif self.no_leader or not game.clan.leader.status.alive_in_player_clan:
            self.no_leader = True
            self.screen_elements["clan_notice_text"].set_text(
                "screens.leader_den.no_leader_clan"
            )
            self.screen_elements["outsider_notice_text"].set_text(
                "screens.leader_den.no_leader_outsider"
            )
        # if leader is sick but helper is available, give special notice
        elif game.clan.leader.not_working() and self.helper_cat:
            self.helper_name = self.helper_cat.name
            self.screen_elements["clan_notice_text"].set_text(
                "screens.leader_den.clan_notice_text",
                text_kwargs={
                    "m_c": game.clan.leader,
                    "r_c": self.helper_cat,
                    "count": 2,
                },
            )
            self.screen_elements["outsider_notice_text"].set_text(
                "screens.leader_den.outsider_notice_text",
                text_kwargs={
                    "m_c": game.clan.leader,
                    "r_c": self.helper_cat,
                    "count": 2,
                },
            )
        # if leader is sick but no helper is available, give special notice
        elif game.clan.leader.not_working():
            self.no_leader = True
            self.screen_elements["clan_notice_text"].set_text(
                "screens.leader_den.leader_sick_clan",
                text_kwargs={"m_c": game.clan.leader},
            )
            self.screen_elements["outsider_notice_text"].set_text(
                "screens.leader_den.leader_sick_outsider",
                text_kwargs={"m_c": game.clan.leader},
            )

        self.screen_elements["clan_notice_text"].show()

        self.screen_elements["temper_text"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((68, 410), (445, -1))),
            html_text="screens.leader_den.temper_text",
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            text_kwargs={
                "temper": i18n.t(f"screens.leader_den.{self.clan_temper}"),
                "clan": game.clan.name,
            },
        )

        # INITIAL DISPLAY - display currently chosen interaction OR first clan in list
        if get_clan_setting("lead_den_clan_event"):
            current_setting = get_clan_setting("lead_den_clan_event")
            self.focus_clan = get_other_clan(current_setting["other_clan"])
            self.update_other_clan_focus()
            self.update_clan_interaction_choice(current_setting["interaction_type"])
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
        self.focus_frame_container = UIContainer(
            ui_scale(pygame.Rect((509, 61), (240, 398))),
            object_id="#focus_frame_container",
            starting_height=3,
            manager=MANAGER,
        )
        self.focus_frame_elements["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 31), (240, 364))),
            pygame.image.load(
                "resources/images/lead_den_focus_frame.png"
            ).convert_alpha(),
            object_id="#lead_den_focus_frame",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER,
        )
        self.focus_frame_elements["clans_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 2), (69, 34))),
            "screens.leader_den.clans",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (69, 34)),
            object_id="@buttonstyles_horizontal_tab",
            container=self.focus_frame_container,
            starting_height=2,
            manager=MANAGER,
        )
        self.focus_frame_elements["clans_tab"].disable()

        self.focus_frame_elements["outsiders_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((111, 2), (102, 34))),
            "screens.leader_den.outsiders",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (102, 34)),
            object_id="@buttonstyles_horizontal_tab",
            container=self.focus_frame_container,
            starting_height=2,
            manager=MANAGER,
            tab_movement={
                "hovered": False,
            },
        )

        # TODO: create button images for Drive Off, Hunt Down, Search For, and Invite In

    def create_other_clan_selection_box(self):
        """
        handles the creation of other_clan_selection_container
        """
        self.other_clan_selection_container = (
            pygame_gui.elements.UIAutoResizingContainer(
                ui_scale(pygame.Rect((66, 451), (50, 50))),
                object_id="#other_clan_selection_container",
                starting_height=1,
                manager=MANAGER,
            )
        )
        self.other_clan_selection_elements["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (662, 194))),
            get_box(BoxStyles.FRAME, (662, 194)),
            container=self.other_clan_selection_container,
            starting_height=1,
            manager=MANAGER,
        )
        for i, other_clan in enumerate(game.clan.all_clans):
            if other_clan.name == game.clan.name:
                continue
            x_pos = 128
            self.other_clan_selection_elements[f"container{i}"] = UIContainer(
                ui_scale(pygame.Rect((8 + (x_pos * i), 10), (134, 174))),
                starting_height=1,
                container=self.other_clan_selection_container,
                manager=MANAGER,
            )
            self.other_clan_selection_elements[f"button{i}"] = UIImageButton(
                ui_scale(pygame.Rect((0, 0), (134, 174))),
                "",
                object_id="#other_clan_select_button",
                starting_height=2,
                container=self.other_clan_selection_elements[f"container{i}"],
                manager=MANAGER,
                anchors={"centerx": "centerx"},
            )

            self.other_clan_selection_elements[
                f"clan_symbol{i}"
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, -30), (50, 50))),
                clan_symbol_sprite(other_clan),
                object_id=f"#clan_symbol{i}",
                starting_height=1,
                container=self.other_clan_selection_elements[f"container{i}"],
                manager=MANAGER,
                anchors={"center": "center"},
            )

            self.other_clan_selection_elements[
                f"clan_name{i}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 20), (133, -1))),
                text=f"{other_clan.name}Clan",
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                container=self.other_clan_selection_elements[f"container{i}"],
                manager=MANAGER,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.other_clan_selection_elements[f"clan_symbol{i}"],
                },
            )
            self.other_clan_selection_elements[
                f"clan_temper{i}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 2), (133, -1))),
                text=f"screens.leader_den.{other_clan.temperament.strip()}",
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                container=self.other_clan_selection_elements[f"container{i}"],
                manager=MANAGER,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.other_clan_selection_elements[f"clan_name{i}"],
                },
            )
            self.other_clan_selection_elements[
                f"clan_rel{i}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 2), (133, -1))),
                text=f"screens.leader_den.{get_other_clan_relation(other_clan.relations).strip()}",
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                container=self.other_clan_selection_elements[f"container{i}"],
                manager=MANAGER,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.other_clan_selection_elements[f"clan_temper{i}"],
                },
            )

    def create_outsider_selection_box(self):
        self.outsider_selection_container = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((59, 455), (0, 0))),
            object_id="#outsider_selection_container",
            starting_height=1,
            manager=MANAGER,
            visible=False,
        )
        self.outsider_selection_elements["page_left"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 70), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.outsider_selection_container,
            starting_height=1,
            manager=MANAGER,
        )
        self.outsider_selection_elements["page_right"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((646, 70), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.outsider_selection_container,
            starting_height=1,
            manager=MANAGER,
        )
        self.outsider_selection_elements["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((28, 0), (624, 174))),
            get_box(BoxStyles.ROUNDED_BOX, (624, 174)),
            container=self.outsider_selection_container,
            starting_height=2,
            manager=MANAGER,
        )

        self.focus_outsider_container = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#focus_outsider_container",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER,
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

        self.update_text(clan=True)

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

        if get_clan_setting("lead_den_outsider_event"):
            current_setting = get_clan_setting("lead_den_outsider_event")
            self.focus_cat = Cat.fetch_cat(current_setting["cat_ID"])
            self.update_outsider_focus()
            self.update_outsider_interaction_choice(current_setting["interaction_type"])

        self.update_text(clan=False)

    def update_other_clan_focus(self):
        """
        handles changing the clan that is currently in focus
        """
        # killing so we can reset what's inside
        if self.focus_clan_container:
            self.focus_clan_container.kill()

        self.focus_clan_container = UIContainer(
            ui_scale(pygame.Rect((0, 0), (240, 398))),
            object_id="#focus_clan_container",
            container=self.focus_frame_container,
            manager=MANAGER,
        )

        self.focus_clan_elements["clan_symbol"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 67), (100, 100))),
            pygame.transform.scale(
                clan_symbol_sprite(self.focus_clan, force_light=True),
                ui_scale_dimensions((100, 100)),
            ),
            object_id="#clan_symbol",
            starting_height=1,
            container=self.focus_clan_container,
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        x_pos = 10
        y_pos = 182
        relation = get_other_clan_relation(self.focus_clan.relations)

        self.focus_clan_elements["clan_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 15), (215, -1))),
            text=f"{self.focus_clan.name}Clan",
            object_id="#text_box_30_horizcenter",
            container=self.focus_clan_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_clan_elements["clan_symbol"],
            },
        )
        self.focus_clan_elements["clan_temper"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (215, -1))),
            text=f"screens.leader_den.{self.focus_clan.temperament.strip()}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_clan_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_clan_elements["clan_name"],
            },
        )
        self.focus_clan_elements["clan_rel"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 0), (215, -1))),
            text=f"screens.leader_den.{relation}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_clan_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_clan_elements["clan_temper"],
            },
        )

        self.focus_frame_elements["negative_interaction"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 265), (121, 30))),
            "provoke",
            get_button_dict(ButtonStyles.SQUOVAL, (121, 30)),
            object_id="@buttonstyles_squoval",
            container=self.focus_clan_container,
            starting_height=3,
            manager=MANAGER,
            visible=False,
            anchors={"centerx": "centerx"},
        )
        self.focus_frame_elements["positive_interaction"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 305), (121, 30))),
            "befriend",
            get_button_dict(ButtonStyles.SQUOVAL, (121, 30)),
            container=self.focus_clan_container,
            object_id="@buttonstyles_squoval",
            starting_height=3,
            manager=MANAGER,
            visible=False,
            anchors={"centerx": "centerx"},
        )

        if self.no_leader:
            self.focus_clan_container.disable()

        interaction = OtherClan.interaction_dict[relation]
        self.focus_frame_elements["negative_interaction"].set_text(
            f"screens.leader_den.{interaction[0]}"
        )
        self.focus_frame_elements["negative_interaction"].show()

        self.focus_frame_elements["positive_interaction"].set_text(
            f"screens.leader_den.{interaction[1]}"
        )
        self.focus_frame_elements["positive_interaction"].show()

    def update_clan_interaction_choice(self, object_id):
        """
        handles changing chosen clan interaction. updates notice text.
        :param object_id: the text in the button
        """

        interaction = object_id.replace("#clan_", "")

        self.screen_elements["clan_notice_text"].set_text(
            f"screens.leader_den.action_clan_{interaction}",
            text_kwargs={
                "m_c": game.clan.leader,
                "other_clan": self.focus_clan,
            },
        )

        self.handle_other_clan_interaction(interaction)

    def handle_other_clan_interaction(self, interaction_type: str):
        set_clan_setting("lead_den_interaction", True)

        gathering_cat = game.clan.leader if not self.helper_cat else self.helper_cat

        success = False

        player_temper_int = self._find_temper_int(self.clan_temper)
        other_temper_int = self._find_temper_int(self.focus_clan.temperament)
        fail_chance = self._compare_temper(player_temper_int, other_temper_int)

        if gathering_cat != game.clan.leader:
            fail_chance = fail_chance * 1.4

        if random.random() >= fail_chance:
            success = True

        set_clan_setting(
            "lead_den_clan_event",
            {
                "cat_ID": gathering_cat.ID,
                "other_clan": self.focus_clan.name,
                "player_clan_temper": self.clan_temper,
                "interaction_type": interaction_type,
                "success": success,
            },
        )

    def _compare_temper(self, player_temper_int, other_temper_int) -> float:
        """
        compares two temper ints and finds the chance of failure between them, adds additional modifiers for distance
        between two tempers on the temperament chart.  returns percent chance of failure
        """
        # base equation for fail chance (temper_int - temper_int) / 10
        fail_chance = (abs(int(player_temper_int - other_temper_int))) / 10

        temper_dict = constants.TEMPERAMENT_DICT
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
            if clan_social == "low social" and other_social == "high_social":
                fail_chance += 0.1
            elif other_social == "low social" and clan_social == "high_social":
                fail_chance += 0.1

        # checks aggression distance between tempers and adds modifiers appropriately
        if clan_index != other_index:
            fail_chance += 0.05
            if clan_index == 0 and other_index == 2:
                fail_chance += 0.1
            elif other_index == 0 and clan_index == 2:
                fail_chance += 0.1

        if fail_chance > 0.5:
            fail_chance = 0.5

        return fail_chance

    @staticmethod
    def _find_temper_int(temper: str) -> int:
        """
        returns int value (social rank + aggression rank) of given temperament
        """
        temper_dict = constants.TEMPERAMENT_DICT
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
            self.focus_outsider_container.kill()

        self.focus_outsider_container = UIContainer(
            ui_scale(pygame.Rect((0, 0), (240, 398))),
            object_id="#focus_outsider_container",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER,
        )

        self.focus_outsider_elements["cat_sprite"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 67), (100, 100))),
            pygame.transform.scale(
                self.focus_cat.sprite, ui_scale_dimensions((100, 100))
            ),
            object_id="#focus_cat_sprite",
            container=self.focus_outsider_container,
            starting_height=1,
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.focus_outsider_elements["cat_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 15), (215, -1))),
            text=shorten_text_to_fit(str(self.focus_cat.name), 220, 15),
            object_id="#text_box_30_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_outsider_elements["cat_sprite"],
            },
        )
        self.focus_outsider_elements["cat_status"] = pygame_gui.elements.UILabel(
            relative_rect=ui_scale(pygame.Rect((0, 5), (218, -1))),
            text=f"general.{self.focus_cat.status.rank}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_outsider_elements["cat_name"],
            },
            text_kwargs={"count": 1},
        )
        self.focus_outsider_elements["cat_trait"] = pygame_gui.elements.UILabel(
            relative_rect=ui_scale(pygame.Rect((0, 0), (218, -1))),
            text=f"cat.personality.{self.focus_cat.personality.trait}",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_outsider_elements["cat_status"],
            },
        )
        self.focus_outsider_elements["cat_skills"] = pygame_gui.elements.UILabel(
            relative_rect=ui_scale(pygame.Rect((0, 0), (218, -1))),
            text="screens.leader_den.outsider_skill",
            object_id="#text_box_22_horizcenter",
            container=self.focus_outsider_container,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_outsider_elements["cat_trait"],
            },
            text_kwargs={
                "skill": self.focus_cat.skills.skill_string(short=True),
                "m_c": self.focus_cat,
            },
        )

        if self.focus_outsider_button_container:
            self.focus_outsider_button_container.kill()

        self.focus_outsider_button_container = UIContainer(
            ui_scale(pygame.Rect((0, 5), (121, 121))),
            object_id="#focus_outsider_button_container",
            container=self.focus_outsider_container,
            starting_height=1,
            manager=MANAGER,
            visible=True,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_outsider_elements["cat_skills"],
            },
        )

        self.focus_button["hunt"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 0), (121, 30))),
            "screens.leader_den.hunt",
            get_button_dict(ButtonStyles.SQUOVAL, (121, 30)),
            object_id="@buttonstyles_squoval",
            tool_tip_text="screens.leader_den.hunt_tooltip",
            tool_tip_text_kwargs={"r_c": self.focus_cat},
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
            },
        )

        self.focus_button["drive"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 5), (121, 30))),
            "screens.leader_den.drive",
            get_button_dict(ButtonStyles.SQUOVAL, (121, 30)),
            object_id="@buttonstyles_squoval",
            tool_tip_text="screens.leader_den.drive_tooltip",
            tool_tip_text_kwargs={"r_c": self.focus_cat},
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_button["hunt"],
            },
        )

        self.focus_button["invite"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 5), (121, 30))),
            "screens.leader_den.invite",
            get_button_dict(ButtonStyles.SQUOVAL, (121, 30)),
            object_id="@buttonstyles_squoval",
            tool_tip_text="screens.leader_den.invite_tooltip",
            tool_tip_text_kwargs={"r_c": self.focus_cat},
            container=self.focus_outsider_button_container,
            starting_height=3,
            manager=MANAGER,
            visible=False,
            anchors={
                "centerx": "centerx",
                "top_target": self.focus_button["drive"],
            },
        )

        if self.focus_cat.status.is_outsider and not self.focus_cat.status.is_lost(
            CatGroup.PLAYER_CLAN
        ):
            self.focus_button["invite"].set_text("screens.leader_den.invite")
        else:
            self.focus_button["invite"].set_text("screens.leader_den.search")

        self.focus_button["invite"].show()

        self.focus_outsider_button_container.enable()
        if (
            self.focus_cat.age == "newborn" or self.no_leader
        ):  # not allowed to do things to newborns
            self.focus_outsider_button_container.disable()

    def update_text(self, clan=True):
        """
        changes between clan temper and clan rep text
        :param clan: default True. True sets to other_clan text, False sets to outsider text
        """

        if clan:
            self.screen_elements["outsider_notice_text"].hide()
            self.screen_elements["clan_notice_text"].show()

            self.screen_elements["temper_text"].set_text(
                "screens.leader_den.temper_text",
                text_kwargs={
                    "temper": i18n.t(f"screens.leader_den.{self.clan_temper}")
                },
            )
        else:
            self.screen_elements["outsider_notice_text"].show()
            self.screen_elements["clan_notice_text"].hide()

            self.clan_rep = game.clan.reputation
            if 0 <= int(self.clan_rep) <= 30:
                reputation = "hostile"
            elif 31 <= int(self.clan_rep) <= 70:
                reputation = "neutral"
            else:
                reputation = "welcoming"

            self.screen_elements["temper_text"].set_text(
                "screens.leader_den.outsider_rep",
                text_kwargs={"reputation": i18n.t(f"screens.leader_den.{reputation}")},
            )

    def update_outsider_cats(self):
        """
        handles finding and displaying outsider cats
        """
        # get cats for list
        outsiders = [
            i
            for i in Cat.all_cats.values()
            if not i.dead
            and i.status.is_outsider
            and i.status.is_near(CatGroup.PLAYER_CLAN)
        ]

        # separate them into chunks for the pages
        outsider_chunks = self.chunks(outsiders, 20)

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
            ui_scale(pygame.Rect((40, 27), (0, 0))),
            container=self.outsider_selection_container,
            starting_height=3,
            object_id="#outsider_cat_list",
            manager=MANAGER,
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
                ui_scale(pygame.Rect((5 + pos_x, pos_y), (50, 50))),
                cat.sprite,
                cat_object=cat,
                container=self.outsider_cat_list_container,
                object_id=f"#sprite{str(i)}",
                tool_tip_text=str(cat.name),
                starting_height=2,
                manager=MANAGER,
            )

            # changing pos
            pos_x += 60
            if pos_x >= 590:  # checks if row is full
                pos_x = 0
                pos_y += 60

            i += 1

    def update_outsider_interaction_choice(self, action):
        """
        handles changing chosen outsider interaction. updates notice text.
        :param action: the object ID of the interaction button
        """

        self.screen_elements["outsider_notice_text"].set_text(
            f"screens.leader_den.action_outsider_{action}",
            text_kwargs={
                "m_c": game.clan.leader,
                "r_c": self.focus_cat,
            },
        )

        # because our groups are "hunt", "search", "invite" and "drive"
        # we remove the descriptor ("hunt_down", "drive_off", "invite_in")
        self.handle_outsider_interaction(action.split("_")[0])

    def handle_outsider_interaction(self, action):
        """
        handles determining the outcome of an outsider interaction, returns result text
        :param action: the object id of the interaction button pressed
        """
        set_clan_setting("lead_den_interaction", True)

        # percentage of success
        success_chance = (int(game.clan.reputation) / 100) / 1.5
        if game.clan.leader.not_working:
            success_chance = success_chance / 1.2
        # searching should be extra hard, after all those kitties are LOST
        if action == "search":
            success_chance = success_chance / 2
        # if we got to zero somehow, reset to give a teeny little chance of success
        if success_chance <= 0:
            success_chance = 0.1

        if random.random() < success_chance:
            success = True
        else:
            success = False

        set_clan_setting(
            "lead_den_outsider_event",
            {
                "cat_ID": self.focus_cat.ID,
                "interaction_type": action,
                "success": success,
            },
        )

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
