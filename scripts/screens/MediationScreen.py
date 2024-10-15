from math import ceil
from random import choice

import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UIRelationStatusBar,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon


class MediationScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.selected_mediator = None
        self.selected_cat_1 = None
        self.selected_cat_2 = None
        self.search_bar = None
        self.search_bar_image = None
        self.mediator_elements = {}
        self.mediators = []
        self.cat_buttons = []
        self.page = 1
        self.selected_cat_elements = {}
        self.allow_romantic = True
        self.current_listed_cats = None
        self.previous_search_text = ""

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.last_med:
                self.selected_mediator -= 1
                self.update_mediator_info()
            elif event.ui_element == self.next_med:
                self.selected_mediator += 1
                self.update_mediator_info()
            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.romantic_checkbox:
                if self.allow_romantic:
                    self.allow_romantic = False
                else:
                    self.allow_romantic = True
                self.update_buttons()
            elif event.ui_element == self.deselect_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            elif event.ui_element == self.deselect_2:
                self.selected_cat_2 = None
                self.update_selected_cats()
            elif event.ui_element == self.mediate_button:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.mediators[self.selected_mediator].ID)
                output = Cat.mediate_relationship(
                    self.mediators[self.selected_mediator],
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romantic,
                )
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.sabotage_button:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.mediators[self.selected_mediator].ID)
                output = Cat.mediate_relationship(
                    self.mediators[self.selected_mediator],
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romantic,
                    sabotage=True,
                )
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.random1:
                self.selected_cat_1 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_2 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element == self.random2:
                self.selected_cat_2 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_1 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in [
                    self.selected_cat_1,
                    self.selected_cat_2,
                ]:
                    if (
                        pygame.key.get_mods() & pygame.KMOD_SHIFT
                        or not self.selected_cat_1
                    ):
                        self.selected_cat_1 = event.ui_element.return_cat_object()
                    else:
                        self.selected_cat_2 = event.ui_element.return_cat_object()
                    self.update_selected_cats()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        # Gather the mediators:
        self.mediators = []
        for cat in Cat.all_cats_list:
            if cat.status in ["mediator", "mediator apprentice"] and not (
                cat.dead or cat.outside
            ):
                self.mediators.append(cat)

        self.page = 1

        if self.mediators:
            if Cat.fetch_cat(game.switches["cat"]) in self.mediators:
                self.selected_mediator = self.mediators.index(
                    Cat.fetch_cat(game.switches["cat"])
                )
            else:
                self.selected_mediator = 0
        else:
            self.selected_mediator = None

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.selected_frame_1 = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 80), (200, 350))),
            get_box(BoxStyles.ROUNDED_BOX, (200, 350)),
        )
        self.selected_frame_1.disable()
        self.selected_frame_2 = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((550, 80), (200, 350))),
            get_box(BoxStyles.ROUNDED_BOX, (200, 350)),
        )
        self.selected_frame_2.disable()

        self.cat_bg = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 470), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )
        self.cat_bg.disable()

        # Will be overwritten
        self.romantic_checkbox = None
        self.romantic_checkbox_text = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((368, 325), (100, 20))),
            "Allow romantic",
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
        )

        self.mediate_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((280, 350), (105, 30))),
            "Mediate",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.sabotage_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((400, 350), (109, 30))),
            "Sabotage",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.next_med = UISurfaceImageButton(
            ui_scale(pygame.Rect((476, 270), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.last_med = UISurfaceImageButton(
            ui_scale(pygame.Rect((280, 270), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )

        self.next_page = UIImageButton(
            ui_scale(pygame.Rect((433, 612), (34, 34))),
            "",
            object_id="#relation_list_next",
        )
        self.previous_page = UIImageButton(
            ui_scale(pygame.Rect((333, 612), (34, 34))),
            "",
            object_id="#relation_list_previous",
        )

        self.deselect_1 = UISurfaceImageButton(
            ui_scale(pygame.Rect((68, 434), (127, 30))),
            "Remove Cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.deselect_2 = UISurfaceImageButton(
            ui_scale(pygame.Rect((605, 434), (127, 30))),
            "Remove Cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.results = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 385), (229, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.error = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 37), (229, 57))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.random1 = UISurfaceImageButton(
            ui_scale(pygame.Rect((198, 432), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.random2 = UISurfaceImageButton(
            ui_scale(pygame.Rect((568, 432), (34, 34))),
            "\u2684",
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )

        self.search_bar_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((55, 625), (118, 34))),
            pygame.image.load("resources/images/search_bar.png").convert_alpha(),
            manager=MANAGER,
        )
        self.search_bar = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((60, 629), (115, 27))),
            object_id="#search_entry_box",
            initial_text="name search",
            manager=MANAGER,
        )

        self.update_buttons()
        self.update_mediator_info()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i.ID not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_mediator_info(self):
        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        if (
            self.selected_mediator is not None
        ):  # It can be zero, so we must test for not None here.
            x_value = 315
            mediator = self.mediators[self.selected_mediator]

            # Clear mediator as selected cat
            if mediator == self.selected_cat_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            if mediator == self.selected_cat_2:
                self.selected_cat_2 = None
                self.update_selected_cats()

            self.mediator_elements["mediator_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_value, 90), (150, 150))),
                pygame.transform.scale(
                    mediator.sprite, ui_scale_dimensions((150, 150))
                ),
            )

            name = str(mediator.name)
            short_name = shorten_text_to_fit(name, 120, 11)
            self.mediator_elements["name"] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x_value - 5, 240), (160, -1))),
                short_name,
                object_id=get_text_box_theme(),
            )

            text = mediator.personality.trait + "\n" + mediator.experience_level

            if mediator.not_working():
                text += "\nThis cat isn't able to work"
                self.mediate_button.disable()
                self.sabotage_button.disable()
            else:
                text += "\nThis cat can work"
                self.mediate_button.enable()
                self.sabotage_button.enable()

            self.mediator_elements["details"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((x_value, 260), (155, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                manager=MANAGER,
            )

            mediator_number = len(self.mediators)
            if self.selected_mediator < mediator_number - 1:
                self.next_med.enable()
            else:
                self.next_med.disable()

            if self.selected_mediator > 0:
                self.last_med.enable()
            else:
                self.last_med.disable()

        else:
            self.last_med.disable()
            self.next_med.disable()

        self.update_buttons()
        self.update_list_cats()

    def update_list_cats(self):
        self.all_cats_list = [
            i
            for i in Cat.all_cats_list
            if (i.ID != self.mediators[self.selected_mediator].ID)
            and not (i.dead or i.outside)
        ]
        self.all_cats = self.chunks(self.all_cats_list, 24)
        self.current_listed_cats = self.all_cats_list
        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )
        self.update_page()

    def update_page(self):
        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []
        if self.page > self.all_pages:
            self.page = self.all_pages
        elif self.page < 1:
            self.page = 1

        if self.page >= self.all_pages:
            self.next_page.disable()
        else:
            self.next_page.enable()

        if self.page <= 1:
            self.previous_page.disable()
        else:
            self.previous_page.enable()

        x = 65
        y = 485
        chunked_cats = self.chunks(self.current_listed_cats, 24)
        if chunked_cats:
            for cat in chunked_cats[self.page - 1]:
                if game.clan.clan_settings["show fav"] and cat.favourite:
                    _temp = pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((50, 50)),
                    )

                    self.cat_buttons.append(
                        pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((x, y), (50, 50))), _temp
                        )
                    )
                    self.cat_buttons[-1].disable()

                self.cat_buttons.append(
                    UISpriteButton(
                        ui_scale(pygame.Rect((x, y), (50, 50))),
                        cat.sprite,
                        cat_object=cat,
                    )
                )
                x += 55
                if x > 700:
                    y += 55
                    x = 65

    def update_selected_cats(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.draw_info_block(self.selected_cat_1, (50, 80))
        self.draw_info_block(self.selected_cat_2, (550, 80))

        self.update_buttons()

    def draw_info_block(self, cat, starting_pos: tuple):
        if not cat:
            return

        other_cat = [Cat.fetch_cat(i) for i in self.selected_cat_list() if i != cat.ID]
        if other_cat:
            other_cat = other_cat[0]
        else:
            other_cat = None

        tag = str(starting_pos)

        x = starting_pos[0]
        y = starting_pos[1]

        self.selected_cat_elements["cat_image" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 50, y + 7), (100, 100))),
            pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
        )

        name = str(cat.name)
        short_name = shorten_text_to_fit(name, 62, 7)
        self.selected_cat_elements["name" + tag] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((x, y + 100), (200, 30))),
            short_name,
            object_id="#text_box_30_horizcenter",
        )

        # Gender
        if cat.genderalign == "female":
            gender_icon = image_cache.load_image(
                "resources/images/female_big.png"
            ).convert_alpha()
        elif cat.genderalign == "male":
            gender_icon = image_cache.load_image(
                "resources/images/male_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans female":
            gender_icon = image_cache.load_image(
                "resources/images/transfem_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans male":
            gender_icon = image_cache.load_image(
                "resources/images/transmasc_big.png"
            ).convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image(
                "resources/images/nonbi_big.png"
            ).convert_alpha()

        self.selected_cat_elements["gender" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 160, y + 12), (25, 25))),
            pygame.transform.scale(gender_icon, ui_scale_dimensions((25, 25))),
        )

        related = False
        # MATE
        if other_cat and len(cat.mate) > 0 and other_cat.ID in cat.mate:
            self.selected_cat_elements["mate_icon" + tag] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x + 14, y + 14), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((44, 40)),
                ),
            )
        elif other_cat:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if game.clan.clan_settings["first cousin mates"]:
                check_cousins = False
            else:
                check_cousins = other_cat.is_cousin(cat)

            if (
                other_cat.is_uncle_aunt(cat)
                or cat.is_uncle_aunt(other_cat)
                or other_cat.is_grandparent(cat)
                or cat.is_grandparent(other_cat)
                or other_cat.is_parent(cat)
                or cat.is_parent(other_cat)
                or other_cat.is_sibling(cat)
                or check_cousins
            ):
                related = True
                self.selected_cat_elements[
                    "relation_icon" + tag
                ] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((x + 14, y + 14), (18, 18))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/dot_big.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((18, 18)),
                    ),
                )

        col1 = str(cat.moons)
        if cat.moons == 1:
            col1 += " moon"
        else:
            col1 += " moons"
        if len(cat.personality.trait) > 15:
            _t = cat.personality.trait[:13] + ".."
        else:
            _t = cat.personality.trait
        col1 += "\n" + _t
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(
            col1,
            ui_scale(pygame.Rect((x + 21, y + 126), (90, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )

        mates = False
        if len(cat.mate) > 0:
            col2 = "has a mate"
            if other_cat:
                if other_cat.ID in cat.mate:
                    mates = True
                    col2 = f"{other_cat.name}'s mate"
        else:
            col2 = "mate: none"

        # Relation info:
        if related and other_cat and not mates:
            col2 += "\n"
            if other_cat.is_uncle_aunt(cat):
                if cat.genderalign in ["female", "trans female"]:
                    col2 += "niece"
                elif cat.genderalign in ["male", "trans male"]:
                    col2 += "nephew"
                else:
                    col2 += "sibling's child"
            elif cat.is_uncle_aunt(other_cat):
                if cat.genderalign in ["female", "trans female"]:
                    col2 += "aunt"
                elif cat.genderalign in ["male", "trans male"]:
                    col2 += "uncle"
                else:
                    col2 += "related: parent's sibling"
            elif cat.is_grandparent(other_cat):
                col2 += "grandparent"
            elif other_cat.is_grandparent(cat):
                col2 += "grandchild"
            elif cat.is_parent(other_cat):
                col2 += "parent"
            elif other_cat.is_parent(cat):
                col2 += "child"
            elif cat.is_sibling(other_cat) or other_cat.is_sibling(cat):
                col2 += "sibling"
            elif not game.clan.clan_settings[
                "first cousin mates"
            ] and other_cat.is_cousin(cat):
                col2 += "cousin"

        self.selected_cat_elements["col2" + tag] = pygame_gui.elements.UITextBox(
            col2,
            ui_scale(pygame.Rect((x + 110, y + 126), (80, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        if other_cat:
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 68, 11)

            self.selected_cat_elements[
                f"relation_heading{tag}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x + 20, y + 160), (160, -1))),
                f"~~{short_name}'s feelings~~",
                object_id="#text_box_22_horizcenter",
            )

            if other_cat.ID in cat.relationships:
                the_relationship = cat.relationships[other_cat.ID]
            else:
                the_relationship = cat.create_one_relationship(other_cat)

            barbar = 21
            bar_count = 0
            y_start = 177
            x_start = 25

            # ROMANTIC LOVE
            # CHECK AGE DIFFERENCE
            same_age = the_relationship.cat_to.age == cat.age
            adult_ages = ["young adult", "adult", "senior adult", "senior"]
            both_adult = (
                the_relationship.cat_to.age in adult_ages and cat.age in adult_ages
            )
            check_age = both_adult or same_age

            # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
            # even if they somehow have some. They should not be able to get any, but it never hurts to check.
            if not check_age or related:
                display_romantic = 0
                # Print, just for bug checking. Again, they should not be able to get love towards their relative.
                if the_relationship.romantic_love and related:
                    print(
                        str(cat.name)
                        + " has "
                        + str(the_relationship.romantic_love)
                        + " romantic love "
                        "towards their relative, " + str(the_relationship.cat_to.name)
                    )
            else:
                display_romantic = the_relationship.romantic_love

            if display_romantic > 49:
                text = "romantic love:"
            else:
                text = "romantic like:"

            self.selected_cat_elements[
                f"romantic_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"romantic_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
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
            self.selected_cat_elements[
                f"plantonic_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"platonic_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
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
            self.selected_cat_elements[
                f"dislike_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"dislike_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
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
            self.selected_cat_elements[
                f"admiration_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"admiration_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
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
                text = "comfortable:"
            self.selected_cat_elements[
                f"comfortable_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"comfortable_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
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
            self.selected_cat_elements[
                f"jealous_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"jealous_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
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
            self.selected_cat_elements[
                f"trust_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"trust_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.trust,
                positive_trait=True,
                dark_mode=game.settings["dark mode"],
            )

    def selected_cat_list(self):
        output = []
        if self.selected_cat_1:
            output.append(self.selected_cat_1.ID)
        if self.selected_cat_2:
            output.append(self.selected_cat_2.ID)

        return output

    def update_buttons(self):
        error_message = ""

        invalid_mediator = False
        if self.selected_mediator is not None:
            if self.mediators[self.selected_mediator].not_working():
                invalid_mediator = True
                error_message += "This mediator can't work this moon. "
            elif self.mediators[self.selected_mediator].ID in game.patrolled:
                invalid_mediator = True
                error_message += "This mediator has already worked this moon. "
        else:
            invalid_mediator = True

        invalid_pair = False
        if self.selected_cat_1 and self.selected_cat_2:
            for x in game.mediated:
                if self.selected_cat_1.ID in x and self.selected_cat_2.ID in x:
                    invalid_pair = True
                    error_message += "This pair has already been mediated this moon. "
                    break
        else:
            invalid_pair = True

        self.error.set_text(error_message)

        if invalid_mediator or invalid_pair:
            self.mediate_button.disable()
            self.sabotage_button.disable()
        else:
            self.mediate_button.enable()
            self.sabotage_button.enable()

        if self.romantic_checkbox:
            self.romantic_checkbox.kill()

        if self.allow_romantic:
            self.romantic_checkbox = UIImageButton(
                ui_scale(pygame.Rect((321, 317), (34, 34))),
                "",
                object_id="@checked_checkbox",
                tool_tip_text="Allow effects on romantic like, if possible. ",
                manager=MANAGER,
            )
        else:
            self.romantic_checkbox = UIImageButton(
                ui_scale(pygame.Rect((321, 317), (34, 34))),
                "",
                object_id="@unchecked_checkbox",
                tool_tip_text="Allow effects on romantic like, if possible. ",
                manager=MANAGER,
            )

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        Cat.sort_cats(self.all_cats_list)

        search_text = search_text.strip()
        if search_text not in ["", "name search"]:
            for cat in self.all_cats_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.all_cats_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_page()

    def exit_screen(self):
        self.selected_cat_1 = None
        self.selected_cat_2 = None

        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.mediators = []
        self.back_button.kill()
        del self.back_button
        self.selected_frame_1.kill()
        del self.selected_frame_1
        self.selected_frame_2.kill()
        del self.selected_frame_2
        self.cat_bg.kill()
        del self.cat_bg
        self.mediate_button.kill()
        del self.mediate_button
        self.sabotage_button.kill()
        del self.sabotage_button
        self.last_med.kill()
        del self.last_med
        self.next_med.kill()
        del self.next_med
        self.deselect_1.kill()
        del self.deselect_1
        self.deselect_2.kill()
        del self.deselect_2
        self.next_page.kill()
        del self.next_page
        self.previous_page.kill()
        del self.previous_page
        self.results.kill()
        del self.results
        self.random1.kill()
        del self.random1
        self.random2.kill()
        del self.random2
        if self.romantic_checkbox:
            self.romantic_checkbox.kill()
            del self.romantic_checkbox
        self.romantic_checkbox_text.kill()
        del self.romantic_checkbox_text
        self.error.kill()
        del self.error
        self.search_bar_image.kill()
        del self.search_bar_image
        self.search_bar.kill()
        del self.search_bar

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    def on_use(self):
        super().on_use()
        # Only update the positions if the search text changes
        if self.search_bar.is_focused and self.search_bar.get_text() == "name search":
            self.search_bar.set_text("")
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()
