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
from scripts.utility import (
    get_personality_compatibility,
    get_text_box_theme,
    scale,
    scale_dimentions,
)
from .Screens import Screens


class ChooseMateScreen(Screens):
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
        if game.switches["window_open"]:
            return

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            # Cat buttons list
            if event.ui_element == self.back_button:
                self.selected_mate_index = 0
                self.change_screen("profile screen")
            elif event.ui_element == self.toggle_mate:

                self.work_thread = self.loading_screen_start_work(self.change_mate)

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

                game.switches["cat"] = event.ui_element.cat_object.ID
                self.change_screen("profile screen")

    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        self.show_mute_buttons()
        self.info = pygame_gui.elements.UITextBox(
            "If a cat has mates, then they will be loyal and only have kittens with their mates"
            " (unless affairs are toggled on.) Potential mates are listed below! The lines "
            "connecting the two cats may give a hint on their compatibility with one another "
            "and any existing romantic feelings will be shown with small hearts.",
            scale(pygame.Rect((360, 120), (880, 200))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
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
        self.mate_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((988, 226), (532, 394))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_mate.png"
                ).convert_alpha(),
                (532, 394),
            ),
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

        self.mates_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.mates_container
        self.mates_next_page = UIImageButton(
            scale(pygame.Rect((732, 358), (68, 68))),
            "",
            object_id="#relation_list_next",
            container=self.mates_container,
        )
        self.mates_last_page = UIImageButton(
            scale(pygame.Rect((460, 358), (68, 68))),
            "",
            object_id="#relation_list_previous",
            container=self.mates_container,
        )

        self.offspring_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.offspring_container
        self.offspring_next_page = UIImageButton(
            scale(pygame.Rect((732, 358), (68, 68))),
            "",
            object_id="#relation_list_next",
            container=self.offspring_container,
        )
        self.offspring_last_page = UIImageButton(
            scale(pygame.Rect((460, 358), (68, 68))),
            "",
            object_id="#relation_list_previous",
            container=self.offspring_container,
        )
        self.offspring_seperator = pygame_gui.elements.UIImage(
            scale(pygame.Rect((995, 0), (20, 352))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                scale_dimentions((20, 352)),
            ),
            container=self.offspring_container,
        )

        self.with_selected_cat_text = pygame_gui.elements.UITextBox(
            "Offspring with selected cat",
            scale(pygame.Rect((1035, 25), (209, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.offspring_container,
        )

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
        self.single_only_text = pygame_gui.elements.UITextBox(
            "No mates",
            scale(pygame.Rect((1035, 22), (209, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        self.have_kits_text = pygame_gui.elements.UITextBox(
            "Can have biological kits",
            scale(pygame.Rect((1035, 150), (209, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        # Page numbers
        self.mates_page = 0
        self.offspring_page = 0
        self.potential_mates_page = 0

        # This may be deleted and changed later.
        self.toggle_mate = UIImageButton(
            scale(pygame.Rect((646, 620), (306, 60))),
            "",
            object_id="#confirm_mate_button",
        )

        self.open_tab = "potential"

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

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
                scale(pygame.Rect((480, 26), (300, 300))),
                pygame.transform.scale(_mate.sprite, (300, 300)),
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
                scale(pygame.Rect((528, 370), (204, 48))),
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

        pos_x = 30
        pos_y = 0
        i = 0
        for _mate in display_cats:
            self.mates_cat_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                _mate.sprite,
                cat_object=_mate,
                manager=MANAGER,
                container=self.mates_container,
            )
            pos_x += 120
            if pos_x >= 1200:
                pos_x = 30
                pos_y += 120
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
            theme = "#checked_checkbox"
        else:
            theme = "#unchecked_checkbox"

        self.checkboxes["kits_selected_pair"] = UIImageButton(
            scale(pygame.Rect((1106, 124), (68, 68))),
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
                scale(pygame.Rect((528, 370), (204, 48))),
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

        pos_x = 30
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
                scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                _off.sprite,
                cat_object=_off,
                manager=MANAGER,
                container=self.offspring_container,
                tool_tip_text=info_text,
                starting_height=2,
            )
            pos_x += 120
            if pos_x >= 990:
                pos_x = 30
                pos_y += 120
            i += 1

        if self.no_kits_message:
            self.no_kits_message.kill()
        if not display_cats:
            if self.kits_selected_pair and self.selected_cat:
                text = f"{self.the_cat.name} has no offspring with {self.selected_cat.name}."
            else:
                text = f"{self.the_cat.name} has no offspring."

            self.no_kits_message = pygame_gui.elements.UITextBox(
                text,
                scale(pygame.Rect((0, 0), (994, 352))),
                container=self.offspring_container,
                object_id="#text_box_30_horizcenter_vertcenter",
            )

    def update_potential_mates_container(self):
        """Updates everything in the potential mates container, including the list of current mates, checkboxes
        and the page"""

        # Update checkboxes
        if "single_only" in self.checkboxes:
            self.checkboxes["single_only"].kill()

        if self.single_only:
            theme = "#checked_checkbox"
        else:
            theme = "#unchecked_checkbox"

        self.checkboxes["single_only"] = UIImageButton(
            scale(pygame.Rect((1106, 85), (68, 68))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        if "have_kits_only" in self.checkboxes:
            self.checkboxes["have_kits_only"].kill()

        if self.have_kits_only:
            theme = "#checked_checkbox"
        else:
            theme = "#unchecked_checkbox"

        self.checkboxes["have_kits_only"] = UIImageButton(
            scale(pygame.Rect((1106, 254), (68, 68))),
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
                scale(pygame.Rect((528, 370), (204, 48))),
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

        pos_x = 30
        pos_y = 0
        i = 0

        for _off in display_cats:
            self.potential_mates_buttons["cat" + str(i)] = UISpriteButton(
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

        self.all_mates = []
        self.all_potential_mates = []
        self.all_offspring = []

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
        self.offspring_seperator = None
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
        self.the_cat = Cat.all_cats[game.switches["cat"]]
        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()
        self.get_previous_next_cat()

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

        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            "Choose a mate for " + str(self.the_cat.name),
            scale(pygame.Rect((300, 50), (1000, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
        )

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((100, 300), (300, 300))),
            pygame.transform.scale(self.the_cat.sprite, (300, 300)),
        )
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((130, 230), (240, 60))),
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
        if self.the_cat.mate:
            info += f"\n{len(self.the_cat.mate)} "
            if len(self.the_cat.mate) > 1:
                info += "mates"
            else:
                info += "mate"
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            scale(pygame.Rect((412, 350), (188, 200))),
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

        button_x = 200
        self.tab_buttons["potential"] = UIImageButton(
            scale(pygame.Rect((button_x, 722), (306, 78))),
            "",
            object_id="#potential_mates_tab_button",
            starting_height=2,
        )
        button_x += 320

        mates_tab_shown = False
        if self.the_cat.mate:
            self.tab_buttons["mates"] = UIImageButton(
                scale(pygame.Rect((button_x, 722), (306, 78))),
                "",
                object_id="#mates_tab_button",
                starting_height=2,
            )
            mates_tab_shown = True
            button_x += 320

        self.tab_buttons["offspring"] = UIImageButton(
            scale(pygame.Rect((button_x, 722), (306, 78))),
            "",
            object_id="#offspring_tab_button",
            starting_height=2,
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
        if self.selected_cat.ID in self.the_cat.mate:
            self.selected_cat_elements["center_heart"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((600, 376), (400, 156))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_mates.png"
                    ).convert_alpha(),
                    (400, 156),
                ),
            )
        elif self.selected_cat.ID in self.the_cat.previous_mates:
            self.selected_cat_elements["center_heart"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((600, 376), (400, 156))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_breakup.png"
                    ).convert_alpha(),
                    (400, 156),
                ),
            )
        else:
            self.selected_cat_elements["center_heart"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((600, 376), (400, 156))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_maybe.png"
                    ).convert_alpha(),
                    (400, 156),
                ),
            )

        self.selected_cat_elements["image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1200, 300), (300, 300))),
            pygame.transform.scale(self.selected_cat.sprite, (300, 300)),
        )

        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.selected_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (220, 60))),
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
        if self.selected_cat.mate:
            info += f"\n{len(self.selected_cat.mate)} "
            if len(self.selected_cat.mate) > 1:
                info += "mates"
            else:
                info += "mate"

        self.selected_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            scale(pygame.Rect((1000, 350), (188, 200))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        if (
            not game.clan.clan_settings["same sex birth"]
            and self.the_cat.gender == self.selected_cat.gender
        ):
            self.selected_cat_elements["no kit warning"] = (
                pygame_gui.elements.UITextBox(
                    f"<font pixel_size={int(22 / 1400 * screen_y)}> This pair can't have biological kittens </font>",
                    scale(pygame.Rect((550, 250), (498, 50))),
                    object_id=get_text_box_theme(
                        "#text_box_22_horizcenter_vertcenter_spacing_95"
                    ),
                )
            )

        if self.kits_selected_pair:
            self.update_offspring_container()

        self.toggle_mate.kill()

        if self.selected_cat.ID in self.the_cat.mate:
            self.toggle_mate = UIImageButton(
                scale(pygame.Rect((646, 620), (306, 60))),
                "",
                object_id="#break_up_button",
            )
        else:
            self.toggle_mate = UIImageButton(
                scale(pygame.Rect((646, 620), (306, 60))),
                "",
                object_id="#confirm_mate_button",
            )

    def draw_compatible_line_affection(self):
        """Draws the heart-line based on capability, and draws the hearts based on romantic love."""

        # Set the lines
        self.selected_cat_elements["compat_line"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((600, 380), (400, 156))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/line_neutral.png"
                ).convert_alpha(),
                (400, 156),
            ),
        )
        if get_personality_compatibility(self.the_cat, self.selected_cat) is True:
            self.selected_cat_elements["compat_line"].set_image(
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/line_compatible.png"
                    ).convert_alpha(),
                    (400, 156),
                )
            )
        elif get_personality_compatibility(self.the_cat, self.selected_cat) is False:
            self.selected_cat_elements["compat_line"].set_image(
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/line_incompatible.png"
                    ).convert_alpha(),
                    (400, 156),
                )
            )

        # Set romantic hearts of current cat towards mate or selected cat.
        if self.the_cat.dead:
            romantic_love = 0
        else:
            if self.selected_cat.ID in self.the_cat.relationships:
                relation = self.the_cat.relationships[self.selected_cat.ID]
            else:
                relation = self.the_cat.create_one_relationship(self.selected_cat)
            romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 31 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 420
        for i in range(0, heart_number):
            self.selected_cat_elements["heart1" + str(i)] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_pos, 570), (44, 40))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    (44, 40),
                ),
            )
            x_pos += 54

        # Set romantic hearts of mate/selected cat towards current_cat.
        if self.selected_cat.dead:
            romantic_love = 0
        else:
            if self.the_cat.ID in self.selected_cat.relationships:
                relation = self.selected_cat.relationships[self.the_cat.ID]
            else:
                relation = self.selected_cat.create_one_relationship(self.the_cat)
            romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 31 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 1136
        for i in range(0, heart_number):
            self.selected_cat_elements["heart2" + str(i)] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_pos, 570), (44, 40))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    (44, 40),
                ),
            )
            x_pos -= 54

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
                and check_cat.age not in ["adolescent", "kitten", "newborn"]
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
                and check_cat.age not in ["adolescent", "kitten", "newborn"]
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

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 782 / 1400 * screen_y))

        self.loading_screen_on_use(self.work_thread, self.update_both, (700, 600))

    def get_valid_mates(self):
        """Get a list of valid mates for the current cat"""

        # Behold! The uglest list comprehension ever created!
        valid_mates = [
            i
            for i in Cat.all_cats_list
            if not i.faded
            and self.the_cat.is_potential_mate(
                i, for_love_interest=False, age_restriction=False, ignore_no_mates=True
            )
            and i.ID not in self.the_cat.mate
            and (not self.single_only or not i.mate)
            and (
                not self.have_kits_only
                or game.clan.clan_settings["same sex birth"]
                or i.gender != self.the_cat.gender
            )
        ]

        return valid_mates

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
