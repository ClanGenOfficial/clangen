from random import randrange, choice
from typing import Optional

import i18n
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIContainer

from scripts.cat.cats import create_cat, Cat, create_example_cats
from scripts.cat.enums import CatRank
from scripts.cat.sprites.load_sprites import sprites
from scripts.game_structure import image_cache, constants
from scripts.game_structure.game import Switch, switch_get_value
from scripts.game_structure.game.settings import game_setting_set
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme

from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase


class ChooseCatsScreen(MakeClanScreenBase):
    path = "resources/images/pick_clan_screen"
    ui_images = {
        "name_frame": pygame.image.load(f"{path}/name_frame.png").convert_alpha(),
        "clan_blank": pygame.image.load(f"{path}/clan_blank.png").convert_alpha(),
        "leader_empty": pygame.image.load(f"{path}/leader_empty.png").convert_alpha(),
        "leader_chosen": pygame.image.load(f"{path}/leader_chosen.png").convert_alpha(),
        "deputy_empty": pygame.image.load(f"{path}/deputy_empty.png").convert_alpha(),
        "deputy_chosen": pygame.image.load(f"{path}/deputy_chosen.png").convert_alpha(),
        "med_empty": pygame.image.load(f"{path}/med_empty.png").convert_alpha(),
        "med_chosen": pygame.image.load(f"{path}/med_chosen.png").convert_alpha(),
        "1_empty": pygame.image.load(f"{path}/first_empty.png").convert_alpha(),
        "1_chosen": pygame.image.load(f"{path}/first_chosen.png").convert_alpha(),
        "2_empty": pygame.image.load(f"{path}/second_empty.png").convert_alpha(),
        "2_chosen": pygame.image.load(f"{path}/second_chosen.png").convert_alpha(),
        "3_empty": pygame.image.load(f"{path}/third_empty.png").convert_alpha(),
        "3_chosen": pygame.image.load(f"{path}/third_chosen.png").convert_alpha(),
        "4_empty": pygame.image.load(f"{path}/fourth_empty.png").convert_alpha(),
        "4_chosen": pygame.image.load(f"{path}/fourth_chosen.png").convert_alpha(),
        "clan_glow": pygame.image.load(f"{path}/clan_glow.png").convert_alpha(),
    }

    def __init__(self, name="choose_cats_screen"):
        super().__init__(name)

        self.step = "leader"

        self.rolls_left = constants.CONFIG["clan_creation"]["rerolls"]
        self.selected_cat: Optional[Cat] = None

    def screen_switches(self):
        super().screen_switches()

        # move the step buttons up
        self.elements["previous_step"].set_relative_position(
            ui_scale_dimensions((253, 400))
        )
        self.elements["next_step"].set_relative_position(ui_scale_dimensions((0, 400)))

        # create background pizzazz
        self.elements["background"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 440), (800, 260))),
            pygame.transform.scale(
                self.ui_images["clan_blank"],
                ui_scale_dimensions((800, 260)),
            ),
            manager=MANAGER,
        )
        self.elements["background"].disable()

        self.elements["title"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.leader_title",
            ui_scale(pygame.Rect((0, 610), (800, 90))),
            object_id="@clangen_32",
            anchors={"centerx": "centerx"},
        )
        self.clan_name_header()

        # Roll_buttons
        self.elements["roll_container"] = UIContainer(
            ui_scale(pygame.Rect((155, 225), (50, 150))),
            manager=MANAGER,
        )
        self.elements["roll1"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 0), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            container=self.elements["roll_container"],
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.elements["roll2"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 10), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            container=self.elements["roll_container"],
            object_id="@buttonstyles_icon",
            anchors={"top_target": self.elements["roll1"]},
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.elements["roll3"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 10), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            container=self.elements["roll_container"],
            object_id="@buttonstyles_icon",
            anchors={"top_target": self.elements["roll2"]},
            manager=MANAGER,
            sound_id="dice_roll",
        )

        # set to infinite or higher than typical
        if self.rolls_left == -1 or constants.CONFIG["clan_creation"]["rerolls"] > 3:
            # hide top and bottom so only center remains
            self.elements["roll1"].hide()
            self.elements["roll3"].hide()
        # add a counter for this one
        if constants.CONFIG["clan_creation"]["rerolls"]:
            self.elements["reroll_count"] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 0), (30, 30))),
                str(self.rolls_left),
                container=self.elements["roll_container"],
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                anchors={"top_target": self.elements["roll2"]},
                manager=MANAGER,
            )

        if constants.CONFIG["clan_creation"]["rerolls"] == 3:
            if self.rolls_left <= 2:
                self.elements["roll1"].disable()
            if self.rolls_left <= 1:
                self.elements["roll2"].disable()
            if self.rolls_left == 0:
                self.elements["roll3"].disable()
            self.elements["reroll_count"].hide()
        else:
            if self.rolls_left == 0:
                self.elements["roll2"].disable()
            elif self.rolls_left == -1:
                self.elements["reroll_count"].hide()

        self.create_cat_info()

        self.elements["select_cat"] = UIImageButton(
            ui_scale(pygame.Rect((234, 348), (332, 52))),
            "screens.make_clan.choose_leader",
            object_id="#nine_lives_button",
            starting_height=2,
            visible=False,
            manager=MANAGER,
            text_kwargs={"m_c": self.selected_cat},
        )

        # Error message, to appear if you can't choose that cat.
        self.elements["error_message"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.error_too_young",
            ui_scale(pygame.Rect((150, 353), (500, 55))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_red"),
            visible=False,
            manager=MANAGER,
        )

        self.refresh_cat_images_and_info()
        self.update_head_display()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in (
                self.elements["roll1"],
                self.elements["roll2"],
                self.elements["roll3"],
            ):
                self.elements["select_cat"].kill()
                # create new cats
                switch_set_value(Switch.possible_cats, create_example_cats())
                self.selected_cat = None

                if self.elements["error_message"]:
                    self.elements["error_message"].hide()

                self.refresh_cat_images_and_info()  # Refresh all the images.
                self.rolls_left -= 1
                if constants.CONFIG["clan_creation"]["rerolls"] == 3:
                    event.ui_element.disable()
                else:
                    self.elements["reroll_count"].set_text(str(self.rolls_left))
                    if self.rolls_left == 0:
                        event.ui_element.disable()

            elif event.ui_element in (
                self.elements["cat" + str(u)] for u in range(0, 12)
            ):
                self.elements["roll_container"].hide()

                self.selected_cat = event.ui_element.return_cat_object()
                if self.selected_cat in self.clan_info.get("starting_members", []):
                    self.clan_info["starting_members"].remove(self.selected_cat)
                elif self.selected_cat == self.clan_info.get("leader"):
                    self.clan_info["leader"] = None
                elif self.selected_cat == self.clan_info.get("deputy"):
                    self.clan_info["deputy"] = None
                elif self.selected_cat == self.clan_info.get("medicine_cat"):
                    self.clan_info["medicine_cat"] = None

                self.refresh_cat_images_and_info(self.selected_cat)
                self.refresh_text_and_buttons()
                self.update_head_display()
                self.refresh_text_and_buttons()

            elif event.ui_element == self.elements["select_cat"]:
                self._assign_cat()
                self.selected_cat = None
                self.update_head_display()
                self.refresh_cat_images_and_info()
                self.refresh_text_and_buttons()

            elif event.ui_element == self.elements["previous_step"]:
                self.change_screen(GameScreen.CHOOSE_NAME)

        return super().handle_event(event)

    def _assign_cat(self):
        cat = self.selected_cat
        if not self.clan_info.get("leader"):
            self.clan_info["leader"] = cat
        elif not self.clan_info.get("deputy"):
            self.clan_info["deputy"] = cat
        elif not self.clan_info.get("medicine_cat"):
            self.clan_info["medicine_cat"] = cat
        else:
            if not self.clan_info.get("starting_members"):
                self.clan_info["starting_members"] = [cat]
            else:
                self.clan_info["starting_members"].append(cat)

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""

        if len(self.clan_info.get("starting_members", [])) == 7:
            self.elements["select_cat"].disable()
        elif not self.selected_cat:
            self.elements["select_cat"].hide()
        # Show the error message if you try to choose a child for leader, deputy, or med cat.
        elif (
            self.selected_cat  # if we have a cat selected
            and (  # and we don't have a leadership role
                not self.clan_info.get("leader")
                or not self.clan_info.get("deputy")
                or not self.clan_info.get("medicine_cat")
            )
            and self.selected_cat.age  # and cat age is in one of these
            in (
                "newborn",
                "kitten",
                "adolescent",
            )
        ):
            self.elements["select_cat"].hide()
            self.elements["error_message"].set_text(
                self.elements["error_message"].html_text,
                text_kwargs={"m_c": self.selected_cat},
            )
            self.elements["error_message"].show()
        else:
            self.elements["select_cat"].show()
            self.elements["error_message"].hide()

            # Change button text for different ranks
            # LEAD
            if not self.clan_info.get("leader"):
                self.elements["select_cat"].kill()
                self.elements["select_cat"] = UIImageButton(
                    ui_scale(pygame.Rect((234, 348), (332, 52))),
                    "screens.make_clan.choose_leader",
                    object_id="#nine_lives_button",
                    starting_height=2,
                    manager=MANAGER,
                    text_kwargs={"m_c": self.selected_cat},
                )
            # DEP
            elif not self.clan_info.get("deputy"):
                self.elements["select_cat"].kill()
                self.elements["select_cat"] = UIImageButton(
                    ui_scale(pygame.Rect((209, 348), (384, 52))),
                    "screens.make_clan.choose_deputy",
                    object_id="#support_leader_button",
                    starting_height=2,
                    manager=MANAGER,
                )
            # MED
            elif not self.clan_info.get("medicine_cat"):
                self.elements["select_cat"].kill()
                self.elements["select_cat"] = UIImageButton(
                    ui_scale(pygame.Rect((260, 342), (306, 58))),
                    i18n.t("screens.make_clan.choose_medcat")
                    + "    ",  # it's necessary for centering...
                    object_id="#aid_clan_button",
                    starting_height=2,
                    manager=MANAGER,
                )
            # NORMIES
            else:
                self.elements["select_cat"].kill()
                self.elements["select_cat"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((353, 360), (95, 30))),
                    "screens.make_clan.recruit",
                    get_button_dict(ButtonStyles.SQUOVAL, (95, 30)),
                    object_id="@buttonstyles_squoval",
                    starting_height=2,
                    manager=MANAGER,
                )

    def clan_name_header(self):
        """
        Creates clan name header
        """
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((292, 100), (216, 50))),
            self.ui_images["name_frame"],
            manager=MANAGER,
        )
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(
            "general.clan",
            ui_scale(pygame.Rect((292, 100), (216, 50))),
            object_id=ObjectID("#text_box_30_horizcenter_vertcenter", "#dark"),
            text_kwargs={"name": self.clan_info["name"]},
            manager=MANAGER,
        )

    def update_head_display(self):
        """
        Updates the cat head display to match the current selection of cats
        """
        # CREATE HEADS
        if not self.elements.get("leader"):
            self.elements["leader"] = UIModifiedImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["leader_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
            )
            self.elements["deputy"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["deputy_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )
            self.elements["med"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["med_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )
            self.elements["1_cat"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["1_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )
            self.elements["2_cat"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["2_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )
            self.elements["3_cat"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["3_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )
            self.elements["4_cat"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["4_empty"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )
            self.elements["clan_glow"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 440), (800, 260))),
                pygame.transform.scale(
                    self.ui_images["clan_glow"],
                    ui_scale_dimensions((800, 260)),
                ),
                manager=MANAGER,
                visible=False,
            )

        # SET TEXT
        if not self.clan_info.get("leader"):
            self.elements["title"].set_text("screens.make_clan.leader_title")
        elif not self.clan_info.get("deputy"):
            self.elements["title"].set_text("screens.make_clan.deputy_title")
        elif not self.clan_info.get("medicine_cat"):
            self.elements["title"].set_text("screens.make_clan.medcat_title")
        else:
            self.elements["title"].set_text("screens.make_clan.recruit_title")

        # TOGGLE HEAD VISIBLE
        cat_heads = [
            "deputy",
            "med",
            "1_cat",
            "2_cat",
            "3_cat",
            "4_cat",
            "clan_glow",
        ]

        for head in cat_heads:
            self.elements[head].hide()

        # TOGGLE EYE LIGHTS
        if self.clan_info.get("leader"):
            self.elements["leader"].set_image(
                pygame.transform.scale(
                    self.ui_images["leader_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            self.elements["deputy"].show()
        else:
            self.elements["leader"].set_image(
                pygame.transform.scale(
                    self.ui_images["leader_empty"],
                    ui_scale_dimensions((800, 260)),
                )
            )

        if self.clan_info.get("deputy"):
            self.elements["deputy"].show()
            self.elements["deputy"].set_image(
                pygame.transform.scale(
                    self.ui_images["deputy_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            if self.clan_info.get("leader"):
                self.elements["med"].show()
        else:
            self.elements["deputy"].set_image(
                pygame.transform.scale(
                    self.ui_images["deputy_empty"],
                    ui_scale_dimensions((800, 260)),
                )
            )

        if self.clan_info.get("medicine_cat"):
            self.elements["med"].show()
            self.elements["med"].set_image(
                pygame.transform.scale(
                    self.ui_images["med_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            if self.clan_info.get("leader") and self.clan_info.get("deputy"):
                self.elements["1_cat"].show()
        else:
            self.elements["med"].set_image(
                pygame.transform.scale(
                    self.ui_images["med_empty"],
                    ui_scale_dimensions((800, 260)),
                )
            )

        for i in range(min(len(self.clan_info.get("starting_members", [])), 4), 5):
            if i == 0:
                continue
            self.elements[f"{i}_cat"].set_image(
                pygame.transform.scale(
                    self.ui_images[f"{i}_empty"],
                    ui_scale_dimensions((800, 260)),
                )
            )

        if len(self.clan_info.get("starting_members", [])) >= 7:
            self.elements["clan_glow"].show()
        elif len(self.clan_info.get("starting_members", [])) >= 4:
            self.elements["4_cat"].show()
            self.elements["4_cat"].set_image(
                pygame.transform.scale(
                    self.ui_images["4_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            self.elements["clan_glow"].hide()
        elif len(self.clan_info.get("starting_members", [])) >= 3:
            self.elements["3_cat"].show()
            self.elements["3_cat"].set_image(
                pygame.transform.scale(
                    self.ui_images["3_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            if (
                self.clan_info.get("leader")
                and self.clan_info.get("deputy")
                and self.clan_info.get("medicine_cat")
            ):
                self.elements["4_cat"].show()
        elif len(self.clan_info.get("starting_members", [])) >= 2:
            self.elements["2_cat"].show()
            self.elements["2_cat"].set_image(
                pygame.transform.scale(
                    self.ui_images["2_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            if (
                self.clan_info.get("leader")
                and self.clan_info.get("deputy")
                and self.clan_info.get("medicine_cat")
            ):
                self.elements["3_cat"].show()
        elif len(self.clan_info.get("starting_members", [])) == 1:
            self.elements["1_cat"].show()
            self.elements["1_cat"].set_image(
                pygame.transform.scale(
                    self.ui_images["1_chosen"],
                    ui_scale_dimensions((800, 260)),
                )
            )
            if (
                self.clan_info.get("leader")
                and self.clan_info.get("deputy")
                and self.clan_info.get("medicine_cat")
            ):
                self.elements["2_cat"].show()
        elif (
            self.clan_info.get("leader")
            and self.clan_info.get("deputy")
            and self.clan_info.get("medicine_cat")
        ):
            self.elements["1_cat"].show()
            self.elements["1_cat"].set_image(
                pygame.transform.scale(
                    self.ui_images["1_empty"],
                    ui_scale_dimensions((800, 260)),
                )
            )

    def create_cat_info(self):
        self.elements["cat_name"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 10), (350, -1))),
            visible=False,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["name_backdrop"],
                "centerx": "centerx",
            },
        )

        # info for chosen cats:
        self.elements["cat_info"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((440, 220), (175, 125))),
            visible=False,
            object_id=get_text_box_theme("#text_box_26_horizcenter"),
            manager=MANAGER,
        )

    def refresh_selected_cat_info(self, selected: Optional[Cat] = None):
        # SELECTED CAT INFO
        if selected is None:
            self.elements["next_step"].disable()
            self.elements["cat_info"].hide()
            self.elements["cat_name"].hide()
            return

        if not self.clan_info.get("leader"):
            self.elements["cat_name"].set_text(
                str(selected.name)
                + " --> "
                + selected.name.get_specsuffix_name(CatRank.LEADER)
            )
        else:
            self.elements["cat_name"].set_text(str(selected.name))

        self.elements["select_cat"].set_text(
            self.elements["select_cat"].text, text_kwargs={"m_c": selected}
        )
        self.elements["cat_name"].show()
        self.elements["cat_info"].set_text(
            selected.get_info_block(make_clan=True), text_kwargs={"m_c": selected}
        )
        self.elements["cat_info"].show()

    def refresh_cat_images_and_info(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats."""

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        possible_cats = switch_get_value(Switch.possible_cats)
        chosen_cats = [
            self.clan_info.get("leader"),
            self.clan_info.get("deputy"),
            self.clan_info.get("medicine_cat"),
        ] + self.clan_info.get("starting_members", [])

        # CAT IMAGES
        selected_cat_index: Optional[int] = None
        # first half
        for u in range(6):
            # kill existing element so we start fresh
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()

            if not self.elements.get("possible1_container"):
                self.elements["possible1_container"] = UIContainer(
                    ui_scale(pygame.Rect((50, 130), (50, 300))),
                    manager=MANAGER,
                )

            if not self.elements.get("chosen1_container"):
                self.elements["chosen1_container"] = UIContainer(
                    ui_scale(pygame.Rect((650, 130), (50, 300))),
                    manager=MANAGER,
                )

            # locate selected cat
            if possible_cats[u] == selected:
                selected_cat_index = u

            # place chosen cat
            elif possible_cats[u] in chosen_cats:
                self._add_to_cat_column(
                    possible_cats[u], u, self.elements["chosen1_container"], u
                )

            # place possible cat
            else:
                self._add_to_cat_column(
                    possible_cats[u], u, self.elements["possible1_container"], u
                )

        # second half
        for u in range(6, 12):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()

            if not self.elements.get("possible2_container"):
                self.elements["possible2_container"] = UIContainer(
                    ui_scale(pygame.Rect((100, 130), (50, 300))),
                    manager=MANAGER,
                )

            if not self.elements.get("chosen2_container"):
                self.elements["chosen2_container"] = UIContainer(
                    ui_scale(pygame.Rect((700, 130), (50, 300))),
                    manager=MANAGER,
                )

            # locate selected cat
            if possible_cats[u] == selected:
                selected_cat_index = u

            # place chosen cat
            elif possible_cats[u] in chosen_cats:
                self._add_to_cat_column(
                    possible_cats[u], u, self.elements["chosen2_container"], u - 6
                )

            # place possible cat
            else:
                self._add_to_cat_column(
                    possible_cats[u], u, self.elements["possible2_container"], u - 6
                )

        # placing selected cat
        if selected_cat_index is not None:
            i = selected_cat_index
            self.elements["cat" + str(i)] = self.elements[
                "cat" + str(i)
            ] = UISpriteButton(
                ui_scale(pygame.Rect((270, 200), (150, 150))),
                pygame.transform.scale(
                    possible_cats[i].sprite, ui_scale_dimensions((150, 150))
                ),
                cat_object=possible_cats[i],
            )

    def _add_to_cat_column(self, cat, index, container, position_offset):
        """Places the cat into its column within the given container"""

        self.elements["cat" + str(index)] = UISpriteButton(
            ui_scale(pygame.Rect((0, 0 + 50 * position_offset), (50, 50))),
            cat.sprite,
            container=container,
            tool_tip_text=self._get_cat_tooltip_string(cat),
            cat_object=cat,
            manager=MANAGER,
        )

    def _get_cat_tooltip_string(self, cat: Cat):
        """Get tooltip for cat. Tooltip displays name, sex, age group, and trait."""
        name = (
            cat.name
            if self.clan_info.get("leader") != cat
            else cat.name.get_specsuffix_name(CatRank.LEADER)
        )
        return f"<b>{name}</b><br>{cat.genderalign_string}<br>{i18n.t('general.' + cat.age, count=1)}<br>{i18n.t('cat.personality.' + cat.personality.trait)}<br>{cat.skills.skill_string(short=True)}"
