from typing import Union, Optional, Dict, Iterable, Callable

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface, IUIElementInterface

from scripts.game_input import INPUT_ACTION_PRESSED, Action, INPUT_ACTION_RELEASED
from scripts.game_structure import game
from scripts.game_structure.screen_settings import screen


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
        parent_element: Optional[UIElement] = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        allow_double_clicks: bool = False,
        generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
        visible: int = 1,
        sound_id: str = None,
        mask: Union[pygame.Mask, pygame.Surface, None] = None,
        mask_padding: int = 2,
        *,
        command: Optional[Union[Callable, Dict[int, Callable]]] = None,
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
            manager=manager,
            container=container,
            tool_tip_text=tool_tip_text,
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
            text_kwargs=text_kwargs,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            max_dynamic_width=max_dynamic_width,
        )

        self._mask = None
        self.mask = mask

    @staticmethod
    def _scale_image_to_fit(
        image: pygame.Surface, target_size: tuple[int, int]
    ) -> pygame.Surface:
        """
        Scale an image to fit within the target size while maintaining aspect ratio.
        The image will be scaled to the largest size that fits within the target dimensions.

        :param image: The image surface to scale.
        :param target_size: The target size (width, height) to fit the image within.
        :return: The scaled image surface.
        """
        if image is None:
            return None

        image_width, image_height = image.get_size()
        target_width, target_height = target_size

        # Calculate scale factors for both dimensions
        scale_x = target_width / image_width
        scale_y = target_height / image_height

        # Use the smaller scale factor to ensure the image fits within the target size
        scale = min(scale_x, scale_y)

        # Calculate new dimensions
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        # Scale the image
        if new_width > 0 and new_height > 0:
            return pygame.transform.scale(
                image, (new_width, new_height)
            )  # This is the only line I changed from the orginal function.
        else:
            return image

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
        changed = super()._set_any_images_from_theme()

        if changed:
            self.mask = self.normal_images[0]

        return changed

    def return_sound_id(self):
        return self.sound_id
