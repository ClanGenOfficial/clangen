from typing import Dict

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
    get_personality_compatibility,
    get_text_box_theme,
    ui_scale,
    ui_scale_dimensions,
    ui_scale_offset,
    shorten_text_to_fit,
)
from .Screens import Screens
from ..clan_package.settings import get_clan_setting
from ..game_structure.game.switches import switch_set_value, switch_get_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


class ChooseMateScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.list_frame_image = None
        self.next_cat = None
        self.previous_cat = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.the_cat = None
        self.selected_cat = None
        self.back_button = None

        self.toggle_mate = None
        self.page_number = None

        self.mate_frame = None
        self.the_cat_frame = None
        self.info = None
        self.checkboxes = {}

        self.current_cat_elements = {}
        self.selected_cat_elements = {}

        self.mates_tab_button = None
        self.offspring_tab_button = None
        self.potential_mates_button = None

        # Keep track of all the cats we want to display
        self.all_mates = []
        self.all_offspring = []
        self.all_potential_mates = []

        # Keep track of the current page on all three tabs
        self.mates_page = 0
        self.offspring_page = 0
        self.potential_mates_page = 0

        self.mates_cat_buttons = {}
        self.offspring_cat_buttons = {}
        self.potential_mates_buttons = {}

        # Tab containers.
        self.mates_container = None
        self.offspring_container = None
        self.potential_container = None

        # Filter toggles
        self.kits_selected_pair = True
        self.single_only = False
        self.have_kits_only = False

        self.single_only_text = None
        self.have_kits_text = None
        self.with_selected_cat_text = None

        self.potential_page_display = None
        self.offspring_page_display = None
        self.mate_page_display = None

        # Keep track of the open tab
        # Can be "potential" for the potential mates tab, "offspring"
        # for the offspring tab, and "mates" for the mate tab.
        self.open_tab = "potential"
        self.tab_buttons = {}

        self.no_kits_message = None

        # Loading screen
        self.work_thread = None

    def handle_event(self, event):
        """Handles events."""
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            # Cat buttons list
            if event.ui_element == self.back_button:
                self.selected_mate_index = 0
                self.change_screen("profile screen")
            elif event.ui_element == self.toggle_mate:
                if self.work_thread is not None and self.work_thread.is_alive():
                    return
                self.work_thread = self.loading_screen_start_work(self.change_mate)

            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_current_cat_info()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_current_cat_info()
                else:
                    print("invalid next cat", self.next_cat)

            # Checkboxes
            elif event.ui_element == self.checkboxes.get("single_only"):
                if self.single_only:
                    self.single_only = False
                else:
                    self.single_only = True
                self.update_potential_mates_container()
            elif event.ui_element == self.checkboxes.get("have_kits_only"):
                if self.have_kits_only:
                    self.have_kits_only = False
                else:
                    self.have_kits_only = True
                self.update_potential_mates_container()
            elif event.ui_element == self.checkboxes.get("kits_selected_pair"):
                if self.kits_selected_pair:
                    self.kits_selected_pair = False
                else:
                    self.kits_selected_pair = True
                self.update_offspring_container()

            # Next and last page buttons
            elif event.ui_element == self.offspring_next_page:
                self.offspring_page += 1
                self.update_offspring_container_page()
            elif event.ui_element == self.offspring_last_page:
                self.offspring_page -= 1
                self.update_offspring_container_page()
            elif event.ui_element == self.potential_next_page:
                self.potential_mates_page += 1
                self.update_potential_mates_container_page()
            elif event.ui_element == self.potential_last_page:
                self.potential_mates_page -= 1
                self.update_potential_mates_container_page()
            elif event.ui_element == self.mates_next_page:
                self.mates_page += 1
                self.update_mates_container_page()
            elif event.ui_element == self.mates_last_page:
                self.mates_page -= 1
                self.update_mates_container_page()

            elif event.ui_element == self.tab_buttons.get("mates"):
                self.open_tab = "mates"
                self.switch_tab()
            elif event.ui_element == self.tab_buttons.get("offspring"):
                self.open_tab = "offspring"
                self.switch_tab()
            elif event.ui_element == self.tab_buttons.get("potential"):
                self.open_tab = "potential"
                self.switch_tab()
            elif (
                event.ui_element in self.mates_cat_buttons.values()
                or event.ui_element in self.potential_mates_buttons.values()
            ):
                self.selected_cat = event.ui_element.cat_object
                self.update_selected_cat()
            elif event.ui_element in self.offspring_cat_buttons.values():
                if event.ui_element.cat_object.faded:
                    return

                switch_set_value(Switch.cat, event.ui_element.cat_object.ID)
                self.change_screen("profile screen")

    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        super().screen_switches()
        self.show_mute_buttons()

        self.list_frame_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 391), (650, 194))),
            get_box(BoxStyles.ROUNDED_BOX, (650, 194)),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.info = pygame_gui.elements.UITextBox(
            "screens.choose_mate.info",
            ui_scale(pygame.Rect((0, 5), (375, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            anchors={"centerx": "centerx"},
        )

        self.the_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 113), (266, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat1_frame_mate.png"
                ).convert_alpha(),
                ui_scale_dimensions((266, 197)),
            ),
        )
        self.mate_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((494, 113), (266, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_mate.png"
                ).convert_alpha(),
                ui_scale_dimensions((266, 197)),
            ),
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

        # Tab containers:
        contain_rect = ui_scale(pygame.Rect((85, 400), (630, 219)))

        self.mates_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.mates_container
        self.mates_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.mates_container,
        )
        self.mates_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.mates_container,
        )

        self.offspring_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.offspring_container
        self.offspring_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.offspring_container,
        )
        self.offspring_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.offspring_container,
        )
        self.offspring_separator = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((497, 0), (10, 176))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                ui_scale_dimensions((10, 176)),
            ),
            container=self.offspring_container,
        )

        self.with_selected_cat_text = pygame_gui.elements.UITextBox(
            "screens.choose_mate.with_selected_cat",
            ui_scale(pygame.Rect((510, 12), (120, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.offspring_container,
        )

        self.potential_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.potential_container
        self.potential_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.potential_container,
        )
        self.potential_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.potential_container,
        )
        self.potential_seperator = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((497, 0), (10, 176))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                ui_scale_dimensions((10, 176)),
            ),
            container=self.potential_container,
        )

        # Checkboxes and text
        self.single_only_text = pygame_gui.elements.UITextBox(
            "screens.choose_mate.no_mates",
            ui_scale(pygame.Rect((517, 11), (104, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        self.have_kits_text = pygame_gui.elements.UITextBox(
            "screens.choose_mate.can_have_kits",
            ui_scale(pygame.Rect((517, 75), (104, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        # Page numbers
        self.mates_page = 0
        self.offspring_page = 0
        self.potential_mates_page = 0

        # This exists solely to stop the code freaking out
        self.toggle_mate = UIImageButton(
            ui_scale(pygame.Rect((323, 310), (153, 30))),
            "",
        )

        self.open_tab = "potential"

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

        self.set_cat_location_bg(self.the_cat)

    def display_change_save(self) -> Dict:
        variable_dict = super().display_change_save()
        variable_dict["selected_cat"] = self.selected_cat
        variable_dict["the_cat"] = self.the_cat
        variable_dict["kits_selected_pair"] = self.kits_selected_pair
        variable_dict["single_only"] = self.single_only
        variable_dict["have_kits_only"] = self.have_kits_only
        variable_dict["open_tab"] = self.open_tab

        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        for key, value in variable_dict.items():
            try:
                setattr(self, key, value)
            except KeyError:
                continue

        self.update_both()
        self.switch_tab()

    def change_mate(self):
        if not self.selected_cat:
            return

        if self.selected_cat.ID not in self.the_cat.mate:
            self.the_cat.set_mate(self.selected_cat)

        else:
            self.the_cat.unset_mate(self.selected_cat, breakup=True)

    def update_both(self):
        """Updates both the current cat and selected cat info."""

        self.update_current_cat_info(
            reset_selected_cat=False
        )  # This will also refresh tab contents
        self.update_selected_cat()

    def update_mates_container(self):
        """Updates everything in the mates container, including the list of current mates,
        and the page"""

        self.all_mates = self.chunks([Cat.fetch_cat(i) for i in self.the_cat.mate], 30)
        self.update_mates_container_page()

    def update_mates_container_page(self):
        """Updates just the current page for the mates container, does
        not refresh the list. It will also update the disable status of the
        next and last page buttons"""
        for ele in self.mates_cat_buttons:
            self.mates_cat_buttons[ele].kill()
        self.mates_cat_buttons = {}

        # Different layout for a single mate - they are just big in the center
        if len(self.all_mates) == 1 and len(self.all_mates[0]) == 1:
            # TODO disable both next and previous page buttons
            self.mates_page = 0
            self.mates_last_page.disable()
            self.mates_next_page.disable()
            _mate = self.all_mates[0][0]
            self.mates_cat_buttons["cat"] = UISpriteButton(
                ui_scale(pygame.Rect((240, 13), (150, 150))),
                pygame.transform.scale(_mate.sprite, ui_scale_dimensions((150, 150))),
                cat_object=_mate,
                manager=MANAGER,
                container=self.mates_container,
            )
            return

        total_pages = len(self.all_mates)
        if max(1, total_pages) - 1 < self.mates_page:
            self.mates_page = total_pages - 1
        elif self.mates_page < 0:
            self.mates_page = 0

        if total_pages <= 1:
            self.mates_last_page.disable()
            self.mates_next_page.disable()
        elif self.mates_page >= total_pages - 1:
            self.mates_last_page.enable()
            self.mates_next_page.disable()
        elif self.mates_page <= 0:
            self.mates_last_page.disable()
            self.mates_next_page.enable()
        else:
            self.mates_last_page.enable()
            self.mates_next_page.enable()

        text = f"{self.mates_page + 1} / {max(1, total_pages)}"
        if not self.mate_page_display:
            self.mate_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.mates_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.mate_page_display.set_text(text)

        if self.all_mates:
            display_cats = self.all_mates[self.mates_page]
        else:
            display_cats = []

        pos_x = 15
        pos_y = 0
        i = 0
        for _mate in display_cats:
            self.mates_cat_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _mate.sprite,
                cat_object=_mate,
                manager=MANAGER,
                container=self.mates_container,
            )
            pos_x += 60
            if pos_x >= 600:
                pos_x = 15
                pos_y += 60
            i += 1

    def update_offspring_container(self):
        """Updates everything in the mates container, including the list of current mates, checkboxes
        and the page"""
        self.all_offspring = [
            Cat.fetch_cat(i)
            for i in list(self.the_cat.inheritance.kits)
            if isinstance(Cat.fetch_cat(i), Cat)
        ]
        if self.selected_cat and self.kits_selected_pair:
            self.all_offspring = [
                i for i in self.all_offspring if self.selected_cat.is_parent(i)
            ]

        self.all_offspring = self.chunks(self.all_offspring, 24)

        if "kits_selected_pair" in self.checkboxes:
            self.checkboxes["kits_selected_pair"].kill()

        if self.kits_selected_pair:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["kits_selected_pair"] = UIImageButton(
            ui_scale(pygame.Rect((553, 62), (34, 34))),
            "",
            object_id=theme,
            container=self.offspring_container,
        )

        self.update_offspring_container_page()

    def update_offspring_container_page(self):
        """Updates just the current page for the mates container, does
        not refresh the list. It will also update the disable status of the
        next and last page buttons"""
        for ele in self.offspring_cat_buttons:
            self.offspring_cat_buttons[ele].kill()
        self.offspring_cat_buttons = {}

        total_pages = len(self.all_offspring)
        if max(1, total_pages) - 1 < self.offspring_page:
            self.offspring_page = total_pages - 1
        elif self.offspring_page < 0:
            self.offspring_page = 0

        if total_pages <= 1:
            self.offspring_last_page.disable()
            self.offspring_next_page.disable()
        elif self.offspring_page >= total_pages - 1:
            self.offspring_last_page.enable()
            self.offspring_next_page.disable()
        elif self.offspring_page <= 0:
            self.offspring_last_page.disable()
            self.offspring_next_page.enable()
        else:
            self.offspring_last_page.enable()
            self.offspring_next_page.enable()

        text = f"{self.offspring_page + 1} / {max(1, total_pages)}"
        if not self.offspring_page_display:
            self.offspring_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.offspring_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.offspring_page_display.set_text(text)

        if self.all_offspring:
            display_cats = self.all_offspring[self.offspring_page]
        else:
            display_cats = []

        pos_x = 15
        pos_y = 0
        i = 0
        for _off in display_cats:
            info_text = f"{str(_off.name)}"
            additional_info = self.the_cat.inheritance.get_cat_info(_off.ID)
            if len(additional_info["type"]) > 0:  # types is always real
                rel_types = [
                    str(rel_type.value) for rel_type in additional_info["type"]
                ]
                rel_types = set(rel_types)  # remove duplicates
                if "" in rel_types:
                    rel_types.remove("")  # removes empty
                if len(rel_types) > 0:
                    info_text += "\n"
                    info_text += ", ".join(rel_types)
                if len(additional_info["additional"]) > 0:
                    add_info = set(additional_info["additional"])  # remove duplicates
                    info_text += "\n"
                    info_text += ", ".join(add_info)

            self.offspring_cat_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _off.sprite,
                cat_object=_off,
                manager=MANAGER,
                container=self.offspring_container,
                tool_tip_text=info_text,
                starting_height=2,
            )
            pos_x += 60
            if pos_x >= 495:
                pos_x = 15
                pos_y += 60
            i += 1

        if self.no_kits_message:
            self.no_kits_message.kill()
        if not display_cats:
            if self.kits_selected_pair and self.selected_cat:
                text = f"{self.the_cat.name} has no offspring with {self.selected_cat.name}."
            else:
                text = f"{self.the_cat.name} has no offspring."

            self.no_kits_message = pygame_gui.elements.UITextBox(
                (
                    "screens.choose_mate.no_kits_pair"
                    if self.kits_selected_pair and self.selected_cat
                    else "screens.choose_mate.no_kits_single"
                ),
                ui_scale(pygame.Rect((0, 0), (497, 120))),
                container=self.offspring_container,
                object_id="#text_box_30_horizcenter_vertcenter",
                text_kwargs={
                    "m_c": self.the_cat,
                    "r_c": self.selected_cat if self.selected_cat else None,
                },
            )

    def update_potential_mates_container(self):
        """Updates everything in the potential mates container, including the list of current mates, checkboxes
        and the page"""

        # Update checkboxes
        if "single_only" in self.checkboxes:
            self.checkboxes["single_only"].kill()

        if self.single_only:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["single_only"] = UIImageButton(
            ui_scale(pygame.Rect((553, 42), (34, 34))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        if "have_kits_only" in self.checkboxes:
            self.checkboxes["have_kits_only"].kill()

        if self.have_kits_only:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["have_kits_only"] = UIImageButton(
            ui_scale(pygame.Rect((553, 127), (34, 34))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        self.all_potential_mates = self.chunks(self.get_valid_mates(), 24)

        # Update checkboxes
        # TODO

        self.update_potential_mates_container_page()

    def update_potential_mates_container_page(self):
        """Updates just the current page for the mates container, does
        not refresh the list. It will also update the disable status of the
        next and last page buttons"""

        for ele in self.potential_mates_buttons:
            self.potential_mates_buttons[ele].kill()
        self.potential_mates_buttons = {}

        total_pages = len(self.all_potential_mates)
        if max(1, total_pages) - 1 < self.potential_mates_page:
            self.potential_mates_page = total_pages - 1
        elif self.potential_mates_page < 0:
            self.potential_mates_page = 0

        if total_pages <= 1:
            self.potential_last_page.disable()
            self.potential_next_page.disable()
        elif self.potential_mates_page >= total_pages - 1:
            self.potential_last_page.enable()
            self.potential_next_page.disable()
        elif self.potential_mates_page <= 0:
            self.potential_last_page.disable()
            self.potential_next_page.enable()
        else:
            self.potential_last_page.enable()
            self.potential_next_page.enable()

        text = f"{self.potential_mates_page + 1} / {max(1, total_pages)}"
        if not self.potential_page_display:
            self.potential_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.potential_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.potential_page_display.set_text(text)

        if self.all_potential_mates:
            display_cats = self.all_potential_mates[self.potential_mates_page]
        else:
            display_cats = []

        pos_x = 15
        pos_y = 0
        i = 0

        for _off in display_cats:
            self.potential_mates_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _off.sprite,
                cat_object=_off,
                container=self.potential_container,
            )
            pos_x += 60
            if pos_x >= 495:
                pos_x = 15
                pos_y += 60
            i += 1

    def exit_screen(self):
        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        for ele in self.tab_buttons:
            self.tab_buttons[ele].kill()
        self.tab_buttons = {}

        self.all_mates = []
        self.all_potential_mates = []
        self.all_offspring = []

        self.list_frame_image.kill()
        self.list_frame_image = None

        self.mates_cat_buttons = {}
        self.offspring_cat_buttons = {}
        self.potential_mates_buttons = {}
        self.checkboxes = {}

        self.potential_container.kill()
        self.potential_container = None
        self.offspring_container.kill()
        self.offspring_container = None
        self.mates_container.kill()
        self.mates_container = None

        self.single_only_text.kill()
        self.single_only_text = None
        self.have_kits_text.kill()
        self.have_kits_text = None
        self.with_selected_cat_text.kill()
        self.with_selected_cat_text = None

        self.the_cat_frame.kill()
        self.the_cat_frame = None
        self.mate_frame.kill()
        self.mate_frame = None
        self.info.kill()
        self.info = None
        self.back_button.kill()
        self.back_button = None
        self.previous_cat_button.kill()
        self.previous_cat_button = None
        self.next_cat_button.kill()
        self.next_cat_button = None
        self.toggle_mate.kill()
        self.toggle_mate = None

        self.potential_seperator = None
        self.offspring_separator = None
        self.potential_last_page = None
        self.potential_next_page = None
        self.offspring_last_page = None
        self.offspring_next_page = None
        self.mates_last_page = None
        self.mates_next_page = None
        self.potential_page_display = None
        self.offspring_page_display = None
        self.mate_page_display = None

    def update_current_cat_info(self, reset_selected_cat=True):
        """Updates all elements with the current cat, as well as the selected cat.
        Called when the screen switched, and whenever the focused cat is switched"""
        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats(
            filter_func=(
                lambda cat: cat.age
                in ("young adult", "adult", "senior adult", "senior")
            )
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

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        # Page numbers
        self.mates_page = 0
        self.offspring_page = 0
        self.potential_mates_page = 0

        heading_rect = ui_scale(pygame.Rect((0, 25), (400, -1)))
        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            "screens.choose_mate.heading",
            heading_rect,
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            anchors={
                "centerx": "centerx",
            },
            text_kwargs={
                "name": shorten_text_to_fit(str(self.the_cat.name), 500, 18),
                "m_c": self.the_cat,
            },
        )

        self.info.set_anchors(
            {"centerx": "centerx", "top_target": self.current_cat_elements["heading"]}
        )
        self.info.set_relative_position((0, 10))

        self.current_cat_elements["heading"].line_spacing = 0.95
        self.current_cat_elements["heading"].redraw_from_chunks()

        del heading_rect

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 150), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
        )
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((65, 115), (120, 30))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = self.the_cat.get_info_block()
        if self.the_cat.mate:
            info += f"\n{len(self.the_cat.mate)} " + i18n.t(
                "general.mate", count=len(self.the_cat.mate)
            )
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((206, 175), (94, 100))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        if reset_selected_cat:
            self.selected_cat = None
            if self.the_cat.mate:
                self.selected_cat = Cat.fetch_cat(self.the_cat.mate[0])
            self.update_selected_cat()

        self.draw_tab_button()
        self.update_mates_container()
        self.update_potential_mates_container()
        self.update_offspring_container()

    def draw_tab_button(self):
        """Draw the tab buttons, and will switch the currently open tab if the button is
        not supposed to show up."""

        for x in self.tab_buttons:
            self.tab_buttons[x].kill()
        self.tab_buttons = {}

        button_rect = ui_scale(pygame.Rect((0, 0), (153, 39)))
        button_rect.bottomleft = ui_scale_offset((100, 8))
        self.tab_buttons["potential"] = UISurfaceImageButton(
            button_rect,
            "screens.choose_mate.potential",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={"bottom": "bottom", "bottom_target": self.list_frame_image},
        )

        mates_tab_shown = False
        button_rect.bottomleft = ui_scale_offset((7, 8))
        if self.the_cat.mate:
            self.tab_buttons["mates"] = UISurfaceImageButton(
                button_rect,
                "screens.choose_mate.current",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
                object_id="@buttonstyles_horizontal_tab",
                starting_height=2,
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.list_frame_image,
                    "left_target": self.tab_buttons["potential"],
                },
            )
            mates_tab_shown = True

        self.tab_buttons["offspring"] = UISurfaceImageButton(
            button_rect,
            "screens.choose_mate.offspring",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={
                "bottom": "bottom",
                "bottom_target": self.list_frame_image,
                "left_target": (
                    self.tab_buttons["mates"]
                    if mates_tab_shown
                    else self.tab_buttons["potential"]
                ),
            },
        )

        if self.open_tab == "mates" and not mates_tab_shown:
            self.open_tab = "potential"

        self.switch_tab()

    def switch_tab(self):
        if self.open_tab == "mates":
            self.mates_container.show()
            self.offspring_container.hide()
            self.potential_container.hide()

            if "mates" in self.tab_buttons:
                self.tab_buttons["mates"].disable()
            self.tab_buttons["offspring"].enable()
            self.tab_buttons["potential"].enable()
        elif self.open_tab == "offspring":
            self.mates_container.hide()
            self.offspring_container.show()
            self.potential_container.hide()

            if "mates" in self.tab_buttons:
                self.tab_buttons["mates"].enable()
            self.tab_buttons["offspring"].disable()
            self.tab_buttons["potential"].enable()
        else:
            self.mates_container.hide()
            self.offspring_container.hide()
            self.potential_container.show()

            if "mates" in self.tab_buttons:
                self.tab_buttons["mates"].enable()
            self.tab_buttons["offspring"].enable()
            self.tab_buttons["potential"].disable()

    def update_selected_cat(self):
        """Updates all elements of the selected cat"""

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        if not isinstance(self.selected_cat, Cat):
            self.selected_cat = None
            self.toggle_mate.disable()
            return

        self.draw_compatible_line_affection()

        self.selected_cat_elements["center_heart"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 188), (200, 78))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/heart_mates.png"
                    if self.selected_cat.ID in self.the_cat.mate
                    else (
                        "resources/images/heart_breakup.png"
                        if self.selected_cat.ID in self.the_cat.previous_mates
                        else "resources/images/heart_maybe.png"
                    )
                ).convert_alpha(),
                ui_scale_dimensions((200, 78)),
            ),
            anchors={"centerx": "centerx"},
        )

        self.selected_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((600, 150), (150, 150))),
            pygame.transform.scale(
                self.selected_cat.sprite, ui_scale_dimensions((150, 150))
            ),
        )

        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.selected_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((620, 115), (110, 30))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = self.selected_cat.get_info_block()
        if self.selected_cat.mate:
            info += f"\n{len(self.selected_cat.mate)} " + i18n.t(
                "general.mate", count=len(self.selected_cat.mate)
            )

        self.selected_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((500, 175), (94, 100))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        if self.kits_selected_pair:
            self.update_offspring_container()

        self.toggle_mate.kill()

        if self.selected_cat.ID in self.the_cat.mate:
            self.toggle_mate = UISurfaceImageButton(
                ui_scale(pygame.Rect((323, 310), (153, 30))),
                "screens.choose_mate.unset_mate",
                get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
                object_id="@buttonstyles_squoval",
            )
        else:
            self.toggle_mate = UISurfaceImageButton(
                ui_scale(pygame.Rect((323, 310), (153, 30))),
                "screens.choose_mate.set_mate",
                get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
                object_id="@buttonstyles_squoval",
            )

        if (
            not get_clan_setting("same sex birth")
            and self.the_cat.gender == self.selected_cat.gender
        ):
            warning_rect = ui_scale(pygame.Rect((0, 0), (160, 45)))
            warning_rect.bottomleft = ui_scale_offset((0, -5))
            self.selected_cat_elements[
                "no kit warning"
            ] = pygame_gui.elements.UITextBox(
                "screens.choose_mate.no_kit_warning",
                warning_rect,
                object_id=get_text_box_theme(
                    "#text_box_22_horizcenter_vertcenter_spacing_95"
                ),
                anchors={
                    "centerx": "centerx",
                    "bottom": "bottom",
                    "bottom_target": self.toggle_mate,
                },
            )
            del warning_rect

    def draw_compatible_line_affection(self):
        """Draws the heart-line based on capability, and draws the hearts based on romantic love."""

        # Set the lines
        self.selected_cat_elements["compat_line"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 190), (200, 78))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/line_compatible.png"
                    if get_personality_compatibility(self.the_cat, self.selected_cat)
                    else (
                        "resources/images/line_incompatible.png"
                        if not get_personality_compatibility(
                            self.the_cat, self.selected_cat
                        )
                        else "resources/images/line_neutral.png"
                    )
                ).convert_alpha(),
                ui_scale_dimensions((200, 78)),
            ),
            anchors={"centerx": "centerx"},
        )

        # Set romantic hearts of current cat towards mate or selected cat.
        if self.the_cat.dead:
            romantic_love = 0
        else:
            if self.selected_cat.ID in self.the_cat.relationships:
                relation = self.the_cat.relationships[self.selected_cat.ID]
            else:
                relation = self.the_cat.create_one_relationship(self.selected_cat)
            romantic_love = relation.romance

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 31 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 210
        for i in range(0, heart_number):
            self.selected_cat_elements["heart1" + str(i)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, 285), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((22, 20)),
                ),
            )
            x_pos += 27

        # Set romantic hearts of mate/selected cat towards current_cat.
        if self.selected_cat.dead:
            romantic_love = 0
        else:
            if self.the_cat.ID in self.selected_cat.relationships:
                relation = self.selected_cat.relationships[self.the_cat.ID]
            else:
                relation = self.selected_cat.create_one_relationship(self.the_cat)
            romantic_love = relation.romance

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 31 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 568
        for i in range(0, heart_number):
            self.selected_cat_elements["heart2" + str(i)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, 285), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((22, 20)),
                ),
            )
            x_pos -= 27

    def on_use(self):
        super().on_use()

        self.loading_screen_on_use(self.work_thread, self.update_both)

    def get_valid_mates(self):
        """Get a list of valid mates for the current cat"""

        # Behold! The ugliest list comprehension ever created!
        valid_mates = [
            i
            for i in Cat.all_cats_list
            if not i.faded
            and self.the_cat.is_potential_mate(
                i, for_love_interest=False, age_restriction=False, ignore_no_mates=True
            )
            and i.status.is_outsider == self.the_cat.status.is_outsider
            and i.status.group_ID == self.the_cat.status.group_ID
            and i.ID not in self.the_cat.mate
            and (not self.single_only or not i.mate)
            and (
                not self.have_kits_only
                or get_clan_setting("same sex birth")
                or i.gender != self.the_cat.gender
            )
        ]

        return valid_mates

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
