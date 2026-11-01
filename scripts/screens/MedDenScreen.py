import itertools
from collections import deque, defaultdict
from math import ceil
from random import choice
from typing import Literal

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.cat.conditions.coverage_check import (
    amount_of_clan_covered_total,
)
from scripts.cat.enums import CatRank, CatGroup
from scripts.cat.sprites.load_sprites import Sprites
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.clan_resources.den_resources.quarantine_nest import get_current_nest_count
from scripts.clan_resources.herb.herb_supply import MESSAGES
from scripts.events_module.text_adjust import (
    event_text_adjust,
    shorten_text_to_fit,
    find_text_width,
    adjust_list_text,
)
from scripts.game_structure import game
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.screens.enums import GameScreen
from scripts.ui.elements.cat_list_display import UICatListDisplay
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_value, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.build_nests import BuildNestWindow
from scripts.ui.windows.herbs import HerbManagementWindow


class MedDenScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.back_button = None
        self.current_main_display_page = 1
        self.current_quarantine_page = 1

        self.tab_showing: Literal["minor", "major", "severe"] = "severe"

        self.den_image = {}
        self.elements = {}
        self.nest_images = {}

        self.condition_cats = defaultdict(list)
        self.meds: deque | None = None
        self.med_messages: dict = {}
        """Dict of supply message attached to each cat. Key is cat, value is message."""
        self.coverage_message: str = ""

        self.open_view: Literal["supply", "quarantine"] = "supply"

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.elements["next_cat_page_arrow"]:
                self.current_main_display_page += 1
                self.update_tab_and_page()
            elif event.ui_element == self.elements["prior_cat_page_arrow"]:
                self.current_main_display_page -= 1
                self.update_tab_and_page()
            elif event.ui_element == self.elements["severe_tab"]:
                self.tab_showing = "severe"
                self.update_tab_and_page(changed_tab=True)
            elif event.ui_element == self.elements["major_tab"]:
                self.tab_showing = "major"
                self.update_tab_and_page(changed_tab=True)
            elif event.ui_element == self.elements["minor_tab"]:
                self.tab_showing = "minor"
                self.update_tab_and_page(changed_tab=True)
            elif event.ui_element == self.elements["open_log"]:
                HerbManagementWindow(den_button=False)
            elif event.ui_element == self.elements["open_quarantine"]:
                self.open_view = "quarantine"
                if not self.elements.get("quarantine_view_container"):
                    self.create_quarantine_view()
                else:
                    self.elements["quarantine_view_container"].show()
                self.elements["supply_view_container"].hide()
                self.elements["open_quarantine"].disable()
                self.elements["open_supply"].enable()
                self.elements["hurt_sick_title"].set_text(
                    "screens.med_den.infectious_cats_title"
                )
                self.find_display_cats(only_show_infectious=True)
                self.update_tab_and_page(changed_tab=True)
            elif event.ui_element == self.elements["open_supply"]:
                self.open_view = "supply"
                self.elements["supply_view_container"].show()
                self.elements["quarantine_view_container"].hide()
                self.elements["open_quarantine"].enable()
                self.elements["open_supply"].disable()
                self.elements["hurt_sick_title"].set_text(
                    "screens.med_den.hurt_sick_title"
                )
                self.find_display_cats()
                self.update_tab_and_page(changed_tab=True)

        if self.open_view == "supply":
            self.handle_supply_event(event)
        elif self.open_view == "quarantine":
            self.handle_quarantine_event(event)

    def handle_supply_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.elements["cat_list"].cat_sprites.values():
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.elements["next_med_arrow"]:
                self.meds.rotate(-1)
                self.update_med_cat()
            elif event.ui_element == self.elements["prior_med_arrow"]:
                self.meds.rotate(1)
                self.update_med_cat()
            elif event.ui_element == self.elements["med_image"]:
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen(GameScreen.PROFILE)

    def handle_quarantine_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element in self.elements["cat_list"].cat_sprites.values():
                self.update_potential_quarantine_display(
                    event.ui_element.return_cat_object()
                )
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["build_nest"]:
                BuildNestWindow(self)
            if event.ui_element in self.elements["cat_list"].cat_sprites.values():
                cat = event.ui_element.return_cat_object().ID
                if (
                    len(game.clan.quarantined_cats) < get_current_nest_count()
                    and cat not in game.clan.quarantined_cats
                ):
                    game.clan.quarantined_cats.append(cat)
                    self.update_nest_display()
            elif event.ui_element == self.elements["next_nest_page_arrow"]:
                self.current_quarantine_page += 1
                self.update_nest_display()
            elif event.ui_element == self.elements["prior_nest_page_arrow"]:
                self.current_quarantine_page -= 1
                self.update_nest_display()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        self.hide_menu_buttons()
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.open_view = "supply"
        self.create_supply_view()

        if game.clan.game_mode != "classic":
            self.help_button = UIImageButton(
                ui_scale(pygame.Rect((725, 25), (34, 34))),
                "",
                object_id="#help_button",
                manager=MANAGER,
                tool_tip_text="screens.med_den.help_tooltip",
            )

            # find cats who will be displayed
            self.find_display_cats()

            self.create_cat_display()

            # ADDITIONAL BUTTONS
            self.elements["open_log"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 60), (140, 30))),
                "screens.med_den.log_title",
                get_button_dict(ButtonStyles.SQUOVAL, (140, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                anchors={"top_target": self.elements["med_message"]},
            )
            self.elements["open_supply"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 15), (140, 30))),
                "screens.med_den.supply_title",
                get_button_dict(ButtonStyles.SQUOVAL, (140, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                anchors={"top_target": self.elements["open_log"]},
            )
            self.elements["open_supply"].disable()
            self.elements["open_quarantine"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 15), (140, 30))),
                "screens.med_den.quarantine_title",
                get_button_dict(ButtonStyles.SQUOVAL, (140, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                anchors={"top_target": self.elements["open_supply"]},
            )

            self.add_to_map(
                [
                    self.help_button,
                    self.elements["open_log"],
                    self.elements["open_supply"],
                    self.elements["open_quarantine"],
                ]
            )

        self.current_focus = self.back_button

    def create_supply_view(self):
        # container for supply view, this will let us hide and show easily
        self.elements["supply_view_container"] = UIContainer(
            ui_scale(pygame.Rect((100, 85), (650, 324))),
            manager=MANAGER,
        )
        self.meds = deque(
            find_alive_cats_with_rank(
                Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
            )
        )
        self.draw_med_den()
        self.update_med_cat()
        self.add_to_map([self.back_button])

    def create_quarantine_view(self):
        # container for quarantine view, this will let us hide and show easily
        self.elements["quarantine_view_container"] = UIContainer(
            ui_scale(pygame.Rect((50, 75), (700, 324))),
            manager=MANAGER,
        )

        self.elements["potential_cat_frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((10, 0), (295, 200))),
            get_box(BoxStyles.NAMEPLATE, (295, 200)),
            manager=MANAGER,
            container=self.elements["quarantine_view_container"],
        )

        # INFO
        self.elements["quarantine_info"] = pygame_gui.elements.UITextBox(
            "screens.med_den.quarantine_info",
            ui_scale(pygame.Rect((0, 200), (315, 120))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
            container=self.elements["quarantine_view_container"],
        )

        # NEST AMOUNT
        self.elements["quarantine_nest_count"] = pygame_gui.elements.UITextBox(
            "screens.med_den.nest_count",
            ui_scale(pygame.Rect((330, 10), (350, 120))),
            text_kwargs={"count": get_current_nest_count()},
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
            container=self.elements["quarantine_view_container"],
        )
        # NEST FRAME
        self.elements["quarantine_nest_frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((330, 0), (350, 300))),
            get_box(BoxStyles.FRAME, (350, 300)),
            manager=MANAGER,
            container=self.elements["quarantine_view_container"],
        )
        self.elements["quarantine_nest_frame"].disable()

        # ARROWS
        self.elements["prior_nest_page_arrow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((313, 133), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.elements["quarantine_view_container"],
        )
        self.elements["next_nest_page_arrow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((663, 133), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self.elements["quarantine_view_container"],
        )
        self.elements["build_nest"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((445, 278), (120, 30))),
            "screens.med_den.build_nest",
            get_button_dict(ButtonStyles.SQUOVAL, (120, 30)),
            object_id="@buttonstyles_squoval",
            container=self.elements["quarantine_view_container"],
        )

        self.update_nest_display()

    def update_nest_display(self):
        """
        Displays the nests and the quarantined cats
        """
        for ele in self.nest_images.values():
            ele.kill()
        if self.elements.get("quarantine_cat_list"):
            self.remove_from_map(
                self.elements["quarantine_cat_list"].cat_sprites.values()
            )
            self.elements["quarantine_cat_list"].kill()

        self.elements["quarantine_nest_count"].set_text(
            "screens.med_den.nest_count",
            text_kwargs={"count": get_current_nest_count()},
        )

        nest_sprite = Sprites.get_platform(
            biome=game.clan.biome,
            season=game.clan.current_season,
            show_nest=True,
            group=CatGroup.PLAYER_CLAN,
        )

        if get_current_nest_count():
            nest_chunks = self.get_list_chunks(list(range(get_current_nest_count())), 9)

            current_chunk = nest_chunks[self.current_quarantine_page - 1]

            # I apologize for my sins
            row_gap = 86
            column_gap = 103
            i = 0
            for row in range(3):
                if i >= len(current_chunk):
                    break
                for column in range(3):
                    if i >= len(current_chunk):
                        break
                    self.nest_images[f"nest{i}"] = pygame_gui.elements.UIImage(
                        ui_scale(
                            pygame.Rect(
                                (361 + (column_gap * column), 35 + (row_gap * row)),
                                (80, 70),
                            )
                        ),
                        pygame.transform.scale(
                            nest_sprite,
                            ui_scale_dimensions((80, 70)),
                        ),
                        manager=MANAGER,
                        container=self.elements["quarantine_view_container"],
                    )
                    i += 1

            # this is a really weird thing to have to do for the cat list display
            # but, it's necessary since we're doing weird stuff by displaying the nests separate from the cats
            # while also having the arrows control both the nest display and the cat display at once

            cat_chunks = self.get_list_chunks(
                [Cat.fetch_cat(c) for c in game.clan.quarantined_cats], 9
            )
            if self.current_quarantine_page <= len(cat_chunks):
                current_cat_chunk = cat_chunks[self.current_quarantine_page - 1]

                self.elements["quarantine_cat_list"] = UICatListDisplay(
                    ui_scale(pygame.Rect((350, 20), (310, 260))),
                    manager=MANAGER,
                    cat_list=current_cat_chunk,
                    cats_displayed=9,
                    x_px_between=ui_scale_value(5),
                    y_px_between=ui_scale_value(5),
                    columns=3,
                    rows=3,
                    tool_tip_name=True,
                    current_page=self.current_quarantine_page,
                    next_button=self.elements["next_nest_page_arrow"],
                    prev_button=self.elements["prior_nest_page_arrow"],
                    starting_height=1,
                    container=self.elements["quarantine_view_container"],
                )
                self.add_to_map(
                    self.elements["quarantine_cat_list"].cat_sprites.values()
                )

            if self.current_quarantine_page == 1:
                self.elements["prior_nest_page_arrow"].disable()
            if self.current_quarantine_page == len(nest_chunks):
                self.elements["next_nest_page_arrow"].disable()
            if self.current_quarantine_page > 1 and len(nest_chunks) > 1:
                self.elements["prior_nest_page_arrow"].enable()
            if self.current_quarantine_page < len(nest_chunks):
                self.elements["next_nest_page_arrow"].enable()

    def update_potential_quarantine_display(self, cat: Cat):
        if self.elements.get("potential_quarantine_cat_image"):
            self.elements["potential_quarantine_cat_image"].kill()

        self.elements["potential_quarantine_cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((15, 25), (150, 150))),
            pygame.transform.scale(cat.sprite, ui_scale_dimensions((150, 150))),
            container=self.elements["quarantine_view_container"],
        )

        if not self.elements.get("potential_quarantine_cat_name"):
            self.elements[
                "potential_quarantine_cat_name"
            ] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((0, 60), (140, 30))),
                shorten_text_to_fit(str(cat.name), 120, 15),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                anchors={
                    "left_target": self.elements["potential_quarantine_cat_image"]
                },
                container=self.elements["quarantine_view_container"],
            )
        else:
            self.elements["potential_quarantine_cat_name"].set_text(
                shorten_text_to_fit(str(cat.name), 130, 15)
            )

        conditions = adjust_list_text(
            [
                i18n.t(f"conditions.temporary_conditions.{c.name}")
                for c in cat.temporary_conditions
                if c.infectiousness
            ]
        )
        full_infectiousness = 0
        for c in cat.temporary_conditions:
            full_infectiousness += c.infectiousness

        if cat.ID in game.clan.quarantined_cats:
            infection_level = "quarantined"
        elif full_infectiousness > 0.7:
            infection_level = "highly_infectious"
        elif full_infectiousness > 0.4:
            infection_level = "very_infectious"
        else:
            infection_level = "somewhat_infectious"

        infection_level = i18n.t(f"screens.med_den.{infection_level}")

        if not self.elements.get("potential_quarantine_cat_info"):
            self.elements[
                "potential_quarantine_cat_info"
            ] = pygame_gui.elements.UITextBox(
                "<br>".join([conditions, infection_level]),
                ui_scale(pygame.Rect((0, 0), (140, 45))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                manager=MANAGER,
                anchors={
                    "top_target": self.elements["potential_quarantine_cat_name"],
                    "left_target": self.elements["potential_quarantine_cat_image"],
                },
                container=self.elements["quarantine_view_container"],
            )
        else:
            self.elements["potential_quarantine_cat_info"].set_text(
                "<br>".join([conditions, infection_level])
            )

    def draw_med_den(self):
        herb_list = []
        herb_supply = game.clan.herb_supply

        # BASE IMAGE
        self.den_image["base"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (396, 224))),
            "",
            object_id="#med_cat_den_hover_big",
            manager=MANAGER,
            container=self.elements["supply_view_container"],
        )
        self.add_to_map([self.den_image["base"]])

        # GET LIST OF HERB COUNTS TO DISPLAY
        if herb_supply.total <= 0:
            # TODO: localize
            herb_list = ["Empty"]

        elif game.clan.game_mode != "classic":
            herb_list.extend(
                [
                    f"{count} {i18n.t(f'conditions.herbs.{herb}', count=count)}"
                    for herb, count in herb_supply.entire_supply.items()
                    if count > 0
                ]
            )

        # CREATE TOOLTIP OF HERB COUNTS - classic does not do this
        if not game.clan.game_mode == "classic":
            # 10 OR LESS DISPLAY AS SINGLE COLUMN
            if len(herb_list) <= 10:
                herb_display = "<br>".join(sorted(herb_list))

            # OVER 10 DISPLAYS AS TWO COLUMNS
            else:
                herb_list = sorted(
                    herb_list, key=lambda k: find_text_width(k, 13), reverse=True
                )
                midway = ceil(len(herb_list) / 2)
                herb_display = "<br>".join(
                    [
                        (
                            a
                            + " "
                            * (
                                (237 - find_text_width(f"{a}{b}", 13))
                                // find_text_width(" ", 13)
                            )
                            + b
                        )
                        if b
                        else a
                        for a, b in itertools.zip_longest(
                            herb_list[0:midway],
                            sorted(
                                herb_list[midway:], key=lambda k: find_text_width(k, 13)
                            ),
                        )
                    ]
                )

            self.den_image["base"].set_tooltip(herb_display)

        # draw the herbs onto the base
        for herb, count in game.clan.herb_supply.entire_supply.items():
            if count <= 0:
                continue
            # cobwebs get two bc they're special little meowmeows
            if herb == "cobwebs":
                self.den_image["cobweb1"] = UIModifiedImage(
                    ui_scale(pygame.Rect((0, 0), (396, 224))),
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/med_cat_den/cobweb1.png"
                        ).convert_alpha(),
                        (792, 448),
                    ),
                    manager=MANAGER,
                    container=self.elements["supply_view_container"],
                )
                self.den_image["cobweb1"].disable()
                if count > 1:
                    self.den_image["cobweb2"] = UIModifiedImage(
                        ui_scale(pygame.Rect((0, 0), (396, 224))),
                        pygame.transform.scale(
                            pygame.image.load(
                                "resources/images/med_cat_den/cobweb2.png"
                            ).convert_alpha(),
                            (792, 448),
                        ),
                        manager=MANAGER,
                        container=self.elements["supply_view_container"],
                    )
                    self.den_image["cobweb2"].disable()
                continue

            self.den_image[herb] = UIModifiedImage(
                ui_scale(pygame.Rect((0, 0), (396, 224))),
                pygame.transform.scale(
                    pygame.image.load(
                        f"resources/images/med_cat_den/{herb}.png"
                    ).convert_alpha(),
                    (792, 448),
                ),
                manager=MANAGER,
                container=self.elements["supply_view_container"],
            )
            self.den_image[herb].disable()

    def update_med_cat(self):
        """
        Updates the med cat display
        """
        displayed_med_cat = self.meds[0]

        # create cat image
        if self.elements.get("med_image"):
            self.elements["med_image"].kill()

        self.elements["med_image"] = UISpriteButton(
            ui_scale(pygame.Rect((335, 65), (150, 150))),
            displayed_med_cat.sprite,
            cat_object=displayed_med_cat,
            manager=MANAGER,
            container=self.elements["supply_view_container"],
        )
        self.add_to_map([self.elements["med_image"]])

        # display name
        if not self.elements.get("med_name"):
            self.elements["med_name"] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((-44, 55), (225, 30))),
                shorten_text_to_fit(str(displayed_med_cat.name), 137, 15),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                anchors={"left_target": self.elements["med_image"]},
                container=self.elements["supply_view_container"],
            )
        else:
            self.elements["med_name"].set_text(
                shorten_text_to_fit(str(displayed_med_cat.name), 137, 15)
            )

        # display info
        med_trait = i18n.t(f"cat.personality.{displayed_med_cat.personality.trait}")
        med_skill = displayed_med_cat.skills.skill_string(short=True)
        med_exp = i18n.t(
            "general.exp_label", exp=displayed_med_cat.experience_level_string
        )
        work_status = (
            i18n.t("general.can_work")
            if displayed_med_cat.can_work()
            else i18n.t("general.cant_work")
        )
        info_text = "<br>".join([med_trait, med_skill, med_exp, work_status])
        if not self.elements.get("med_info"):
            self.elements["med_info"] = pygame_gui.elements.UITextBox(
                info_text,
                ui_scale(pygame.Rect((0, 0), (140, 100))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                manager=MANAGER,
                anchors={
                    "top_target": self.elements["med_name"],
                    "left_target": self.elements["med_image"],
                },
                container=self.elements["supply_view_container"],
            )
        else:
            self.elements["med_info"].set_text(info_text)

        # arrows for switching to other med cats
        if not self.elements.get("prior_med_arrow"):
            self.elements["prior_med_arrow"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((30, 0), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                starting_height=2,
                anchors={
                    "top_target": self.elements["med_info"],
                    "left_target": self.elements["med_image"],
                },
                container=self.elements["supply_view_container"],
            )
            self.elements["next_med_arrow"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((11, 0), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                starting_height=2,
                anchors={
                    "top_target": self.elements["med_info"],
                    "left_target": self.elements["prior_med_arrow"],
                },
                container=self.elements["supply_view_container"],
            )
            self.add_to_map(
                [self.elements["next_med_arrow"], self.elements["prior_med_arrow"]]
            )

        if len(self.meds) <= 1:
            self.elements["prior_med_arrow"].hide()
            self.elements["next_med_arrow"].hide()

        if not self.elements.get("med_message"):
            self.elements["med_message"] = pygame_gui.elements.UITextBox(
                "",
                ui_scale(pygame.Rect((0, 0), (600, 100))),
                object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter"),
                anchors={
                    "top_target": self.elements["med_image"],
                },
                container=self.elements["supply_view_container"],
            )

            # message on size of clan that can be cared for
            # this is not created for classic clans
            if not game.clan.game_mode == "classic":
                # MESSAGE IF NO MEDS
                if not self.meds:
                    self.coverage_message = choice(MESSAGES["no_meds_warning"])
                # MESSAGE IF SINGLE NON-WORKING MED
                elif len(self.meds) == 1 and not self.meds[0].can_work():
                    self.coverage_message = event_text_adjust(
                        Cat=Cat,
                        text=choice(MESSAGES["single_not_working"]),
                        main_cat=self.meds[0],
                        clan=game.clan,
                    )
                # MESSAGE IF ALL OF MULTIPLE MEDS ARE NOT WORKING
                elif len(self.meds) >= 2 and not any([c.can_work() for c in self.meds]):
                    self.coverage_message = event_text_adjust(
                        Cat=Cat,
                        text=choice(MESSAGES["many_not_working"]),
                        clan=game.clan,
                    )
                # MESSAGE IF A MED CAN WORK
                else:
                    amount_of_clan_covered = amount_of_clan_covered_total(
                        Cat.all_cats.values()
                    )
                    self.coverage_message = event_text_adjust(
                        Cat=Cat,
                        text=i18n.t(
                            "screens.med_den.meds_cover",
                            clansize=amount_of_clan_covered,
                            count=len(self.meds),
                        ),
                        main_cat=self.meds[0],
                        clan=game.clan,
                    )

        if not self.med_messages.get(displayed_med_cat.ID):
            self.med_messages[
                displayed_med_cat.ID
            ] = game.clan.herb_supply.get_status_message(displayed_med_cat)

        self.elements["med_message"].set_text(
            f"{self.coverage_message}<br>{self.med_messages[displayed_med_cat.ID]}"
        )

    def find_display_cats(self, only_show_infectious=False):
        self.condition_cats.clear()
        for cat in Cat.all_cats_list:
            if not cat.status.alive_in_player_clan:
                continue

            all_cons = cat.temporary_conditions + cat.permanent_conditions
            if not all_cons:
                continue

            if only_show_infectious:
                if not any([con.infectiousness for con in cat.temporary_conditions]):
                    continue

            if any([condition.severity == "severe" for condition in all_cons]):
                self.condition_cats["severe"].append(cat)
            elif any([condition.severity == "major" for condition in all_cons]):
                self.condition_cats["major"].append(cat)
            else:
                self.condition_cats["minor"].append(cat)
        if self.condition_cats["severe"]:
            self.tab_showing = "severe"
        elif self.condition_cats["major"]:
            self.tab_showing = "major"
        else:
            self.tab_showing = "minor"

    def create_cat_display(self):
        self.elements["cat_list_container"] = UIContainer(
            ui_scale(pygame.Rect((180, 410), (570, 260))),
            manager=MANAGER,
        )

        # TITLE
        self.elements["hurt_sick_title"] = pygame_gui.elements.UITextBox(
            "screens.med_den.hurt_sick_title",
            ui_scale(pygame.Rect((0, 0), (280, 30))),
            object_id=get_text_box_theme("#text_box_40_horizleft"),
            manager=MANAGER,
            container=self.elements["cat_list_container"],
        )
        # BACKGROUND BOX
        self.elements["cat_list_bg"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 0), (570, 200))),
            get_box(BoxStyles.ROUNDED_BOX, (560, 200)),
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"top_target": self.elements["hurt_sick_title"]},
        )
        self.elements["cat_list_bg"].disable()

        # TABS
        self.elements["severe_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, 0), (75, 35))),
            "screens.med_den.in_den",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (75, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"left_target": self.elements["hurt_sick_title"]},
        )
        self.elements["major_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, 0), (75, 35))),
            "screens.med_den.out_den",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (75, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"left_target": self.elements["severe_tab"]},
        )
        self.elements["minor_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, 0), (75, 35))),
            "screens.med_den.minor",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (75, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"left_target": self.elements["major_tab"]},
        )

        self.elements[f"{self.tab_showing}_tab"].disable()

        # PAGE ARROWS
        self.elements["cat_arrow_container"] = UIContainer(
            ui_scale(pygame.Rect((0, -6), (150, 35))),
            container=self.elements["cat_list_container"],
            manager=MANAGER,
            anchors={"top_target": self.elements["cat_list_bg"], "centerx": "centerx"},
        )
        self.elements["prior_cat_page_arrow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 0), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.elements["cat_arrow_container"],
            starting_height=-1,
        )
        self.elements["next_cat_page_arrow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((115, 0), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self.elements["cat_arrow_container"],
            starting_height=-1,
        )
        self.add_to_map(
            [
                self.elements["severe_tab"],
                self.elements["major_tab"],
                self.elements["minor_tab"],
                self.elements["prior_cat_page_arrow"],
                self.elements["next_cat_page_arrow"],
            ]
        )

        self.current_main_display_page = 1
        self.update_cat_display()

    def update_cat_display(self):
        """
        Creates the actual cat list
        """

        tooltip_text = [
            adjust_list_text(
                (
                    [
                        i18n.t(
                            f"conditions.{'temporary_conditions' if con in cat.temporary_conditions else 'permanent_conditions'}.{con.name}"
                        )
                        for con in cat.temporary_conditions + cat.permanent_conditions
                    ]
                )
            )
            for cat in self.condition_cats[self.tab_showing]
        ]

        self.elements["cat_list"] = UICatListDisplay(
            ui_scale(pygame.Rect((8, 25), (560, 200))),
            manager=MANAGER,
            cat_list=self.condition_cats[self.tab_showing],
            cats_displayed=12,
            x_px_between=ui_scale_value(5),
            y_px_between=ui_scale_value(5),
            columns=6,
            rows=2,
            show_names=True,
            tool_tip_text_list=tooltip_text,
            current_page=self.current_main_display_page,
            next_button=self.elements["next_cat_page_arrow"],
            prev_button=self.elements["prior_cat_page_arrow"],
            text_theme="#text_box_30_horizcenter",
            starting_height=1,
            container=self.elements["cat_list_container"],
        )

        self.add_to_map(self.elements["cat_list"].cat_sprites.values())

    def update_tab_and_page(self, changed_tab=False):
        """
        Updates the cat display to a new tab, if changed_tab, else updates to self.current_page.
        """
        if changed_tab:
            self.current_main_display_page = 1
            for tab in ("minor_tab", "major_tab", "severe_tab"):
                self.elements[tab].enable()
            self.elements[f"{self.tab_showing}_tab"].disable()

            self.remove_from_map(self.elements["cat_list"].cat_sprites.values())
            self.elements["cat_list"].kill()
            self.update_cat_display()

        else:
            self.remove_from_map(self.elements["cat_list"].cat_sprites.values())
            self.elements["cat_list"].update_display(
                current_page=self.current_main_display_page
            )
            self.add_to_map(self.elements["cat_list"].cat_sprites.values())

    def exit_screen(self):
        for herb in self.den_image:
            self.den_image[herb].kill()
        self.den_image = {}
        for ele in self.elements.values():
            ele.kill()
        self.elements = {}
        for ele in self.nest_images.values():
            ele.kill()
        self.nest_images = {}
        self.back_button.kill()
        if game.clan.game_mode != "classic":
            self.help_button.kill()

        self.condition_cats.clear()
        self.med_messages.clear()
