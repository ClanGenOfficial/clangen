import pygame
import pygame_gui

from scripts.game_structure.game.switches import (
    switch_get_value,
    Switch,
    switch_append_list_value,
    switch_remove_list_value,
)
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UIModifiedScrollingContainer,
)
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class SymbolFilterWindow(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((250, 125), (300, 450))),
        )

        self.possible_tags = {
            "plant": ["flower", "tree", "leaf", "other plant", "fruit"],
            "animal": ["cat", "fish", "bird", "mammal", "bug", "other animal"],
            "element": ["water", "fire", "earth", "air", "light"],
            "location": [],
            "descriptor": [],
            "miscellaneous": [],
        }

        self.filter_title = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((5, 5), (-1, -1))),
            text="windows.symbol_filter_title",
            object_id="#text_box_40",
            container=self,
        )
        self.filter_container = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((5, 45), (285, 400))),
            manager=MANAGER,
            starting_height=1,
            allow_scroll_x=False,
            allow_scroll_y=True,
            container=self,
        )
        self.checkbox = {}
        self.checkbox_text = {}
        x_pos = 15
        y_pos = 20

        for tag, subtags in self.possible_tags.items():
            self.checkbox[tag] = UIImageButton(
                ui_scale(pygame.Rect((x_pos, y_pos), (34, 34))),
                "",
                object_id="@checked_checkbox",
                container=self.filter_container,
                starting_height=2,
                manager=MANAGER,
            )
            if tag in switch_get_value(Switch.disallowed_symbol_tags):
                self.checkbox[tag].change_object_id("@unchecked_checkbox")

            self.checkbox_text[tag] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((6, y_pos + 4), (-1, -1))),
                text=f"windows.{tag}",
                container=self.filter_container,
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                anchors={"left_target": self.checkbox[tag]},
            )
            y_pos += 35
            if subtags:
                for s_tag in subtags:
                    self.checkbox[s_tag] = UIImageButton(
                        ui_scale(pygame.Rect((x_pos + 35, y_pos), (34, 34))),
                        "",
                        object_id="@checked_checkbox",
                        container=self.filter_container,
                        starting_height=2,
                        manager=MANAGER,
                    )

                    if tag in switch_get_value(Switch.disallowed_symbol_tags):
                        self.checkbox[s_tag].disable()
                    if s_tag in switch_get_value(Switch.disallowed_symbol_tags):
                        self.checkbox[s_tag].change_object_id("@unchecked_checkbox")

                    self.checkbox_text[s_tag] = pygame_gui.elements.UILabel(
                        ui_scale(pygame.Rect((6, y_pos + 4), (-1, -1))),
                        text=f"windows.{s_tag}",
                        container=self.filter_container,
                        object_id="#text_box_30_horizleft",
                        manager=MANAGER,
                        anchors={"left_target": self.checkbox[s_tag]},
                    )
                    y_pos += 30
                y_pos += 5

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.checkbox.values():
                for tag, element in self.checkbox.items():
                    if element == event.ui_element:
                        # find out what state the checkbox was in when clicked
                        object_ids = element.get_object_ids()
                        # handle checked checkboxes becoming unchecked
                        if "@checked_checkbox" in object_ids:
                            self.checkbox[tag].change_object_id("@unchecked_checkbox")
                            # add tag to disallowed list
                            if tag not in switch_get_value(
                                Switch.disallowed_symbol_tags
                            ):
                                switch_append_list_value(
                                    Switch.disallowed_symbol_tags, tag
                                )
                            # if tag had subtags, also add those subtags
                            if tag in self.possible_tags:
                                for s_tag in self.possible_tags[tag]:
                                    self.checkbox[s_tag].change_object_id(
                                        "@unchecked_checkbox"
                                    )
                                    self.checkbox[s_tag].disable()
                                    if s_tag not in switch_get_value(
                                        Switch.disallowed_symbol_tags
                                    ):
                                        switch_append_list_value(
                                            Switch.disallowed_symbol_tags, tag
                                        )

                        # handle unchecked checkboxes becoming checked
                        elif "@unchecked_checkbox" in object_ids:
                            self.checkbox[tag].change_object_id("@checked_checkbox")
                            # remove tag from disallowed list
                            if tag in switch_get_value(Switch.disallowed_symbol_tags):
                                switch_remove_list_value(
                                    Switch.disallowed_symbol_tags, tag
                                )
                            # if tag had subtags, also add those subtags
                            if tag in self.possible_tags:
                                for s_tag in self.possible_tags[tag]:
                                    self.checkbox[s_tag].change_object_id(
                                        "@checked_checkbox"
                                    )
                                    self.checkbox[s_tag].enable()
                                    if tag in switch_get_value(
                                        Switch.disallowed_symbol_tags
                                    ):
                                        switch_remove_list_value(
                                            Switch.disallowed_symbol_tags, tag
                                        )
        return super().process_event(event)
