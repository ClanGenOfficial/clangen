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


class WhitePatchToolWindow(ComboToolWindow):
    def __init__(self):
        super().__init__()
        sprites.create_patch_combo(
            combos={"TEST": []}, sheet_name="patches_white_", white_category="little"
        )

        self.example_cat = self.create_cat(patch="TEST")
        self.preview_cat = self.create_cat(patch="TEST")

        self.create_elements()

    def create_elements(self):
        super().create_elements()

        prev_element = self.elements["preview_cat"]
        i = 2
        for name, data in {
            "little": sprites.WHITE_LITTLE_DATA,
            "mid": sprites.WHITE_MID_DATA,
            "high": sprites.WHITE_HIGH_DATA,
            "mostly": sprites.WHITE_MOSTLY_DATA,
        }.items():
            patches = list(itertools.chain.from_iterable(data["sprite_list"]))
            patches.sort()
            self.elements[f"{name}_patch_choice"] = UIScrollingDropDown(
                ui_scale(pygame.Rect((0, 2), (180, 34))),
                dropdown_dimensions=ui_scale_dimensions((180, 225 + (150 / i))),
                parent_text=f"{name} patches",
                multiple_choice=True,
                item_list=patches,
                manager=MANAGER,
                container=self,
                anchors={
                    "top_target": prev_element,
                    "left_target": self.elements["example_cat"],
                },
                starting_height=5,
            )
            prev_element = self.elements[f"{name}_patch_choice"].parent_button
            i += i * 2

        self.elements["combo_coverage"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((40, 360), (150, 34))),
            dropdown_dimensions=ui_scale_dimensions((150, 100)),
            parent_text="combo coverage",
            item_list=list(sprites.WHITE_PATCH_COMBOS.keys()),
            manager=MANAGER,
            multiple_choice=False,
            container=self,
            child_trigger_close=True,
            starting_height=3,
        )

    def process_event(self, event):
        super().process_event(event)
        if event.type == SELECTION_CHANGED:
            if (
                event.ui_element
                == self.elements["combo_coverage"].child_button_container
            ):
                selection = self.elements["combo_coverage"].selected_list
                if selection:
                    self.elements["combo_coverage"].parent_button.set_text(selection[0])
                else:
                    self.elements["combo_coverage"].parent_button.set_text(
                        "combo coverage"
                    )
                return
            elif event.ui_element in (
                self.elements["little_patch_choice"].child_button_container,
                self.elements["mid_patch_choice"].child_button_container,
                self.elements["high_patch_choice"].child_button_container,
                self.elements["mostly_patch_choice"].child_button_container,
            ):
                selection = self.get_selection_list()
                self.set_combo_selection(selection)
                return

            elif (
                self.elements["existing_combos"].child_button_container
                == event.ui_element
            ):
                selection = self.elements["existing_combos"].selected_list
                if not selection:
                    return
                new_selection = [
                    s.replace("little", "")
                    .replace("mid", "")
                    .replace("high", "")
                    .replace("mostly", "")
                    for s in self.get_combos()[selection[0]]
                ]
                for dropdown in (
                    self.elements["little_patch_choice"],
                    self.elements["mid_patch_choice"],
                    self.elements["high_patch_choice"],
                    self.elements["mostly_patch_choice"],
                ):
                    current_selection = dropdown.selected_list
                    updated = []

                    for i in dropdown.item_list:
                        if i in new_selection and i not in current_selection:
                            updated.append(i)
                    dropdown.set_selected_list(updated)

                self.set_combo_selection(self.get_selection_list())
                return

        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            for patch_dropdown in (
                "little_patch_choice",
                "mid_patch_choice",
                "high_patch_choice",
                "mostly_patch_choice",
            ):
                for name, button in self.elements[
                    patch_dropdown
                ].child_button_dicts.items():
                    if button == event.ui_element:
                        self.set_preview_cat(name)
                        return

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.elements["save_button"]:
                if self.save_combo():
                    self.elements["little_patch_choice"].set_selected_list([])
                    self.elements["mid_patch_choice"].set_selected_list([])
                    self.elements["high_patch_choice"].set_selected_list([])
                    self.elements["mostly_patch_choice"].set_selected_list([])
                    combos = list(self.get_combos().keys())
                    combos.sort()
                    self.elements["existing_combos"].new_item_list(combos)
                    self.elements["name_entry"].set_text("")

            elif event.ui_element == self.elements["clear_button"]:
                self.elements["little_patch_choice"].set_selected_list([])
                self.elements["mid_patch_choice"].set_selected_list([])
                self.elements["high_patch_choice"].set_selected_list([])
                self.elements["mostly_patch_choice"].set_selected_list([])
                self.elements["existing_combos"].set_selected_list([])

    def set_combo_selection(self, selection):
        sprites.create_patch_combo(
            combos={"TEST": selection},
            sheet_name="patches_white_",
            white_category="little",
        )
        self.example_cat = self.create_cat("TEST")
        self.elements["example_cat"].set_image(
            pygame.transform.scale(
                self.example_cat.sprite, ui_scale_dimensions((200, 200))
            )
        )
        self.elements["chosen_patches"].set_text(str(selection))
        self.check_current_combos(selection)

    def get_selection_list(self):
        return [
            f"{amount}{p}"
            for amount in ["little", "mid", "high", "mostly"]
            for p in self.elements[f"{amount}_patch_choice"].selected_list
        ]

    def set_preview_cat(self, name):
        self.preview_cat = self.create_cat(name)
        self.elements["preview_cat"].set_image(
            pygame.transform.scale(
                self.preview_cat.sprite, ui_scale_dimensions((100, 100))
            )
        )

    def save_combo(self) -> bool:
        coverage = (
            self.elements["combo_coverage"].selected_list[0]
            if self.elements["combo_coverage"].selected_list
            else None
        )
        name = self.elements["name_entry"].get_text().upper().replace(" ", "_")
        selection = self.get_selection_list()

        if not name or not selection or not coverage:
            self.elements["save_text"].set_text("missing information...")
            return False

        path = "sprites/dicts/white_patches_combos.json"
        try:
            with open(path, "r") as read_file:
                combos = read_file.read()
                combos_dict = ujson.loads(combos)

        except Exception as e:
            print(f"Something went wrong with {path}: {e}")
            self.elements["save_text"].set_text("save failed!")
            return False

        combos_dict[coverage].update({name: selection})

        dict_text = ujson.dumps(combos_dict, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        with open(path, "w") as write_file:
            write_file.write(dict_text)

        # update sprites so this can appear on our existing combo preview
        sprites.create_patch_combo(
            combos={name: selection},
            sheet_name="patches_white_",
            white_category=coverage,
        )

        self.elements["save_text"].set_text("saved!")
        return True

    def create_cat(self, patch: str):
        new_cat = TestCatFactory.create_cat(
            moons=60,
            loading_cat=True,
            pelt=Pelt(
                name="Rosette",
                colour="GINGER",
                length="medium",
                eye_color="SAGE",
                reverse=False,
                white_patches=patch,
                white_patches_tint="offwhite",
                vitiligo=None,
                points=None,
                tortie_marking=None,
                tortie_base=None,
                tortie_pattern=None,
                tortie_colour=None,
                tint="pink",
                skin="DARK",
                adult_sprite=self.current_pose,
            ),
        )

        return new_cat

    def get_combos(self) -> dict:
        with open(
            "sprites/dicts/white_patches_combos.json", "r", encoding="utf-8"
        ) as read_file:
            combos = ujson.loads(read_file.read())

        output = {}
        for coverage, combo_list in combos.items():
            for c in combo_list:
                output.update({c: combo_list[c]})
        return output
