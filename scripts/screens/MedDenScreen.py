import itertools
from collections import deque, defaultdict
from math import ceil
from random import choice
from typing import TypedDict

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
    process_text,
    find_text_width,
)
from scripts.game_structure import game
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.screens.enums import GameScreen
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_offset
from scripts.ui.theme import get_text_box_theme


class MedDenScreen(Screens):
    cat_buttons = {}
    conditions_hover = {}
    cat_names = []

    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.log_box = None
        self.log_title = None
        self.log_tab = None
        self.cats_tab = None
        self.display_med = None
        self.injured_and_sick_cats = None
        self.minor_cats = None
        self.out_den_cats = None
        self.in_den_cats = None
        self.current_med = None
        self.den_base = None
        self.current_page = None
        self.back_button = None

        self.tab_showing = None
        self.tab_list = self.in_den_cats

        self.open_tab = None

        self.den_image = {}
        self.elements = {}

        self.condition_cats = defaultdict(list)
        self.meds: deque | None = None
        self.med_messages: dict = {}
        """Dict of supply message attached to each cat. Key is cat, value is message."""
        self.coverage_message: str = ""

    def handle_event(self, event):
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
                self.update_sick_cats()
            elif event.ui_element == self.elements["prior_cat_page_arrow"]:
                self.current_page -= 1
                self.update_sick_cats()
            elif event.ui_element == self.elements["in_den_tab"]:
                self.elements["in_den_tab"].disable()
                self.tab_showing.enable()
                self.tab_list = self.in_den_cats
                self.tab_showing = self.elements["in_den_tab"]
                self.update_sick_cats()
            elif event.ui_element == self.elements["out_den_tab"]:
                self.tab_showing.enable()
                self.tab_list = self.out_den_cats
                self.tab_showing = self.elements["out_den_tab"]
                self.elements["out_den_tab"].disable()
                self.update_sick_cats()
            elif event.ui_element == self.elements["minor_tab"]:
                self.tab_showing.enable()
                self.tab_list = self.minor_cats
                self.tab_showing = self.elements["minor_tab"]
                self.elements["minor_tab"].disable()
                self.update_sick_cats()
            elif event.ui_element in self.cat_buttons.values():
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.elements["med_image"]:
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.cats_tab:
                self.open_tab = "cats"
                self.cats_tab.disable()
                self.log_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.log_tab:
                self.open_tab = "log"
                self.log_tab.disable()
                self.cats_tab.enable()
                self.handle_tab_toggles()

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

            self.create_cat_display_box()

            # self.tab_list = self.in_den_cats
            # self.current_page = 1
            # self.update_sick_cats()

        self.meds = deque(
            find_alive_cats_with_rank(
                Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
            )
        )
        self.draw_med_den()
        self.update_med_cat()

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.log_title.hide()
            self.log_box.hide()

            self.elements["hurt_sick_title"].show()
            self.elements["prior_cat_page_arrow"].show()
            self.elements["next_cat_page_arrow"].show()
            self.elements["in_den_tab"].show()
            self.elements["out_den_tab"].show()
            self.elements["minor_tab"].show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
        elif self.open_tab == "log":
            self.elements["hurt_sick_title"].hide()
            self.elements["prior_cat_page_arrow"].hide()
            self.elements["next_cat_page_arrow"].hide()
            self.elements["in_den_tab"].hide()
            self.elements["out_den_tab"].hide()
            self.elements["minor_tab"].hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.log_title.show()
            self.log_box.show()

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
        med_skill = displayed_med_cat.skills.skill_string(short=True)
        med_exp = i18n.t(
            "general.exp_label", exp=displayed_med_cat.experience_level_string
        )
        work_status = (
            i18n.t("general.can_work")
            if displayed_med_cat.can_work()
            else i18n.t("general.cant_work")
        )
        info_text = "<br>".join([med_skill, med_exp, work_status])
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

    def update_sick_cats(self):
        """
        set tab showing as either self.in_den_cats, self.out_den_cats, or self.minor_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        tab_list = self.tab_list

        if not tab_list:
            all_pages = []
        else:
            all_pages = self.get_list_chunks(tab_list, 10)

        self.current_page = max(1, min(self.current_page, len(all_pages)))

        # Check for empty list (no cats)
        if all_pages:
            self.display_cats = all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.elements["next_cat_page_arrow"].disable()
            self.elements["prior_cat_page_arrow"].disable()
        else:
            if self.current_page >= len(all_pages):
                self.elements["next_cat_page_arrow"].disable()
            else:
                self.elements["next_cat_page_arrow"].enable()

            if self.current_page <= 1:
                self.elements["prior_cat_page_arrow"].disable()
            else:
                self.elements["prior_cat_page_arrow"].enable()

        pos_x = 175
        pos_y = 460
        i = 0
        for cat in self.display_cats:
            condition_list = []
            if cat.temporary_conditions:
                condition_list.extend(
                    [
                        i18n.t(f"conditions.temporary_conditions.{condition.name}")
                        for condition in cat.temporary_conditions
                    ]
                )
            if cat.permanent_conditions:
                for condition in cat.permanent_conditions:
                    if condition.moons_until_discovery == -2:
                        condition_list.extend(
                            [
                                i18n.t(
                                    f"conditions.permanent_conditions.{permcond.name}"
                                )
                                for permcond in list(cat.permanent_conditions)
                            ]
                        )
            conditions = ",<br>".join(condition_list)

            conditions = process_text(
                conditions, {"m_c": (str(cat.name), choice(cat.pronouns))}
            )

            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                cat.sprite,
                cat_object=cat,
                manager=MANAGER,
                tool_tip_text=conditions,
                starting_height=2,
            )

            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 92, 15)
            self.cat_names.append(
                pygame_gui.elements.UITextBox(
                    short_name,
                    ui_scale(pygame.Rect((pos_x - 30, pos_y + 50), (110, -1))),
                    object_id="#text_box_30_horizcenter",
                    manager=MANAGER,
                )
            )

            pos_x += 100
            if pos_x >= 670:
                pos_x = 175
                pos_y += 80
            i += 1

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

    def create_cat_display_box(self):
        self.elements["cat_list_container"] = UIContainer(
            ui_scale(pygame.Rect((180, 410), (560, 260))),
            manager=MANAGER,
        )

        # TITLE
        self.elements["hurt_sick_title"] = pygame_gui.elements.UITextBox(
            "screens.med_den.hurt_sick_title",
            ui_scale(pygame.Rect((0, 0), (200, 30))),
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            manager=MANAGER,
            container=self.elements["cat_list_container"],
        )
        # BACKGROUND BOX
        self.elements["cat_list_bg"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 0), (560, 200))),
            get_box(BoxStyles.ROUNDED_BOX, (560, 200)),
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"top_target": self.elements["hurt_sick_title"]},
        )
        self.elements["cat_list_bg"].disable()

        # TABS
        self.elements["in_den_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((50, 0), (75, 35))),
            "screens.med_den.in_den",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (75, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"left_target": self.elements["hurt_sick_title"]},
        )
        self.elements["in_den_tab"].disable()
        self.elements["out_den_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, 0), (112, 35))),
            "screens.med_den.out_den",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (112, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"left_target": self.elements["in_den_tab"]},
        )
        self.elements["minor_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, 0), (70, 35))),
            "screens.med_den.minor",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (70, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.elements["cat_list_container"],
            anchors={"left_target": self.elements["out_den_tab"]},
        )
        self.tab_showing = self.elements["in_den_tab"]

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
        )
        self.elements["next_cat_page_arrow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((115, 0), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self.elements["cat_arrow_container"],
        )

    def update_cat_display(self):
        """
        Creates the actual cat list
        """

    def exit_screen(self):
        self.den_base.kill()
        for herb in self.den_image:
            self.den_image[herb].kill()
        self.den_image = {}
        for ele in self.elements.values():
            ele.kill()
        self.back_button.kill()
        if game.clan.game_mode != "classic":
            self.help_button.kill()
            self.elements["cat_list_bg"].kill()
            self.elements["in_den_tab"].kill()
            self.elements["out_den_tab"].kill()
            self.elements["minor_tab"].kill()
            self.clear_cat_buttons()
            self.elements["hurt_sick_title"].kill()
            self.cats_tab.kill()
            self.log_tab.kill()
            self.log_title.kill()
            self.log_box.kill()
        if self.elements["med_image"]:
            self.elements["med_image"].kill()

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        for button in self.conditions_hover:
            self.conditions_hover[button].kill()
        for x in range(len(self.cat_names)):
            self.cat_names[x].kill()

        self.cat_names = []
        self.cat_buttons = {}
