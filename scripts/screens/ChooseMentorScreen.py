from typing import Dict, Optional

import i18n
import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    ui_scale_dimensions,
    shorten_text_to_fit,
)
from .Screens import Screens
from ..game_structure.game.switches import switch_set_value, switch_get_value, Switch
from ..cat.enums import CatRank
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


class ChooseMentorScreen(Screens):
    selected_mentor: Optional[Cat] = None
    current_page = 1
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.list_frame = None
        self.list_page = None
        self.next_cat = None
        self.previous_cat = None
        self.next_page_button = None
        self.previous_page_button = None
        self.current_mentor_warning = None
        self.no_mentor_warning = None
        self.confirm_mentor = None
        self.remove_mentor = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.mentor_icon = None
        self.app_frame = None
        self.mentor_frame = None
        self.current_mentor_text = None
        self.info = None
        self.heading = None
        self.mentor = None
        self.the_cat = None
        self.show_only_no_current_app_mentors = False
        self.show_only_no_former_app_mentors = False
        self.filter_container = None
        self.filter_seperator = None
        self.checkboxes = {}
        self.no_current_app_text = None
        self.no_former_app_text = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element in self.cat_list_buttons.values():
                self.selected_mentor = event.ui_element.return_cat_object()
                self.update_selected_cat()
                self.update_buttons()
            elif event.ui_element == self.confirm_mentor:
                self.change_mentor(self.selected_mentor)
                self.update_buttons()
                self.update_selected_cat()
            elif event.ui_element == self.remove_mentor:
                self.change_mentor(self.selected_mentor)
                self.update_buttons()
                self.update_selected_cat()
            elif event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_apprentice()
                    self.update_cat_list()
                    self.update_selected_cat()
                    self.update_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_apprentice()
                    self.update_cat_list()
                    self.update_selected_cat()
                    self.update_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()
            elif event.ui_element == self.checkboxes["show_no_current_app"]:
                self.show_only_no_current_app_mentors = (
                    not self.show_only_no_current_app_mentors
                )
                self.update_buttons()
                self.update_cat_list()
            elif event.ui_element == self.checkboxes.get("show_no_former_app"):
                self.show_only_no_former_app_mentors = (
                    not self.show_only_no_former_app_mentors
                )
                self.update_buttons()
                self.update_cat_list()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)

        self.heading = pygame_gui.elements.UITextBox(
            "Choose a new mentor for " + str(self.the_cat.name),
            ui_scale(pygame.Rect((150, 25), (500, 40))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            manager=MANAGER,
        )
        self.info = pygame_gui.elements.UITextBox(
            "screens.choose_mentor.info",
            ui_scale(pygame.Rect((180, 52), (440, 92))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        self.current_mentor_text = pygame_gui.elements.UITextBox(
            "screens.choose_mentor.current_mentor",
            ui_scale(pygame.Rect((230, 130), (340, 30))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
            text_kwargs={
                "count": 1 if self.mentor is not None else 0,
                "m_c": self.the_cat,
                "r_c": self.mentor if self.mentor else None,
            },
        )

        # Layout Images:
        list_frame = get_box(BoxStyles.ROUNDED_BOX, (650, 226))
        self.list_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((75, 360), (650, 226))), list_frame, starting_height=1
        )

        self.mentor_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 113), (281, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat1_frame_ment.png"
                ).convert_alpha(),
                (562, 394),
            ),
            manager=MANAGER,
        )
        self.app_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((480, 113), (281, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_ment.png"
                ).convert_alpha(),
                (562, 394),
            ),
            manager=MANAGER,
        )

        self.mentor_icon = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((315, 160), (171, 114))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/mentor.png").convert_alpha(),
                (343, 228),
            ),
            manager=MANAGER,
        )

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.confirm_mentor = UISurfaceImageButton(
            ui_scale(pygame.Rect((326, 310), (148, 30))),
            "screens.choose_mentor.set_mentor",
            get_button_dict(ButtonStyles.SQUOVAL, (148, 30)),
            object_id="@buttonstyles_squoval",
        )
        self.remove_mentor = UISurfaceImageButton(
            ui_scale(pygame.Rect((326, 310), (148, 30))),
            "screens.choose_mentor.unset_mentor",
            get_button_dict(ButtonStyles.SQUOVAL, (148, 30)),
            object_id="@buttonstyles_squoval",
        )
        self.current_mentor_warning = pygame_gui.elements.UITextBox(
            "screens.choose_mentor.current_mentor_warning",
            ui_scale(pygame.Rect((300, 335), (200, 30))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_red"),
            manager=MANAGER,
        )
        self.no_mentor_warning = pygame_gui.elements.UITextBox(
            "screens.choose_mentor.no_mentor_warning",
            ui_scale(pygame.Rect((300, 335), (200, 30))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
        )

        self.previous_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((315, 579), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=0,
        )
        self.next_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((451, 579), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=0,
        )

        # Create a container for the checkboxes
        self.filter_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((85, 360), (630, 226))), manager=MANAGER
        )

        # Add a vertical separator
        self.filter_seperator = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((497, 7), (10, 210))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                ui_scale_dimensions((10, 210)),
            ),
            container=self.filter_container,
        )

        # Reposition and style checkboxes and labels
        checkbox_x = 553
        checkbox_y = 7
        checkbox_spacing = 50

        self.no_current_app_text = pygame_gui.elements.UITextBox(
            "screens.choose_mentor.no_current_apprentices",
            ui_scale(pygame.Rect((checkbox_x - 45, checkbox_y + 10), (100, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.filter_container,
        )
        checkbox_y += checkbox_spacing
        self.checkboxes["show_no_current_app"] = UIImageButton(
            ui_scale(pygame.Rect((checkbox_x, checkbox_y + 10), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            container=self.filter_container,
            tool_tip_text="screens.choose_mentor.no_current_apprentices_tooltip",
        )
        checkbox_y += checkbox_spacing

        self.no_former_app_text = pygame_gui.elements.UITextBox(
            "screens.choose_mentor.no_former_apprentices",
            ui_scale(pygame.Rect((checkbox_x - 45, checkbox_y), (100, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.filter_container,
        )
        checkbox_y += checkbox_spacing
        self.checkboxes["show_no_former_app"] = UIImageButton(
            ui_scale(pygame.Rect((checkbox_x, checkbox_y), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            container=self.filter_container,
            tool_tip_text="screens.choose_mentor.no_former_apprentices_tooltip",
        )
        self.update_apprentice()  # Draws the current apprentice
        self.update_selected_cat()  # Updates the image and details of selected cat
        self.update_cat_list()
        self.update_buttons()

    def display_change_save(self) -> Dict:
        variable_dict = super().display_change_save()

        variable_dict["selected_mentor"] = self.selected_mentor
        variable_dict[
            "show_only_no_current_app_mentors"
        ] = self.show_only_no_current_app_mentors
        variable_dict[
            "show_only_no_former_app_mentors"
        ] = self.show_only_no_former_app_mentors

        variable_dict["current_page"] = self.current_page

        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        for key, value in variable_dict.items():
            try:
                setattr(self, key, value)
            except KeyError:
                continue

        self.update_buttons()
        self.update_selected_cat()

    def exit_screen(self):
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}

        self.list_frame.kill()
        self.heading.kill()
        del self.heading
        self.info.kill()
        del self.info
        self.current_mentor_text.kill()
        del self.current_mentor_text
        self.mentor_frame.kill()
        del self.mentor_frame
        self.mentor_icon.kill()
        del self.mentor_icon
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.confirm_mentor.kill()
        del self.confirm_mentor
        self.remove_mentor.kill()
        del self.remove_mentor
        self.current_mentor_warning.kill()
        del self.current_mentor_warning
        self.no_mentor_warning.kill()
        del self.no_mentor_warning
        self.previous_page_button.kill()
        del self.previous_page_button
        self.next_page_button.kill()
        del self.next_page_button
        self.app_frame.kill()
        del self.app_frame
        self.filter_container.kill()
        del self.filter_container
        self.no_current_app_text.kill()
        del self.no_current_app_text
        self.no_former_app_text.kill()
        del self.no_former_app_text
        self.checkboxes["show_no_current_app"].kill()
        del self.checkboxes["show_no_current_app"]
        self.checkboxes["show_no_former_app"].kill()
        del self.checkboxes["show_no_former_app"]

    def update_apprentice(self):
        """Updates the apprentice focused on."""
        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        self.current_page = 1
        self.selected_mentor = Cat.fetch_cat(self.the_cat.mentor)
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)

        self.heading.set_text(
            "screens.choose_mentor.heading",
            text_kwargs={"m_c": self.the_cat},
        )
        self.current_mentor_text.set_text(
            "screens.choose_mentor.current_mentor",
            text_kwargs={
                "count": 1 if self.mentor is not None else 0,
                "m_c": self.the_cat,
                "r_c": self.mentor if self.mentor else None,
            },
        )
        self.apprentice_details["apprentice_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((600, 150), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        self.apprentice_details["apprentice_info"] = pygame_gui.elements.UITextBox(
            self.the_cat.get_info_block(),
            ui_scale(pygame.Rect((490, 162), (105, 125))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 115, 17)
        self.apprentice_details[
            "apprentice_name"
        ] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((620, 115), (117, 32))),
            short_name,
            object_id="#text_box_34_horizcenter",
            manager=MANAGER,
        )

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats(
            filter_func=(lambda cat: cat.status.rank.is_any_apprentice_rank())
        )

        (
            self.next_cat_button.disable()
            if self.next_cat == 0
            else self.next_cat_button.enable()
        )
        (
            self.previous_cat_button.disable()
            if self.previous_cat == 0
            else self.previous_cat_button.enable()
        )

    def change_mentor(self, new_mentor=None):
        old_mentor = Cat.fetch_cat(self.the_cat.mentor)
        if new_mentor == old_mentor:
            # if "changing mentor" to the same cat, remove them as mentor instead
            if (
                self.the_cat.moons > 6
                and self.the_cat.ID not in old_mentor.former_apprentices
            ):
                old_mentor.former_apprentices.append(self.the_cat.ID)
            self.the_cat.mentor = None
            old_mentor.apprentice.remove(self.the_cat.ID)
            self.mentor = None
        elif new_mentor and old_mentor is not None:
            old_mentor.apprentice.remove(self.the_cat.ID)
            if (
                self.the_cat.moons > 6
                and self.the_cat.ID not in old_mentor.former_apprentices
            ):
                old_mentor.former_apprentices.append(self.the_cat.ID)

            self.the_cat.patrol_with_mentor = 0
            self.the_cat.mentor = new_mentor.ID
            new_mentor.apprentice.append(self.the_cat.ID)
            self.mentor = new_mentor

            # They are a current apprentice, not a former one now!
            if self.the_cat.ID in new_mentor.former_apprentices:
                new_mentor.former_apprentices.remove(self.the_cat.ID)

        elif new_mentor:
            self.the_cat.mentor = new_mentor.ID
            new_mentor.apprentice.append(self.the_cat.ID)
            self.mentor = new_mentor
            if self.the_cat.ID not in new_mentor.former_apprentices:
                self.the_cat.patrol_with_mentor = 0

            # They are a current apprentice, not a former one now!
            if self.the_cat.ID in new_mentor.former_apprentices:
                new_mentor.former_apprentices.remove(self.the_cat.ID)

        self.current_mentor_text.set_text(
            "screens.choose_mentor.current_mentor",
            text_kwargs={
                "count": 1 if self.mentor is not None else 0,
                "m_c": self.the_cat,
                "r_c": self.mentor if self.mentor else None,
            },
        )

    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_mentor:
            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((50, 150), (150, 150))),
                pygame.transform.scale(
                    self.selected_mentor.sprite, ui_scale_dimensions((150, 150))
                ),
                manager=MANAGER,
            )

            info = self.selected_mentor.get_info_block()
            info += i18n.t(
                "screens.choose_mentor.former_apps",
                count=len(self.selected_mentor.former_apprentices),
            )
            info += i18n.t(
                "screens.choose_mentor.current_apps",
                count=len(self.selected_mentor.apprentice),
            )
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(
                info,
                ui_scale(pygame.Rect((210, 162), (105, 125))),
                object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                manager=MANAGER,
            )

            name = str(self.selected_mentor.name)  # get name
            short_name = shorten_text_to_fit(name, 239, 17)
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((65, 115), (117, 32))),
                short_name,
                object_id="#text_box_34_horizcenter",
                manager=MANAGER,
            )

    def update_cat_list(self):
        """Updates the cat sprite buttons."""
        valid_mentors = self.chunks(self.get_valid_mentors(), 24)

        # clamp current page to a valid page number
        self.current_page = max(1, min(self.current_page, len(valid_mentors)))

        # Handle which next buttons are clickable.
        if len(valid_mentors) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(valid_mentors):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(valid_mentors) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()
        display_cats = []
        if valid_mentors:
            display_cats = valid_mentors[self.current_page - 1]

        # Kill all the currently displayed cats.
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        pos_x = 0
        pos_y = 20
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((100 + pos_x, 365 + pos_y), (50, 50))),
                cat.sprite,
                cat_object=cat,
                manager=MANAGER,
            )
            pos_x += 60
            if pos_x >= 450:
                pos_x = 0
                pos_y += 60
            i += 1

    def update_buttons(self):
        """Updates the status of buttons."""
        # Disable to enable the choose mentor button
        if not self.selected_mentor:
            self.remove_mentor.hide()
            self.remove_mentor.disable()
            self.confirm_mentor.show()
            self.confirm_mentor.disable()
            self.current_mentor_warning.hide()
            self.no_mentor_warning.show()
        elif self.selected_mentor.ID == self.the_cat.mentor:
            self.confirm_mentor.hide()
            self.remove_mentor.show()
            self.remove_mentor.enable()
            self.current_mentor_warning.show()
            self.no_mentor_warning.hide()
        else:
            self.remove_mentor.hide()
            self.remove_mentor.disable()
            self.confirm_mentor.show()
            self.confirm_mentor.enable()
            self.current_mentor_warning.hide()
            self.no_mentor_warning.hide()

        # Update checkboxes
        checkboxes = [
            (
                "show_no_current_app",
                self.checkboxes["show_no_current_app"],
                self.show_only_no_current_app_mentors,
            ),
            (
                "show_no_former_app",
                self.checkboxes["show_no_former_app"],
                self.show_only_no_former_app_mentors,
            ),
        ]
        for name, checkbox, is_checked in checkboxes:
            checkbox.kill()
            theme = "@checked_checkbox" if is_checked else "@unchecked_checkbox"
            self.checkboxes[name] = UIImageButton(
                relative_rect=checkbox.relative_rect,
                text="",
                object_id=theme,
                container=self.filter_container,
                tool_tip_text=checkbox.tool_tip_text,
            )

    def get_valid_mentors(self):
        potential_warrior_mentors = [
            cat
            for cat in Cat.all_cats_list
            if cat.status.alive_in_player_clan
            and cat.status.rank.is_any_adult_warrior_like_rank()
        ]
        valid_warrior_mentors = []
        potential_medcat_mentors = [
            cat
            for cat in Cat.all_cats_list
            if cat.status.alive_in_player_clan
            and cat.status.rank == CatRank.MEDICINE_CAT
        ]
        valid_medcat_mentors = []
        potential_mediator_mentors = [
            cat
            for cat in Cat.all_cats_list
            if cat.status.alive_in_player_clan and cat.status.rank == CatRank.MEDIATOR
        ]
        valid_mediator_mentors = []

        if self.the_cat.status.rank == CatRank.APPRENTICE:
            for cat in potential_warrior_mentors:
                # Assume cat is valid initially
                is_valid = True

                # Check for no former apprentices filter
                if self.show_only_no_former_app_mentors:
                    if cat.former_apprentices:
                        is_valid = False
                    elif cat.apprentice:
                        is_valid = False

                # Check for no current apprentices filter
                if self.show_only_no_current_app_mentors and cat.apprentice:
                    is_valid = False

                # Add to valid or invalid list based on checks
                if is_valid:
                    valid_warrior_mentors.append(cat)

            return valid_warrior_mentors

        elif self.the_cat.status.rank == CatRank.MEDICINE_APPRENTICE:
            for cat in potential_medcat_mentors:
                is_valid = True

                # Check no former apprentices filter
                if self.show_only_no_former_app_mentors and cat.former_apprentices:
                    is_valid = False

                # Check no current apprentices filter
                if self.show_only_no_current_app_mentors and cat.apprentice:
                    is_valid = False

                # Add to valid or invalid list based on checks
                if is_valid:
                    valid_medcat_mentors.append(cat)

            return valid_medcat_mentors

        elif self.the_cat.status.rank == CatRank.MEDIATOR_APPRENTICE:
            for cat in potential_mediator_mentors:
                # Assume cat is valid initially
                is_valid = True

                # Check for no former apprentices filter
                if self.show_only_no_former_app_mentors and cat.former_apprentices:
                    is_valid = False

                # Check for no current apprentices filter
                if self.show_only_no_current_app_mentors and cat.apprentice:
                    is_valid = False

                # Add to valid or invalid list based on checks
                if is_valid:
                    valid_mediator_mentors.append(cat)

            return potential_mediator_mentors
        return []

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blitted
        super().on_use()

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
