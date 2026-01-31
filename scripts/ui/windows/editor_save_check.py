import pygame
import pygame_gui
import ujson

from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UITextBoxTweaked,
)
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class EditorSaveCheck(GameWindow):
    def __init__(self, path, old_path, editor_save, event_list, old_event_list):
        super().__init__(
            ui_scale(pygame.Rect((200, 200), (400, 200))),
        )
        self.path = path
        self.old_path = old_path
        self.editor_save = editor_save
        self.event_list = event_list
        self.old_event_list = old_event_list
        # adding a variable for starting_height to make sure that this menu is always on top

        self.game_over_message = UITextBoxTweaked(
            "windows.editor_save_check_message",
            ui_scale(pygame.Rect((0, 20), (360, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={"centerx": "centerx"},
        )
        self.path_text = UITextBoxTweaked(
            path,
            ui_scale(pygame.Rect((0, 0), (360, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={"top_target": self.game_over_message, "centerx": "centerx"},
        )

        self.save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 145), (114, 30))),
            "buttons.save",
            get_button_dict(ButtonStyles.SQUOVAL, (114, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="save",
            container=self,
            anchors={"centerx": "centerx"},
        )

    @staticmethod
    def modify_file(event_list, path):
        event_json = ujson.dumps(event_list, indent=4)
        event_json = event_json.replace(
            "\\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        try:
            with open(path, "w", encoding="utf-8") as write_file:
                write_file.write(event_json)
        except:
            print(f"Something went wrong with event writing. Is {path} valid?")

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.save_button:
                if self.old_event_list:
                    self.modify_file(self.old_event_list, self.old_path)
                self.modify_file(self.event_list, self.path)
                self.editor_save.set_text("buttons.clan_saved")
                self.kill()

        return super().process_event(event)
