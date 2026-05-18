from random import randrange, choice
from typing import Optional

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import create_cat, create_example_cats
from scripts.cat.enums import CatRank
from scripts.cat.sprites.load_sprites import sprites
from scripts.game_structure import image_cache
from scripts.game_structure.game import Switch, game_setting_get
from scripts.game_structure.game.settings import game_setting_set
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.screens.screens_core import screens_core
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset
from scripts.ui.theme import get_text_box_theme


from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase


class ChooseCampScreen(MakeClanScreenBase):
    def __init__(self, name="choose_camp_screen"):
        super().__init__(name)
        self.tabs = {}
        self.selected_camp_tab = 0

    def screen_switches(self):
        super().screen_switches()

        # move the step buttons back down
        self.elements["previous_step"].set_relative_position(
            ui_scale_dimensions((253, 620))
        )
        self.elements["next_step"].set_relative_position(ui_scale_dimensions((0, 620)))

        # Biome buttons
        self.elements["forest_biome"] = UIImageButton(
            ui_scale(pygame.Rect((196, 100), (100, 46))),
            "screens.make_clan.Forest",
            object_id="#forest_biome_button",
            manager=MANAGER,
        )
        self.elements["mountain_biome"] = UIImageButton(
            ui_scale(pygame.Rect((304, 100), (106, 46))),
            "screens.make_clan.Mountainous",
            object_id="#mountain_biome_button",
            manager=MANAGER,
        )
        self.elements["plains_biome"] = UIImageButton(
            ui_scale(pygame.Rect((424, 100), (88, 46))),
            "screens.make_clan.Plains",
            object_id="#plains_biome_button",
            manager=MANAGER,
        )
        self.elements["beach_biome"] = UIImageButton(
            ui_scale(pygame.Rect((520, 100), (82, 46))),
            "screens.make_clan.Beach",
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
            tool_tip_text="screens.make_clan.season_tooltip",
            tool_tip_text_kwargs={"season": i18n.t("general.Newleaf")},
        )
        self.tabs["greenleaf_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 25), (39, 34))),
            Icon.GREENLEAF,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="screens.make_clan.season_tooltip",
            tool_tip_text_kwargs={"season": i18n.t("general.Greenleaf")},
            anchors={"top_target": self.tabs["newleaf_tab"]},
        )
        self.tabs["leaffall_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 25), (39, 34))),
            Icon.LEAFFALL,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="screens.make_clan.season_tooltip",
            tool_tip_text_kwargs={"season": i18n.t("general.Leaf-fall")},
            anchors={"top_target": self.tabs["greenleaf_tab"]},
        )
        self.tabs["leafbare_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 25), (39, 34))),
            Icon.LEAFBARE,
            get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
            object_id="@buttonstyles_icon_tab_left",
            manager=MANAGER,
            tool_tip_text="screens.make_clan.season_tooltip",
            tool_tip_text_kwargs={"season": i18n.t("general.Leaf-bare")},
            anchors={"top_target": self.tabs["leaffall_tab"]},
        )
        # Random background
        self.elements["random_background"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((255, 585), (290, 30))),
            "screens.make_clan.choose_random_background",
            get_button_dict(ButtonStyles.SQUOVAL, (290, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # art frame
        self.draw_art_frame()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["previous_step"]:
                self.set_bg(None)
                self.change_screen(GameScreen.CHOOSE_CATS)
            elif event.ui_element == self.elements["forest_biome"]:
                self.clan_info["biome"] = "Forest"
                self.selected_camp_tab = 1
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["mountain_biome"]:
                self.clan_info["biome"] = "Mountainous"
                self.selected_camp_tab = 1
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["plains_biome"]:
                self.clan_info["biome"] = "Plains"
                self.selected_camp_tab = 1
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["beach_biome"]:
                self.clan_info["biome"] = "Beach"
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
                self.clan_info["season"] = "Newleaf"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.tabs["greenleaf_tab"]:
                self.clan_info["season"] = "Greenleaf"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.tabs["leaffall_tab"]:
                self.clan_info["season"] = "Leaf-fall"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.tabs["leafbare_tab"]:
                self.clan_info["season"] = "Leaf-bare"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["random_background"]:
                # Select a random biome and background
                self.clan_info["biome"] = self.random_biome_selection()
                self.selected_camp_tab = randrange(1, 5)
                self.refresh_selected_camp()
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["next_step"]:
                pass
                # TODO: open symbols

        return super().handle_event(event)

    def exit_screen(self):
        for ele in self.tabs.values():
            ele.kill()

        super().exit_screen()

    def draw_art_frame(self):
        if "art_frame" in self.elements:
            return
        self.elements["art_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect(((0, 20), (466, 416)))),
            get_box(BoxStyles.FRAME, (466, 416)),
            manager=MANAGER,
            starting_height=2,
            anchors={"center": "center"},
        )

    def refresh_text_and_buttons(self):
        # Enable/disable biome buttons
        if self.clan_info.get("biome") == "Forest":
            self.elements["forest_biome"].disable()
            self.elements["mountain_biome"].enable()
            self.elements["plains_biome"].enable()
            self.elements["beach_biome"].enable()
        elif self.clan_info.get("biome") == "Mountainous":
            self.elements["forest_biome"].enable()
            self.elements["mountain_biome"].disable()
            self.elements["plains_biome"].enable()
            self.elements["beach_biome"].enable()
        elif self.clan_info.get("biome") == "Plains":
            self.elements["forest_biome"].enable()
            self.elements["mountain_biome"].enable()
            self.elements["plains_biome"].disable()
            self.elements["beach_biome"].enable()
        elif self.clan_info.get("biome") == "Beach":
            self.elements["forest_biome"].enable()
            self.elements["mountain_biome"].enable()
            self.elements["plains_biome"].enable()
            self.elements["beach_biome"].disable()

        if self.clan_info.get("season") == "Newleaf":
            self.tabs["newleaf_tab"].disable()
            self.tabs["greenleaf_tab"].enable()
            self.tabs["leaffall_tab"].enable()
            self.tabs["leafbare_tab"].enable()
        elif self.clan_info.get("season") == "Greenleaf":
            self.tabs["newleaf_tab"].enable()
            self.tabs["greenleaf_tab"].disable()
            self.tabs["leaffall_tab"].enable()
            self.tabs["leafbare_tab"].enable()
        elif self.clan_info.get("season") == "Leaf-fall":
            self.tabs["newleaf_tab"].enable()
            self.tabs["greenleaf_tab"].enable()
            self.tabs["leaffall_tab"].disable()
            self.tabs["leafbare_tab"].enable()
        elif self.clan_info.get("season") == "Leaf-bare":
            self.tabs["newleaf_tab"].enable()
            self.tabs["greenleaf_tab"].enable()
            self.tabs["leaffall_tab"].enable()
            self.tabs["leafbare_tab"].disable()

        if self.clan_info.get("biome") and self.selected_camp_tab:
            self.elements["next_step"].enable()

        # Deal with tab and shown camp image:
        self.refresh_selected_camp()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""
        self.tabs["tab1"].kill()
        self.tabs["tab2"].kill()
        self.tabs["tab3"].kill()
        self.tabs["tab4"].kill()

        if self.clan_info.get("biome") == "Forest":
            tab_rect = ui_scale(pygame.Rect((0, 0), (85, 30)))
            tab_rect.topright = ui_scale_offset((5, 180))
            self.tabs["tab1"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_classic",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (85, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.elements["art_frame"]},
            )
            tab_rect = ui_scale(pygame.Rect((0, 0), (70, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab2"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_gully",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (70, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab1"],
                },
            )
            tab_rect = ui_scale(pygame.Rect((0, 0), (85, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab3"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_grotto",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (85, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab2"],
                },
            )

            tab_rect.size = ui_scale_dimensions((100, 30))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab4"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_lakeside",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (100, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab3"],
                },
            )
        elif self.clan_info.get("biome") == "Mountainous":
            tab_rect = ui_scale(pygame.Rect((0, 0), (70, 30)))
            tab_rect.topright = ui_scale_offset((5, 180))
            self.tabs["tab1"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_cliff",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (70, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.elements["art_frame"]},
            )

            tab_rect = ui_scale(pygame.Rect((0, 0), (90, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab2"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_cavern",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (90, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab1"],
                },
            )
            tab_rect = ui_scale(pygame.Rect((0, 0), (130, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab3"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_crystal_river",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (130, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab2"],
                },
            )
            tab_rect = ui_scale(pygame.Rect((0, 0), (80, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab4"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_ruins",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (80, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab3"],
                },
            )
        elif self.clan_info.get("biome") == "Plains":
            tab_rect = ui_scale(pygame.Rect((0, 0), (115, 30)))
            tab_rect.topright = ui_scale_offset((5, 180))
            self.tabs["tab1"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_grasslands",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (115, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.elements["art_frame"]},
            )

            tab_rect = ui_scale(pygame.Rect((0, 0), (90, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab2"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_tunnels",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (90, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab1"],
                },
            )
            tab_rect = ui_scale(pygame.Rect((0, 0), (115, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab3"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_wastelands",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (115, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab2"],
                },
            )
            tab_rect = ui_scale(pygame.Rect((0, 0), (80, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab4"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_bridge",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (80, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab3"],
                },
            )
        elif self.clan_info.get("biome") == "Beach":
            tab_rect = ui_scale(pygame.Rect((0, 0), (110, 30)))
            tab_rect.topright = ui_scale_offset((5, 180))
            self.tabs["tab1"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_tidepools",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (110, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.elements["art_frame"]},
            )

            tab_rect = ui_scale(pygame.Rect((0, 0), (110, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab2"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_tidal_cave",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (110, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab1"],
                },
            )

            tab_rect = ui_scale(pygame.Rect((0, 0), (110, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab3"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_shipwreck",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (110, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab2"],
                },
            )

            tab_rect = ui_scale(pygame.Rect((0, 0), (80, 30)))
            tab_rect.topright = ui_scale_offset((5, 5))
            self.tabs["tab4"] = UISurfaceImageButton(
                tab_rect,
                "screens.make_clan.camp_fjord",
                get_button_dict(ButtonStyles.VERTICAL_TAB, (80, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.elements["art_frame"],
                    "top_target": self.tabs["tab3"],
                },
            )

        (
            self.tabs["tab1"].disable()
            if self.selected_camp_tab == 1
            else self.tabs["tab1"].enable()
        )
        (
            self.tabs["tab2"].disable()
            if self.selected_camp_tab == 2
            else self.tabs["tab2"].enable()
        )
        (
            self.tabs["tab3"].disable()
            if self.selected_camp_tab == 3
            else self.tabs["tab3"].enable()
        )
        (
            self.tabs["tab4"].disable()
            if self.selected_camp_tab == 4
            else self.tabs["tab4"].enable()
        )

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        if self.clan_info.get("biome"):
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

    def get_camp_art_path(self, campnum) -> Optional[str]:
        if not campnum:
            return None

        leaf = self.clan_info.get("season", "Newleaf").replace("-", "")

        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = leaf.casefold()
        light_dark = "dark" if game_setting_get("dark mode") else "light"

        biome = self.clan_info.get("biome").lower()

        return (
            f"{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png"
        )

    def get_camp_bg(self, src=None):
        if src is None:
            src = pygame.image.load(
                self.get_camp_art_path(self.selected_camp_tab)
            ).convert_alpha()

        name = "_".join(
            [
                str(self.clan_info["biome"]),
                str(self.selected_camp_tab),
                self.clan_info.get("season", "Newleaf"),
            ]
        )
        if name not in self.game_bgs:
            self.game_bgs[name] = screens_core.default_game_bgs[self.theme]["default"]
            self.fullscreen_bgs[name] = screens_core.process_blur_bg(src)

        self.set_bg(name)
