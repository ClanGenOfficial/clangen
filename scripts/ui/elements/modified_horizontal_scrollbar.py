import pygame_gui
from pygame_gui.core.gui_type_hints import RectLike

from scripts.ui.scale import ui_scale_value


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
