import math
from fractions import Fraction

import i18n
import pygame
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.clan_package.settings import (
    get_clan_setting,
    set_clan_setting,
    switch_clan_setting,
)
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIImageButton,
    UICheckbox,
    UITextBoxTweaked,
    UICatListDisplay,
    UIModifiedScrollingContainer,
)
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale, ui_scale_offset, ui_scale_value


class FreshkillManagement(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((125, 150), (550, 400))),
            window_display_title="Freshkill Management",
            object_id="#freshkill_management_window",
        )

        self.open_view = None
        self.log = None
        self.low_nutrition_cats = None
        self.prey_requirement = game.prey_config["prey_requirement"]
        self.feeding_order = game.prey_config["feeding_order"]
        self.possible_priorities = ["hunter_first", "sick_injured_first"]
        self.possible_orders = [
            "low_rank",
            "high_rank",
            "youngest_first",
            "oldest_first",
            "hungriest_first",
            "experience_first",
        ]
        help_output = i18n.t("screens.clearing.help_tooltip")
        help_output += f"<br>"
        for rank in self.feeding_order:
            amount = self.prey_requirement[rank]
            count = 1
            if amount > 1:
                count = 2

            amount = Fraction(amount)
            if amount.numerator > amount.denominator:
                if amount.denominator == 1:
                    amount = amount.numerator
                else:
                    start_int = amount.numerator - amount.denominator
                    amount = f"{start_int} {start_int}/{amount.denominator}"

            help_output += f"<br><b>{rank}:</b> {i18n.t('screens.clearing.prey_count', count=count, amount=amount)}"

        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((18, 18), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text=help_output,
            container=self,
        )

        # TOP BUTTONS
        self.feed_cats = UISurfaceImageButton(
            ui_scale(pygame.Rect((121, 20), (105, 30))),
            "screens.clearing.feed_cats",
            get_button_dict(ButtonStyles.PROFILE_LEFT, (105, 30)),
            object_id="@buttonstyles_profile_left",
            manager=MANAGER,
            container=self,
        )
        self.open_log = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (65, 30))),
            "screens.clearing.log",
            get_button_dict(ButtonStyles.PROFILE_MIDDLE, (65, 30)),
            object_id="@buttonstyles_profile_middle",
            anchors={"left_target": self.feed_cats},
            manager=MANAGER,
            container=self,
        )
        self.change_tactics = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (140, 30))),
            "screens.clearing.change_tactics",
            get_button_dict(ButtonStyles.PROFILE_RIGHT, (140, 30)),
            object_id="@buttonstyles_profile_right",
            manager=MANAGER,
            anchors={"left_target": self.open_log},
            container=self,
        )

        self.tactic_view_elements = {}

        self.feed_view_elements = {}
        self.current_page = 1
        self.create_feed_view()

    def create_feed_view(self):
        self.feed_cats.disable()
        self.change_tactics.enable()
        self.open_log.enable()
        self.open_view = "feed"

        # CAT LIST
        self.feed_view_elements["previous_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 160), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self,
            manager=MANAGER,
        )
        scale_rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
        scale_rect.topright = ui_scale_offset((-20, 160))
        self.feed_view_elements["next_page_button"] = UISurfaceImageButton(
            scale_rect,
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            anchors={"top": "top", "right": "right"},
            container=self,
            manager=MANAGER,
        )
        self.update_cats_list()

        # BOTTOM BUTTONS
        scale_rect = ui_scale(pygame.Rect((0, 0), (85, 30)))
        scale_rect.bottomleft = ui_scale_offset((35, -20))
        self.feed_view_elements["feed_all"] = UISurfaceImageButton(
            scale_rect,
            "screens.clearing.feed_all",
            get_button_dict(ButtonStyles.SQUOVAL, (85, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"bottom": "bottom", "left": "left"},
            container=self,
        )
        scale_rect = ui_scale(pygame.Rect((0, 0), (125, 30)))
        scale_rect.bottomleft = ui_scale_offset((20, -20))
        self.feed_view_elements["feed_selected"] = UISurfaceImageButton(
            scale_rect,
            "screens.clearing.feed_selected",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={
                "bottom": "bottom",
                "left_target": self.feed_view_elements["feed_all"],
            },
            container=self,
        )
        self.feed_view_elements["ration_prey"] = UICheckbox(
            (15, 345),
            container=self,
            manager=MANAGER,
            check=get_clan_setting("ration_prey"),
            anchors={"left_target": self.feed_view_elements["feed_selected"]},
            tool_tip_text="settings.ration_prey_tooltip",
        )
        scale_rect = ui_scale(pygame.Rect((0, 0), (-1, -1)))
        scale_rect.bottomleft = ui_scale_offset((0, -47))
        self.feed_view_elements["ration_prey_text"] = pygame_gui.elements.UILabel(
            relative_rect=scale_rect,
            text="settings.ration_prey",
            object_id="#text_box_30_horizleft",
            anchors={
                "bottom": "bottom",
                "left_target": self.feed_view_elements["ration_prey"],
            },
            container=self,
            manager=MANAGER,
        )
        self.feed_view_elements["auto_feed"] = UICheckbox(
            (15, 345),
            container=self,
            manager=MANAGER,
            check=get_clan_setting("auto_feed"),
            anchors={"left_target": self.feed_view_elements["ration_prey_text"]},
            tool_tip_text="settings.auto_feed_tooltip",
        )
        scale_rect = ui_scale(pygame.Rect((0, 0), (-1, -1)))
        scale_rect.bottomleft = ui_scale_offset((0, -47))
        self.feed_view_elements["auto_feed_text"] = pygame_gui.elements.UILabel(
            relative_rect=scale_rect,
            text="settings.auto_feed",
            object_id="#text_box_30_horizleft",
            anchors={
                "bottom": "bottom",
                "left_target": self.feed_view_elements["auto_feed"],
            },
            container=self,
            manager=MANAGER,
        )

    def close_feed_view(self):
        for ele in self.feed_view_elements.values():
            ele.kill()

    def update_cats_list(self):
        self.low_nutrition_cats = [
            Cat.fetch_cat(cat_id)
            for cat_id, nutrient in game.clan.freshkill_pile.nutrition_info.items()
            if nutrient.percentage <= 90
        ]

        if "cat_list" in self.feed_view_elements:
            self.feed_view_elements["cat_list"].kill()
            self.feed_view_elements.pop("cat_list")

        self.feed_view_elements["cat_list"] = UICatListDisplay(
            ui_scale(pygame.Rect((45, 40), (455, 300))),
            container=self,
            manager=MANAGER,
            cat_list=self.low_nutrition_cats,
            cats_displayed=12,
            x_px_between=ui_scale_value(5),
            y_px_between=ui_scale_value(10),
            columns=4,
            rows=3,
            show_names=True,
            tool_tip_nutrition=True,
            current_page=self.current_page,
            next_button=self.feed_view_elements["next_page_button"],
            prev_button=self.feed_view_elements["previous_page_button"],
            text_theme="#text_box_30_horizcenter",
            starting_height=1,
            allow_selection=True,
        )

        # STATUS TEXT, this is updated here bc any update to the cat list would be affecting the prey count too
        if "status_text" in self.feed_view_elements:
            self.feed_view_elements["status_text"].kill()
            self.feed_view_elements.pop("status_text")

        current_prey_amount = int(game.clan.freshkill_pile.total_amount)
        needed_amount = math.ceil(game.clan.freshkill_pile.amount_food_needed())

        scale_rect = ui_scale(pygame.Rect((0, 0), (450, -1)))
        scale_rect.bottomleft = ui_scale_offset((0, -100))
        self.feed_view_elements["status_text"] = UITextBoxTweaked(
            i18n.t(
                "screens.clearing.freshkill_pile_tooltip",
                current_prey_amount=current_prey_amount,
                needed_amount=needed_amount,
            ),
            scale_rect,
            object_id="#text_box_30_horizcenter",
            line_spacing=1,
            manager=MANAGER,
            container=self,
            anchors={"bottom": "bottom", "centerx": "centerx"},
        )

    def create_log_view(self):
        self.feed_cats.enable()
        self.change_tactics.enable()
        self.open_log.disable()
        self.open_view = "log"

        log_text = game.freshkill_event_list.copy()
        if not log_text:
            log_text = [i18n.t("screens.clearing.log_empty")]
        self.log = UITextBoxTweaked(
            f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
            ui_scale(pygame.Rect((25, 25), (500, 320))),
            object_id="#text_box_26_horizleft_verttop_pad_14_0_10",
            manager=MANAGER,
            container=self,
            anchors={"top_target": self.feed_cats, "centerx": "centerx"},
        )

    def close_log_view(self):
        if self.log:
            self.log.kill()

    def create_tactic_view(self):
        self.feed_cats.enable()
        self.change_tactics.disable()
        self.open_log.enable()
        self.open_view = "tactic"

        # TOP TEXT
        self.tactic_view_elements["feeding_order_text"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((25, 15), (225, -1))),
            html_text="screens.clearing.feeding_order",
            object_id="#text_box_30_horizcenter",
            anchors={
                "top_target": self.feed_cats,
            },
            container=self,
            manager=MANAGER,
        )
        scale_rect = ui_scale(pygame.Rect((0, 0), (225, -1)))
        scale_rect.topright = ui_scale_offset((-25, 15))
        self.tactic_view_elements["priority_text"] = UITextBoxTweaked(
            relative_rect=scale_rect,
            html_text="screens.clearing.priority",
            object_id="#text_box_30_horizcenter",
            anchors={"top_target": self.feed_cats, "right": "right"},
            container=self,
            manager=MANAGER,
        )

        prev_element = self.tactic_view_elements["feeding_order_text"]
        for order in self.possible_orders:
            self.tactic_view_elements[order] = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 5), (225, 30))),
                f"settings.{order}",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (225, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                tool_tip_text=f"settings.{order}_tooltip",
                anchors={
                    "top_target": prev_element,
                },
                container=self,
            )
            if get_clan_setting(order):
                self.tactic_view_elements[order].disable()
            prev_element = self.tactic_view_elements[order]

        scale_rect = ui_scale(pygame.Rect((0, 0), (225, 350)))
        scale_rect.topright = ui_scale_offset((-25, 15))
        self.tactic_view_elements["checkbox_container"] = UIModifiedScrollingContainer(
            relative_rect=scale_rect,
            anchors={
                "top_target": self.tactic_view_elements["priority_text"],
                "right": "right",
            },
            container=self,
            manager=MANAGER,
        )

        prev_element = self.tactic_view_elements["priority_text"]
        for priority in self.possible_priorities:
            self.tactic_view_elements[priority] = UICheckbox(
                (15, 10),
                container=self.tactic_view_elements["checkbox_container"],
                manager=MANAGER,
                check=get_clan_setting(priority),
                anchors={"top_target": prev_element},
                tool_tip_text=f"settings.{priority}_tooltip",
            )

            self.tactic_view_elements[f"{priority}_text"] = pygame_gui.elements.UILabel(
                relative_rect=ui_scale(pygame.Rect((10, 15), (-1, -1))),
                text=f"settings.{priority}",
                object_id="#text_box_30_horizleft",
                anchors={
                    "left_target": self.tactic_view_elements[priority],
                    "top_target": prev_element,
                },
                container=self.tactic_view_elements["checkbox_container"],
                manager=MANAGER,
            )
            prev_element = self.tactic_view_elements[priority]

    def close_tactic_view(self):
        for ele in self.tactic_view_elements.values():
            ele.kill()

    def close_views(self):
        self.close_log_view()
        self.close_feed_view()
        self.close_tactic_view()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # NAVIGATION
            if event.ui_element == self.feed_cats:
                self.close_views()
                self.create_feed_view()
            elif event.ui_element == self.open_log:
                self.close_views()
                self.create_log_view()
            elif event.ui_element == self.change_tactics:
                self.close_log_view()
                self.close_views()
                self.create_tactic_view()

            # FEEDING
            if self.open_view == "feed":
                if event.ui_element == self.feed_view_elements.get("feed_all"):
                    game.clan.freshkill_pile.already_fed = []
                    game.clan.freshkill_pile.feed_cats(self.low_nutrition_cats, True)
                    game.clan.freshkill_pile.already_fed = []
                    self.update_cats_list()
                elif event.ui_element == self.feed_view_elements.get("feed_selected"):
                    game.clan.freshkill_pile.already_fed = []
                    cats_to_feed = [
                        Cat.fetch_cat(i)
                        for i in self.feed_view_elements["cat_list"].selected
                    ]
                    game.clan.freshkill_pile.feed_cats(cats_to_feed, True)
                    game.clan.freshkill_pile.already_fed = []
                    self.feed_view_elements["cat_list"].reset_selection()
                    self.update_cats_list()
                # RATION AND AUTOFEED
                elif event.ui_element == self.feed_view_elements.get("ration_prey"):
                    self.setting_switch(
                        self.feed_view_elements.get("ration_prey"), "ration_prey"
                    )
                elif event.ui_element == self.feed_view_elements.get("auto_feed"):
                    self.setting_switch(
                        self.feed_view_elements.get("auto_feed"), "auto_feed"
                    )

            # CHANGE TACTICS
            elif self.open_view == "tactic":
                for order in self.possible_orders:
                    if event.ui_element == self.tactic_view_elements[order]:
                        switch_clan_setting(order)
                        self.tactic_view_elements[order].disable()
                        # enable all other buttons, since only one of these can be chosen at a time
                        for other_order in self.possible_orders:
                            if order == other_order:
                                continue
                            if get_clan_setting(other_order):
                                switch_clan_setting(other_order)
                                self.tactic_view_elements[other_order].enable()
                                break
                        break
                for priority in self.possible_priorities:
                    if event.ui_element == self.tactic_view_elements[priority]:
                        self.setting_switch(
                            self.tactic_view_elements[priority], priority
                        )
                        # next we need to run through the other settings to uncheck them, cus only one of these can be checked at a time.
                        for other_priority in self.possible_priorities:
                            if other_priority == priority:
                                continue
                            if self.tactic_view_elements[other_priority].checked:
                                self.setting_switch(
                                    self.tactic_view_elements[other_priority],
                                    other_priority,
                                )
                                break
                        break

    @staticmethod
    def setting_switch(button, setting):
        if button.checked:
            button.uncheck()
        else:
            button.check()
        switch_clan_setting(setting)
