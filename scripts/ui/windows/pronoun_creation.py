from collections import namedtuple

import pygame
import pygame_gui

from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import (
    get_custom_pronouns,
    get_lang_config,
    add_custom_pronouns,
)
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIDropDown,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale


class PronounCreation(GameWindow):
    # This window allows the user to create a pronoun set
    PronounCat = namedtuple("PronounCat", ["name", "pronouns"])

    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((80, 150), (650, 450))),
            window_display_title="Create Cat Pronouns",
            object_id="#change_cat_gender_window",
        )
        self.dropdowns = {}
        self.the_cat = cat
        self.pronoun_cat = self.PronounCat(
            str(self.the_cat.name), self.the_cat.pronouns
        )
        self.pronoun_template = self.the_cat.pronouns[0].copy()
        self.pronoun_template["ID"] = "custom" + str(len(get_custom_pronouns()))
        self.conju = self.pronoun_template.get("conju", 2)
        self.gender = self.pronoun_template.get("gender", 0)
        self.box_labels = {}
        self.elements = {}
        self.boxes = {}
        self.checkbox_label = {}

        self.elements["core_container"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 3), (375, 448))),
            manager=MANAGER,
            container=self,
        )
        self.elements["core_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((4, 0), (375, 448))),
            get_box(BoxStyles.FRAME, (375, 448), sides=(False, True, False, False)),
            container=self.elements["core_container"],
            manager=MANAGER,
        )

        # Create a sub-container for the Demo frame and sample text
        demo_container_rect = ui_scale(pygame.Rect((0, 0), (275, 450)))
        self.demo_container = pygame_gui.core.UIContainer(
            relative_rect=demo_container_rect,
            manager=MANAGER,
            container=self,
            anchors={"left": "left", "left_target": self.elements["core_container"]},
        )

        # # Add the Demo frame to the sub-container
        self.elements["demo_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 4), (208, 288))),
            get_box(BoxStyles.FRAME, (208, 288), sides=(False, True, True, True)),
            manager=MANAGER,
            container=self.demo_container,
            anchors={"center": "center"},
        )
        # Title of Demo Box
        self.elements["demo_title"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, -14), (208, 30))),
            "windows.create_pronouns_demo_title",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (208, 30), static=True),
            object_id="@buttonstyles_rounded_rect",
            manager=MANAGER,
            container=self.demo_container,
            anchors={
                "centerx": "centerx",
                "bottom": "bottom",
                "bottom_target": self.elements["demo_frame"],
            },
        )
        self.elements["demo_title"].disable()

        # Add UITextBox for the sample text to the sub-container
        self.sample_text_box = pygame_gui.elements.UITextBox(
            "screens.change_gender.demo",
            ui_scale(pygame.Rect((0, 4), (195, 268))),
            object_id="#text_box_30_horizcenter_vertcenter",
            manager=MANAGER,
            container=self.demo_container,
            anchors={"center": "center"},
            text_kwargs={"m_c": self.the_cat},
        )

        # Title
        self.elements["title"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 15), (225, 40))),
            "windows.pronoun_creation",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (225, 40), static=True),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self.elements["core_container"],
            anchors={"centerx": "centerx"},
        )
        self.elements["title"].disable()

        self.heading = pygame_gui.elements.UITextBox(
            "windows.create_pronouns_desc",
            ui_scale(pygame.Rect((0, 60), (350, 75))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self.elements["core_container"],
            anchors={"centerx": "centerx"},
        )
        config = get_lang_config()["pronouns"]

        self.dropdowns["conju_label"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((-50, 130), (100, 32))),
            "windows.conju",
            object_id="#text_box_30_horizcenter_spacing_95",
            container=self.elements["core_container"],
            anchors={"centerx": "centerx"},
        )

        self.dropdowns["gender_label"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((-50, 5), (100, 32))),
            "windows.gender",
            object_id="#text_box_30_horizcenter_spacing_95",
            container=self.elements["core_container"],
            anchors={"top_target": self.dropdowns["conju_label"], "centerx": "centerx"},
        )

        self.dropdowns["conju"] = UIDropDown(
            pygame.Rect((0, -3), (100, 32)),
            parent_text=f"windows.conju{self.conju}",
            item_list=[
                f"windows.conju{i}" for i in range(1, config["conju_count"] + 1)
            ],
            manager=MANAGER,
            container=self.elements["core_container"],
            anchors={
                "left_target": self.dropdowns["gender_label"],
                "top_target": self.heading,
            },
            starting_selection=[f"windows.conju{self.conju}"],
        )
        self.dropdowns["gender"] = UIDropDown(
            pygame.Rect((0, 34), (100, 32)),
            parent_text=f"windows.gender{self.gender}",
            item_list=[f"windows.gender{i}" for i in range(0, config["gender_count"])],
            manager=MANAGER,
            container=self.elements["core_container"],
            anchors={
                "left_target": self.dropdowns["gender_label"],
                "top_target": self.heading,
            },
            starting_selection=[f"windows.gender{self.gender}"],
        )

        text_inputs = list(self.pronoun_template.keys())
        try:
            text_inputs.remove("ID")
            text_inputs.remove("conju")
            text_inputs.remove("gender")
        except ValueError:
            pass

        for i, item in enumerate(text_inputs):
            self.box_labels[item] = pygame_gui.elements.UITextBox(
                f"windows.{item}",
                ui_scale(pygame.Rect((0, 5), (200, 30))),
                object_id="#text_box_30_horizcenter_spacing_95",
                manager=MANAGER,
                container=self.elements["core_container"],
                anchors=(
                    {"top_target": self.box_labels[text_inputs[i - 1]]}
                    if i > 0
                    else {"top_target": self.dropdowns["gender_label"]}
                ),
            )
            self.boxes[item] = pygame_gui.elements.UITextEntryLine(
                ui_scale(pygame.Rect((0, 5), (150, 30))),
                placeholder_text=self.the_cat.pronouns[0][item],
                manager=MANAGER,
                container=self,
                anchors=(
                    {
                        "top_target": self.boxes[text_inputs[i - 1]],
                        "left_target": self.box_labels[item],
                    }
                    if i > 0
                    else {
                        "top_target": self.dropdowns["gender_label"],
                        "left_target": self.box_labels[item],
                    }
                ),
            )
            self.boxes[item].set_allowed_characters("alpha_numeric")

        self.buttons = {}
        self.buttons["save_pronouns"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 400), (73, 30))),
            "buttons.save",
            get_button_dict(ButtonStyles.SQUOVAL, (73, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.elements["core_container"],
            anchors={"centerx": "centerx"},
        )

        self.pronoun_added = pygame_gui.elements.UITextBox(
            f"windows.pronoun_confirm",
            ui_scale(pygame.Rect((0, 375), (300, 40))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
            container=self.elements["core_container"],
            anchors={"centerx": "centerx"},
        )

    def update_display(self):
        for name, entry in self.boxes.items():
            self.pronoun_template[name] = (
                entry.get_text() if entry.get_text() != "" else entry.placeholder_text
            )
        self.sample_text_box.set_text(
            "screens.change_gender.demo",
            text_kwargs={
                "m_c": self.PronounCat(str(self.the_cat.name), [self.pronoun_template])
            },
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.all_screens[GameScreen.CHANGE_GENDER].exit_screen()
                game.all_screens[GameScreen.CHANGE_GENDER].screen_switches()
                [item.kill() for item in self.dropdowns.values()]
            elif event.ui_element in self.dropdowns["conju"].child_buttons:
                self.pronoun_template["conju"] = int(
                    event.ui_element.text.replace("windows.conju", "")
                )
                self.dropdowns["conju"].parent_button.set_text(event.ui_element.text)
                self.update_display()
            elif event.ui_element in self.dropdowns["gender"].child_buttons:
                self.pronoun_template["gender"] = int(
                    event.ui_element.text.replace("windows.gender", "")
                )
                self.dropdowns["gender"].parent_button.set_text(event.ui_element.text)
                self.update_display()
            elif event.ui_element == self.buttons["save_pronouns"]:
                add_custom_pronouns(self.pronoun_template)
                self.pronoun_added.show()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                focused_box = [key for key, box in self.boxes.items() if box.is_focused]
                if not focused_box:
                    [box.unfocus() for box in self.boxes.values()]
                    return super().process_event(event)
                key = focused_box[0]
                boxlist = list(self.boxes)
                if event.mod & pygame.KMOD_SHIFT:
                    try:
                        idx = boxlist[boxlist.index(key) - 1]
                    except IndexError:
                        idx = boxlist[-1]
                else:
                    try:
                        idx = boxlist[boxlist.index(key) + 1]
                    except IndexError:
                        idx = boxlist[0]

                self.boxes[key].unfocus()
                self.boxes[idx].focus()
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            self.update_display()

        return super().process_event(event)
