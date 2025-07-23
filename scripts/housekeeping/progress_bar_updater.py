from typing import Optional, Union, Dict

import pygame
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIStatusBar

from scripts.game_structure.ui_elements import UITextBoxTweaked


class UIUpdateProgressBar(UIStatusBar):
    status_text: str
    step_count: int
    step_value: float
    step_label: UITextBoxTweaked
    steps_taken: int
    maximum_progress: int
    scaling_factor: float
    display_percent: bool
    unit: str

    def __init__(
        self,
        relative_rect: pygame.Rect,
        step_label: UITextBoxTweaked = None,
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[
            Union[
                ObjectID,
                str,
            ]
        ] = None,
        anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
        visible: int = 1,
    ):
        self.step_label = step_label
        self.maximum_progress = 100
        self.steps_taken = 0
        self.step_value = 0
        self.step_count = 0
        self.scaling_factor = 0
        self.display_percent = True
        self.unit = ""

        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

    def set_steps(
        self,
        step_count: int,
        step_text: str,
        display_percent: bool = True,
        unit: str = "",
        scaling_factor: float = 0,
    ):
        self.step_count = step_count
        self.step_value = 100 / self.step_count / 100
        self.steps_taken = 0
        self.percent_full = 0
        self.display_percent = display_percent
        self.unit = unit
        self.scaling_factor = scaling_factor
        self.step_label.set_text(step_text)

    def status_text(self):
        if self.display_percent:
            return f"{self.percent_full * 100:0.1f}/{100:0.1f}"
        else:
            if self.step_count:
                if self.scaling_factor:
                    current_value = "{:.2f}".format(
                        round(
                            self.maximum_progress
                            / self.step_count
                            * self.steps_taken
                            * self.scaling_factor,
                            2,
                        )
                    )
                    maximum_value = "{:.2f}".format(
                        round(self.maximum_progress * self.scaling_factor, 2)
                    )

                    return f"{current_value}{self.unit} / {maximum_value}{self.unit}"
                else:
                    current_value = round(
                        self.maximum_progress / self.step_count * self.steps_taken, 2
                    )
                    maximum_value = round(self.maximum_progress, 2)

                    return f"{current_value}{self.unit} / {maximum_value}{self.unit}"
            else:
                return ""

    def advance(self):
        self.steps_taken += 1

        if self.steps_taken == self.step_count:
            self.percent_full = 1
        else:
            self.percent_full += self.step_value

        self.update(1)
