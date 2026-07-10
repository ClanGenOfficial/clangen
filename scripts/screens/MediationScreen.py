from collections import deque
from random import choice
from typing import List, Optional

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
        self.selected_cat0 = None
        self.selected_cat1 = None
        self.mediators = deque()
        self.page = 1
        self.selected_cat_elements = {}
        self.allow_romance = False
        self.previous_search_text = ""

        self.elements = {}
        self.mediator_elements = {}
        self.tab_view = "all"

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            # MEDIATOR ARROWS
            elif event.ui_element == self.elements["last_mediator"]:
                self.mediators.rotate()
                self.update_mediator_info()
            elif event.ui_element == self.elements["next_mediator"]:
                self.mediators.rotate(-1)
                self.update_mediator_info()
            # CAT LIST ARROWS
            elif event.ui_element == self.elements["next_page"]:
                self.page += 1
                self.update_list_cats()
            elif event.ui_element == self.elements["prev_page"]:
                self.page -= 1
                self.update_list_cats()
            # ROMANCE CHECKBOX
            elif event.ui_element == self.elements["romance_checkbox"]:
                self.allow_romance = not self.allow_romance
                if self.elements["romance_checkbox"].checked:
                    self.elements["romance_checkbox"].uncheck()
                else:
                    self.elements["romance_checkbox"].check()
            # REMOVE CAT
            elif event.ui_element == self.elements["remove_cat0"]:
                self.selected_cat0 = None
                # now we move the other cat to be cat0
                if self.selected_cat1:
                    self.selected_cat0 = self.selected_cat1
                    self.selected_cat1 = None
                # if no cats are selected, we reset the tab to All
                if not self.selected_cat0 and self.tab_view != "all":
                    self.tab_view = "all"
                    self.elements["all_tab"].disable()
                    self.elements["neg_tab"].enable()
                    self.elements["pos_tab"].enable()
                    self.update_list_cats()
                self.update_selected_cats()
            elif event.ui_element == self.elements["remove_cat1"]:
                self.selected_cat1 = None
                self.update_selected_cats()
            # IMPROVE BUTTON
            elif event.ui_element == self.elements["improve_rel"]:
                game.mediated.append([self.selected_cat0.ID, self.selected_cat1.ID])
                game.patrolled.append(self.mediators[0].ID)
                output = Cat.mediate_relationship(
                    self.mediators[0],
                    self.selected_cat0,
                    self.selected_cat1,
                    self.allow_romance,
                )
                self.elements["results"].set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            # SABOTAGE BUTTON
            elif event.ui_element == self.elements["sabotage_rel"]:
                game.mediated.append([self.selected_cat0.ID, self.selected_cat1.ID])
                game.patrolled.append(self.mediators[0].ID)
                output = Cat.mediate_relationship(
                    self.mediators[0],
                    self.selected_cat0,
                    self.selected_cat1,
                    self.allow_romance,
                    sabotage=True,
                )
                self.elements["results"].set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            # PICK RANDOM CATS
            elif event.ui_element == self.elements["random_cat0"]:
                self.selected_cat0 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat1 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element == self.elements["random_cat1"]:
                self.selected_cat1 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat0 = self.random_cat()
                self.update_selected_cats()
            # SWITCH TO ALL TAB
            elif event.ui_element == self.elements["all_tab"]:
                self.tab_view = "all"
                self.elements["all_tab"].disable()
                self.elements["neg_tab"].enable()
                self.elements["pos_tab"].enable()
                self.update_list_cats()
            # SWITCH TO NEG TAB
            elif event.ui_element == self.elements["neg_tab"]:
                self.tab_view = "negative"
                self.elements["all_tab"].enable()
                self.elements["neg_tab"].disable()
                self.elements["pos_tab"].enable()
                self.update_list_cats()
            # SWITCH TO POS TAB
            elif event.ui_element == self.elements["pos_tab"]:
                self.tab_view = "positive"
                self.elements["all_tab"].enable()
                self.elements["neg_tab"].enable()
                self.elements["pos_tab"].disable()
                self.update_list_cats()
            # SELECT A CAT
            elif (
                self.elements.get("cat_list")
                and event.ui_element in self.elements["cat_list"].cat_sprites.values()
            ):
                if event.ui_element.return_cat_object() not in (
                    self.selected_cat0,
                    self.selected_cat1,
                ):
                    if (
                        pygame.key.get_mods() & pygame.KMOD_SHIFT
                        or not self.selected_cat0
                    ):
                        self.selected_cat0 = event.ui_element.return_cat_object()
                    else:
                        self.selected_cat1 = event.ui_element.return_cat_object()
                    self.update_selected_cats()

        super().handle_event(event)

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

        interactable_elements = []

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.current_focus = self.back_button
        interactable_elements.append(self.back_button)

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

        # SEARCH BAR
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
        interactable_elements.append(self.elements["search_bar"])

        # CAT LIST
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
        # LIST ARROWS
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
        interactable_elements.extend(
            [self.elements["prev_page"], self.elements["next_page"]]
        )

        # LIST TABS
        self.elements["all_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((50, 5), (50, 35))),
            "screens.mediation.all",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (50, 35)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={"bottom_target": self.elements["cat_list_bg"]},
            container=self.elements["cat_list_container"],
        )
        self.elements["all_tab"].disable()
        self.elements["pos_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((10, 5), (80, 35))),
            "screens.mediation.positive",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (80, 35)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={
                "bottom_target": self.elements["cat_list_bg"],
                "left_target": self.elements["all_tab"],
            },
            container=self.elements["cat_list_container"],
            visible=False,
        )
        self.elements["neg_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((10, 5), (90, 35))),
            "screens.mediation.negative",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (90, 35)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={
                "bottom_target": self.elements["cat_list_bg"],
                "left_target": self.elements["pos_tab"],
            },
            container=self.elements["cat_list_container"],
            visible=False,
        )
        interactable_elements.extend(
            [
                self.elements["all_tab"],
                self.elements["pos_tab"],
                self.elements["neg_tab"],
            ]
        )

        # RESULTS
        self.elements["result_frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 8), (270, 125))),
            get_box(BoxStyles.FRAME, (270, 125)),
            container=self.elements["effects_container"],
            manager=MANAGER,
        )
        # ROMANCE CHECKBOX
        self.elements["romance_checkbox"] = UICheckbox(
            position=(70, 0),
            container=self.elements["effects_container"],
            manager=MANAGER,
            anchors={"top_target": self.elements["result_frame"]},
            visible=False,
            check=self.allow_romance,
        )
        interactable_elements.append(self.elements["romance_checkbox"])
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

        # EFFECT BUTTONS
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
        interactable_elements.extend(
            [self.elements["improve_rel"], self.elements["sabotage_rel"]]
        )

        # RESULT TEXT
        self.elements["results"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((20, 40), (229, 80))),
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
        interactable_elements.extend(
            [self.elements["last_mediator"], self.elements["next_mediator"]]
        )

        # INDICATOR TEXT
        self.elements["select_cat0"] = pygame_gui.elements.UITextBox(
            "screens.mediation.select_cat0",
            ui_scale(pygame.Rect((68, 385), (165, -1))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        self.elements["select_cat1"] = pygame_gui.elements.UITextBox(
            "screens.mediation.select_cat1",
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

        interactable_elements.extend(
            [
                self.elements["remove_cat0"],
                self.elements["remove_cat1"],
                self.elements["random_cat0"],
                self.elements["random_cat1"],
            ]
        )

        self.add_to_map(interactable_elements)

        # UPDATE
        if self.mediators:
            self.update_mediator_info()
        else:
            NoMediatorsWindow()

    def random_cat(self) -> Optional[Cat]:
        """
        Return a random cat to influence
        """
        if self.selected_cat_list:
            random_list = [
                i for i in self.all_cats_list if i not in self.selected_cat_list
            ]
        else:
            random_list = self.all_cats_list

        if not random_list:
            return None

        return choice(random_list)

    def update_mediator_info(self):
        """
        Update mediator elements and corresponding information
        """
        # kill and reset
        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements.clear()

        # grab the mediator to use
        mediator = self.mediators[0]

        # mediator can't be one of the selected cats
        if mediator == self.selected_cat0:
            self.selected_cat0 = None
            if self.selected_cat1:  # move other cat over
                self.selected_cat0 = self.selected_cat1
                self.selected_cat1 = None
            self.update_selected_cats()
        if mediator == self.selected_cat1:
            self.selected_cat1 = None
            self.update_selected_cats()

        # this is gonna be the "{name} can influence" yada yada above the mediator sprite
        self.mediator_elements["mediator_status"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 37), (229, 57))),
            anchors={"centerx": "centerx"},
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        # container for all the other elements
        self.mediator_elements["container"] = UIContainer(
            ui_scale(pygame.Rect((0, 0), (150, 200))),
            anchors={
                "centerx": "centerx",
                "top_target": self.mediator_elements["mediator_status"],
            },
            manager=MANAGER,
        )
        # cat sprite stuff
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
            pygame.transform.scale(mediator.sprite, ui_scale_dimensions((150, 150))),
            container=self.mediator_elements["container"],
        )

        # cat description
        text = (
            i18n.t(f"cat.personality.{mediator.personality.trait}")
            + "\n"
            + mediator.experience_level_string
        )
        self.mediator_elements["details"] = pygame_gui.elements.UITextBox(
            text,
            ui_scale(pygame.Rect((0, 0), (150, -1))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            container=self.mediator_elements["container"],
            anchors={"top_target": self.mediator_elements["mediator_image"]},
            manager=MANAGER,
            visible=not mediator.not_working(),  # doesn't appear if the cat isn't working
        )
        # disable buttons if mediator can't work
        if mediator.not_working():
            self.elements["improve_rel"].disable()
            self.elements["sabotage_rel"].disable()
        else:
            self.elements["improve_rel"].enable()
            self.elements["sabotage_rel"].enable()

        # deactivate arrows if no other mediators
        if len(self.mediators) <= 1:
            self.elements["last_mediator"].disable()
            self.elements["next_mediator"].disable()

        self.update_mediator_status_and_buttons()
        self.update_list_cats()

    def update_list_cats(self):
        """
        Updates the cat list display according to current selections
        """
        # make sure the list is up to date
        self._set_cat_list()
        if not self.elements.get("cat_list"):  # create the element in the first place
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
            self.add_to_map(self.elements["cat_list"].cat_sprites.values())

        self.update_search_cats(self.elements["search_bar"].get_text())

    def _set_cat_list(self):
        """
        Updates self.all_cats_list according to chosen tab
        """
        if self.tab_view == "positive":
            self.all_cats_list = [
                c
                for c in Cat.all_cats_list
                if (c.ID != self.mediators[0].ID)
                and c.status.alive_in_player_clan
                and c.ID in self.selected_cat0.relationships
                and self.selected_cat0.relationships[c.ID].total_relationship_value > 0
            ]
        elif self.tab_view == "negative":
            self.all_cats_list = [
                c
                for c in Cat.all_cats_list
                if (c.ID != self.mediators[0].ID)
                and c.status.alive_in_player_clan
                and c.ID in self.selected_cat0.relationships
                and self.selected_cat0.relationships[c.ID].total_relationship_value < 0
            ]
        else:
            self.all_cats_list = [
                i
                for i in Cat.all_cats_list
                if (i.ID != self.mediators[0].ID) and i.status.alive_in_player_clan
            ]

    def update_selected_cats(self):
        """
        Updates all elements connected to the selected cats.
        """
        # kill and reset all the elements
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        # show both "select a cat" text. these will be hidden later if need be.
        self.elements["select_cat0"].show()
        self.elements["select_cat1"].show()

        # check if the neg/pos tabs should be hidden or shown
        if self.selected_cat0:
            self.elements["neg_tab"].show()
            self.elements["pos_tab"].show()
        else:
            self.elements["neg_tab"].hide()
            self.elements["pos_tab"].hide()
            self.elements["remove_cat0"].disable()
            self.elements["random_cat1"].disable()

        if not self.selected_cat1:
            self.elements["remove_cat1"].disable()

        # draw each cat block
        self._draw_cat_block(self.selected_cat0, (50, 80))
        self._draw_cat_block(self.selected_cat1, (550, 80))

        # update the mediator info
        self.update_mediator_status_and_buttons()

    def _draw_cat_block(self, cat: Cat, starting_pos: tuple):
        """
        Creates all the elements within a selected cat block
        """
        if not cat:
            return

        # first we grab an index for the cat, so that we can create unique elements using it
        selected_cats = self.selected_cat_list
        cat_num = selected_cats.index(cat)
        # we also find the other cat, so that we can get any important info we need from them
        other_cat = (
            [c for c in selected_cats if c != cat][0]
            if len(selected_cats) > 1
            else None
        )

        # hide "select cat to influence" text, cus at this point we know a cat has been selected
        self.elements[f"select_cat{cat_num}"].hide()

        # enable random and remove
        self.elements[f"remove_cat{cat_num}"].enable()
        # we just enable random1 because if we're here, then at least 1 cat has been selected
        # and so the player can now choose a second cat
        self.elements[f"random_cat1"].enable()

        # we love a container
        self.selected_cat_elements[f"cat_container{cat_num}"] = UIContainer(
            ui_scale(pygame.Rect((starting_pos[0], starting_pos[1]), (200, 350))),
            manager=MANAGER,
        )

        # this is the background bubble for the relationship display
        self.selected_cat_elements[f"rel_bg{cat_num}"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 0), (140, 185))),
            get_box(BoxStyles.ROUNDED_BOX, (140, 185)),
            container=self.selected_cat_elements[f"cat_container{cat_num}"],
            anchors={"centerx": "centerx"},
            manager=MANAGER,
            visible=other_cat,
        )

        # and this is the tail of that bubble
        image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/thought_bubble_tail.png"
            ).convert_alpha(),
            ui_scale_dimensions((32, 52)),
        )
        if cat == self.selected_cat1:  # tail has to flip if this is the right-side cat
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

        # if we have another cat, then we create the relationship display
        if other_cat:
            the_relationship = cat.relationships[other_cat.ID]

            same_age = the_relationship.cat_to.age == cat.age
            adult_ages = ["young adult", "adult", "senior adult", "senior"]
            both_adult = (
                the_relationship.cat_to.age in adult_ages and cat.age in adult_ages
            )
            check_age = both_adult or same_age

            # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
            # even if they somehow have some. They should not be able to get any, but it never hurts to check.
            if not check_age or cat.is_related(
                other_cat, get_clan_setting("first cousin mates")
            ):
                allow_romance = False
                self.elements["romance_checkbox"].hide()
                self.elements["romance_text"].hide()
            else:
                allow_romance = True
                self.elements["romance_checkbox"].show()
                self.elements["romance_text"].show()

            self.selected_cat_elements[
                f"relation_display{cat_num}"
            ] = UIRelationDisplay(
                (2, 10),
                the_relationship,
                romance=allow_romance,
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={"centerx": "centerx"},
            )

        # cat stuff needs to be drawn differently for each cat due to changes in alignment and anchoring
        if cat == self.selected_cat0:
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
                object_id=get_text_box_theme("#text_box_30_horizleft"),
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
                self._get_cat_details(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (100, -1))),
                object_id=get_text_box_theme("#text_box_22_horizleft_spacing_95"),
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
                object_id=get_text_box_theme("#text_box_30_horizright"),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"bubble_tail{cat_num}"]
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self._get_cat_details(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (100, -1))),
                object_id=get_text_box_theme("#text_box_22_horizright_spacing_95"),
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

    @staticmethod
    def _get_cat_details(cat, other_cat) -> str:
        """
        Returns a string with the cat's details: gender, relation to other cat, age, and trait
        """
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

    @property
    def selected_cat_list(self) -> List[Cat]:
        """Easy way to get a list of both selected cats"""
        output = []
        if self.selected_cat0:
            output.append(self.selected_cat0)
        if self.selected_cat1:
            output.append(self.selected_cat1)

        return output

    def update_mediator_status_and_buttons(self):
        """
        Updates the mediator status text and the states of improve/sabotage buttons
        """
        if not self.mediator_elements:
            # early return, sometimes this func is called when no mediator elements are made
            # in which case, we should just skip all of it
            return

        # finding mediator status string
        invalid_mediator = False  # will be True if a mediator can't work
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

        # check if influence pair has already been mediated
        invalid_pair = False
        if self.selected_cat0 and self.selected_cat1:
            for x in game.mediated:
                if self.selected_cat0.ID in x and self.selected_cat1.ID in x:
                    invalid_pair = True
                    mediator_status = i18n.t("screens.mediation.pair_already_mediated")
                    break

        # set status text
        self.mediator_elements["mediator_status"].set_text(mediator_status)

        # disable associated buttons if something is invalid
        if (invalid_mediator or invalid_pair) or not (
            self.selected_cat0 and self.selected_cat1
        ):
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

        self.remove_from_map(self.elements["cat_list"].cat_sprites.values())
        self.elements["cat_list"].update_display(self.page, current_listed_cats)
        self.add_to_map(self.elements["cat_list"].cat_sprites.values())

    def exit_screen(self):
        self.selected_cat0 = None
        self.selected_cat1 = None
        self.mediators.clear()
        self.tab_view = "all"

        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        for ele in self.elements.values():
            ele.kill()
        self.elements.clear()

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.back_button.kill()
        del self.back_button

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
