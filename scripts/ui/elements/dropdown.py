import pygame
from pygame_gui.core import UIContainer
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIAutoResizingContainer

from scripts.ui.elements.dropdown_container import UIDropDownContainer
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.scale import ui_scale


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
