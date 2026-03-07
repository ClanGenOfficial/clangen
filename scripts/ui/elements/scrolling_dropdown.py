import pygame
from pygame_gui.core import UIContainer
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.ui.elements.dropdown_container import UIDropDownContainer
from scripts.ui.elements.scrolling_button_list import UIScrollingButtonList
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.scale import ui_scale


class UIScrollingDropDown(UIDropDownContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        manager: IUIManagerInterface,
        parent_text: str,
        item_list: list,
        dropdown_dimensions: tuple,
        container: UIContainer = None,
        child_dimensions: tuple = None,
        parent_style: ButtonStyles = ButtonStyles.DROPDOWN,
        child_style: ButtonStyles = ButtonStyles.DROPDOWN,
        offset_scroll: bool = True,
        multiple_choice: bool = True,
        disable_selection: bool = False,
        starting_height: int = 1,
        object_id: str = None,
        visible: bool = True,
        anchors: dict = None,
        child_trigger_close=False,
        starting_selection: list = None,
    ):
        """
        Class to handle the creation and management of scrolling dropdowns. It's recommended to use the on_use()
        screen func to check for changes to the selected_list attribute rather than handle_event()

        :param relative_rect: The rect for the parent button, by default these dimensions are also used for the child
        buttons. All positioning is based off this rect's position. THIS SHOULD NOT BE UI_SCALED
        :param parent_text: The text to display on the parent button.
        :param item_list: The list of options that will become child buttons.
        :param child_dimensions: This overrides the relative_rect dimensions for the child buttons, allowing you to create
        parent and child buttons with differing dimensions
        :param dropdown_dimensions: The dimensions for the dropdown. If there are enough item_list items to exceed these
         dimensions, then a scrollbar is created.
        :param parent_style: The button style to use for the parent button, defaults to DROPDOWN
        :param child_style: The button style to use for the child buttons, defaults to DROPDOWN
        :param offset_scroll: If the scrollbar will sit to the side of the dropdown, rather than overlapping, defaults
        to True
        :param multiple_choice: If the selected_list should hold multiple selections, defaults to True
        :param disable_selection: If the clicked child_button should be disabled, defaults to False
        :param child_trigger_close: If clicking a child_button should close the dropdown, defaults to False
        :param starting_selection: Items from item_list that should begin selected.
        """

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
        )

        # create parent button
        self.parent_button = UISurfaceImageButton(
            ui_scale(relative_rect.copy()),
            parent_text,
            get_button_dict(parent_style, relative_rect.size),
            manager=manager,
            object_id=f"@buttonstyles_{parent_style.value}",
            container=self,
            anchors=anchors,
        )

        # create child buttons
        if child_dimensions:
            dimensions = child_dimensions
        else:
            dimensions = relative_rect.size

        dropdown_rect = ((relative_rect.x, 0), dropdown_dimensions)
        self.child_button_container = UIScrollingButtonList(
            pygame.Rect(dropdown_rect),
            button_dimensions=dimensions,
            item_list=item_list,
            manager=manager,
            container=self,
            anchors=(
                {
                    "top_target": self.parent_button,
                    "left_target": self.parent_button.anchors.get("left_target"),
                }
                if self.parent_button.anchors.get("left_target")
                else {"top_target": self.parent_button}
            ),
            offset_scroll=offset_scroll,
            button_style=child_style,
            multiple_choice=multiple_choice,
            disable_selection=disable_selection,
            starting_selection=starting_selection,
        )
        self.child_buttons = self.child_button_container.buttons.values()
        self.child_button_dicts = self.child_button_container.buttons

        self.close()

    def update(self, time_delta: float):
        if self.is_open and self.child_trigger_close:
            for button in self.child_buttons:
                if button.pressed:
                    self.close()

        super().update(time_delta)

        self.selected_list = self.child_button_container.selected_list

    def set_selected_list(self, new_list):
        self.child_button_container.set_selected_list(new_list)

    def new_item_list(self, item_list):
        """
        Replace the old item_list with a new one. This kills and then rebuilds the child buttons.
        """
        self.child_button_container.new_item_list(item_list)

        self.child_buttons = self.child_button_container.buttons.values()
        self.child_button_dicts = self.child_button_container.buttons
