import html
from functools import lru_cache
from math import ceil
from typing import Tuple, Optional, List

import pygame
import pygame_gui
from pygame_gui.core import UIContainer
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.text.html_parser import HTMLParser
from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.utility import translate
from pygame_gui.elements import UIAutoResizingContainer

from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.utility import scale, shorten_text_to_fit


class UIImageButton(pygame_gui.elements.UIButton):
    """Subclass of pygame_gui's button class. This allows for auto-scaling of the
    button image."""

    def __init__(self, relative_rect, text="", object_id=None, sound_id=None, visible=True, starting_height=1,
                 manager=None, tool_tip_text=None,
                 container=None, anchors=None, parent_element=None, allow_double_clicks=False):

        self.sound_id = sound_id

        super().__init__(relative_rect, text=text, object_id=object_id, visible=visible,
                         starting_height=starting_height, manager=manager, tool_tip_text=tool_tip_text,
                         container=container, anchors=anchors, parent_element=parent_element,
                         allow_double_clicks=allow_double_clicks)

    def _set_any_images_from_theme(self):
        changed = False
        normal_image = None
        try:
            normal_image = self.ui_theme.get_image(
                "normal_image", self.combined_element_ids
            )
            normal_image = pygame.transform.scale(
                normal_image, self.relative_rect.size
            )  # auto-rescale the image
        except LookupError:
            normal_image = None
        finally:
            if normal_image != self.normal_image:
                self.normal_image = normal_image
                self.hovered_image = normal_image
                self.selected_image = normal_image
                self.disabled_image = normal_image
                changed = True

        hovered_image = None
        try:
            hovered_image = self.ui_theme.get_image(
                "hovered_image", self.combined_element_ids
            )
            hovered_image = pygame.transform.scale(
                hovered_image, self.relative_rect.size
            )  # auto-rescale the image
        except LookupError:
            hovered_image = self.normal_image
        finally:
            if hovered_image != self.hovered_image:
                self.hovered_image = hovered_image
                changed = True

        selected_image = None
        try:
            selected_image = self.ui_theme.get_image(
                "selected_image", self.combined_element_ids
            )
            selected_image = pygame.transform.scale(
                selected_image, self.relative_rect.size
            )  # auto-rescale the image
        except LookupError:
            selected_image = self.normal_image
        finally:
            if selected_image != self.selected_image:
                self.selected_image = selected_image
                changed = True

        disabled_image = None
        try:
            disabled_image = self.ui_theme.get_image(
                "disabled_image", self.combined_element_ids
            )
            disabled_image = pygame.transform.scale(
                disabled_image, self.relative_rect.size
            )  # auto-rescale the image
        except LookupError:
            disabled_image = self.normal_image
        finally:
            if disabled_image != self.disabled_image:
                self.disabled_image = disabled_image
                changed = True

        return changed
    def return_sound_id(self):
        return self.sound_id

class UIModifiedScrollingContainer(pygame_gui.elements.UIScrollingContainer):
    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager=None,
        starting_height: int = 1,
        container=None,
        object_id=None,
        visible: int = 1,
        allow_scroll_x: bool = False,
        allow_scroll_y: bool = False,
    ):

        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            starting_height=starting_height,
            container=container,
            object_id=object_id,
            visible=visible,
            allow_scroll_x=allow_scroll_x,
            allow_scroll_y=allow_scroll_y,
            should_grow_automatically=True,
        )

        if self.allow_scroll_y:
            self.vert_scroll_bar.kill()
            self.vert_scroll_bar = None

            self.scroll_bar_width = self._get_scroll_bar_width()
            scroll_bar_rect = pygame.Rect(
                -self.scroll_bar_width,
                0,
                self.scroll_bar_width,
                self.relative_rect.height,
            )

            self.vert_scroll_bar = UIImageVerticalScrollBar(
                relative_rect=scroll_bar_rect,
                visible_percentage=1.0,
                manager=self.ui_manager,
                container=self._root_container,
                parent_element=self,
                starting_height=10,
                anchors={
                    "left": "right",
                    "right": "right",
                    "top": "top",
                    "bottom": "bottom",
                },
                visible=False,
            )
            self.join_focus_sets(self.vert_scroll_bar)

            self.vert_scroll_bar.set_container_this_will_scroll(
                self.scrollable_container
            )

        if self.allow_scroll_x:
            self.horiz_scroll_bar.kill()
            self.horiz_scroll_bar = None

            self.scroll_bar_height = self._get_scroll_bar_height()

            scroll_bar_rect = scale(
                pygame.Rect(
                    0,
                    -self.scroll_bar_height,
                    self.relative_rect.width,
                    self.scroll_bar_height,
                )
            )
            self.horiz_scroll_bar = UIModifiedHorizScrollBar(
                relative_rect=scroll_bar_rect,
                visible_percentage=1.0,
                manager=self.ui_manager,
                container=self._root_container,
                parent_element=self,
                anchors={
                    "left": "left",
                    "right": "right",
                    "top": "bottom",
                    "bottom": "bottom",
                },
                visible=False,
            )
            self.horiz_scroll_bar.set_dimensions((self.relative_rect.width, 0))
            self.horiz_scroll_bar.set_relative_position((0, 0))
            self.horiz_scroll_bar.set_container_this_will_scroll(
                self.scrollable_container
            )

    def set_view_container_dimensions(self, dimensions: Coordinate):
        self._view_container.set_dimensions(dimensions)

    def set_dimensions(self, dimensions, clamp_to_container: bool = False):
        super().set_dimensions(dimensions, clamp_to_container)

    def _sort_out_element_container_scroll_bars(self):
        """
        This creates, re-sizes or removes the scrollbars after resizing, but not after the scroll
        bar has been moved. Instead, it tries to keep the scrollbars in the same approximate position
        they were in before resizing
        """
        self.scroll_bar_width = self._get_scroll_bar_width()
        super()._sort_out_element_container_scroll_bars()

        if self.vert_scroll_bar:
            self.vert_scroll_bar.change_layer(9)
            self.vert_scroll_bar.show()

        if self.horiz_scroll_bar:
            self.horiz_scroll_bar.change_layer(9)
            self.horiz_scroll_bar.show()

    def _check_scroll_bars(self) -> Tuple[bool, bool]:
        """
        Check if we need a horizontal or vertical scrollbar.
        """
        self.scroll_bar_width = 0
        self.scroll_bar_height = 0
        need_horiz_scroll_bar = False
        need_vert_scroll_bar = False

        if (
            self.scrolling_height > self._view_container.rect.height
            or self.scrollable_container.relative_rect.top != 0
        ) and self.allow_scroll_y:
            need_vert_scroll_bar = True
            self.scroll_bar_width = self._get_scroll_bar_width()

        # Need to subtract scrollbar width here to account for when the above statement evaluated to True
        if (
            self.scrolling_width
            > self._view_container.rect.width - self.scroll_bar_width
            or self.scrollable_container.relative_rect.left != 0
        ) and self.allow_scroll_x:
            need_horiz_scroll_bar = True
            self.scroll_bar_height = self._get_scroll_bar_height()

            # Needs a second check for the case where we didn't need the vertical scroll bar until after creating a
            # horizontal scroll bar
            if (
                self.scrolling_height
                > self._view_container.rect.height - self.scroll_bar_height
                or self.scrollable_container.relative_rect.top != 0
            ) and self.allow_scroll_y:
                need_vert_scroll_bar = True
                self.scroll_bar_width = self._get_scroll_bar_width()

        self._calculate_scrolling_dimensions()
        return need_horiz_scroll_bar, need_vert_scroll_bar

    def _get_scroll_bar_width(self) -> int:
        if game.settings["fullscreen"]:
            return 44
        else:
            return 24

    def _get_scroll_bar_height(self) -> int:
        if game.settings["fullscreen"]:
            return 38
        else:
            return 20


class UIImageVerticalScrollBar(pygame_gui.elements.UIVerticalScrollBar):
    def __init__(
        self,
        relative_rect: pygame.Rect,
        visible_percentage: float,
        manager=None,
        container=None,
        parent_element=None,
        object_id=None,
        anchors=None,
        visible: int = 1,
        starting_height: int = 1,
    ):

        super().__init__(
            relative_rect=relative_rect,
            visible_percentage=visible_percentage,
            manager=manager,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

        self.scroll_wheel_speed = 100
        self.sliding_button.change_layer(starting_height)
        if game.settings["fullscreen"]:
            self.button_height = 32
        else:
            self.button_height = 16
        self.arrow_button_height = self.button_height
        self.top_button.kill()
        self.top_button = UIImageButton(
            scale(pygame.Rect((0, 0), (32, 32))),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=starting_height,
            parent_element=self,
            object_id="#vertical_slider_up_arrow_button",
            anchors={"left": "left", "right": "right", "top": "top", "bottom": "top"},
        )

        self.bottom_button.kill()
        self.bottom_button = UIImageButton(
            scale(pygame.Rect((0, -self.arrow_button_height), (32, 32))),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=starting_height,
            parent_element=self,
            object_id="#vertical_slider_down_arrow_button",
            anchors={
                "left": "left",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

    def set_visible_percentage(self, percentage: float):
        super().set_visible_percentage(percentage)
        if game.settings["fullscreen"]:
            speed = 30
        else:
            speed = 15
        self.scroll_wheel_speed = (1 / self.visible_percentage) * speed


class UIModifiedHorizScrollBar(pygame_gui.elements.UIHorizontalScrollBar):
    def __init__(
        self,
        relative_rect: RectLike,
        visible_percentage: float,
        manager,
        container,
        parent_element,
        anchors,
        visible,
    ):
        super().__init__(
            relative_rect,
            visible_percentage,
            manager=manager,
            container=container,
            parent_element=parent_element,
            anchors=anchors,
            visible=visible,
        )

        self.button_width = 15
        self.arrow_button_width = self.button_width

        self.rebuild()


class UISpriteButton:
    """This is for use with the cat sprites. It wraps together a UIImage and Transparent Button.
    For most functions, this can be used exactly like other pygame_gui elements."""

    def __init__(
        self,
        relative_rect,
        sprite,
        cat_id=None,
        visible=1,
        cat_object=None,
        starting_height=1,
        manager: IUIManagerInterface = None,
        container=None,
        object_id=None,
        tool_tip_text=None,
        anchors=None,
    ):

        # We have to scale the image before putting it into the image object. Otherwise, the method of upscaling that
        # UIImage uses will make the pixel art fuzzy
        self.image = pygame_gui.elements.UIImage(
            relative_rect,
            pygame.transform.scale(sprite, relative_rect.size),
            visible=visible,
            manager=manager,
            container=container,
            object_id=object_id,
            anchors=anchors,
        )
        self.image.disable()
        # The transparent button. This a subclass that UIButton that also hold the cat_id.

        self.button = CatButton(
            relative_rect,
            "",
            object_id="#cat_button",
            visible=visible,
            cat_id=cat_id,
            cat_object=cat_object,
            starting_height=starting_height,
            manager=manager,
            tool_tip_text=tool_tip_text,
            container=container,
            anchors=anchors,
        )

    def return_cat_id(self):
        return self.button.return_cat_id()

    def return_cat_object(self):
        return self.button.return_cat_object()

    def enable(self):
        self.button.enable()

    def disable(self):
        self.button.disable()

    def hide(self):
        self.image.hide()
        self.button.hide()

    def show(self):
        self.image.show()
        self.button.show()

    def kill(self):
        self.button.kill()
        self.image.kill()
        del self

    def set_image(self, new_image):
        self.image.set_image(new_image)

    """This is to simplify event handling. Rather that writing 
            'if event.ui_element = cat_sprite_object.button'
            you can treat is as any other single pygame UI element and write:
            'if event.ui_element = cat_sprite_object. """

    def __eq__(self, __o: object) -> bool:
        if self.button == __o:
            return True
        else:
            return False

    def get_abs_rect(self):
        return self.button.get_abs_rect()


class CatButton(UIImageButton):
    """Basic UIButton subclass for at sprite buttons. It stores the cat ID.
    Can also be used as a general button that holds some data"""

    def __init__(
        self,
        relative_rect,
        text,
        cat_id=None,
        visible=True,
        cat_object=None,
        starting_height=1,
        parent_element=None,
        object_id=None,
        manager=None,
        tool_tip_text=None,
        container=None,
        anchors=None,
    ):
        self.cat_id = cat_id
        self.cat_object = cat_object
        super().__init__(
            relative_rect,
            text,
            object_id=object_id,
            visible=visible,
            parent_element=parent_element,
            starting_height=starting_height,
            manager=manager,
            tool_tip_text=tool_tip_text,
            container=container,
            anchors=anchors,
            allow_double_clicks=True
        )

    def return_cat_id(self):
        return self.cat_id

    def return_cat_object(self):
        return self.cat_object

    def set_id(self, id):
        self.cat_id = id


class UITextBoxTweaked(pygame_gui.elements.UITextBox):
    """The default class has 1.25 line spacing. It would be fairly easy to allow the user to change that,
    but it doesn't allow it... for some reason This class only exists as a way to specify the line spacing. Please
    only use if you want to have control over the line spacing."""

    def __init__(
        self,
        html_text: str,
        relative_rect,
        manager=None,
        line_spacing=1,
        wrap_to_height: bool = False,
        starting_height: int = 1,
        container=None,
        parent_element=None,
        object_id=None,
        anchors=None,
        visible: int = 1,
        *,
        pre_parsing_enabled: bool = True,
        text_kwargs=None,
        allow_split_dashes: bool = True,
    ):

        self.line_spaceing = line_spacing

        super().__init__(
            html_text,
            relative_rect,
            manager=manager,
            container=container,
            starting_height=starting_height,
            wrap_to_height=wrap_to_height,
            parent_element=parent_element,
            anchors=anchors,
            object_id=object_id,
            visible=visible,
            pre_parsing_enabled=pre_parsing_enabled,
            text_kwargs=text_kwargs,
            allow_split_dashes=allow_split_dashes,
        )

    # 99% of this is copy-pasted from the original function.
    def _reparse_and_rebuild(self):
        self.parser = HTMLParser(
            self.ui_theme,
            self.combined_element_ids,
            self.link_style,
            line_spacing=self.line_spaceing,
        )  # THIS IS THE ONLY LINE CHANGED WITH THIS SUBCLASS
        self.rebuild()

    # 99% of this is copy-pasted from the original function.
    def parse_html_into_style_data(self):
        """
        Parses HTML styled string text into a format more useful for styling pygame.freetype
        rendered text.
        """
        feed_input = self.html_text
        if self.plain_text_display_only:
            feed_input = html.escape(
                feed_input
            )  # might have to add true to second param here for quotes
        feed_input = self._pre_parse_text(
            translate(feed_input, **self.text_kwargs) + self.appended_text
        )
        self.parser.feed(feed_input)

        default_font = self.ui_theme.get_font_dictionary().find_font(
            font_name=self.parser.default_style["font_name"],
            font_size=self.parser.default_style["font_size"],
            bold=self.parser.default_style["bold"],
            italic=self.parser.default_style["italic"],
        )
        default_font_data = {
            "font": default_font,
            "font_colour": self.parser.default_style["font_colour"],
            "bg_colour": self.parser.default_style["bg_colour"],
        }
        self.text_box_layout = TextBoxLayout(
            self.parser.layout_rect_queue,
            pygame.Rect((0, 0), (self.text_wrap_rect[2], self.text_wrap_rect[3])),
            pygame.Rect((0, 0), (self.text_wrap_rect[2], self.text_wrap_rect[3])),
            line_spacing=self.line_spaceing,
            # THIS IS THE ONLY LINE CHANGED WITH THIS SUBCLASS
            default_font_data=default_font_data,
            allow_split_dashes=self.allow_split_dashes,
        )
        self.parser.empty_layout_queue()
        if self.text_wrap_rect[3] == -1:
            self.text_box_layout.view_rect.height = (
                self.text_box_layout.layout_rect.height
            )

        self._align_all_text_rows()
        self.text_box_layout.finalise_to_new()


class UIRelationStatusBar:
    """Wraps together a status bar"""

    def __init__(
        self,
        relative_rect,
        percent_full=0,
        positive_trait=True,
        dark_mode=False,
        manager=None,
        style="bars",
    ):

        # Change the color of the bar depending on the value and if it's a negative or positive trait
        if percent_full > 49:
            if positive_trait:
                theme = "#relation_bar_pos"
            else:
                theme = "#relation_bar_neg"
        else:
            theme = "#relation_bar"

        # Determine dark mode or light mode
        if dark_mode:
            theme += "_dark"

        self.status_bar = pygame_gui.elements.UIStatusBar(
            relative_rect, object_id=theme, manager=manager
        )
        self.status_bar.percent_full = percent_full / 100

        # Now to make the overlay
        overlay_path = "resources/images/"
        if style == "bars":
            if dark_mode:
                overlay_path += "relations_border_bars_dark.png"
            else:
                overlay_path += "relations_border_bars.png"
        elif style == "dots":
            if dark_mode:
                overlay_path += "relations_border_dots_dark.png"
            else:
                overlay_path += "relations_border_dots.png"

        image = pygame.transform.scale(
            image_cache.load_image(overlay_path).convert_alpha(),
            (relative_rect[2], relative_rect[3]),
        )

        self.overlay = pygame_gui.elements.UIImage(
            relative_rect, image, manager=manager
        )

    def kill(self):
        self.status_bar.kill()
        self.overlay.kill()
        del self


class IDImageButton(UIImageButton):
    """Class to handle the "involved cats" button on the events page. It stores the IDs of the cat's involved."""

    def __init__(
        self,
        relative_rect,
        text="",
        ids=None,
        object_id=None,
        container=None,
        manager=None,
        layer_starting_height=1,
    ):

        if ids:
            self.ids = ids
        else:
            self.ids = None

        super().__init__(
            relative_rect,
            text,
            object_id=object_id,
            container=container,
            starting_height=layer_starting_height,
            manager=manager,
        )
        # This button will auto-disable if no ids are entered.
        if not self.ids:
            self.disable()


class UIDropDownContainer(UIAutoResizingContainer):
    """
    holds and controls the elements within a dropdown
    :param relative_rect: The starting size and relative position of the container.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param object_id: An object ID for this element.
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param parent_button: The button that opens and closes the dropdown
    :param child_button_container: The container holding the buttons within the dropdown
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this."""

    def __init__(
        self,
        relative_rect: RectLike,
        container: UIContainer,
        object_id: str,
        starting_height: int,
        parent_button: UIImageButton,
        child_button_container: UIContainer,
        manager: IUIManagerInterface,
        visible: bool = False,
    ):
        super().__init__(
            relative_rect=relative_rect,
            container=container,
            object_id=object_id,
            starting_height=starting_height,
            visible=visible,
            manager=manager,
        )

        self.parent_button = parent_button
        self.child_button_container = child_button_container

        self.is_open: bool = False
        self.selected_element = None

    def close(self):
        """
        closes the dropdown
        """
        self.child_button_container.hide()
        self.is_open = False

    def open(self):
        """
        opens the dropdown
        """
        self.child_button_container.show()
        self.is_open = True

    def disable_child(self, button):
        """
        disables the given element and enables all other children
        """

        button.disable()
        self.selected_element = button

        for child in self.child_button_container.elements:
            if child == button:
                continue
            child.enable()


class UICheckbox(UIImageButton):
    """
    Creates a checkbox and allows for easy check and uncheck
    :param position: The relative position of the container.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    :param check: the checkbox begins in the "checked" state, default False
    """

    def __init__(
        self,
        position: tuple,
        container: UIContainer,
        tool_tip_text: str,
        starting_height: int,
        visible: bool,
        manager,
        check: bool = False,
    ):

        self.checked = check

        relative_rect = scale(pygame.Rect(position, (68, 68)))

        if check:
            object_id = "#checked_checkbox"
        else:
            object_id = "#unchecked_checkbox"

        super().__init__(
            relative_rect=relative_rect,
            text="",
            container=container,
            tool_tip_text=tool_tip_text,
            starting_height=starting_height,
            visible=visible,
            manager=manager,
            object_id=object_id,
        )

    def check(self):
        """
        switches the checkbox into the "checked" state
        """
        self.checked = True
        self.change_object_id("#checked_checkbox")

    def uncheck(self):
        """
        switches the checkbox into the "unchecked" state
        """
        self.checked = False
        self.change_object_id("#unchecked_checkbox")


class UICatListDisplay(UIContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        container: UIContainer,
        starting_height: int,
        object_id: str,
        manager,
        cat_list: list,
        cats_displayed: int,
        x_px_between: int,
        columns: int,
        current_page: int,
        next_button: UIImageButton,
        prev_button: UIImageButton,
        first_button: UIImageButton = None,
        last_button: UIImageButton = None,
        anchors: Optional[dict] = None,
        rows: int = None,
        show_names: bool = False,
        tool_tip_name: bool = False,
        visible: bool = True,
        text_theme="#cat_list_text",
        y_px_between: int = None,
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
        :param visible: Whether the element is visible by default. Warning - container visibility
                        may override this.
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
        self.tool_tip_name = tool_tip_name
        self.text_theme = text_theme

        self.total_pages: int = 0
        self.favor_indicator = {}
        self.cat_sprites = {}
        self.cat_names = {}
        self.cat_chunks = []
        self.boxes = []

        self.show_names = show_names

        self._favor_circle = pygame.transform.scale(
            pygame.image.load(f"resources/images/fav_marker.png").convert_alpha(),
            (100, 100),
        )
        if game.settings["dark mode"]:
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

        show_fav = game.clan.clan_settings["show fav"]

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
        self.cat_sprites[f"sprite{i}"] = UISpriteButton(
            scale(pygame.Rect((0, 30), (100, 100))),
            kitty.sprite,
            cat_object=kitty,
            cat_id=kitty.ID,
            container=container,
            object_id=f"#sprite{str(i)}",
            tool_tip_text=str(kitty.name) if self.tool_tip_name else None,
            starting_height=1,
            anchors={"centerx": "centerx"},
        )

    def create_name(self, i, kitty, container):
        self.cat_names[f"name{i}"] = pygame_gui.elements.UILabel(
            scale(
                pygame.Rect(
                    (0, 10),
                    (100 + self.x_px_between, 60),
                )
            ),
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
            scale(pygame.Rect((0, 30), (100, 100))),
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

class UIImageHorizontalSlider(pygame_gui.elements.UIHorizontalSlider):
    """
    a subclass of UIHorizontalSlider, this is really only meant for one size and appearance of slider, though could
    be modified to allow for more customizability.  As we currently only use horizontal sliders in one spot and I
    don't forsee future additional sliders, I will leave it as is for now.
    """

    def __init__(self, relative_rect, start_value,
                 value_range, click_increment=None, object_id=None,
                 manager=None):
        super().__init__(relative_rect=relative_rect, start_value=start_value, value_range=value_range,
                         click_increment=click_increment, object_id=object_id, manager=manager)

        # kill the sliding button that the UIHorizontalSlider class makes, then make it again
        self.sliding_button.kill()
        sliding_x_pos = int(self.background_rect.width / 2 - self.sliding_button_width / 2)
        self.sliding_button = UIImageButton(scale(pygame.Rect((sliding_x_pos, 0),
                                                              (60,
                                                               44))),
                                            text='',
                                            manager=self.ui_manager,
                                            container=self.button_container,
                                            starting_height=1,
                                            parent_element=self,
                                            object_id="#horizontal_slider_button",
                                            anchors={'left': 'left',
                                                     'right': 'left',
                                                     'top': 'top',
                                                     'bottom': 'bottom'},
                                            visible=self.visible
                                            )

        # reset start value, for some reason it defaults to 50 otherwise
        self.set_current_value(start_value)
        # set hold range manually since using UIImageButton breaks it?
        self.sliding_button.set_hold_range((1600, 1400))

        # kill and remake the left button
        self.left_button.kill()
        self.left_button = UIImageButton(scale(pygame.Rect((0, 0),
                                                           (40, 44))),
                                         text='',
                                         manager=self.ui_manager,
                                         container=self.button_container,
                                         starting_height=1,
                                         parent_element=self,
                                         object_id="#horizontal_slider_left_arrow_button",
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'top',
                                                  'bottom': 'bottom'},
                                         visible=self.visible
                                         )

        # kill and remake the right button
        self.right_button.kill()
        self.right_button = UIImageButton(scale(pygame.Rect((-self.arrow_button_width, 0),
                                                            (40, 44))),
                                          text='',
                                          manager=self.ui_manager,
                                          container=self.button_container,
                                          starting_height=1,
                                          parent_element=self,
                                          object_id="#horizontal_slider_right_arrow_button",
                                          anchors={'left': 'right',
                                                   'right': 'right',
                                                   'top': 'top',
                                                   'bottom': 'bottom'},
                                          visible=self.visible
                                          )



