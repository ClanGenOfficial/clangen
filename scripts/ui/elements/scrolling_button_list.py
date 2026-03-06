import pygame

from scripts.ui.elements.modified_scrolling_container import (
    UIModifiedScrollingContainer,
)
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.scale import ui_scale


class UIScrollingButtonList(UIModifiedScrollingContainer):
    def __init__(
        self,
        relative_rect,
        item_list,
        button_dimensions: tuple,
        button_style=ButtonStyles.DROPDOWN,
        multiple_choice: bool = True,
        disable_selection: bool = False,
        offset_scroll: bool = True,
        manager=None,
        container=None,
        starting_height=1,
        object_id=None,
        anchors=None,
        visible=1,
        starting_selection: list = None,
    ):
        self.selected_list = (
            [item for item in starting_selection if starting_selection]
            if starting_selection
            else []
        )
        self.button_style = button_style
        child_rect_height = (
            button_dimensions[1] if button_dimensions else relative_rect.height
        )
        child_rect_width = (
            button_dimensions[0] if button_dimensions else relative_rect.width
        )
        self.child_rect = (child_rect_width, child_rect_height)

        if offset_scroll:
            relative_rect.width += 20

        self.vert_scroll_bar = None

        super().__init__(
            relative_rect=ui_scale(relative_rect.copy()),
            manager=manager,
            container=container,
            starting_height=starting_height,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
            allow_scroll_y=True,
        )
        self.buttons = {}
        self.multiple_choice = multiple_choice
        self.disable_selection = disable_selection
        self.total_button_height = (child_rect_height - 2) * len(item_list)
        prev_element = None
        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.buttons[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_rect)),
                child,
                get_button_dict(self.button_style, self.child_rect),
                manager=manager,
                object_id=f"@buttonstyles_{self.button_style.value}",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.buttons[child]

        if disable_selection and starting_selection:
            for button in starting_selection:
                self.buttons[button].disable()

    def hide(self):
        super().hide()
        if self.vert_scroll_bar:
            self.vert_scroll_bar.hide()

    def update(self, time_delta: float):
        # updates our selection list
        for name, button in self.buttons.items():
            # multiple choice
            if button.pressed and self.multiple_choice:
                if self.disable_selection:
                    button.disable()

                (
                    self.selected_list.remove(name)
                    if name in self.selected_list
                    else self.selected_list.append(name)
                )
                break

            # single choice
            elif button.pressed and not self.multiple_choice:
                if name in self.selected_list:
                    self.selected_list.clear()
                else:
                    self.selected_list.clear()
                    self.selected_list.append(name)
                if self.disable_selection:
                    for other_button in self.buttons.values():
                        other_button.enable()
                    button.disable()
                break

        super().update(time_delta)

        # don't ask me why the scroll bar doesn't obey the container's visibility, updating it after the super().update
        # fixes it and that's all I want to know
        if not self.visible:
            self.vert_scroll_bar.hide()

    def set_selected_list(self, new_list):
        self.selected_list.clear()
        self.selected_list = new_list
        if self.disable_selection:
            for item in self.selected_list:
                self.buttons[item].disable()

    def new_item_list(self, item_list):
        """
        Replace the old item_list with a new one. This kills and then rebuilds the child buttons.
        """
        # destroy old buttons and clear selected list
        for button in self.buttons.values():
            button.kill()
        self.buttons.clear()
        self.selected_list.clear()

        prev_element = None
        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.buttons[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_rect)),
                child,
                get_button_dict(self.button_style, self.child_rect),
                manager=self.ui_manager,
                object_id=f"@buttonstyles_{self.button_style.value}",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.buttons[child]
