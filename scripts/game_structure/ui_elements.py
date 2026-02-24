from typing import (
    Optional,
    Union,
    Dict,
)

import pygame
import pygame_gui
from pygame_gui.core import UIContainer, IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIAutoResizingContainer

from scripts.ui.elements.dropdown_container import UIDropDownContainer
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale


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


class UIDropDown(UIDropDownContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        parent_text: str,
        item_list: list or tuple,
        manager: IUIManagerInterface,
        container: UIContainer = None,
        child_dimensions: tuple = None,
        center_children: bool = False,
        parent_style: ButtonStyles = ButtonStyles.DROPDOWN,
        parent_override=None,
        parent_reflect_selection=False,
        child_style: ButtonStyles = ButtonStyles.DROPDOWN,
        multiple_choice: bool = False,
        disable_selection: bool = True,
        starting_height: int = 1,
        object_id: str = None,
        visible: bool = True,
        anchors: dict = None,
        child_trigger_close: bool = True,
        starting_selection: list = None,
        open_on_hover: bool = False,
    ):
        """
        Class to handle the creation and management of non-scrolling dropdowns. It's recommended to use the on_use()
        screen func to check for changes to the selected_list attribute rather than handle_event()

        :param relative_rect: The rect for the parent button, by default these dimensions are also used for the child
        buttons. All positioning is based off this rect's position. THIS SHOULD NOT BE UI_SCALED
        :param parent_text: The text to display on the parent button.
        :param item_list: The list of options that will become child buttons.
        :param child_dimensions: This overrides the relative_rect dimensions for the child buttons, allowing you to create
        parent and child buttons with differing dimensions
        :param center_children: Set True if child buttons should be centered beneath the parent button, rather than anchored to the parent's left side. Only useful if child dimensions are larger than the parent's. Defaults to False.
        :param parent_style: The button style to use for the parent button, defaults to DROPDOWN
        :param parent_override: This isn't best practice to use, but it's an exception added for the filter dropdown
        :param parent_reflect_selection: When a selection is made, the parent text changes to reflect the selection.
        :param child_style: The button style to use for the child buttons, defaults to DROPDOWN
        :param multiple_choice: If the selected_list should hold multiple selections, defaults to False
        :param disable_selection: If the clicked child_button should be disabled, defaults to True
        :param child_trigger_close: If clicking a child_button should close the dropdown, defaults to True
        :param starting_selection: Items from item_list that should begin selected.
        :param open_on_hover: Dropdown will open while being hovered and close once unhovered
        """
        self.selected_list = (
            [item for item in starting_selection if starting_selection]
            if starting_selection
            else []
        )
        self.multiple_choice = multiple_choice
        self.disable_selection = disable_selection
        self.parent_text = parent_text
        self.parent_reflect_selection = parent_reflect_selection

        super().__init__(
            relative_rect=ui_scale(relative_rect.copy()),
            container=container,
            manager=manager,
            starting_height=starting_height,
            object_id=object_id,
            visible=visible,
            anchors=anchors,
            child_trigger_close=child_trigger_close,
            starting_selection=starting_selection,
            open_on_hover=open_on_hover,
        )

        rect = pygame.Rect(
            (relative_rect.x, 0), (relative_rect.width, relative_rect.height)
        )

        # create parent button
        if not parent_override:
            self.parent_button = UISurfaceImageButton(
                ui_scale(rect),
                parent_text,
                get_button_dict(parent_style, relative_rect.size),
                manager=manager,
                object_id=f"@buttonstyles_{parent_style.value}",
                container=self,
                anchors=anchors,
            )
        else:
            self.parent_button = parent_override
            self.parent_button.set_container(self)

        if center_children:
            x_pos = -int(child_dimensions[0] / 2 - relative_rect.width / 2)
        else:
            x_pos = relative_rect.x
        dropdown_rect = ((x_pos, 0), (0, 0))

        self.child_button_container = UIAutoResizingContainer(
            ui_scale(pygame.Rect(dropdown_rect)),
            manager=manager,
            container=self,
            resize_left=False,
            resize_top=False,
            anchors=(
                {
                    "top_target": self.parent_button,
                    "left_target": self.parent_button.anchors.get("left_target"),
                }
                if self.parent_button.anchors.get("left_target")
                else {"top_target": self.parent_button}
            ),
        )

        # create child buttons
        if child_dimensions:
            self.child_dimensions = child_dimensions
        else:
            self.child_dimensions = relative_rect.size

        self.child_style = child_style

        prev_element = None
        self.child_button_dicts = {}
        self.manager = manager

        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.child_button_dicts[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_dimensions)),
                child,
                get_button_dict(self.child_style, self.child_dimensions),
                manager=manager,
                object_id=f"@buttonstyles_{self.child_style.value}",
                container=self.child_button_container,
                starting_height=starting_height,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.child_button_dicts[child]

        self.child_buttons = self.child_button_dicts.values()
        if starting_selection:
            if disable_selection:
                for button in starting_selection:
                    self.child_button_dicts[button].disable()
            if parent_reflect_selection:
                self.parent_button.set_text(starting_selection[0])
        self.close()

    def new_item_list(self, item_list):
        """
        Replace the old item_list with a new one. This kills and then rebuilds the child buttons.
        """
        # destroy old buttons and clear selected list
        for button in self.child_button_dicts.values():
            button.kill()
        self.child_button_dicts.clear()
        self.selected_list.clear()

        prev_element = None
        for child in item_list:
            y_pos = -2 if prev_element else 0

            self.child_button_dicts[child] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), self.child_dimensions)),
                child,
                get_button_dict(self.child_style, self.child_dimensions),
                manager=self.manager,
                object_id=f"@buttonstyles_{self.child_style.value}",
                container=self.child_button_container,
                starting_height=self.starting_height,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.child_button_dicts[child]

        self.child_buttons = self.child_button_dicts.values()

    def set_selected_list(self, new_list):
        self.selected_list.clear()
        self.selected_list = new_list
        if self.disable_selection:
            for item in self.selected_list:
                self.child_button_dicts[item].disable()
        if self.parent_reflect_selection and new_list:
            self.parent_button.set_text(new_list[0])

    def update(self, time_delta: float):
        # updates our selection list
        for name, button in self.child_button_dicts.items():
            if not button.pressed:
                continue

            if self.child_trigger_close:
                self.close()

            # multiple choice
            if self.multiple_choice:
                if name in self.selected_list:
                    self.selected_list.remove(name)
                else:
                    self.selected_list.append(name)

                if self.disable_selection:
                    button.disable()

                break

            # single choice
            elif not self.multiple_choice:
                if self.selected_list and self.selected_list[0] == name:
                    self.selected_list.clear()
                    if self.parent_reflect_selection:
                        self.parent_button.set_text(self.parent_text)
                else:
                    self.selected_list.clear()
                    self.selected_list.append(name)
                    if self.parent_reflect_selection:
                        self.parent_button.set_text(name)
                if self.disable_selection:
                    for other_button in self.child_buttons:
                        other_button.enable()
                    button.disable()
                break

        super().update(time_delta)


class UICollapsibleContainer(
    pygame_gui.elements.UIAutoResizingContainer, IContainerLikeInterface
):
    def __init__(
        self,
        relative_rect: RectLike,
        title_text: str = None,
        top_button_oriented_left: bool = True,
        bottom_button: bool = True,
        bottom_button_oriented_left: bool = True,
        scrolling_container_to_reset=None,
        min_edges_rect: pygame.Rect = None,
        max_edges_rect: pygame.Rect = None,
        resize_left: bool = True,
        resize_right: bool = True,
        resize_top: bool = True,
        resize_bottom: bool = True,
        manager: Optional[IUIManagerInterface] = None,
        starting_height: int = 1,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        title_object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
        visible: int = 1,
    ):
        """
        A collapsible container that can be created with a title (text visible while closed) as well as top and bottom
        buttons on the right or left side.
        :param title_text: Text visible while container is closed, this will align with the top button
        :param top_button_oriented_left: The top button will appear on the far left of the container if this is True,
        else it will appear on the right. Default is True.
        :param bottom_button: Should this container have a bottom button. Default is True
        :param bottom_button_oriented_left: If it has a bottom button, will it be oriented to the left side. Default is True
        """
        super().__init__(
            relative_rect=relative_rect,
            min_edges_rect=min_edges_rect,
            max_edges_rect=max_edges_rect,
            resize_left=resize_left,
            resize_right=resize_right,
            resize_top=resize_top,
            resize_bottom=resize_bottom,
            manager=manager,
            starting_height=starting_height,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )
        self.title_text = None
        self.top_button_oriented_left = top_button_oriented_left
        self.bottom_button_oriented_left = bottom_button_oriented_left
        self.scrolling_container_to_reset = scrolling_container_to_reset

        rect = ui_scale(pygame.Rect((0, 0), (36, 36)))
        if not self.top_button_oriented_left:
            rect.topright = ((-10, 10),)
            anchors = {"right": "right"}
        else:
            rect.topleft = ((10, 10),)
            anchors = None

        self.top_button = UISurfaceImageButton(
            rect,
            Icon.ARROW_UP,
            get_button_dict(ButtonStyles.ICON, (36, 36)),
            manager=manager,
            object_id="@buttonstyles_icon",
            starting_height=1,
            container=self,
            tool_tip_text="buttons.collapse_down",
            anchors=anchors if anchors else None,
        )

        if title_text:
            self.title_text = UITextBoxTweaked(
                title_text,
                ui_scale(pygame.Rect((0, 10), (-1, -1))),
                object_id=title_object_id,
                line_spacing=1,
                manager=manager,
                container=self,
                anchors=(
                    {"left_target": self.top_button}
                    if self.top_button_oriented_left
                    else None
                ),
            )

        self.bottom_button = None
        if bottom_button:
            if not self.bottom_button_oriented_left:
                rect.bottomright = ((-10, 10),)
                anchors = {"right": "right", "bottom": "bottom"}
            else:
                rect.bottomleft = ((10, -10),)
                anchors = {"bottom": "bottom"}

            self.bottom_button = UISurfaceImageButton(
                rect,
                Icon.ARROW_UP,
                get_button_dict(ButtonStyles.ICON, (36, 36)),
                manager=manager,
                object_id="@buttonstyles_icon",
                starting_height=1,
                container=self,
                tool_tip_text="buttons.collapse_up",
                anchors=anchors,
            )

        self.is_open = True
        self.saved_scroll_position = None

    def close(self):
        """
        Closes the container, leaving only the top button visible
        """

        for ele in self.elements:
            if ele == self.title_text:
                continue
            if ele == self.top_button:
                self.top_button.set_text(Icon.ARROW_DOWN)
                self.top_button.set_tooltip("buttons.collapse_down")
                continue
            ele.hide()

        self.resize_bottom = False
        self.set_dimensions(
            (
                self.get_relative_rect().w,
                self.top_button.get_relative_rect().h
                + self.top_button.get_relative_rect().y,
            )
        )

        # this resets the scrolling container containing this container back to its prior position (or close to it)
        if self.scrolling_container_to_reset and self.saved_scroll_position:
            self.scrolling_container_to_reset.scrollable_container.recalculate_abs_edges_rect()
            self.scrolling_container_to_reset.update(1)

            self.scrolling_container_to_reset.vert_scroll_bar.set_scroll_from_start_percentage(
                self.saved_scroll_position
            )
            self.scrolling_container_to_reset.vert_scroll_bar.has_moved_recently = True
            self.scrolling_container_to_reset.update(1)

        self.is_open = False

    def open(self):
        """
        Opens the container, revealing its contents
        """
        if self.scrolling_container_to_reset:
            # saves the scroll positions .481 is the magic number to actually make this accurate, don't ask me why
            self.saved_scroll_position = (
                self.scrolling_container_to_reset.vert_scroll_bar.scroll_position
                * 0.481
            ) / self.scrolling_container_to_reset.vert_scroll_bar.scrollable_height
        for ele in self.elements:
            if ele == self.top_button:
                self.top_button.set_text(Icon.ARROW_UP)
                self.top_button.set_tooltip("buttons.collapse_up")
                continue
            ele.show()

        self.resize_bottom = True
        self.should_update_dimensions = True

        self.is_open = True

    def update(self, time_delta: float):
        if self.top_button.pressed:
            if self.is_open:
                self.close()
            else:
                self.open()
        elif self.bottom_button and self.bottom_button.pressed:
            if self.is_open:
                self.close()
            else:
                self.open()

        super().update(time_delta)
