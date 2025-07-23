from typing import Optional

import i18n
import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache, constants
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UIRelationStatusBar,
    UISurfaceImageButton,
)
from scripts.game_structure.windows import RelationshipLog
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale_blit,
    ui_scale_offset,
)
from .Screens import Screens
from ..cat_relations.relationship import Relationship
from ..clan_package.settings import get_clan_setting
from ..clan_package.settings.clan_settings import set_clan_setting
from ..game_structure.game.settings import game_setting_get
from ..game_structure.game.switches import switch_set_value, switch_get_value, Switch
from ..game_structure.screen_settings import MANAGER, screen
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


class RelationshipScreen(Screens):
    checkboxes = {}  # To hold the checkboxes.
    focus_cat_elements = {}
    relation_list_elements = {}
    sprite_buttons = {}
    inspect_cat_elements = {}
    previous_search_text = ""

    current_page = 1

    inspect_cat: Optional[Cat] = None

    # this isn't actually used here (thought likely could, if anyone is looking to refactor a bit
    # rather this is used for the event editor, if changes are made to what each value is referred to in the code,
    # this should also change to reflect it so that the editor changes alongside it.
    # if you modify this, also add a matching string to resources/lang/en/screens/event_edit.en.json
    rel_value_names = (
        "romantic",
        "platonic",
        "dislike",
        "comfort",
        "jealousy",
        "respect",
        "trust",
    )

    def __init__(self, name=None):
        super().__init__(name)
        self.all_relations = None
        self.the_cat = None
        self.previous_cat = None
        self.next_cat = None
        self.view_profile_button = None
        self.switch_focus_button = None
        self.page_number = None
        self.next_page_button = None
        self.previous_page_button = None
        self.show_empty_text = None
        self.show_dead_text = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.log_icon = None

        self.search_bar_image = None
        self.details_frame_image = None
        self.toggle_frame_image = None
        self.list_frame_image = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element in self.sprite_buttons.values():
                self.inspect_cat = event.ui_element.return_cat_object()
                self.update_inspected_relation()
            elif event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.switch_focus_button:
                switch_set_value(Switch.cat, self.inspect_cat.ID)
                self.update_focus_cat()
            elif event.ui_element == self.view_profile_button:
                switch_set_value(Switch.cat, self.inspect_cat.ID)
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_focus_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_focus_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_page()
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_page()
            elif event.ui_element == self.log_icon:
                if self.inspect_cat.ID not in self.the_cat.relationships:
                    return
                if self.next_cat == 0 and self.previous_cat == 0:
                    RelationshipLog(
                        self.the_cat.relationships[self.inspect_cat.ID],
                        [
                            self.view_profile_button,
                            self.switch_focus_button,
                            self.next_page_button,
                            self.previous_cat_button,
                            self.next_page_button,
                        ],
                        [
                            self.back_button,
                            self.log_icon,
                            self.checkboxes["show_dead"],
                            self.checkboxes["show_empty"],
                            self.show_dead_text,
                            self.show_empty_text,
                        ],
                    )
                elif self.next_cat == 0:
                    RelationshipLog(
                        self.the_cat.relationships[self.inspect_cat.ID],
                        [
                            self.view_profile_button,
                            self.switch_focus_button,
                            self.previous_cat_button,
                            self.next_page_button,
                        ],
                        [
                            self.back_button,
                            self.log_icon,
                            self.checkboxes["show_dead"],
                            self.checkboxes["show_empty"],
                            self.show_dead_text,
                            self.show_empty_text,
                        ],
                    )
                elif self.previous_cat == 0:
                    RelationshipLog(
                        self.the_cat.relationships[self.inspect_cat.ID],
                        [
                            self.view_profile_button,
                            self.switch_focus_button,
                            self.next_cat_button,
                            self.next_page_button,
                        ],
                        [
                            self.back_button,
                            self.log_icon,
                            self.checkboxes["show_dead"],
                            self.checkboxes["show_empty"],
                            self.show_dead_text,
                            self.show_empty_text,
                        ],
                    )
                else:
                    RelationshipLog(
                        self.the_cat.relationships[self.inspect_cat.ID],
                        [
                            self.view_profile_button,
                            self.switch_focus_button,
                            self.next_page_button,
                            self.next_cat_button,
                            self.previous_cat_button,
                            self.next_page_button,
                        ],
                        [
                            self.back_button,
                            self.log_icon,
                            self.checkboxes["show_dead"],
                            self.checkboxes["show_empty"],
                            self.show_dead_text,
                            self.show_empty_text,
                        ],
                    )
            elif event.ui_element == self.checkboxes["show_dead"]:
                set_clan_setting(
                    "show dead relation", not get_clan_setting("show dead relation")
                )
                self.update_checkboxes()
                self.apply_cat_filter()
                self.update_cat_page()
            elif event.ui_element == self.checkboxes["show_empty"]:
                set_clan_setting(
                    "show empty relation", not get_clan_setting("show empty relation")
                )
                self.update_checkboxes()
                self.apply_cat_filter()
                self.update_cat_page()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

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
            sound_id="page_flip",
            manager=MANAGER,
        )

        back_rect = ui_scale(pygame.Rect((0, 0), (105, 30)))
        back_rect.bottomleft = ui_scale_offset((25, -25))
        self.back_button = UISurfaceImageButton(
            back_rect,
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"bottom": "bottom", "left": "left"},
        )

        self.search_bar = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((610, 97), (145, 23))), object_id="#search_entry_box"
        )

        self.search_bar_image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/relationship_search.png"
            ).convert_alpha(),
            ui_scale_dimensions((228, 39)),
        )
        self.details_frame_image = get_box(
            BoxStyles.ROUNDED_BOX, (230, 340), sides=(True, False, True, True)
        )
        self.selected_cat_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((53, 143), (220, 320))), MANAGER
        )
        self.toggle_frame_image = get_box(
            BoxStyles.ROUNDED_BOX, (220, 120), sides=(True, False, True, True)
        )

        self.list_frame_image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/relationship_list_frame.png"
            ).convert_alpha(),
            ui_scale_dimensions((502, 500)),
        )

        self.show_dead_text = pygame_gui.elements.UITextBox(
            "screens.relationship.show_dead_checkbox",
            ui_scale(pygame.Rect((110, 505), (100, 30))),
            object_id="#text_box_30_horizleft",
        )
        self.show_empty_text = pygame_gui.elements.UITextBox(
            "screens.relationship.show_empty_checkbox",
            ui_scale(pygame.Rect((110, 550), (100, 30))),
            object_id="#text_box_30_horizleft",
        )

        # Draw the checkboxes
        self.update_checkboxes()

        self.page_number = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((125, 617), (100, 34))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            anchors={"centerx": "centerx"},
        )

        rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
        rect.topright = ui_scale_offset((-25, 616))
        self.previous_page_button = UISurfaceImageButton(
            rect,
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            anchors={"right": "right", "top": "top", "right_target": self.page_number},
        )
        del rect

        self.next_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 616), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            anchors={"left_target": self.page_number},
        )

        self.switch_focus_button = UIImageButton(
            ui_scale(pygame.Rect((32, 245), (136, 30))),
            "",
            object_id="#switch_focus_button",
            container=self.selected_cat_container,
        )
        self.switch_focus_button.disable()
        self.view_profile_button = UIImageButton(
            ui_scale(pygame.Rect((32, 275), (136, 30))),
            "",
            object_id="#view_profile_button",
            container=self.selected_cat_container,
        )
        self.view_profile_button.disable()

        self.log_icon = UISurfaceImageButton(
            ui_scale(pygame.Rect((169, 258), (34, 34))),
            Icon.NOTEPAD,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.selected_cat_container,
        )
        self.log_icon.disable()

        # Updates all info for the currently focused cat.
        self.update_focus_cat()

    def exit_screen(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        self.selected_cat_container.kill()

        for ele in self.focus_cat_elements:
            self.focus_cat_elements[ele].kill()
        self.focus_cat_elements = {}

        for ele in self.relation_list_elements:
            self.relation_list_elements[ele].kill()
        self.relation_list_elements = {}

        for ele in self.sprite_buttons:
            self.sprite_buttons[ele].kill()
        self.sprite_buttons = {}

        for ele in self.inspect_cat_elements:
            self.inspect_cat_elements[ele].kill()
        self.inspect_cat_elements = {}

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.search_bar.kill()
        del self.search_bar
        self.show_dead_text.kill()
        del self.show_dead_text
        self.show_empty_text.kill()
        del self.show_empty_text
        self.previous_page_button.kill()
        del self.previous_page_button
        self.next_page_button.kill()
        del self.next_page_button
        self.page_number.kill()
        del self.page_number
        self.switch_focus_button.kill()
        del self.switch_focus_button
        self.view_profile_button.kill()
        del self.view_profile_button
        self.log_icon.kill()
        del self.log_icon

    def update_checkboxes(self):
        # Remove all checkboxes
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        self.checkboxes["show_dead"] = UIImageButton(
            ui_scale(pygame.Rect((78, 505), (34, 34))),
            "",
            object_id=(
                "@checked_checkbox"
                if get_clan_setting("show dead relation")
                else "@unchecked_checkbox"
            ),
        )

        self.checkboxes["show_empty"] = UIImageButton(
            ui_scale(pygame.Rect((78, 550), (34, 34))),
            "",
            object_id=(
                "@checked_checkbox"
                if get_clan_setting("show empty relation")
                else "@unchecked_checkbox"
            ),
        )

    def update_focus_cat(self):
        for ele in self.focus_cat_elements:
            self.focus_cat_elements[ele].kill()
        self.focus_cat_elements = {}

        self.the_cat = Cat.all_cats.get(
            switch_get_value(Switch.cat), game.clan.instructor
        )

        self.current_page = 1
        self.inspect_cat = None

        # Keep a list of all the relations
        if constants.CONFIG["sorting"]["sort_by_rel_total"]:
            self.all_relations = sorted(
                self.the_cat.relationships.values(),
                key=lambda x: sum(
                    map(
                        abs,
                        [
                            x.romantic_love,
                            x.platonic_like,
                            x.dislike,
                            x.admiration,
                            x.comfortable,
                            x.jealousy,
                            x.trust,
                        ],
                    )
                ),
                reverse=True,
            )
        else:
            self.all_relations = list(self.the_cat.relationships.values()).copy()

        self.focus_cat_elements["header"] = pygame_gui.elements.UITextBox(
            "screens.relationship.heading",
            ui_scale(pygame.Rect((75, 75), (400, 50))),
            object_id=get_text_box_theme("#text_box_34_horizleft"),
            text_kwargs={"m_c": self.the_cat},
        )
        self.focus_cat_elements["details"] = pygame_gui.elements.UITextBox(
            self.the_cat.get_info_block(relationship=True),
            ui_scale(pygame.Rect((80, 105), (400, 30))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
        )
        self.focus_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((25, 75), (50, 50))), self.the_cat.sprite
        )

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

        self.apply_cat_filter(self.search_bar.get_text())
        self.update_inspected_relation()
        self.update_cat_page()

    def update_inspected_relation(self):
        for ele in self.inspect_cat_elements:
            self.inspect_cat_elements[ele].kill()
        self.inspect_cat_elements = {}

        if self.inspect_cat is not None:
            # NAME LENGTH
            chosen_name = shorten_text_to_fit(str(self.inspect_cat.name), 180, 18)

            self.inspect_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((0, 152), (180, 40))),
                chosen_name,
                object_id="#text_box_34_horizcenter",
                container=self.selected_cat_container,
                anchors={"centerx": "centerx"},
            )

            # Cat Image
            self.inspect_cat_elements["image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (150, 150))),
                pygame.transform.scale(
                    self.inspect_cat.sprite, ui_scale_dimensions((150, 150))
                ),
                container=self.selected_cat_container,
                anchors={"centerx": "centerx"},
            )

            related = False
            # Mate Heart
            if len(self.the_cat.mate) > 0 and self.inspect_cat.ID in self.the_cat.mate:
                self.inspect_cat_elements["mate"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((8, 8), (22, 20))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/heart_big.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((22, 20)),
                    ),
                    container=self.selected_cat_container,
                )
            else:
                # Family Dot
                related = self.the_cat.is_related(
                    self.inspect_cat, get_clan_setting("first cousin mates")
                )
                if related:
                    self.inspect_cat_elements["family"] = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((10, 8), (18, 18))),
                        pygame.transform.scale(
                            image_cache.load_image(
                                "resources/images/dot_big.png"
                            ).convert_alpha(),
                            ui_scale_dimensions((18, 18)),
                        ),
                        container=self.selected_cat_container,
                    )

            # Gender
            if self.inspect_cat.genderalign == "female":
                gender_icon = image_cache.load_image(
                    "resources/images/female_big.png"
                ).convert_alpha()
            elif self.inspect_cat.genderalign == "male":
                gender_icon = image_cache.load_image(
                    "resources/images/male_big.png"
                ).convert_alpha()
            elif self.inspect_cat.genderalign == "trans female":
                gender_icon = image_cache.load_image(
                    "resources/images/transfem_big.png"
                ).convert_alpha()
            elif self.inspect_cat.genderalign == "trans male":
                gender_icon = image_cache.load_image(
                    "resources/images/transmasc_big.png"
                ).convert_alpha()
            else:
                # Everyone else gets the nonbinary icon
                gender_icon = image_cache.load_image(
                    "resources/images/nonbi_big.png"
                ).convert_alpha()

            gender_rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
            gender_rect.topright = ui_scale_offset((-3, 3))
            self.inspect_cat_elements["gender"] = pygame_gui.elements.UIImage(
                gender_rect,
                pygame.transform.scale(gender_icon, ui_scale_dimensions((34, 34))),
                container=self.selected_cat_container,
                anchors={"right": "right", "top": "top"},
            )
            del gender_rect

            # Column One Details:
            self.inspect_cat_elements["col1"] = pygame_gui.elements.UITextBox(
                self.inspect_cat.get_info_block(relationship=True),
                ui_scale(pygame.Rect((15, 185), (90, 70))),
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
                container=self.selected_cat_container,
            )

            # Column Two Details:
            col2 = []

            # Mate
            if (
                len(self.inspect_cat.mate) > 0
                and self.the_cat.ID not in self.inspect_cat.mate
            ):
                col2.append(i18n.t("general.has_a_mate"))
            elif (
                len(self.the_cat.mate) > 0 and self.inspect_cat.ID in self.the_cat.mate
            ):
                col2.append(i18n.t("general.has_a_mate", name=self.the_cat.name))
            else:
                col2.append(i18n.t("general.mate_none"))

            # Relation info:
            if related:
                relation = ""
                if self.the_cat.is_uncle_aunt(self.inspect_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.niece"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.nephew"
                    else:
                        relation = "general.siblings_child"
                elif self.inspect_cat.is_uncle_aunt(self.the_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.aunt"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.uncle"
                    else:
                        relation = "general.parents_sibling"
                elif self.inspect_cat.is_grandparent(self.the_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.grandmother"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.grandfather"
                    else:
                        relation = "general.grandparent"
                elif self.the_cat.is_grandparent(self.inspect_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.granddaughter"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.grandson"
                    else:
                        relation = "general.grandchild"
                elif self.inspect_cat.is_parent(self.the_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.mother"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.father"
                    else:
                        relation = "general.parent"
                elif self.the_cat.is_parent(self.inspect_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.daughter"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.son"
                    else:
                        relation = "general.child"
                elif self.inspect_cat.is_sibling(
                    self.the_cat
                ) or self.the_cat.is_sibling(self.inspect_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.sister"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.brother"
                    else:
                        relation = "general.sibling"

                    if self.inspect_cat.is_littermate(
                        self.the_cat
                    ) or self.the_cat.is_littermate(self.inspect_cat):
                        relation = i18n.t(
                            "general.sibling_littermate", relation=i18n.t(relation)
                        )
                elif not get_clan_setting(
                    "first cousin mates"
                ) and self.inspect_cat.is_cousin(self.the_cat):
                    if self.inspect_cat.genderalign in ("female", "trans female"):
                        relation = "general.cousin_female"
                    elif self.inspect_cat.genderalign in ("male", "trans male"):
                        relation = "general.cousin_male"
                    else:
                        relation = "general.cousin_nb"
                col2.append(i18n.t("general.related_label", relation=i18n.t(relation)))

            col2_rect = ui_scale(pygame.Rect((0, 0), (90, 70)))
            col2_rect.topright = ui_scale_offset((-15, 185))

            self.inspect_cat_elements["col2"] = pygame_gui.elements.UITextBox(
                "\n".join(col2),
                col2_rect,
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
                container=self.selected_cat_container,
                anchors={"right": "right", "top": "top"},
                text_kwargs={"m_c": self.inspect_cat},
            )
            del col2_rect

            if self.inspect_cat.dead:
                self.view_profile_button.enable()
                self.switch_focus_button.disable()
                self.log_icon.enable()
            else:
                self.view_profile_button.enable()
                self.switch_focus_button.enable()
                self.log_icon.enable()
        else:
            self.view_profile_button.disable()
            self.switch_focus_button.disable()
            self.log_icon.disable()

    def apply_cat_filter(self, search_text=""):
        # Filter for dead or empty cats
        self.filtered_cats = self.all_relations.copy()
        if not get_clan_setting("show dead relation"):
            self.filtered_cats = list(
                filter(lambda rel: not rel.cat_to.dead, self.filtered_cats)
            )

        if not get_clan_setting("show empty relation"):
            self.filtered_cats = list(
                filter(
                    lambda rel: (
                        rel.romantic_love
                        + rel.platonic_like
                        + rel.dislike
                        + rel.admiration
                        + rel.comfortable
                        + rel.jealousy
                        + rel.trust
                    )
                    > 0,
                    self.filtered_cats,
                )
            )

        # Filter for search
        search_cats = []
        if search_text.strip() != "":
            for cat in self.filtered_cats:
                if search_text.lower() in str(cat.cat_to.name).lower():
                    search_cats.append(cat)
            self.filtered_cats = search_cats

    def update_cat_page(self):
        for ele in self.relation_list_elements:
            self.relation_list_elements[ele].kill()
        self.relation_list_elements = {}

        for ele in self.sprite_buttons:
            self.sprite_buttons[ele].kill()
        self.sprite_buttons = {}

        all_pages = self.chunks(self.filtered_cats, 8)

        self.current_page = max(1, min(self.current_page, len(all_pages)))

        if all_pages:
            display_rel = all_pages[self.current_page - 1]
        else:
            display_rel = []

        pos_x = 290
        pos_y = 150
        i = 0
        for rel in display_rel:
            self.generate_relation_block((pos_x, pos_y), rel, i)

            i += 1
            pos_x += 122
            if pos_x > 700:
                pos_y += 242
                pos_x = 290

        self.page_number.set_text(f"{self.current_page} / {len(all_pages)}")

        # Enable and disable page buttons.
        if len(all_pages) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(all_pages):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(all_pages) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()

    def generate_relation_block(self, pos, the_relationship: "Relationship", i):
        # Generates a relation_block starting at postion, from the relationship object "the_relation"
        # "position" should refer to the top left corner of the *main* relation box, not including the name.
        pos_x = pos[0]
        pos_y = pos[1]

        self.sprite_buttons["image" + str(i)] = UISpriteButton(
            ui_scale(pygame.Rect((pos_x + 22, pos_y), (50, 50))),
            the_relationship.cat_to.sprite,
            cat_object=the_relationship.cat_to,
        )

        # CHECK NAME LENGTH - SHORTEN IF NECESSARY
        name = str(the_relationship.cat_to.name)  # get name
        short_name = shorten_text_to_fit(name, 90, 13)
        self.relation_list_elements["name" + str(i)] = pygame_gui.elements.UITextBox(
            short_name,
            ui_scale(pygame.Rect((pos_x - 5, pos_y - 25), (110, 30))),
            object_id="#text_box_26_horizcenter",
        )

        # Gender alignment
        if the_relationship.cat_to.genderalign == "female":
            gender_icon = image_cache.load_image(
                "resources/images/female_big.png"
            ).convert_alpha()
        elif the_relationship.cat_to.genderalign == "male":
            gender_icon = image_cache.load_image(
                "resources/images/male_big.png"
            ).convert_alpha()
        elif the_relationship.cat_to.genderalign == "trans female":
            gender_icon = image_cache.load_image(
                "resources/images/transfem_big.png"
            ).convert_alpha()
        elif the_relationship.cat_to.genderalign == "trans male":
            gender_icon = image_cache.load_image(
                "resources/images/transmasc_big.png"
            ).convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image(
                "resources/images/nonbi_big.png"
            ).convert_alpha()

        self.relation_list_elements["gender" + str(i)] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((pos_x + 80, pos_y + 5), (18, 18))),
            pygame.transform.scale(gender_icon, ui_scale_dimensions((18, 18))),
        )

        related = False
        # MATE
        if (
            len(self.the_cat.mate) > 0
            and the_relationship.cat_to.ID in self.the_cat.mate
        ):
            self.relation_list_elements[
                "mate_icon" + str(i)
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((pos_x + 5, pos_y + 5), (11, 10))),
                image_cache.load_image(
                    "resources/images/heart_big.png"
                ).convert_alpha(),
            )
        else:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if get_clan_setting("first cousin mates"):
                check_cousins = False
            else:
                check_cousins = the_relationship.cat_to.is_cousin(self.the_cat)

            if (
                the_relationship.cat_to.is_uncle_aunt(self.the_cat)
                or self.the_cat.is_uncle_aunt(the_relationship.cat_to)
                or the_relationship.cat_to.is_grandparent(self.the_cat)
                or self.the_cat.is_grandparent(the_relationship.cat_to)
                or the_relationship.cat_to.is_parent(self.the_cat)
                or self.the_cat.is_parent(the_relationship.cat_to)
                or the_relationship.cat_to.is_sibling(self.the_cat)
                or check_cousins
            ):
                related = True
                self.relation_list_elements[
                    "relation_icon" + str(i)
                ] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((pos_x + 5, pos_y + 5), (9, 9))),
                    image_cache.load_image(
                        "resources/images/dot_big.png"
                    ).convert_alpha(),
                )

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        # ROMANTIC LOVE
        # CHECK AGE DIFFERENCE
        same_age = the_relationship.cat_to.age == self.the_cat.age
        adult_ages = ["young adult", "adult", "senior adult", "senior"]
        both_adult = (
            the_relationship.cat_to.age in adult_ages and self.the_cat.age in adult_ages
        )
        check_age = both_adult or same_age

        # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
        # even if they somehow have some. They should not be able to get any, but it never hurts to check.
        if not check_age or related:
            display_romantic = 0
            # Print, just for bug checking. Again, they should not be able to get love towards their relative.
            if the_relationship.romantic_love and related:
                print(
                    f"WARNING: {self.the_cat.name} has {the_relationship.romantic_love} romantic love towards their relative, {the_relationship.cat_to.name}"
                )
        else:
            display_romantic = the_relationship.romantic_love

        # determine placing on screen
        barbar = 22
        bar_count = 0

        rel_pos_x = pos_x + 3
        text_pos_y = pos_y + 45
        bar_pos_y = pos_y + 65

        text_size_x = -1
        text_size_y = 30

        bar_size_x = 94
        bar_size_y = 10

        self.relation_list_elements[
            f"romantic_text{i}"
        ] = pygame_gui.elements.UITextBox(
            "relationships.romantic_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if display_romantic > 49 else 1},
        )
        self.relation_list_elements[f"romantic_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            display_romantic,
            positive_trait=True,
            dark_mode=game_setting_get("dark mode"),
        )
        bar_count += 1

        # PLATONIC
        self.relation_list_elements[
            f"platonic_text{i}"
        ] = pygame_gui.elements.UITextBox(
            "relationships.platonic_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if the_relationship.platonic_like > 49 else 1},
        )
        self.relation_list_elements[f"platonic_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.platonic_like,
            positive_trait=True,
            dark_mode=game_setting_get("dark mode"),
        )

        bar_count += 1

        # DISLIKE
        self.relation_list_elements[f"dislike_text{i}"] = pygame_gui.elements.UITextBox(
            "relationships.dislike_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if the_relationship.dislike > 49 else 1},
        )
        self.relation_list_elements[f"dislike_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect((rel_pos_x, bar_pos_y + (barbar * bar_count)), (94, 10))
            ),
            the_relationship.dislike,
            positive_trait=False,
            dark_mode=game_setting_get("dark mode"),
        )

        bar_count += 1

        # ADMIRE
        self.relation_list_elements[
            f"admiration_text{i}"
        ] = pygame_gui.elements.UITextBox(
            "relationships.admire_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if the_relationship.admiration > 49 else 1},
        )
        self.relation_list_elements[f"admiration_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.admiration,
            positive_trait=True,
            dark_mode=game_setting_get("dark mode"),
        )

        bar_count += 1

        # COMFORTABLE
        self.relation_list_elements[
            f"comfortable_text{i}"
        ] = pygame_gui.elements.UITextBox(
            "relationships.comfortable_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if the_relationship.comfortable > 49 else 1},
        )
        self.relation_list_elements[f"comfortable_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.comfortable,
            positive_trait=True,
            dark_mode=game_setting_get("dark mode"),
        )

        bar_count += 1

        # JEALOUS
        self.relation_list_elements[f"jealous_text{i}"] = pygame_gui.elements.UITextBox(
            "relationships.jealous_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if the_relationship.jealousy > 49 else 1},
        )
        self.relation_list_elements[f"jealous_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.jealousy,
            positive_trait=False,
            dark_mode=game_setting_get("dark mode"),
        )

        bar_count += 1

        # TRUST
        self.relation_list_elements[f"trust_text{i}"] = pygame_gui.elements.UITextBox(
            "relationships.trust_label",
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
            text_kwargs={"count": 2 if the_relationship.trust > 49 else 1},
        )
        self.relation_list_elements[f"trust_bar{i}"] = UIRelationStatusBar(
            ui_scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.trust,
            positive_trait=True,
            dark_mode=game_setting_get("dark mode"),
        )

    def on_use(self):
        super().on_use()

        # LOAD UI IMAGES
        screen.blit(self.search_bar_image, ui_scale_blit((535, 90)))
        screen.blit(
            self.details_frame_image,
            ui_scale_blit((43, 133)),
        )
        screen.blit(
            self.toggle_frame_image,
            ui_scale_blit((53, 482)),
        )
        screen.blit(self.list_frame_image, ui_scale_blit((273, 122)))

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.apply_cat_filter(self.search_bar.get_text())
            self.update_cat_page()
        self.previous_search_text = self.search_bar.get_text()

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
