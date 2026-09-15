import itertools

import pygame
import pygame_gui
import ujson
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIImage, UITextEntryLine

from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.pelts import Pelt
from scripts.cat.sprites.load_sprites import sprites
from scripts.events_module.text_adjust import adjust_list_text
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.scrolling_button_list import SELECTION_CHANGED
from scripts.ui.elements.scrolling_dropdown import UIScrollingDropDown
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.windows.window_base_class import GameWindow


class TortiePatchToolWindow(GameWindow):
    """This window allows the user to change the cat's name"""

    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((100, 100), (600, 500))),
        )
        self.elements = {}

        sprites.create_patch_combo(combos={"TEST": []}, sheet_name="patches_tortie")

        self.example_cat = self.create_cat(patch="TEST")
        self.preview_cat = self.create_cat(patch="TEST")

        self.elements["example_cat"] = UIImage(
            ui_scale(pygame.Rect((10, 0), (200, 200))),
            pygame.transform.scale(
                self.example_cat.sprite, ui_scale_dimensions((200, 200))
            ),
            container=self,
        )

        self.elements["chosen_patches"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, -1))),
            html_text="",
            container=self,
            anchors={"top_target": self.elements["example_cat"]},
        )
        self.elements["warning"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, -1))),
            html_text="",
            container=self,
            anchors={"top_target": self.elements["chosen_patches"]},
        )

        self.elements["preview_cat"] = UIImage(
            ui_scale(pygame.Rect((40, 20), (100, 100))),
            pygame.transform.scale(
                self.preview_cat.sprite, ui_scale_dimensions((100, 100))
            ),
            container=self,
            anchors={"left_target": self.elements["example_cat"]},
        )

        patches = list(
            itertools.chain.from_iterable(sprites.TORTIE_DATA["sprite_list"])
        )
        patches.sort()
        self.elements["patch_choice"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((10, 20), (150, 34))),
            dropdown_dimensions=ui_scale_dimensions((150, 290)),
            parent_text="patches",
            multiple_choice=True,
            item_list=patches,
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["preview_cat"],
                "left_target": self.elements["example_cat"],
            },
            starting_height=3,
        )

        self.elements["combo_preview_cat"] = UIImage(
            ui_scale(pygame.Rect((90, 20), (100, 100))),
            pygame.transform.scale(
                self.preview_cat.sprite, ui_scale_dimensions((100, 100))
            ),
            container=self,
            anchors={"left_target": self.elements["preview_cat"]},
        )
        combos = list(self.get_combos().keys())
        combos.sort()
        self.elements["existing_combos"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((50, 20), (170, 34))),
            dropdown_dimensions=ui_scale_dimensions((170, 290)),
            parent_text="existing combos",
            multiple_choice=True,
            item_list=combos,
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["combo_preview_cat"],
                "left_target": self.elements["preview_cat"],
            },
            child_trigger_close=True,
            starting_height=3,
        )

        self.elements["saving_container"] = UIContainer(
            ui_scale(pygame.Rect((40, 420), (500, 40))),
            container=self,
            manager=MANAGER,
        )
        self.elements["name_entry"] = UITextEntryLine(
            ui_scale(pygame.Rect((0, 0), (150, 40))),
            container=self.elements["saving_container"],
            placeholder_text="new combo name",
        )

        self.elements["save_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 0), (70, 34))),
            text="save",
            image_dict=get_button_dict(ButtonStyles.SQUOVAL, (70, 34)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.elements["saving_container"],
            anchors={"left_target": self.elements["name_entry"], "centery": "centery"},
        )
        self.elements["save_text"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, -1))),
            html_text="",
            container=self.elements["saving_container"],
            anchors={"left_target": self.elements["save_button"]},
        )

    def process_event(self, event):
        super().process_event(event)
        if event.type == SELECTION_CHANGED:
            selection = self.elements["patch_choice"].selected_list
            sprites.create_patch_combo(
                combos={"TEST": selection},
                sheet_name="patches_tortie",
            )
            self.example_cat = self.create_cat("TEST")
            self.elements["example_cat"].set_image(
                pygame.transform.scale(
                    self.example_cat.sprite, ui_scale_dimensions((200, 200))
                )
            )
            self.elements["chosen_patches"].set_text(str(selection))
            self.check_current_combos(selection)
        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            for name, button in self.elements[
                "patch_choice"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.preview_cat = self.create_cat(name)
                    self.elements["preview_cat"].set_image(
                        pygame.transform.scale(
                            self.preview_cat.sprite, ui_scale_dimensions((100, 100))
                        )
                    )
                    return
            for name, button in self.elements[
                "existing_combos"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.preview_cat = self.create_cat(name)
                    self.elements["combo_preview_cat"].set_image(
                        pygame.transform.scale(
                            self.preview_cat.sprite, ui_scale_dimensions((100, 100))
                        )
                    )
                    return
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.elements["save_button"]:
                self.save_combo()
                self.elements["patch_choice"].set_selected_list([])
                combos = list(self.get_combos().keys())
                combos.sort()
                self.elements["existing_combos"].new_item_list(combos)
                self.elements["name_entry"].set_text("")

    def check_current_combos(self, selection):
        if not selection:
            self.elements["warning"].set_text(f"")
            return

        existing_combos = []
        for name, combo in self.get_combos().items():
            if set(selection) == set(combo):
                self.elements["warning"].set_text(
                    f"This combo already exists as {name}"
                )
                existing_combos.clear()
                break

            elif set(selection).issubset(set(combo)):
                existing_combos.append(name)

        if existing_combos:
            self.elements["warning"].set_text(
                f"This combo is part of {adjust_list_text(existing_combos)}"
            )

        self.elements["warning"].update_containing_rect_position()

    def save_combo(self):
        name = self.elements["name_entry"].get_text().upper().replace(" ", "_")
        selection = self.elements["patch_choice"].selected_list

        if not name or not selection:
            self.elements["save_text"].set_text("missing information...")
            return

        path = "sprites/dicts/tortie_patches_combos.json"
        try:
            with open(path, "r") as read_file:
                combos = read_file.read()
                combos_dict = ujson.loads(combos)

        except Exception as e:
            print(f"Something went wrong with {path}: {e}")
            self.elements["save_text"].set_text("save failed!")
            return

        combos_dict.update({name: selection})

        dict_text = ujson.dumps(combos_dict, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        with open(path, "w") as write_file:
            write_file.write(dict_text)

        # update sprites so this can appear on our existing combo preview
        sprites.create_patch_combo(
            combos={name: selection},
            sheet_name="patches_tortie",
        )

        self.elements["save_text"].set_text("saved!")

    def create_cat(self, patch: str):
        new_cat = TestCatFactory.create_cat(
            moons=60,
            loading_cat=True,
            pelt=Pelt(
                name="Tortie",
                colour="BLACK",
                length="medium",
                eye_color="SAGE",
                reverse=False,
                white_patches=None,
                vitiligo=None,
                points=None,
                tortie_marking=patch,
                tortie_base="mackerel",
                tortie_pattern="mackerel",
                tortie_colour="GINGER",
                tint="pink",
                skin="DARK",
                adult_sprite="adult_short2",
            ),
        )

        return new_cat

    def get_combos(self) -> dict:
        with open(
            "sprites/dicts/tortie_patches_combos.json", "r", encoding="utf-8"
        ) as read_file:
            return ujson.loads(read_file.read())

    def kill(self):
        super().kill()
        # sets the game to reload!
        # this makes sure the sprites info is up to date if a dev decides to play after using this tool
        switch_set_value(Switch.switch_clan, True)
