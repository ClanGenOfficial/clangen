import pygame.transform
import pygame_gui.elements

from .Screens import Screens

from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit, scale_dimentions
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import (
    game,
    screen,
    screen_x,
    screen_y,
    MANAGER,
)
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton
from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit
from .Screens import Screens


class ChooseMentorScreen(Screens):
    selected_mentor = None
    current_page = 1
    list_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
        (1300 / 1600 * screen_x, 452 / 1400 * screen_y),
    )
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
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
                    game.switches["cat"] = self.next_cat
                    self.update_apprentice()
                    self.update_cat_list()
                    self.update_selected_cat()
                    self.update_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
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
                self.show_only_no_current_app_mentors = not self.show_only_no_current_app_mentors
                self.update_buttons()
                self.update_cat_list()
            elif event.ui_element == self.checkboxes.get("show_no_former_app"):
                self.show_only_no_former_app_mentors = not self.show_only_no_former_app_mentors
                self.update_buttons()
                self.update_cat_list()

    def screen_switches(self):
        self.show_mute_buttons()
        self.the_cat = Cat.all_cats[game.switches["cat"]]
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)

        self.heading = pygame_gui.elements.UITextBox(
            "Choose a new mentor for " + str(self.the_cat.name),
            scale(pygame.Rect((300, 50), (1000, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            manager=MANAGER,
        )
        self.info = pygame_gui.elements.UITextBox(
            "If an apprentice is 6 moons old and their mentor is changed, they "
            "will not be listed as a former apprentice on their old mentor's "
            "profile. Apprentices without a mentor will have one automatically "
            "assigned next moon. An apprentice's mentor can have an influence on "
            "their trait and skill later in life.\nChoose your mentors wisely",
            scale(pygame.Rect((360, 105), (880, 185))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        if self.mentor is not None:
            self.current_mentor_text = pygame_gui.elements.UITextBox(
                f"{self.the_cat.name}'s current mentor is {self.mentor.name}",
                scale(pygame.Rect((460, 260), (680, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                manager=MANAGER,
            )
        else:
            self.current_mentor_text = pygame_gui.elements.UITextBox(
                f"{self.the_cat.name} does not have a mentor",
                scale(pygame.Rect((460, 260), (680, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                manager=MANAGER,
            )

        # Layout Images:
        self.mentor_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((80, 226), (562, 394))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat1_frame_ment.png"
                ).convert_alpha(),
                (562, 394),
            ),
            manager=MANAGER,
        )
        self.app_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((960, 226), (562, 394))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_ment.png"
                ).convert_alpha(),
                (562, 394),
            ),
            manager=MANAGER,
        )

        self.mentor_icon = pygame_gui.elements.UIImage(
            scale(pygame.Rect((630, 320), (343, 228))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/mentor.png").convert_alpha(),
                (343, 228),
            ),
            manager=MANAGER,
        )

        self.previous_cat_button = UIImageButton(
            scale(pygame.Rect((50, 50), (306, 60))),
            "",
            object_id="#previous_cat_button",
            sound_id="page_flip",
        )
        self.next_cat_button = UIImageButton(
            scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button", sound_id="page_flip",
        )
        self.back_button = UIImageButton(
            scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button"
        )
        self.confirm_mentor = UIImageButton(
            scale(pygame.Rect((652, 620), (296, 60))),
            "",
            object_id="#confirm_mentor_button",
        )
        self.remove_mentor = UIImageButton(
            scale(pygame.Rect((652, 620), (296, 60))),
            "",
            object_id="#remove_mentor_button",
        )
        self.current_mentor_warning = pygame_gui.elements.UITextBox(
            "Current mentor selected",
            scale(pygame.Rect((600, 670), (400, 60))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_red"),
            manager=MANAGER)
        self.no_mentor_warning = pygame_gui.elements.UITextBox(
            "<font color=#FF0000>No mentor selected</font>",
            scale(pygame.Rect((600, 670), (400, 60))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER)
        self.previous_page_button = UIImageButton(
            scale(pygame.Rect((630, 1158), (68, 68))),
            "",
            object_id="#relation_list_previous",
            manager=MANAGER
        )
        self.next_page_button = UIImageButton(
            scale(pygame.Rect((902, 1158), (68, 68))),
            "",
            object_id="#relation_list_next",
            manager=MANAGER
        )

        # Create a container for the checkboxes
        self.filter_container = pygame_gui.core.UIContainer(
            scale(pygame.Rect((170, 720), (1260, 452))),
            manager=MANAGER
        )

        # Add a vertical separator
        self.filter_seperator = pygame_gui.elements.UIImage(
            scale(pygame.Rect((995, 15), (20, 420))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                scale_dimentions((20, 420))
            ),
            container=self.filter_container
        )

        # Reposition and style checkboxes and labels
        checkbox_x = 1106
        checkbox_y = 15
        checkbox_spacing = 100

        self.no_current_app_text = pygame_gui.elements.UITextBox(
            "No current apprentices",
            scale(pygame.Rect((checkbox_x - 70, checkbox_y + 20), (200, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.filter_container
        )
        checkbox_y += checkbox_spacing
        self.checkboxes["show_no_current_app"] = UIImageButton(
            scale(pygame.Rect((checkbox_x, checkbox_y + 20), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            container=self.filter_container,
            tool_tip_text='Only show mentors with no current apprentices'
        )
        checkbox_y += checkbox_spacing
        
        self.no_former_app_text = pygame_gui.elements.UITextBox(
            "No former apprentices",
            scale(pygame.Rect((checkbox_x - 70, checkbox_y), (200, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.filter_container
        )
        checkbox_y += checkbox_spacing
        self.checkboxes["show_no_former_app"] = UIImageButton(
            scale(pygame.Rect((checkbox_x, checkbox_y), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            container=self.filter_container,
            tool_tip_text='Only show mentors who have not had an apprentice'
        )
        self.update_apprentice()  # Draws the current apprentice
        self.update_selected_cat()  # Updates the image and details of selected cat
        self.update_cat_list()
        self.update_buttons()

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

        self.the_cat = Cat.all_cats[game.switches["cat"]]
        self.current_page = 1
        self.selected_mentor = Cat.fetch_cat(self.the_cat.mentor)
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)

        self.heading.set_text(f"Choose a new mentor for {self.the_cat.name}")
        if self.the_cat.mentor:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name}'s current mentor is {self.mentor.name}"
            )
        else:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name} does not have a mentor"
            )
        self.apprentice_details["apprentice_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1200, 300), (300, 300))),
            pygame.transform.scale(self.the_cat.sprite, (300, 300)),
            manager=MANAGER,
        )

        info = (
            self.the_cat.status
            + "\n"
            + self.the_cat.genderalign
            + "\n"
            + self.the_cat.personality.trait
            + "\n"
            + self.the_cat.skills.skill_string(short=True)
        )
        self.apprentice_details["apprentice_info"] = pygame_gui.elements.UITextBox(
            info,
            scale(pygame.Rect((980, 325), (210, 250))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 239, 34)
        self.apprentice_details["apprentice_name"] = (
            pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((1240, 230), (235, 65))),
                short_name,
                object_id="#text_box_34_horizcenter",
                manager=MANAGER,
            )
        )

        self.find_next_previous_cats()  # Determine where the next and previous cat buttons lead

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def find_next_previous_cats(self):
        """Determines where the previous and next buttons lead"""
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        self.previous_cat = 0
        self.next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            self.previous_cat = game.clan.instructor.ID

        if is_instructor:
            self.next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                self.next_cat = 1

            if (
                self.next_cat == 0
                and check_cat.ID != self.the_cat.ID
                and check_cat.dead == self.the_cat.dead
                and check_cat.ID != game.clan.instructor.ID
                and not check_cat.exiled
                and check_cat.status
                in ["apprentice", "medicine cat apprentice", "mediator apprentice"]
                and check_cat.df == self.the_cat.df
            ):
                self.previous_cat = check_cat.ID

            elif (
                self.next_cat == 1
                and check_cat.ID != self.the_cat.ID
                and check_cat.dead == self.the_cat.dead
                and check_cat.ID != game.clan.instructor.ID
                and not check_cat.exiled
                and check_cat.status
                in ["apprentice", "medicine cat apprentice", "mediator apprentice"]
                and check_cat.df == self.the_cat.df
            ):
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

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

        if self.mentor is not None:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name}'s current mentor is {self.mentor.name}"
            )
        else:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name} does not have a mentor"
            )

    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_mentor:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((100, 300), (300, 300))),
                pygame.transform.scale(self.selected_mentor.sprite, (300, 300)),
                manager=MANAGER,
            )

            info = (
                self.selected_mentor.status
                + "\n"
                + self.selected_mentor.genderalign
                + "\n"
                + self.selected_mentor.personality.trait
                + "\n"
                + self.selected_mentor.skills.skill_string(short=True)
            )
            if len(self.selected_mentor.former_apprentices) >= 1:
                info += (
                    f"\n{len(self.selected_mentor.former_apprentices)} former app(s)"
                )
            if len(self.selected_mentor.apprentice) >= 1:
                info += f"\n{len(self.selected_mentor.apprentice)} current app(s)"
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(
                info,
                scale(pygame.Rect((420, 325), (210, 250))),
                object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                manager=MANAGER,
            )

            name = str(self.selected_mentor.name)  # get name
            short_name = shorten_text_to_fit(name, 239, 34)
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((130, 230), (235, 65))),
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
        pos_y = 40
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                cat.sprite,
                cat_object=cat,
                manager=MANAGER,
            )
            pos_x += 120
            if pos_x >= 900:
                pos_x = 0
                pos_y += 120
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
            ("show_no_current_app", self.checkboxes["show_no_current_app"], self.show_only_no_current_app_mentors),
            ("show_no_former_app", self.checkboxes["show_no_former_app"], self.show_only_no_former_app_mentors)
        ]
        for name, checkbox, is_checked in checkboxes:
            checkbox.kill()
            theme = "#checked_checkbox" if is_checked else "#unchecked_checkbox"
            self.checkboxes[name] = UIImageButton(
                relative_rect=checkbox.relative_rect,
                text="",
                object_id=theme,
                container=self.filter_container,
                tool_tip_text=checkbox.tool_tip_text
            )

    def get_valid_mentors(self):
        
        potential_warrior_mentors = [cat for cat in Cat.all_cats_list if not (cat.dead or cat.outside) and cat.status in ['warrior', 'deputy', 'leader']]
        valid_warrior_mentors = []
        invalid_warrior_mentors = []
        potential_medcat_mentors = [cat for cat in Cat.all_cats_list if not (cat.dead or cat.outside) and cat.status == 'medicine cat']
        valid_medcat_mentors = []
        invalid_medcat_mentors = []
        potential_mediator_mentors = [cat for cat in Cat.all_cats_list if not (cat.dead or cat.outside) and cat.status == 'mediator']
        valid_mediator_mentors = []
        invalid_mediator_mentors = []

        if self.the_cat.status == "apprentice":
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


        elif self.the_cat.status == "medicine cat apprentice":
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

        elif self.the_cat.status == "mediator apprentice":
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
        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
