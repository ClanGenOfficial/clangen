import html
from functools import lru_cache
from math import ceil
from typing import (
    Tuple,
    Optional,
    List,
    Union,
    Dict,
    Iterable,
    Callable,
)

import pygame
import pygame_gui
from pygame_gui.core import UIContainer, IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface, IUIElementInterface
from pygame_gui.core.text.html_parser import HTMLParser
from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.utility import translate
from pygame_gui.elements import UIAutoResizingContainer

from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import screen
from scripts.game_structure.game.settings import game_setting_get
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import (
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale_value,
)


class UISurfaceImageButton(pygame_gui.elements.UIButton):
    """Subclass of the button class that allows you to pass in surfaces for the images directly."""

    def __init__(
        self,
        relative_rect: Union[RectLike, Coordinate],
        text: str,
        image_dict: Dict[str, pygame.Surface],
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        tool_tip_text: Union[str, None] = None,
        starting_height: int = 1,
        parent_element: UIElement = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Dict[str, Union[str, UIElement]] = None,
        allow_double_clicks: bool = False,
        generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
        visible: int = 1,
        sound_id: str = None,
        *,
        command: Union[Callable, Dict[int, Callable]] = None,
        tool_tip_object_id: Optional[ObjectID] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
        tool_tip_text_kwargs: Optional[Dict[str, str]] = None,
        max_dynamic_width: Optional[int] = None,
        text_is_multiline: bool = False,
        text_layer_object_id: Optional[Union[ObjectID, str]] = None,
        tab_movement: Dict[str, bool] = None,
    ):
        self.sound_id = sound_id
        if object_id is None:
            ids = None
        else:
            ids = (
                [object_id.object_id, object_id.class_id]
                if isinstance(object_id, ObjectID)
                else [object_id]
            )

        self.tab_data = None
        if ids is not None:
            self._is_tab = any(["tab" in temp for temp in ids if temp is not None])
            self._is_bottom_tab = any(
                ["tab_bottom" in temp for temp in ids if temp is not None]
            )
        else:
            self._is_tab = False
        if self._is_tab:
            for obj_id in ids:
                obj_id = obj_id.replace("@buttonstyles_", "")
                try:
                    from scripts.ui.generate_button import buttonstyles

                    self.tab_data = buttonstyles[obj_id]["tab_movement"]
                    break
                except KeyError:
                    continue
            if self.tab_data is None:
                raise Exception(
                    "Button is tab, but unable to find matching data! Ensure object_id is correct & that buttonstyles has tab_movement key"
                )
            self.tab_movement = {
                "hovered": (
                    self.tab_data["hovered"]
                    if not hasattr(tab_movement, "hovered")
                    else tab_movement["hovered"]
                ),
                "disabled": (
                    self.tab_data["disabled"]
                    if not hasattr(tab_movement, "disabled")
                    else tab_movement["disabled"]
                ),
            }

        self._normal_image = image_dict["normal"]
        self._hovered_image = (
            image_dict["hovered"] if "hovered" in image_dict else self.normal_image
        )
        self._selected_image = (
            image_dict["selected"] if "selected" in image_dict else self.normal_image
        )
        self._disabled_image = (
            image_dict["disabled"] if "disabled" in image_dict else self.normal_image
        )
        super().__init__(
            relative_rect,
            text,
            manager,
            container,
            tool_tip_text,
            starting_height,
            parent_element,
            object_id,
            anchors,
            allow_double_clicks,
            generate_click_events_from,
            visible,
            command=command,
            tool_tip_object_id=tool_tip_object_id,
            text_kwargs=text_kwargs,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            max_dynamic_width=max_dynamic_width,
        )
        self.relative_rect = relative_rect

        if text_is_multiline or self._is_tab:
            temp_text = self.text
            if self._is_tab and self.tab_data["amount"][0] != 0:
                text_rect = pygame.Rect(
                    relative_rect[0] + ui_scale_value(self.tab_data["amount"][0]),
                    relative_rect[1] + ui_scale_value(self.tab_data["amount"][1]),
                    relative_rect[2] - ui_scale_value(self.tab_data["amount"][0]),
                    -1,
                )
            else:
                text_rect = pygame.Rect(
                    relative_rect[0], relative_rect[1], relative_rect[2], -1
                )
            self.set_text("")
            self.text_layer = UITextBoxTweaked(
                temp_text,
                text_rect,
                object_id=(
                    text_layer_object_id
                    if text_layer_object_id is not None
                    else object_id
                ),
                container=container,
                starting_height=self.starting_height,
                anchors=self.anchors,
                line_spacing=0.95,
            )
            self.join_focus_sets(self.text_layer)
            self.text_layer.disable()

            # Override the text layer hover check so that it doesn't block anything below it
            self.text_layer.check_hover = self.__text_layer_check_hover

            if self._is_tab:
                self.find_text_layer_pos()

    def __text_layer_check_hover(self, time_delta: float, hovered_higher_element: bool):
        return False

    def find_text_layer_pos(self):
        if self.text_layer.rect.height >= self.relative_rect[3]:
            if self._is_bottom_tab:
                offset = ui_scale_value(2)
            else:
                offset = 0
            offset = offset + (
                (self.text_layer.rect.height - self.relative_rect[3]) // 2
            )
            current = self.text_layer.get_relative_rect()
            self.text_layer.set_relative_position((current[0], current[1] - offset))
        text_layer_pos = self.text_layer.get_abs_rect()
        self.text_layer_offset = (text_layer_pos[0], text_layer_pos[1])
        self.text_layer_active_offset: Tuple[int, int] = (
            text_layer_pos[0] - ui_scale_value(self.tab_data["amount"][0]),
            text_layer_pos[1] - ui_scale_value(self.tab_data["amount"][1]),
        )

    def set_text(self, text: str, *, text_kwargs: Optional[Dict[str, str]] = None):
        if hasattr(self, "text_layer"):
            self.text_layer.set_text(text, text_kwargs=text_kwargs)
        else:
            super().set_text(text, text_kwargs=text_kwargs)

    def return_sound_id(self):
        return self.sound_id

    def kill(self):
        if hasattr(self, "text_layer"):
            self.text_layer.kill()
        super().kill()

    def hide(self):
        if hasattr(self, "text_layer"):
            self.text_layer.hide()
        super().hide()

    def show(self):
        if hasattr(self, "text_layer"):
            self.text_layer.show()
        super().show()

    def on_hovered(self):
        if self._is_tab and self.tab_movement["hovered"]:
            if self._is_bottom_tab:
                self.find_text_layer_pos()
            self.text_layer.set_position(self.text_layer_active_offset)
        super().on_hovered()

    def on_unhovered(self):
        if self._is_tab and self.tab_movement["hovered"]:
            if self._is_bottom_tab:
                self.find_text_layer_pos()
            self.text_layer.set_position(self.text_layer_offset)
        super().on_unhovered()

    def disable(self):
        if self.hovered:
            self.on_unhovered()
        super().disable()
        if self._is_tab and self.tab_movement["disabled"]:
            self.text_layer.set_position(self.text_layer_active_offset)

    def enable(self):
        super().enable()
        if self._is_tab and self.tab_movement["disabled"]:
            self.drawable_shape.active_state.transition = None
            self.text_layer.set_position(self.text_layer_offset)

    def _set_active(self):
        self.drawable_shape.set_active_state("hovered")

    @property
    def normal_image(self):
        return self._normal_image

    @normal_image.setter
    def normal_image(self, val):
        pass

    @property
    def hovered_image(self):
        return self._hovered_image

    @hovered_image.setter
    def hovered_image(self, val):
        pass

    @property
    def selected_image(self):
        return self._selected_image

    @selected_image.setter
    def selected_image(self, val):
        pass

    @property
    def disabled_image(self):
        return self._disabled_image

    @disabled_image.setter
    def disabled_image(self, val):
        pass


class UIImageButton(pygame_gui.elements.UIButton):
    """Subclass of pygame_gui's button class. This allows for auto-scaling of the
    button image."""

    def __init__(
        self,
        relative_rect: Union[RectLike, Coordinate],
        text: str,
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        tool_tip_text: Union[str, None] = None,
        starting_height: int = 1,
        parent_element: UIElement = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Dict[str, Union[str, UIElement]] = None,
        allow_double_clicks: bool = False,
        generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
        visible: int = 1,
        sound_id=None,
        mask: Union[pygame.Mask, pygame.Surface, None] = None,
        mask_padding: int = 2,
        *,
        command: Union[Callable, Dict[int, Callable]] = None,
        tool_tip_object_id: Optional[ObjectID] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
        tool_tip_text_kwargs: Optional[Dict[str, str]] = None,
        max_dynamic_width: Optional[int] = None,
    ):
        self.sound_id = sound_id
        self.mask_padding = mask_padding if mask_padding is not None else 2
        self.mask_info = [relative_rect[0:2], []]

        super().__init__(
            relative_rect=relative_rect,
            text=text,
            text_kwargs=text_kwargs,
            manager=manager,
            container=container,
            tool_tip_text=tool_tip_text,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            starting_height=starting_height,
            parent_element=parent_element,
            object_id=(
                ObjectID(class_id="@image_button", object_id=object_id)
                if not isinstance(object_id, ObjectID)
                else object_id
            ),
            anchors=anchors,
            allow_double_clicks=allow_double_clicks,
            generate_click_events_from=generate_click_events_from,
            visible=visible,
            command=command,
            tool_tip_object_id=tool_tip_object_id,
            max_dynamic_width=max_dynamic_width,
        )

        self._mask = None
        self.mask = mask

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, val: Union[pygame.Mask, pygame.Surface, None]):
        if not isinstance(val, Union[pygame.Mask, pygame.Surface, None]):
            return

        if val is None:
            self._mask = None
            return
        if isinstance(val, pygame.Mask):
            self._mask = val
            self.mask_padding = (val.get_size()[0] - self.rect[2]) / 2
        else:
            # if you're looking for the cat's sprite mask, that's
            # set in utility.py:update_mask
            val = pygame.mask.from_surface(val, threshold=250)

            inflated_mask = pygame.Mask(
                (
                    self.relative_rect[2] + self.mask_padding * 2,
                    self.relative_rect[3] + self.mask_padding * 2,
                )
            )
            inflated_mask.draw(val, (self.mask_padding, self.mask_padding))
            for _ in range(self.mask_padding):
                outline = inflated_mask.outline()
                for point in outline:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            try:
                                inflated_mask.set_at((point[0] + dx, point[1] + dy), 1)
                            except IndexError:
                                continue
            self._mask = inflated_mask
        self.mask_info[0] = (
            self.rect[0] - self.mask_padding,
            self.rect[1] - self.mask_padding,
        )
        self.mask_info[1] = [
            (
                x + self.mask_info[0][0],
                y + self.mask_info[0][1],
            )
            for x, y in self.mask.outline()
        ]

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
            self.mask = normal_image
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

    def hover_point(self, hover_x: int, hover_y: int) -> bool:
        if self.mask is None:
            return self.rect.collidepoint((hover_x, hover_y))
        pos_in_mask = (hover_x - self.mask_info[0][0], hover_y - self.mask_info[0][1])
        if (
            0 <= pos_in_mask[0] < self.mask.get_size()[0]
            and 0 <= pos_in_mask[1] < self.mask.get_size()[1]
        ):
            return bool(self.mask.get_at(pos_in_mask))
        else:
            return False

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        hover = super().check_hover(time_delta, hovered_higher_element)
        if game.debug_settings["showbounds"] and self.mask is not None:
            if hover:
                pygame.draw.lines(screen, (0, 255, 0), True, self.mask_info[1], width=2)
            else:
                pygame.draw.lines(screen, (255, 0, 0), True, self.mask_info[1], width=2)
        return hover


class UIModifiedScrollingContainer(
    pygame_gui.elements.UIScrollingContainer, IContainerLikeInterface
):
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
        should_grow_automatically=True,
        anchors=None,
    ):
        self.scroll_bar_starting_height = 1

        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            starting_height=starting_height,
            container=container,
            object_id=object_id,
            visible=visible,
            allow_scroll_x=allow_scroll_x,
            allow_scroll_y=allow_scroll_y,
            should_grow_automatically=should_grow_automatically,
            anchors=anchors,
        )
        self.scroll_bar_starting_height = self.get_top_layer()
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
                starting_height=self.scroll_bar_starting_height,
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

            scroll_bar_rect = pygame.Rect(
                0,
                -self.scroll_bar_height,
                self.relative_rect.width,
                self.scroll_bar_height,
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
                visible=True,
                starting_height=self.scroll_bar_starting_height,
            )
            self.horiz_scroll_bar.set_dimensions((self.relative_rect.width, 0))
            self.horiz_scroll_bar.set_relative_position((0, 0))
            self.horiz_scroll_bar.set_container_this_will_scroll(
                self.scrollable_container
            )
            self.join_focus_sets(self.horiz_scroll_bar)

    def set_view_container_dimensions(self, dimensions: Coordinate):
        self._view_container.set_dimensions(dimensions)

    def set_dimensions(self, dimensions, clamp_to_container: bool = False):
        super().set_dimensions(dimensions, clamp_to_container)

    def on_contained_elements_changed(self, target: IUIElementInterface) -> None:
        """
        Update the positioning of the contained elements of this container. To be called when one of the contained
        elements may have moved, been resized or changed its anchors.

        :param target: the UI element that has been benn moved resized or changed its anchors.
        """
        self.scrollable_container.on_contained_elements_changed(target)

    def _sort_out_element_container_scroll_bars(self):
        """
        This creates, re-sizes or removes the scrollbars after resizing, but not after the scroll
        bar has been moved. Instead, it tries to keep the scrollbars in the same approximate position
        they were in before resizing
        """
        self.scroll_bar_width = self._get_scroll_bar_width()
        super()._sort_out_element_container_scroll_bars()

        if self.vert_scroll_bar:
            self.vert_scroll_bar.change_layer(self.scroll_bar_starting_height)
            self.vert_scroll_bar.show()

        if self.horiz_scroll_bar:
            self.horiz_scroll_bar.change_layer(self.scroll_bar_starting_height)
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
        return ui_scale_value(20) + 4

    def _get_scroll_bar_height(self) -> int:
        return ui_scale_value(18) + 2

    def are_contents_hovered(self) -> bool:
        """
        Are any of the elements in the container hovered? Used for handling mousewheel events.

        :return: True if one of the elements is hovered, False otherwise.
        """
        for element in self:
            if any(sub_element.hovered for sub_element in element.get_focus_set()):
                return True
            elif (
                isinstance(element, IContainerLikeInterface)
                and element.are_contents_hovered()
            ):
                return True
        return False


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
        self.button_height = 16
        self.arrow_button_height = self.button_height
        self.top_button.kill()
        self.top_button = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (16, 16))),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=starting_height,
            parent_element=self,
            object_id="#vertical_slider_up_arrow_button",
            anchors={
                "centerx": "centerx",
            },
        )

        self.bottom_button.kill()
        bottom_button_rect = ui_scale(pygame.Rect((0, 0), (16, 16)))
        bottom_button_rect.bottomleft = (0, 0)
        self.bottom_button = UIImageButton(
            bottom_button_rect,
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=starting_height,
            parent_element=self,
            object_id="#vertical_slider_down_arrow_button",
            anchors={
                "bottom": "bottom",
                "centerx": "centerx",
            },
        )
        del bottom_button_rect

        self.sliding_button.kill()
        scroll_bar_height = max(
            5, int(self.scrollable_height * self.visible_percentage)
        )
        self.sliding_button = pygame_gui.elements.UIButton(
            pygame.Rect(
                (
                    int(self.sliding_rect_position[0]),
                    int(self.sliding_rect_position[1]),
                ),
                (self.background_rect.width, scroll_bar_height),
            ),
            "",
            self.ui_manager,
            container=self.button_container,
            starting_height=starting_height,
            parent_element=self,
            object_id="#sliding_button",
            anchors={"left": "left", "right": "right", "top": "top", "bottom": "top"},
        )

        self.join_focus_sets(self.sliding_button)
        self.sliding_button.set_hold_range((100, self.background_rect.height))

    def set_visible_percentage(self, percentage: float):
        super().set_visible_percentage(percentage)
        self.scroll_wheel_speed = (1 / self.visible_percentage) * ui_scale_value(15)

    def _check_should_handle_mousewheel_event(self) -> bool:
        def recursive_check_if_ignore(element):
            """
            If this is TRUE, we should ignore the scroll. This just helps with shortcutting
            :param element: The UIElement to check
            :return: True to ignore, False if we should care
            """
            if (
                isinstance(element, (UIScrollingDropDown, UIScrollingButtonList))
                and element.are_contents_hovered()
            ):
                return True
            elif isinstance(element, IContainerLikeInterface):
                for sub_element in element:
                    if recursive_check_if_ignore(sub_element):
                        return True
            return False

        # inverting the outcome of that
        if any(recursive_check_if_ignore(ele) for ele in self._container_to_scroll):
            return False
        else:
            return (
                self._container_to_scroll
                and self._container_to_scroll.are_contents_hovered()
            ) or self._check_is_focus_set_hovered()


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
        starting_height=1,
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

        self.button_width = ui_scale_value(15)
        self.arrow_button_width = self.button_width
        self.sliding_button.change_layer(starting_height + 1)

        self.rebuild()


class UISpriteButton:
    """This is for use with the cat sprites. It wraps together a UIImage and Transparent Button.
    For most functions, this can be used exactly like other pygame_gui elements."""

    def __init__(
        self,
        relative_rect: pygame.Rect,
        sprite: pygame.Surface,
        cat_id=None,
        visible=1,
        cat_object=None,
        starting_height=1,
        manager: IUIManagerInterface = None,
        container=None,
        object_id=None,
        tool_tip_object_id=None,
        tool_tip_text=None,
        text_kwargs=None,
        tool_tip_text_kwargs=None,
        anchors=None,
        mask=None,
        mask_padding=None,
    ):
        # The transparent button. This a subclass that UIButton that also hold the cat_id.

        self.button = CatButton(
            relative_rect,
            "",
            text_kwargs=text_kwargs,
            object_id=ObjectID("#cat_button", object_id),
            visible=visible,
            cat_id=cat_id,
            cat_object=cat_object,
            starting_height=starting_height,
            manager=manager,
            tool_tip_text=tool_tip_text,
            tool_tip_object_id=tool_tip_object_id,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            container=container,
            anchors=anchors,
            mask=mask,
            mask_padding=mask_padding,
        )
        input_sprite = sprite.premul_alpha()
        # if it's going to be small on the screen, smoothscale out the crunch
        input_sprite = (
            pygame.transform.smoothscale(input_sprite, relative_rect.size)
            if (
                (
                    relative_rect.height <= ui_scale_value(sprite.get_height())
                    or relative_rect.width <= ui_scale_value(sprite.get_height())
                )
                and not game_setting_get("no sprite antialiasing")
            )
            else pygame.transform.scale(input_sprite, relative_rect.size)
        )
        self.image = pygame_gui.elements.UIImage(
            relative_rect,
            input_sprite,
            visible=visible,
            manager=manager,
            container=container,
            object_id=object_id,
            anchors=anchors,
            starting_height=starting_height,
        )
        del input_sprite
        self.button.join_focus_sets(self.image)
        self.image.check_hover = self.__image_check_hover

    def __image_check_hover(self, time_delta: float, hovered_higher_element: bool):
        return False

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

    def on_hovered(self):
        self.button.on_hovered()


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
        text_kwargs=None,
        tool_tip_text_kwargs=None,
        container=None,
        anchors=None,
        mask=None,
        mask_padding=None,
        auto_disable_if_no_data=False,
        tool_tip_object_id=None,
    ):
        self.cat_id = cat_id
        self.cat_object = cat_object

        super().__init__(
            relative_rect,
            text,
            text_kwargs=text_kwargs,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            object_id=object_id,
            visible=visible,
            parent_element=parent_element,
            starting_height=starting_height,
            manager=manager,
            tool_tip_text=tool_tip_text,
            container=container,
            anchors=anchors,
            allow_double_clicks=True,
            mask=mask,
            mask_padding=mask_padding,
            tool_tip_object_id=tool_tip_object_id,
        )
        if auto_disable_if_no_data and cat_id is None and cat_object is None:
            self.disable()

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
        line_spacing: float = 1,
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


class IDImageButton(UISurfaceImageButton):
    """Class to handle the "involved cats" button on the events page. It stores the IDs of the cat's involved."""

    def __init__(
        self,
        relative_rect,
        text,
        button_dict,
        ids=None,
        object_id=None,
        container=None,
        manager=None,
        layer_starting_height=1,
        anchors=None,
        parent_element=None,
    ):
        if ids:
            self.ids = ids
        else:
            self.ids = None

        super().__init__(
            relative_rect,
            text,
            image_dict=button_dict,
            object_id=object_id,
            container=container,
            starting_height=layer_starting_height,
            manager=manager,
            anchors=anchors,
            parent_element=parent_element,
        )
        # This button will auto-disable if no ids are entered.
        if not self.ids:
            self.disable()


class UIDropDownContainer(UIAutoResizingContainer):
    """
    Holds all the elements of a dropdown and coordinates its basic responses.
    :param relative_rect: The starting size and relative position of the container.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param object_id: An object ID for this element.
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        container: UIContainer,
        manager: IUIManagerInterface,
        starting_height: int = 1,
        object_id: str = None,
        visible: bool = False,
        anchors: dict = None,
        child_trigger_close: bool = False,
        starting_selection: list = None,
    ):
        super().__init__(
            relative_rect=relative_rect,
            container=container,
            object_id=object_id,
            starting_height=starting_height,
            visible=visible,
            manager=manager,
            anchors=anchors,
        )

        self.parent_button = None
        self.child_button_container = None
        self.child_buttons = []
        self.child_button_dicts = []

        self.is_open: bool = False
        self.child_trigger_close = child_trigger_close
        self.selected_list = (
            [item for item in starting_selection] if starting_selection else []
        )

    def close(self):
        """
        closes the dropdown
        """
        self.child_button_container.hide()

        self.resize_bottom = False
        self.set_dimensions(self.parent_button.get_relative_rect().size)

        self.is_open = False

    def open(self):
        """
        opens the dropdown
        """
        self.resize_bottom = True
        self.should_update_dimensions = True

        self.child_button_container.show()
        self.is_open = True

    def disable_child(self, item_name, button=None):
        """
        disables the given element and enables all other children
        clears self.selected_list and adds given item_name to it
        """
        if not button:
            button = self.child_button_dicts[item_name]

        button.disable()
        self.selected_list.clear()
        self.selected_list.append(item_name)

        for child in self.child_button_container.elements:
            if child == button:
                continue
            child.enable()

    def update(self, time_delta: float):
        if self.parent_button.pressed:
            if self.is_open:
                self.close()
            else:
                self.open()

        super().update(time_delta)


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
        manager,
        visible: bool = True,
        tool_tip_text: str = None,
        starting_height: int = 1,
        check: bool = False,
        anchors=None,
    ):
        self.checked = check

        relative_rect = ui_scale(pygame.Rect(position, (34, 34)))

        if check:
            object_id = "@checked_checkbox"
        else:
            object_id = "@unchecked_checkbox"

        super().__init__(
            relative_rect=relative_rect,
            text="",
            container=container,
            tool_tip_text=tool_tip_text,
            starting_height=starting_height,
            visible=visible,
            manager=manager,
            object_id=object_id,
            anchors=anchors,
        )

    def check(self):
        """
        switches the checkbox into the "checked" state
        """
        self.checked = True
        self.change_object_id("@checked_checkbox")

    def uncheck(self):
        """
        switches the checkbox into the "unchecked" state
        """
        self.checked = False
        self.change_object_id("@unchecked_checkbox")


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
        self.cat_sprites[f"sprite{i}"] = UISpriteButton(
            ui_scale(pygame.Rect((0, 15), (50, 50))),
            kitty.sprite,
            cat_object=kitty,
            cat_id=kitty.ID,
            mask=None,
            container=container,
            object_id=f"#sprite{str(i)}",
            tool_tip_text=str(kitty.name) if self.tool_tip_name else None,
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


class UIImageHorizontalSlider(pygame_gui.elements.UIHorizontalSlider):
    """
    a subclass of UIHorizontalSlider, this is really only meant for one size and appearance of slider, though could
    be modified to allow for more customizability.  As we currently only use horizontal sliders in one spot and I
    don't foresee future additional sliders, I will leave it as is for now.
    """

    def __init__(
        self,
        relative_rect,
        start_value,
        value_range,
        click_increment=None,
        object_id=None,
        manager=None,
        anchors=None,
    ):
        super().__init__(
            relative_rect=relative_rect,
            start_value=start_value,
            value_range=value_range,
            click_increment=click_increment,
            object_id=object_id,
            manager=manager,
            anchors=anchors,
        )

        self.sliding_button_width = ui_scale_value(30)
        self.arrow_button_width = ui_scale_value(self.arrow_button_width)

        self.scrollable_width = (
            self.background_rect.width
            - self.sliding_button_width
            - (2 * self.arrow_button_width)
        )
        self.right_limit_position = self.scrollable_width
        self.scroll_position = self.scrollable_width / 2

        # kill the sliding button that the UIHorizontalSlider class makes, then make it again
        self.sliding_button.kill()
        self.sliding_button = UIImageButton(
            pygame.Rect(
                (0, 0), (self.sliding_button_width, self.background_rect.height)
            ),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#horizontal_slider_button",
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "bottom"},
            visible=self.visible,
        )

        # reset start value, for some reason it defaults to 50 otherwise
        self.set_current_value(start_value)
        # set hold range manually since using UIImageButton breaks it?
        self.sliding_button.set_hold_range((self.background_rect.width, 100))

        # kill and remake the left button
        self.left_button.kill()
        self.left_button = UIImageButton(
            pygame.Rect((0, 0), (self.arrow_button_width, self.background_rect.height)),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#horizontal_slider_left_arrow_button",
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "bottom"},
            visible=self.visible,
        )

        # kill and remake the right button
        self.right_button.kill()
        self.right_button = UIImageButton(
            pygame.Rect(
                (-self.arrow_button_width, 0),
                (ui_scale_value(20), self.background_rect.height),
            ),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#horizontal_slider_right_arrow_button",
            anchors={
                "left": "right",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
            visible=self.visible,
        )


class UIModifiedImage(pygame_gui.elements.UIImage):
    """
    UIImage class modified to prevent it from blocking hover actions in other elements
    """

    def __init__(
        self,
        relative_rect: RectLike,
        image_surface: pygame.surface.Surface,
        manager: Optional[IUIManagerInterface] = None,
        image_is_alpha_premultiplied: bool = False,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
        visible: int = 1,
        *,
        starting_height: int = 1,
    ):
        super().__init__(
            relative_rect=relative_rect,
            image_surface=image_surface,
            manager=manager,
            image_is_alpha_premultiplied=image_is_alpha_premultiplied,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
            starting_height=starting_height,
        )

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered
        by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function
                           and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a
                                       'higher' element.

        :return bool: A boolean that is true if we have hovered a UI element, either just now or
                      before this method.
        """
        should_block_hover = False
        if self.alive():
            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            mouse_pos = pygame.math.Vector2(mouse_x, mouse_y)

            if self.hover_point(mouse_x, mouse_y) and not hovered_higher_element:
                should_block_hover = True

                if self.can_hover():
                    if not self.hovered:
                        self.hovered = True
                        self.on_hovered()

                    self.while_hovering(time_delta, mouse_pos)
                else:
                    should_block_hover = False
                    if self.hovered:
                        self.hovered = False
                        self.on_unhovered()
            else:
                if self.hovered:
                    self.hovered = False
                    self.on_unhovered()
        elif self.hovered:
            self.hovered = False
        return should_block_hover

    def can_hover(self) -> bool:
        """
        A stub method to override. Called to test if this method can be hovered.
        """
        if self.alive() and self.is_enabled:
            return True
        else:
            return False


class UIScrollingButtonList(UIModifiedScrollingContainer):
    def __init__(
        self,
        relative_rect,
        item_list,
        button_dimensions: tuple,
        button_style=ButtonStyles.DROPDOWN,
        multiple_choice: bool = True,
        disable_selection: bool = False,
        offset_scroll: bool = True,
        manager=None,
        container=None,
        starting_height=1,
        object_id=None,
        anchors=None,
        visible=1,
        starting_selection: list = None,
    ):
        self.selected_list = (
            [item for item in starting_selection if starting_selection]
            if starting_selection
            else []
        )
        self.button_style = button_style
        child_rect_height = (
            button_dimensions[1] if button_dimensions else relative_rect.height
        )
        child_rect_width = (
            button_dimensions[0] if button_dimensions else relative_rect.width
        )
        self.child_rect = (child_rect_width, child_rect_height)

        if offset_scroll:
            relative_rect.width += 20

        self.vert_scroll_bar = None

        super().__init__(
            relative_rect=ui_scale(relative_rect.copy()),
            manager=manager,
            container=container,
            starting_height=starting_height,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
            allow_scroll_y=True,
        )
        self.buttons = {}
        self.multiple_choice = multiple_choice
        self.disable_selection = disable_selection
        self.total_button_height = (child_rect_height - 2) * len(item_list)
        prev_element = None
        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.buttons[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_rect)),
                child,
                get_button_dict(self.button_style, self.child_rect),
                manager=manager,
                object_id=f"@buttonstyles_{self.button_style.value}",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.buttons[child]

        if disable_selection and starting_selection:
            for button in starting_selection:
                self.buttons[button].disable()

    def hide(self):
        super().hide()
        if self.vert_scroll_bar:
            self.vert_scroll_bar.hide()

    def update(self, time_delta: float):
        # updates our selection list
        for name, button in self.buttons.items():
            # multiple choice
            if button.pressed and self.multiple_choice:
                if self.disable_selection:
                    button.disable()

                (
                    self.selected_list.remove(name)
                    if name in self.selected_list
                    else self.selected_list.append(name)
                )
                break

            # single choice
            elif button.pressed and not self.multiple_choice:
                if name in self.selected_list:
                    self.selected_list.clear()
                else:
                    self.selected_list.clear()
                    self.selected_list.append(name)
                if self.disable_selection:
                    for other_button in self.buttons.values():
                        other_button.enable()
                    button.disable()
                break

        super().update(time_delta)

        # don't ask me why the scroll bar doesn't obey the container's visibility, updating it after the super().update
        # fixes it and that's all I want to know
        if not self.visible:
            self.vert_scroll_bar.hide()

    def set_selected_list(self, new_list):
        self.selected_list.clear()
        self.selected_list = new_list
        if self.disable_selection:
            for item in self.selected_list:
                self.buttons[item].disable()

    def new_item_list(self, item_list):
        """
        Replace the old item_list with a new one. This kills and then rebuilds the child buttons.
        """
        # destroy old buttons and clear selected list
        for button in self.buttons.values():
            button.kill()
        self.buttons.clear()
        self.selected_list.clear()

        prev_element = None
        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.buttons[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_rect)),
                child,
                get_button_dict(self.button_style, self.child_rect),
                manager=self.ui_manager,
                object_id=f"@buttonstyles_{self.button_style.value}",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.buttons[child]


class UIDropDown(UIDropDownContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        parent_text: str,
        item_list: list or tuple,
        manager: IUIManagerInterface,
        container: UIContainer = None,
        child_dimensions: tuple = None,
        parent_style: ButtonStyles = ButtonStyles.DROPDOWN,
        parent_override=None,
        parent_reflect_selection=False,
        child_style: ButtonStyles = ButtonStyles.DROPDOWN,
        multiple_choice: bool = False,
        disable_selection: bool = True,
        starting_height: int = 1,
        object_id: str = None,
        visible: bool = True,
        anchors: dict = None,
        child_trigger_close: bool = True,
        starting_selection: list = None,
    ):
        """
        Class to handle the creation and management of non-scrolling dropdowns. It's recommended to use the on_use()
        screen func to check for changes to the selected_list attribute rather than handle_event()

        :param relative_rect: The rect for the parent button, by default these dimensions are also used for the child
        buttons. All positioning is based off this rect's position. THIS SHOULD NOT BE UI_SCALED
        :param parent_text: The text to display on the parent button.
        :param item_list: The list of options that will become child buttons.
        :param child_dimensions: This overrides the relative_rect dimensions for the child buttons, allowing you to create
        parent and child buttons with differing dimensions
        :param parent_style: The button style to use for the parent button, defaults to DROPDOWN
        :param parent_override: This isn't best practice to use, but it's an exception added for the filter dropdown
        :param parent_reflect_selection: When a selection is made, the parent text changes to reflect the selection.
        :param child_style: The button style to use for the child buttons, defaults to DROPDOWN
        :param multiple_choice: If the selected_list should hold multiple selections, defaults to False
        :param disable_selection: If the clicked child_button should be disabled, defaults to True
        :param child_trigger_close: If clicking a child_button should close the dropdown, defaults to True
        :param starting_selection: Items from item_list that should begin selected.
        """
        self.selected_list = (
            [item for item in starting_selection if starting_selection]
            if starting_selection
            else []
        )
        self.multiple_choice = multiple_choice
        self.disable_selection = disable_selection
        self.parent_text = parent_text
        self.parent_reflect_selection = parent_reflect_selection

        super().__init__(
            relative_rect=ui_scale(relative_rect.copy()),
            container=container,
            manager=manager,
            starting_height=starting_height,
            object_id=object_id,
            visible=visible,
            anchors=anchors,
            child_trigger_close=child_trigger_close,
            starting_selection=starting_selection,
        )

        rect = pygame.Rect(
            (relative_rect.x, 0), (relative_rect.width, relative_rect.height)
        )

        # create parent button
        if not parent_override:
            self.parent_button = UISurfaceImageButton(
                ui_scale(rect),
                parent_text,
                get_button_dict(parent_style, relative_rect.size),
                manager=manager,
                object_id=f"@buttonstyles_{parent_style.value}",
                container=self,
                anchors=anchors,
            )
        else:
            self.parent_button = parent_override

        dropdown_rect = ((relative_rect.x, 0), (0, 0))

        self.child_button_container = UIAutoResizingContainer(
            ui_scale(pygame.Rect(dropdown_rect)),
            manager=manager,
            container=self,
            resize_left=False,
            resize_top=False,
            anchors=(
                {
                    "top_target": self.parent_button,
                    "left_target": self.parent_button.anchors.get("left_target"),
                }
                if self.parent_button.anchors.get("left_target")
                else {"top_target": self.parent_button}
            ),
        )

        # create child buttons
        if child_dimensions:
            self.child_dimensions = child_dimensions
        else:
            self.child_dimensions = relative_rect.size

        self.child_style = child_style

        prev_element = None
        self.child_button_dicts = {}
        self.manager = manager

        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.child_button_dicts[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_dimensions)),
                child,
                get_button_dict(self.child_style, self.child_dimensions),
                manager=manager,
                object_id=f"@buttonstyles_{self.child_style.value}",
                container=self.child_button_container,
                starting_height=starting_height,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.child_button_dicts[child]

        self.child_buttons = self.child_button_dicts.values()
        if starting_selection:
            if disable_selection:
                for button in starting_selection:
                    self.child_button_dicts[button].disable()
            if parent_reflect_selection:
                self.parent_button.set_text(starting_selection[0])
        self.close()

    def new_item_list(self, item_list):
        """
        Replace the old item_list with a new one. This kills and then rebuilds the child buttons.
        """
        # destroy old buttons and clear selected list
        for button in self.child_button_dicts.values():
            button.kill()
        self.child_button_dicts.clear()
        self.selected_list.clear()

        prev_element = None
        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.child_button_dicts[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_dimensions)),
                child,
                get_button_dict(self.child_style, self.child_dimensions),
                manager=self.manager,
                object_id=f"@buttonstyles_{self.child_style.value}",
                container=self.child_button_container,
                starting_height=self.starting_height,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.child_button_dicts[child]

        self.child_buttons = self.child_button_dicts.values()

    def set_selected_list(self, new_list):
        self.selected_list.clear()
        self.selected_list = new_list
        if self.disable_selection:
            for item in self.selected_list:
                self.child_button_dicts[item].disable()
        if self.parent_reflect_selection and new_list:
            self.parent_button.set_text(new_list[0])

    def update(self, time_delta: float):
        # updates our selection list
        for name, button in self.child_button_dicts.items():
            if not button.pressed:
                continue

            if self.child_trigger_close:
                self.close()

            # multiple choice
            if self.multiple_choice:
                if name in self.selected_list:
                    self.selected_list.remove(name)
                else:
                    self.selected_list.append(name)

                if self.disable_selection:
                    button.disable()

                break
            # single choice
            elif not self.multiple_choice:
                if self.selected_list and self.selected_list[0] == name:
                    self.selected_list.clear()
                    if self.parent_reflect_selection:
                        self.parent_button.set_text(self.parent_text)
                else:
                    self.selected_list.clear()
                    self.selected_list.append(name)
                    if self.parent_reflect_selection:
                        self.parent_button.set_text(name)
                if self.disable_selection:
                    for other_button in self.child_buttons:
                        other_button.enable()
                    button.disable()
                break

        super().update(time_delta)


class UIScrollingDropDown(UIDropDownContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        manager: IUIManagerInterface,
        parent_text: str,
        item_list: list,
        dropdown_dimensions: tuple,
        container: UIContainer = None,
        child_dimensions: tuple = None,
        parent_style: ButtonStyles = ButtonStyles.DROPDOWN,
        child_style: ButtonStyles = ButtonStyles.DROPDOWN,
        offset_scroll: bool = True,
        multiple_choice: bool = True,
        disable_selection: bool = False,
        starting_height: int = 1,
        object_id: str = None,
        visible: bool = True,
        anchors: dict = None,
        child_trigger_close=False,
        starting_selection: list = None,
    ):
        """
        Class to handle the creation and management of scrolling dropdowns. It's recommended to use the on_use()
        screen func to check for changes to the selected_list attribute rather than handle_event()

        :param relative_rect: The rect for the parent button, by default these dimensions are also used for the child
        buttons. All positioning is based off this rect's position. THIS SHOULD NOT BE UI_SCALED
        :param parent_text: The text to display on the parent button.
        :param item_list: The list of options that will become child buttons.
        :param child_dimensions: This overrides the relative_rect dimensions for the child buttons, allowing you to create
        parent and child buttons with differing dimensions
        :param dropdown_dimensions: The dimensions for the dropdown. If there are enough item_list items to exceed these
         dimensions, then a scrollbar is created.
        :param parent_style: The button style to use for the parent button, defaults to DROPDOWN
        :param child_style: The button style to use for the child buttons, defaults to DROPDOWN
        :param offset_scroll: If the scrollbar will sit to the side of the dropdown, rather than overlapping, defaults
        to True
        :param multiple_choice: If the selected_list should hold multiple selections, defaults to True
        :param disable_selection: If the clicked child_button should be disabled, defaults to False
        :param child_trigger_close: If clicking a child_button should close the dropdown, defaults to False
        :param starting_selection: Items from item_list that should begin selected.
        """

        super().__init__(
            relative_rect=ui_scale(relative_rect.copy()),
            container=container,
            manager=manager,
            starting_height=starting_height,
            object_id=object_id,
            visible=visible,
            anchors=anchors,
            child_trigger_close=child_trigger_close,
            starting_selection=starting_selection,
        )

        # create parent button
        self.parent_button = UISurfaceImageButton(
            ui_scale(relative_rect.copy()),
            parent_text,
            get_button_dict(parent_style, relative_rect.size),
            manager=manager,
            object_id=f"@buttonstyles_{parent_style.value}",
            container=self,
            anchors=anchors,
        )

        # create child buttons
        if child_dimensions:
            dimensions = child_dimensions
        else:
            dimensions = relative_rect.size

        dropdown_rect = ((relative_rect.x, 0), dropdown_dimensions)
        self.child_button_container = UIScrollingButtonList(
            pygame.Rect(dropdown_rect),
            button_dimensions=dimensions,
            item_list=item_list,
            manager=manager,
            container=self,
            anchors=(
                {
                    "top_target": self.parent_button,
                    "left_target": self.parent_button.anchors.get("left_target"),
                }
                if self.parent_button.anchors.get("left_target")
                else {"top_target": self.parent_button}
            ),
            offset_scroll=offset_scroll,
            button_style=child_style,
            multiple_choice=multiple_choice,
            disable_selection=disable_selection,
            starting_selection=starting_selection,
        )
        self.child_buttons = self.child_button_container.buttons.values()
        self.child_button_dicts = self.child_button_container.buttons

        self.close()

    def update(self, time_delta: float):
        if self.is_open and self.child_trigger_close:
            for button in self.child_buttons:
                if button.pressed:
                    self.close()

        super().update(time_delta)

        self.selected_list = self.child_button_container.selected_list

    def set_selected_list(self, new_list):
        self.child_button_container.set_selected_list(new_list)

    def new_item_list(self, item_list):
        """
        Replace the old item_list with a new one. This kills and then rebuilds the child buttons.
        """
        self.child_button_container.new_item_list(item_list)

        self.child_buttons = self.child_button_container.buttons.values()
        self.child_button_dicts = self.child_button_container.buttons


class UICollapsibleContainer(
    pygame_gui.elements.UIAutoResizingContainer, IContainerLikeInterface
):
    def __init__(
        self,
        relative_rect: RectLike,
        title_text: str = None,
        top_button_oriented_left: bool = True,
        bottom_button: bool = True,
        bottom_button_oriented_left: bool = True,
        scrolling_container_to_reset=None,
        min_edges_rect: pygame.Rect = None,
        max_edges_rect: pygame.Rect = None,
        resize_left: bool = True,
        resize_right: bool = True,
        resize_top: bool = True,
        resize_bottom: bool = True,
        manager: Optional[IUIManagerInterface] = None,
        starting_height: int = 1,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        title_object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
        visible: int = 1,
    ):
        """
        A collapsible container that can be created with a title (text visible while closed) as well as top and bottom
        buttons on the right or left side.
        :param title_text: Text visible while container is closed, this will align with the top button
        :param top_button_oriented_left: The top button will appear on the far left of the container if this is True,
        else it will appear on the right. Default is True.
        :param bottom_button: Should this container have a bottom button. Default is True
        :param bottom_button_oriented_left: If it has a bottom button, will it be oriented to the left side. Default is True
        """
        super().__init__(
            relative_rect=relative_rect,
            min_edges_rect=min_edges_rect,
            max_edges_rect=max_edges_rect,
            resize_left=resize_left,
            resize_right=resize_right,
            resize_top=resize_top,
            resize_bottom=resize_bottom,
            manager=manager,
            starting_height=starting_height,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )
        self.title_text = None
        self.top_button_oriented_left = top_button_oriented_left
        self.bottom_button_oriented_left = bottom_button_oriented_left
        self.scrolling_container_to_reset = scrolling_container_to_reset

        rect = ui_scale(pygame.Rect((0, 0), (36, 36)))
        if not self.top_button_oriented_left:
            rect.topright = ((-10, 10),)
            anchors = {"right": "right"}
        else:
            rect.topleft = ((10, 10),)
            anchors = None

        self.top_button = UISurfaceImageButton(
            rect,
            Icon.ARROW_UP,
            get_button_dict(ButtonStyles.ICON, (36, 36)),
            manager=manager,
            object_id="@buttonstyles_icon",
            starting_height=1,
            container=self,
            tool_tip_text="buttons.collapse_down",
            anchors=anchors if anchors else None,
        )

        if title_text:
            self.title_text = UITextBoxTweaked(
                title_text,
                ui_scale(pygame.Rect((0, 10), (-1, -1))),
                object_id=title_object_id,
                line_spacing=1,
                manager=manager,
                container=self,
                anchors=(
                    {"left_target": self.top_button}
                    if self.top_button_oriented_left
                    else None
                ),
            )

        self.bottom_button = None
        if bottom_button:
            if not self.bottom_button_oriented_left:
                rect.bottomright = ((-10, 10),)
                anchors = {"right": "right", "bottom": "bottom"}
            else:
                rect.bottomleft = ((10, -10),)
                anchors = {"bottom": "bottom"}

            self.bottom_button = UISurfaceImageButton(
                rect,
                Icon.ARROW_UP,
                get_button_dict(ButtonStyles.ICON, (36, 36)),
                manager=manager,
                object_id="@buttonstyles_icon",
                starting_height=1,
                container=self,
                tool_tip_text="buttons.collapse_up",
                anchors=anchors,
            )

        self.is_open = True
        self.saved_scroll_position = None

    def close(self):
        """
        Closes the container, leaving only the top button visible
        """

        for ele in self.elements:
            if ele == self.title_text:
                continue
            if ele == self.top_button:
                self.top_button.set_text(Icon.ARROW_DOWN)
                self.top_button.set_tooltip("buttons.collapse_down")
                continue
            ele.hide()

        self.resize_bottom = False
        self.set_dimensions(
            (
                self.get_relative_rect().w,
                self.top_button.get_relative_rect().h
                + self.top_button.get_relative_rect().y,
            )
        )

        # this resets the scrolling container containing this container back to its prior position (or close to it)
        if self.scrolling_container_to_reset and self.saved_scroll_position:
            self.scrolling_container_to_reset.scrollable_container.recalculate_abs_edges_rect()
            self.scrolling_container_to_reset.update(1)

            self.scrolling_container_to_reset.vert_scroll_bar.set_scroll_from_start_percentage(
                self.saved_scroll_position
            )
            self.scrolling_container_to_reset.vert_scroll_bar.has_moved_recently = True
            self.scrolling_container_to_reset.update(1)

        self.is_open = False

    def open(self):
        """
        Opens the container, revealing its contents
        """
        if self.scrolling_container_to_reset:
            # saves the scroll positions .481 is the magic number to actually make this accurate, don't ask me why
            self.saved_scroll_position = (
                self.scrolling_container_to_reset.vert_scroll_bar.scroll_position
                * 0.481
            ) / self.scrolling_container_to_reset.vert_scroll_bar.scrollable_height
        for ele in self.elements:
            if ele == self.top_button:
                self.top_button.set_text(Icon.ARROW_UP)
                self.top_button.set_tooltip("buttons.collapse_up")
                continue
            ele.show()

        self.resize_bottom = True
        self.should_update_dimensions = True

        self.is_open = True

    def update(self, time_delta: float):
        if self.top_button.pressed:
            if self.is_open:
                self.close()
            else:
                self.open()
        elif self.bottom_button and self.bottom_button.pressed:
            if self.is_open:
                self.close()
            else:
                self.open()

        super().update(time_delta)
