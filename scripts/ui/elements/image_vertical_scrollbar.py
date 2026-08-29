import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface

from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.scale import ui_scale, ui_scale_value


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
                isinstance(
                    element,
                    (pygame_gui.elements.UIScrollingContainer),
                )
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
