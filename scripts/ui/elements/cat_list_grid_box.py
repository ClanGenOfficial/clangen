from pygame_gui.core import UIContainer


class UICatListGridBox(UIContainer):
    def __init__(self, relative_rect, anchors, manager):
        super().__init__(
            relative_rect=relative_rect,
            anchors=anchors,
            manager=manager,
        )

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        # this is literally JUST so that the boxes won't block hover detection on lower elements
        return False
