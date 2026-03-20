from typing import Union, Optional, Dict, Iterable, Callable

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface

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
