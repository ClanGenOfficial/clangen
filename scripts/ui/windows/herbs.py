from random import choice

import i18n
import pygame
import pygame_gui.elements

from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.game_structure import game
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.game_structure.game.switches import (
    switch_get_value,
    Switch,
    switch_set_value,
)
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIImageButton,
    UITextBoxTweaked,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale, ui_scale_offset


class HerbManagementWindow(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((125, 150), (550, 400))),
            window_display_title="Herb Management",
        )

        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((18, 18), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="windows.herb_help_tooltip",
            container=self,
        )
        self.meds = find_alive_cats_with_rank(
            Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
        )
        if self.meds:
            log_text = [game.clan.herb_supply.get_status_message(choice(self.meds))]
        else:
            log_text = []

        if not game.herb_events_list:
            log_text.append(i18n.t("windows.log_empty"))
        else:
            log_text.extend(game.herb_events_list.copy())

        self.log = UITextBoxTweaked(
            f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
            ui_scale(pygame.Rect((25, 25), (500, 250))),
            object_id="#text_box_26_horizleft_verttop_pad_14_0_10",
            manager=MANAGER,
            container=self,
            anchors={"top_target": self.help_button},
        )

        scale_rect = ui_scale(pygame.Rect((0, 0), (151, 28)))
        scale_rect.bottomleft = ui_scale_offset((0, -25))
        self.med_den_button = UISurfaceImageButton(
            scale_rect,
            "screens.core.medicine_cat_den",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (151, 28)),
            object_id="@buttonstyles_rounded_rect",
            manager=MANAGER,
            starting_height=2,
            container=self,
            anchors={"bottom": "bottom", "centerx": "centerx"},
        )

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # NAVIGATION
            if event.ui_element == self.med_den_button:
                game.last_screen_forupdate = switch_get_value(Switch.cur_screen)
                switch_set_value(Switch.cur_screen, GameScreen.MED_DEN)
                game.switch_screens = True
                self.kill()

        return super().process_event(event)
