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
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UIRelationStatusBar,
)
from scripts.game_structure.windows import RelationshipLog
from scripts.utility import (
    get_text_box_theme,
    scale,
    shorten_text_to_fit,
)
from .Screens import Screens


class RelationshipScreen(Screens):
    checkboxes = {}  # To hold the checkboxes.
    focus_cat_elements = {}
    relation_list_elements = {}
    sprite_buttons = {}
    inspect_cat_elements = {}
    previous_search_text = ""

    current_page = 1

    inspect_cat = None

    search_bar = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_search.png"
        ).convert_alpha(),
        (456 / 1600 * screen_x, 78 / 1400 * screen_y),
    )
    details_frame = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_details_frame.png"
        ).convert_alpha(),
        (508 / 1600 * screen_x, 688 / 1400 * screen_y),
    )
    toggle_frame = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_toggle_frame.png"
        ).convert_alpha(),
        (502 / 1600 * screen_x, 240 / 1400 * screen_y),
    )
    list_frame = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_list_frame.png"
        ).convert_alpha(),
        (1004 / 1600 * screen_x, 1000 / 1400 * screen_y),
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

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element in self.sprite_buttons.values():
                self.inspect_cat = event.ui_element.return_cat_object()
                self.update_inspected_relation()
            elif event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.switch_focus_button:
                game.switches["cat"] = self.inspect_cat.ID
                self.update_focus_cat()
            elif event.ui_element == self.view_profile_button:
                game.switches["cat"] = self.inspect_cat.ID
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_focus_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
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
                game.clan.clan_settings["show dead relation"] = (
                    not game.clan.clan_settings["show dead relation"]
                )
                self.update_checkboxes()
                self.apply_cat_filter()
                self.update_cat_page()
            elif event.ui_element == self.checkboxes["show_empty"]:
                game.clan.clan_settings["show empty relation"] = (
                    not game.clan.clan_settings["show empty relation"]
                )
                self.update_checkboxes()
                self.apply_cat_filter()
                self.update_cat_page()

    def screen_switches(self):
        self.show_mute_buttons()

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

        self.search_bar = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((1220, 194), (290, 46))), object_id="#search_entry_box"
        )

        self.show_dead_text = pygame_gui.elements.UITextBox(
            "Show Dead",
            scale(pygame.Rect((220, 1010), (200, 60))),
            object_id="#text_box_30_horizleft",
        )
        self.show_empty_text = pygame_gui.elements.UITextBox(
            "Show Empty",
            scale(pygame.Rect((220, 1100), (200, 60))),
            object_id="#text_box_30_horizleft",
        )

        # Draw the checkboxes
        self.update_checkboxes()

        self.previous_page_button = UIImageButton(
            scale(pygame.Rect((880, 1232), (68, 68))),
            "",
            object_id="#relation_list_previous",
        )
        self.next_page_button = UIImageButton(
            scale(pygame.Rect((1160, 1232), (68, 68))),
            "",
            object_id="#relation_list_next",
        )

        self.page_number = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((890, 1234), (300, 68))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
        )

        self.switch_focus_button = UIImageButton(
            scale(pygame.Rect((170, 780), (272, 60))),
            "",
            object_id="#switch_focus_button",
        )
        self.switch_focus_button.disable()
        self.view_profile_button = UIImageButton(
            scale(pygame.Rect((170, 840), (272, 60))),
            "",
            object_id="#view_profile_button",
        )
        self.view_profile_button.disable()

        self.log_icon = UIImageButton(
            scale(pygame.Rect((445, 808), (68, 68))), "", object_id="#log_icon"
        )
        self.log_icon.disable()

        # Updates all info for the currently focused cat.
        self.update_focus_cat()

    def exit_screen(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

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

    def get_previous_next_cat(self):
        """Determines where the previous the next buttons should lead, and enables/diables them"""
        """'Determines where the next and previous buttons point too."""

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

    def update_checkboxes(self):
        # Remove all checkboxes
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        if game.clan.clan_settings["show dead relation"]:
            checkbox_type = "#checked_checkbox"
        else:
            checkbox_type = "#unchecked_checkbox"

        self.checkboxes["show_dead"] = UIImageButton(
            scale(pygame.Rect((156, 1010), (68, 68))), "", object_id=checkbox_type
        )

        if game.clan.clan_settings["show empty relation"]:
            checkbox_type = "#checked_checkbox"
        else:
            checkbox_type = "#unchecked_checkbox"

        self.checkboxes["show_empty"] = UIImageButton(
            scale(pygame.Rect((156, 1100), (68, 68))), "", object_id=checkbox_type
        )

    def update_focus_cat(self):
        for ele in self.focus_cat_elements:
            self.focus_cat_elements[ele].kill()
        self.focus_cat_elements = {}

        self.the_cat = Cat.all_cats.get(game.switches["cat"], game.clan.instructor)

        self.current_page = 1
        self.inspect_cat = None

        # Keep a list of all the relations
        if game.config["sorting"]["sort_by_rel_total"]:
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
            str(self.the_cat.name) + " Relationships",
            scale(pygame.Rect((150, 150), (800, 100))),
            object_id=get_text_box_theme("#text_box_34_horizleft"),
        )
        self.focus_cat_elements["details"] = pygame_gui.elements.UITextBox(
            self.the_cat.genderalign
            + " - "
            + str(self.the_cat.moons)
            + " moons - "
            + self.the_cat.personality.trait,
            scale(pygame.Rect((160, 210), (800, 60))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
        )
        self.focus_cat_elements["image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((50, 150), (100, 100))), self.the_cat.sprite
        )

        self.get_previous_next_cat()
        self.apply_cat_filter(self.search_bar.get_text())
        self.update_inspected_relation()
        self.update_cat_page()

    def update_inspected_relation(self):
        for ele in self.inspect_cat_elements:
            self.inspect_cat_elements[ele].kill()
        self.inspect_cat_elements = {}

        if self.inspect_cat is not None:
            # NAME LENGTH
            chosen_name = str(self.inspect_cat.name)
            if 19 <= len(chosen_name):
                if self.inspect_cat.dead:
                    chosen_short_name = str(self.inspect_cat.name)[0:11]
                    chosen_name = chosen_short_name + "..."
                    chosen_name += " (dead)"
                else:
                    chosen_short_name = str(self.inspect_cat.name)[0:16]
                    chosen_name = chosen_short_name + "..."

            self.inspect_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((150, 590), (300, 80))),
                chosen_name,
                object_id="#text_box_34_horizcenter",
            )

            # Cat Image
            self.inspect_cat_elements["image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((150, 290), (300, 300))),
                pygame.transform.scale(self.inspect_cat.sprite, (300, 300)),
            )

            related = False
            # Mate Heart
            # TODO: UI UPDATE IS NEEDED
            if len(self.the_cat.mate) > 0 and self.inspect_cat.ID in self.the_cat.mate:
                self.inspect_cat_elements["mate"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((90, 300), (44, 40))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/heart_big.png"
                        ).convert_alpha(),
                        (44, 40),
                    ),
                )
            else:
                # Family Dot
                related = self.the_cat.is_related(
                    self.inspect_cat, game.clan.clan_settings["first cousin mates"]
                )
                if related:
                    self.inspect_cat_elements["family"] = pygame_gui.elements.UIImage(
                        scale(pygame.Rect((90, 300), (36, 36))),
                        pygame.transform.scale(
                            image_cache.load_image(
                                "resources/images/dot_big.png"
                            ).convert_alpha(),
                            (36, 36),
                        ),
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

            self.inspect_cat_elements["gender"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((470, 290), (68, 68))),
                pygame.transform.scale(gender_icon, (68, 68)),
            )

            # Column One Details:
            col1 = ""
            # Gender-Align
            col1 += self.inspect_cat.genderalign + "\n"

            # Age
            col1 += f"{self.inspect_cat.moons} moons\n"

            # Trait
            col1 += f"{self.inspect_cat.personality.trait}\n"

            self.inspect_cat_elements["col1"] = pygame_gui.elements.UITextBox(
                col1,
                scale(pygame.Rect((120, 650), (180, 180))),
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
            )

            # Column Two Details:
            col2 = ""

            # Mate
            if (
                len(self.inspect_cat.mate) > 0
                and self.the_cat.ID not in self.inspect_cat.mate
            ):
                col2 += "has a mate\n"
            elif (
                len(self.the_cat.mate) > 0 and self.inspect_cat.ID in self.the_cat.mate
            ):
                col2 += f"{self.the_cat.name}'s mate\n"
            else:
                col2 += "mate: none\n"

            # Relation info:
            if related:
                if self.the_cat.is_uncle_aunt(self.inspect_cat):
                    if self.inspect_cat.genderalign in ["female", "trans female"]:
                        col2 += "related: niece"
                    elif self.inspect_cat.genderalign in ["male", "trans male"]:
                        col2 += "related: nephew"
                    else:
                        col2 += "related: sibling's child\n"
                elif self.inspect_cat.is_uncle_aunt(self.the_cat):
                    if self.inspect_cat.genderalign in ["female", "trans female"]:
                        col2 += "related: aunt"
                    elif self.inspect_cat.genderalign in ["male", "trans male"]:
                        col2 += "related: uncle"
                    else:
                        col2 += "related: parent's sibling"
                elif self.inspect_cat.is_grandparent(self.the_cat):
                    col2 += "related: grandparent"
                elif self.the_cat.is_grandparent(self.inspect_cat):
                    col2 += "related: grandchild"
                elif self.inspect_cat.is_parent(self.the_cat):
                    col2 += "related: parent"
                elif self.the_cat.is_parent(self.inspect_cat):
                    col2 += "related: child"
                elif self.inspect_cat.is_sibling(
                    self.the_cat
                ) or self.the_cat.is_sibling(self.inspect_cat):
                    if self.inspect_cat.is_littermate(
                        self.the_cat
                    ) or self.the_cat.is_littermate(self.inspect_cat):
                        col2 += "related: sibling (littermate)"
                    else:
                        col2 += "related: sibling"
                elif not game.clan.clan_settings[
                    "first cousin mates"
                ] and self.inspect_cat.is_cousin(self.the_cat):
                    col2 += "related: cousin"

            self.inspect_cat_elements["col2"] = pygame_gui.elements.UITextBox(
                col2,
                scale(pygame.Rect((300, 650), (180, 180))),
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
            )

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
        if not game.clan.clan_settings["show dead relation"]:
            self.filtered_cats = list(
                filter(lambda rel: not rel.cat_to.dead, self.filtered_cats)
            )

        if not game.clan.clan_settings["show empty relation"]:
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

        pos_x = 580
        pos_y = 300
        i = 0
        for rel in display_rel:
            self.generate_relation_block((pos_x, pos_y), rel, i)

            i += 1
            pos_x += 244
            if pos_x > 1400:
                pos_y += 484
                pos_x = 580

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

    def generate_relation_block(self, pos, the_relationship, i):
        # Generates a relation_block starting at postion, from the relationship object "the_relation"
        # "position" should refer to the top left corner of the *main* relation box, not including the name.
        pos_x = pos[0]
        pos_y = pos[1]

        self.sprite_buttons["image" + str(i)] = UISpriteButton(
            scale(pygame.Rect((pos_x + 44, pos_y), (100, 100))),
            the_relationship.cat_to.sprite,
            cat_object=the_relationship.cat_to,
        )

        # CHECK NAME LENGTH - SHORTEN IF NECESSARY
        name = str(the_relationship.cat_to.name)  # get name
        short_name = shorten_text_to_fit(name, 210, 26)
        self.relation_list_elements["name" + str(i)] = pygame_gui.elements.UITextBox(
            short_name,
            scale(pygame.Rect((pos_x - 10, pos_y - 50), (220, 60))),
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
            scale(pygame.Rect((pos_x + 160, pos_y + 10), (36, 36))),
            pygame.transform.scale(gender_icon, (36, 36)),
        )

        related = False
        # MATE
        if (
            len(self.the_cat.mate) > 0
            and the_relationship.cat_to.ID in self.the_cat.mate
        ):

            self.relation_list_elements["mate_icon" + str(i)] = (
                pygame_gui.elements.UIImage(
                    scale(pygame.Rect((pos_x + 10, pos_y + 10), (22, 20))),
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                )
            )
        else:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if game.clan.clan_settings["first cousin mates"]:
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
                self.relation_list_elements["relation_icon" + str(i)] = (
                    pygame_gui.elements.UIImage(
                        scale(pygame.Rect((pos_x + 10, pos_y + 10), (18, 18))),
                        image_cache.load_image(
                            "resources/images/dot_big.png"
                        ).convert_alpha(),
                    )
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

        if display_romantic > 49:
            text = "romantic love:"
        else:
            text = "romantic like:"

        # determine placing on screen
        barbar = 44
        bar_count = 0

        # fix text positioning on fullscreen
        if game.settings["fullscreen"]:
            f_add = 5
        else:
            f_add = 0

        rel_pos_x = pos_x + 6
        text_pos_y = pos_y + f_add + 87
        bar_pos_y = pos_y + 130

        text_size_x = -1
        text_size_y = 60

        bar_size_x = 188
        bar_size_y = 20

        self.relation_list_elements[f"romantic_text{i}"] = (
            pygame_gui.elements.UITextBox(
                text,
                scale(
                    pygame.Rect(
                        (rel_pos_x, text_pos_y + (barbar * bar_count)),
                        (text_size_x, text_size_y),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
        )
        self.relation_list_elements[f"romantic_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            display_romantic,
            positive_trait=True,
            dark_mode=game.settings["dark mode"],
        )
        bar_count += 1

        # PLANTONIC
        if the_relationship.platonic_like > 49:
            text = "platonic love:"
        else:
            text = "platonic like:"
        self.relation_list_elements[f"plantonic_text{i}"] = (
            pygame_gui.elements.UITextBox(
                text,
                scale(
                    pygame.Rect(
                        (rel_pos_x, text_pos_y + (barbar * bar_count)),
                        (text_size_x, text_size_y),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
        )
        self.relation_list_elements[f"platonic_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.platonic_like,
            positive_trait=True,
            dark_mode=game.settings["dark mode"],
        )

        bar_count += 1

        # DISLIKE
        if the_relationship.dislike > 49:
            text = "hate:"
        else:
            text = "dislike:"
        self.relation_list_elements[f"dislike_text{i}"] = pygame_gui.elements.UITextBox(
            text,
            scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
        )
        self.relation_list_elements[f"dislike_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect((rel_pos_x, bar_pos_y + (barbar * bar_count)), (188, 20))
            ),
            the_relationship.dislike,
            positive_trait=False,
            dark_mode=game.settings["dark mode"],
        )

        bar_count += 1

        # ADMIRE
        if the_relationship.admiration > 49:
            text = "admiration:"
        else:
            text = "respect:"
        self.relation_list_elements[f"admiration_text{i}"] = (
            pygame_gui.elements.UITextBox(
                text,
                scale(
                    pygame.Rect(
                        (rel_pos_x, text_pos_y + (barbar * bar_count)),
                        (text_size_x, text_size_y),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
        )
        self.relation_list_elements[f"admiration_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.admiration,
            positive_trait=True,
            dark_mode=game.settings["dark mode"],
        )

        bar_count += 1

        # COMFORTABLE
        if the_relationship.comfortable > 49:
            text = "security:"
        else:
            text = "comfort:"
        self.relation_list_elements[f"comfortable_text{i}"] = (
            pygame_gui.elements.UITextBox(
                text,
                scale(
                    pygame.Rect(
                        (rel_pos_x, text_pos_y + (barbar * bar_count)),
                        (text_size_x, text_size_y),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
        )
        self.relation_list_elements[f"comfortable_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.comfortable,
            positive_trait=True,
            dark_mode=game.settings["dark mode"],
        )

        bar_count += 1

        # JEALOUS
        if the_relationship.jealousy > 49:
            text = "resentment:"
        else:
            text = "jealousy:"
        self.relation_list_elements[f"jealous_text{i}"] = pygame_gui.elements.UITextBox(
            text,
            scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
        )
        self.relation_list_elements[f"jealous_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.jealousy,
            positive_trait=False,
            dark_mode=game.settings["dark mode"],
        )

        bar_count += 1

        # TRUST
        if the_relationship.trust > 49:
            text = "reliance:"
        else:
            text = "trust:"
        self.relation_list_elements[f"trust_text{i}"] = pygame_gui.elements.UITextBox(
            text,
            scale(
                pygame.Rect(
                    (rel_pos_x, text_pos_y + (barbar * bar_count)),
                    (text_size_x, text_size_y),
                )
            ),
            object_id="#text_box_22_horizleft",
        )
        self.relation_list_elements[f"trust_bar{i}"] = UIRelationStatusBar(
            scale(
                pygame.Rect(
                    (rel_pos_x, bar_pos_y + (barbar * bar_count)),
                    (bar_size_x, bar_size_y),
                )
            ),
            the_relationship.trust,
            positive_trait=True,
            dark_mode=game.settings["dark mode"],
        )

    def on_use(self):

        # LOAD UI IMAGES
        screen.blit(
            RelationshipScreen.search_bar,
            (1070 / 1600 * screen_x, 180 / 1400 * screen_y),
        )
        screen.blit(
            RelationshipScreen.details_frame,
            (50 / 1600 * screen_x, 260 / 1400 * screen_y),
        )
        screen.blit(
            RelationshipScreen.toggle_frame,
            (90 / 1600 * screen_x, 958 / 1400 * screen_y),
        )
        screen.blit(
            RelationshipScreen.list_frame,
            (546 / 1600 * screen_x, 244 / 1400 * screen_y),
        )

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.apply_cat_filter(self.search_bar.get_text())
            self.update_cat_page()
        self.previous_search_text = self.search_bar.get_text()

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]
