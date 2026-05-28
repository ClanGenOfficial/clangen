from typing import Dict, Any

import pygame
import pygame_gui
from pygame_gui import (
    UI_BUTTON_ON_HOVERED,
    UI_BUTTON_ON_UNHOVERED,
    UI_BUTTON_START_PRESS,
)
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIImage

from scripts.game_input import INPUT_ACTION_PRESSED, Action, INPUT_ACTION_RELEASED
from scripts.game_structure import image_cache, game
from scripts.ui.scale import ui_scale, ui_scale_dimensions, ui_scale_value


class UICruelCardLarge(UIImage):
    HOVER_MOVE_AMOUNT = 50

    def __init__(
        self,
        unscaled_position: tuple[int, int],
        image_path: str,
        name: str,
        group_layer_count: int,
        card_interval: int,
        last_in_line: bool = False,
        visible: bool = True,
        manager: IUIManagerInterface = None,
        container=None,
        starting_height: int = 1,
        anchors: dict = None,
    ):
        super().__init__(
            ui_scale(pygame.Rect(unscaled_position, (230, 360))),
            pygame.transform.scale(
                image_cache.load_image(image_path), ui_scale_dimensions((230, 360))
            ),
            visible=visible,
            manager=manager,
            container=container,
            object_id="#cruel_card",
            starting_height=starting_height,
            anchors=anchors,
        )

        self.held = False
        self.starting_position = unscaled_position
        self.group_layer_count = group_layer_count
        self.last_in_line = last_in_line
        self.card_interval = card_interval
        self.name = name

    def on_hovered(self):
        self.set_relative_position(
            (
                self.relative_rect.x,
                self.relative_rect.y - ui_scale_value(self.HOVER_MOVE_AMOUNT),
            )
        )
        self.change_layer(self.starting_height + self.group_layer_count)

        self.on_self_event(UI_BUTTON_ON_HOVERED)

        super().on_hovered()

    def on_unhovered(self):
        self.set_relative_position(ui_scale_dimensions(self.starting_position))
        self.change_layer(self.starting_height)
        self.on_self_event(UI_BUTTON_ON_UNHOVERED)

        super().on_unhovered()

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

        if self.drawable_shape is not None:
            return self.drawable_shape.collide_point((hover_x, hover_y)) and bool(
                container_clip_rect.collidepoint(hover_x, hover_y)
            )

        if self.hovered:
            hover_rect = self.rect.copy()
            hover_rect.height += ui_scale_value(self.HOVER_MOVE_AMOUNT)
            if not self.last_in_line:
                hover_rect.width = ui_scale_value(self.card_interval)
            return bool(hover_rect.collidepoint(hover_x, hover_y)) and bool(
                container_clip_rect.collidepoint(hover_x, hover_y)
            )

        return bool(self.rect.collidepoint(hover_x, hover_y)) and bool(
            container_clip_rect.collidepoint(hover_x, hover_y)
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False
        if self.is_focused and event.type == INPUT_ACTION_PRESSED:
            if event.action == Action.CONFIRM:
                self.on_self_event(
                    pygame_gui.UI_BUTTON_START_PRESS,
                    {"mouse_button": pygame.BUTTON_LEFT},
                )
        elif self.is_focused and event.type == INPUT_ACTION_RELEASED:
            if event.action == Action.CONFIRM:
                self.on_self_event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {"mouse_button": pygame.BUTTON_LEFT},
                )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(
                event.pos
            )
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                if self.is_enabled:
                    self.on_self_event(
                        UI_BUTTON_START_PRESS, {"mouse_button": event.button}
                    )
                    self.held = True
                    self.hovered = False
                    self.on_unhovered()

                consumed_event = True

        return consumed_event

    def on_self_event(self, event: int, data: Dict[str, Any] = None):
        """
        Called when an event is triggered by this element. Handles these events either by posting the event back
        to the event queue, or by running a function supplied by the user.

        :param event: The event triggered.

        :param data: event data

        """
        if data is None:
            data = {}

        event_data = data
        event_data.update(
            {
                "ui_element": self,
                "ui_object_id": self.most_specific_combined_id,
                "card_name": self.name,
            }
        )
        pygame.event.post(pygame.event.Event(event, event_data))
