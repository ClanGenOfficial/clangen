import pygame
import pygame_gui
from scripts.game_structure import game
from scripts.screens.enums import GameScreen
from scripts.ui.elements.cat_list_display import UICatListDisplay
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked

from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale, ui_scale_offset, ui_scale_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.cat.cats import Cat
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from typing import Union
from scripts.game_structure.game.switches import (
    switch_get_value,
    Switch,
    switch_set_value,
)


class RelChangeDetailWindow(GameWindow):
    """
    This window displays given rel logs.
    """

    def __init__(self, rel_logs: dict[Union[Cat, str], str]):
        super().__init__(ui_scale(pygame.Rect((100, 200), (600, 400))))
        # this needs to be here to prevent a crash
        # don't ask me WHY it crashes, i couldn't figure it out. i think it's a pygui issue.
        # setting this to false has no adverse consequences, it just prevents the crash
        self.bring_to_front_on_focused = False
        self.clan_reaction = None
        self.rel_logs = rel_logs.copy()
        if "clan" in rel_logs:
            self.clan_reaction = self.rel_logs["clan"]
            self.rel_logs.pop("clan")
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

        if self.clan_reaction:
            self.window_element["clan_reaction"] = UITextBoxTweaked(
                self.clan_reaction,
                ui_scale(pygame.Rect((0, 0), (600, 100))),
                object_id="#text_box_30_horizcenter",
                anchors={"top_target": self.window_element["cat_list"]},
                container=self,
            )

    def update_cats_list(self):
        """
        Updates the cat list display.
        """
        if "cat_list" in self.window_element:
            self.window_element["cat_list"].kill()
            self.window_element.pop("cat_list")

        self.window_element["cat_list"] = UICatListDisplay(
            ui_scale(pygame.Rect((50, 20), (500, 300))),
            container=self,
            manager=MANAGER,
            cat_list=list(self.rel_logs.keys()),
            cats_displayed=12,
            x_px_between=ui_scale_value(5),
            y_px_between=ui_scale_value(0),
            columns=4,
            rows=3,
            show_names=True,
            current_page=self.current_page,
            next_button=self.window_element["next_page_button"],
            prev_button=self.window_element["previous_page_button"],
            text_theme="#text_box_30_horizcenter",
            starting_height=1,
            allow_selection=True,
            tool_tip_text_list=list(self.rel_logs.values()),
            custom_sprites_object_id="#rel_log_cat_sprite",
        )

    def kill(self):
        self.window_element["cat_list"].cache_clear()

        super().kill()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.window_element["cat_list"].cat_sprites.values():
                switch_set_value(Switch.cat, event.ui_element.return_cat_id())
                game.last_screen_forupdate = switch_get_value(Switch.cur_screen)
                switch_set_value(Switch.cur_screen, GameScreen.RELATIONSHIP)
                game.switch_screens = True
                self.kill()
            elif event.ui_element == self.window_element["next_page_button"]:
                self.current_page += 1
                self.update_cats_list()
            elif event.ui_element == self.window_element["previous_page_button"]:
                self.current_page -= 1
                self.update_cats_list()

        super().process_event(event)
