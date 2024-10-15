from typing import Dict

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UISpriteButton,
    UIImageButton,
    UITextBoxTweaked,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
)
from .Screens import Screens
from ..events_module.condition_events import Condition_Events
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import ButtonStyles, get_button_dict
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon

with open("resources/clansettings.json", "r", encoding="utf-8") as f:
    settings_dict = ujson.load(f)


class ClearingScreen(Screens):
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
        self.tactic_tab = None
        self.nutrition_title = None
        self.satisfied_tab = None
        self.satisfied_cats = None
        self.hungry_tab = None
        self.hungry_cats = None
        self.info_messages = None
        self.cat_bg = None
        self.last_page = None
        self.next_page = None
        self.feed_all_button = None
        self.feed_one_button = None
        self.feed_max_button = None
        self.pile_base = None
        self.stop_focus = None
        self.focus_cat = None
        self.focus_cat_object = None
        self.focus_info = None
        self.focus_name = None
        self.current_page = None
        self.back_button = None
        self.tactic_text = {}
        self.tactic_boxes = {}
        self.additional_text = {}
        self.checkboxes = {}

        self.cat_tab_open = self.hungry_tab
        self.tab_list = self.hungry_cats
        self.pile_size = "#freshkill_pile_average"

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            if event.ui_element == self.stop_focus_button:
                self.feed_all_button.show()
                self.stop_focus_button.hide()
                self.feed_one_button.hide()
                self.feed_max_button.hide()
                self.focus_cat_object = None
                if self.focus_cat:
                    self.focus_cat.kill()
                if self.focus_info:
                    self.focus_info.kill()
                if self.focus_name:
                    self.focus_name.kill()
            elif event.ui_element in [self.feed_one_button, self.feed_max_button]:
                amount = 1
                if event.ui_element == self.feed_max_button:
                    amount = (
                        self.focus_cat_object.nutrition.max_score
                        - self.focus_cat_object.nutrition.current_score
                    )
                game.clan.freshkill_pile.feed_one_cat(self.focus_cat_object, amount, 0)
                Condition_Events.handle_nutrient(self.focus_cat_object)
                self.update_cats_list()
                self.update_nutrition_cats()
                self.update_focus_cat()
                self.draw_pile()
                if self.open_tab == "tactic":
                    self.log_tab.enable()
                    self.cats_tab.enable()
                    self.tactic_tab.disable()
                    self.handle_tab_toggles()
                if self.open_tab == "log":
                    self.log_tab.disable()
                    self.cats_tab.enable()
                    self.tactic_tab.enable()
                    self.handle_tab_toggles()
            elif event.ui_element == self.feed_all_button:
                game.clan.freshkill_pile.already_fed = []
                game.clan.freshkill_pile.prepare_feed_cats(self.hungry_cats, True)
                game.clan.freshkill_pile.already_fed = []
                self.update_cats_list()
                self.update_nutrition_cats()
                self.update_focus_cat()
                self.draw_pile()
                if self.open_tab == "tactic":
                    self.log_tab.enable()
                    self.cats_tab.enable()
                    self.tactic_tab.disable()
                    self.handle_tab_toggles()
                if self.open_tab == "log":
                    self.log_tab.disable()
                    self.cats_tab.enable()
                    self.tactic_tab.enable()
                    self.handle_tab_toggles()
            elif event.ui_element == self.next_page:
                self.current_page += 1
                self.update_nutrition_cats()
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                self.update_nutrition_cats()
            elif event.ui_element == self.hungry_tab:
                self.cat_tab_open.enable()
                self.tab_list = self.hungry_cats
                self.cat_tab_open = self.hungry_tab
                self.hungry_tab.disable()
                self.update_cats_list()
                self.update_nutrition_cats()
            elif event.ui_element == self.satisfied_tab:
                self.cat_tab_open.enable()
                self.tab_list = self.satisfied_cats
                self.cat_tab_open = self.satisfied_tab
                self.satisfied_tab.disable()
                self.update_cats_list()
                self.update_nutrition_cats()
            elif (
                event.ui_element in self.cat_buttons.values()
                and event.ui_element != self.focus_cat
            ):
                self.focus_cat_object = event.ui_element.return_cat_object()
                self.update_focus_cat()
            elif event.ui_element == self.cats_tab:
                self.open_tab = "cats"
                self.cats_tab.disable()
                self.log_tab.enable()
                self.tactic_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.log_tab:
                self.open_tab = "log"
                self.log_tab.disable()
                self.cats_tab.enable()
                self.tactic_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.tactic_tab:
                self.open_tab = "tactic"
                self.log_tab.enable()
                self.cats_tab.enable()
                self.tactic_tab.disable()
                self.handle_tab_toggles()

            if len(self.hungry_cats) >= 1 and not self.feed_all_button.is_enabled:
                self.feed_all_button.enable()
            if len(self.hungry_cats) <= 0 and self.feed_all_button.is_enabled:
                self.feed_all_button.disable()
            self.handle_checkbox_events(event)

    def update_cats_list(self):
        clan_cats = [
            cat for cat in Cat.all_cats_list if not cat.outside and not cat.dead
        ]

        self.hungry_cats = [cat for cat in clan_cats if cat.nutrition.percentage <= 99]
        self.satisfied_cats = [
            cat for cat in clan_cats if cat.ID not in self.hungry_cats
        ]

        if self.cat_tab_open == self.satisfied_tab:
            self.tab_list = self.satisfied_cats
        else:
            self.tab_list = self.hungry_cats

    def screen_switches(self):
        super().screen_switches()
        self.hide_menu_buttons()
        if game.clan.game_mode == "classic":
            self.change_screen(game.last_screen_forupdate)
            return

        self.show_mute_buttons()
        self.hide_menu_buttons()
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.stop_focus_button = UIImageButton(
            ui_scale(pygame.Rect((755, 155), (22, 22))),
            "",
            object_id="#exit_window_button",
            manager=MANAGER,
        )
        self.feed_all_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((625, 300), (160, 30))),
            "Feed all hungry",
            get_button_dict(ButtonStyles.SQUOVAL, (160, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.feed_one_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((650, 300), (111, 30))),
            "Feed one",
            get_button_dict(ButtonStyles.SQUOVAL, (115, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.feed_max_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((648, 335), (115, 30))),
            "Feed max",
            get_button_dict(ButtonStyles.SQUOVAL, (115, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.stop_focus_button.hide()
        self.feed_one_button.hide()
        self.feed_max_button.hide()

        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((725, 25), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="Your clan will catch some amount of prey over each timeskip, but successful hunting patrols are the most "
            "important source of freshkill. You can see what was consumed and catched in the Log below! "
            "Freshkill can't be stored endlessly, after four moons prey will rot and will be thrown away. "
            "Cats under 3 moons with a parent(queen) taking care of them, don't need food. "
            "<br><br>"
            "Feeding the Clan is very important, therefore cats will be fed before any changes to rank. "
            "Hover your mouse over the pile to see the current amount and the needed amount of prey of your Clan! ",
        )
        self.last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((330, 636), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((476, 636), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.nutrition_title = pygame_gui.elements.UITextBox(
            "Nutrition Overview",
            ui_scale(pygame.Rect((140, 405), (200, 40))),
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            manager=MANAGER,
        )
        self.log_title = pygame_gui.elements.UITextBox(
            "Freshkill Pile Log",
            ui_scale(pygame.Rect((140, 405), (200, 40))),
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            manager=MANAGER,
        )
        self.tactic_title = pygame_gui.elements.UITextBox(
            "Feeding Tactic",
            ui_scale(pygame.Rect((140, 405), (200, 40))),
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            manager=MANAGER,
        )
        self.log_title.hide()
        self.tactic_title.hide()
        self.cat_bg = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((140, 440), (560, 200))),
            get_box(BoxStyles.ROUNDED_BOX, (560, 200)),
            manager=MANAGER,
        )
        self.cat_bg.disable()
        log_text = game.freshkill_event_list.copy()
        self.log_box = pygame_gui.elements.UITextBox(
            f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
            ui_scale(pygame.Rect((150, 450), (540, 180))),
            object_id="#text_box_26_horizleft_verttop_pad_14_0_10",
            manager=MANAGER,
        )
        self.log_box.hide()
        self.cats_tab = UISurfaceImageButton(
            ui_scale(pygame.Rect((40, 460), (100, 30))),
            Icon.CAT_HEAD + " Cats",
            get_button_dict(ButtonStyles.VERTICAL_TAB, (100, 30)),
            object_id="@buttonstyles_vertical_tab",
            manager=MANAGER,
        )
        self.cats_tab.disable()
        self.log_tab = UISurfaceImageButton(
            ui_scale(pygame.Rect((40, 500), (100, 30))),
            Icon.NOTEPAD + " Log",
            get_button_dict(ButtonStyles.VERTICAL_TAB, (100, 30)),
            object_id="@buttonstyles_vertical_tab",
            manager=MANAGER,
        )
        self.tactic_tab = UISurfaceImageButton(
            ui_scale(pygame.Rect((40, 540), (100, 30))),
            Icon.MAGNIFY + " Tactics",
            get_button_dict(ButtonStyles.VERTICAL_TAB, (100, 30)),
            object_id="@buttonstyles_vertical_tab",
            manager=MANAGER,
        )
        self.hungry_tab = UISurfaceImageButton(
            ui_scale(pygame.Rect((490, 409), (80, 35))),
            "Hungry",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (80, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
        )
        self.satisfied_tab = UISurfaceImageButton(
            ui_scale(pygame.Rect((587, 409), (95, 35))),
            "Satisfied",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (95, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
        )
        self.cat_tab_open = self.hungry_tab
        self.current_page = 1
        self.update_cats_list()
        self.update_nutrition_cats()
        self.update_focus_cat()

        if len(self.hungry_cats) >= 1 and not self.feed_all_button.is_enabled:
            self.feed_all_button.enable()
        if len(self.hungry_cats) <= 0 and self.feed_all_button.is_enabled:
            self.feed_all_button.disable()

        self.draw_pile()

    def display_change_save(self) -> Dict:
        variable_dict = super().display_change_save()

        variable_dict["open_tab"] = self.open_tab
        variable_dict["current_page"] = self.current_page
        variable_dict["focus_cat_object"] = self.focus_cat_object

        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        for key, value in variable_dict.items():
            try:
                setattr(self, key, value)
            except KeyError:
                continue

        if self.open_tab == "tactic":
            self.log_tab.enable()
            self.cats_tab.enable()
            self.tactic_tab.disable()
        elif self.open_tab == "log":
            self.log_tab.disable()
            self.cats_tab.enable()
            self.tactic_tab.enable()
        elif self.open_tab == "cats":
            self.log_tab.enable()
            self.cats_tab.disable()
            self.tactic_tab.enable()

        if len(self.hungry_cats) >= 1 and not self.feed_all_button.is_enabled:
            self.feed_all_button.enable()
        if len(self.hungry_cats) <= 0 and self.feed_all_button.is_enabled:
            self.feed_all_button.disable()

        self.handle_tab_toggles()
        self.update_cats_list()
        self.update_focus_cat()

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.tactic_title.hide()
            self.log_title.hide()
            self.log_box.hide()

            self.nutrition_title.show()
            self.last_page.show()
            self.next_page.show()
            self.hungry_tab.show()
            self.satisfied_tab.show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
            self.delete_checkboxes()
        elif self.open_tab == "log":
            self.tactic_title.hide()
            self.nutrition_title.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.hungry_tab.hide()
            self.satisfied_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()
            self.delete_checkboxes()
            self.log_title.show()
            self.log_box.show()
        elif self.open_tab == "tactic":
            self.nutrition_title.hide()
            self.log_title.hide()
            self.log_box.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.hungry_tab.hide()
            self.satisfied_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.tactic_title.show()
            self.create_checkboxes()

    def update_focus_cat(self):
        if not self.focus_cat_object:
            self.feed_all_button.enable()
            return
        if self.focus_cat:
            self.focus_cat.kill()
        if self.focus_info:
            self.focus_info.kill()
        if self.focus_name:
            self.focus_name.kill()

        # if the nutrition is full grey the feed button out
        self.feed_one_button.show()
        self.feed_max_button.show()
        self.stop_focus_button.show()
        self.feed_all_button.hide()
        p = int(self.focus_cat_object.nutrition.percentage)
        if p >= 100:
            self.feed_one_button.disable()
            self.feed_max_button.disable()
        else:
            self.feed_one_button.enable()
            self.feed_max_button.enable()

        name = str(self.focus_cat_object.name)
        short_name = shorten_text_to_fit(name, 165, 15)
        self.focus_name = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((585, 75), (225, 30))),
            short_name,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )
        self.focus_info = UITextBoxTweaked(
            "",
            ui_scale(pygame.Rect((625, 95), (150, 120))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            line_spacing=1,
            manager=MANAGER,
        )
        self.focus_cat = UISpriteButton(
            ui_scale(pygame.Rect((625, 145), (150, 150))),
            self.focus_cat_object.sprite,
            cat_object=self.focus_cat_object,
            manager=MANAGER,
        )
        info_list = [self.focus_cat_object.skills.skill_string(short=True)]
        nutrition_text = "nutrition: " + self.focus_cat_object.nutrition.nutrition_text
        if game.clan.clan_settings["showxp"]:
            nutrition_text += (
                " (" + str(int(self.focus_cat_object.nutrition.percentage)) + ")"
            )
        info_list.append(nutrition_text)
        work_status = "This cat can work"
        if self.focus_cat_object.not_working():
            work_status = "This cat isn't able to work"
            if self.focus_cat_object.not_work_because_hunger():
                work_status += "\n(because of hunger)"
        info_list.append(work_status)

        self.focus_info.set_text("<br>".join(info_list))

    def update_nutrition_cats(self):
        """
        set tab showing as either self.hungry_cats or self.satisfied_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        tab_list = self.tab_list

        if not tab_list:
            all_pages = []
        else:
            all_pages = self.chunks(tab_list, 10)

        self.current_page = max(1, min(self.current_page, len(all_pages)))

        # Check for empty list (no cats)
        if all_pages:
            self.display_cats = all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.next_page.disable()
            self.last_page.disable()
        else:
            if self.current_page >= len(all_pages):
                self.next_page.disable()
            else:
                self.next_page.enable()

            if self.current_page <= 1:
                self.last_page.disable()
            else:
                self.last_page.enable()

        pos_x = 175
        pos_y = 460
        i = 0
        for cat in self.display_cats:
            condition_list = []
            if cat.illnesses:
                if "starving" in cat.illnesses.keys():
                    condition_list.append("starving")
                elif "malnourished" in cat.illnesses.keys():
                    condition_list.append("malnourished")
            if self.cat_tab_open == self.hungry_tab:
                full_text = " nutrition: " + cat.nutrition.nutrition_text
                if game.clan.clan_settings["showxp"]:
                    full_text += " (" + str(cat.nutrition.percentage) + ")"
                condition_list.append(full_text)
            conditions = (
                ",<br>".join(condition_list) if len(condition_list) > 0 else None
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

    def draw_pile(self):
        if self.info_messages:
            self.info_messages.kill()
        self.info_messages = UITextBoxTweaked(
            "",
            ui_scale(pygame.Rect((108, 310), (550, 80))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter"),
            line_spacing=1,
        )

        information_display = []

        current_prey_amount = game.clan.freshkill_pile.total_amount
        needed_amount = game.clan.freshkill_pile.amount_food_needed()
        warrior_need = game.prey_config["prey_requirement"]["warrior"]
        warrior_amount = int(current_prey_amount / warrior_need)
        general_text = (
            f"Up to {warrior_amount} warriors can be fed with this amount of prey."
        )

        concern_text = "This should not appear."
        if current_prey_amount == 0:
            concern_text = (
                "The fresh-kill pile is empty, the Clan desperately needs prey!"
            )
            self.pile_size = "#freshkill_pile_empty"
        elif 0 < current_prey_amount <= needed_amount / 2:
            concern_text = "The fresh-kill pile can't even feed half of the Clan. Hunting patrols should be organized immediately."
            self.pile_size = "#freshkill_pile_verylow"
        elif needed_amount / 2 < current_prey_amount <= needed_amount:
            concern_text = "Only half of the Clan can be fed currently. Hunting patrols should be organized."
            self.pile_size = "#freshkill_pile_low"
        elif needed_amount < current_prey_amount <= needed_amount * 1.5:
            concern_text = (
                "Every mouth of the Clan can be fed, but some more prey would not harm."
            )
            self.pile_size = "#freshkill_pile_average"
        elif needed_amount * 1.5 < current_prey_amount <= needed_amount * 2.5:
            concern_text = "The fresh-kill pile is overflowing and the Clan can feast!"
            self.pile_size = "#freshkill_pile_good"
        elif needed_amount * 2.5 < current_prey_amount:
            concern_text = "StarClan has blessed the Clan with plentiful prey and the leader sends their thanks to Silverpelt."
            self.pile_size = "#freshkill_pile_full"

        information_display.append(general_text)
        information_display.append(concern_text)
        self.info_messages.set_text("<br>".join(information_display))

        if self.pile_base:
            self.pile_base.kill()
        current_prey_amount = game.clan.freshkill_pile.total_amount
        needed_amount = round(game.clan.freshkill_pile.amount_food_needed(), 2)
        hover_display = f"<b>Current amount:</b> {current_prey_amount}<br><b>Needed amount:</b> {needed_amount}"
        self.pile_base = UIImageButton(
            ui_scale(pygame.Rect((250, 25), (300, 300))),
            "",
            object_id=self.pile_size,
            tool_tip_text=hover_display,
            manager=MANAGER,
        )

    def exit_screen(self):
        if game.clan.game_mode == "classic":
            return
        self.info_messages.kill()
        self.stop_focus_button.kill()
        self.feed_all_button.kill()
        self.feed_one_button.kill()
        self.feed_max_button.kill()
        self.pile_base.kill()
        self.focus_cat_object = None
        if self.focus_cat:
            self.focus_cat.kill()
        if self.focus_info:
            self.focus_info.kill()
        if self.focus_name:
            self.focus_name.kill()
        self.back_button.kill()
        self.help_button.kill()
        self.cat_bg.kill()
        self.last_page.kill()
        self.next_page.kill()
        self.hungry_tab.kill()
        self.satisfied_tab.kill()
        self.clear_cat_buttons()
        self.nutrition_title.kill()
        self.cats_tab.kill()
        self.log_tab.kill()
        self.log_title.kill()
        self.log_box.kill()
        self.tactic_tab.kill()
        self.tactic_title.kill()
        self.delete_checkboxes()
        if self.focus_cat:
            self.focus_cat.kill()

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        for button in self.conditions_hover:
            self.conditions_hover[button].kill()
        for x in range(len(self.cat_names)):
            self.cat_names[x].kill()

        self.cat_names = []
        self.cat_buttons = {}

    def create_checkboxes(self):
        self.delete_checkboxes()

        self.tactic_text[
            "container_general"
        ] = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((140, 450), (230, 175))),
            allow_scroll_x=False,
            manager=MANAGER,
        )

        n = 0
        x_val = 55
        for code, desc in settings_dict["freshkill_tactics"].items():
            if code == "ration prey":
                continue
            if len(desc) == 4 and isinstance(desc[3], list):
                x_val += 40

            self.tactic_text[code] = pygame_gui.elements.UITextBox(
                desc[0],
                ui_scale(pygame.Rect((x_val, n * 45), (500, 39))),
                container=self.tactic_text["container_general"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER,
            )
            n += 1

        self.tactic_text["container_general"].set_scrollable_area_dimensions(
            ui_scale_dimensions((200, (n * 30 + x_val + 20)))
        )

        self.additional_text[
            "container_general"
        ] = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((360, 450), (327, 175))),
            allow_scroll_x=False,
            manager=MANAGER,
        )

        n = 0
        x_val = 55
        for code, desc in settings_dict["freshkill_tactics"].items():
            if code == "ration prey":
                # Handle nested
                if len(desc) == 4 and isinstance(desc[3], list):
                    x_val += 20

                self.additional_text[code] = pygame_gui.elements.UITextBox(
                    desc[0],
                    ui_scale(pygame.Rect((x_val, n * 30), (500, 39))),
                    container=self.additional_text["container_general"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                )
                n += 1

        x_val = 22
        self.additional_text["condition_increase"] = pygame_gui.elements.UITextBox(
            "<b>Status-order + needed amount:</b>",
            ui_scale(pygame.Rect((x_val, n * 25 + 5), (500, 39))),
            container=self.additional_text["container_general"],
            object_id="#text_box_30_horizleft_pad_0_8",
            manager=MANAGER,
        )

        prey_requirement = game.prey_config["prey_requirement"]
        feeding_order = game.prey_config["feeding_order"]
        for status in feeding_order:
            amount = prey_requirement[status]
            self.additional_text["condition_increase"] = pygame_gui.elements.UITextBox(
                f"{n}. {status}: {amount} prey",
                ui_scale(pygame.Rect((x_val, n * 22 + 27), (500, 39))),
                container=self.additional_text["container_general"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER,
            )
            n += 1

        self.additional_text["container_general"].set_scrollable_area_dimensions(
            ui_scale_dimensions((305, (n * 30)))
        )

        self.refresh_checkboxes("general")

    def delete_checkboxes(self):
        for checkbox in self.tactic_boxes.values():
            checkbox.kill()
        self.tactic_boxes = {}
        for text in self.tactic_text.values():
            text.kill()
        self.tactic_text = {}
        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}
        for text in self.additional_text.values():
            text.kill()
        self.additional_text = {}

    def refresh_checkboxes(self, sub_menu):
        """
        TODO: DOCS
        """
        # Kill the checkboxes. No mercy here.
        for checkbox in self.tactic_boxes.values():
            checkbox.kill()
        self.tactic_boxes = {}

        n = 0
        for code, desc in settings_dict["freshkill_tactics"].items():
            if code == "ration prey":
                continue
            if game.clan.clan_settings[code]:
                box_type = "@checked_checkbox"
            else:
                box_type = "@unchecked_checkbox"

            # Handle nested
            disabled = False
            x_val = 10
            if len(desc) == 4 and isinstance(desc[3], list):
                x_val += 25
                disabled = (
                    game.clan.clan_settings.get(desc[3][0], not desc[3][1])
                    != desc[3][1]
                )

            self.tactic_boxes[code] = UIImageButton(
                ui_scale(pygame.Rect((x_val, n * 45), (34, 34))),
                "",
                object_id=box_type,
                container=self.tactic_text["container_" + sub_menu],
                tool_tip_text=desc[1],
            )

            if disabled:
                self.tactic_boxes[code].disable()

            n += 1

        for checkbox in self.checkboxes.values():
            checkbox.kill()
        self.checkboxes = {}

        n = 0
        for code, desc in settings_dict["freshkill_tactics"].items():
            if code == "ration prey":
                if game.clan.clan_settings[code]:
                    box_type = "@checked_checkbox"
                else:
                    box_type = "@unchecked_checkbox"

                # Handle nested
                disabled = False
                x_val = 20
                if len(desc) == 4 and isinstance(desc[3], list):
                    x_val += 50
                    disabled = (
                        game.clan.clan_settings.get(desc[3][0], not desc[3][1])
                        != desc[3][1]
                    )

                self.checkboxes[code] = UIImageButton(
                    ui_scale(pygame.Rect((x_val, n * 25), (34, 34))),
                    "",
                    object_id=box_type,
                    container=self.additional_text["container_" + sub_menu],
                    tool_tip_text=desc[1],
                )

                if disabled:
                    self.checkboxes[code].disable()
                n += 1

    def handle_checkbox_events(self, event):
        """
        Switch on or off, only allow one checkbox to be selected.
        """
        active_key = None
        if event.ui_element in self.tactic_boxes.values():
            for key, value in self.tactic_boxes.items():
                if (
                    value == event.ui_element
                    and value.object_ids[1] == "@unchecked_checkbox"
                ):
                    game.clan.switch_setting(key)
                    active_key = key
                    self.settings_changed = True
                    self.create_checkboxes()
                    break

            # un-switch all other keys
            for key, value in self.tactic_boxes.items():
                if (
                    active_key
                    and key != active_key
                    and value.object_ids[1] == "@checked_checkbox"
                ):
                    game.clan.switch_setting(key)
                    self.settings_changed = True
                    self.create_checkboxes()
                    break

        if event.ui_element in self.checkboxes.values():
            for key, value in self.checkboxes.items():
                if value == event.ui_element:
                    game.clan.switch_setting(key)
                    active_key = key
                    self.settings_changed = True
                    self.create_checkboxes()
                    break
