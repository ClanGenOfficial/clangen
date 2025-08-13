from random import choice, sample
from typing import Dict, Optional

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.events_module.patrol.patrol import Patrol
from scripts.game_structure import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
)
from .Screens import Screens
from ..clan_package.settings import get_clan_setting
from ..game_structure import image_cache, constants
from ..game_structure.game.settings import game_setting_get
from ..cat.enums import CatRank
from ..game_structure.propagating_thread import PropagatingThread
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


class PatrolScreen(Screens):
    current_patrol = []
    patrol_stage = "choose_cats"  # Can be 'choose_cats', 'patrol_events' or 'patrol_complete'. Controls the stage of patrol.
    patrol_screen = "patrol_cats"  # Can be "patrol_cats" or "skills". Controls the tab on the select_cats stage
    patrol_type = (
        "general"  # Can be 'general', 'border', 'training', 'med', or 'hunting'
    )
    current_page = 1
    elements = {}  # hold elements for sub-page
    cat_buttons = {}  # Hold cat image sprites.
    selected_cat = None  # Holds selected cat.
    selected_apprentice_index = 0
    selected_mate_index = 0

    def __init__(self, name=None):
        super().__init__(name)

        self.in_progress_data = None
        self.able_box = pygame.transform.scale(
            image_cache.load_image("resources/images/patrol_able_cats.png"),
            ui_scale_dimensions((270, 201)),
        )
        self.app_frame = pygame.transform.scale(
            image_cache.load_image("resources/images/patrol_app_frame.png"),
            ui_scale_dimensions((166, 170)),
        )
        self.mate_frame = pygame.transform.flip(self.app_frame, True, False)

        self.fav = {}
        self.normal_event_choice = None
        self.romantic_event_choice = None
        self.intro_image = None
        self.app_mentor = None
        self.able_cats = None
        self.current_patrol = None
        self.display_text = ""
        self.results_text = ""
        self.start_patrol_thread: Optional[PropagatingThread] = None
        self.proceed_patrol_thread: Optional[PropagatingThread] = None
        self.outcome_art = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
            if self.patrol_stage == "choose_cats":
                self.handle_choose_cats_events(event)

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if self.patrol_stage == "choose_cats":
                self.handle_choose_cats_events(event)
            elif self.patrol_stage == "patrol_events":
                self.handle_patrol_events_event(event)
            elif self.patrol_stage == "patrol_complete":
                self.handle_patrol_complete_events(event)

            self.menu_button_pressed(event)
            self.mute_button_pressed(event)

        elif event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            if event.key == pygame.K_LEFT:
                self.change_screen("list screen")
            # elif event.key == pygame.K_RIGHT:
            # self.change_screen('list screen')

    def handle_choose_cats_events(self, event):
        if event.ui_element == self.elements["random"]:
            if self.able_cats:
                self.selected_cat = choice(self.able_cats)
            else:
                print(
                    "WARNING: attempted to select random cat for patrol from empty list of able cats"
                )
            self.update_selected_cat()
            self.update_button()
        # Check is a cat is clicked
        elif event.ui_element in self.cat_buttons.values():
            self.selected_cat = event.ui_element.return_cat_object()
            self.update_selected_cat()
            self.update_button()
            # Checks if the event was a double click, if it was it add/removes the cat from the patrol
            # as long as the patrol isn't full (6 cats).
            if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
                if self.selected_cat in self.current_patrol:
                    self.current_patrol.remove(self.selected_cat)
                elif len(self.current_patrol) < 6:
                    self.current_patrol.append(self.selected_cat)
                self.update_cat_images_buttons()
                self.update_button()
        elif event.ui_element == self.elements["add_remove_cat"]:
            if self.selected_cat in self.current_patrol:
                self.current_patrol.remove(self.selected_cat)
            else:
                self.current_patrol.append(self.selected_cat)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["add_one"]:
            if len(self.current_patrol) < 6:
                if not get_clan_setting("random med cat"):
                    able_no_med = [
                        cat
                        for cat in self.able_cats
                        if not cat.status.rank.is_any_medicine_rank()
                    ]
                    if len(able_no_med) == 0:
                        able_no_med = self.able_cats
                    self.selected_cat = choice(able_no_med)
                else:
                    if self.able_cats:
                        self.selected_cat = choice(self.able_cats)
                    else:
                        print(
                            "WARNING: attempted to select random cat for patrol from empty list of able cats"
                        )
                self.update_selected_cat()
                self.current_patrol.append(self.selected_cat)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["add_three"]:
            if len(self.current_patrol) <= 3:
                if not get_clan_setting("random med cat"):
                    able_no_med = [
                        cat
                        for cat in self.able_cats
                        if not cat.status.rank.is_any_medicine_rank()
                    ]
                    if len(able_no_med) < 3:
                        able_no_med = self.able_cats
                    self.current_patrol += sample(able_no_med, k=3)
                else:
                    self.current_patrol += sample(self.able_cats, k=3)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["add_six"]:
            if len(self.current_patrol) == 0:
                if not get_clan_setting("random med cat"):
                    able_no_med = [
                        cat
                        for cat in self.able_cats
                        if not cat.status.rank.is_any_medicine_rank()
                    ]
                    if len(able_no_med) < 6:
                        able_no_med = self.able_cats
                    self.current_patrol += sample(able_no_med, k=6)
                else:
                    self.current_patrol += sample(self.able_cats, k=6)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["remove_all"]:
            self.current_patrol = []
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["patrol_tab"]:
            self.patrol_screen = "patrol_cats"
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["skills"]:
            self.patrol_screen = "skills"
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["next_page"]:
            self.current_page += 1
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["last_page"]:
            self.current_page -= 1
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["paw"]:
            if self.patrol_type == "training":
                self.patrol_type = "general"
            else:
                self.patrol_type = "training"
            self.update_button()
        elif event.ui_element == self.elements["claws"]:
            if self.patrol_type == "border":
                self.patrol_type = "general"
            else:
                self.patrol_type = "border"
            self.update_button()
        elif event.ui_element == self.elements["herb"]:
            if self.patrol_type == "med":
                self.patrol_type = "general"
            else:
                self.patrol_type = "med"
            self.update_button()
        elif event.ui_element == self.elements["mouse"]:
            if self.patrol_type == "hunting":
                self.patrol_type = "general"
            else:
                self.patrol_type = "hunting"
            self.update_button()
        elif event.ui_element == self.elements["patrol_start"]:
            self.elements["patrol_start"].disable()
            self.selected_cat = None
            if (
                self.start_patrol_thread is not None
                and self.start_patrol_thread.is_alive()
            ):
                return
            self.start_patrol_thread = self.loading_screen_start_work(
                self.run_patrol_start, "start"
            )
        elif event.ui_element == self.elements.get("mate_button"):
            self.selected_cat = self.mate
            self.update_button()
            self.update_cat_images_buttons()
            self.update_selected_cat()
        elif event.ui_element == self.elements.get("app_mentor_button"):
            self.selected_cat = self.app_mentor
            self.update_button()
            self.update_cat_images_buttons()
            self.update_selected_cat()
        elif event.ui_element == self.elements.get("cycle_app_mentor_left_button"):
            self.selected_apprentice_index -= 1
            self.app_mentor = self.selected_cat.apprentice[
                self.selected_apprentice_index
            ]
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements.get("cycle_app_mentor_right_button"):
            self.selected_apprentice_index += 1
            self.app_mentor = self.selected_cat.apprentice[
                self.selected_apprentice_index
            ]
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements.get("cycle_mate_left_button"):
            self.selected_mate_index -= 1
            self.mate = self.selected_cat.mate[self.selected_mate_index]
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements.get("cycle_mate_right_button"):
            self.selected_mate_index += 1
            self.mate = self.selected_cat.mate[self.selected_mate_index]
            self.update_selected_cat()
            self.update_button()

    def handle_patrol_events_event(self, event):
        inp = None
        if event.ui_element == self.elements["proceed"]:
            inp = "proceed"
        elif event.ui_element == self.elements["not_proceed"]:
            inp = "notproceed"
        elif event.ui_element == self.elements["antagonize"]:
            inp = "antagonize"

        if inp:
            if (
                self.proceed_patrol_thread is not None
                and self.proceed_patrol_thread.is_alive()
            ):
                return
            self.proceed_patrol_thread = self.loading_screen_start_work(
                self.run_patrol_proceed, "proceed", (inp,)
            )

    def handle_patrol_complete_events(self, event):
        if event.ui_element == self.elements["patrol_again"]:
            self.in_progress_data = None
            self.open_choose_cats_screen()
        elif event.ui_element == self.elements["clan_return"]:
            self.in_progress_data = None
            self.change_screen("camp screen")

    def screen_switches(self):
        super().screen_switches()
        self.set_disabled_menu_buttons(["patrol_screen"])
        self.update_heading_text(f"{game.clan.displayname}Clan")
        self.show_mute_buttons()
        self.show_menu_buttons()

        if (
            self.in_progress_data is not None
            and self.in_progress_data["current_moon"] == game.clan.age
            and self.in_progress_data["clan_name"] == game.clan.name
        ):
            self.display_change_load(self.in_progress_data)
        else:
            self.in_progress_data = None
            self.open_choose_cats_screen()

    def display_change_save(self) -> Dict:
        if self.start_patrol_thread is not None and self.start_patrol_thread.is_alive():
            self.start_patrol_thread.join()

        if (
            self.proceed_patrol_thread is not None
            and self.proceed_patrol_thread.is_alive()
        ):
            self.proceed_patrol_thread.join()

        variable_dict = super().display_change_save()

        variable_dict["patrol_stage"] = self.patrol_stage
        variable_dict["patrol_screen"] = self.patrol_screen
        variable_dict["patrol_type"] = self.patrol_type

        variable_dict["selected_cat"] = self.selected_cat
        variable_dict["current_page"] = self.current_page
        variable_dict["current_patrol"] = self.current_patrol
        variable_dict["patrol_obj"] = self.patrol_obj
        variable_dict["intro_image"] = self.intro_image

        variable_dict["display_text"] = self.display_text
        variable_dict["results_text"] = self.results_text
        variable_dict["outcome_art"] = self.outcome_art

        variable_dict["current_moon"] = game.clan.age
        variable_dict["clan_name"] = game.clan.name

        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        for key, value in variable_dict.items():
            try:
                setattr(self, key, value)
            except KeyError:
                continue

        if self.patrol_stage == "choose_cats":
            self.open_choose_cats_screen()
            self.update_selected_cat()
            self.current_patrol = variable_dict["current_patrol"]
            self.update_cat_images_buttons()
            self.update_button()
        elif self.patrol_stage == "patrol_events":
            self.open_patrol_event_screen()
        elif self.patrol_stage == "patrol_complete":
            self.open_patrol_event_screen()
            self.open_patrol_complete_screen()
        else:
            print("how'd that happen? Unidentified patrol stage.")

    def update_button(self):
        """ " Updates button availabilities."""
        if self.patrol_stage == "choose_cats":
            # Killing it now, because we have to switch it out for a "remove cat" button if the cat if
            # already in the patrol
            self.elements["add_remove_cat"].kill()

            if self.selected_cat in self.current_patrol:
                self.elements["add_remove_cat"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, 460), (127, 30))),
                    "buttons.remove_cat",
                    get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
                    object_id="@buttonstyles_squoval",
                    manager=MANAGER,
                    anchors={"centerx": "centerx"},
                )
            elif self.selected_cat is None or len(self.current_patrol) >= 6:
                self.elements["add_remove_cat"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, 460), (98, 30))),
                    "buttons.add_cat",
                    get_button_dict(ButtonStyles.SQUOVAL, (98, 30)),
                    object_id="@buttonstyles_squoval",
                    manager=MANAGER,
                    anchors={"centerx": "centerx"},
                )
                self.elements["add_remove_cat"].disable()
            else:
                self.elements["add_remove_cat"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, 460), (98, 30))),
                    "buttons.add_cat",
                    get_button_dict(ButtonStyles.SQUOVAL, (98, 30)),
                    object_id="@buttonstyles_squoval",
                    manager=MANAGER,
                    anchors={"centerx": "centerx"},
                )

            # Update start patrol button
            if not self.current_patrol:
                self.elements["patrol_start"].disable()
            else:
                self.elements["patrol_start"].enable()

            # Update add random cat buttons
            # Enable all the buttons, to reset them
            self.elements["add_one"].enable()
            self.elements["add_three"].enable()
            self.elements["add_six"].enable()
            self.elements["random"].enable()

            # making sure meds don't get the option for other patrols
            if any(
                (cat.status.rank.is_any_medicine_rank() for cat in self.current_patrol)
            ):
                self.patrol_type = "med"
            else:
                if self.patrol_type == "med":
                    self.patrol_type = "general"

            self.elements["paw"].enable()
            self.elements["mouse"].enable()
            self.elements["claws"].enable()
            self.elements["herb"].enable()
            self.elements["info"].kill()  # clearing the text before displaying new text

            if self.patrol_type != "med" and self.current_patrol:
                self.elements["herb"].disable()
                if self.patrol_type == "med":
                    self.patrol_type = "general"
            if self.patrol_type == "general":
                text = "screens.patrol.random_patrol"
            elif self.patrol_type == "training":
                text = "screens.patrol.training"
            elif self.patrol_type == "border":
                text = "screens.patrol.border"
            elif self.patrol_type == "hunting":
                text = "screens.patrol.hunting"
            elif self.patrol_type == "med":
                if self.current_patrol:
                    text = "screens.patrol.herb_gathering"
                    self.elements["mouse"].disable()
                    self.elements["claws"].disable()
                    self.elements["paw"].disable()
                else:
                    text = "screens.patrol.herb_gathering"
            else:
                text = ""

            self.elements["info"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((0, 525), (175, -1))),
                starting_height=0,
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                anchors={"centerx": "centerx"},
            )

            able_no_med = [
                cat
                for cat in self.able_cats
                if not cat.status.rank.is_any_medicine_rank()
            ]
            if get_clan_setting("random med cat"):
                able_no_med = self.able_cats
            if len(able_no_med) == 0:
                able_no_med = self.able_cats
            if len(self.current_patrol) >= 6 or len(able_no_med) < 1:
                self.elements["add_one"].disable()
                self.elements["random"].disable()
            if len(self.current_patrol) > 3 or len(able_no_med) < 3:
                self.elements["add_three"].disable()
            if len(self.current_patrol) > 0 or len(able_no_med) < 6:
                self.elements["add_six"].disable()
                # Update the availability of the tab buttons
            if self.patrol_screen == "patrol_cats":
                self.elements["patrol_tab"].disable()
                self.elements["skills"].enable()
            elif self.patrol_screen == "skills":
                self.elements["patrol_tab"].enable()
                self.elements["skills"].disable()

            if self.patrol_screen == "patrol_cats":
                self.elements["patrol_tab"].disable()
                self.elements["skills"].enable()
            elif self.patrol_screen == "skills":
                self.elements["patrol_tab"].enable()
                self.elements["skills"].disable()

            if self.selected_cat != None:
                if (
                    "cycle_app_mentor_right_button" in self.elements
                    and "cycle_app_mentor_left_button" in self.elements
                ):
                    if (
                        self.selected_apprentice_index
                        == len(self.selected_cat.apprentice) - 1
                    ):
                        self.elements["cycle_app_mentor_right_button"].disable()
                    else:
                        self.elements["cycle_app_mentor_left_button"].enable()

                    if self.selected_apprentice_index == 0:
                        self.elements["cycle_app_mentor_left_button"].disable()
                    else:
                        self.elements["cycle_app_mentor_left_button"].enable()

                    if self.selected_cat.mentor != None:
                        self.elements["cycle_app_mentor_left_button"].hide()
                        self.elements["cycle_app_mentor_right_button"].hide()

                if (
                    "cycle_mate_right_button" in self.elements
                    and "cycle_mate_left_button" in self.elements
                ):
                    if self.selected_mate_index == len(self.selected_cat.mate) - 1:
                        self.elements["cycle_mate_right_button"].disable()
                    else:
                        self.elements["cycle_mate_left_button"].enable()

                    if self.selected_mate_index == 0:
                        self.elements["cycle_mate_left_button"].disable()
                    else:
                        self.elements["cycle_mate_left_button"].enable()

                    if len(self.selected_cat.mate) <= 0:
                        self.elements["cycle_mate_left_button"].hide()
                        self.elements["cycle_mate_right_button"].hide()

    def open_choose_cats_screen(self):
        """Opens the choose-cat patrol stage."""
        self.clear_page()  # Clear the page
        self.clear_cat_buttons()
        self.patrol_obj = Patrol()

        self.display_text = ""
        self.results_text = ""
        self.current_patrol = []
        self.current_page = 1
        self.patrol_stage = "choose_cats"
        self.patrol_screen = "patrol_cats"  # List

        self.elements["info"] = pygame_gui.elements.UITextBox(
            "screens.patrol.choose_cats_info",
            ui_scale(pygame.Rect((187, 95), (425, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
        )
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((300, 165), (200, 275))),
            get_box(BoxStyles.FRAME, (200, 275)),
            manager=MANAGER,
        )
        self.elements["cat_frame"].disable()

        # Frames
        self.elements["able_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 490), (270, 171))),
            get_box(BoxStyles.ROUNDED_BOX, (270, 171)),
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["able_frame"].disable()

        label_pos = ui_scale(pygame.Rect((0, 0), (270, 30)))
        label_pos.bottomleft = ui_scale_dimensions((40, 0))
        self.elements["able_label"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((40, 460), (270, 30))),
            "screens.patrol.able_cats_label",
            {
                "normal": get_button_dict(ButtonStyles.HORIZONTAL_TAB, (100, 30))[
                    "disabled"
                ]
            },
            object_id="@buttonstyles_horizontal_tab",
            anchors={
                "bottom_target": self.elements["able_frame"],
            },
        )

        self.elements["patrol_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((490, 490), (270, 140))),
            get_box(BoxStyles.ROUNDED_BOX, (270, 140)),
            manager=MANAGER,
        )
        self.elements["patrol_frame"].disable()

        # Buttons
        self.elements["add_remove_cat"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 460), (98, 30))),
            "buttons.add_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (98, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )
        # No cat is selected when the screen is opened, so the button is disabled
        self.elements["add_remove_cat"].disable()

        # Randomizing buttons
        self.elements["random"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((323, 495), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            sound_id="dice_roll",
            manager=MANAGER,
        )
        self.elements["add_one"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((363, 495), (34, 34))),
            "+1",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_rounded_rect",
            sound_id="dice_roll",
            manager=MANAGER,
        )
        self.elements["add_three"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((403, 495), (34, 34))),
            "+3",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_rounded_rect",
            sound_id="dice_roll",
            manager=MANAGER,
        )
        self.elements["add_six"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((443, 495), (34, 34))),
            "+6",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_rounded_rect",
            sound_id="dice_roll",
            manager=MANAGER,
        )

        # patrol type buttons - disabled for now
        self.elements["paw"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((323, 560), (34, 34))),
            Icon.PAW,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.elements["paw"].disable()
        self.elements["mouse"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((363, 560), (34, 34))),
            Icon.MOUSE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.elements["mouse"].disable()
        self.elements["claws"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((403, 560), (34, 34))),
            Icon.SCRATCHES,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.elements["claws"].disable()
        self.elements["herb"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((443, 560), (34, 34))),
            Icon.HERB,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.elements["herb"].disable()

        # Able cat page buttons
        self.elements["last_page"] = UIImageButton(
            ui_scale(pygame.Rect((75, 462), (34, 34))),
            "",
            object_id="#patrol_last_page",
            starting_height=2,
            manager=MANAGER,
        )
        self.elements["next_page"] = UIImageButton(
            ui_scale(pygame.Rect((241, 462), (34, 34))),
            "",
            object_id="#patrol_next_page",
            starting_height=2,
            manager=MANAGER,
        )

        # Tabs for the current patrol
        tab_rect = ui_scale(pygame.Rect((0, 0), (80, 35)))
        tab_rect.bottomleft = ui_scale_dimensions((505, 4))
        self.elements["patrol_tab"] = UISurfaceImageButton(
            tab_rect,
            "screens.patrol.patrol_label",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (80, 35)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            manager=MANAGER,
            anchors={
                "bottom": "bottom",
                "left": "left",
                "bottom_target": self.elements["patrol_frame"],
            },
        )
        self.elements["patrol_tab"].disable()  # We start on the patrol_cats_tab

        tab_rect = ui_scale(pygame.Rect((0, 0), (154, 35)))
        tab_rect.bottomleft = ui_scale_dimensions((590, 4))
        self.elements["skills"] = UISurfaceImageButton(
            tab_rect,
            "screens.patrol.skills_traits_label",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (154, 35)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            manager=MANAGER,
            anchors={
                "bottom": "bottom",
                "left": "left",
                "bottom_target": self.elements["patrol_frame"],
            },
        )
        del tab_rect

        # Remove all button
        self.elements["remove_all"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((560, -4), (124, 35))),
            "screens.patrol.remove_all_label",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB_MIRRORED, (124, 35)),
            starting_height=2,
            object_id="@buttonstyles_horizontal_tab_mirrored",
            manager=MANAGER,
            anchors={"left": "left", "top_target": self.elements["patrol_frame"]},
        )

        # Text box for skills and traits. Hidden for now, and with no text in it
        self.elements["skills_box"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((510, 510), (240, 90))),
            visible=False,
            object_id="#text_box_22_horizcenter_spacing_95",
            manager=MANAGER,
        )

        # Start Patrol Button
        self.elements["patrol_start"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 600), (135, 30))),
            "screens.patrol.go_on_patrol",
            get_button_dict(ButtonStyles.SQUOVAL, (135, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )
        self.elements["patrol_start"].disable()

        # add prey information
        if game.clan.game_mode != "classic":
            current_amount = round(game.clan.freshkill_pile.total_amount, 2)
            self.elements["current_prey"] = pygame_gui.elements.UITextBox(
                "screens.patrol.current_prey",
                ui_scale(pygame.Rect((300, 630), (200, 400))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                text_kwargs={"prey": str(current_amount)},
            )
            needed_amount = round(game.clan.freshkill_pile.amount_food_needed(), 2)
            self.elements["needed_prey"] = pygame_gui.elements.UITextBox(
                "screens.patrol.needed_prey",
                ui_scale(pygame.Rect((300, 647), (200, 400))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                text_kwargs={"prey": str(needed_amount)},
            )
        self.update_cat_images_buttons()
        self.update_button()

    def run_patrol_start(self):
        """Runs patrol start. To be run in a separate thread."""
        try:
            self.display_text = self.patrol_obj.setup_patrol(
                self.current_patrol, self.patrol_type
            )
        except RuntimeError:
            self.display_text = None

    def open_patrol_event_screen(self):
        """Open the patrol event screen. This sets up the patrol starting"""
        self.clear_page()
        self.clear_cat_buttons()
        self.patrol_stage = "patrol_events"

        if self.display_text is None:
            # No patrol events were found.
            self.change_screen("camp screen")
            return

        # Layout images
        self.elements["event_bg"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((381, 165), (354, 270))),
            get_box(BoxStyles.ROUNDED_BOX, (354, 270), sides=(True, True, True, False)),
            manager=MANAGER,
        )
        self.elements["event_bg"].disable()
        self.elements["info_bg"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((90, 456), (420, 204))),
            pygame.transform.scale(
                pygame.image.load("resources/images/patrol_info.png").convert_alpha(),
                ui_scale_dimensions((420, 204)),
            ),
            manager=MANAGER,
        )
        self.elements["image_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((65, 140), (320, 320))),
            get_box(BoxStyles.FRAME, (320, 320)),
            manager=MANAGER,
        )
        self.elements["intro_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((75, 150), (300, 300))),
            (
                pygame.transform.scale(
                    self.patrol_obj.get_patrol_art().premul_alpha(),
                    ui_scale_dimensions((300, 300)),
                )
                if game_setting_get("no sprite antialiasing")
                else pygame.transform.smoothscale(
                    self.patrol_obj.get_patrol_art().premul_alpha(),
                    ui_scale_dimensions((300, 300)),
                )
            ),
        )

        # Prepare Intro Text
        # adjusting text for solo patrols
        # intro_text = adjust_patrol_text(intro_text, self.patrol_obj)
        self.elements["patrol_text"] = pygame_gui.elements.UITextBox(
            self.display_text,
            ui_scale(pygame.Rect((385, 172), (335, 250))),
            object_id="#text_box_30_horizleft_pad_10_10_spacing_95",
            manager=MANAGER,
        )
        # Patrol Info
        # TEXT CATEGORIES AND CHECKING FOR REPEATS
        members = []
        skills = []
        traits = []
        for x in self.patrol_obj.patrol_cats:
            if x != self.patrol_obj.patrol_leader:
                members.append(str(x.name))
        for x in self.patrol_obj.patrol_cats:
            if x.personality.trait not in traits:
                traits.append(x.personality.trait)

            if x.skills.primary and x.skills.primary.get_short_skill() not in skills:
                skills.append(x.skills.primary.get_short_skill())

            if (
                x.skills.secondary
                and x.skills.secondary.get_short_skill() not in skills
            ):
                skills.append(x.skills.secondary.get_short_skill())

        self.elements["patrol_info"] = pygame_gui.elements.UITextBox(
            "screens.patrol.label_patrol_info",
            ui_scale(pygame.Rect((105, 460), (240, 200))),
            object_id="#text_box_22_horizleft",
            manager=MANAGER,
            text_kwargs={
                "leader": str(self.patrol_obj.patrol_leader.name),
                "p_l": self.patrol_obj.patrol_leader,
                "members": self.get_list_text(members),
                "patrol_cats": members,
                "skills": self.get_list_text(skills),
                "traits": self.get_list_text(traits),
            },
        )

        # Draw Patrol Cats
        pos_x = 400
        pos_y = 475
        for u in range(6):
            if u < len(self.patrol_obj.patrol_cats):
                self.elements["cat" + str(u)] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                    self.patrol_obj.patrol_cats[u].sprite,
                    manager=MANAGER,
                )
                pos_x += 50
                if pos_x > 450:
                    pos_y += 50
                    pos_x = 400
            else:
                break

        ##################### Buttons:
        self.elements["proceed"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((550, 433), (172, 30))),
            "screens.patrol.proceed",
            get_button_dict(ButtonStyles.DROPDOWN, (172, 30)),
            object_id="@buttonstyles_dropdown",
            starting_height=2,
            manager=MANAGER,
        )
        self.elements["not_proceed"] = UIImageButton(
            ui_scale(pygame.Rect((550, 461), (172, 30))),
            "screens.patrol.dont_proceed",
            object_id="#not_proceed_button",
            starting_height=2,
            manager=MANAGER,
        )

        self.elements["antagonize"] = UIImageButton(
            ui_scale(pygame.Rect((550, 490), (172, 36))),
            "screens.patrol.antagonize",
            object_id="#antagonize_button",
            sound_id="antagonize",
            manager=MANAGER,
        )
        if not self.patrol_obj.patrol_event.antag_success_outcomes:
            self.elements["antagonize"].hide()

    def run_patrol_proceed(self, user_input):
        """Proceeds the patrol - to be run in the separate thread."""
        if user_input in ["nopro", "notproceed"]:
            (
                self.display_text,
                self.results_text,
                self.outcome_art,
            ) = self.patrol_obj.proceed_patrol("decline")
        elif user_input in ["antag", "antagonize"]:
            (
                self.display_text,
                self.results_text,
                self.outcome_art,
            ) = self.patrol_obj.proceed_patrol("antag")
        else:
            (
                self.display_text,
                self.results_text,
                self.outcome_art,
            ) = self.patrol_obj.proceed_patrol("proceed")

    def open_patrol_complete_screen(self):
        """Deals with the next stage of the patrol, including antagonize, proceed, and do not proceed.
        You must put the type of next step (user input) into the user_input parameter.
        For antagonize: user_input = "antag" or "antagonize"
        For Proceed: user_input = "pro" or "proceed"
        For do not Proceed: user_input = "nopro" or "notproceed" """
        self.patrol_stage = "patrol_complete"

        self.elements["clan_return"] = UIImageButton(
            ui_scale(pygame.Rect((400, 137), (162, 30))),
            "screens.patrol.back_to_clan",
            object_id="#return_to_clan",
            manager=MANAGER,
        )
        self.elements["patrol_again"] = UIImageButton(
            ui_scale(pygame.Rect((560, 137), (162, 30))),
            "screens.patrol.patrol_again",
            object_id="#patrol_again",
            manager=MANAGER,
        )
        # Update patrol art, if needed.
        if (
            self.outcome_art is not None
            and self.elements.get("intro_image") is not None
        ):
            self.elements["intro_image"].set_image(self.outcome_art)

        self.elements["patrol_results"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((550, 500), (172, 150))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        self.elements["patrol_results"].set_text(self.results_text)

        self.elements["patrol_text"].set_text(self.display_text)

        self.elements["proceed"].disable()
        self.elements["not_proceed"].disable()
        self.elements["antagonize"].hide()

    def update_cat_images_buttons(self):
        """Updates all the cat sprite buttons. Also updates the skills tab, if open, and the next and
        previous page buttons."""
        self.clear_cat_buttons()  # Clear all the cat buttons

        self.able_cats = []

        # ASSIGN TO ABLE CATS
        for the_cat in Cat.all_cats_list:
            if (
                the_cat.in_camp
                and the_cat.ID not in game.patrolled
                and the_cat.status.rank.is_allowed_to_patrol()
                and the_cat.status.alive_in_player_clan
                and the_cat not in self.current_patrol
                and not the_cat.not_working()
            ):
                if (
                    the_cat.status.rank == CatRank.NEWBORN
                    or constants.CONFIG["fun"]["all_cats_are_newborn"]
                ):
                    if constants.CONFIG["fun"]["newborns_can_patrol"]:
                        self.able_cats.append(the_cat)
                else:
                    self.able_cats.append(the_cat)

        if not self.able_cats:
            all_pages = []
        else:
            all_pages = self.chunks(self.able_cats, 15)

        self.current_page = max(1, min(self.current_page, len(all_pages)))

        # Check for empty list (no able cats)
        if all_pages:
            display_cats = all_pages[self.current_page - 1]
        else:
            display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.elements["next_page"].disable()
            self.elements["last_page"].disable()
        else:
            if self.current_page >= len(all_pages):
                self.elements["next_page"].disable()
            else:
                self.elements["next_page"].enable()

            if self.current_page <= 1:
                self.elements["last_page"].disable()
            else:
                self.elements["last_page"].enable()

        # Draw able cats.
        pos_y = 500
        pos_x = 50
        i = 0
        for cat in display_cats:
            if get_clan_setting("show fav") and cat.favourite:
                self.fav[str(i)] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                    pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((50, 50)),
                    ),
                )
                self.fav[str(i)].disable()
            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                (
                    pygame.transform.scale(cat.sprite, ui_scale_dimensions((50, 50)))
                    if game_setting_get("no sprite antialiasing")
                    else pygame.transform.smoothscale(
                        cat.sprite, ui_scale_dimensions((50, 50))
                    )
                ),
                cat_object=cat,
                manager=MANAGER,
            )
            pos_x += 50
            if pos_x >= 300:
                pos_x = 50
                pos_y += 50
            i += 1

        if self.patrol_screen == "patrol_cats":
            # Hide Skills Info
            self.elements["skills_box"].hide()
            # Draw cats in patrol
            pos_y = 508
            pos_x = 525
            i = 0
            for cat in self.current_patrol:
                self.cat_buttons["patrol_cat" + str(i)] = UISpriteButton(
                    ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                    (
                        pygame.transform.scale(
                            cat.sprite, ui_scale_dimensions((50, 50))
                        )
                        if game_setting_get("no sprite antialiasing")
                        else pygame.transform.smoothscale(
                            cat.sprite, ui_scale_dimensions((50, 50))
                        )
                    ),
                    cat_object=cat,
                    manager=MANAGER,
                )
                pos_x += 75
                if pos_x >= 725:
                    pos_x = 525
                    pos_y += 50
                i += 1
        elif self.patrol_screen == "skills":
            self.update_skills_tab()

    def update_skills_tab(self):
        self.elements["skills_box"].show()
        patrol_skills = []
        patrol_traits = []
        if self.current_patrol is not []:
            for x in self.current_patrol:
                if (
                    x.skills.primary
                    and x.skills.primary.get_short_skill() not in patrol_skills
                ):
                    patrol_skills.append(x.skills.primary.get_short_skill())

                if (
                    x.skills.secondary
                    and x.skills.secondary.get_short_skill() not in patrol_skills
                ):
                    patrol_skills.append(x.skills.secondary.get_short_skill())

                if x.personality.trait not in patrol_traits:
                    patrol_traits.append(x.personality.trait)

        self.elements["skills_box"].set_text(
            "screens.patrol.current_patrol_info",
            text_kwargs={
                "skills": ", ".join(patrol_skills),
                "traits": ", ".join(patrol_traits),
            },
        )

    def update_selected_cat(self):
        """Refreshes the image displaying the selected cat, traits, mentor/apprentice/mate ext"""

        # Kill and delete all relevant elements
        if "selected_image" in self.elements:
            self.elements["selected_image"].kill()
            del self.elements["selected_image"]
        if "selected_name" in self.elements:
            self.elements["selected_name"].kill()
            del self.elements["selected_name"]
        if "selected_bio" in self.elements:
            self.elements["selected_bio"].kill()
            del self.elements["selected_bio"]

        # Kill mate frame, apprentice/mentor frame, and respective images, if they exist:
        if "mate_frame" in self.elements:
            self.elements["mate_frame"].kill()
            del self.elements["mate_frame"]  # No need to keep this in memory
        if "mate_image" in self.elements:
            self.elements["mate_image"].kill()
            del self.elements["mate_image"]  # No need to keep this in memory
        if "mate_name" in self.elements:
            self.elements["mate_name"].kill()
            del self.elements["mate_name"]  # No need to keep this in memory
        if "mate_info" in self.elements:
            self.elements["mate_info"].kill()
            del self.elements["mate_info"]
        if "mate_button" in self.elements:
            self.elements["mate_button"].kill()
            del self.elements["mate_button"]  # No need to keep this in memory
        if "app_mentor_frame" in self.elements:
            self.elements["app_mentor_frame"].kill()
            del self.elements["app_mentor_frame"]  # No need to keep this in memory
        if "app_mentor_image" in self.elements:
            self.elements["app_mentor_image"].kill()
            del self.elements["app_mentor_image"]  # No need to keep this in memory
        if "app_mentor_name" in self.elements:
            self.elements["app_mentor_name"].kill()
            del self.elements["app_mentor_name"]  # No need to keep this in memory
        if "app_mentor_button" in self.elements:
            self.elements["app_mentor_button"].kill()
            del self.elements["app_mentor_button"]  # No need to keep this in memory
        if "app_mentor_info" in self.elements:
            self.elements["app_mentor_info"].kill()
            del self.elements["app_mentor_info"]
        if "cycle_app_mentor_left_button" in self.elements:
            self.elements["cycle_app_mentor_left_button"].kill()
            del self.elements["cycle_app_mentor_left_button"]
        if "cycle_app_mentor_right_button" in self.elements:
            self.elements["cycle_app_mentor_right_button"].kill()
            del self.elements["cycle_app_mentor_right_button"]
        if "cycle_mate_left_button" in self.elements:
            self.elements["cycle_mate_left_button"].kill()
            del self.elements["cycle_mate_left_button"]
        if "cycle_mate_right_button" in self.elements:
            self.elements["cycle_mate_right_button"].kill()
            del self.elements["cycle_mate_right_button"]

        if self.selected_cat is not None:
            # Now, if the selected cat is not None, we rebuild everything with the correct cat info
            # Selected Cat Image
            self.elements["selected_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 175), (150, 150))),
                pygame.transform.scale(
                    self.selected_cat.sprite, ui_scale_dimensions((150, 150))
                ),
                manager=MANAGER,
                anchors={"centerx": "centerx"},
            )

            name = str(self.selected_cat.name)  # get name
            short_name = shorten_text_to_fit(name, 172, 15)

            self.elements["selected_name"] = pygame_gui.elements.UITextBox(
                short_name,
                ui_scale(pygame.Rect((0, 0), (200, 34))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                anchors={
                    "top_target": self.elements["selected_image"],
                    "centerx": "centerx",
                },
            )

            self.elements["selected_bio"] = pygame_gui.elements.UITextBox(
                self.selected_cat.get_info_block(patrol=True),
                ui_scale(pygame.Rect((0, -5), (190, 110))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                manager=MANAGER,
                anchors={
                    "top_target": self.elements["selected_name"],
                    "centerx": "centerx",
                },
            )

            # Show Cat's Mate, if they have one
            if len(self.selected_cat.mate) > 0:
                if self.selected_mate_index > len(self.selected_cat.mate) - 1:
                    self.selected_mate_index = 0
                self.mate = Cat.fetch_cat(
                    self.selected_cat.mate[self.selected_mate_index]
                )
                self.elements["mate_frame"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((140, 190), (166, 170))), self.mate_frame
                )
                self.elements["mate_image"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((150, 200), (100, 100))),
                    pygame.transform.scale(
                        self.mate.sprite, ui_scale_dimensions((100, 100))
                    ),
                    manager=MANAGER,
                )
                # Check for name length
                name = str(self.mate.name)  # get name
                if 10 <= len(name):  # check name length
                    short_name = name[0:9]
                    name = short_name + ".."
                self.elements["mate_name"] = pygame_gui.elements.ui_label.UILabel(
                    ui_scale(pygame.Rect((153, 300), (95, 30))),
                    name,
                    object_id=get_text_box_theme(),
                )
                self.elements["mate_info"] = pygame_gui.elements.UITextBox(
                    "general.mate",
                    ui_scale(pygame.Rect((150, 325), (100, 30))),
                    object_id=get_text_box_theme("#text_box_22_horizcenter"),
                    text_kwargs={"count": 1},
                )
                self.elements["mate_button"] = UIImageButton(
                    ui_scale(pygame.Rect((148, -4), (104, 26))),
                    (
                        "screens.patrol.select"
                        if self.mate in self.able_cats
                        else "screens.patrol.unavailable"
                    ),
                    object_id="#patrol_select_button",
                    manager=MANAGER,
                    anchors={"top_target": self.elements["mate_frame"]},
                )
                # Disable mate_button if the cat is not able to go on a patrol
                if self.mate not in self.able_cats:
                    self.elements["mate_button"].disable()

                # Buttons to cycle between mates
                if len(self.selected_cat.mate) > 1:
                    self.elements["cycle_mate_left_button"] = UISurfaceImageButton(
                        ui_scale(pygame.Rect((148, 390), (34, 34))),
                        Icon.ARROW_LEFT,
                        get_button_dict(ButtonStyles.ICON, (34, 34)),
                        object_id="@buttonstyles_icon",
                        manager=MANAGER,
                    )
                    self.elements["cycle_mate_right_button"] = UISurfaceImageButton(
                        ui_scale(pygame.Rect((218, 390), (34, 34))),
                        Icon.ARROW_RIGHT,
                        get_button_dict(ButtonStyles.ICON, (34, 34)),
                        object_id="@buttonstyles_icon",
                        manager=MANAGER,
                    )
                    self.update_button()

            # Draw mentor or apprentice
            relation = "should not display"
            if (
                self.selected_cat.status.rank
                in [CatRank.MEDICINE_APPRENTICE, CatRank.APPRENTICE]
                or self.selected_cat.apprentice != []
            ):
                self.elements["app_mentor_frame"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((495, 190), (166, 170))),
                    self.app_frame,
                    manager=MANAGER,
                )

                if (
                    self.selected_cat.status.rank
                    in [CatRank.MEDICINE_APPRENTICE, CatRank.APPRENTICE]
                    and self.selected_cat.mentor is not None
                ):
                    self.app_mentor = Cat.fetch_cat(self.selected_cat.mentor)
                    relation = "general.mentor"

                elif self.selected_cat.apprentice:
                    if (
                        self.selected_apprentice_index
                        > len(self.selected_cat.apprentice) - 1
                    ):
                        self.selected_apprentice_index = 0
                    self.app_mentor = Cat.fetch_cat(
                        self.selected_cat.apprentice[self.selected_apprentice_index]
                    )
                    relation = "general.apprentice"
                else:
                    self.app_mentor = None
                    self.elements["app_mentor_frame"].hide()

                # Failsafe, if apprentice or mentor is set to none.
                if self.app_mentor is not None:
                    name = str(self.app_mentor.name)  # get name
                    if 10 <= len(name):  # check name length
                        short_name = name[0:9]
                        name = short_name + ".."
                    self.elements[
                        "app_mentor_name"
                    ] = pygame_gui.elements.ui_label.UILabel(
                        ui_scale(pygame.Rect((553, 300), (95, 30))),
                        name,
                        object_id=get_text_box_theme(),
                        manager=MANAGER,
                    )
                    self.elements["app_mentor_info"] = pygame_gui.elements.UITextBox(
                        relation,
                        ui_scale(pygame.Rect((550, 325), (100, 30))),
                        object_id=get_text_box_theme("#text_box_22_horizcenter"),
                        text_kwargs={"count": 1},
                    )
                    self.elements["app_mentor_image"] = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((550, 200), (100, 100))),
                        pygame.transform.scale(
                            self.app_mentor.sprite, ui_scale_dimensions((100, 100))
                        ),
                        manager=MANAGER,
                    )

                    # Button to switch to that cat
                    self.elements["app_mentor_button"] = UIImageButton(
                        ui_scale(pygame.Rect((548, -4), (104, 26))),
                        (
                            "screens.patrol.select"
                            if self.app_mentor in self.able_cats
                            else "screens.patrol.unavailable"
                        ),
                        object_id="#patrol_select_button",
                        manager=MANAGER,
                        anchors={"top_target": self.elements["app_mentor_frame"]},
                    )
                    # Disable mate_button if the cat is not able to go on a patrol
                    if self.app_mentor not in self.able_cats:
                        self.elements["app_mentor_button"].disable()

                    # Buttons to cycle between apprentices
                    if self.selected_cat.mentor == None:
                        self.elements[
                            "cycle_app_mentor_left_button"
                        ] = UISurfaceImageButton(
                            ui_scale(pygame.Rect((548, 390), (34, 34))),
                            Icon.ARROW_LEFT,
                            get_button_dict(ButtonStyles.ICON, (34, 34)),
                            object_id="@buttonstyles_icon",
                        )
                        self.elements[
                            "cycle_app_mentor_right_button"
                        ] = UISurfaceImageButton(
                            ui_scale(pygame.Rect((618, 390), (34, 34))),
                            Icon.ARROW_RIGHT,
                            get_button_dict(ButtonStyles.ICON, (34, 34)),
                            object_id="@buttonstyles_icon",
                            manager=MANAGER,
                        )
                        self.update_button()

    def clear_page(self):
        """Clears all the elements"""
        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        self.cat_buttons = {}
        for marker in self.fav:
            self.fav[marker].kill()
        self.fav = {}

    def exit_screen(self):
        self.in_progress_data = self.display_change_save()
        self.clear_page()
        self.clear_cat_buttons()
        self.hide_menu_buttons()

    def on_use(self):
        super().on_use()

        self.loading_screen_on_use(
            self.start_patrol_thread, self.open_patrol_event_screen
        )
        self.loading_screen_on_use(
            self.proceed_patrol_thread, self.open_patrol_complete_screen
        )

    @staticmethod
    def chunks(L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    @staticmethod
    def get_list_text(patrol_list):
        if not patrol_list:
            return i18n.t("general.none").capitalize()
        # Removes duplicates.
        patrol_set = list(patrol_list)
        return ", ".join(patrol_set)
