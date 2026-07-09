from typing import Optional, Dict, Union, Any

import pygame
from pygame_gui import UI_BUTTON_ON_UNHOVERED, UI_BUTTON_ON_HOVERED
from pygame_gui.core import ObjectID, UIElement, IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.scale import ui_scale


class UICruelCardIcon(UIImageButton):
    def __init__(
        self,
        unscaled_position: tuple[int, int],
        name: str,
        container: Optional[IContainerLikeInterface] = None,
        tool_tip_text: Union[str, None] = None,
        starting_height: int = 1,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Dict[str, Union[str, UIElement]] = None,
        visible: int = 1,
        manager: Optional[IUIManagerInterface] = None,
    ):
        super().__init__(
            relative_rect=ui_scale(pygame.Rect(unscaled_position, (26, 38))),
            text="",
            manager=manager,
            container=container,
            tool_tip_text=tool_tip_text,
            starting_height=starting_height,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

        self.name = name

    def on_self_event(self, event: int, data: Dict[str, Any] = None):
        """
        Called when an event is triggered by this element. Handles these events either by posting the event back
        to the event queue, or by running a function supplied by the user.

        :param event: The event triggered.

        :param data: event data

        """
        if data is None:
            data = {}

        if event in self._handler:
            self._handler[event](data)
        else:
            event_data = data
            event_data.update(
                {
                    "ui_element": self,
                    "ui_object_id": self.most_specific_combined_id,
                    "card_name": self.name,
                }
            )
            pygame.event.post(pygame.event.Event(event, event_data))

    def on_unhovered(self):
        # we're overriding this completely because the base class is handling its hover events inconsistently
        # with how they handle click events, and we have to be able to use our overridden `on_self_event` for hover events
        if self.tool_tip is not None:
            self.tool_tip.kill()
            self.tool_tip = None

        if self.drawable_shape is not None:
            self.drawable_shape.set_active_state(self._get_appropriate_state_name())

        self.on_self_event(UI_BUTTON_ON_UNHOVERED)

    def on_hovered(self):
        # we're overriding this completely because the base class is handling its hover events inconsistently
        # with how they handle click events, and we have to be able to use our overridden `on_self_event` for hover events
        self.hover_time = 0.0

        self.drawable_shape.set_active_state("hovered")

        self.on_self_event(UI_BUTTON_ON_HOVERED)
