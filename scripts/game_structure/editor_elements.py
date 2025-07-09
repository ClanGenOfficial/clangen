from typing import Tuple

import pygame
import pygame_gui

from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
    UIScrollingDropDown,
    UISurfaceImageButton,
    UIScrollingButtonList,
    UIModifiedImage,
)
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import get_text_box_theme, ui_scale


class EditorElement:
    def __init__(self):
        self.ui_elements = []
        self.bottom_element = None

    def kill(self):
        for ele in self.ui_elements:
            ele.kill()

    def hide(self):
        for ele in self.ui_elements:
            ele.hide()

    def show(self):
        for ele in self.ui_elements:
            ele.show()


class EditorLock(EditorElement):
    def __init__(
        self,
        name: str,
        position: tuple,
        manager=None,
        container=None,
        anchors=None,
    ):
        super().__init__()

        self.lock = UISurfaceImageButton(
            ui_scale(pygame.Rect(position, (36, 36))),
            Icon.UNLOCK,
            get_button_dict(ButtonStyles.ICON, (36, 36)),
            manager=manager,
            object_id="@buttonstyles_icon",
            container=container,
            anchors=anchors,
            starting_height=2,
            tool_tip_text="If locked, these parameters will be preserved when making a new event.",
        )
        self.ui_elements.append(self.lock)
        self.bottom_element = self.lock
        self.name = name

    def flip_state(self):
        """If locked, it will unlock. If unlocked, it will lock."""
        if self.locked:
            self.locked = False
        else:
            self.locked = True

    @property
    def locked(self):
        return self.lock.text == Icon.LOCK

    @locked.setter
    def locked(self, lock: bool):
        """Set True to lock, set False to unlock."""
        self.lock.set_text(Icon.LOCK if lock else Icon.UNLOCK)


class EditorTextEntryLine(EditorElement):
    def __init__(
        self,
        position: Tuple[int, int],
        anchors: dict = None,
        container=None,
        description: str = None,
        entry_length: int = None,
        initial_entry_text: str = "",
        manager=None,
        lock: bool = False,
        lock_name: str = None,
    ):
        """
        Creates descriptive text and an associated entry line.
        :param position: The element's position
        :param anchors: The element's anchors
        :param container: The element's container
        :param description: The descriptive text to precede the entry line
        :param entry_length: The entry line length
        :param initial_entry_text: The initial entry text
        :param manager: The element's manager
        """
        super().__init__()

        self.description = UITextBoxTweaked(
            description,
            ui_scale(pygame.Rect(position, (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=manager,
            container=container,
            anchors=anchors,
        )
        self.ui_elements.append(self.description)
        entry_anchors = {"left_target": self.description}
        if anchors and "top_target" in anchors:
            entry_anchors["top_target"] = anchors["top_target"]
        self.initial_entry_text = initial_entry_text
        self.entry = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 16), (entry_length, 29))),
            manager=manager,
            container=container,
            anchors=entry_anchors,
            initial_text=self.initial_entry_text,
        )
        self.ui_elements.append(self.entry)

        if lock:
            lock_anchors = None
            if anchors and "top_target" in anchors:
                lock_anchors = {"top_target": anchors["top_target"]}
            self.lock = EditorLock(
                position=(400, 10),
                name=lock_name,
                anchors=lock_anchors,
                manager=manager,
                container=container,
            )
            self.ui_elements.append(self.lock)

        self.bottom_element = self.description

    @property
    def changed(self) -> bool:
        """
        Returns true if the entry text has changed since last checked.
        """
        if self.entry.text != self.initial_entry_text:
            # save new text state to compare when next changed
            self.initial_entry_text = self.entry.text
            return True
        return False

    @property
    def info(self) -> str:
        """
        Returns the currently entered text
        """
        return self.entry.text


class EditorDropDownSelection(EditorElement):
    def __init__(
        self,
        position: Tuple[int, int],
        anchors: dict = None,
        container=None,
        description: str = None,
        item_list: list = None,
        starting_selection: list = None,
        dropdown_parent_text: str = None,
        multiple_choice: bool = False,
        disable_selection: bool = False,
        child_trigger_close: bool = False,
        display_text: str = None,
        lock: bool = False,
        lock_name: str = None,
        manager=None,
    ):
        """
        Creates descriptive text and an associated scrolling dropdown.
        """
        super().__init__()

        self.description = UITextBoxTweaked(
            description,
            ui_scale(pygame.Rect(position, (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=manager,
            container=container,
            anchors=anchors,
        )
        self.ui_elements.append(self.description)

        dropdown_anchors = {"left_target": self.description}
        if anchors.get("top_target"):
            dropdown_anchors["top_target"] = anchors["top_target"]
        self.selection = starting_selection
        self.dropdown = UIScrollingDropDown(
            pygame.Rect((10, 20), (150, 30)),
            dropdown_dimensions=(150, 200),
            parent_text=dropdown_parent_text,
            item_list=item_list,
            container=container,
            manager=manager,
            multiple_choice=multiple_choice,
            disable_selection=disable_selection,
            child_trigger_close=child_trigger_close,
            starting_selection=self.selection,
            starting_height=5,
            anchors=dropdown_anchors,
        )
        self.ui_elements.append(self.dropdown)

        self.display_text = display_text
        self.display = UITextBoxTweaked(
            f"{self.display_text} {starting_selection}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=manager,
            container=container,
            anchors={
                "top_target": self.description,
            },
            allow_split_dashes=False,
        )
        self.ui_elements.append(self.display)

        if lock:
            self.lock = EditorLock(
                position=(10, 10),
                name=lock_name,
                anchors={"top_target": self.description, "left_target": self.display},
                manager=manager,
                container=container,
            )
            self.ui_elements.append(self.lock)

        self.bottom_element = self.display

    @property
    def changed(self):
        if self.selection != self.dropdown.selected_list:
            self.selection = self.dropdown.selected_list.copy()
            return True
        return False

    @property
    def info(self):
        return self.dropdown.selected_list.copy()

    @property
    def displayed_info(self):
        return self.display.html_text

    @displayed_info.setter
    def displayed_info(self, new_text):
        self.display.set_text(f"{self.display_text} {new_text}")


class EditorTwoStepSelection(EditorElement):
    def __init__(
        self,
        position: Tuple[int, int],
        anchors: dict = None,
        container=None,
        description: str = None,
        item_dict: dict = None,
        key_selection: list = None,
        value_selection: list = None,
        display_text: str = None,
        lock: bool = False,
        lock_name: str = None,
        manager=None,
    ):
        """
        Creates descriptive text and an associated two-step selection element. The two-step selection element is a list of broader categories that allows the user to open each category and select from it's held options.
        :param position: The element's position
        :param anchors: The element's anchors
        :param container: The element's container
        :param description: The descriptive text to precede the entry line
        :param manager: The element's manager
        """
        super().__init__()

        self.item_dict = item_dict

        self.description = UITextBoxTweaked(
            description,
            ui_scale(pygame.Rect(position, (420, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=manager,
            container=container,
            anchors=anchors,
        )
        self.ui_elements.append(self.description)

        self.keys = UIScrollingButtonList(
            pygame.Rect((25, 20), (200, 198)),
            item_list=list(item_dict.keys()),
            button_dimensions=(200, 30),
            multiple_choice=False,
            starting_selection=key_selection,
            container=container,
            anchors={"top_target": self.description},
            manager=manager,
        )
        self.ui_elements.append(self.keys)
        self.key_selection = key_selection

        self.frame = UIModifiedImage(
            ui_scale(pygame.Rect((-20, 30), (180, 170))),
            get_box(BoxStyles.ROUNDED_BOX, (180, 170)),
            manager=manager,
            container=container,
            anchors={
                "top_target": self.description,
                "left_target": self.keys,
            },
        )
        self.frame.disable()
        self.ui_elements.append(self.frame)
        self.values = UIScrollingButtonList(
            pygame.Rect((-4, 38), (156, 152)),
            item_list=list(item_dict.values()),
            button_dimensions=(156, 30),
            starting_selection=value_selection,
            container=container,
            anchors={
                "top_target": self.description,
                "left_target": self.keys,
            },
            manager=manager,
        )
        self.ui_elements.append(self.values)
        self.value_selection = value_selection

        self.display_text = display_text
        self.display = UITextBoxTweaked(
            f"{display_text} {value_selection}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=manager,
            container=container,
            anchors={
                "top_target": self.keys,
            },
            allow_split_dashes=False,
        )
        self.ui_elements.append(self.display)

        if lock:
            self.lock = EditorLock(
                position=(10, 10),
                name=lock_name,
                anchors={"top_target": self.keys, "left_target": self.display},
                manager=manager,
                container=container,
            )
        self.ui_elements.append(self.lock)
        self.bottom_element = self.display

    @property
    def changed(self):
        if self.key_selection != self.keys.selected_list:
            self.key_selection = self.keys.selected_list.copy()
            self.update_values()
            return True
        elif self.value_selection != self.values.selected_list:
            self.value_selection = self.values.selected_list.copy()
            return True
        return False

    @property
    def info(self) -> dict:
        current_info: dict = {self.key_selection[0]: self.value_selection}
        return current_info

    @property
    def displayed_info(self) -> str:
        return self.display.html_text

    @displayed_info.setter
    def displayed_info(self, new_text):
        self.display.set_text(f"{self.display_text} {new_text}")

    def update_values(self):
        """
        Updates the value list to match the current selected key
        """
        self.values.new_item_list(self.item_dict[self.key_selection[0]])
