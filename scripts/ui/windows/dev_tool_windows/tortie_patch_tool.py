import itertools

import pygame
import pygame_gui
import ujson

from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.pelts import Pelt
from scripts.cat.sprites.load_sprites import sprites
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.scrolling_button_list import SELECTION_CHANGED
from scripts.ui.elements.scrolling_dropdown import UIScrollingDropDown
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.windows.dev_tool_windows.combo_tool_base import ComboToolWindow


class TortiePatchToolWindow(ComboToolWindow):
    def __init__(self):
        super().__init__()
        sprites.create_patch_combo(combos={"TEST": []}, sheet_name="patches_tortie")

        self.example_cat = self.create_cat(patch="TEST")
        self.preview_cat = self.create_cat(patch="TEST")

        self.create_elements()

    def create_elements(self):
        super().create_elements()
        patches = list(
            itertools.chain.from_iterable(sprites.TORTIE_DATA["sprite_list"])
        )
        patches.sort()
        self.elements["patch_choice"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((10, 10), (150, 34))),
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

    def process_event(self, event):
        super().process_event(event)
        if event.type == SELECTION_CHANGED:
            if event.ui_element == self.elements["patch_choice"].child_button_container:
                selection = self.elements["patch_choice"].selected_list
                self.set_combo_selection(selection)
                return
            elif (
                self.elements["existing_combos"].child_button_container
                == event.ui_element
            ):
                selection = self.elements["existing_combos"].selected_list
                if not selection:
                    return
                new_selection = self.get_combos()[selection[0]]
                self.elements["patch_choice"].set_selected_list(new_selection)
                self.set_combo_selection(new_selection)
                return

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
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.elements["save_button"]:
                self.save_combo()
                self.elements["patch_choice"].set_selected_list([])
                combos = list(self.get_combos().keys())
                combos.sort()
                self.elements["existing_combos"].new_item_list(combos)
                self.elements["name_entry"].set_text("")
            elif event.ui_element == self.elements["clear_button"]:
                self.elements["patch_choice"].set_selected_list([])
                self.elements["existing_combos"].set_selected_list([])

    def set_combo_selection(self, selection):
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
                adult_sprite=self.current_pose,
            ),
        )

        return new_cat

    def get_combos(self) -> dict:
        with open(
            "sprites/dicts/tortie_patches_combos.json", "r", encoding="utf-8"
        ) as read_file:
            return ujson.loads(read_file.read())
