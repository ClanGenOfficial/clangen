from typing import Tuple

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface
from pygame_gui.core.gui_type_hints import Coordinate
from pygame_gui.core.interfaces import IUIElementInterface

from scripts.ui.elements.modified_horizontal_scrollbar import UIModifiedHorizScrollBar
from scripts.ui.elements.image_vertical_scrollbar import UIImageVerticalScrollBar
from scripts.ui.scale import ui_scale_value


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
