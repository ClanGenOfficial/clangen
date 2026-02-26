import pygame
import pygame_gui

from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.scale import ui_scale_value


class UIImageHorizontalSlider(pygame_gui.elements.UIHorizontalSlider):
    """
    a subclass of UIHorizontalSlider, this is really only meant for one size and appearance of slider, though could
    be modified to allow for more customizability.  As we currently only use horizontal sliders in one spot and I
    don't foresee future additional sliders, I will leave it as is for now.
    """

    def __init__(
        self,
        relative_rect,
        start_value,
        value_range,
        click_increment=None,
        object_id=None,
        manager=None,
        anchors=None,
    ):
        super().__init__(
            relative_rect=relative_rect,
            start_value=start_value,
            value_range=value_range,
            click_increment=click_increment,
            object_id=object_id,
            manager=manager,
            anchors=anchors,
        )

        self.sliding_button_width = ui_scale_value(30)
        self.arrow_button_width = ui_scale_value(self.arrow_button_width)

        self.scrollable_width = (
            self.background_rect.width
            - self.sliding_button_width
            - (2 * self.arrow_button_width)
        )
        self.right_limit_position = self.scrollable_width
        self.scroll_position = self.scrollable_width / 2

        # kill the sliding button that the UIHorizontalSlider class makes, then make it again
        self.sliding_button.kill()
        self.sliding_button = UIImageButton(
            pygame.Rect(
                (0, 0), (self.sliding_button_width, self.background_rect.height)
            ),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#horizontal_slider_button",
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "bottom"},
            visible=self.visible,
        )

        # reset start value, for some reason it defaults to 50 otherwise
        self.set_current_value(start_value)
        # set hold range manually since using UIImageButton breaks it?
        self.sliding_button.set_hold_range((self.background_rect.width, 100))

        # kill and remake the left button
        self.left_button.kill()
        self.left_button = UIImageButton(
            pygame.Rect((0, 0), (self.arrow_button_width, self.background_rect.height)),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#horizontal_slider_left_arrow_button",
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "bottom"},
            visible=self.visible,
        )

        # kill and remake the right button
        self.right_button.kill()
        self.right_button = UIImageButton(
            pygame.Rect(
                (-self.arrow_button_width, 0),
                (ui_scale_value(20), self.background_rect.height),
            ),
            text="",
            manager=self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#horizontal_slider_right_arrow_button",
            anchors={
                "left": "right",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
            visible=self.visible,
        )
