from random import randrange

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset


from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase


class ChooseCampScreen(MakeClanScreenBase):
    def __init__(self, name="choose_camp_screen"):
        super().__init__(name)
        self.tabs = {}
        self.selected_camp_tab = 0

    def screen_switches(self):
        super().screen_switches()

        # return step buttons to their default position
        self.elements["previous_step"].set_relative_position(
            ui_scale_dimensions((253, 620))
        )
        self.elements["next_step"].set_relative_position(ui_scale_dimensions((0, 620)))

        # Biome buttons
        self.elements["biome_container"] = UIContainer(
            ui_scale(pygame.Rect(((0, 100), (500, 100)))),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        prev_element = None
        for biome in ("forest", "mountainous", "plains", "beach"):
            self.elements[f"{biome}_biome"] = UIImageButton(
                ui_scale(pygame.Rect((20, 0), (100, 46))),
                f"screens.make_clan.{biome.capitalize()}",
                object_id=f"#{biome}_biome_button",
                container=self.elements["biome_container"],
                anchors={"left_target": prev_element} if prev_element else None,
                manager=MANAGER,
            )
            prev_element = self.elements[f"{biome}_biome"]

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        for i in range(1, 5):
            self.tabs[f"tab{i}"] = UIImageButton(
                ui_scale(pygame.Rect((0, 0), (0, 0))),
                "",
                visible=False,
                manager=MANAGER,
            )

        self.elements["season_container"] = UIContainer(
            ui_scale(pygame.Rect((625, 225), (39, 400))),
            manager=MANAGER,
        )
        season_icon_map = {
            "newleaf": Icon.NEWLEAF,
            "greenleaf": Icon.GREENLEAF,
            "leaf-fall": Icon.LEAFFALL,
            "leaf-bare": Icon.LEAFBARE,
        }
        prev_element = None
        for season, icon in season_icon_map.items():
            self.tabs[f"{season}_tab"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 30), (39, 34))),
                icon,
                get_button_dict(ButtonStyles.ICON_TAB_LEFT, (39, 36)),
                object_id="@buttonstyles_icon_tab_left",
                manager=MANAGER,
                tool_tip_text="screens.make_clan.season_tooltip",
                container=self.elements["season_container"],
                tool_tip_text_kwargs={
                    "season": i18n.t(f"general.{season.capitalize()}")
                },
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.tabs[f"{season}_tab"]

        # Random background
        self.elements["random_background"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((255, 580), (290, 30))),
            "screens.make_clan.choose_random_background",
            get_button_dict(ButtonStyles.SQUOVAL, (290, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # art frame
        self.draw_art_frame()
        self.refresh_text_and_buttons()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["previous_step"]:
                self.set_bg(None)
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_CATS)
            elif event.ui_element == self.elements["forest_biome"]:
                self.clan_info.biome = "Forest"
                self.selected_camp_tab = 1
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["mountainous_biome"]:
                self.clan_info.biome = "Mountainous"
                self.selected_camp_tab = 1
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["plains_biome"]:
                self.clan_info.biome = "Plains"
                self.selected_camp_tab = 1
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["beach_biome"]:
                self.clan_info.biome = "Beach"
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
                self.clan_info.starting_season = "Newleaf"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.tabs["greenleaf_tab"]:
                self.clan_info.starting_season = "Greenleaf"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.tabs["leaf-fall_tab"]:
                self.clan_info.starting_season = "Leaf-fall"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.tabs["leaf-bare_tab"]:
                self.clan_info.starting_season = "Leaf-bare"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["random_background"]:
                # Select a random biome and background
                self.clan_info.biome = self.random_biome_selection()
                self.selected_camp_tab = randrange(1, 5)
                self.clan_info.camp_bg = f"camp{self.selected_camp_tab}"
                self.refresh_selected_camp()
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["next_step"]:
                self.clan_info.camp_bg = f"camp{self.selected_camp_tab}"
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_SYMBOL)

        return super().handle_event(event)

    def exit_screen(self):
        for ele in self.tabs.values():
            ele.kill()

        super().exit_screen()

    def draw_art_frame(self):
        if "art_frame" in self.elements:
            return
        self.elements["art_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect(((0, 10), (466, 416)))),
            get_box(BoxStyles.FRAME, (466, 416)),
            manager=MANAGER,
            starting_height=2,
            anchors={"center": "center"},
        )

    def refresh_text_and_buttons(self):
        # Enable/disable biome buttons
        self.elements["forest_biome"].enable()
        self.elements["mountainous_biome"].enable()
        self.elements["plains_biome"].enable()
        self.elements["beach_biome"].enable()

        if self.clan_info.biome == "Forest":
            self.elements["forest_biome"].disable()
        elif self.clan_info.biome == "Mountainous":
            self.elements["mountainous_biome"].disable()
        elif self.clan_info.biome == "Plains":
            self.elements["plains_biome"].disable()
        elif self.clan_info.biome == "Beach":
            self.elements["beach_biome"].disable()

        # enable/disable season buttons
        self.tabs["newleaf_tab"].enable()
        self.tabs["greenleaf_tab"].enable()
        self.tabs["leaf-fall_tab"].enable()
        self.tabs["leaf-bare_tab"].enable()
        if self.clan_info.starting_season == "Newleaf":
            self.tabs["newleaf_tab"].disable()
        elif self.clan_info.starting_season == "Greenleaf":
            self.tabs["greenleaf_tab"].disable()
        elif self.clan_info.starting_season == "Leaf-fall":
            self.tabs["leaf-fall_tab"].disable()
        elif self.clan_info.starting_season == "Leaf-bare":
            self.tabs["leaf-bare_tab"].disable()

        if self.clan_info.biome and self.selected_camp_tab:
            self.elements["next_step"].enable()

        # Deal with tab and shown camp image:
        self.refresh_selected_camp()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""
        self.tabs["tab1"].kill()
        self.tabs["tab2"].kill()
        self.tabs["tab3"].kill()
        self.tabs["tab4"].kill()

        if self.clan_info.biome == "Forest":
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
        elif self.clan_info.biome == "Mountainous":
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
        elif self.clan_info.biome == "Plains":
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
        elif self.clan_info.biome == "Beach":
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

        self.tabs["tab1"].enable()
        self.tabs["tab2"].enable()
        self.tabs["tab3"].enable()
        self.tabs["tab4"].enable()
        if self.selected_camp_tab:
            self.tabs[f"tab{self.selected_camp_tab}"].disable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        if self.clan_info.biome:
            src = pygame.image.load(
                self.get_camp_art_path(self.selected_camp_tab)
            ).convert_alpha()
            self.elements["camp_art"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((175, 160), (450, 400))),
                pygame.transform.scale(
                    src.copy(),
                    ui_scale_dimensions((450, 400)),
                ),
                manager=MANAGER,
            )
            self.get_camp_bg(src)

        self.draw_art_frame()
