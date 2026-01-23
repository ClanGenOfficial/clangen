import pygame
import pygame_gui

from scripts.cat.names import Name
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIImageButton,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale, shorten_text_to_fit
from re import sub


class ChangeCatName(GameWindow):
    """This window allows the user to change the cat's name"""

    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((300, 215), (400, 185))),
            window_display_title="Change Cat Name",
            object_id="#change_cat_name_window",
        )
        self.the_cat = cat

        self.specsuffic_hidden = self.the_cat.name.specsuffix_hidden

        self.heading = pygame_gui.elements.UITextBox(
            "windows.change_name_title",
            ui_scale(pygame.Rect((0, 10), (340, -1))),
            object_id="#text_box_30_horizcenter",
            manager=MANAGER,
            container=self,
            text_kwargs={"name": shorten_text_to_fit(str(self.the_cat.name), 150)},
            anchors={"centerx": "centerx"},
        )

        self.name_changed = pygame_gui.elements.UITextBox(
            "windows.name_changed",
            ui_scale(pygame.Rect((245, 130), (400, 40))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
            container=self,
        )

        self.done_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((161, 145), (77, 30))),
            "buttons.done_lower",
            get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
        )

        x_pos, y_pos = 37, 17

        self.prefix_entry_box = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0 + x_pos, 50 + y_pos), (120, 30))),
            initial_text=self.the_cat.name.prefix,
            manager=MANAGER,
            container=self,
        )

        self.random_prefix = UISurfaceImageButton(
            ui_scale(pygame.Rect((122 + x_pos, 48 + y_pos), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self,
            tool_tip_text="Randomize the prefix",
            sound_id="dice_roll",
        )

        self.random_suffix = UISurfaceImageButton(
            ui_scale(pygame.Rect((281 + x_pos, 48 + y_pos), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self,
            tool_tip_text="Randomize the suffix",
            sound_id="dice_roll",
        )

        self.toggle_spec_block_on = UIImageButton(
            ui_scale(pygame.Rect((202 + x_pos, 80 + y_pos), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            tool_tip_text="windows.remove_spec_block",
            manager=MANAGER,
            container=self,
        )

        self.toggle_spec_block_off = UIImageButton(
            ui_scale(pygame.Rect((202 + x_pos, 80 + y_pos), (34, 34))),
            "",
            object_id="@checked_checkbox",
            tool_tip_text="windows.add_spec_block",
            manager=MANAGER,
            container=self,
        )

        if self.the_cat.status.rank in self.the_cat.name.names_dict["special_suffixes"]:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(
                ui_scale(pygame.Rect((159 + x_pos, 50 + y_pos), (120, 30))),
                placeholder_text=self.the_cat.name.names_dict["special_suffixes"][
                    self.the_cat.status.rank
                ],
                manager=MANAGER,
                container=self,
            )
            if not self.the_cat.name.specsuffix_hidden:
                self.toggle_spec_block_on.show()
                self.toggle_spec_block_on.enable()
                self.toggle_spec_block_off.hide()
                self.toggle_spec_block_off.disable()
                self.random_suffix.disable()
                self.suffix_entry_box.disable()
            else:
                self.toggle_spec_block_on.hide()
                self.toggle_spec_block_on.disable()
                self.toggle_spec_block_off.show()
                self.toggle_spec_block_off.enable()
                self.random_suffix.enable()
                self.suffix_entry_box.enable()
                self.suffix_entry_box.set_text(self.the_cat.name.suffix)

        else:
            self.toggle_spec_block_on.disable()
            self.toggle_spec_block_on.hide()
            self.toggle_spec_block_off.disable()
            self.toggle_spec_block_off.hide()
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(
                ui_scale(pygame.Rect((159 + x_pos, 50 + y_pos), (120, 30))),
                initial_text=self.the_cat.name.suffix,
                manager=MANAGER,
                container=self,
            )
        self.set_blocking(True)

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                old_name = str(self.the_cat.name)

                self.the_cat.specsuffix_hidden = self.specsuffic_hidden
                self.the_cat.name.specsuffix_hidden = self.specsuffic_hidden

                # Note: Prefixes are not allowed be all spaces or empty, but they can have spaces in them.
                if sub(r"[^A-Za-z0-9 ]+", "", self.prefix_entry_box.get_text()) != "":
                    self.the_cat.name.prefix = sub(
                        r"[^A-Za-z0-9 ]+", "", self.prefix_entry_box.get_text()
                    )

                # Suffixes can be empty, if you want. However, don't change the suffix if it's currently being hidden
                # by a special suffix.
                if (
                    self.the_cat.status.rank
                    not in self.the_cat.name.names_dict["special_suffixes"]
                    or self.the_cat.name.specsuffix_hidden
                ):
                    self.the_cat.name.suffix = sub(
                        r"[^A-Za-z0-9 ]+", "", self.suffix_entry_box.get_text()
                    )
                    self.name_changed.show()

                if old_name != str(self.the_cat.name):
                    self.name_changed.show()
                    self.heading.set_text(f"-Change {self.the_cat.name}'s Name-")
                else:
                    self.name_changed.hide()

            elif event.ui_element == self.random_prefix:
                if self.suffix_entry_box.text:
                    use_suffix = self.suffix_entry_box.text
                else:
                    use_suffix = self.the_cat.name.suffix
                self.prefix_entry_box.set_text(
                    Name(None, use_suffix, cat=self.the_cat).prefix
                )
            elif event.ui_element == self.random_suffix:
                if self.prefix_entry_box.text:
                    use_prefix = self.prefix_entry_box.text
                else:
                    use_prefix = self.the_cat.name.prefix
                self.suffix_entry_box.set_text(
                    Name(use_prefix, None, cat=self.the_cat).suffix
                )
            elif event.ui_element == self.toggle_spec_block_on:
                self.specsuffic_hidden = True
                self.suffix_entry_box.enable()
                self.random_suffix.enable()
                self.toggle_spec_block_on.disable()
                self.toggle_spec_block_on.hide()
                self.toggle_spec_block_off.enable()
                self.toggle_spec_block_off.show()
                self.suffix_entry_box.set_text(self.the_cat.name.suffix)
            elif event.ui_element == self.toggle_spec_block_off:
                self.specsuffic_hidden = False
                self.random_suffix.disable()
                self.toggle_spec_block_off.disable()
                self.toggle_spec_block_off.hide()
                self.toggle_spec_block_on.enable()
                self.toggle_spec_block_on.show()
                self.suffix_entry_box.set_text("")
                self.suffix_entry_box.rebuild()
                self.suffix_entry_box.disable()
            elif event.ui_element == self.back_button:
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
        return super().process_event(event)
