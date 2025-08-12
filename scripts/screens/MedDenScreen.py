from random import choice

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.clan_resources.herb.herb_supply import MESSAGES
from scripts.game_structure import game
from scripts.game_structure.ui_elements import (
    UISpriteButton,
    UIImageButton,
    UITextBoxTweaked,
    UISurfaceImageButton,
    UIModifiedImage,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    find_alive_cats_with_rank,
    shorten_text_to_fit,
    event_text_adjust,
    ui_scale_offset,
)
from .Screens import Screens
from ..cat.enums import CatRank
from ..conditions import get_amount_cat_for_one_medic, amount_clanmembers_covered
from ..game_structure.game.switches import switch_set_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


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
        self.hurt_sick_title = None
        self.display_med = None
        self.med_cat = None
        self.minor_tab = None
        self.out_den_tab = None
        self.in_den_tab = None
        self.injured_and_sick_cats = None
        self.minor_cats = None
        self.out_den_cats = None
        self.in_den_cats = None
        self.meds_messages = None
        self.current_med = None
        self.cat_bg = None
        self.last_page = None
        self.next_page = None
        self.last_med = None
        self.next_med = None
        self.den_base = None
        self.med_info = None
        self.med_name = None
        self.current_page = None
        self.meds = None
        self.back_button = None

        self.tab_showing = self.in_den_tab
        self.tab_list = self.in_den_cats

        self.herbs = {}

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.next_med:
                self.current_med += 1
                self.update_med_cat()
            elif event.ui_element == self.last_med:
                self.current_med -= 1
                self.update_med_cat()
            elif event.ui_element == self.next_page:
                self.current_page += 1
                self.update_sick_cats()
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                self.update_sick_cats()
            elif event.ui_element == self.in_den_tab:
                self.in_den_tab.disable()
                self.tab_showing.enable()
                self.tab_list = self.in_den_cats
                self.tab_showing = self.in_den_tab
                self.update_sick_cats()
            elif event.ui_element == self.out_den_tab:
                self.tab_showing.enable()
                self.tab_list = self.out_den_cats
                self.tab_showing = self.out_den_tab
                self.out_den_tab.disable()
                self.update_sick_cats()
            elif event.ui_element == self.minor_tab:
                self.tab_showing.enable()
                self.tab_list = self.minor_cats
                self.tab_showing = self.minor_tab
                self.minor_tab.disable()
                self.update_sick_cats()
            elif event.ui_element in self.cat_buttons.values():
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen("profile screen")
            elif event.ui_element == self.med_cat:
                cat = event.ui_element.return_cat_object()
                switch_set_value(Switch.cat, cat.ID)
                self.change_screen("profile screen")
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
        self.next_med = UISurfaceImageButton(
            ui_scale(pygame.Rect((645, 278), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.last_med = UISurfaceImageButton(
            ui_scale(pygame.Rect((600, 278), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
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
                manager=MANAGER,
            )

            self.hurt_sick_title = pygame_gui.elements.UITextBox(
                "screens.med_den.hurt_sick_title",
                ui_scale(pygame.Rect((140, 410), (200, 30))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"),
                manager=MANAGER,
            )
            self.log_title = pygame_gui.elements.UITextBox(
                "screens.med_den.log_title",
                ui_scale(pygame.Rect((140, 410), (200, 30))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"),
                manager=MANAGER,
            )
            self.log_title.hide()
            self.cat_bg = UIModifiedImage(
                ui_scale(pygame.Rect((140, 440), (560, 200))),
                get_box(BoxStyles.ROUNDED_BOX, (560, 200)),
                manager=MANAGER,
            )
            self.cat_bg.disable()
            log_text = game.herb_events_list.copy()
            self.log_box = pygame_gui.elements.UITextBox(
                f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
                ui_scale(pygame.Rect((150, 450), (540, 180))),
                object_id="#text_box_26_horizleft_verttop_pad_14_0_10",
                manager=MANAGER,
            )
            self.log_box.hide()
            tab_rect = ui_scale(pygame.Rect((109, 462), (100, 30)))
            tab_rect.topright = ui_scale_offset((0, 462))
            self.cats_tab = UISurfaceImageButton(
                tab_rect,
                Icon.CAT_HEAD + i18n.t("screens.med_den.hurt_sick_label"),
                get_button_dict(ButtonStyles.VERTICAL_TAB, (100, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.cat_bg},
            )
            self.cats_tab.disable()
            tab_rect = ui_scale(pygame.Rect((0, 0), (100, 30)))
            tab_rect.topright = ui_scale_offset((0, 10))
            self.log_tab = UISurfaceImageButton(
                tab_rect,
                Icon.NOTEPAD + i18n.t("screens.med_den.log_label"),
                get_button_dict(ButtonStyles.VERTICAL_TAB, (100, 30)),
                object_id="@buttonstyles_vertical_tab",
                manager=MANAGER,
                anchors={
                    "right": "right",
                    "right_target": self.cat_bg,
                    "top_target": self.cats_tab,
                },
            )
            del tab_rect
            self.in_den_tab = UISurfaceImageButton(
                ui_scale(pygame.Rect((370, 409), (75, 35))),
                "screens.med_den.in_den",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (75, 35)),
                object_id="@buttonstyles_horizontal_tab",
                manager=MANAGER,
            )
            self.in_den_tab.disable()
            self.out_den_tab = UISurfaceImageButton(
                ui_scale(pygame.Rect((460, 409), (112, 35))),
                "screens.med_den.out_den",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (112, 35)),
                object_id="@buttonstyles_horizontal_tab",
                manager=MANAGER,
            )
            self.minor_tab = UISurfaceImageButton(
                ui_scale(pygame.Rect((587, 409), (70, 35))),
                "screens.med_den.minor",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (70, 35)),
                object_id="@buttonstyles_horizontal_tab",
                manager=MANAGER,
            )
            self.tab_showing = self.in_den_tab

            self.in_den_cats = []
            self.out_den_cats = []
            self.minor_cats = []
            self.injured_and_sick_cats = []
            for the_cat in Cat.all_cats_list:
                if the_cat.status.alive_in_player_clan and (
                    the_cat.injuries or the_cat.illnesses
                ):
                    self.injured_and_sick_cats.append(the_cat)
            for cat in self.injured_and_sick_cats:
                if cat.injuries:
                    for injury in cat.injuries:
                        if cat.injuries[injury][
                            "severity"
                        ] != "minor" and injury not in [
                            "pregnant",
                            "recovering from birth",
                            "sprain",
                            "lingering shock",
                        ]:
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif (
                            injury
                            in [
                                "recovering from birth",
                                "sprain",
                                "lingering shock",
                                "pregnant",
                            ]
                            and cat not in self.in_den_cats
                        ):
                            if cat not in self.out_den_cats:
                                self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif cat not in (self.in_den_cats or self.out_den_cats):
                            if cat not in self.minor_cats:
                                self.minor_cats.append(cat)
                if cat.illnesses:
                    for illness in cat.illnesses:
                        if (
                            cat.illnesses[illness]["severity"] != "minor"
                            and illness != "grief stricken"
                        ):
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif illness == "grief stricken":
                            if cat not in self.in_den_cats:
                                if cat not in self.out_den_cats:
                                    self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        else:
                            if (
                                cat not in self.in_den_cats
                                and cat not in self.out_den_cats
                                and cat not in self.minor_cats
                            ):
                                self.minor_cats.append(cat)
            self.tab_list = self.in_den_cats
            self.current_page = 1
            self.update_sick_cats()

        self.current_med = 1

        self.draw_med_den()
        self.update_med_cat()

        self.meds_messages = UITextBoxTweaked(
            "",
            ui_scale(pygame.Rect((108, 310), (600, 100))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter"),
            line_spacing=1,
        )

        if self.meds:
            med_messages = []

            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            number = amount_clanmembers_covered(Cat.all_cats.values(), amount_per_med)

            meds_cover = i18n.t(
                "screens.med_den.meds_cover", clansize=number, count=len(self.meds)
            )

            if game.clan.game_mode == "classic":
                meds_cover = ""

            if not self.meds:
                meds_cover = choice(MESSAGES["no_meds_warning"])
            elif len(self.meds) == 1 and number == 0:
                meds_cover = event_text_adjust(
                    Cat=Cat,
                    text=choice(MESSAGES["single_not_working"]),
                    main_cat=self.meds[0],
                    clan=game.clan,
                )
            elif len(self.meds) >= 2 and number == 0:
                meds_cover = event_text_adjust(
                    Cat=Cat, text=choice(MESSAGES["many_not_working"]), clan=game.clan
                )

            if meds_cover:
                med_messages.append(
                    event_text_adjust(Cat, meds_cover, main_cat=self.meds[0])
                )

            if self.meds:
                med_messages.append(
                    game.clan.herb_supply.get_status_message(choice(self.meds))
                )
            self.meds_messages.set_text("<br>".join(med_messages))

        else:
            self.meds_messages.set_text(choice(MESSAGES["no_meds_warning"]))

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.log_title.hide()
            self.log_box.hide()

            self.hurt_sick_title.show()
            self.last_page.show()
            self.next_page.show()
            self.in_den_tab.show()
            self.out_den_tab.show()
            self.minor_tab.show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
        elif self.open_tab == "log":
            self.hurt_sick_title.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.in_den_tab.hide()
            self.out_den_tab.hide()
            self.minor_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.log_title.show()
            self.log_box.show()

    def update_med_cat(self):
        if self.med_cat:
            self.med_cat.kill()
        if self.med_info:
            self.med_info.kill()
        if self.med_name:
            self.med_name.kill()

        # get the med cats
        self.meds = find_alive_cats_with_rank(
            Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
        )

        if not self.meds:
            all_pages = []
        else:
            all_pages = self.chunks(self.meds, 1)

        if self.current_med > len(all_pages):
            if len(all_pages) == 0:
                self.current_med = 1
            else:
                self.current_med = len(all_pages)

        if all_pages:
            self.display_med = all_pages[self.current_med - 1]
        else:
            self.display_med = []

        if len(all_pages) <= 1:
            self.next_med.disable()
            self.last_med.disable()
        else:
            if self.current_med >= len(all_pages):
                self.next_med.disable()
            else:
                self.next_med.enable()

            if self.current_med <= 1:
                self.last_med.disable()
            else:
                self.last_med.enable()

        for cat in self.display_med:
            self.med_cat = UISpriteButton(
                ui_scale(pygame.Rect((435, 165), (150, 150))),
                cat.sprite,
                cat_object=cat,
                manager=MANAGER,
            )
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 137, 15)
            self.med_name = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((525, 155), (225, 30))),
                short_name,
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
            )
            self.med_info = UITextBoxTweaked(
                "",
                ui_scale(pygame.Rect((580, 185), (120, 120))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                line_spacing=1,
                manager=MANAGER,
            )
            med_skill = cat.skills.skill_string(short=True)
            med_exp = i18n.t("general.exp_label", exp=cat.experience_level)
            med_working = True
            if cat.not_working():
                med_working = False
            if med_working is True:
                work_status = i18n.t("general.can_work")
            else:
                work_status = i18n.t("general.cant_work")
            info_list = [med_skill, med_exp, work_status]
            self.med_info.set_text("<br>".join(info_list))

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
            if cat.injuries:
                condition_list.extend(
                    [
                        i18n.t(f"conditions.injuries.{injury}")
                        for injury in list(cat.injuries.keys())
                    ]
                )
            if cat.illnesses:
                condition_list.extend(
                    [
                        i18n.t(f"conditions.illnesses.{illness}")
                        for illness in list(cat.illnesses.keys())
                    ]
                )
            if cat.permanent_condition:
                for condition in cat.permanent_condition:
                    if cat.permanent_condition[condition]["moons_until"] == -2:
                        condition_list.extend(
                            [
                                i18n.t(f"conditions.permanent_conditions.{permcond}")
                                for permcond in list(cat.permanent_condition.keys())
                            ]
                        )
            conditions = ",<br>".join(condition_list)

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

        if not herb_supply.total:
            herb_list = ["Empty"]

        elif game.clan.game_mode != "classic":
            for herb, count in herb_supply.entire_supply.items():
                if count <= 0:
                    continue
                display = (
                    herb_supply.herb[herb].plural_display
                    if count > 1
                    else herb_supply.herb[herb].singular_display
                )
                herb_list.append(f"{count} {display}")

        if len(herb_list) <= 10:
            # classic doesn't display herbs
            if game.clan.game_mode == "classic":
                herb_display = None
            else:
                herb_display = "<br>".join(sorted(herb_list))

            self.den_base = UIImageButton(
                ui_scale(pygame.Rect((108, 95), (396, 224))),
                "",
                object_id="#med_cat_den_hover",
                tool_tip_text=herb_display,
                manager=MANAGER,
            )
        else:
            count = 1
            holding_pairs = []
            pair = []
            added = False
            for y in range(len(herb_list)):
                if (count % 2) == 0:  # checking if count is an even number
                    count += 1
                    pair.append(herb_list[y])
                    holding_pairs.append("   -   ".join(pair))
                    pair.clear()
                    added = True
                    continue
                else:
                    pair.append(herb_list[y])
                    count += 1
                    added = False
            if added is False:
                holding_pairs.extend(pair)

            # classic doesn't display herbs
            if game.clan.game_mode == "classic":
                herb_display = None
            else:
                herb_display = "<br>".join(holding_pairs)
            self.den_base = UIImageButton(
                ui_scale(pygame.Rect((108, 95), (396, 224))),
                "",
                object_id="#med_cat_den_hover_big",
                tool_tip_text=herb_display,
                manager=MANAGER,
            )

        # otherwise draw the herbs you have
        herbs = game.clan.herb_supply.entire_supply

        for herb, count in herbs.items():
            if count <= 0:
                continue
            if herb == "cobwebs":
                self.herbs["cobweb1"] = UIModifiedImage(
                    ui_scale(pygame.Rect((108, 95), (396, 224))),
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/med_cat_den/cobweb1.png"
                        ).convert_alpha(),
                        (792, 448),
                    ),
                    manager=MANAGER,
                )
                self.herbs["cobweb1"].disable()
                if count > 1:
                    self.herbs["cobweb2"] = UIModifiedImage(
                        ui_scale(pygame.Rect((108, 95), (396, 224))),
                        pygame.transform.scale(
                            pygame.image.load(
                                "resources/images/med_cat_den/cobweb2.png"
                            ).convert_alpha(),
                            (792, 448),
                        ),
                        manager=MANAGER,
                    )
                    self.herbs["cobweb2"].disable()
                continue
            self.herbs[herb] = UIModifiedImage(
                ui_scale(pygame.Rect((108, 95), (396, 224))),
                pygame.transform.scale(
                    pygame.image.load(
                        f"resources/images/med_cat_den/{herb}.png"
                    ).convert_alpha(),
                    (792, 448),
                ),
                manager=MANAGER,
            )
            self.herbs[herb].disable()

    def exit_screen(self):
        self.meds_messages.kill()
        self.last_med.kill()
        self.next_med.kill()
        self.den_base.kill()
        for herb in self.herbs:
            self.herbs[herb].kill()
        self.herbs = {}
        if self.med_info:
            self.med_info.kill()
        if self.med_name:
            self.med_name.kill()
        self.back_button.kill()
        if game.clan.game_mode != "classic":
            self.help_button.kill()
            self.cat_bg.kill()
            self.last_page.kill()
            self.next_page.kill()
            self.in_den_tab.kill()
            self.out_den_tab.kill()
            self.minor_tab.kill()
            self.clear_cat_buttons()
            self.hurt_sick_title.kill()
            self.cats_tab.kill()
            self.log_tab.kill()
            self.log_title.kill()
            self.log_box.kill()
        if self.med_cat:
            self.med_cat.kill()

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
