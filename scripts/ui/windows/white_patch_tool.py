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


class WhitePatchToolWindow(GameWindow):
    """This window allows the user to change the cat's name"""

    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((100, 100), (600, 500))),
        )
        self.elements = {}

        sprites.create_patch_combo(
            combos={"TEST": []}, sheet_name="patches_white_", white_category="little"
        )

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
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, 100))),
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

        prev_element = self.elements["preview_cat"]
        for name, data in {
            "little": sprites.WHITE_LITTLE_DATA,
            "mid": sprites.WHITE_MID_DATA,
            "high": sprites.WHITE_HIGH_DATA,
            "mostly": sprites.WHITE_MOSTLY_DATA,
        }.items():
            patches = list(itertools.chain.from_iterable(data["sprite_list"]))
            patches.sort()
            self.elements[f"{name}_patch_choice"] = UIScrollingDropDown(
                ui_scale(pygame.Rect((10, 10), (150, 34))),
                dropdown_dimensions=ui_scale_dimensions((150, 194)),
                parent_text=f"{name} patches",
                multiple_choice=True,
                item_list=patches,
                manager=MANAGER,
                container=self,
                anchors={
                    "top_target": prev_element,
                    "left_target": self.elements["example_cat"],
                },
                starting_height=3,
            )
            prev_element = self.elements[f"{name}_patch_choice"].parent_button

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
            ui_scale(pygame.Rect((50, 10), (170, 34))),
            dropdown_dimensions=ui_scale_dimensions((170, 290)),
            parent_text="existing combos",
            item_list=combos,
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["combo_preview_cat"],
                "left_target": self.elements["preview_cat"],
            },
            child_trigger_close=True,
            starting_height=3,
            multiple_choice=False,
        )

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

            if (
                self.elements["existing_combos"].child_button_container
                == event.ui_element
            ):
                selection = self.elements["existing_combos"].selected_list
                if not selection:
                    return
                self.set_combo_selection(self.get_combos()[selection[0]])
                return
        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            for name, button in self.elements[
                "little_patch_choice"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.set_preview_cat(name)
                    return
            for name, button in self.elements[
                "mid_patch_choice"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.set_preview_cat(name)
                    return
            for name, button in self.elements[
                "high_patch_choice"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.set_preview_cat(name)
                    return
            for name, button in self.elements[
                "mostly_patch_choice"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.set_preview_cat(name)
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
                if self.save_combo():
                    self.elements["little_patch_choice"].set_selected_list([])
                    self.elements["mid_patch_choice"].set_selected_list([])
                    self.elements["high_patch_choice"].set_selected_list([])
                    self.elements["mostly_patch_choice"].set_selected_list([])
                    combos = list(self.get_combos().keys())
                    combos.sort()
                    self.elements["existing_combos"].new_item_list(combos)
                    self.elements["name_entry"].set_text("")

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
        selection = [
            f"little{p}" for p in self.elements["little_patch_choice"].selected_list
        ]
        selection.extend(
            [f"mid{p}" for p in self.elements["mid_patch_choice"].selected_list]
        )
        selection.extend(
            [f"high{p}" for p in self.elements["high_patch_choice"].selected_list]
        )
        selection.extend(
            [f"mostly{p}" for p in self.elements["mostly_patch_choice"].selected_list]
        )
        return selection

    def set_preview_cat(self, name):
        self.preview_cat = self.create_cat(name)
        self.elements["preview_cat"].set_image(
            pygame.transform.scale(
                self.preview_cat.sprite, ui_scale_dimensions((100, 100))
            )
        )

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
                adult_sprite="adult_short2",
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

    def kill(self):
        super().kill()
        # sets the game to reload!
        # this makes sure the sprites info is up to date if a dev decides to play after using this tool
        switch_set_value(Switch.switch_clan, True)
