from typing import Union, Dict, Optional, Iterable, Callable, Tuple

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.scale import ui_scale_value


class UISurfaceImageButton(pygame_gui.elements.UIButton):
    """Subclass of the button class that allows you to pass in surfaces for the images directly."""

    def __init__(
        self,
        relative_rect: Union[RectLike, Coordinate],
        text: str,
        image_dict: Dict[str, pygame.Surface],
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
        sound_id: str = None,
        *,
        command: Union[Callable, Dict[int, Callable]] = None,
        tool_tip_object_id: Optional[ObjectID] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
        tool_tip_text_kwargs: Optional[Dict[str, str]] = None,
        max_dynamic_width: Optional[int] = None,
        text_is_multiline: bool = False,
        text_layer_object_id: Optional[Union[ObjectID, str]] = None,
        tab_movement: Dict[str, bool] = None,
    ):
        self.sound_id = sound_id
        if object_id is None:
            ids = None
        else:
            ids = (
                [object_id.object_id, object_id.class_id]
                if isinstance(object_id, ObjectID)
                else [object_id]
            )

        self.tab_data = None
        if ids is not None:
            self._is_tab = any(["tab" in temp for temp in ids if temp is not None])
            self._is_bottom_tab = any(
                ["tab_bottom" in temp for temp in ids if temp is not None]
            )
        else:
            self._is_tab = False
        if self._is_tab:
            for obj_id in ids:
                obj_id = obj_id.replace("@buttonstyles_", "")
                try:
                    from scripts.ui.generate_button import buttonstyles

                    self.tab_data = buttonstyles[obj_id]["tab_movement"]
                    break
                except KeyError:
                    continue
            if self.tab_data is None:
                raise Exception(
                    "Button is tab, but unable to find matching data! Ensure object_id is correct & that buttonstyles has tab_movement key"
                )
            self.tab_movement = {
                "hovered": (
                    self.tab_data["hovered"]
                    if not hasattr(tab_movement, "hovered")
                    else tab_movement["hovered"]
                ),
                "disabled": (
                    self.tab_data["disabled"]
                    if not hasattr(tab_movement, "disabled")
                    else tab_movement["disabled"]
                ),
            }

        self._normal_image = image_dict["normal"]
        self._hovered_image = (
            image_dict["hovered"] if "hovered" in image_dict else self.normal_image
        )
        self._selected_image = (
            image_dict["selected"] if "selected" in image_dict else self.normal_image
        )
        self._disabled_image = (
            image_dict["disabled"] if "disabled" in image_dict else self.normal_image
        )
        super().__init__(
            relative_rect,
            text,
            manager,
            container,
            tool_tip_text,
            starting_height,
            parent_element,
            object_id,
            anchors,
            allow_double_clicks,
            generate_click_events_from,
            visible,
            command=command,
            tool_tip_object_id=tool_tip_object_id,
            text_kwargs=text_kwargs,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            max_dynamic_width=max_dynamic_width,
        )
        self.relative_rect = relative_rect

        if text_is_multiline or self._is_tab:
            temp_text = self.text
            if self._is_tab and self.tab_data["amount"][0] != 0:
                text_rect = pygame.Rect(
                    relative_rect[0] + ui_scale_value(self.tab_data["amount"][0]),
                    relative_rect[1] + ui_scale_value(self.tab_data["amount"][1]),
                    relative_rect[2] - ui_scale_value(self.tab_data["amount"][0]),
                    -1,
                )
            else:
                text_rect = pygame.Rect(
                    relative_rect[0], relative_rect[1], relative_rect[2], -1
                )
            self.set_text("")
            self.text_layer = UITextBoxTweaked(
                temp_text,
                text_rect,
                object_id=(
                    text_layer_object_id
                    if text_layer_object_id is not None
                    else object_id
                ),
                container=container,
                starting_height=self.starting_height,
                anchors=self.anchors,
                line_spacing=0.95,
            )
            self.join_focus_sets(self.text_layer)
            self.text_layer.disable()

            # Override the text layer hover check so that it doesn't block anything below it
            self.text_layer.check_hover = self.__text_layer_check_hover

            if self._is_tab:
                self.find_text_layer_pos()

    def __text_layer_check_hover(self, time_delta: float, hovered_higher_element: bool):
        return False

    def find_text_layer_pos(self):
        if self.text_layer.rect.height >= self.relative_rect[3]:
            if self._is_bottom_tab:
                offset = ui_scale_value(2)
            else:
                offset = 0
            offset = offset + (
                (self.text_layer.rect.height - self.relative_rect[3]) // 2
            )
            current = self.text_layer.get_relative_rect()
            self.text_layer.set_relative_position((current[0], current[1] - offset))
        text_layer_pos = self.text_layer.get_abs_rect()
        self.text_layer_offset = (text_layer_pos[0], text_layer_pos[1])
        self.text_layer_active_offset: Tuple[int, int] = (
            text_layer_pos[0] - ui_scale_value(self.tab_data["amount"][0]),
            text_layer_pos[1] - ui_scale_value(self.tab_data["amount"][1]),
        )

    def set_text(self, text: str, *, text_kwargs: Optional[Dict[str, str]] = None):
        if hasattr(self, "text_layer"):
            self.text_layer.set_text(text, text_kwargs=text_kwargs)
        else:
            super().set_text(text, text_kwargs=text_kwargs)

    def return_sound_id(self):
        return self.sound_id

    def kill(self):
        if hasattr(self, "text_layer"):
            self.text_layer.kill()
        super().kill()

    def hide(self):
        if hasattr(self, "text_layer"):
            self.text_layer.hide()
        super().hide()

    def show(self):
        if hasattr(self, "text_layer"):
            self.text_layer.show()
        super().show()

    def on_hovered(self):
        if self._is_tab and self.tab_movement["hovered"]:
            if self._is_bottom_tab:
                self.find_text_layer_pos()
            self.text_layer.set_position(self.text_layer_active_offset)
        super().on_hovered()

    def on_unhovered(self):
        if self._is_tab and self.tab_movement["hovered"]:
            if self._is_bottom_tab:
                self.find_text_layer_pos()
            self.text_layer.set_position(self.text_layer_offset)
        super().on_unhovered()

    def disable(self):
        if self.hovered:
            self.on_unhovered()
        super().disable()
        if self._is_tab and self.tab_movement["disabled"]:
            self.text_layer.set_position(self.text_layer_active_offset)

    def enable(self):
        super().enable()
        if self._is_tab and self.tab_movement["disabled"]:
            self.drawable_shape.active_state.transition = None
            self.text_layer.set_position(self.text_layer_offset)

    def _set_active(self):
        self.drawable_shape.set_active_state("hovered")

    @property
    def normal_image(self):
        return self._normal_image

    @normal_image.setter
    def normal_image(self, val):
        pass

    @property
    def hovered_image(self):
        return self._hovered_image

    @hovered_image.setter
    def hovered_image(self, val):
        pass

    @property
    def selected_image(self):
        return self._selected_image

    @selected_image.setter
    def selected_image(self, val):
        pass

    @property
    def disabled_image(self):
        return self._disabled_image

    @disabled_image.setter
    def disabled_image(self, val):
        pass
