import math
from fractions import Fraction

import i18n
import pygame
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.clan_package.settings import (
    get_clan_setting,
    switch_clan_setting,
)
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIImageButton,
    UICheckbox,
    UITextBoxTweaked,
    UICatListDisplay,
    UIModifiedScrollingContainer,
)
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import (
    ui_scale,
    ui_scale_offset,
    ui_scale_value,
    get_text_box_theme,
)


class EditorSettingTags(GameWindow):
    def __init__(
        self,
        tag_info: list,
        basic_tag_list: list,
        type_info: list,
        tag_element: dict,
        editor_container,
    ):
        super().__init__(
            ui_scale(pygame.Rect((175, 100), (450, 500))),
            window_display_title="Editor Setting Tags",
        )

        self.rank_tag_checkbox = {}
        self.basic_tag_checkbox = {}
        self.tag_info = tag_info
        self.basic_tag_list = basic_tag_list
        self.tag_element = tag_element
        self.editor_container = editor_container

        self.container = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((0, 30), (442, 460))),
            container=self,
            manager=MANAGER,
            allow_scroll_y=True,
        )

        self.basic_container = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((20, 0), (0, 0))),
            container=self.container,
            manager=MANAGER,
        )

        prev_element = None
        for info in self.basic_tag_list:
            if info["tag"] in self.tag_info and not info["setting"]:
                info["setting"] = True
            # first reset the values
            if info.get("required_type") and info["required_type"] != type_info[0]:
                # this is to change the setting to false
                index = self.basic_tag_list.index(info)
                self.basic_tag_list[index] = {
                    "tag": info["tag"],
                    "setting": False,
                    "required_type": info["required_type"],
                    "conflict": info["conflict"],
                }
                continue

            self.basic_tag_checkbox[f"{info['tag']}_text"] = UITextBoxTweaked(
                f"screens.event_edit.{info['tag']}",
                ui_scale(pygame.Rect((0, 10), (350, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
                line_spacing=1,
                manager=MANAGER,
                container=self.basic_container,
                anchors={
                    "top_target": prev_element,
                }
                if prev_element
                else None,
            )

            self.basic_tag_checkbox[info["tag"]] = UICheckbox(
                position=(350, 10),
                container=self.basic_container,
                manager=MANAGER,
                check=info["setting"],
                anchors={"top_target": prev_element} if prev_element else None,
            )

            prev_element = self.basic_tag_checkbox[f"{info['tag']}_text"]

        self.rank_tag_checkbox["text"] = UITextBoxTweaked(
            "screens.event_edit.rank_tags",
            ui_scale(pygame.Rect((20, 10), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.container,
            anchors={
                "top_target": self.basic_container,
            },
        )
        prev_element = None
        rank_list = Cat.rank_sort_order.copy()
        rank_list.append("apps")
        for rank in rank_list:
            if f"clan:{rank}" in self.tag_info:
                setting = True
            else:
                setting = False

            self.rank_tag_checkbox[rank] = UICheckbox(
                position=(370, 10),
                container=self.container,
                manager=MANAGER,
                check=setting,
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.rank_tag_checkbox["text"]
                    ),
                },
            )

            check_box_rect = pygame.Rect((0, 10), (350, -1))
            check_box_rect.right = -90
            if rank == "apps":
                rank_string = f"two of any apprentice type"
            else:
                rank_string = (
                    f"two {rank}s" if rank not in ("deputy", "leader") else rank
                )
            self.rank_tag_checkbox[f"{rank}_text"] = UITextBoxTweaked(
                rank_string,
                ui_scale(check_box_rect),
                object_id="#text_box_30_horizright_pad_10_10",
                line_spacing=1,
                manager=MANAGER,
                container=self.container,
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.rank_tag_checkbox["text"]
                    ),
                    "right": "right",
                },
            )

            prev_element = self.rank_tag_checkbox[f"{rank}_text"]

    def update_tag_info(self):
        for info in self.basic_tag_list:
            if info["tag"] not in self.tag_info and info["setting"]:
                self.tag_info.append(info["tag"])
            elif info["tag"] in self.tag_info and not info["setting"]:
                self.tag_info.remove(info["tag"])

        for rank, box in self.rank_tag_checkbox.items():
            if "text" in rank:
                continue
            tag = f"clan:{rank}"
            if box.checked and tag not in self.tag_info:
                self.tag_info.append(tag)
            elif not box.checked and tag in self.tag_info:
                self.tag_info.remove(tag)

        if self.tag_element.get("display"):
            self.tag_element["display"].set_text(f"chosen tags: {self.tag_info}")
            self.editor_container.on_contained_elements_changed(
                self.tag_element["display"]
            )

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.basic_tag_checkbox.values():
                event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
                for info in self.basic_tag_list:
                    if event.ui_element == self.basic_tag_checkbox.get(info["tag"]):
                        index = self.basic_tag_list.index(info)
                        self.basic_tag_list[index] = {
                            "tag": info["tag"],
                            "setting": False if info["setting"] else True,
                            "required_type": info["required_type"],
                            "conflict": info["conflict"],
                        }

                        # flip the setting of any conflicting tags
                        if info["conflict"]:
                            for tag in info["conflict"]:
                                conflict_info = [
                                    block
                                    for block in self.basic_tag_list
                                    if tag == block["tag"]
                                ][0]
                                conflict_index = self.basic_tag_list.index(
                                    conflict_info
                                )
                                if not info[
                                    "setting"
                                ]:  # unchecks if conflicted setting is checked
                                    self.basic_tag_checkbox[tag].uncheck()
                                self.basic_tag_list[conflict_index] = {
                                    "tag": conflict_info["tag"],
                                    "setting": False,
                                    "required_type": conflict_info["required_type"],
                                    "conflict": conflict_info["conflict"],
                                }

                        self.update_tag_info()
                        break

            elif event.ui_element in self.rank_tag_checkbox.values():
                event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
                self.update_tag_info()

        return super().process_event(event)
