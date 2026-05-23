from collections import deque
from math import ceil
from random import choice

import i18n
import pygame.transform
import pygame_gui.elements
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache, game
from ..cat.sprites.load_sprites import sprites
from ..ui.elements.cat_list_display import UICatListDisplay
from ..ui.elements.checkbox import UICheckbox
from ..ui.elements.modified_image import UIModifiedImage
from ..ui.elements.relation_display import UIRelationDisplay
from ..ui.elements.sprite_button import UISpriteButton
from ..ui.elements.image_button import UIImageButton
from ..ui.elements.surface_image_button import UISurfaceImageButton
from ..ui.theme import get_text_box_theme
from ..events_module.text_adjust import shorten_text_to_fit
from ..ui.scale import ui_scale, ui_scale_dimensions
from .Screens import Screens
from ..clan_package.settings import get_clan_setting
from ..game_structure.game.switches import switch_get_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon
from ..ui.windows.no_mediator import NoMediatorsWindow


class MediationScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.all_cats_list = None
        self.back_button = None
        self.selected_cat_1 = None
        self.selected_cat_2 = None
        self.mediators = deque()
        self.cat_buttons = []
        self.page = 1
        self.selected_cat_elements = {}
        self.allow_romance = True
        self.current_listed_cats = None
        self.previous_search_text = ""

        self.elements = {}
        self.mediator_elements = {}

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.elements["last_mediator"]:
                self.mediators.rotate()
                self.update_mediator_info()
            elif event.ui_element == self.elements["next_mediator"]:
                self.mediators.rotate(-1)
                self.update_mediator_info()
            elif event.ui_element == self.elements["next_page"]:
                self.page += 1
                self._set_cat_list()
                self.elements["cat_list"].update_display(
                    current_page=self.page, cat_list=self.all_cats_list
                )
            elif event.ui_element == self.elements["prev_page"]:
                self.page -= 1
                self._set_cat_list()
                self.elements["cat_list"].update_display(
                    current_page=self.page, cat_list=self.all_cats_list
                )
            elif event.ui_element == self.elements["romance_checkbox"]:
                self.allow_romance = not self.allow_romance
                if self.elements["romance_checkbox"].checked:
                    self.elements["romance_checkbox"].uncheck()
                else:
                    self.elements["romance_checkbox"].check()
                self.update_buttons()
            elif event.ui_element == self.elements["remove_cat0"]:
                self.selected_cat_1 = None
                if self.selected_cat_2:
                    self.selected_cat_1 = self.selected_cat_2
                    self.selected_cat_2 = None
                self.update_selected_cats()
            elif event.ui_element == self.elements["remove_cat1"]:
                self.selected_cat_2 = None
                self.update_selected_cats()
            elif event.ui_element == self.elements["improve_rel"]:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.mediators[0].ID)
                output = Cat.mediate_relationship(
                    self.mediators[0],
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                )
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.elements["sabotage_rel"]:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.mediators[0].ID)
                output = Cat.mediate_relationship(
                    self.mediators[0],
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    sabotage=True,
                )
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.elements["random_cat0"]:
                self.selected_cat_1 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_2 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element == self.elements["random_cat1"]:
                self.selected_cat_2 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_1 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in (
                    self.selected_cat_1,
                    self.selected_cat_2,
                ):
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
        self.mediators.clear()
        for cat in Cat.all_cats_list:
            if (
                cat.status.rank.is_any_mediator_rank()
                and cat.status.alive_in_player_clan
            ):
                if cat == switch_get_value(Switch.cat):
                    self.mediators.appendleft(cat)
                else:
                    self.mediators.append(cat)

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # CONTAINERS
        self.elements["effects_container"] = UIContainer(
            ui_scale(pygame.Rect((0, 300), (270, 170))),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.page = 1
        self.elements["cat_list_container"] = UIContainer(
            ui_scale(pygame.Rect((0, 480), (673, 200))),
            anchors={"centerx": "centerx"},
            manager=MANAGER,
        )

        # BOXES
        self.elements["result_frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 10), (270, 125))),
            get_box(BoxStyles.FRAME, (270, 125)),
            container=self.elements["effects_container"],
            manager=MANAGER,
        )

        self.elements["search_bar_back"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((410, 0), (228, 39))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/relationship_search.png"
                ).convert_alpha(),
                ui_scale_dimensions((228, 39)),
            ),
            container=self.elements["cat_list_container"],
            manager=MANAGER,
        )
        self.elements["search_bar"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((485, 8), (145, 23))),
            object_id="#search_entry_box",
            placeholder_text="general.name_search",
            container=self.elements["cat_list_container"],
            manager=MANAGER,
        )

        self.elements["cat_list_bg"] = UIModifiedImage(
            ui_scale(pygame.Rect((24, -5), (625, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (600, 150)),
            anchors={
                "top_target": self.elements["search_bar_back"],
            },
            container=self.elements["cat_list_container"],
            manager=MANAGER,
            starting_height=2,
        )

        self.elements["cat_list_bg"].disable()
        # arrows for cat list
        self.elements["prev_page"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 90), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.elements["cat_list_container"],
            manager=MANAGER,
            starting_height=1,
        )
        self.elements["next_page"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((-10, 90), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            anchors={"left_target": self.elements["cat_list_bg"]},
            container=self.elements["cat_list_container"],
            manager=MANAGER,
            starting_height=1,
        )

        self.elements["romance_checkbox"] = UICheckbox(
            position=(70, 0),
            container=self.elements["effects_container"],
            manager=MANAGER,
            anchors={"top_target": self.elements["result_frame"]},
            visible=False,
        )
        self.elements["romance_text"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 7), (100, 20))),
            "screens.mediation.allow_romantic",
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            container=self.elements["effects_container"],
            anchors={
                "top_target": self.elements["result_frame"],
                "left_target": self.elements["romance_checkbox"],
            },
            manager=MANAGER,
            visible=False,
        )

        # EFFECT
        self.elements["improve_rel"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 0), (105, 30))),
            "screens.mediation.improve",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            container=self.elements["effects_container"],
            manager=MANAGER,
        )
        self.elements["sabotage_rel"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 0), (105, 30))),
            "screens.mediation.sabotage",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            container=self.elements["effects_container"],
            anchors={"left_target": self.elements["improve_rel"]},
            manager=MANAGER,
        )

        self.results = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 385), (229, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            container=self.elements["effects_container"],
            manager=MANAGER,
        )

        # MEDIATOR ARROWS
        self.elements["last_mediator"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((290, 150), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.elements["next_mediator"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((476, 150), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )

        self.elements["select_cat0"] = pygame_gui.elements.UITextBox(
            "screens.mediation.select_cat",
            ui_scale(pygame.Rect((68, 385), (165, -1))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        self.elements["select_cat1"] = pygame_gui.elements.UITextBox(
            "screens.mediation.select_cat",
            ui_scale(pygame.Rect((568, 385), (165, -1))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        # REMOVE AND RANDOM CAT
        self.elements["remove_cat0"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((68, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.elements["remove_cat0"].disable()
        self.elements["remove_cat1"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((605, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.elements["remove_cat1"].disable()
        self.elements["random_cat0"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((198, 432), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.elements["random_cat1"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((568, 432), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.elements["random_cat1"].disable()

        if self.mediators:
            self.update_mediator_info()
        else:
            NoMediatorsWindow()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_mediator_info(self):
        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements.clear()

        if self.mediators:
            mediator = self.mediators[0]

            # mediator can't be one of the selected cats
            if mediator == self.selected_cat_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            if mediator == self.selected_cat_2:
                self.selected_cat_2 = None
                self.update_selected_cats()

            # this is gonna be the "{name} can influence" yada yada above the mediator sprite
            self.mediator_elements["mediator_status"] = pygame_gui.elements.UITextBox(
                "",
                ui_scale(pygame.Rect((0, 37), (229, 57))),
                anchors={"centerx": "centerx"},
                object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
                manager=MANAGER,
            )

            self.mediator_elements["container"] = UIContainer(
                ui_scale(pygame.Rect((0, 0), (150, 200))),
                anchors={
                    "centerx": "centerx",
                    "top_target": self.mediator_elements["mediator_status"],
                },
                manager=MANAGER,
            )
            self.mediator_elements["platform"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (240, 210))),
                pygame.transform.scale(
                    sprites.get_platform(
                        biome=(
                            game.clan.override_biome
                            if game.clan.override_biome
                            else game.clan.biome
                        ),
                        season=game.clan.current_season,
                        show_nest=mediator.not_working(),
                        group=mediator.status.group,
                    ),
                    ui_scale_dimensions((240, 210)),
                ),
                anchors={
                    "centerx": "centerx",
                    "top_target": self.mediator_elements["mediator_status"],
                },
                manager=MANAGER,
                starting_height=-1,
            )
            self.mediator_elements["mediator_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (150, 150))),
                pygame.transform.scale(
                    mediator.sprite, ui_scale_dimensions((150, 150))
                ),
                container=self.mediator_elements["container"],
            )

            text = (
                i18n.t(f"cat.personality.{mediator.personality.trait}")
                + "\n"
                + mediator.experience_level_string
            )

            if mediator.not_working():
                self.elements["improve_rel"].disable()
                self.elements["sabotage_rel"].disable()
            else:
                self.elements["improve_rel"].enable()
                self.elements["sabotage_rel"].enable()

            self.mediator_elements["details"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((0, 0), (150, -1))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                container=self.mediator_elements["container"],
                anchors={"top_target": self.mediator_elements["mediator_image"]},
                manager=MANAGER,
                visible=not mediator.not_working(),
            )

        # deactivate arrows
        if len(self.mediators) <= 1:
            self.elements["last_mediator"].disable()
            self.elements["next_mediator"].disable()

        self.update_buttons()
        self.update_list_cats()

    def update_list_cats(self):
        self._set_cat_list()
        if not self.elements.get("cat_list"):
            self.elements["cat_list"] = UICatListDisplay(
                ui_scale(pygame.Rect(((35, 35), (600, 130)))),
                container=self.elements["cat_list_container"],
                starting_height=3,
                cat_list=self.all_cats_list,
                cats_displayed=20,
                x_px_between=5,
                y_px_between=5,
                columns=10,
                rows=2,
                current_page=1,
                next_button=self.elements["next_page"],
                prev_button=self.elements["prev_page"],
                tool_tip_name=True,
                manager=MANAGER,
            )
        else:
            self.elements["cat_list"].update_display(self.page, self.all_cats_list)

    def _set_cat_list(self):
        self.all_cats_list = [
            i
            for i in Cat.all_cats_list
            if (i.ID != self.mediators[0].ID) and i.status.alive_in_player_clan
        ]

    def update_selected_cats(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.draw_cat_block(self.selected_cat_1, (50, 80))
        self.draw_cat_block(self.selected_cat_2, (550, 80))

        self.update_buttons()

    def draw_cat_block(self, cat: Cat, starting_pos: tuple):
        if not cat:
            return

        selected_cats = self.selected_cat_list()
        cat_num = selected_cats.index(cat)
        other_cat = (
            [c for c in selected_cats if c != cat][0]
            if len(selected_cats) > 1
            else None
        )

        # hide "select cat to influence" text
        self.elements[f"select_cat{cat_num}"].hide()

        # enable random and remove
        self.elements[f"remove_cat{cat_num}"].enable()
        # we just enable random1 because if we're here, then at least 1 cat has been selected
        # and so the player can now choose a second cat
        self.elements[f"random_cat1"].enable()

        self.selected_cat_elements[f"cat_container{cat_num}"] = UIContainer(
            ui_scale(pygame.Rect((starting_pos[0], starting_pos[1]), (200, 350))),
            manager=MANAGER,
        )

        self.selected_cat_elements[f"rel_bg{cat_num}"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 0), (140, 185))),
            get_box(BoxStyles.ROUNDED_BOX, (140, 185)),
            container=self.selected_cat_elements[f"cat_container{cat_num}"],
            anchors={"centerx": "centerx"},
            manager=MANAGER,
            visible=other_cat,
        )

        image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/thought_bubble_tail.png"
            ).convert_alpha(),
            ui_scale_dimensions((32, 52)),
        )
        if cat == self.selected_cat_2:
            image = pygame.transform.flip(image, True, False)

        self.selected_cat_elements[f"bubble_tail{cat_num}"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 10), (32, 52))),
            image,
            container=self.selected_cat_elements[f"cat_container{cat_num}"],
            anchors={
                "centerx": "centerx",
                "top_target": self.selected_cat_elements[f"rel_bg{cat_num}"],
            },
            manager=MANAGER,
            visible=other_cat,
        )

        if cat == self.selected_cat_1:
            self.selected_cat_elements[
                f"cat_image{cat_num}"
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (100, 100))),
                pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"bubble_tail{cat_num}"],
                },
                manager=MANAGER,
            )
            short_name = shorten_text_to_fit(str(cat.name), 45, 7)
            self.selected_cat_elements[
                f"cat_name{cat_num}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 0), (100, 30))),
                short_name,
                object_id="#text_box_30_horizleft",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"bubble_tail{cat_num}"],
                    "left_target": self.selected_cat_elements[f"cat_image{cat_num}"],
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self.get_cat_details(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (100, -1))),
                object_id="#text_box_22_horizleft_spacing_95",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_name{cat_num}"],
                    "left_target": self.selected_cat_elements[f"cat_image{cat_num}"],
                },
                manager=MANAGER,
            )

        else:
            short_name = shorten_text_to_fit(str(cat.name), 45, 7)
            self.selected_cat_elements[
                f"cat_name{cat_num}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 0), (100, 30))),
                short_name,
                object_id="#text_box_30_horizright",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"bubble_tail{cat_num}"]
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self.get_cat_details(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (100, -1))),
                object_id="#text_box_22_horizright_spacing_95",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_name{cat_num}"]
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_image{cat_num}"
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (100, 100))),
                pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"bubble_tail{cat_num}"],
                    "left_target": self.selected_cat_elements[f"cat_details{cat_num}"],
                },
                manager=MANAGER,
            )

    def get_cat_details(self, cat, other_cat):
        output = ""
        output += f"{cat.genderalign}<br>"

        # show relation
        if other_cat:
            if other_cat in cat.mate:
                output += f"{i18n.t('general.are_mates')}<br>"
            elif cat.is_parent(other_cat):
                output += f"{i18n.t('general.parent')}<br>"
            elif other_cat.is_parent(cat):
                output += f"{i18n.t('general.child')}<br>"
            elif cat.is_sibling(other_cat):
                output += f"{i18n.t('general.sibling')}<br>"
            # any relations more complex just get "related" text for my sanity
            elif cat.is_related(other_cat, False):
                output += f"{i18n.t('general.related_text')}<br>"

        # age
        output += f"{i18n.t('general.moons_age', count=cat.moons)}<br>"

        # trait
        output += f"{i18n.t(f'cat.personality.{cat.personality.trait}')}<br>"

        return output

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
            if get_clan_setting("first cousin mates"):
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

        col1 = i18n.t("general.moons_age", count=cat.moons)
        t = i18n.t(f"cat.personality.{cat.personality.trait}")
        if len(t) > 15:
            col1 += "\n" + t[:12] + "..."
        else:
            col1 += "\n" + t
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(
            col1,
            ui_scale(pygame.Rect((x + 21, y + 126), (90, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        self.selected_cat_elements["col1" + tag].disable()

        mates = False
        if len(cat.mate) > 0:
            col2 = i18n.t("general.has_a_mate")
            if other_cat:
                if other_cat.ID in cat.mate:
                    mates = True
                    col2 = i18n.t("general.cats_mate", name=other_cat.name)
        else:
            col2 = i18n.t("general.mate_none")

        self.selected_cat_elements["col2" + tag] = pygame_gui.elements.UITextBox(
            col2,
            ui_scale(pygame.Rect((x + 110, y + 126), (80, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        self.selected_cat_elements["col2" + tag].disable()

        # Relation info:
        if related and other_cat and not mates:
            relation = ""
            if cat.is_uncle_aunt(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.niece"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.nephew"
                else:
                    relation = "general.siblings_child"
            elif other_cat.is_uncle_aunt(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.aunt"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.uncle"
                else:
                    relation = "general.parents_sibling"
            elif other_cat.is_grandparent(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.grandmother"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.grandfather"
                else:
                    relation = "general.grandparent"
            elif cat.is_grandparent(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.granddaughter"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.grandson"
                else:
                    relation = "general.grandchild"
            elif other_cat.is_parent(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.mother"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.father"
                else:
                    relation = "general.parent"
            elif cat.is_parent(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.daughter"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.son"
                else:
                    relation = "general.child"
            elif other_cat.is_sibling(cat) or cat.is_sibling(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.sister"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.brother"
                else:
                    relation = "general.sibling"

                if other_cat.is_littermate(cat) or cat.is_littermate(other_cat):
                    relation = i18n.t(
                        "general.sibling_littermate", relation=i18n.t(relation)
                    )
            elif not get_clan_setting("first cousin mates") and other_cat.is_cousin(
                cat
            ):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.cousin_female"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.cousin_male"
                else:
                    relation = "general.cousin_nb"

            self.selected_cat_elements[
                "col2_relation" + tag
            ] = pygame_gui.elements.UITextBox(
                i18n.t("general.related_text"),
                ui_scale(pygame.Rect((x + 110, -15), (80, -1))),
                starting_height=3,
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
                anchors={"top_target": self.selected_cat_elements["col2" + tag]},
            )
            self.selected_cat_elements["col2_relation" + tag].set_tooltip(
                text=i18n.t(relation)
            )
            self.selected_cat_elements["col2_relation" + tag].tool_tip_delay = 0
            self.selected_cat_elements["col2_relation" + tag].disable()

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        if other_cat:
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 68, 11)

            self.selected_cat_elements[
                f"relation_heading{tag}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x + 20, y + 160), (160, -1))),
                "screens.mediation.cat_feelings",
                object_id="#text_box_22_horizcenter",
                text_kwargs={"name": short_name, "m_c": cat},
            )

            if other_cat.ID in cat.relationships:
                the_relationship = cat.relationships[other_cat.ID]
            else:
                the_relationship = cat.create_one_relationship(other_cat)

            # ROMANTIC LOVE
            # CHECK AGE DIFFERENCE
            same_age = the_relationship.cat_to.age == cat.age
            both_adult = (
                cat.age.can_have_mate() and the_relationship.cat_to.age.can_have_mate()
            )
            check_age = both_adult or same_age

            # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
            # even if they somehow have some. They should not be able to get any, but it never hurts to check.
            if not check_age or related:
                allow_romance = False
                # Print, just for bug checking. Again, they should not be able to get love towards their relative.
                if the_relationship.romance and related:
                    print(
                        f"WARNING: {cat.name} has {the_relationship.romance} romantic love towards their relative, {the_relationship.cat_to.name}"
                    )
            else:
                allow_romance = True

            self.selected_cat_elements[f"display{tag}"] = UIRelationDisplay(
                position=(x + 50, 0),
                relationship=the_relationship,
                romance=allow_romance,
                manager=MANAGER,
                anchors={
                    "top_target": self.selected_cat_elements[f"relation_heading{tag}"]
                },
            )

    def selected_cat_list(self):
        output = []
        if self.selected_cat_1:
            output.append(self.selected_cat_1)
        if self.selected_cat_2:
            output.append(self.selected_cat_2)

        return output

    def update_buttons(self):
        mediator_status = ""

        invalid_mediator = False
        if self.mediators is not None:
            mediator_name = self.mediators[0].name
            if self.mediators[0].not_working():
                invalid_mediator = True
                mediator_status = i18n.t(
                    "screens.mediation.mediator_cant_work", name=mediator_name
                )
            elif self.mediators[0].ID in game.patrolled:
                invalid_mediator = True
                mediator_status = i18n.t(
                    "screens.mediation.mediator_already_worked", name=mediator_name
                )
            else:
                mediator_status = i18n.t(
                    "screens.mediation.mediator_ready_to_work", name=mediator_name
                )
        else:
            invalid_mediator = True

        invalid_pair = False
        if self.selected_cat_1 and self.selected_cat_2:
            for x in game.mediated:
                if self.selected_cat_1.ID in x and self.selected_cat_2.ID in x:
                    invalid_pair = True
                    mediator_status = i18n.t("screens.mediation.pair_already_mediated")
                    break
        else:
            invalid_pair = True

        self.mediator_elements["mediator_status"].set_text(mediator_status)

        if invalid_mediator or invalid_pair:
            self.elements["improve_rel"].disable()
            self.elements["sabotage_rel"].disable()
        else:
            self.elements["improve_rel"].enable()
            self.elements["sabotage_rel"].enable()

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        current_listed_cats = []
        Cat.sort_cats(self.all_cats_list)

        search_text = search_text.strip()
        if search_text not in (""):
            for cat in self.all_cats_list:
                if search_text.lower() in str(cat.name).lower():
                    current_listed_cats.append(cat)
        else:
            current_listed_cats = self.all_cats_list.copy()

        Cat.ordered_cat_list = current_listed_cats

        self.elements["cat_list"].update_display(self.page, current_listed_cats)

    def exit_screen(self):
        self.selected_cat_1 = None
        self.selected_cat_2 = None

        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        for ele in self.elements.values():
            ele.kilL()
        self.elements.clear()

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons.clear()

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.mediators.clear()
        self.back_button.kill()
        del self.back_button
        self.results.kill()
        del self.results

    def on_use(self):
        super().on_use()
        # Only update the positions if the search text changes
        if (
            self.elements["search_bar"].is_focused
            and self.elements["search_bar"].get_text() == "name search"
        ):
            self.elements["search_bar"].set_text("")
        if self.elements["search_bar"].get_text() != self.previous_search_text:
            self.update_search_cats(self.elements["search_bar"].get_text())
        self.previous_search_text = self.elements["search_bar"].get_text()
