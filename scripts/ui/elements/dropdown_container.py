from pygame_gui.core import UIContainer
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIAutoResizingContainer


class UIDropDownContainer(UIAutoResizingContainer):
    def __init__(
        self,
        relative_rect: RectLike,
        container: UIContainer,
        manager: IUIManagerInterface,
        starting_height: int = 1,
        object_id: str = None,
        visible: bool = False,
        anchors: dict = None,
        child_trigger_close: bool = False,
        starting_selection: list = None,
        open_on_hover: bool = False,
    ):
        """
        Holds all the elements of a dropdown and coordinates its basic responses.
        :param relative_rect: The starting size and relative position of the container.
        :param container: The container this container is within. Defaults to None (which is the root
                          container for the UI)
        :param starting_height: The starting layer height of this container above its container.
                                Defaults to 1.
        :param object_id: An object ID for this element.
        :param manager: The UI manager for this element. If not provided or set to None,
                        it will try to use the first UIManager that was created by your application.
        :param visible: Whether the element is visible by default. Warning - container visibility
                        may override this.
        :param open_on_hover: Dropdown will open while being hovered and close once unhovered

        """
        self.open_on_hover = open_on_hover

        super().__init__(
            relative_rect=relative_rect,
            container=container,
            object_id=object_id,
            starting_height=starting_height,
            visible=visible,
            manager=manager,
            anchors=anchors,
        )

        self.parent_button = None
        self.child_button_container = None
        self.child_buttons = []
        self.child_button_dicts = []

        self.is_open: bool = False
        self.child_trigger_close = child_trigger_close
        self.selected_list = (
            [item for item in starting_selection] if starting_selection else []
        )

    def close(self):
        """
        closes the dropdown
        """
        self.child_button_container.hide()

        self.resize_bottom = False
        self.set_dimensions(self.parent_button.get_relative_rect().size)

        self.is_open = False

    def open(self):
        """
        opens the dropdown
        """
        self.resize_bottom = True
        self.should_update_dimensions = True

        self.child_button_container.show()
        self.is_open = True

    def disable_child(self, item_name, button=None):
        """
        disables the given element and enables all other children
        clears self.selected_list and adds given item_name to it
        """
        if not button:
            button = self.child_button_dicts[item_name]

        button.disable()
        self.selected_list.clear()
        self.selected_list.append(item_name)

        for child in self.child_button_container.elements:
            if child == button:
                continue
            child.enable()

    def check_if_hovering(self):
        mouse_x, mouse_y = self.ui_manager.get_mouse_position()
        if self.hover_point(mouse_x, mouse_y):
            return True
        else:
            return False

    def update(self, time_delta: float):
        # hover
        if self.open_on_hover:
            if self.check_if_hovering():
                if not self.is_open and self.parent_button.hovered:
                    self.open()
            else:
                self.close()
        # press
        else:
            if self.parent_button.pressed:
                if self.is_open:
                    self.close()
                else:
                    self.open()

        super().update(time_delta)
