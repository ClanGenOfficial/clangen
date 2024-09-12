import os
import shutil
import subprocess
import threading
import time
from platform import system
from random import choice
from re import search as re_search
from re import sub

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow

from scripts.cat.history import History
from scripts.cat.names import Name
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import UIImageButton, UITextBoxTweaked
from scripts.housekeeping.datadir import (
    get_save_dir,
    get_cache_dir,
    get_saved_images_dir,
    get_data_dir,
)
from scripts.housekeeping.progress_bar_updater import UIUpdateProgressBar
from scripts.housekeeping.update import (
    self_update,
    UpdateChannel,
    get_latest_version_number,
)
from scripts.housekeeping.version import get_version_info
from scripts.utility import (
    scale,
    quit,
    update_sprite,
    scale_dimentions,
    logger,
    process_text,
)


class SymbolFilterWindow(UIWindow):
    def __init__(self):

        super().__init__(
            scale(pygame.Rect((500, 350), (600, 700))),
            window_display_title="Symbol Filters",
            object_id="#filter_window",
        )
        game.switches["window_open"] = True
        self.set_blocking(True)

        self.possible_tags = {
            "plant": ["flower", "tree"],
            "animal": ["cat", "fish", "bird", "mammal", "bug", "other animals"],
            "element": ["water", "fire", "earth", "air", "light"],
            "location": [],
            "descriptor": [],
            "miscellaneous": [],
        }

        self.back_button = UIImageButton(
            scale(pygame.Rect((540, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            starting_height=10,
            container=self,
        )
        self.filter_title = pygame_gui.elements.UILabel(
            scale(pygame.Rect((10, 10), (-1, -1))),
            text="Show Symbols With:",
            object_id="#text_box_40",
            container=self,
        )
        self.filter_container = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((10, 70), (570, 620))),
            manager=MANAGER,
            starting_height=1,
            object_id="#filter_container",
            allow_scroll_x=False,
            container=self,
        )
        self.checkbox = {}
        self.checkbox_text = {}
        x_pos = 30
        y_pos = 40
        for tag, subtags in self.possible_tags.items():
            print(game.switches["disallowed_symbol_tags"])
            self.checkbox[tag] = UIImageButton(
                scale(pygame.Rect((x_pos, y_pos), (68, 68))),
                "",
                object_id="#checked_checkbox",
                container=self.filter_container,
                starting_height=2,
                manager=MANAGER,
            )
            if tag in game.switches["disallowed_symbol_tags"]:
                self.checkbox[tag].change_object_id("#unchecked_checkbox")

            self.checkbox_text[tag] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((x_pos + 80, y_pos + 6), (-1, -1))),
                text=str(tag),
                container=self.filter_container,
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
            )
            y_pos += 70
            if subtags:
                for s_tag in subtags:
                    self.checkbox[s_tag] = UIImageButton(
                        scale(pygame.Rect((x_pos + 70, y_pos), (68, 68))),
                        "",
                        object_id="#checked_checkbox",
                        container=self.filter_container,
                        starting_height=2,
                        manager=MANAGER,
                    )

                    if tag in game.switches["disallowed_symbol_tags"]:
                        self.checkbox[s_tag].disable()
                    if s_tag in game.switches["disallowed_symbol_tags"]:
                        self.checkbox[s_tag].change_object_id("#unchecked_checkbox")

                    self.checkbox_text[s_tag] = pygame_gui.elements.UILabel(
                        scale(pygame.Rect((x_pos + 150, y_pos + 6), (-1, -1))),
                        text=s_tag,
                        container=self.filter_container,
                        object_id="#text_box_30_horizleft",
                        manager=MANAGER,
                    )
                    y_pos += 60
                y_pos += 10

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.switches["window_open"] = False
                self.kill()

            elif event.ui_element in self.checkbox.values():
                for tag, element in self.checkbox.items():
                    if element == event.ui_element:
                        # find out what state the checkbox was in when clicked
                        object_ids = element.get_object_ids()
                        # handle checked checkboxes becoming unchecked
                        if "#checked_checkbox" in object_ids:
                            self.checkbox[tag].change_object_id("#unchecked_checkbox")
                            # add tag to disallowed list
                            if tag not in game.switches["disallowed_symbol_tags"]:
                                game.switches["disallowed_symbol_tags"].append(tag)
                            # if tag had subtags, also add those subtags
                            if tag in self.possible_tags:
                                for s_tag in self.possible_tags[tag]:
                                    self.checkbox[s_tag].change_object_id(
                                        "#unchecked_checkbox"
                                    )
                                    self.checkbox[s_tag].disable()
                                    if s_tag not in game.switches["disallowed_symbol_tags"]:
                                        game.switches["disallowed_symbol_tags"].append(
                                            s_tag
                                        )

                        # handle unchecked checkboxes becoming checked
                        elif "#unchecked_checkbox" in object_ids:
                            self.checkbox[tag].change_object_id("#checked_checkbox")
                            # remove tag from disallowed list
                            if tag in game.switches["disallowed_symbol_tags"]:
                                game.switches["disallowed_symbol_tags"].remove(tag)
                            # if tag had subtags, also add those subtags
                            if tag in self.possible_tags:
                                for s_tag in self.possible_tags[tag]:
                                    self.checkbox[s_tag].change_object_id(
                                        "#checked_checkbox"
                                    )
                                    self.checkbox[s_tag].enable()
                                    if s_tag in game.switches["disallowed_symbol_tags"]:
                                        game.switches["disallowed_symbol_tags"].remove(
                                            s_tag
                                        )


class SaveCheck(UIWindow):
    def __init__(self, last_screen, isMainMenu, mm_btn):
        game.switches["window_open"] = True
        if game.is_close_menu_open:
            return
        game.is_close_menu_open = True
        super().__init__(
            scale(pygame.Rect((500, 400), (600, 400))),
            window_display_title="Save Check",
            object_id="#save_check_window",
            resizable=False,
            always_on_top=True,
        )

        self.clan_name = "UndefinedClan"
        if game.clan:
            self.clan_name = f"{game.clan.name}Clan"
        self.last_screen = last_screen
        self.isMainMenu = isMainMenu
        self.mm_btn = mm_btn
        # adding a variable for starting_height to make sure that this menu is always on top
        top_stack_menu_layer_height = 10000
        if self.isMainMenu:
            self.mm_btn.disable()
            self.main_menu_button = UIImageButton(
                scale(pygame.Rect((146, 310), (305, 60))),
                "",
                object_id="#main_menu_button",
                starting_height=top_stack_menu_layer_height,
                container=self,
            )
            self.message = f"Would you like to save your game before exiting to the Main Menu? If you don't, progress may be lost!"
        else:
            self.main_menu_button = UIImageButton(
                scale(pygame.Rect((146, 310), (305, 60))),
                "",
                object_id="#smallquit_button",
                starting_height=top_stack_menu_layer_height,
                container=self,
            )
            self.message = f"Would you like to save your game before exiting? If you don't, progress may be lost!"

        self.game_over_message = UITextBoxTweaked(
            self.message,
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
        )

        self.save_button = UIImageButton(
            scale(pygame.Rect((186, 230), (228, 60))),
            "",
            object_id="#save_button",
            starting_height=top_stack_menu_layer_height,
            container=self,
        )
        self.save_button_saved_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((186, 230), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/save_clan_saved.png"),
                (228, 60),
            ),
            starting_height=top_stack_menu_layer_height + 2,
            container=self,
        )
        self.save_button_saved_state.hide()
        self.save_button_saving_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((186, 230), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/save_clan_saving.png"),
                (228, 60),
            ),
            starting_height=top_stack_menu_layer_height + 1,
            container=self,
        )
        self.save_button_saving_state.hide()

        self.back_button = UIImageButton(
            scale(pygame.Rect((540, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            starting_height=top_stack_menu_layer_height,
            container=self,
        )

        self.back_button.enable()
        self.main_menu_button.enable()
        self.set_blocking(True)

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu_button:
                if self.isMainMenu:
                    game.is_close_menu_open = False
                    self.mm_btn.enable()
                    game.last_screen_forupdate = game.switches["cur_screen"]
                    game.switches["cur_screen"] = "start screen"
                    game.switch_screens = True
                    self.kill()
                    game.switches["window_open"] = False
                else:
                    game.is_close_menu_open = False
                    quit(savesettings=False, clearevents=False)
            elif event.ui_element == self.save_button:
                if game.clan is not None:
                    self.save_button_saving_state.show()
                    self.save_button.disable()
                    game.save_cats()
                    game.clan.save_clan()
                    game.clan.save_pregnancy(game.clan)
                    game.save_events()
                    self.save_button_saving_state.hide()
                    self.save_button_saved_state.show()
            elif event.ui_element == self.back_button:
                game.is_close_menu_open = False
                game.switches["window_open"] = False
                self.kill()
                if self.isMainMenu:
                    self.mm_btn.enable()

                # only allow one instance of this window


class DeleteCheck(UIWindow):
    def __init__(self, reloadscreen, clan_name):
        super().__init__(
            scale(pygame.Rect((500, 400), (600, 360))),
            window_display_title="Delete Check",
            object_id="#delete_check_window",
            resizable=False,
        )
        self.set_blocking(True)
        game.switches["window_open"] = True
        self.clan_name = clan_name
        self.reloadscreen = reloadscreen

        self.delete_check_message = UITextBoxTweaked(
            f"Do you wish to delete {str(self.clan_name + 'Clan')}? This is permanent and cannot be undone.",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
        )

        self.delete_it_button = UIImageButton(
            scale(pygame.Rect((142, 200), (306, 60))),
            "delete",
            object_id="#delete_it_button",
            container=self,
        )
        self.go_back_button = UIImageButton(
            scale(pygame.Rect((142, 270), (306, 60))),
            "go back",
            object_id="#go_back_button",
            container=self,
        )

        self.back_button = UIImageButton(
            scale(pygame.Rect((540, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )

        self.back_button.enable()

        self.go_back_button.enable()
        self.delete_it_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.delete_it_button:
                game.switches['window_open'] = False
                rempath = get_save_dir() + "/" + self.clan_name
                shutil.rmtree(rempath)
                if os.path.exists(rempath + "clan.json"):
                    os.remove(rempath + "clan.json")
                elif os.path.exists(rempath + "clan.txt"):
                    os.remove(rempath + "clan.txt")
                else:
                    print("No clan.json/txt???? Clan prolly wasnt initalized kekw")
                self.kill()
                self.reloadscreen("switch clan screen")

            elif event.ui_element == self.go_back_button:
                game.switches["window_open"] = False
                self.kill()
            elif event.ui_element == self.back_button:
                game.switches["window_open"] = False
                game.is_close_menu_open = False
                self.kill()


class GameOver(UIWindow):
    def __init__(self, last_screen):
        super().__init__(
            scale(pygame.Rect((500, 400), (600, 360))),
            window_display_title="Game Over",
            object_id="#game_over_window",
            resizable=False,
        )
        self.set_blocking(True)
        game.switches["window_open"] = True
        self.clan_name = str(game.clan.name + "Clan")
        self.last_screen = last_screen
        self.game_over_message = UITextBoxTweaked(
            f"{self.clan_name} has died out. For now, this is where their story ends. Perhaps it's time to tell a new "
            f"tale?",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="",
            container=self,
        )

        self.game_over_message = UITextBoxTweaked(
            f"(leaving will not erase the save file)",
            scale(pygame.Rect((40, 310), (520, -1))),
            line_spacing=0.8,
            object_id="#text_box_22_horizcenter",
            container=self,
        )

        self.begin_anew_button = UIImageButton(
            scale(pygame.Rect((50, 230), (222, 60))),
            "",
            object_id="#begin_anew_button",
            container=self,
        )
        self.not_yet_button = UIImageButton(
            scale(pygame.Rect((318, 230), (222, 60))),
            "",
            object_id="#not_yet_button",
            container=self,
        )

        self.not_yet_button.enable()
        self.begin_anew_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.begin_anew_button:
                game.last_screen_forupdate = game.switches["cur_screen"]
                game.switches["cur_screen"] = "start screen"
                game.switch_screens = True
                game.switches["window_open"] = False
                self.kill()
            elif event.ui_element == self.not_yet_button:
                game.switches["window_open"] = False
                self.kill()


class ChangeCatName(UIWindow):
    """This window allows the user to change the cat's name"""

    def __init__(self, cat):
        super().__init__(
            scale(pygame.Rect((600, 430), (800, 370))),
            window_display_title="Change Cat Name",
            object_id="#change_cat_name_window",
            resizable=False,
        )
        game.switches["window_open"] = True
        self.the_cat = cat
        self.back_button = UIImageButton(
            scale(pygame.Rect((740, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )

        self.specsuffic_hidden = self.the_cat.name.specsuffix_hidden

        self.heading = pygame_gui.elements.UITextBox(
            f"-Change {self.the_cat.name}'s Name-",
            scale(pygame.Rect((0, 20), (800, 80))),
            object_id="#text_box_30_horizcenter",
            manager=MANAGER,
            container=self,
        )

        self.name_changed = pygame_gui.elements.UITextBox(
            "Name Changed!",
            scale(pygame.Rect((490, 260), (800, 80))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
            container=self,
        )

        self.done_button = UIImageButton(
            scale(pygame.Rect((323, 270), (154, 60))),
            "",
            object_id="#done_button",
            manager=MANAGER,
            container=self,
        )

        x_pos, y_pos = 75, 35

        self.prefix_entry_box = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((0 + x_pos, 100 + y_pos), (240, 60))),
            initial_text=self.the_cat.name.prefix,
            manager=MANAGER,
            container=self,
        )

        self.random_prefix = UIImageButton(
            scale(pygame.Rect((245 + x_pos, 97 + y_pos), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
            container=self,
            tool_tip_text="Randomize the prefix",
            sound_id="dice_roll",
        )

        self.random_suffix = UIImageButton(
            scale(pygame.Rect((563 + x_pos, 97 + y_pos), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
            container=self,
            tool_tip_text="Randomize the suffix",
            sound_id="dice_roll",
        )

        # 636
        self.toggle_spec_block_on = UIImageButton(
            scale(pygame.Rect((405 + x_pos, 160 + y_pos), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            tool_tip_text=f"Remove the cat's special suffix",
            manager=MANAGER,
            container=self,
        )

        self.toggle_spec_block_off = UIImageButton(
            scale(pygame.Rect((405 + x_pos, 160 + y_pos), (68, 68))),
            "",
            object_id="#checked_checkbox",
            tool_tip_text="Re-enable the cat's special suffix",
            manager=MANAGER,
            container=self,
        )

        if self.the_cat.name.status in self.the_cat.name.names_dict["special_suffixes"]:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(
                scale(pygame.Rect((318 + x_pos, 100 + y_pos), (240, 60))),
                placeholder_text=self.the_cat.name.names_dict["special_suffixes"][
                    self.the_cat.name.status
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
                scale(pygame.Rect((318 + x_pos, 100 + y_pos), (240, 60))),
                initial_text=self.the_cat.name.suffix,
                manager=MANAGER,
                container=self,
            )
        self.set_blocking(True)

    def process_event(self, event):
        super().process_event(event)

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
                    self.the_cat.name.status
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
                    Name(
                        self.the_cat.status,
                        None,
                        use_suffix,
                        self.the_cat.pelt.colour,
                        self.the_cat.pelt.eye_colour,
                        self.the_cat.pelt.name,
                        self.the_cat.pelt.tortiepattern,
                    ).prefix
                )
            elif event.ui_element == self.random_suffix:
                if self.prefix_entry_box.text:
                    use_prefix = self.prefix_entry_box.text
                else:
                    use_prefix = self.the_cat.name.prefix
                self.suffix_entry_box.set_text(
                    Name(
                        self.the_cat.status,
                        use_prefix,
                        None,
                        self.the_cat.pelt.colour,
                        self.the_cat.pelt.eye_colour,
                        self.the_cat.pelt.name,
                        self.the_cat.pelt.tortiepattern,
                    ).suffix
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
                game.switches["window_open"] = False
                game.all_screens["profile screen"].exit_screen()
                game.all_screens["profile screen"].screen_switches()
                self.kill()


class PronounCreation(UIWindow):
    # This window allows the user to create a pronoun set

    def __init__(self, cat):
        super().__init__(
            scale(pygame.Rect((160, 300), (1300, 800))),
            window_display_title="Create Cat Pronouns",
            object_id="#change_cat_gender_window",
            resizable=False,
        )
        game.switches["window_open"] = True
        self.the_cat = cat
        self.conju = 1
        self.box_labels = {}
        self.elements = {}
        self.boxes = {}
        self.checkbox_label = {}
        Demo_frame = "resources/images/demo_frame.png"
        self.back_button = UIImageButton(
            scale(pygame.Rect((1230, 20), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )
        self.heading = pygame_gui.elements.UITextBox(
            f"Create new pronouns,"
            f" you have full control. "
            f"<br> Test your created pronouns before saving them!",
            scale(pygame.Rect((30, 120), (760, 150))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        # Create a sub-container for the Demo frame and sample text
        demo_container_rect = scale(pygame.Rect((795, 115), (851, 1184)))
        self.demo_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=demo_container_rect, manager=MANAGER, container=self
        )

        # Add the Demo frame to the sub-container
        self.elements["demo_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (414, 576))),
            pygame.transform.scale(
                pygame.image.load(Demo_frame).convert_alpha(), (699, 520)
            ),
            manager=MANAGER,
            container=self.demo_container,
        )
        # Tittle of Demo Box
        self.elements["demo title"] = pygame_gui.elements.UITextBox(
            "<b>Demo",
            scale(pygame.Rect((150, 30), (450, 65))),
            object_id="#text_box_34_horizleft",
            manager=MANAGER,
            container=self.demo_container,
        )

        # Add UITextBox for the sample text to the sub-container
        self.sample_text_box = pygame_gui.elements.UITextBox(
            self.get_sample_text(self.the_cat.pronouns[0]),
            scale(pygame.Rect((18, 120), (394, 556))),
            object_id="#text_box_30_horizcenter",
            manager=MANAGER,
            container=self.demo_container,
        )
        # Tittle
        self.elements["Pronoun Creation"] = pygame_gui.elements.UITextBox(
            "Pronoun Creation",
            scale(pygame.Rect((200, 30), (450, 65))),
            object_id="#text_box_40_horizcenter",
            manager=MANAGER,
            container=self,
        )

        # Adjusted positions for labels
        self.box_labels["subject"] = pygame_gui.elements.UITextBox(
            "Subject",
            scale(pygame.Rect((175, 230), (200, 60))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        self.box_labels["object"] = pygame_gui.elements.UITextBox(
            "Object",
            scale(pygame.Rect((425, 230), (200, 60))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        self.box_labels["poss"] = pygame_gui.elements.UITextBox(
            "Possessive",
            scale(pygame.Rect((50, 410), (200, 60))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        self.box_labels["inposs"] = pygame_gui.elements.UITextBox(
            "Independent<br>Possessive",
            scale(pygame.Rect((250, 370), (300, 120))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        self.box_labels["self"] = pygame_gui.elements.UITextBox(
            "Reflexive",
            scale(pygame.Rect((550, 410), (200, 60))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )
        self.checkbox_label["singular_label"] = pygame_gui.elements.UITextBox(
            "Singular",
            scale(pygame.Rect((255, 570), (200, 60))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )
        self.checkbox_label["plural_label"] = pygame_gui.elements.UITextBox(
            "Plural",
            scale(pygame.Rect((470, 570), (200, 60))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        # Row 1
        self.boxes["subject"] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((180, 290), (200, 60))),
            placeholder_text=self.the_cat.pronouns[0]["subject"],
            manager=MANAGER,
            container=self,
        )

        self.boxes["object"] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((430, 290), (200, 60))),
            placeholder_text=self.the_cat.pronouns[0]["object"],
            manager=MANAGER,
            container=self,
        )

        # Row 2
        self.boxes["poss"] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((50, 470), (200, 60))),
            placeholder_text=self.the_cat.pronouns[0]["poss"],
            manager=MANAGER,
            container=self,
        )

        self.boxes["inposs"] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((300, 470), (200, 60))),
            placeholder_text=self.the_cat.pronouns[0]["inposs"],
            manager=MANAGER,
            container=self,
        )

        self.boxes["self"] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((550, 470), (200, 60))),
            placeholder_text=self.the_cat.pronouns[0]["self"],
            manager=MANAGER,
            container=self,
        )

        # Save Confirmation
        self.pronoun_added = pygame_gui.elements.UITextBox(
            f"Pronoun saved and added to presets!",
            scale(pygame.Rect((550, 700), (800, 80))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
            container=self,
        )

        # Add buttons
        self.buttons = {}
        self.buttons["save_pronouns"] = UIImageButton(
            scale(pygame.Rect((350, 670), (146, 60))),
            "",
            manager=MANAGER,
            object_id="#save_button_pronoun",
            container=self,
        )
        # Creating Checkmarks
        self.buttons["singular_unchecked"] = UIImageButton(
            scale(pygame.Rect((225, 570), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            starting_height=2,
            visible=False,
            manager=MANAGER,
            container=self,
        )
        self.buttons["singular_checked"] = UIImageButton(
            scale(pygame.Rect((225, 570), (68, 68))),
            "",
            object_id="#checked_checkbox",
            starting_height=2,
            visible=False,
            manager=MANAGER,
            container=self,
        )

        self.buttons["plural_unchecked"] = UIImageButton(
            scale(pygame.Rect((455, 570), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            starting_height=2,
            visible=False,
            manager=MANAGER,
            container=self,
        )
        self.buttons["plural_checked"] = UIImageButton(
            scale(pygame.Rect((455, 570), (68, 68))),
            "",
            object_id="#checked_checkbox",
            starting_height=2,
            visible=False,
            manager=MANAGER,
            container=self,
        )
        if self.the_cat.pronouns[0]["conju"] == 1:
            # self.buttons["plural"].disable()
            self.buttons["plural_checked"].show()
            self.buttons["singular_unchecked"].show()
        else:
            self.buttons["plural_unchecked"].show()
            self.buttons["singular_checked"].show()
            self.conju = 2

        self.buttons["test_set"] = UIImageButton(
            scale(pygame.Rect((120, 475), (208, 60))),
            "",
            object_id="#test_set_button",
            starting_height=2,
            manager=MANAGER,
            container=self.demo_container,
        )

        self.set_blocking(True)

    def get_new_pronouns(self):
        pronoun_template = {
            "name": "",
            "subject": "",
            "object": "",
            "poss": "",
            "inposs": "",
            "self": "",
            "conju": 1,
        }

        if sub(r"[^A-Za-z0-9 ]+", "", self.boxes["subject"].get_text()) != "":
            pronoun_template["subject"] = sub(
                r"[^A-Za-z0-9 ]+", "", self.boxes["subject"].get_text()
            )
        if sub(r"[^A-Za-z0-9 ]+", "", self.boxes["object"].get_text()) != "":
            pronoun_template["object"] = sub(
                r"[^A-Za-z0-9 ]+", "", self.boxes["object"].get_text()
            )
        if sub(r"[^A-Za-z0-9 ]+", "", self.boxes["poss"].get_text()) != "":
            pronoun_template["poss"] = sub(
                r"[^A-Za-z0-9 ]+", "", self.boxes["poss"].get_text()
            )
        if sub(r"[^A-Za-z0-9 ]+", "", self.boxes["inposs"].get_text()) != "":
            pronoun_template["inposs"] = sub(
                r"[^A-Za-z0-9 ]+", "", self.boxes["inposs"].get_text()
            )
        if sub(r"[^A-Za-z0-9 ]+", "", self.boxes["self"].get_text()) != "":
            pronoun_template["self"] = sub(
                r"[^A-Za-z0-9 ]+", "", self.boxes["self"].get_text()
            )
        if self.conju == 2:
            pronoun_template["conju"] = 2
        # if save button or add to cat is pressed, set 'name' as a counting number thing as an invisible identifier
        newid = len(game.clan.custom_pronouns) + 1
        pronoun_template["ID"] = "custom" + str(newid)
        return pronoun_template

    def is_box_full(self, entry):
        if entry.get_text() == "":
            return False
        else:
            return True

    def are_boxes_full(self):
        values = []
        values.append(self.is_box_full(self.boxes["subject"]))
        values.append(self.is_box_full(self.boxes["object"]))
        values.append(self.is_box_full(self.boxes["poss"]))
        values.append(self.is_box_full(self.boxes["inposs"]))
        values.append(self.is_box_full(self.boxes["self"]))
        for value in values:
            if value is False:
                return False
        return True

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.switches["window_open"] = False
                game.all_screens["change gender screen"].exit_screen()
                game.all_screens["change gender screen"].screen_switches()
                self.kill()
            elif event.ui_element == self.buttons["save_pronouns"]:
                if self.are_boxes_full():
                    new_pronouns = self.get_new_pronouns()
                    game.clan.custom_pronouns.append(new_pronouns)
                    self.pronoun_added.show()
            elif event.ui_element == self.buttons["singular_unchecked"]:
                self.buttons["plural_checked"].hide()
                self.buttons["singular_unchecked"].hide()
                self.buttons["plural_unchecked"].show()
                self.buttons["singular_checked"].show()
                self.conju = 2
            elif event.ui_element == self.buttons["plural_unchecked"]:
                """self.buttons["plural"].enable()"""
                self.buttons["plural_checked"].show()
                self.buttons["singular_unchecked"].show()
                self.buttons["plural_unchecked"].hide()
                self.buttons["singular_checked"].hide()
                self.conju = 1
            elif event.ui_element == self.buttons["test_set"]:
                self.sample_text_box.kill()
                self.sample_text_box = pygame_gui.elements.UITextBox(
                    self.get_sample_text(self.get_new_pronouns()),
                    scale(pygame.Rect((15, 120), (394, 556))),
                    object_id="#text_box_30_horizcenter_spacing_95",
                    manager=MANAGER,
                    container=self.demo_container,
                )

    def get_sample_text(self, pronouns):
        text = ""
        subject = f"{pronouns['subject']} are quick. <br>"
        if pronouns["conju"] == 2:
            subject = f"{pronouns['subject']} is quick. <br>"
        text += subject.capitalize()
        text += f"Everyone saw {pronouns['object']}. <br>"
        poss = f"{pronouns['poss']} paw slipped.<br>"
        text += poss.capitalize()
        text += f"That den is {pronouns['inposs']}. <br>"
        text += f"This cat hunts by {pronouns['self']}.<br>"
        # Full Sentence Example, doesn't fit.
        """sentence = f"{pronouns['poss']} keen sense alerted {pronouns['object']} to prey and {pronouns['subject']} decided to treat {pronouns['self']} by catching prey that would be {pronouns['inposs']} alone to eat. "
        if pronouns["conju"] == 2:
            sentence = f"{pronouns['poss']} keen sense alerted {pronouns['object']} to prey and {pronouns['subject']} decides to treat {pronouns['self']} by catching prey that would be {pronouns['inposs']} alone to eat. "
        text += sentence.capitalize()"""
        # print (len(game.clan.custom_pronouns)+1)
        return text


class KillCat(UIWindow):
    """This window allows the user to specify the cat's gender"""

    def __init__(self, cat):
        super().__init__(
            scale(pygame.Rect((600, 400), (900, 400))),
            window_display_title="Kill Cat",
            object_id="#change_cat_gender_window",
            resizable=False,
        )
        self.history = History()
        game.switches["window_open"] = True
        self.the_cat = cat
        self.take_all = False
        cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
        self.back_button = UIImageButton(
            scale(pygame.Rect((840, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )
        cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
        self.heading = pygame_gui.elements.UITextBox(
            f"<b>-- How did this cat die? --</b>",
            scale(pygame.Rect((20, 20), (860, 150))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
        )

        self.one_life_check = UIImageButton(
            scale(pygame.Rect((50, 300), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            tool_tip_text=process_text(
                "If this is checked, the leader will lose all {PRONOUN/m_c/poss} lives",
                cat_dict,
            ),
            manager=MANAGER,
            container=self,
        )
        self.all_lives_check = UIImageButton(
            scale(pygame.Rect((50, 300), (68, 68))),
            "",
            object_id="#checked_checkbox",
            tool_tip_text=process_text(
                "If this is checked, the leader will lose all {PRONOUN/m_c/poss} lives",
                cat_dict,
            ),
            manager=MANAGER,
            container=self,
        )

        if self.the_cat.status == "leader":
            self.done_button = UIImageButton(
                scale(pygame.Rect((695, 305), (154, 60))),
                "",
                object_id="#done_button",
                manager=MANAGER,
                container=self,
            )

            self.prompt = process_text(
                "This cat died when {PRONOUN/m_c/subject}...", cat_dict
            )
            self.initial = process_text(
                "{VERB/m_c/were/was} killed by a higher power.", cat_dict
            )

            self.all_lives_check.hide()
            self.life_text = pygame_gui.elements.UITextBox(
                "Take all the leader's lives",
                scale(pygame.Rect((120, 295), (900, 80))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
            self.beginning_prompt = pygame_gui.elements.UITextBox(
                self.prompt,
                scale(pygame.Rect((50, 60), (900, 80))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(
                scale(pygame.Rect((50, 130), (800, 150))),
                initial_text=self.initial,
                object_id="text_entry_line",
                manager=MANAGER,
                container=self,
            )

        elif History.get_death_or_scars(self.the_cat, death=True):
            # This should only occur for retired leaders.

            self.prompt = process_text(
                "This cat died when {PRONOUN/m_c/subject}...", cat_dict
            )
            self.initial = process_text(
                "{VERB/m_c/were/was} killed by something unknowable to even StarClan",
                cat_dict,
            )
            self.all_lives_check.hide()
            self.one_life_check.hide()

            self.beginning_prompt = pygame_gui.elements.UITextBox(
                self.prompt,
                scale(pygame.Rect((50, 60), (900, 80))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(
                scale(pygame.Rect((50, 130), (800, 150))),
                initial_text=self.initial,
                object_id="text_entry_line",
                manager=MANAGER,
                container=self,
            )

            self.done_button = UIImageButton(
                scale(pygame.Rect((373, 305), (154, 60))),
                "",
                object_id="#done_button",
                manager=MANAGER,
                container=self,
            )
        else:
            self.initial = "This cat was killed by a higher power."
            self.prompt = None
            self.all_lives_check.hide()
            self.one_life_check.hide()

            self.death_entry_box = pygame_gui.elements.UITextEntryBox(
                scale(pygame.Rect((50, 110), (800, 150))),
                initial_text=self.initial,
                object_id="text_entry_line",
                manager=MANAGER,
                container=self,
            )

            self.done_button = UIImageButton(
                scale(pygame.Rect((373, 305), (154, 60))),
                "",
                object_id="#done_button",
                manager=MANAGER,
                container=self,
            )
        self.set_blocking(True)

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                death_message = sub(
                    r"[^A-Za-z0-9<->/.()*'&#!?,| _]+",
                    "",
                    self.death_entry_box.get_text(),
                )
                if self.the_cat.status == "leader":

                    if death_message.startswith("was"):
                        death_message = death_message.replace(
                            "was", "{VERB/m_c/were/was}", 1
                        )
                    elif death_message.startswith("were"):
                        death_message = death_message.replace(
                            "were", "{VERB/m_c/were/was}", 1
                        )

                    if self.take_all:
                        game.clan.leader_lives = 0
                    else:
                        game.clan.leader_lives -= 1

                self.the_cat.die()
                self.history.add_death(self.the_cat, death_message)
                update_sprite(self.the_cat)
                game.switches["window_open"] = False
                game.all_screens["profile screen"].exit_screen()
                game.all_screens["profile screen"].screen_switches()
                self.kill()
            elif event.ui_element == self.all_lives_check:
                self.take_all = False
                self.all_lives_check.hide()
                self.one_life_check.show()
            elif event.ui_element == self.one_life_check:
                self.take_all = True
                self.all_lives_check.show()
                self.one_life_check.hide()
            elif event.ui_element == self.back_button:
                game.switches["window_open"] = False
                game.all_screens["profile screen"].exit_screen()
                game.all_screens["profile screen"].screen_switches()
                self.kill()


class UpdateWindow(UIWindow):
    def __init__(self, last_screen, announce_restart_callback):
        super().__init__(
            scale(pygame.Rect((500, 400), (600, 320))),
            window_display_title="Game Over",
            object_id="#game_over_window",
            resizable=False,
        )
        self.set_blocking(True)
        self.last_screen = last_screen
        self.update_message = pygame_gui.elements.UITextBox(
            f"Update in progress.",
            scale(pygame.Rect((40, 20), (520, -1))),
            object_id="#text_box_30_horizcenter_spacing_95",
            starting_height=4,
            container=self,
        )
        self.announce_restart_callback = announce_restart_callback

        self.step_text = UITextBoxTweaked(
            f"Downloading update...",
            scale(pygame.Rect((40, 80), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
        )

        self.progress_bar = UIUpdateProgressBar(
            scale(pygame.Rect((40, 130), (520, 70))),
            self.step_text,
            object_id="progress_bar",
            container=self,
        )

        self.update_thread = threading.Thread(
            target=self_update,
            daemon=True,
            args=(
                UpdateChannel(get_version_info().release_channel),
                self.progress_bar,
                announce_restart_callback,
            ),
        )
        self.update_thread.start()

        self.cancel_button = UIImageButton(
            scale(pygame.Rect((400, 230), (156, 60))),
            "",
            object_id="#cancel_button",
            container=self,
        )

        self.cancel_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.cancel_button:
                self.kill()


class AnnounceRestart(UIWindow):
    def __init__(self, last_screen):
        super().__init__(
            scale(pygame.Rect((500, 400), (600, 180))),
            window_display_title="Game Over",
            object_id="#game_over_window",
            resizable=False,
        )
        self.last_screen = last_screen
        self.announce_message = UITextBoxTweaked(
            f"The game will automatically restart in 3...",
            scale(pygame.Rect((40, 40), (520, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
        )

        threading.Thread(target=self.update_text, daemon=True).start()

    def update_text(self):
        for i in range(2, 0, -1):
            time.sleep(1)
            self.announce_message.set_text(
                f"The game will automatically restart in {i}..."
            )


class UpdateAvailablePopup(UIWindow):
    def __init__(self, last_screen, show_checkbox: bool = False):
        super().__init__(
            scale(pygame.Rect((400, 400), (800, 460))),
            window_display_title="Update available",
            object_id="#game_over_window",
            resizable=False,
        )
        self.set_blocking(True)
        game.switches["window_open"] = True
        self.last_screen = last_screen

        self.begin_update_title = UIImageButton(
            scale(pygame.Rect((195, 30), (400, 81))),
            "",
            object_id="#new_update_button",
            container=self,
        )

        latest_version_number = "{:.16}".format(get_latest_version_number())
        current_version_number = "{:.16}".format(get_version_info().version_number)

        self.game_over_message = UITextBoxTweaked(
            f"<strong>Update to ClanGen {latest_version_number}</strong>",
            scale(pygame.Rect((20, 160), (800, -1))),
            line_spacing=0.8,
            object_id="#update_popup_title",
            container=self,
        )

        self.game_over_message = UITextBoxTweaked(
            f"Your current version: {current_version_number}",
            scale(pygame.Rect((22, 200), (800, -1))),
            line_spacing=0.8,
            object_id="#text_box_current_version",
            container=self,
        )

        self.game_over_message = UITextBoxTweaked(
            f"Install update now?",
            scale(pygame.Rect((20, 262), (400, -1))),
            line_spacing=0.8,
            object_id="#text_box_30",
            container=self,
        )

        self.box_unchecked = UIImageButton(
            scale(pygame.Rect((15, 366), (68, 68))),
            "",
            object_id="#unchecked_checkbox",
            container=self,
        )
        self.box_checked = UIImageButton(
            scale(pygame.Rect((15, 366), (68, 68))),
            "",
            object_id="#checked_checkbox",
            container=self,
        )
        self.box_text = UITextBoxTweaked(
            f"Don't ask again",
            scale(pygame.Rect((78, 370), (250, -1))),
            line_spacing=0.8,
            object_id="#text_box_30",
            container=self,
        )

        self.continue_button = UIImageButton(
            scale(pygame.Rect((556, 370), (204, 60))),
            "",
            object_id="#continue_button_small",
            container=self,
        )

        self.cancel_button = UIImageButton(
            scale(pygame.Rect((374, 370), (156, 60))),
            "",
            object_id="#cancel_button",
            container=self,
        )

        self.close_button = UIImageButton(
            scale(pygame.Rect((740, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )

        if show_checkbox:
            self.box_unchecked.enable()
            self.box_checked.hide()
        else:
            self.box_checked.hide()
            self.box_unchecked.hide()
            self.box_text.hide()

        self.continue_button.enable()
        self.cancel_button.enable()
        self.close_button.enable()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.continue_button:
                game.switches["window_open"] = False
                self.x = UpdateWindow(
                    game.switches["cur_screen"], self.announce_restart_callback
                )
                self.kill()
            elif (
                event.ui_element == self.close_button
                or event.ui_element == self.cancel_button
            ):
                game.switches["window_open"] = False
                self.kill()
            elif event.ui_element == self.box_unchecked:
                self.box_unchecked.disable()
                self.box_unchecked.hide()
                self.box_checked.enable()
                self.box_checked.show()
                with open(
                    f"{get_cache_dir()}/suppress_update_popup", "w"
                ) as write_file:
                    write_file.write(get_latest_version_number())
            elif event.ui_element == self.box_checked:
                self.box_checked.disable()
                self.box_checked.hide()
                self.box_unchecked.enable()
                self.box_unchecked.show()
                if os.path.exists(f"{get_cache_dir()}/suppress_update_popup"):
                    os.remove(f"{get_cache_dir()}/suppress_update_popup")

    def announce_restart_callback(self):
        self.x.kill()
        y = AnnounceRestart(game.switches["cur_screen"])
        y.update(1)


class ChangelogPopup(UIWindow):
    def __init__(self, last_screen):
        super().__init__(
            scale(pygame.Rect((300, 300), (1000, 800))),
            window_display_title="Changelog",
            object_id="#game_over_window",
            resizable=False,
        )
        self.set_blocking(True)

        game.switches["window_open"] = True

        self.last_screen = last_screen
        self.changelog_popup_title = UITextBoxTweaked(
            f"<strong>What's New</strong>",
            scale(pygame.Rect((40, 20), (960, -1))),
            line_spacing=1,
            object_id="#changelog_popup_title",
            container=self,
        )

        current_version_number = "{:.16}".format(get_version_info().version_number)

        self.changelog_popup_subtitle = UITextBoxTweaked(
            f"Version {current_version_number}",
            scale(pygame.Rect((40, 70), (960, -1))),
            line_spacing=1,
            object_id="#changelog_popup_subtitle",
            container=self,
        )

        dynamic_changelog = False
        if (
            get_version_info().is_dev()
            and get_version_info().is_source_build
            and get_version_info().git_installed
        ):
            file_cont = subprocess.check_output(
                [
                    "git",
                    "log",
                    r"--pretty=format:%H|||%cd|||%b|||%s",
                    "-15",
                    "--no-decorate",
                    "--merges",
                    "--grep=Merge pull request",
                    "--date=short",
                ]
            ).decode("utf-8")
            dynamic_changelog = True
        else:
            with open("changelog.txt", "r", encoding="utf-8") as read_file:
                file_cont = read_file.read()

        if get_version_info().is_dev() and not get_version_info().is_source_build:
            dynamic_changelog = True

        if dynamic_changelog:
            commits = file_cont.splitlines()
            file_cont = ""
            for line in commits:
                info = line.split("|||")

                # Get PR number so we can link the PR
                pr_number = re_search(r"Merge pull request #([0-9]*?) ", info[3])
                if pr_number:
                    # For some reason, multi-line links on pygame_gui's text boxes don't work very well.
                    # So, to work around that, just add a little "link" at the end
                    info[
                        2
                    ] += f" <a href='https://github.com/ClanGenOfficial/clangen/pull/{pr_number.group(1)}'>(link)</a>"

                # Format: DATE- \n PR Title (link)
                file_cont += f"<b>{info[1]}</b>\n- {info[2]}\n"

        self.changelog_text = UITextBoxTweaked(
            file_cont,
            scale(pygame.Rect((20, 130), (960, 650))),
            object_id="#text_box_30",
            line_spacing=0.95,
            starting_height=2,
            container=self,
            manager=MANAGER,
        )

        self.close_button = UIImageButton(
            scale(pygame.Rect((940, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            starting_height=2,
            container=self,
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.close_button:
                game.switches["window_open"] = False
                self.kill()


class RelationshipLog(UIWindow):
    """This window allows the user to see the relationship log of a certain relationship."""

    def __init__(self, relationship, disable_button_list, hide_button_list):
        super().__init__(
            scale(pygame.Rect((546, 245), (1010, 1100))),
            window_display_title="Relationship Log",
            object_id="#relationship_log_window",
            resizable=False,
        )
        game.switches["window_open"] = True
        self.hide_button_list = hide_button_list
        for button in self.hide_button_list:
            button.hide()

        self.exit_button = UIImageButton(
            scale(pygame.Rect((940, 15), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )
        self.back_button = UIImageButton(
            scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button"
        )
        self.log_icon = UIImageButton(
            scale(pygame.Rect((445, 808), (68, 68))), "", object_id="#log_icon"
        )
        self.closing_buttons = [self.exit_button, self.back_button, self.log_icon]

        self.disable_button_list = disable_button_list
        for button in self.disable_button_list:
            button.disable()

        """if game.settings["fullscreen"]:
            img_path = "resources/images/spacer.png"
        else:
            img_path = "resources/images/spacer_small.png"""

        opposite_log_string = None
        if not relationship.opposite_relationship:
            relationship.link_relationship()
        if (
            relationship.opposite_relationship
            and len(relationship.opposite_relationship.log) > 0
        ):
            opposite_log_string = f"{f'<br>-----------------------------<br>'.join(relationship.opposite_relationship.log)}<br>"

        log_string = (
            f"{f'<br>-----------------------------<br>'.join(relationship.log)}<br>"
            if len(relationship.log) > 0
            else "There are no relationship logs."
        )

        if not opposite_log_string:
            self.log = pygame_gui.elements.UITextBox(
                log_string,
                scale(pygame.Rect((30, 70), (953, 850))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
        else:
            self.log = pygame_gui.elements.UITextBox(
                log_string,
                scale(pygame.Rect((30, 70), (953, 500))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
            self.opp_heading = pygame_gui.elements.UITextBox(
                "<u><b>OTHER PERSPECTIVE</b></u>",
                scale(pygame.Rect((30, 550), (953, 560))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
            self.opp_heading.disable()
            self.opp_log = pygame_gui.elements.UITextBox(
                opposite_log_string,
                scale(pygame.Rect((30, 610), (953, 465))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )

        self.set_blocking(True)

    def closing_process(self):
        """Handles to enable and kill all processes when a exit button is clicked."""
        game.switches["window_open"] = False
        for button in self.disable_button_list:
            button.enable()

        for button in self.hide_button_list:
            button.show()
            button.enable()
        self.log_icon.kill()
        self.exit_button.kill()
        self.back_button.kill()
        self.kill()

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.closing_buttons:
                self.closing_process()


class SaveError(UIWindow):
    def __init__(self, error_text):
        super().__init__(
            scale(pygame.Rect((300, 300), (1000, 800))),
            window_display_title="Changelog",
            object_id="#game_over_window",
            resizable=False,
        )
        self.set_blocking(True)
        game.switches["window_open"] = True
        self.changelog_popup_title = pygame_gui.elements.UITextBox(
            f"<strong>Saving Failed!</strong>\n\n{error_text}",
            scale(pygame.Rect((40, 20), (890, 750))),
            object_id="#text_box_30",
            container=self,
        )

        self.close_button = UIImageButton(
            scale(pygame.Rect((940, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            starting_height=2,
            container=self,
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.close_button:
                game.switches["window_open"] = False
                self.kill()


class SaveAsImage(UIWindow):
    def __init__(self, image_to_save, file_name):
        super().__init__(
            scale(pygame.Rect((400, 350), (800, 500))),
            object_id="#game_over_window",
            resizable=False,
        )

        self.set_blocking(True)
        game.switches["window_open"] = True

        self.image_to_save = image_to_save
        self.file_name = file_name
        self.scale_factor = 1

        button_layout_rect = scale(pygame.Rect((0, 10), (44, 44)))
        button_layout_rect.topright = scale_dimentions((-2, 10))

        self.close_button = UIImageButton(
            button_layout_rect,
            "",
            object_id="#exit_window_button",
            starting_height=2,
            container=self,
            anchors={"right": "right", "top": "top"},
        )

        self.save_as_image = UIImageButton(
            scale(pygame.Rect((0, 180), (270, 60))),
            "",
            object_id="#save_image_button",
            starting_height=2,
            container=self,
            anchors={"centerx": "centerx"},
            sound_id="save",
        )

        self.open_data_directory_button = UIImageButton(
            scale(pygame.Rect((0, 350), (356, 60))),
            "",
            object_id="#open_data_directory_button",
            container=self,
            starting_height=2,
            tool_tip_text="Opens the data directory. "
            "This is where save files, images, "
            "and logs are stored.",
            anchors={"centerx": "centerx"},
        )

        self.small_size_button = UIImageButton(
            scale(pygame.Rect((109, 100), (194, 60))),
            "",
            object_id="#image_small_button",
            container=self,
            starting_height=2,
        )
        self.small_size_button.disable()

        self.medium_size_button = UIImageButton(
            scale(pygame.Rect((303, 100), (194, 60))),
            "",
            object_id="#image_medium_button",
            container=self,
            starting_height=2,
        )

        self.large_size_button = UIImageButton(
            scale(pygame.Rect((497, 100), (194, 60))),
            "",
            object_id="#image_large_button",
            container=self,
            starting_height=2,
        )

        self.confirm_text = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((10, 250), (780, 90))),
            object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
            container=self,
            starting_height=2,
        )

    def save_image(self):
        file_name = self.file_name
        file_number = ""
        i = 0
        while True:
            if os.path.isfile(
                f"{get_saved_images_dir()}/{file_name + file_number}.png"
            ):
                i += 1
                file_number = f"_{i}"
            else:
                break

        scaled_image = pygame.transform.scale_by(self.image_to_save, self.scale_factor)
        pygame.image.save(
            scaled_image, f"{get_saved_images_dir()}/{file_name + file_number}.png"
        )
        return f"{file_name + file_number}.png"

    def process_event(self, event) -> bool:
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.close_button:
                game.switches["window_open"] = False
                self.kill()
            elif event.ui_element == self.open_data_directory_button:
                if system() == "Darwin":
                    subprocess.Popen(["open", "-R", get_data_dir()])
                elif system() == "Windows":
                    os.startfile(get_data_dir())  # pylint: disable=no-member
                elif system() == "Linux":
                    try:
                        subprocess.Popen(["xdg-open", get_data_dir()])
                    except OSError:
                        logger.exception("Failed to call to xdg-open.")
                return
            elif event.ui_element == self.save_as_image:
                file_name = self.save_image()
                self.confirm_text.set_text(
                    f"Saved as {file_name} in the saved_images folder"
                )
            elif event.ui_element == self.small_size_button:
                self.scale_factor = 1
                self.small_size_button.disable()
                self.medium_size_button.enable()
                self.large_size_button.enable()
            elif event.ui_element == self.medium_size_button:
                self.scale_factor = 4
                self.small_size_button.enable()
                self.medium_size_button.disable()
                self.large_size_button.enable()
            elif event.ui_element == self.large_size_button:
                self.scale_factor = 6
                self.small_size_button.enable()
                self.medium_size_button.enable()
                self.large_size_button.disable()


class EventLoading(UIWindow):
    def __init__(self, pos):

        if pos is None:
            pos = (800, 700)

        super().__init__(
            scale(pygame.Rect(pos, (200, 200))),
            window_display_title="Game Over",
            object_id="#loading_window",
            resizable=False,
        )

        self.set_blocking(True)

        self.frames = self.load_images()
        self.end_animation = False

        self.animated_image = pygame_gui.elements.UIImage(
            scale(pygame.Rect(0, 0, 200, 200)), self.frames[0], container=self
        )

        self.animation_thread = threading.Thread(target=self.animate)
        self.animation_thread.start()

    @staticmethod
    def load_images():
        frames = []
        for i in range(0, 16):
            frames.append(
                pygame.image.load(f"resources/images/loading_animate/timeskip/{i}.png")
            )

        return frames

    def animate(self):

        i = 0
        while True:
            if self.end_animation:
                break

            i += 1
            if i >= len(self.frames):
                i = 0

            self.animated_image.set_image(self.frames[i])

            time.sleep(0.125)

    def kill(self):
        self.end_animation = True
        super().kill()


class ChangeCatToggles(UIWindow):
    """This window allows the user to edit various cat behavior toggles"""

    def __init__(self, cat):
        super().__init__(
            scale(pygame.Rect((600, 430), (800, 370))),
            window_display_title="Change Cat Name",
            object_id="#change_cat_name_window",
            resizable=False,
        )
        game.switches["window_open"] = True
        self.the_cat = cat
        self.set_blocking(True)
        self.back_button = UIImageButton(
            scale(pygame.Rect((740, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )

        self.checkboxes = {}
        self.refresh_checkboxes()

        # Text
        self.text_1 = pygame_gui.elements.UITextBox(
            "Prevent fading",
            scale(pygame.Rect(110, 60, -1, 50)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        self.text_2 = pygame_gui.elements.UITextBox(
            "Prevent kits",
            scale(pygame.Rect(110, 110, -1, 50)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        self.text_3 = pygame_gui.elements.UITextBox(
            "Prevent retirement",
            scale(pygame.Rect(110, 160, -1, 50)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        self.text_4 = pygame_gui.elements.UITextBox(
            "Limit romantic interactions and mate changes",
            scale(pygame.Rect(110, 210, -1, 50)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        # Text

    def refresh_checkboxes(self):

        for x in self.checkboxes.values():
            x.kill()
        self.checkboxes = {}

        # Prevent Fading
        if self.the_cat == game.clan.instructor:
            box_type = "#checked_checkbox"
            tool_tip = "The afterlife guide can never fade."
        elif self.the_cat.prevent_fading:
            box_type = "#checked_checkbox"
            tool_tip = "Prevents cat from fading away after being dead for 202 moons."
        else:
            box_type = "#unchecked_checkbox"
            tool_tip = "Prevents cat from fading away after being dead for 202 moons."

        # Fading
        self.checkboxes["prevent_fading"] = UIImageButton(
            scale(pygame.Rect(45, 50, 68, 68)),
            "",
            container=self,
            object_id=box_type,
            tool_tip_text=tool_tip,
        )

        if self.the_cat == game.clan.instructor:
            self.checkboxes["prevent_fading"].disable()

        # No Kits
        if self.the_cat.no_kits:
            box_type = "#checked_checkbox"
            tool_tip = "Prevent the cat from adopting or having kittens."
        else:
            box_type = "#unchecked_checkbox"
            tool_tip = "Prevent the cat from adopting or having kittens."

        self.checkboxes["prevent_kits"] = UIImageButton(
            scale(pygame.Rect(45, 100, 68, 68)),
            "",
            container=self,
            object_id=box_type,
            tool_tip_text=tool_tip,
        )

        # No Retire
        if self.the_cat.no_retire:
            box_type = "#checked_checkbox"
            tool_tip = "Allow cat to retiring automatically."
        else:
            box_type = "#unchecked_checkbox"
            tool_tip = "Prevent cat from retiring automatically."

        self.checkboxes["prevent_retire"] = UIImageButton(
            scale(pygame.Rect(45, 150, 68, 68)),
            "",
            container=self,
            object_id=box_type,
            tool_tip_text=tool_tip,
        )

        # No mates
        if self.the_cat.no_mates:
            box_type = "#checked_checkbox"
            tool_tip = "Prevent cat from automatically taking a mate, breaking up, or having romantic interactions with non-mates."
        else:
            box_type = "#unchecked_checkbox"
            tool_tip = "Prevent cat from automatically taking a mate, breaking up, or having romantic interactions with non-mates."

        self.checkboxes["prevent_mates"] = UIImageButton(
            scale(pygame.Rect(45, 200, 68, 68)),
            "",
            container=self,
            object_id=box_type,
            tool_tip_text=tool_tip,
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.switches["window_open"] = False
                game.all_screens["profile screen"].exit_screen()
                game.all_screens["profile screen"].screen_switches()
                self.kill()
            elif event.ui_element == self.checkboxes["prevent_fading"]:
                self.the_cat.prevent_fading = not self.the_cat.prevent_fading
                self.refresh_checkboxes()
            elif event.ui_element == self.checkboxes["prevent_kits"]:
                self.the_cat.no_kits = not self.the_cat.no_kits
                self.refresh_checkboxes()
            elif event.ui_element == self.checkboxes["prevent_retire"]:
                self.the_cat.no_retire = not self.the_cat.no_retire
                self.refresh_checkboxes()
            elif event.ui_element == self.checkboxes["prevent_mates"]:
                self.the_cat.no_mates = not self.the_cat.no_mates
                self.refresh_checkboxes()

        return super().process_event(event)


class SelectFocusClans(UIWindow):
    """This window allows the user to select the clans to be sabotaged, aided or raided in the focus setting."""

    def __init__(self):
        super().__init__(
            scale(pygame.Rect((500, 420), (600, 450))),
            window_display_title="Change Cat Name",
            object_id="#change_cat_name_window",
            resizable=False,
        )
        game.switches["window_open"] = True
        self.set_blocking(True)
        self.back_button = UIImageButton(
            scale(pygame.Rect((540, 10), (44, 44))),
            "",
            object_id="#exit_window_button",
            container=self,
        )
        self.save_button = UIImageButton(
            scale(pygame.Rect((161, 360), (278, 60))),
            "",
            object_id="#change_focus_button",
            container=self,
        )
        self.save_button.disable()

        self.checkboxes = {}
        self.refresh_checkboxes()

        # Text
        self.texts = {}
        self.texts["prompt"] = pygame_gui.elements.UITextBox(
            "<b>Which Clans will you target?</b>",
            scale(pygame.Rect((0, 10), (600, 60))),
            object_id="#text_box_30_horizcenter",
            container=self,
        )
        n = 0
        for clan in game.clan.all_clans:
            self.texts[clan.name] = pygame_gui.elements.UITextBox(
                clan.name + "clan",
                scale(pygame.Rect(215, n * 55 + 77, -1, 50)),
                object_id="#text_box_30_horizleft_pad_0_8",
                container=self,
            )
            n += 1

    def refresh_checkboxes(self):
        for x in self.checkboxes.values():
            x.kill()
        self.checkboxes = {}

        n = 0
        for clan in game.clan.all_clans:
            box_type = "#unchecked_checkbox"
            if clan.name in game.clan.clans_in_focus:
                box_type = "#checked_checkbox"

            self.checkboxes[clan.name] = UIImageButton(
                scale(pygame.Rect(150, n * 55 + 70, 68, 68)),
                "",
                container=self,
                object_id=box_type,
            )
            n += 1

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.clan.clans_in_focus = []
                game.switches["window_open"] = False
                game.all_screens["warrior den screen"].exit_screen()
                game.all_screens["warrior den screen"].screen_switches()
                self.kill()
            if event.ui_element == self.save_button:
                game.switches["window_open"] = False
                game.all_screens["warrior den screen"].save_focus()
                game.all_screens["warrior den screen"].exit_screen()
                game.all_screens["warrior den screen"].screen_switches()
                self.kill()
            if event.ui_element in self.checkboxes.values():
                for clan_name, value in self.checkboxes.items():
                    if value == event.ui_element:
                        if value.object_ids[1] == "#unchecked_checkbox":
                            game.clan.clans_in_focus.append(clan_name)
                        if value.object_ids[1] == "#checked_checkbox":
                            game.clan.clans_in_focus.remove(clan_name)
                        self.refresh_checkboxes()
                if len(game.clan.clans_in_focus) < 1 and self.save_button.is_enabled:
                    self.save_button.disable()
                if (
                    len(game.clan.clans_in_focus) >= 1
                    and not self.save_button.is_enabled
                ):
                    self.save_button.enable()

        return super().process_event(event)
