from typing import Optional

import pygame
import pygame_gui

from scripts.cat.cats import create_option_preview_cat, Cat
from scripts.cat.pelts import Pelt
from scripts.game_structure import constants
from scripts.game_structure.editor_elements import (
    EditorTextEntryLine,
    EditorDropDownSelection,
    EditorDivider,
    EditorLock,
)
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
    UISurfaceImageButton,
    UIScrollingButtonList,
    UIModifiedImage,
    UICollapsibleContainer,
    UICheckbox,
    UIDropDown,
)
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.utility import (
    ui_scale,
    get_text_box_theme,
    generate_sprite,
    ui_scale_dimensions,
)


class SettingsTab:
    all_camps: dict = constants.LOCATIONS
    """Dict with key as biome and value as camp name."""
    all_seasons: list = [s.casefold() for s in constants.SEASONS]
    """Tuple of all seasons possible."""

    event_types: dict = constants.EVENT_TYPES
    """Dict with key as event type and value as allowed subtypes for that type."""

    basic_tag_list: list = constants.EVENT_TAGS["settings"]
    """List of dicts for all basic event tags. Each dict holds tag name, conflicts, setting, and type required."""

    def __init__(self):
        self.param_locks: dict = {}

        self.editor_container = None
        self.editor_element = None

        self.event_id_element: Optional[EditorTextEntryLine] = None
        self.event_id_info: str = ""
        """Loaded event_id"""

        self.location_element = {}
        self.location_info: list = []
        """Loaded location tags"""

        self.season_element: Optional[EditorDropDownSelection] = None
        self.season_info: list = []
        """Loaded season tags"""

        self.type_element = {}
        self.type_info: list = ["death"]
        """Loaded type, kept in a list for ease of use with it's dropdown, but there should only ever be one type"""

        self.sub_element = {}
        self.sub_info: list = []
        """Loaded subtypes"""

        self.tag_element = {}
        self.basic_tag_checkbox = {}
        self.rank_tag_checkbox = {}
        self.tag_info: list = []
        """Loaded tags"""

        self.frequency_element: Optional[EditorTextEntryLine] = None
        self.frequency_info: int = 4
        """Loaded frequency"""

        self.acc_element = {}
        self.acc_button = {}
        self.acc_info: list = []
        """Loaded accessory tags"""
        self.acc_categories = Pelt.acc_categories
        self.open_category: str = ""
        """Currently open acc category (wild, collar, ect.)"""

    def handle_events(self, event):
        # CHANGE LOCATION LIST
        if event.ui_element in self.location_element.values():
            biome_list = constants.BIOME_TYPES
            for biome in biome_list:
                if event.ui_element == self.location_element[biome]:
                    self.update_location_info(biome=biome)
                    break
            for camp in [camp for biome in self.all_camps.values() for camp in biome]:
                if event.ui_element == self.location_element.get(camp):
                    self.update_location_info(camp=camp)
                    break

        # CHANGE BASIC TAGS
        elif event.ui_element in self.basic_tag_checkbox.values():
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
                            conflict_index = self.basic_tag_list.index(conflict_info)
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

        # CHANGE RANK TAGS
        elif event.ui_element in self.rank_tag_checkbox.values():
            event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
            self.update_tag_info()

        # CHANGE ACC CATEGORY
        # individual accs
        elif (
            self.acc_element.get("list")
            and event.ui_element in self.acc_element["list"].buttons.values()
        ):
            for acc, button in self.acc_element["list"].buttons.items():
                if event.ui_element != button:
                    continue
                if acc in self.acc_info:
                    self.acc_info.remove(acc)
                else:
                    self.acc_info.append(acc)
                break
            self.update_acc_info()
        # greater categories
        elif event.ui_element in self.acc_element.values():
            for group, button in self.acc_element.items():
                if event.ui_element != button:
                    continue
                if group != self.open_category:
                    self.open_category = group
                    self.update_acc_list()
                    if group not in self.acc_info:
                        self.acc_info.append(group)
                        self.replace_accs_with_group(group)
                else:
                    if group in self.acc_info:
                        self.acc_info.remove(group)
                        self.open_category = None
                        self.update_acc_list()
                    else:
                        self.replace_accs_with_group(group)
                break
            self.update_acc_info()

    def handle_settings_on_use(self):
        # CHANGE ID
        if self.event_id_element.changed:
            self.event_id_info = self.event_id_element.info

        # CHANGE WEIGHT
        if self.frequency_element.changed:
            self.frequency_info = int(self.frequency_element.info)

        # CHANGE TYPE
        if (
            self.type_element.get("type_dropdown")
            and self.type_element["type_dropdown"].selected_list != self.type_info
        ):
            new_type = self.type_element["type_dropdown"].selected_list[0]
            self.type_element["type_dropdown"].parent_button.set_text(new_type)
            self.type_info = [new_type]
            self.sub_info.clear()
            self.update_sub_info()
            self.update_sub_buttons(self.event_types.get(new_type))
            self.update_basic_checkboxes()
        # CHANGE SUBTYPES
        if (
            self.type_element.get("subtype_dropdown")
            and self.type_element["subtype_dropdown"].selected_list != self.sub_info
        ):
            self.sub_info = self.type_element["subtype_dropdown"].selected_list.copy()
            self.update_sub_info()
        # CHANGE SEASONS
        if self.season_element.changed:
            self.season_info = self.season_element.info
            self.season_element.displayed_info = (
                self.season_info if self.season_info else "['any']"
            )

    def replace_accs_with_group(self, group):
        for category_name, accs in self.acc_categories.items():
            if group == category_name:
                for acc in set(self.acc_info).intersection(set(accs)):
                    self.acc_info.remove(acc)
                break

        if group not in self.acc_info:
            self.acc_info.append(group)

    def update_acc_info(self):
        if self.acc_info:
            for (
                category_name,
                accs,
            ) in self.acc_categories.items():
                if category_name in self.acc_info and set(self.acc_info).intersection(
                    set(accs)
                ):
                    self.acc_info.remove(category_name)
                    break
            self.acc_element["display"].set_text(f"chosen accessories: {self.acc_info}")
        else:
            self.acc_element["display"].set_text(f"chosen accessories: []")

        self.editor_container.on_contained_elements_changed(self.acc_element["display"])

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

    def update_location_info(self, biome=None, camp=None):
        if biome:
            biome = biome.casefold()
            present = False
            for location in self.location_info:
                if biome in location:
                    present = True
                    break
            if not present:
                self.location_info.append(biome)
                self.update_camp_list(biome.capitalize())

            else:
                for location in self.location_info:
                    if biome in location:
                        self.location_info.remove(location)
                        self.update_camp_list(None)
                        break

        if camp:
            present = True
            parent_biome = None
            camp_index = 0
            old_location_tag = None
            new_string = None

            for camp_biome in self.all_camps.keys():
                if camp in self.all_camps[camp_biome]:
                    parent_biome = camp_biome
                    camp_index = self.all_camps[camp_biome].index(camp) + 1
                    break

            for location in self.location_info:
                if parent_biome.casefold() in location:
                    if f"camp{camp_index}" in location:
                        break
                    else:
                        new_string = f"{location}_camp{camp_index}"
                        selected_camps = [
                            camp for camp in new_string.split("_") if "camp" in camp
                        ]
                        available_camps = len(self.all_camps[parent_biome])
                        if len(selected_camps) == available_camps:
                            new_string = f"{parent_biome.casefold()}"
                        present = False
                        old_location_tag = location
                        break
            if not present:
                self.location_info.remove(old_location_tag)
                self.location_info.append(new_string.casefold())
            else:
                for location in self.location_info:
                    if parent_biome.casefold() in location:
                        old_location_tag = location
                        new_string = location.replace(f"_camp{camp_index}", "")
                        break
                self.location_info.remove(old_location_tag)
                self.location_info.append(new_string)

        self.location_element["display"].set_text(
            (
                f"chosen location: {str(self.location_info)}"
                if self.location_info
                else "chosen location: ['any']"
            )
        )
        self.editor_container.on_contained_elements_changed(
            self.location_element["display"]
        )

    def update_sub_info(self):
        if "accessory" not in self.sub_info:
            for group in self.acc_categories.keys():
                self.acc_element[group].disable()
                if self.acc_element.get("list"):
                    self.acc_element["list"].kill()
                self.acc_info.clear()
                self.update_acc_info()

        if self.sub_info:
            if "accessory" in self.sub_info:
                for group in self.acc_categories.keys():
                    self.acc_element[group].enable()

            self.type_element["display"].set_text(f"chosen subtypes: {self.sub_info}")
        else:
            self.type_element["display"].set_text("chosen subtypes: []")

    # SETTINGS EDITOR
    def generate_settings_tab(self, editor_container, editor_element):
        self.editor_container = editor_container
        self.editor_element = editor_element
        # EVENT ID
        self.create_event_id_editor()
        # LOCATION
        self.create_location_editor()
        # SEASON
        self.create_season_editor()
        # TYPE AND SUBTYPES
        self.create_type_editor()
        # TAGS
        self.create_tag_editor()
        # WEIGHT
        self.create_frequency_editor()
        # ACC
        self.create_acc_editor()

    def create_acc_editor(self):
        self.acc_element["text"] = UITextBoxTweaked(
            "screens.event_edit.acc_info",
            ui_scale(pygame.Rect((0, 15), (450, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.frequency_element.bottom_element},
        )
        prev_element = None
        for group in self.acc_categories.keys():
            self.acc_element[group] = UISurfaceImageButton(
                ui_scale(pygame.Rect((40, 15), (150, 30))),
                group,
                get_button_dict(ButtonStyles.DROPDOWN, (150, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.acc_element["text"]
                    )
                },
            )
            prev_element = self.acc_element[group]
            if "accessory" not in self.sub_info:
                self.acc_element[group].disable()

        self.acc_element["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((-8, 0), (210, 250))),
            get_box(BoxStyles.FRAME, (210, 250)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["text"],
                "left_target": prev_element,
            },
        )

        self.acc_element["display"] = UITextBoxTweaked(
            f"chosen accessories: {self.acc_info}",
            ui_scale(pygame.Rect((10, 10), (380, 70))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["frame"],
            },
            allow_split_dashes=False,
        )

        self.acc_element["lock"] = EditorLock(
            name="acc",
            position=(10, 10),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["frame"],
                "left_target": self.acc_element["display"],
            },
        )
        self.param_locks["tag"] = self.acc_element["lock"].locked

    def update_acc_list(self):
        # kill old buttons
        if self.acc_element.get("list"):
            self.acc_element["list"].kill()

        if not self.open_category:
            # if no category, we kill buttons and return
            return

        category = None
        for category_name, accs in self.acc_categories.items():
            if self.open_category == category_name:
                category = accs
                break

        self.acc_element["list"] = UIScrollingButtonList(
            ui_scale(pygame.Rect((2, 10), (196, 230))),
            item_list=category,
            button_dimensions=(190, 30),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["text"],
                "left_target": self.acc_element["WILD"],
            },
            starting_selection=self.acc_info,
        )
        if not self.acc_element.get("preview"):
            self.acc_element["preview"] = UIModifiedImage(
                ui_scale(pygame.Rect((80, 0), (100, 100))),
                image_surface=self.get_acc_example(
                    acc=self.acc_info[0] if self.acc_info else category[0]
                ),
                manager=MANAGER,
                container=self.editor_container,
                anchors={
                    "top_target": self.acc_element[list(self.acc_categories.keys())[-1]]
                },
            )

    @staticmethod
    def get_acc_example(acc):
        """
        Returns the example sprite image for the given acc.
        """
        return pygame.transform.scale(
            generate_sprite(create_option_preview_cat(acc=acc)),
            ui_scale_dimensions((100, 100)),
        )

    def create_frequency_editor(self):
        self.frequency_element = EditorTextEntryLine(
            position=(0, 15),
            description=f"<b>frequency:</b>",
            entry_length=50,
            initial_entry_text=str(self.frequency_info) if self.frequency_info else "",
            container=self.editor_container,
            manager=MANAGER,
            anchors={"top_target": self.editor_element["tag"]},
            lock=True,
            lock_name="frequency",
        )
        if self.param_locks.get("frequency"):
            self.frequency_element.lock.locked = True

        self.editor_element["weight"] = EditorDivider(
            top_anchor=self.frequency_element.bottom_element,
            container=self.editor_container,
            manager=MANAGER,
        )

    def create_tag_editor(self):
        self.tag_element["collapse_container"] = UICollapsibleContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            top_button_oriented_left=False,
            title_text="<b>tags:</b>",
            bottom_button=False,
            resize_right=False,
            scrolling_container_to_reset=self.editor_container,
            manager=MANAGER,
            container=self.editor_container,
            title_object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            anchors={"top_target": self.type_element["display"]},
        )
        self.tag_element[
            "basic_checkbox_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((48, 0), (0, 0))),
            container=self.tag_element["collapse_container"],
            manager=MANAGER,
            anchors={"top_target": self.tag_element["collapse_container"].top_button},
        )

        self.update_basic_checkboxes()

        self.rank_tag_checkbox["text"] = UITextBoxTweaked(
            "screens.event_edit.rank_tags",
            ui_scale(pygame.Rect((10, 10), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.tag_element["collapse_container"],
            anchors={
                "top_target": self.tag_element["basic_checkbox_container"],
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
                position=(400, 10),
                container=self.tag_element["collapse_container"],
                manager=MANAGER,
                check=setting,
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.rank_tag_checkbox["text"]
                    ),
                },
            )

            check_box_rect = pygame.Rect((0, 10), (350, -1))
            check_box_rect.right = -70
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
                container=self.tag_element["collapse_container"],
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.rank_tag_checkbox["text"]
                    ),
                    "right": "right",
                },
            )

            prev_element = self.rank_tag_checkbox[f"{rank}_text"]

        self.tag_element["display"] = UITextBoxTweaked(
            f"chosen tags: {self.tag_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.tag_element["collapse_container"],
            },
            allow_split_dashes=False,
        )

        self.tag_element["collapse_container"].close()

        self.tag_element["lock"] = EditorLock(
            name="tag",
            position=(10, 10),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.tag_element["collapse_container"],
                "left_target": self.tag_element["display"],
            },
        )
        self.param_locks["tag"] = self.tag_element["lock"].locked

        self.editor_element["tag"] = EditorDivider(
            top_anchor=self.tag_element["display"],
            container=self.editor_container,
            manager=MANAGER,
        )

    def update_basic_checkboxes(self):
        prev_element = None

        # clear old elements
        if self.basic_tag_checkbox:
            for info in self.basic_tag_list:
                if self.basic_tag_checkbox.get(f"{info['tag']}_text"):
                    self.basic_tag_checkbox[f"{info['tag']}_text"].kill()
                if self.basic_tag_checkbox.get(info["tag"]):
                    self.basic_tag_checkbox[info["tag"]].kill()
            self.basic_tag_checkbox.clear()

        # make new ones!
        for info in self.basic_tag_list:
            if info["tag"] in self.tag_info and not info["setting"]:
                info["setting"] = True
            # first reset the values
            if info.get("required_type") and info["required_type"] != self.type_info[0]:
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
                container=self.tag_element["basic_checkbox_container"],
                anchors={
                    "top_target": prev_element,
                }
                if prev_element
                else None,
            )

            self.basic_tag_checkbox[info["tag"]] = UICheckbox(
                position=(350, 10),
                container=self.tag_element["basic_checkbox_container"],
                manager=MANAGER,
                check=info["setting"],
                anchors={"top_target": prev_element} if prev_element else None,
            )

            prev_element = self.basic_tag_checkbox[f"{info['tag']}_text"]

        self.update_tag_info()

    def create_type_editor(self):
        self.type_element["text"] = UITextBoxTweaked(
            "<b>sub/type:</b>",
            ui_scale(pygame.Rect((0, 14), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.season_element.bottom_element},
        )
        if not self.type_info:
            self.type_info = ["death"]

        self.type_element["type_dropdown"] = UIDropDown(
            pygame.Rect((50, 10), (150, 30)),
            parent_text=self.type_info[0],
            item_list=list(self.event_types.keys()),
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["season"],
            },
            starting_height=3,
            manager=MANAGER,
            child_trigger_close=True,
            starting_selection=self.type_info,
        )

        self.update_sub_buttons(self.event_types[self.type_info[0]])

        self.type_element["display"] = UITextBoxTweaked(
            f"chosen subtypes: {self.sub_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.type_element["text"],
            },
            allow_split_dashes=False,
        )

        self.type_element["lock"] = EditorLock(
            name="subtypes",
            position=(10, 10),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.type_element["text"],
                "left_target": self.type_element["display"],
            },
        )
        self.param_locks["subtypes"] = self.type_element["lock"].locked

        self.editor_element["type"] = EditorDivider(
            top_anchor=self.type_element["display"],
            container=self.editor_container,
            manager=MANAGER,
        )

    def update_sub_buttons(self, type_list):
        if self.type_element.get("subtype_dropdown"):
            self.type_element["subtype_dropdown"].kill()

        self.type_element["subtype_dropdown"] = UIDropDown(
            pygame.Rect((0, 10), (150, 30)),
            parent_text="pick subtypes",
            item_list=type_list,
            manager=MANAGER,
            container=self.editor_container,
            multiple_choice=True,
            disable_selection=False,
            child_trigger_close=False,
            starting_height=3,
            anchors={
                "left_target": self.type_element["type_dropdown"],
                "top_target": self.editor_element["season"],
            },
            starting_selection=self.sub_info,
        )

    def create_season_editor(self):
        self.season_element = EditorDropDownSelection(
            position=(0, 10),
            anchors={"top_target": self.location_element["display"]},
            container=self.editor_container,
            manager=MANAGER,
            description="screens.event_edit.season_info",
            item_list=self.all_seasons,
            dropdown_parent_text="seasons",
            display_text="seasons: ",
            starting_selection=self.season_info,
            multiple_choice=True,
            lock_name="season",
            lock=True,
        )
        if self.param_locks.get("season"):
            self.season_element.lock.locked = True

        self.editor_element["season"] = EditorDivider(
            top_anchor=self.season_element.bottom_element,
            container=self.editor_container,
            manager=MANAGER,
        )

    def create_location_editor(self):
        self.location_element["text"] = UITextBoxTweaked(
            "screens.event_edit.location_info",
            ui_scale(pygame.Rect((0, 10), (450, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["event_id"]},
        )
        biome_list = constants.BIOME_TYPES
        prev_element = None
        for biome in biome_list:
            y_pos = 10 if not prev_element else -2
            self.location_element[biome] = UISurfaceImageButton(
                ui_scale(pygame.Rect((10, y_pos), (150, 30))),
                biome,
                get_button_dict(ButtonStyles.DROPDOWN, (150, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "top_target": (
                        self.location_element["text"]
                        if not prev_element
                        else prev_element
                    ),
                },
            )
            prev_element = self.location_element[biome]

        self.location_element["display"] = UITextBoxTweaked(
            f"chosen location: {self.location_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.location_element[biome_list[-1]]},
            allow_split_dashes=False,
        )

        self.location_element["lock"] = EditorLock(
            name="location",
            position=(10, 10),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.location_element[biome_list[-1]],
                "left_target": self.location_element["display"],
            },
        )
        self.param_locks["location"] = self.location_element["lock"].locked

        self.editor_element["location"] = EditorDivider(
            top_anchor=self.location_element["display"],
            container=self.editor_container,
            manager=MANAGER,
        )

    def update_camp_list(self, chosen_biome):
        for biome in self.all_camps:
            for camp in self.all_camps[biome]:
                if self.location_element.get(camp):
                    self.location_element[camp].kill()

        camp_list = self.all_camps.get(chosen_biome)

        if not camp_list:
            return

        prev_element = None
        for camp in camp_list:
            y_pos = 10 if not prev_element else -2
            self.location_element[camp] = UISurfaceImageButton(
                ui_scale(pygame.Rect((20, y_pos), (150, 30))),
                camp,
                get_button_dict(ButtonStyles.DROPDOWN, (150, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "left_target": self.location_element[chosen_biome],
                    "top_target": (
                        self.location_element["text"]
                        if not prev_element
                        else prev_element
                    ),
                },
            )
            prev_element = self.location_element[camp]

    def create_event_id_editor(self):
        self.event_id_element = EditorTextEntryLine(
            position=(0, 13),
            description=f"<b>event_id:</b>",
            entry_length=230,
            initial_entry_text=self.event_id_info if self.event_id_info else "",
            container=self.editor_container,
            manager=MANAGER,
        )

        self.editor_element["event_id"] = EditorDivider(
            top_anchor=self.event_id_element.bottom_element,
            container=self.editor_container,
            manager=MANAGER,
        )
