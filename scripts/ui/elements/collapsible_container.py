from typing import Optional, Union, Dict

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale


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
