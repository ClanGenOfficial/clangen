from functools import lru_cache
from math import ceil
from typing import Optional, List

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer
from pygame_gui.core.gui_type_hints import RectLike

from scripts.clan_package.settings import get_clan_setting
from scripts.events_module.text_adjust import shorten_text_to_fit
from scripts.game_structure import game
from scripts.game_structure.game import game_setting_get
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.scale import ui_scale_dimensions, ui_scale, ui_scale_value


class UICatListDisplay(UIContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        container: UIContainer,
        starting_height: int,
        manager,
        cat_list: list,
        cats_displayed: int,
        x_px_between: int,
        columns: int,
        current_page: int,
        next_button: UIImageButton,
        prev_button: UIImageButton,
        object_id: str = None,
        first_button: UIImageButton = None,
        last_button: UIImageButton = None,
        anchors: Optional[dict] = None,
        rows: int = None,
        show_names: bool = False,
        tool_tip_text_list: list = None,
        tool_tip_name: bool = False,
        tool_tip_nutrition: bool = False,
        custom_sprites_object_id: str = None,
        visible: bool = True,
        text_theme="#cat_list_text",
        y_px_between: int = None,
        allow_selection: bool = False,
    ):
        """
        Creates and displays a list of click-able cat sprites.
        :param relative_rect: The starting size and relative position of the container.
        :param container: The container this container is within. Defaults to None (which is the root
                          container for the UI)
        :param starting_height: The starting layer height of this container above its container.
                                Defaults to 1.
        :param object_id: An object ID for this element.
        :param manager: The UI manager for this element. If not provided or set to None,
                        it will try to use the first UIManager that was created by your application.
        :param cat_list: the list of cat objects that need to display
        :param cats_displayed: the number of cats to display on one page
        :param x_px_between: the pixel space between each column of cats
        :param y_px_between: the pixel space between each row of cats. Optional, defaults to x_px_between
        :param columns: the number of cats in a row before a new row is created
        :param next_button: the next_button ui_element
        :param prev_button: the prev_button ui_element
        :param current_page: the currently displayed page of the cat list
        :param tool_tip_name: should a tooltip displaying the cat's name be added to each cat sprite, default False
        :param tool_tip_nutrition: should a tooltip displaying the cat's nutrition status be added to each cat sprite, default False
        :param visible: Whether the element is visible by default. Warning - container visibility
                        may override this.
        :param allow_selection: Whether cats should be selectable.
        """

        super().__init__(
            relative_rect=relative_rect,
            container=container,
            starting_height=starting_height,
            object_id=object_id,
            visible=visible,
            anchors=anchors,
            manager=manager,
        )

        self.cat_list = cat_list
        self.cats_displayed = cats_displayed
        self.x_px_between = x_px_between
        self.y_px_between = y_px_between if y_px_between is not None else x_px_between
        self.columns = columns
        self.rows = rows if rows is not None else ceil(cats_displayed / columns)
        self.current_page = current_page
        self.next_button = next_button
        self.prev_button = prev_button
        self.first_button = first_button
        self.last_button = last_button
        self.tool_tip_text = tool_tip_text_list
        self.tool_tip_name = tool_tip_name
        self.tool_tip_nutrition = tool_tip_nutrition
        self.custom_sprites_object_id = custom_sprites_object_id
        self.text_theme = text_theme
        self.allow_selection = allow_selection

        self.total_pages: int = 0
        self.favor_indicator = {}
        self.cat_sprites = {}
        self.cat_names = {}
        self.cat_chunks = []
        self.boxes = []
        self.selection_boxes = {}
        self.selected = []

        self.show_names = show_names

        self._favor_circle = pygame.transform.scale(
            pygame.image.load(f"resources/images/fav_marker.png").convert_alpha(),
            ui_scale_dimensions((50, 50)),
        )
        if game_setting_get("dark mode"):
            self._favor_circle.set_alpha(150)

        self.generate_grid()

        self._chunk()
        self._display_cats()

    def generate_grid(self):
        """
        A wrapper for the grid generation to speed it up significantly.
        Must be done like this to avoid memory leak.
        """
        self.boxes = self._generate_grid_cached(
            self.relative_rect.width // self.columns,
            self.relative_rect.height // self.rows,
            self.rows,
            self.columns,
            self.ui_manager,
        )
        for box in self.boxes:
            box.set_container(self)
            box.rebuild()

    def cache_clear(self):
        """
        Clears the cached grid. This is only necessary for cat lists being displayed on popup windows. I'm not sure *why*, but the cache starts causing crashes. I recommend that we try to keep cat list displays on popup windows to a minimum to avoid lag and, when possible, hide & show the list instead of killing and recreating.
        """

        self._generate_grid_cached.cache_clear()

    @staticmethod
    @lru_cache(maxsize=5)
    def _generate_grid_cached(cell_width, cell_height, rows, columns, manager):
        boxes: List[Optional[UIContainer]] = [None] * (rows * columns)
        for i, box in enumerate(boxes):
            if i == 0:
                anchors = {}
            elif i % columns == 0:
                # first item in a row excluding first
                anchors = {"top_target": boxes[i - columns]}
            elif i < columns:
                # top row
                anchors = {"left_target": boxes[i - 1]}
            else:
                # all other rows
                anchors = {
                    "left_target": boxes[i - 1],
                    "top_target": boxes[i - columns],
                }

            boxes[i] = UIContainer(
                pygame.Rect(
                    0,
                    0,
                    cell_width,
                    cell_height,
                ),
                anchors=anchors,
                manager=manager,
            )
        return boxes

    def clear_display(self):
        [sprite.kill() for sprite in self.cat_sprites.values()]
        [name.kill() for name in self.cat_names.values()]
        [favor.kill() for favor in self.favor_indicator.values()]
        self.next_button = None
        self.prev_button = None
        self.first_button = None
        self.last_button = None

    def update_display(self, current_page: int, cat_list: list):
        """
        updates current_page and refreshes the cat display
        :param current_page: the currently displayed page
        :param cat_list: the new list of cats to display, leave None if list isn't changing, default None
        """

        self.current_page = current_page
        if cat_list != self.cat_list:
            self.cat_list = cat_list
            self._chunk()
        self._display_cats()

    def _chunk(self):
        """
        separates the cat list into smaller chunks to display on each page
        """
        self.cat_chunks = [
            self.cat_list[x : x + self.cats_displayed]
            for x in range(0, len(self.cat_list), self.cats_displayed)
        ]

    def _display_cats(self):
        """
        creates the cat display
        """
        self.current_page = max(1, min(self.current_page, len(self.cat_chunks)))

        self._update_arrow_buttons()

        display_cats = []
        if self.cat_chunks:
            self.total_pages = len(self.cat_chunks)
            display_cats = self.cat_chunks[self.current_page - 1]

        [sprite.kill() for sprite in self.cat_sprites.values()]
        [name.kill() for name in self.cat_names.values()]
        [favor.kill() for favor in self.favor_indicator.values()]

        show_fav = get_clan_setting("show fav")

        # FAVOURITE ICON
        if show_fav:
            fav_indexes = [
                display_cats.index(cat) for cat in display_cats if cat.favourite
            ]
            [self.create_favor_indicator(i, self.boxes[i]) for i in fav_indexes]

        # CAT SPRITE
        [
            self.create_cat_button(i, kitty, self.boxes[i])
            for i, kitty in enumerate(display_cats)
        ]

        # CAT NAME
        if self.show_names:
            [
                self.create_name(i, kitty, self.boxes[i])
                for i, kitty in enumerate(display_cats)
            ]

    def create_cat_button(self, i, kitty, container):
        if self.tool_tip_nutrition:
            condition_list = []
            if kitty.illnesses:
                if "starving" in kitty.illnesses.keys():
                    condition_list.append(i18n.t("conditions.illnesses.starving"))
                elif "malnourished" in kitty.illnesses.keys():
                    condition_list.append(i18n.t("conditions.illnesses.malnourished"))
            nutrition_info = game.clan.freshkill_pile.nutrition_info
            if kitty.ID in nutrition_info:
                full_text = i18n.t(
                    "screens.profile.nutrition_text",
                    nutrition_text=nutrition_info[kitty.ID].nutrition_text,
                )
                if get_clan_setting("showxp"):
                    full_text += f" ({str(int(nutrition_info[kitty.ID].percentage))})"
                condition_list.append(full_text)
            tooltip_text = (
                "<br>".join(condition_list) if len(condition_list) > 0 else None
            )
        elif self.tool_tip_name:
            tooltip_text = str(kitty.name)
        elif self.tool_tip_text:
            tooltip_text = self.tool_tip_text[
                i + ((self.current_page - 1) * self.cats_displayed)
            ]
        else:
            tooltip_text = None

        if self.allow_selection:
            self.selection_boxes[f"sprite{i}"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 15), (56, 56))),
                get_box(BoxStyles.SELECTION_BOX, (60, 60)),
                container=container,
                starting_height=1,
                manager=MANAGER,
                visible=False,
                anchors={"centerx": "centerx"},
            )
        self.cat_sprites[f"sprite{i}"] = UISpriteButton(
            ui_scale(pygame.Rect((0, 15), (50, 50))),
            kitty.sprite,
            cat_object=kitty,
            cat_id=kitty.ID,
            mask=None,
            container=container,
            object_id=f"#cat_sprite"
            if not self.custom_sprites_object_id
            else self.custom_sprites_object_id,
            tool_tip_text=tooltip_text,
            starting_height=1,
            anchors={"centerx": "centerx"},
        )

    def create_name(self, i, kitty, container):
        self.cat_names[f"name{i}"] = pygame_gui.elements.UILabel(
            pygame.Rect((0, 0), (container.rect[2], ui_scale_value(30))),
            shorten_text_to_fit(str(kitty.name), 220, 30),
            container=container,
            object_id=self.text_theme,
            anchors={
                "centerx": "centerx",
                "top_target": self.cat_sprites[f"sprite{i}"],
            },
        )

    def create_favor_indicator(self, i, container):
        self.favor_indicator[f"favor{i}"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 15), (50, 50))),
            self._favor_circle,
            object_id=f"favor_circle{i}",
            container=container,
            starting_height=1,
            anchors={"centerx": "centerx"},
        )

    def _update_arrow_buttons(self):
        """
        enables/disables appropriate arrow buttons
        """
        if len(self.cat_chunks) <= 1:
            self.prev_button.disable()
            self.next_button.disable()
            if self.first_button:
                self.first_button.disable()
                self.last_button.disable()
        elif self.current_page >= len(self.cat_chunks):
            self.prev_button.enable()
            self.next_button.disable()
            if self.first_button:
                self.first_button.enable()
                self.last_button.disable()
        elif self.current_page == 1 and len(self.cat_chunks) > 1:
            self.prev_button.disable()
            self.next_button.enable()
            if self.first_button:
                self.first_button.disable()
                self.last_button.enable()
        else:
            self.prev_button.enable()
            self.next_button.enable()
            if self.first_button:
                self.first_button.enable()
                self.last_button.enable()

    def process_event(self, event: pygame.event.Event) -> bool:
        if self.allow_selection and event.type in (
            pygame_gui.UI_BUTTON_ON_HOVERED,
            pygame_gui.UI_BUTTON_ON_UNHOVERED,
            pygame_gui.UI_BUTTON_START_PRESS,
        ):
            for sprite, button in self.cat_sprites.items():
                cat_id = button.return_cat_id()
                if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
                    if button != event.ui_element:
                        continue
                    self.selection_boxes[sprite].show()
                elif (
                    event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED
                    and cat_id not in self.selected
                ):
                    if button != event.ui_element:
                        continue
                    self.selection_boxes[sprite].hide()
                elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
                    if button != event.ui_element:
                        continue
                    if cat_id in self.selected:
                        self.selected.remove(cat_id)
                    else:
                        self.selected.append(cat_id)

        return super().process_event(event)

    def reset_selection(self):
        for box in self.selection_boxes.values():
            box.hide()
        self.selected.clear()

    def show(self, show_contents: bool = True):
        super().show(show_contents)

        if self.allow_selection:
            for sprite, button in self.cat_sprites.items():
                cat_id = button.return_cat_id()
                if cat_id not in self.selected:
                    self.selection_boxes[sprite].hide()
