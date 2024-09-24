import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton
from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit
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
            self.mute_button_pressed(event)

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

        self.show_mute_buttons()
        self.current_group = None
        self.current_group_name = None
        # prev/next and back buttons
        self.previous_cat_button = UIImageButton(
            scale(pygame.Rect((50, 50), (306, 60))),
            "",
            object_id="#previous_cat_button",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.next_cat_button = UIImageButton(
            scale(pygame.Rect((1244, 50), (306, 60))),
            "",
            object_id="#next_cat_button",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.back_button = UIImageButton(
            scale(pygame.Rect((50, 120), (210, 60))),
            "",
            object_id="#back_button",
            manager=MANAGER,
        )

        # our container for the family tree, this will center itself based on visible relation group buttons
        # it starts with just the center cat frame inside it, since that will always be visible
        self.family_tree = pygame_gui.core.UIContainer(
            scale(pygame.Rect((720, 450), (160, 180))), MANAGER
        )

        # now grab the other necessary UI elements
        self.previous_group_page = UIImageButton(
            scale(pygame.Rect((941, 1281), (68, 68))),
            "",
            object_id="#arrow_left_button",
            manager=MANAGER,
        )
        self.previous_group_page.disable()
        self.next_group_page = UIImageButton(
            scale(pygame.Rect((1082, 1281), (68, 68))),
            "",
            object_id="#arrow_right_button",
            manager=MANAGER,
        )
        self.next_group_page.disable()
        self.relation_backdrop = pygame_gui.elements.UIImage(
            scale(pygame.Rect((628, 950), (841, 342))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_relationbackdrop.png"
                ).convert_alpha(),
                (841, 342),
            ),
            manager=MANAGER,
        )
        self.relation_backdrop.disable()

        if not game.switches["root_cat"]:
            game.switches["root_cat"] = Cat.all_cats[game.switches["cat"]]
        self.root_cat_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((129, 950), (452, 340))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_bigcatbox.png"
                ).convert_alpha(),
                (452, 340),
            ),
            manager=MANAGER,
        )
        self.cat_elements["root_cat_image"] = UISpriteButton(
            scale(pygame.Rect((462, 1151), (100, 100))),
            game.switches["root_cat"].sprite,
            cat_id=game.switches["root_cat"].ID,
            manager=MANAGER,
            tool_tip_text=f'Started viewing tree at {game.switches["root_cat"].name}',
        )

        self.root_cat_frame.disable()

        self.center_cat_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (160, 180))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_smallcatbox.png"
                ).convert_alpha(),
                (160, 180),
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
            scale(pygame.Rect((300, 50), (1000, 100))),
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
        x_dim = 160
        y_dim = 180

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
            y_dim += 196
            y_pos += 196
            if self.grandparents:
                y_dim += 160
                y_pos += 160

            x_dim += 309
            if self.siblings_mates:
                x_dim += 417
            if self.siblings_kits:
                y_dim += 80
                if not self.siblings_mates:
                    x_dim += 417

        # collect cousins
        if self.parents_siblings:
            if not self.siblings_mates and not self.siblings_kits:
                x_dim += 433

        # collect mates
        if self.mates or self.kits:
            x_pos += 276
            x_dim += 280
        # collect kits
        if self.kits:
            if not self.siblings_kits:
                y_dim += 80
            if self.kits_mates:
                x_pos += 202
                x_dim += 202
            if self.grandkits:
                y_dim += 140
                if not self.kits_mates:
                    x_pos += 202
                    x_dim += 202

        self.family_tree.kill()
        self.family_tree = pygame_gui.core.UIContainer(
            scale(pygame.Rect((800 - x_dim / 2, 550 - y_dim / 2), (x_dim, y_dim))),
            MANAGER,
        )

        # creating the center frame, cat, and name
        self.cat_elements["the_cat_image"] = UISpriteButton(
            scale(pygame.Rect((150, 969), (300, 300))),
            self.the_cat.sprite,
            cat_id=self.the_cat.ID,
            manager=MANAGER,
        )
        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 260, 22)
        self.cat_elements["viewing_cat_text"] = pygame_gui.elements.UITextBox(
            f"Viewing {short_name}'s Lineage",
            scale(pygame.Rect((150, 1282), (300, 150))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        self.center_cat_frame = pygame_gui.elements.UIImage(
            scale(pygame.Rect((x_pos, y_pos), (160, 180))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/familytree_smallcatbox.png"
                ).convert_alpha(),
                (160, 180),
            ),
            manager=MANAGER,
            container=self.family_tree,
        )
        self.center_cat_frame.disable()
        self.cat_elements["center_cat_image"] = UISpriteButton(
            scale(pygame.Rect((x_pos + 30, y_pos + 20), (100, 100))),
            self.the_cat.sprite,
            cat_id=self.the_cat.ID,
            manager=MANAGER,
            container=self.family_tree,
        )
        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 114, 22)

        self.cat_elements["center_cat_name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((10 + x_pos, 90 + y_pos), (145, 100))),
            short_name,
            object_id="#text_box_22_horizcenter",
            manager=MANAGER,
            container=self.family_tree,
        )

        if self.parents:
            self.siblings_button = UIImageButton(
                scale(pygame.Rect((152 + x_pos, 65 + y_pos), (316, 60))),
                "",
                object_id="#siblings_button",
                manager=MANAGER,
                container=self.family_tree,
            )
            if self.siblings:
                if self.siblings_mates or self.siblings_kits:
                    self.sibling_mates_button = UIImageButton(
                        scale(pygame.Rect((464 + x_pos, 65 + y_pos), (418, 60))),
                        "",
                        object_id="#siblingmates_button",
                        manager=MANAGER,
                        container=self.family_tree,
                    )
                if self.siblings_kits:
                    self.sibling_kits_button = UIImageButton(
                        scale(pygame.Rect((406 + x_pos, 97 + y_pos), (252, 164))),
                        "",
                        object_id="#siblingkits_button",
                        manager=MANAGER,
                        container=self.family_tree,
                    )
            self.parents_button = UIImageButton(
                scale(pygame.Rect((136 + x_pos, -196 + y_pos), (176, 288))),
                "",
                object_id="#parents_button",
                manager=MANAGER,
                container=self.family_tree,
            )
            self.family_tree.add_element(self.parents_button)
            if self.parents_siblings:
                self.parents_siblings_button = UIImageButton(
                    scale(pygame.Rect((308 + x_pos, -196 + y_pos), (436, 60))),
                    "",
                    object_id="#parentsiblings_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )
                if self.cousins:
                    self.cousins_button = UIImageButton(
                        scale(pygame.Rect((504 + x_pos, -139 + y_pos), (170, 164))),
                        "",
                        object_id="#cousins_button",
                        manager=MANAGER,
                        container=self.family_tree,
                    )
            if self.grandparents:
                self.grandparents_button = UIImageButton(
                    scale(pygame.Rect((94 + x_pos, -355 + y_pos), (260, 164))),
                    "",
                    object_id="#grandparents_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )

        if self.mates or self.kits:
            self.mates_button = UIImageButton(
                scale(pygame.Rect((-276 + x_pos, 65 + y_pos), (288, 60))),
                "",
                object_id="#mates_button",
                manager=MANAGER,
                container=self.family_tree,
            )
        if self.kits:
            self.kits_button = UIImageButton(
                scale(pygame.Rect((-118 + x_pos, 97 + y_pos), (116, 164))),
                "",
                object_id="#kits_button",
                manager=MANAGER,
                container=self.family_tree,
            )
            if self.kits_mates or self.grandkits:
                self.kits_mates_button = UIImageButton(
                    scale(pygame.Rect((-477 + x_pos, 198 + y_pos), (364, 60))),
                    "",
                    object_id="#kitsmates_button",
                    manager=MANAGER,
                    container=self.family_tree,
                )
            if self.grandkits:
                self.grandkits_button = UIImageButton(
                    scale(pygame.Rect((-282 + x_pos, 233 + y_pos), (202, 164))),
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
                scale(pygame.Rect((550, 1080), (900, 60))),
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
                scale(pygame.Rect((649 + pos_x, 970 + pos_y), (100, 100))),
                _kitty.sprite,
                cat_id=_kitty.ID,
                manager=MANAGER,
                tool_tip_text=info_text,
                starting_height=2,
            )

            pos_x += 100
            if pos_x > 700:
                pos_y += 100
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
                scale(pygame.Rect((1164, 890), (256, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/grandparents_tab.png"
                    ).convert_alpha(),
                    (256, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "parents":
            self.tabs["parents_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1246, 890), (174, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/parents_tab.png"
                    ).convert_alpha(),
                    (174, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "parents_siblings":
            self.tabs["parents_siblings_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1123, 890), (296, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/parentsibling_tab.png"
                    ).convert_alpha(),
                    (296, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "cousins":
            self.tabs["cousins_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1254, 890), (166, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/cousins_tab.png"
                    ).convert_alpha(),
                    (166, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "siblings":
            self.tabs["siblings_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1256, 890), (164, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/siblings_tab.png"
                    ).convert_alpha(),
                    (164, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "siblings_mates":
            self.tabs["siblings_mates_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1146, 890), (274, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/siblingsmate_tab.png"
                    ).convert_alpha(),
                    (274, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "siblings_kits":
            self.tabs["siblings_kits_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1170, 890), (250, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/siblingkits_tab.png"
                    ).convert_alpha(),
                    (250, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "mates":
            self.tabs["mates_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1270, 890), (150, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/mates_tab.png"
                    ).convert_alpha(),
                    (150, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "kits":
            self.tabs["kits_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1306, 890), (114, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/kits_tab.png"
                    ).convert_alpha(),
                    (114, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "kits_mates":
            self.tabs["kits_mates_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1196, 890), (224, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/kitsmate_tab.png"
                    ).convert_alpha(),
                    (224, 60),
                ),
                manager=MANAGER,
            )
        elif self.current_group_name == "grandkits":
            self.tabs["grandkits_tab"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1220, 890), (200, 60))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/grandkits_tab.png"
                    ).convert_alpha(),
                    (200, 60),
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
