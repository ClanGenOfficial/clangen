from collections import deque, defaultdict

import i18n
import pygame
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.cat.skills import SkillPath
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.config import get_config
from scripts.events_module.text_adjust import shorten_text_to_fit
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.window_base_class import GameWindow


class BuildNestWindow(GameWindow):
    def __init__(self, med_den_screen):
        super().__init__(
            ui_scale(pygame.Rect((125, 150), (550, 400))),
            window_display_title="Herb Management",
        )
        self.med_den_screen = med_den_screen
        self.elements = {}
        self.meds = deque(
            find_alive_cats_with_rank(
                Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
            )
        )
        self.nests_built = 0
        self.build_limits: dict[str, int] = defaultdict(int)
        self.determine_build_limits()

        self.elements["build_info"] = pygame_gui.elements.UITextBox(
            "windows.build_nest_help",
            ui_scale(pygame.Rect((180, 30), (340, 170))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            container=self,
        )

        self.update_med_cat()

        moss_supply = game.clan.herb_supply.get_single_herb_total("moss")
        self.elements["moss_limit"] = pygame_gui.elements.UITextBox(
            "windows.build_nest_moss",
            ui_scale(pygame.Rect((180, 0), (340, 50))),
            text_kwargs={"count": moss_supply},
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["cat_limit"],
            },
        )

        self.elements["build_nest"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((290, 0), (120, 30))),
            "windows.build_nest",
            get_button_dict(ButtonStyles.SQUOVAL, (120, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
            anchors={
                "top_target": self.elements["moss_limit"],
            },
        )
        if not moss_supply or not self.build_limits[self.meds[0].ID]:
            self.elements["build_nest"].disable()

        self.elements["built_count"] = pygame_gui.elements.UITextBox(
            "windows.built_count",
            ui_scale(pygame.Rect((180, 0), (340, 50))),
            text_kwargs={"count": self.nests_built},
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["build_nest"],
            },
            visible=False,
        )

    def determine_build_limits(self):
        for c in self.meds:
            self.build_limits[c.ID] = 1

            # add tier level to limit
            skill_info = c.skills.get_all()
            self.build_limits[c.ID] += skill_info.get(SkillPath.CAMP, 0)

            exp_addition = round(c.experience * 0.01)
            self.build_limits[c.ID] += exp_addition

            self.build_limits[c.ID] -= game.clan.current_nest_build_count.get(c.ID, 0)

    def update_med_cat(self):
        displayed_med_cat = self.meds[0]

        # create cat image
        if self.elements.get("med_image"):
            self.elements["med_image"].kill()

        self.elements["med_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((20, 20), (150, 150))),
            pygame.transform.scale(
                displayed_med_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            container=self,
        )

        # display name
        if not self.elements.get("med_name"):
            self.elements["med_name"] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((20, 0), (150, 30))),
                shorten_text_to_fit(str(displayed_med_cat.name), 130, 15),
                object_id="#text_box_30_horizcenter",
                manager=MANAGER,
                anchors={"top_target": self.elements["med_image"]},
                container=self,
            )
        else:
            self.elements["med_name"].set_text(
                shorten_text_to_fit(str(displayed_med_cat.name), 137, 15)
            )

        # display info
        med_trait = i18n.t(f"cat.personality.{displayed_med_cat.personality.trait}")
        med_skill = displayed_med_cat.skills.skill_string(short=True)
        med_exp = i18n.t(
            "general.exp_label", exp=displayed_med_cat.experience_level_string
        )
        work_status = (
            i18n.t("general.can_work")
            if displayed_med_cat.can_work()
            else i18n.t("general.cant_work")
        )
        info_text = "<br>".join([med_trait, med_skill, med_exp, work_status])
        if not self.elements.get("med_info"):
            self.elements["med_info"] = pygame_gui.elements.UITextBox(
                info_text,
                ui_scale(pygame.Rect((20, 0), (150, 90))),
                object_id="#text_box_22_horizcenter",
                manager=MANAGER,
                anchors={
                    "top_target": self.elements["med_name"],
                },
                container=self,
            )
        else:
            self.elements["med_info"].set_text(info_text)

        # arrows for switching to other med cats
        if not self.elements.get("prior_med_arrow"):
            self.elements["prior_med_arrow"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((46, 0), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                starting_height=2,
                anchors={
                    "top_target": self.elements["med_info"],
                },
                container=self,
            )
            self.elements["next_med_arrow"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 0), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                starting_height=2,
                anchors={
                    "top_target": self.elements["med_info"],
                    "left_target": self.elements["prior_med_arrow"],
                },
                container=self,
            )

        if not self.elements.get("cat_limit"):
            self.elements["cat_limit"] = pygame_gui.elements.UITextBox(
                "windows.build_nest_limit",
                ui_scale(pygame.Rect((180, 0), (340, 50))),
                text_kwargs={
                    "cat": str(displayed_med_cat.name),
                    "count": self.build_limits[displayed_med_cat.ID],
                },
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
                container=self,
                anchors={
                    "top_target": self.elements["build_info"],
                },
            )
        else:
            self.elements["cat_limit"].set_text(
                "windows.build_nest_limit",
                text_kwargs={
                    "cat": str(displayed_med_cat.name),
                    "count": self.build_limits[displayed_med_cat.ID],
                },
            )

        if self.elements.get("build_nest"):
            if not self._moss_available() or not self.build_limits[self.meds[0].ID]:
                self.elements["build_nest"].disable()
            else:
                self.elements["build_nest"].enable()

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.elements["next_med_arrow"]:
                self.meds.rotate(-1)
                self.update_med_cat()
            elif event.ui_element == self.elements["prior_med_arrow"]:
                self.meds.rotate(1)
                self.update_med_cat()
            if event.ui_element == self.elements["build_nest"]:
                self.nests_built += 1
                game.clan.quarantine_nests += 1
                game.clan.current_nest_build_count[self.meds[0].ID] = (
                    game.clan.current_nest_build_count.get(self.meds[0].ID, 0) + 1
                )
                self.build_limits[self.meds[0].ID] -= 1
                self.elements["built_count"].set_text(
                    "windows.built_count", text_kwargs={"count": self.nests_built}
                )
                self.elements["built_count"].show()
                game.clan.herb_supply.remove_herb(
                    "moss", get_config("clan_resources.herbs.moss_per_quarantine_nest")
                )
                self.elements["moss_limit"].set_text(
                    "windows.build_nest_moss",
                    text_kwargs={
                        "count": game.clan.herb_supply.get_single_herb_total("moss")
                    },
                )
                self.update_med_cat()
                if not self._moss_available() or not self.build_limits[self.meds[0].ID]:
                    self.elements["build_nest"].disable()

        return super().process_event(event)

    @staticmethod
    def _moss_available():
        return game.clan.herb_supply.get_single_herb_total("moss") >= get_config(
            "clan_resources.herbs.moss_per_quarantine_nest"
        )

    def kill(self):
        # TODO: set nest amount
        self.med_den_screen.update_nest_display()
        super().kill()
