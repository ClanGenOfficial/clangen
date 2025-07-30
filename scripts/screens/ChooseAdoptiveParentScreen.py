from typing import Dict

import i18n
import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    ui_scale_dimensions,
    ui_scale_offset,
)
from .Screens import Screens
from ..game_structure.game.switches import switch_set_value, switch_get_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


class ChooseAdoptiveParentScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.the_cat = None
        self.selected_cat = None
        self.back_button = None

        self.toggle_adoptive_parent = None
        self.page_number = None

        self.parent_frame = None
        self.the_cat_frame = None
        self.info = None
        self.help_button = None
        self.checkboxes = {}

        self.current_cat_elements = {}
        self.selected_cat_elements = {}

        self.adoptive_parents_tab_button = None
        self.birth_parents_tab_button = None
        self.potential_parents_tab_button = None

        # Keep track of all the cats we want to display
        self.all_adoptive_parents = []
        self.all_potential_parents = []

        # Keep track of the current page on all three tabs
        self.adoptive_page = 0
        self.potential_parents_page = 0

        self.birth_parents_buttons = {}
        self.adoptive_parents_buttons = {}
        self.potential_parents_buttons = {}

        # Tab containers.
        self.adoptive_container = None
        self.birth_container = None
        self.potential_container = None

        self.list_frame = None

        self.center_icon = None

        # Filter toggles
        self.mates_current_parents = False
        self.unrelated_only = False

        self.mates_current_parents_text = None

        self.adoptive_page_display = None
        self.potential_page_display = None

        # Keep track of the open tab
        # Can be "potential" for the potential mates tab, "offspring"
        # for the offspring tab, and "mates" for the mate tab.
        self.open_tab = "potential"
        self.tab_buttons = {}

        self.work_thread = PropagatingThread()

    def handle_event(self, event):
        """Handles events."""
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            # Cat buttons list
            if event.ui_element == self.back_button:
                self.selected_mate_index = 0
                self.change_screen("profile screen")
            elif event.ui_element == self.toggle_adoptive_parent:
                if self.work_thread is not None and self.work_thread.is_alive():
                    return
                self.work_thread = self.loading_screen_start_work(
                    self.change_adoptive_parent
                )

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
            elif event.ui_element == self.checkboxes.get("mates_current_parents"):
                self.mates_current_parents = not self.mates_current_parents
                self.update_potential_parents_container()
            elif event.ui_element == self.checkboxes.get("unrelated_only"):
                self.unrelated_only = not self.unrelated_only
                self.update_potential_parents_container()

            # Next and last page buttons
            elif event.ui_element == self.potential_next_page:
                self.potential_parents_page += 1
                self.update_potential_mates_container_page()
            elif event.ui_element == self.potential_last_page:
                self.potential_parents_page -= 1
                self.update_potential_mates_container_page()
            elif event.ui_element == self.adoptive_next_page:
                self.adoptive_page += 1
                self.update_adoptive_parents_container_page()
            elif event.ui_element == self.adoptive_last_page:
                self.adoptive_page -= 1
                self.update_adoptive_parents_container_page()

            elif event.ui_element == self.tab_buttons.get("birth"):
                self.open_tab = "birth"
                self.switch_tab()
            elif event.ui_element == self.tab_buttons.get("adoptive"):
                self.open_tab = "adoptive"
                self.switch_tab()
            elif event.ui_element == self.tab_buttons.get("potential"):
                self.open_tab = "potential"
                self.switch_tab()
            elif (
                event.ui_element in self.potential_parents_buttons.values()
                or event.ui_element in self.adoptive_parents_buttons.values()
            ):
                self.selected_cat = event.ui_element.cat_object
                self.update_selected_cat()
            elif event.ui_element in self.birth_parents_buttons.values():
                switch_set_value(Switch.cat, event.ui_element.cat_object.ID)
                self.change_screen("profile screen")

    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        super().screen_switches()
        self.show_mute_buttons()
        list_frame = get_box(BoxStyles.ROUNDED_BOX, (650, 194))

        self.list_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((75, 391), (650, 194))), list_frame
        )
        del list_frame
        self.info = pygame_gui.elements.UITextBox(
            "screens.choose_adoptive_parent.info",
            ui_scale(pygame.Rect((200, 60), (400, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
        )

        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((725, 70), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="screens.choose_adoptive_parent.help_tooltip",
        )

        self.the_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 113), (266, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat1_frame_mate.png"
                ).convert_alpha(),
                (532, 394),
            ),
        )
        self.parent_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((494, 113), (266, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_mate.png"
                ).convert_alpha(),
                (532, 394),
            ),
        )

        self.center_icon = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((306, 160), (188, 129))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/adoption.png").convert_alpha(),
                ui_scale_dimensions((376, 258)),
            ),
            manager=MANAGER,
        )

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            sound_id="page_flip",
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

        self.adoptive_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.mates_container
        self.adoptive_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.adoptive_container,
        )
        self.adoptive_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.adoptive_container,
        )

        self.birth_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

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
                ui_scale_dimensions((20, 352)),
            ),
            container=self.potential_container,
        )

        # Checkboxes and text
        self.mates_current_parents_text = pygame_gui.elements.UITextBox(
            "screens.choose_adoptive_parent.mates_current_parents",
            ui_scale(pygame.Rect((515, 5), (110, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        self.unrelated_only_text = pygame_gui.elements.UITextBox(
            "screens.choose_adoptive_parent.unrelated",
            ui_scale(pygame.Rect((515, 85), (110, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        # Page numbers
        self.adoptive_page = 0
        self.potential_parents_page = 0

        # This may be deleted and changed later.
        self.toggle_adoptive_parent = UISurfaceImageButton(
            ui_scale(pygame.Rect((303, 310), (192, 30))),
            "screens.choose_adoptive_parent.set_parent",
            get_button_dict(ButtonStyles.SQUOVAL, (192, 30)),
            object_id="@buttonstyles_squoval",
        )

        self.open_tab = "potential"

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

    def display_change_save(self):
        variable_dict = super().display_change_save()

        variable_dict["primary_cat"] = self.the_cat
        variable_dict["selected_cat"] = self.selected_cat
        variable_dict["adopted_page"] = self.adoptive_page
        variable_dict["parent_mate_checkbox"] = self.mates_current_parents
        variable_dict["not_related_checkbox"] = self.unrelated_only
        variable_dict["open_tab"] = self.open_tab

        return variable_dict

    def display_change_load(self, variable_dict: Dict):
        super().display_change_load(variable_dict)

        self.selected_cat = variable_dict["selected_cat"]
        self.the_cat = variable_dict["primary_cat"]

        self.open_tab = variable_dict["open_tab"]

        self.mates_current_parents = variable_dict["parent_mate_checkbox"]
        self.unrelated_only = variable_dict["not_related_checkbox"]

        self.update_current_cat_info(reset_selected_cat=False)
        self.update_selected_cat()

    def change_adoptive_parent(self):
        """Make adoptive parent changes"""
        if not self.selected_cat:
            return

        if self.selected_cat.ID not in self.the_cat.adoptive_parents:
            self.the_cat.set_adoptive_parent(self.selected_cat)

        else:
            self.the_cat.unset_adoptive_parent(self.selected_cat)

    def update_after_change(self):
        """Updates that need to be run after setting an adoptive parent"""

        self.draw_tab_button()
        self.update_toggle_button()
        self.update_potential_parents_container()
        self.update_adoptive_parents_container()

    def update_birth_container(self):
        """Updates everything in the mates container, including the list of current mates,
        and the page"""

        for ele in self.birth_parents_buttons:
            self.birth_parents_buttons[ele].kill()
        self.birth_parents_buttons = {}

        birth_parents = [
            Cat.fetch_cat(i)
            for i in (self.the_cat.parent1, self.the_cat.parent2)
            if isinstance(Cat.fetch_cat(i), Cat)
        ]

        if len(birth_parents) == 1:
            self.birth_parents_buttons["cat"] = UISpriteButton(
                ui_scale(pygame.Rect((240, 13), (150, 150))),
                pygame.transform.scale(
                    birth_parents[0].sprite, ui_scale_dimensions((150, 150))
                ),
                cat_object=birth_parents[0],
                manager=MANAGER,
                container=self.birth_container,
                tool_tip_text=str(birth_parents[0].name),
            )
            if birth_parents[0].faded:
                self.birth_parents_buttons["cat"].disable()
        elif len(birth_parents) >= 2:
            x_pos = 150
            for i, _par in enumerate(birth_parents):
                self.birth_parents_buttons["cat" + str(i)] = UISpriteButton(
                    ui_scale(pygame.Rect((x_pos, 13), (150, 150))),
                    pygame.transform.scale(
                        _par.sprite, ui_scale_dimensions((150, 150))
                    ),
                    cat_object=_par,
                    manager=MANAGER,
                    container=self.birth_container,
                    tool_tip_text=str(_par.name),
                    starting_height=2,
                )
                if _par.faded:
                    self.birth_parents_buttons["cat" + str(i)].disable()
                x_pos += 115

    def update_adoptive_parents_container(self):
        """Updates everything in the mates container, including the list of current mates, checkboxes
        and the page"""

        self.all_adoptive_parents = self.chunks(
            [
                Cat.fetch_cat(i)
                for i in self.the_cat.adoptive_parents
                if isinstance(Cat.fetch_cat(i), Cat)
            ],
            30,
        )

        self.update_adoptive_parents_container_page()

    def update_adoptive_parents_container_page(self):
        """Updates just the current page for the mates container, does
        not refresh the list. It will also update the disable status of the
        next and last page buttons"""
        for ele in self.adoptive_parents_buttons:
            self.adoptive_parents_buttons[ele].kill()
        self.adoptive_parents_buttons = {}

        total_pages = len(self.all_adoptive_parents)
        if max(1, total_pages) - 1 < self.adoptive_page:
            self.adoptive_page = total_pages - 1
        elif self.adoptive_page < 0:
            self.adoptive_page = 0

        if total_pages <= 1:
            self.adoptive_last_page.disable()
            self.adoptive_next_page.disable()
        elif self.adoptive_page >= total_pages - 1:
            self.adoptive_last_page.enable()
            self.adoptive_next_page.disable()
        elif self.adoptive_page <= 0:
            self.adoptive_last_page.disable()
            self.adoptive_next_page.enable()
        else:
            self.adoptive_last_page.enable()
            self.adoptive_last_page.enable()

        text = f"{self.adoptive_page + 1} / {max(1, total_pages)}"
        if not self.adoptive_page_display:
            self.adoptive_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.adoptive_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.adoptive_page_display.set_text(text)

        if self.all_adoptive_parents:
            display_cats = self.all_adoptive_parents[self.adoptive_page]
        else:
            display_cats = []

        pos_x = 15
        pos_y = 0
        i = 0
        for _off in display_cats:
            self.adoptive_parents_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _off.sprite,
                cat_object=_off,
                manager=MANAGER,
                container=self.adoptive_container,
                starting_height=2,
            )
            if _off.faded:
                self.adoptive_parents_buttons["cat" + str(i)].disable()
            pos_x += 60
            if pos_x >= 600:
                pos_x = 15
                pos_y += 60
            i += 1

    def update_potential_parents_container(self):
        """Updates everything in the potential mates container, including the list of current mates, checkboxes
        and the page"""

        # Update checkboxes
        if "mates_current_parents" in self.checkboxes:
            self.checkboxes["mates_current_parents"].kill()

        if self.mates_current_parents:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["mates_current_parents"] = UIImageButton(
            ui_scale(pygame.Rect((553, 56), (34, 34))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        self.all_potential_parents = self.chunks(self.get_valid_adoptive_parents(), 24)

        if "unrelated_only" in self.checkboxes:
            self.checkboxes["unrelated_only"].kill()

        if self.unrelated_only:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["unrelated_only"] = UIImageButton(
            ui_scale(pygame.Rect((553, 131), (34, 34))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        self.all_potential_parents = self.chunks(self.get_valid_adoptive_parents(), 24)

        self.update_potential_mates_container_page()

    def update_potential_mates_container_page(self):
        """Updates just the current page for the mates container, does
        not refresh the list. It will also update the disable status of the
        next and last page buttons"""

        for ele in self.potential_parents_buttons:
            self.potential_parents_buttons[ele].kill()
        self.potential_parents_buttons = {}

        total_pages = len(self.all_potential_parents)
        if max(1, total_pages) - 1 < self.potential_parents_page:
            self.potential_parents_page = total_pages - 1
        elif self.potential_parents_page < 0:
            self.potential_parents_page = 0

        if total_pages <= 1:
            self.potential_last_page.disable()
            self.potential_next_page.disable()
        elif self.potential_parents_page >= total_pages - 1:
            self.potential_last_page.enable()
            self.potential_next_page.disable()
        elif self.potential_parents_page <= 0:
            self.potential_last_page.disable()
            self.potential_next_page.enable()
        else:
            self.potential_last_page.enable()
            self.potential_next_page.enable()

        text = f"{self.potential_parents_page + 1} / {max(1, total_pages)}"
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

        if self.all_potential_parents:
            display_cats = self.all_potential_parents[self.potential_parents_page]
        else:
            display_cats = []

        pos_x = 15
        pos_y = 0
        i = 0

        for _off in display_cats:
            self.potential_parents_buttons["cat" + str(i)] = UISpriteButton(
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

        self.all_adoptive_parents = []
        self.all_potential_parents = []

        self.birth_parents_buttons = {}
        self.adoptive_parents_buttons = {}
        self.potential_parents_buttons = {}
        self.checkboxes = {}

        self.list_frame.kill()
        self.list_frame = None

        self.potential_container.kill()
        self.potential_container = None
        self.adoptive_container.kill()
        self.adoptive_container = None
        self.birth_container.kill()
        self.birth_container = None

        self.unrelated_only_text = None
        self.mates_current_parents_text = None

        self.the_cat_frame.kill()
        self.the_cat_frame = None
        self.parent_frame.kill()
        self.parent_frame = None
        self.info.kill()
        self.info = None
        self.help_button.kill()
        self.help_button = None
        self.back_button.kill()
        self.back_button = None
        self.previous_cat_button.kill()
        self.previous_cat_button = None
        self.next_cat_button.kill()
        self.next_cat_button = None
        self.toggle_adoptive_parent.kill()
        self.toggle_adoptive_parent = None

        self.center_icon.kill()
        self.center_icon = None

        self.potential_seperator = None
        self.potential_last_page = None
        self.potential_next_page = None
        self.adoptive_last_page = None
        self.adoptive_next_page = None
        self.potential_page_display = None
        self.adoptive_page_display = None

    def update_current_cat_info(self, reset_selected_cat=True):
        """Updates all elements with the current cat, as well as the selected cat.
        Called when the screen switched, and whenever the focused cat is switched"""
        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()

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

        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            "screens.choose_adoptive_parent.heading",
            ui_scale(pygame.Rect((150, 25), (500, 40))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            text_kwargs={"m_c": self.the_cat},
        )

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((600, 150), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
        )
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((620, 115), (120, 30))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = "\n".join(
            [
                i18n.t("general.moons_age", count=self.the_cat.moons),
                i18n.t(f"general.{self.the_cat.status.rank.lower()}", count=1),
                self.the_cat.genderalign,
                i18n.t(f"cat.personality.{self.the_cat.personality.trait}"),
            ]
        )
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((500, 175), (94, 100))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        if reset_selected_cat:
            self.selected_cat = None
            # Protection against faded
            for x in self.the_cat.adoptive_parents:
                parent_ob = Cat.fetch_cat(x)
                if not parent_ob.faded:
                    self.selected_cat = Cat.fetch_cat(parent_ob)
            self.update_selected_cat()

        self.draw_tab_button()
        self.update_birth_container()
        self.update_potential_parents_container()
        self.update_adoptive_parents_container()

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
            "screens.choose_adoptive_parent.potential",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={"bottom": "bottom", "bottom_target": self.list_frame},
        )

        adoptive_parents_shown = False
        button_rect.bottomleft = ui_scale_offset((7, 8))
        if self.the_cat.adoptive_parents:
            self.tab_buttons["adoptive"] = UISurfaceImageButton(
                button_rect,
                "screens.choose_adoptive_parent.adoptive",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
                object_id="@buttonstyles_horizontal_tab",
                starting_height=2,
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.list_frame,
                    "left_target": self.tab_buttons["potential"],
                },
            )
            adoptive_parents_shown = True

        birth_parents_shown = False
        if self.the_cat.parent1 or self.the_cat.parent2:
            self.tab_buttons["birth"] = UISurfaceImageButton(
                button_rect,
                "screens.choose_adoptive_parent.birth",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
                object_id="@buttonstyles_horizontal_tab",
                starting_height=2,
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.list_frame,
                    "left_target": (
                        self.tab_buttons["adoptive"]
                        if adoptive_parents_shown
                        else self.tab_buttons["potential"]
                    ),
                },
            )
            birth_parents_shown = True

        if (self.open_tab == "birth" and not birth_parents_shown) or (
            self.open_tab == "adoptive" and not adoptive_parents_shown
        ):
            self.open_tab = "potential"

        self.switch_tab()

    def switch_tab(self):
        if self.open_tab == "birth":
            self.birth_container.show()
            self.adoptive_container.hide()
            self.potential_container.hide()

            if "birth" in self.tab_buttons:
                self.tab_buttons["birth"].disable()
            if "adoptive" in self.tab_buttons:
                self.tab_buttons["adoptive"].enable()
            self.tab_buttons["potential"].enable()
        elif self.open_tab == "adoptive":
            self.birth_container.hide()
            self.adoptive_container.show()
            self.potential_container.hide()

            if "birth" in self.tab_buttons:
                self.tab_buttons["birth"].enable()
            if "adoptive" in self.tab_buttons:
                self.tab_buttons["adoptive"].disable()
            self.tab_buttons["potential"].enable()
        else:
            self.birth_container.hide()
            self.adoptive_container.hide()
            self.potential_container.show()

            if "birth" in self.tab_buttons:
                self.tab_buttons["birth"].enable()
            if "adoptive" in self.tab_buttons:
                self.tab_buttons["adoptive"].enable()
            self.tab_buttons["potential"].disable()

    def update_toggle_button(self):
        self.toggle_adoptive_parent.kill()
        if not self.selected_cat:
            self.toggle_adoptive_parent = UISurfaceImageButton(
                ui_scale(pygame.Rect((303, 310), (192, 30))),
                "screens.choose_adoptive_parent.set_parent",
                get_button_dict(ButtonStyles.SQUOVAL, (192, 30)),
                object_id="@buttonstyles_squoval",
            )
            self.toggle_adoptive_parent.disable()
        elif self.selected_cat.ID in self.the_cat.adoptive_parents:
            self.toggle_adoptive_parent = UISurfaceImageButton(
                ui_scale(pygame.Rect((303, 310), (192, 30))),
                "screens.choose_adoptive_parent.unset_parent",
                get_button_dict(ButtonStyles.SQUOVAL, (192, 30)),
                object_id="@buttonstyles_squoval",
            )
        else:
            self.toggle_adoptive_parent = UISurfaceImageButton(
                ui_scale(pygame.Rect((303, 310), (192, 30))),
                "screens.choose_adoptive_parent.set_parent",
                get_button_dict(ButtonStyles.SQUOVAL, (192, 30)),
                object_id="@buttonstyles_squoval",
            )

    def update_selected_cat(self):
        """Updates all elements of the selected cat"""

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.update_toggle_button()

        if not isinstance(self.selected_cat, Cat):
            self.selected_cat = None
            self.center_icon.hide()
            return

        self.center_icon.show()

        self.selected_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 150), (150, 150))),
            pygame.transform.scale(
                self.selected_cat.sprite, ui_scale_dimensions((150, 150))
            ),
        )

        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.selected_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((65, 115), (110, 30))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = "\n".join(
            [
                i18n.t("general.moons_age", count=self.selected_cat.moons),
                i18n.t(f"general.{self.selected_cat.status.rank.lower()}", count=1),
                self.selected_cat.genderalign,
                i18n.t(f"cat.personality.{self.selected_cat.personality.trait}"),
            ]
        )
        self.selected_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((206, 175), (94, 100))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

    def on_use(self):
        super().on_use()

        self.loading_screen_on_use(self.work_thread, self.update_after_change)

    def get_valid_adoptive_parents(self):
        """Get a list of valid parents for the current cat"""
        valid_parents = [
            inter_cat
            for inter_cat in Cat.all_cats_list
            if inter_cat.status.group
            == self.the_cat.status.group  # Adoptive parents must be part of the same group
            and inter_cat.ID != self.the_cat.ID  # Can't be your own adoptive parent
            and inter_cat.moons - self.the_cat.moons
            >= 14  # Adoptive parent must be at least 14 moons older. -> own child can't adopt you
            and inter_cat.ID
            not in self.the_cat.mate  # Can't set your mate your adoptive parent.
            and inter_cat.ID
            not in self.the_cat.get_parents()  # Adoptive parents can't already be their parent
            and self.not_related_to_mate(
                inter_cat
            )  # quick fix TODO: change / remove later
            and (
                not self.mates_current_parents
                or self.is_parent_mate(self.the_cat, inter_cat)
            )  # Toggle for only mates of current parents
            and (
                not self.unrelated_only
                or inter_cat.ID not in self.the_cat.get_relatives()
            )
        ]  # Toggle for only not-closely-related.

        return valid_parents

    def not_related_to_mate(self, possible_parent) -> bool:
        """
        This should prevent weird combinations, till the pop-up is implemented.
        It checks the potential parent is a relative of your mate.
        Return if the cat is a possible adoptive parent.
        """
        if len(self.the_cat.mate) > 0:
            for mate_id in self.the_cat.mate:
                mate = Cat.fetch_cat(mate_id)
                mate_relatives = mate.get_relatives()
                if possible_parent.ID in mate_relatives:
                    return False

        return True

    @staticmethod
    def is_parent_mate(the_cat: Cat, other_cat: Cat):
        """Checks to see if other_cat is the mate of any of current parents"""
        for x in the_cat.get_parents():
            ob = Cat.fetch_cat(x)
            if not isinstance(ob, Cat):
                continue
            if other_cat.ID in ob.mate:
                return True

        return False

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
