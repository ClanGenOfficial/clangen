import pygame
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale, ui_scale_offset, ui_scale_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UICatListDisplay,
)
from scripts.cat.cats import Cat
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon


class RelChangeDetailWindow(GameWindow):
    """
    This window displays given rel logs.
    """

    def __init__(self, rel_logs: dict[Cat, str]):
        super().__init__(ui_scale(pygame.Rect((100, 200), (600, 400))))
        # this needs to be here to prevent a crash
        # don't ask me WHY it crashes, i couldn't figure it out. i think it's a pygui issue.
        # setting this to false has no adverse consequences, it just prevents the crash
        self.bring_to_front_on_focused = False
        self.rel_logs = rel_logs
        self.current_page = 1
        self.window_element = {}

        self.window_element["previous_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 160), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self,
            manager=MANAGER,
        )
        scale_rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
        scale_rect.topright = ui_scale_offset((-20, 160))
        self.window_element["next_page_button"] = UISurfaceImageButton(
            scale_rect,
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            anchors={"top": "top", "right": "right"},
            container=self,
            manager=MANAGER,
        )
        self.update_cats_list()

    def update_cats_list(self):
        """
        Updates the cat list display.
        """

        self.cat_list = UICatListDisplay(
            ui_scale(pygame.Rect((45, 40), (500, 300))),
            container=self,
            manager=MANAGER,
            cat_list=list(self.rel_logs.keys()),
            cats_displayed=12,
            x_px_between=ui_scale_value(5),
            y_px_between=ui_scale_value(10),
            columns=4,
            rows=3,
            show_names=True,
            current_page=self.current_page,
            next_button=self.window_element["next_page_button"],
            prev_button=self.window_element["previous_page_button"],
            text_theme="#text_box_30_horizcenter",
            starting_height=1,
            allow_selection=True,
            tool_tip_text=list(self.rel_logs.values()),
        )

    def kill(self):
        self.cat_list.cache_clear()

        super().kill()
