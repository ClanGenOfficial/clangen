import pygame
from pygame_gui.core import IContainerLikeInterface

from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.scale import ui_scale


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
        container: IContainerLikeInterface,
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

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a
        straightforward matter of seeing if a point is inside the rectangle. Occasionally it
        will also check if we are in a wider zone around a UI element once it is already active,
        this makes it easier to move scroll bars and the like.

        :param hover_x: The x (horizontal) position of the point.
        :param hover_y: The y (vertical) position of the point.

        :return: Returns True if we are hovering this element.

        """

        container_clip_rect = self.ui_container.get_container().get_rect().copy()
        if self.ui_container.get_container().get_image_clipping_rect() is not None:
            container_clip_rect.size = (
                self.ui_container.get_container().get_image_clipping_rect().size
            )
            container_clip_rect.left += (
                self.ui_container.get_container().get_image_clipping_rect().left
            )
            container_clip_rect.top += (
                self.ui_container.get_container().get_image_clipping_rect().top
            )

        # ONLY CHANGE was to remove the drawable shape collide point check. for some reason, it would cause the checkbox
        # hover to desync when inside a scrolling container

        return bool(self.rect.collidepoint(hover_x, hover_y)) and bool(
            container_clip_rect.collidepoint(hover_x, hover_y)
        )
