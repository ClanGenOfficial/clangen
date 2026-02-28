from typing import Optional, Union, Dict

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIManagerInterface


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
