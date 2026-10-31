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
from scripts.cat.enums import CatRank
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
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
from scripts.ui.scale import ui_scale, ui_scale_value
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.herbs import HerbManagementWindow


class MedDenScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.back_button = None
        self.current_page = None

        self.tab_showing: Literal["minor", "major", "severe"] = "severe"

        self.den_image = {}
        self.elements = {}

        self.condition_cats = defaultdict(list)
        self.meds: deque | None = None
        self.med_messages: dict = {}
        """Dict of supply message attached to each cat. Key is cat, value is message."""
        self.coverage_message: str = ""

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.elements["next_med_arrow"]:
                self.meds.rotate(-1)
                self.update_med_cat()
            elif event.ui_element == self.elements["prior_med_arrow"]:
                self.meds.rotate(1)
                self.update_med_cat()
            elif event.ui_element == self.elements["next_cat_page_arrow"]:
                self.current_page += 1
                self.update_tab_and_page()
            elif event.ui_element == self.elements["prior_cat_page_arrow"]:
                self.current_page -= 1
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
            elif event.ui_element in self.elements["cat_list"].cat_sprites.values():
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.elements["med_image"]:
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.elements["open_log"]:
                HerbManagementWindow(den_button=False)

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

        self.meds = deque(
            find_alive_cats_with_rank(
                Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
            )
        )
        self.draw_med_den()
        self.update_med_cat()

        self.add_to_map([self.back_button])

        if game.clan.game_mode != "classic":
            self.help_button = UIImageButton(
                ui_scale(pygame.Rect((725, 25), (34, 34))),
                "",
                object_id="#help_button",
                manager=MANAGER,
                tool_tip_text="screens.med_den.help_tooltip",
            )

            # find cats who will be displayed
            for cat in Cat.all_cats_list:
                if not cat.status.alive_in_player_clan:
                    continue

                all_cons = cat.temporary_conditions + cat.permanent_conditions
                if not all_cons:
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

            self.create_cat_display()

            # ADDITION BUTTONS
            self.elements["open_log"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 50), (140, 34))),
                "screens.med_den.log_title",
                get_button_dict(ButtonStyles.SQUOVAL, (140, 34)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                anchors={"top_target": self.elements["med_message"]},
            )

            self.add_to_map([self.help_button, self.elements["open_log"]])

        self.current_focus = self.back_button

    def draw_med_den(self):
        herb_list = []
        herb_supply = game.clan.herb_supply

        # BASE IMAGE
        self.den_image["base"] = UIImageButton(
            ui_scale(pygame.Rect((108, 95), (396, 224))),
            "",
            object_id="#med_cat_den_hover_big",
            manager=MANAGER,
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
                    ui_scale(pygame.Rect((108, 95), (396, 224))),
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/med_cat_den/cobweb1.png"
                        ).convert_alpha(),
                        (792, 448),
                    ),
                    manager=MANAGER,
                )
                self.den_image["cobweb1"].disable()
                if count > 1:
                    self.den_image["cobweb2"] = UIModifiedImage(
                        ui_scale(pygame.Rect((108, 95), (396, 224))),
                        pygame.transform.scale(
                            pygame.image.load(
                                "resources/images/med_cat_den/cobweb2.png"
                            ).convert_alpha(),
                            (792, 448),
                        ),
                        manager=MANAGER,
                    )
                    self.den_image["cobweb2"].disable()
                continue

            self.den_image[herb] = UIModifiedImage(
                ui_scale(pygame.Rect((108, 95), (396, 224))),
                pygame.transform.scale(
                    pygame.image.load(
                        f"resources/images/med_cat_den/{herb}.png"
                    ).convert_alpha(),
                    (792, 448),
                ),
                manager=MANAGER,
            )
            self.den_image[herb].disable()

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

        self.current_page = 1
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
            current_page=self.current_page,
            next_button=self.elements["next_cat_page_arrow"],
            prev_button=self.elements["prior_cat_page_arrow"],
            text_theme="#text_box_30_horizcenter",
            starting_height=1,
            container=self.elements["cat_list_container"],
        )

        self.add_to_map(self.elements["cat_list"].cat_sprites.values())

    def update_med_cat(self):
        """
        Updates the med cat display
        """
        displayed_med_cat = self.meds[0]

        # create cat image
        if self.elements.get("med_image"):
            self.elements["med_image"].kill()

        self.elements["med_image"] = UISpriteButton(
            ui_scale(pygame.Rect((435, 160), (150, 150))),
            displayed_med_cat.sprite,
            cat_object=displayed_med_cat,
            manager=MANAGER,
        )
        self.add_to_map([self.elements["med_image"]])

        # display name
        if not self.elements.get("med_name"):
            self.elements["med_name"] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((-60, 150), (225, 30))),
                shorten_text_to_fit(str(displayed_med_cat.name), 137, 15),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                anchors={"left_target": self.elements["med_image"]},
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
                ui_scale(pygame.Rect((0, 0), (120, 90))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                manager=MANAGER,
                anchors={
                    "top_target": self.elements["med_name"],
                    "left_target": self.elements["med_image"],
                },
            )
        else:
            self.elements["med_info"].set_text(info_text)

        # arrows for switching to other med cats
        if not self.elements.get("prior_med_arrow"):
            self.elements["prior_med_arrow"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((20, 0), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                starting_height=2,
                anchors={
                    "top_target": self.elements["med_info"],
                    "left_target": self.elements["med_image"],
                },
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
            )
            self.add_to_map(
                [self.elements["next_med_arrow"], self.elements["prior_med_arrow"]]
            )

        if not self.elements.get("med_message"):
            self.elements["med_message"] = pygame_gui.elements.UITextBox(
                "",
                ui_scale(pygame.Rect((108, 0), (600, 100))),
                object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter"),
                anchors={
                    "top_target": self.elements["med_image"],
                },
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
                    self.coverage_message = i18n.t(
                        "screens.med_den.meds_cover",
                        clansize=amount_of_clan_covered,
                        count=len(self.meds),
                    )

        if not self.med_messages.get(displayed_med_cat.ID):
            self.med_messages[
                displayed_med_cat.ID
            ] = game.clan.herb_supply.get_status_message(displayed_med_cat)

        self.elements["med_message"].set_text(
            f"{self.coverage_message}<br>{self.med_messages[displayed_med_cat.ID]}"
        )

    def update_tab_and_page(self, changed_tab=False):
        """
        Updates the cat display to a new tab, if changed_tab, else updates to self.current_page.
        """
        if changed_tab:
            self.current_page = 1
            for tab in ("minor_tab", "major_tab", "severe_tab"):
                self.elements[tab].enable()
            self.elements[f"{self.tab_showing}_tab"].disable()

            self.remove_from_map(self.elements["cat_list"].cat_sprites.values())
            self.elements["cat_list"].kill()
            self.update_cat_display()

        else:
            self.remove_from_map(self.elements["cat_list"].cat_sprites.values())
            self.elements["cat_list"].update_display(current_page=self.current_page)
            self.add_to_map(self.elements["cat_list"].cat_sprites.values())

    def exit_screen(self):
        for herb in self.den_image:
            self.den_image[herb].kill()
        self.den_image = {}
        for ele in self.elements.values():
            ele.kill()
        self.elements = {}
        self.back_button.kill()
        if game.clan.game_mode != "classic":
            self.help_button.kill()

        self.condition_cats.clear()
