import pygame.transform
import pygame_gui.elements

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
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.utility import get_text_box_theme, scale, scale_dimentions
from .Screens import Screens


class ChooseAdoptiveParentScreen(Screens):
    list_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
        (1300 / 1600 * screen_x, 388 / 1400 * screen_y),
    )

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
        if game.switches["window_open"]:
            return

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            # Cat buttons list
            if event.ui_element == self.back_button:
                self.selected_mate_index = 0
                self.change_screen("profile screen")
            elif event.ui_element == self.toggle_adoptive_parent:
                self.work_thread = self.loading_screen_start_work(
                    self.change_adoptive_parent
                )

            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_current_cat_info()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
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
                game.switches["cat"] = event.ui_element.cat_object.ID
                self.change_screen("profile screen")

    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        self.show_mute_buttons()

        self.info = pygame_gui.elements.UITextBox(
            "If a cat is added as an adoptive parent, they will be displayed on the family page and considered a full relative. "
            "Adoptive and blood parents will be treated the same; this also applies to siblings. ",
            scale(pygame.Rect((400, 120), (800, 200))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
        )

        self.help_button = UIImageButton(
            scale(pygame.Rect((1450, 140), (68, 68))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="A cat's adoptive parents are set automatically when the cat is born. "
            "Any cats that are mates with the parents at the time of birth are considered adoptive parents."
            "<br><br>"
            "To be a possible adoptive parent, the cat has to be 14 moons older than the child.",
        )

        self.the_cat_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((80, 226), (532, 394))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat1_frame_mate.png"
                ).convert_alpha(),
                (532, 394),
            ),
        )
        self.parent_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((988, 226), (532, 394))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_mate.png"
                ).convert_alpha(),
                (532, 394),
            ),
        )

        self.center_icon = pygame_gui.elements.UIImage(
            scale(pygame.Rect((612, 320), (376, 258))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/adoption.png").convert_alpha(),
                scale_dimentions((376, 258)),
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

        # Tab containers:
        contain_rect = scale(pygame.Rect((170, 800), (1260, 438)))

        self.adoptive_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.mates_container
        self.adoptive_next_page = UIImageButton(
            scale(pygame.Rect((732, 358), (68, 68))),
            "",
            object_id="#relation_list_next",
            container=self.adoptive_container,
        )
        self.adoptive_last_page = UIImageButton(
            scale(pygame.Rect((460, 358), (68, 68))),
            "",
            object_id="#relation_list_previous",
            container=self.adoptive_container,
        )

        self.birth_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        self.potential_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.potential_container
        self.potential_next_page = UIImageButton(
            scale(pygame.Rect((732, 358), (68, 68))),
            "",
            object_id="#relation_list_next",
            container=self.potential_container,
        )
        self.potential_last_page = UIImageButton(
            scale(pygame.Rect((460, 358), (68, 68))),
            "",
            object_id="#relation_list_previous",
            container=self.potential_container,
        )
        self.potential_seperator = pygame_gui.elements.UIImage(
            scale(pygame.Rect((995, 0), (20, 352))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                scale_dimentions((20, 352)),
            ),
            container=self.potential_container,
        )

        # Checkboxes and text
        self.mates_current_parents_text = pygame_gui.elements.UITextBox(
            "Mates of current parents",
            scale(pygame.Rect((1030, 10), (219, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        self.unrelated_only_text = pygame_gui.elements.UITextBox(
            "Not closely related",
            scale(pygame.Rect((1030, 170), (219, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        # Page numbers
        self.adoptive_page = 0
        self.potential_parents_page = 0

        # This may be deleted and changed later.
        self.toggle_adoptive_parent = UIImageButton(
            scale(pygame.Rect((607, 620), (384, 60))),
            "",
            object_id="#set_adoptive_parent",
        )

        self.open_tab = "potential"

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

    def change_adoptive_parent(self):
        """Make adoptive parent changes"""

        if not self.selected_cat:
            return

        if self.selected_cat.ID not in self.the_cat.adoptive_parents:
            self.the_cat.adoptive_parents.append(self.selected_cat.ID)
            self.the_cat.create_inheritance_new_cat()

        else:
            self.the_cat.adoptive_parents.remove(self.selected_cat.ID)
            self.the_cat.create_inheritance_new_cat()
            self.selected_cat.create_inheritance_new_cat()

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
            for i in [self.the_cat.parent1, self.the_cat.parent2]
            if isinstance(Cat.fetch_cat(i), Cat)
        ]

        if len(birth_parents) == 1:
            self.birth_parents_buttons["cat"] = UISpriteButton(
                scale(pygame.Rect((480, 26), (300, 300))),
                pygame.transform.scale(birth_parents[0].sprite, (300, 300)),
                cat_object=birth_parents[0],
                manager=MANAGER,
                container=self.birth_container,
            )
            if birth_parents[0].faded:
                self.birth_parents_buttons["cat"].disable()
        elif len(birth_parents) >= 2:
            x_pos = 300
            for i, _par in enumerate(birth_parents):
                self.birth_parents_buttons["cat" + str(i)] = UISpriteButton(
                    scale(pygame.Rect((x_pos, 26), (300, 300))),
                    pygame.transform.scale(_par.sprite, (300, 300)),
                    cat_object=_par,
                    manager=MANAGER,
                    container=self.birth_container,
                    tool_tip_text=str(_par.name),
                    starting_height=2,
                )
                if _par.faded:
                    self.birth_parents_buttons["cat" + str(i)].disable()
                x_pos += 330

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
                scale(pygame.Rect((528, 370), (204, 48))),
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

        pos_x = 30
        pos_y = 0
        i = 0
        for _off in display_cats:
            self.adoptive_parents_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                _off.sprite,
                cat_object=_off,
                manager=MANAGER,
                container=self.adoptive_container,
                starting_height=2,
            )
            if _off.faded:
                self.adoptive_parents_buttons["cat" + str(i)].disable()
            pos_x += 120
            if pos_x >= 1200:
                pos_x = 30
                pos_y += 120
            i += 1

    def update_potential_parents_container(self):
        """Updates everything in the potential mates container, including the list of current mates, checkboxes
        and the page"""

        # Update checkboxes
        if "mates_current_parents" in self.checkboxes:
            self.checkboxes["mates_current_parents"].kill()

        if self.mates_current_parents:
            theme = "#checked_checkbox"
        else:
            theme = "#unchecked_checkbox"

        self.checkboxes["mates_current_parents"] = UIImageButton(
            scale(pygame.Rect((1106, 113), (68, 68))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        self.all_potential_parents = self.chunks(self.get_valid_adoptive_parents(), 24)

        if "unrelated_only" in self.checkboxes:
            self.checkboxes["unrelated_only"].kill()

        if self.unrelated_only:
            theme = "#checked_checkbox"
        else:
            theme = "#unchecked_checkbox"

        self.checkboxes["unrelated_only"] = UIImageButton(
            scale(pygame.Rect((1106, 263), (68, 68))),
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
                scale(pygame.Rect((528, 370), (204, 48))),
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

        pos_x = 30
        pos_y = 0
        i = 0

        for _off in display_cats:
            self.potential_parents_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                _off.sprite,
                cat_object=_off,
                container=self.potential_container,
            )
            pos_x += 120
            if pos_x >= 990:
                pos_x = 30
                pos_y += 120
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
        self.the_cat = Cat.all_cats[game.switches["cat"]]
        self.get_previous_next_cat()

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            "Choose adoptive parents for " + str(self.the_cat.name),
            scale(pygame.Rect((300, 50), (1000, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
        )

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1200, 300), (300, 300))),
            pygame.transform.scale(self.the_cat.sprite, (300, 300)),
        )
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (240, 60))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = (
            str(self.the_cat.moons)
            + " moons\n"
            + self.the_cat.status
            + "\n"
            + self.the_cat.genderalign
            + "\n"
            + self.the_cat.personality.trait
        )
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            scale(pygame.Rect((1000, 350), (188, 200))),
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

        button_x = 200
        self.tab_buttons["potential"] = UIImageButton(
            scale(pygame.Rect((button_x, 722), (306, 78))),
            "",
            object_id="#potential_parents_tab_button",
            starting_height=2,
        )
        button_x += 320

        adoptive_parents_shown = False
        if self.the_cat.adoptive_parents:
            self.tab_buttons["adoptive"] = UIImageButton(
                scale(pygame.Rect((button_x, 722), (306, 78))),
                "",
                object_id="#adoptive_parents_tab_button",
                starting_height=2,
            )
            adoptive_parents_shown = True
            button_x += 320

        birth_parents_shown = False
        if self.the_cat.parent1 or self.the_cat.parent2:
            self.tab_buttons["birth"] = UIImageButton(
                scale(pygame.Rect((button_x, 722), (306, 78))),
                "",
                object_id="#birth_parents_tab_button",
                starting_height=2,
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
            self.toggle_adoptive_parent = UIImageButton(
                scale(pygame.Rect((607, 620), (384, 60))),
                "",
                object_id="#set_adoptive_parent",
            )
            self.toggle_adoptive_parent.disable()
        elif self.selected_cat.ID in self.the_cat.adoptive_parents:
            self.toggle_adoptive_parent = UIImageButton(
                scale(pygame.Rect((607, 620), (384, 60))),
                "",
                object_id="#unset_adoptive_parent",
            )
        else:
            self.toggle_adoptive_parent = UIImageButton(
                scale(pygame.Rect((607, 620), (384, 60))),
                "",
                object_id="#set_adoptive_parent",
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
            scale(pygame.Rect((100, 300), (300, 300))),
            pygame.transform.scale(self.selected_cat.sprite, (300, 300)),
        )

        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.selected_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((130, 230), (220, 60))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = (
            str(self.selected_cat.moons)
            + " moons\n"
            + self.selected_cat.status
            + "\n"
            + self.selected_cat.genderalign
            + "\n"
            + self.selected_cat.personality.trait
        )
        self.selected_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            scale(pygame.Rect((412, 350), (188, 200))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

    def on_use(self):

        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 782 / 1400 * screen_y))

        self.loading_screen_on_use(
            self.work_thread, self.update_after_change, (700, 600)
        )

    def get_valid_adoptive_parents(self):
        """Get a list of valid parents for the current cat"""
        valid_parents = [
            inter_cat
            for inter_cat in Cat.all_cats_list
            if not (
                inter_cat.dead or inter_cat.outside or inter_cat.exiled
            )  # Adoptive parents cant be dead or outside
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

    def get_previous_next_cat(self):
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
                and not check_cat.outside
                and check_cat.df == self.the_cat.df
            ):
                self.previous_cat = check_cat.ID

            elif (
                self.next_cat == 1
                and check_cat.ID != self.the_cat.ID
                and check_cat.dead == self.the_cat.dead
                and check_cat.ID != game.clan.instructor.ID
                and not check_cat.exiled
                and not check_cat.outside
                and check_cat.df == self.the_cat.df
            ):
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

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
