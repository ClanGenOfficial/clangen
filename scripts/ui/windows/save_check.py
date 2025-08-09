import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.cat.save_load import save_cats
from scripts.game_structure import image_cache
from scripts.game_structure.game.switches import (
    switch_get_value,
    Switch,
    switch_set_value,
)
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UITextBoxTweaked,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale, ui_scale_dimensions


class SaveCheck(GameWindow):
    def __init__(self, last_screen, is_main_menu, mm_btn):
        if game.is_close_menu_open:
            return
        game.is_close_menu_open = True
        super().__init__(
            ui_scale(pygame.Rect((250, 200), (300, 200))),
            window_display_title="Save Check",
            object_id="#save_check_window",
        )

        self.clan_name = "UndefinedClan"
        if game.clan:
            self.clan_name = f"{game.clan.name}Clan"
        self.last_screen = last_screen
        self.isMainMenu = is_main_menu
        self.mm_btn = mm_btn
        # adding a variable for starting_height to make sure that this menu is always on top
        top_stack_menu_layer_height = 10000
        if self.isMainMenu:
            self.mm_btn.disable()
            self.main_menu_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 155), (152, 30))),
                i18n.t("buttons.main_menu_lower"),
                get_button_dict(ButtonStyles.SQUOVAL, (152, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_squoval",
                starting_height=top_stack_menu_layer_height,
                container=self,
                anchors={"centerx": "centerx"},
            )
        else:
            self.main_menu_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 155), (152, 30))),
                "buttons.quit_game",
                get_button_dict(ButtonStyles.SQUOVAL, (152, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_squoval",
                starting_height=top_stack_menu_layer_height,
                container=self,
                anchors={"centerx": "centerx"},
            )
        self.game_over_message = UITextBoxTweaked(
            "windows.save_check_message",
            ui_scale(pygame.Rect((20, 20), (260, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
        )
        save_buttons = get_button_dict(ButtonStyles.SQUOVAL, (114, 30))
        save_buttons["normal"] = pygame.transform.scale(
            image_cache.load_image("resources/images/buttons/save_clan.png"),
            ui_scale_dimensions((114, 30)),
        )

        self.save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 115), (114, 30))),
            "buttons.save_clan",
            save_buttons,
            object_id="@buttonstyles_squoval",
            sound_id="save",
            starting_height=top_stack_menu_layer_height,
            container=self,
            anchors={"centerx": "centerx"},
        )
        self.save_button_saved_state = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 115), (114, 30))),
            "buttons.clan_saved",
            {
                "normal": pygame.transform.scale(
                    image_cache.load_image("resources/images/save_clan_saved.png"),
                    ui_scale_dimensions((114, 30)),
                )
            },
            starting_height=top_stack_menu_layer_height + 2,
            container=self,
            object_id="@buttonstyles_squoval",
            anchors={"centerx": "centerx"},
        )
        self.save_button_saved_state.hide()
        self.save_button_saving_state = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 115), (114, 30))),
            "buttons.saving",
            {"normal": get_button_dict(ButtonStyles.SQUOVAL, (114, 30))["normal"]},
            object_id="@buttonstyles_squoval",
            starting_height=top_stack_menu_layer_height + 1,
            container=self,
            anchors={"centerx": "centerx"},
        )
        self.save_button_saving_state.disable()
        self.save_button_saving_state.hide()

        self.main_menu_button.enable()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu_button:
                if self.isMainMenu:
                    game.is_close_menu_open = False
                    self.mm_btn.enable()
                    game.last_screen_forupdate = switch_get_value(Switch.cur_screen)
                    switch_set_value(Switch.cur_screen, GameScreen.START)
                    game.switch_screens = True
                    self.kill()
                else:
                    game.is_close_menu_open = False
                    quit(savesettings=False, clearevents=False)
            elif event.ui_element == self.save_button:
                if game.clan is not None:
                    self.save_button_saving_state.show()
                    self.save_button.disable()
                    save_cats(switch_get_value(Switch.clan_name), Cat, game)
                    game.clan.save_clan()
                    game.clan.save_pregnancy(game.clan)
                    game.save_events()
                    self.save_button_saving_state.hide()
                    self.save_button_saved_state.show()
            elif event.ui_element == self.back_button:
                game.is_close_menu_open = False
                if self.isMainMenu:
                    self.mm_btn.enable()

                # only allow one instance of this window
        return super().process_event(event)
