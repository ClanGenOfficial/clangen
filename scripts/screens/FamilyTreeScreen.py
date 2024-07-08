import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
)
from .Screens import Screens


class FamilyTreeScreen(Screens):
    # Page numbers for siblings and offspring

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None
        self.grandkits_tab = None
        self.kits_mates_tab = None
        self.kits_tab = None
        self.mates_tab = None
        self.siblings_kits_tab = None
        self.siblings_mates_tab = None
        self.siblings_tab = None
        self.cousins_tab = None
        self.parents_siblings_tab = None
        self.parents_tab = None
        self.grandparents_tab = None
        self.next_group_page = None
        self.previous_group_page = None
        self.root_cat = None
        self.family_tree = None
        self.center_cat_frame = None
        self.root_cat_frame = None
        self.relation_backdrop = None
        self.grandkits_button = None
        self.kits_mates_button = None
        self.kits_button = None
        self.mates_button = None
        self.sibling_kits_button = None
        self.sibling_mates_button = None
        self.siblings_button = None
        self.cousins_button = None
        self.parents_siblings_button = None
        self.parents_button = None
        self.grandparents_button = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.the_cat = None

        self.grandparents = []
        self.parents = []
        self.parents_siblings = []
        self.cousins = []
        self.siblings = []
        self.siblings_mates = []
        self.siblings_kits = []
        self.mates = []
        self.kits = []
        self.kits_mates = []
        self.grandkits = []

        self.cat_elements = {}
        self.relation_elements = {}
        self.tabs = {}

        self.group_page_number = 1
        self.current_group = None
        self.current_group_name = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
                game.switches["root_cat"] = None
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    game.switches["root_cat"] = Cat.all_cats[self.previous_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    game.switches["root_cat"] = Cat.all_cats[self.next_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.parents_button:
                self.current_group = self.parents
                self.current_group_name = "parents"
                self.handle_relation_groups()
            elif event.ui_element == self.siblings_button:
                self.current_group = self.siblings
                self.current_group_name = "siblings"
                self.handle_relation_groups()
            elif event.ui_element == self.sibling_mates_button:
                self.current_group = self.siblings_mates
                self.current_group_name = "siblings_mates"
                self.handle_relation_groups()
            elif event.ui_element == self.sibling_kits_button:
                self.current_group = self.siblings_kits
                self.current_group_name = "siblings_kits"
                self.handle_relation_groups()
            elif event.ui_element == self.parents_siblings_button:
                self.current_group = self.parents_siblings
                self.current_group_name = "parents_siblings"
                self.handle_relation_groups()
            elif event.ui_element == self.cousins_button:
                self.current_group = self.cousins
                self.current_group_name = "cousins"
                self.handle_relation_groups()
            elif event.ui_element == self.grandparents_button:
                self.current_group = self.grandparents
                self.current_group_name = "grandparents"
                self.handle_relation_groups()
            elif event.ui_element == self.mates_button:
                self.current_group = self.mates
                self.current_group_name = "mates"
                self.handle_relation_groups()
            elif event.ui_element == self.kits_button:
                self.current_group = self.kits
                self.current_group_name = "kits"
                self.handle_relation_groups()
            elif event.ui_element == self.kits_mates_button:
                self.current_group = self.kits_mates
                self.current_group_name = "kits_mates"
                self.handle_relation_groups()
            elif event.ui_element == self.grandkits_button:
                self.current_group = self.grandkits
                self.current_group_name = "grandkits"
                self.handle_relation_groups()
            elif event.ui_element == self.previous_group_page:
                self.group_page_number -= 1
                self.handle_relation_groups()
            elif event.ui_element == self.next_group_page:
                self.group_page_number += 1
                self.handle_relation_groups()
            elif event.ui_element == self.cat_elements["center_cat_image"]:
                self.change_screen("profile screen")
                game.switches["root_cat"] = None
            elif (
                event.ui_element in self.relation_elements.values()
                or self.cat_elements.values()
            ):
                try:
                    id = event.ui_element.return_cat_id()
                    if Cat.fetch_cat(id).faded:
                        return
                    game.switches["cat"] = id
                except AttributeError:
                    return
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.change_screen("profile screen")
                    game.switches["root_cat"] = None
                else:
                    self.exit_screen()
                    self.screen_switches()

    def screen_switches(self):
        """Set up things that are always on the page"""

        self.current_group = None
        self.current_group_name = None
        # prev/next and back buttons
        self.previous_cat_button = UIImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "",
            object_id="#previous_cat_button",
            manager=MANAGER,
        )
        self.next_cat_button = UIImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "",
            object_id="#next_cat_button",
            manager=MANAGER,
        )
        self.back_button = UIImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "",
            object_id="#back_button",
            manager=MANAGER,
        )

        # our container for the family tree, this will center itself based on visible relation group buttons
        # it starts with just the center cat frame inside it, since that will always be visible
        self.family_tree = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((360, 225), (80, 90))), MANAGER
        )

        # now grab the other necessary UI elements
        self.previous_group_page = UIImageButton(
            ui_scale(pygame.Rect((470, 640), (34, 34))),
            "",
            object_id="#arrow_left_button",
            manager=MANAGER,
        )
        self.previous_group_page.disable()
        self.next_group_page = UIImageButton(
            ui_scale(pygame.Rect((541, 640), (34, 34))),
            "",
            object_id="#arrow_right_button",
            manager=MANAGER,
        )
        self.next_group_page.disable()
        self.relation_backdrop = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((314, 475), (420, 171))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_relationbackdrop.png"
                ).convert_alpha(),
                ui_scale_dimensions((420, 171)),
            ),
            manager=MANAGER,
        )
        self.relation_backdrop.disable()

        if not game.switches["root_cat"]:
            game.switches["root_cat"] = Cat.all_cats[game.switches["cat"]]
        self.root_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((64, 475), (226, 170))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_bigcatbox.png"
                ).convert_alpha(),
                ui_scale_dimensions((425, 170)),
            ),
            manager=MANAGER,
        )
        self.cat_elements["root_cat_image"] = UISpriteButton(
            ui_scale(pygame.Rect((231, 575), (50, 50))),
            game.switches["root_cat"].sprite,
            cat_id=game.switches["root_cat"].ID,
            manager=MANAGER,
            tool_tip_text=f'Started viewing tree at {game.switches["root_cat"].name}',
        )

        self.root_cat_frame.disable()

        self.center_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (80, 90))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_smallcatbox.png"
                ).convert_alpha(),
                ui_scale_dimensions((160, 180)),
            ),
            manager=MANAGER,
            container=self.family_tree,
        )
        self.center_cat_frame.disable()
        self.group_page_number = 1
        # self.family_setup()
        self.create_family_tree()
        self.get_previous_next_cat()

    def create_family_tree(self):
        """
        this function handles creating the family tree, both collecting the relation groups and displaying the buttons
        """
        # everything in here is held together by duct tape and hope, TAKE CARE WHEN EDITING

        # the cat whose family tree is being viewed
        self.the_cat = Cat.all_cats[game.switches["cat"]]

        self.cat_elements["screen_title"] = pygame_gui.elements.UITextBox(
            f"{self.the_cat.name}'s Family Tree",
            ui_scale(pygame.Rect((150, 25), (500, 50))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        # will need these later to adjust positioning
        # as the various groups are collected, the x_pos and y_pos are adjusted to account for the new buttons,
        # these affect the positioning of all the buttons
        x_pos = 0
        y_pos = 0

        # as the various groups are collected, the x_dim and y_dim are adjusted to account for the new button,
        # these affect the size and positioning of the UIContainer holding the family tree
        x_dim = 80
        y_dim = 90

        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()

        self.parents = self.the_cat.inheritance.get_parents()
        self.mates = self.the_cat.inheritance.get_mates()
        self.kits = self.the_cat.inheritance.get_children()
        self.kits_mates = self.the_cat.inheritance.get_kits_mates()
        self.siblings = self.the_cat.inheritance.get_siblings()
        self.siblings_mates = self.the_cat.inheritance.get_siblings_mates()
        self.siblings_kits = self.the_cat.inheritance.get_siblings_kits()
        self.parents_siblings = self.the_cat.inheritance.get_parents_siblings()
        self.cousins = self.the_cat.inheritance.get_cousins()
        self.grandparents = self.the_cat.inheritance.get_grandparents()
        self.grandkits = self.the_cat.inheritance.get_grand_kits()

        # collect grandparents
        if self.parents:
            y_dim += 98
            y_pos += 98
            if self.grandparents:
                y_dim += 80
                y_pos += 80

            x_dim += 154
            if self.siblings_mates:
                x_dim += 208
            if self.siblings_kits:
                y_dim += 40
                if not self.siblings_mates:
                    x_dim += 208

        # collect cousins
        if self.parents_siblings:
            if not self.siblings_mates and not self.siblings_kits:
                x_dim += 216

        # collect mates
        if self.mates or self.kits:
            x_pos += 138
            x_dim += 140
        # collect kits
        if self.kits:
            if not self.siblings_kits:
                y_dim += 40
            if self.kits_mates:
                x_pos += 101
                x_dim += 101
            if self.grandkits:
                y_dim += 70
                if not self.kits_mates:
                    x_pos += 101
                    x_dim += 101

        self.family_tree.kill()
        self.family_tree = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 275 - y_dim / 2), (x_dim, y_dim))),
            MANAGER,
            anchors={"centerx": "centerx"},
        )

        # creating the center frame, cat, and name
        self.cat_elements["the_cat_image"] = UISpriteButton(
            ui_scale(pygame.Rect((75, 484), (150, 150))),
            self.the_cat.sprite,
            cat_id=self.the_cat.ID,
            manager=MANAGER,
        )
        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 130, 11)
        self.cat_elements["viewing_cat_text"] = pygame_gui.elements.UITextBox(
            f"Viewing {short_name}'s Lineage",
            ui_scale(pygame.Rect((75, 641), (150, 75))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        self.center_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x_pos, y_pos), (80, 90))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_smallcatbox.png"
                ).convert_alpha(),
                ui_scale_dimensions((80, 90)),
            ),
            manager=MANAGER,
            container=self.family_tree,
        )
        self.center_cat_frame.disable()
        self.cat_elements["center_cat_image"] = UISpriteButton(
            ui_scale(pygame.Rect((x_pos + 15, y_pos + 10), (50, 50))),
            self.the_cat.sprite,
            cat_id=self.the_cat.ID,
            manager=MANAGER,
            container=self.family_tree,
        )
        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 57, 11)

        self.cat_elements["center_cat_name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((5 + x_pos, 45 + y_pos), (72, 50))),
            short_name,
            object_id="#text_box_22_horizcenter",
            manager=MANAGER,
            container=self.family_tree,
        )

        if self.parents:
            self.siblings_button = UIImageButton(
                ui_scale(pygame.Rect((76 + x_pos, 32 + y_pos), (158, 30))),
                "",
                object_id="#siblings_button",
                manager=MANAGER,
                container=self.family_tree,
            )
            if self.siblings:
                if self.siblings_mates or self.siblings_kits:
                    self.sibling_mates_button = UIImageButton(
                        ui_scale(pygame.Rect((232 + x_pos, 32 + y_pos), (209, 30))),
                        "",
                        object_id="#siblingmates_button",
                        manager=MANAGER,
                        container=self.family_tree,
                    )
                if self.siblings_kits:
                    self.sibling_kits_button = UIImageButton(
                        ui_scale(pygame.Rect((203 + x_pos, 48 + y_pos), (126, 82))),
                        "",
                        object_id="#siblingkits_button",
                        manager=MANAGER,
                        container=self.family_tree,
                    )
            self.parents_button = UIImageButton(
                ui_scale(pygame.Rect((68 + x_pos, -98 + y_pos), (88, 144))),
                "",
                object_id="#parents_button",
                manager=MANAGER,
                container=self.family_tree,
            )
            self.family_tree.add_element(self.parents_button)
            if self.parents_siblings:
                self.parents_siblings_button = UIImageButton(
                    ui_scale(pygame.Rect((154 + x_pos, -98 + y_pos), (217, 30))),
                    "",
                    object_id="#parentsiblings_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )
                if self.cousins:
                    self.cousins_button = UIImageButton(
                        ui_scale(pygame.Rect((252 + x_pos, -69 + y_pos), (85, 82))),
                        "",
                        object_id="#cousins_button",
                        manager=MANAGER,
                        container=self.family_tree,
                    )
            if self.grandparents:
                self.grandparents_button = UIImageButton(
                    ui_scale(pygame.Rect((47 + x_pos, -177 + y_pos), (130, 82))),
                    "",
                    object_id="#grandparents_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )

        if self.mates or self.kits:
            self.mates_button = UIImageButton(
                ui_scale(pygame.Rect((-138 + x_pos, 32 + y_pos), (144, 30))),
                "",
                object_id="#mates_button",
                manager=MANAGER,
                container=self.family_tree,
            )
        if self.kits:
            self.kits_button = UIImageButton(
                ui_scale(pygame.Rect((-59 + x_pos, 48 + y_pos), (58, 82))),
                "",
                object_id="#kits_button",
                manager=MANAGER,
                container=self.family_tree,
            )
            if self.kits_mates or self.grandkits:
                self.kits_mates_button = UIImageButton(
                    ui_scale(pygame.Rect((-238 + x_pos, 99 + y_pos), (182, 30))),
                    "",
                    object_id="#kitsmates_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )
            if self.grandkits:
                self.grandkits_button = UIImageButton(
                    ui_scale(pygame.Rect((-141 + x_pos, 116 + y_pos), (101, 82))),
                    "",
                    object_id="#grandkits_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )

    def handle_relation_groups(self):
        """Updates the given group"""
        for ele in self.relation_elements:
            self.relation_elements[ele].kill()
        self.relation_elements = {}

        self.update_tab()
        if not self.current_group:
            self.relation_elements["no_cats_notice"] = pygame_gui.elements.UITextBox(
                "None",
                ui_scale(pygame.Rect((275, 540), (450, 30))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
            )
        _current_group = self.chunks(self.current_group, 24)

        if self.group_page_number > len(_current_group):
            self.group_page_number = max(len(_current_group), 1)

        if _current_group:
            display_cats = _current_group[self.group_page_number - 1]
        else:
            display_cats = []

        pos_x = 0
        pos_y = 0
        i = 0
        for kitty in display_cats:
            _kitty = Cat.fetch_cat(kitty)
            info_text = f"{str(_kitty.name)}"
            additional_info = self.the_cat.inheritance.get_cat_info(kitty)
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

            self.relation_elements["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((324 + pos_x, 485 + pos_y), (50, 50))),
                _kitty.sprite,
                cat_id=_kitty.ID,
                manager=MANAGER,
                tool_tip_text=info_text,
                starting_height=2,
            )

            pos_x += 50
            if pos_x > 450:
                pos_y += 50
                pos_x = 0
            i += 1

        # Enable and disable page buttons.
        if len(_current_group) <= 1:
            self.previous_group_page.disable()
            self.next_group_page.disable()
        elif self.group_page_number >= len(_current_group):
            self.previous_group_page.enable()
            self.next_group_page.disable()
        elif self.group_page_number == 1 and len(self.current_group) > 1:
            self.previous_group_page.disable()
            self.next_group_page.enable()
        else:
            self.previous_group_page.enable()
            self.next_group_page.enable()

    def update_tab(self):
        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        if self.current_group_name == "grandparents":
            self.tabs["grandparents_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((582, 445), (128, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/grandparents_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((128, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "parents":
            self.tabs["parents_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((623, 445), (87, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/parents_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((87, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "parents_siblings":
            self.tabs["parents_siblings_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((561, 445), (148, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/parentsibling_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((148, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "cousins":
            self.tabs["cousins_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((627, 445), (83, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/cousins_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((83, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "siblings":
            self.tabs["siblings_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((628, 445), (82, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/siblings_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((82, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "siblings_mates":
            self.tabs["siblings_mates_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((573, 445), (137, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/siblingsmate_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((137, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "siblings_kits":
            self.tabs["siblings_kits_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((585, 445), (125, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/siblingkits_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((125, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "mates":
            self.tabs["mates_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((635, 445), (75, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/mates_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((75, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "kits":
            self.tabs["kits_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((653, 445), (57, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/kits_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((57, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "kits_mates":
            self.tabs["kits_mates_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((598, 445), (112, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/kitsmate_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((112, 30)),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "grandkits":
            self.tabs["grandkits_tab"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((610, 445), (100, 30))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/grandkits_tab.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((100, 30)),
                ),
                manager=MANAGER,
            )

    def get_previous_next_cat(self):
        """Determines where the previous and next buttons should lead, and enables/disables them"""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if (
                    next_cat == 0
                    and check_cat.ID != self.the_cat.ID
                    and check_cat.dead == self.the_cat.dead
                    and check_cat.ID != game.clan.instructor.ID
                    and check_cat.outside == self.the_cat.outside
                    and check_cat.df == self.the_cat.df
                    and not check_cat.faded
                ):
                    previous_cat = check_cat.ID

                elif (
                    next_cat == 1
                    and check_cat.ID != self.the_cat.ID
                    and check_cat.dead == self.the_cat.dead
                    and check_cat.ID != game.clan.instructor.ID
                    and check_cat.outside == self.the_cat.outside
                    and check_cat.df == self.the_cat.df
                    and not check_cat.faded
                ):
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    def exit_screen(self):
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}

        for ele in self.relation_elements:
            self.relation_elements[ele].kill()
        self.relation_elements = {}

        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        self.grandparents = []
        self.parents = []
        self.parents_siblings = []
        self.cousins = []
        self.siblings = []
        self.siblings_mates = []
        self.siblings_kits = []
        self.mates = []
        self.kits = []
        self.kits_mates = []
        self.grandkits = []
        self.current_group = None

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.family_tree.kill()
        del self.family_tree
        self.relation_backdrop.kill()
        del self.relation_backdrop
        self.root_cat_frame.kill()
        del self.root_cat_frame
        self.next_group_page.kill()
        del self.next_group_page
        self.previous_group_page.kill()
        del self.previous_group_page
