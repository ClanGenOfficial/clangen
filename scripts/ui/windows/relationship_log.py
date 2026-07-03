import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.cat.constants import BACKSTORIES
from scripts.cat.enums import CatGroup
from scripts.cat_relations.relationship import Relationship
from scripts.clan_package.settings import get_clan_setting
from scripts.events_module.text_adjust import shorten_text_to_fit
from scripts.game_structure import image_cache, game
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.relation_display import UIRelationDisplay
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale, ui_scale_dimensions


class RelationshipLogWindow(GameWindow):
    """This window allows the user to see the relationship log of a certain relationship."""

    def __init__(self, relationship):
        super().__init__(
            ui_scale(pygame.Rect((40, 80), (720, 540))),
        )

        self.cat_from: Cat = relationship.cat_from
        self.cat_to: Cat = relationship.cat_to

        self.relationship: Relationship = relationship
        self.opposite_relationship: Relationship = self.cat_to.relationships[
            self.cat_from.ID
        ]

        self.elements: dict = {}
        self.selected_cat_elements: dict = {}

        self._draw_cat_block(self.cat_from, starting_pos=(13, 15))

        short_name = shorten_text_to_fit(str(self.cat_from.name), 150, 7)
        self.elements["log1_title"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((18, 20), (330, 30))),
            "windows.cat_perspective",
            object_id="#text_box_34_horizleft",
            container=self,
            anchors={"top_target": self.selected_cat_elements[f"cat_container1"]},
            text_kwargs={"cat": short_name},
            manager=MANAGER,
        )

        if self.relationship.log:
            logs = self.relationship.log.copy()
            logs.reverse()
            log_string = "<br><br>".join(logs)

        else:
            log_string = "windows.no_relation_logs"

        self.elements["log1_text"] = pygame_gui.elements.UITextBox(
            log_string,
            ui_scale(pygame.Rect((18, 0), (330, 230))),
            object_id="#text_box_26_horizleft",
            container=self,
            anchors={
                "top_target": self.elements["log1_title"],
            },
            manager=MANAGER,
        )

        self._draw_cat_block(self.cat_to, starting_pos=(5, 15))

        short_name = shorten_text_to_fit(str(self.cat_to.name), 150, 7)
        self.elements["log2_title"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((20, 20), (330, 30))),
            "windows.cat_perspective",
            object_id="#text_box_34_horizleft",
            container=self,
            anchors={
                "left_target": self.elements["log1_text"],
                "top_target": self.selected_cat_elements[f"cat_container2"],
            },
            text_kwargs={"cat": short_name},
            manager=MANAGER,
        )
        if self.relationship.log:
            logs = self.opposite_relationship.log.copy()
            logs.reverse()
            log_string = "<br><br>".join(logs)
        else:
            log_string = "windows.no_relation_logs"
        self.elements["log2_text"] = pygame_gui.elements.UITextBox(
            log_string,
            ui_scale(pygame.Rect((20, 0), (330, 230))),
            object_id="#text_box_26_horizleft",
            container=self,
            anchors={
                "top_target": self.elements["log2_title"],
                "left_target": self.elements["log1_text"],
            },
            manager=MANAGER,
        )

    def _draw_cat_block(self, cat: Cat, starting_pos: tuple):
        """
        Creates all the elements within a selected cat block
        """
        if not cat:
            return

        # first we grab an index for the cat, so that we can create unique elements using it
        cat_num = 1 if cat == self.cat_from else 2

        # we also find the other cat, so that we can get any important info we need from them
        other_cat = self.cat_to if cat == self.cat_from else self.cat_from

        # we love a container
        self.selected_cat_elements[f"cat_container{cat_num}"] = UIContainer(
            ui_scale(pygame.Rect((starting_pos[0], starting_pos[1]), (343, 220))),
            container=self,
            manager=MANAGER,
            anchors={"left_target": self.selected_cat_elements["cat_container1"]}
            if cat == self.cat_to
            else None,
        )
        tail_image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/thought_bubble_tail.png"
            ).convert_alpha(),
            ui_scale_dimensions((32, 52)),
        )
        tail_image = pygame.transform.rotate(tail_image, 90)

        # create the relationship display
        the_relationship = cat.relationships[other_cat.ID]

        same_age = the_relationship.cat_to.age == cat.age
        adult_ages = ["young adult", "adult", "senior adult", "senior"]
        both_adult = the_relationship.cat_to.age in adult_ages and cat.age in adult_ages
        check_age = both_adult or same_age

        # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
        # even if they somehow have some. They should not be able to get any, but it never hurts to check.
        if not check_age or cat.is_related(
            other_cat, get_clan_setting("first cousin mates")
        ):
            allow_romance = False
        else:
            allow_romance = True

        # cat stuff needs to be drawn differently for each cat due to changes in alignment and anchoring
        if cat == self.cat_from:
            # CAT IMAGE
            self.selected_cat_elements[
                f"cat_image{cat_num}"
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((45, 0), (100, 100))),
                pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                manager=MANAGER,
            )

            # BUBBLE TAIL
            tail_image = pygame.transform.flip(tail_image, True, False)
            self.selected_cat_elements[f"bubble_tail{cat_num}"] = UIModifiedImage(
                ui_scale(pygame.Rect((0, 5), (52, 32))),
                tail_image,
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "left_target": self.selected_cat_elements[f"cat_image{cat_num}"]
                },
                manager=MANAGER,
            )
            # BUBBLE
            self.selected_cat_elements[f"rel_bg{cat_num}"] = UIModifiedImage(
                ui_scale(pygame.Rect((5, 20), (140, 185))),
                get_box(BoxStyles.ROUNDED_BOX, (140, 185)),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "left_target": self.selected_cat_elements[f"bubble_tail{cat_num}"]
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"relation_display{cat_num}"
            ] = UIRelationDisplay(
                (25, 30),
                the_relationship,
                romance=allow_romance,
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "left_target": self.selected_cat_elements[f"bubble_tail{cat_num}"]
                },
            )

            short_name = shorten_text_to_fit(str(cat.name), 200, 7)
            self.selected_cat_elements[
                f"cat_name{cat_num}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((0, 0), (190, 30))),
                short_name,
                object_id="#text_box_30_horizcenter",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_image{cat_num}"],
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details1_{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self._get_cat_details1(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (95, -1))),
                object_id="#text_box_22_horizleft_spacing_95",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_name{cat_num}"],
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details2_{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self._get_cat_details2(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (95, -1))),
                object_id="#text_box_22_horizleft_spacing_95",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_name{cat_num}"],
                    "left_target": self.selected_cat_elements[
                        f"cat_details1_{cat_num}"
                    ],
                },
                manager=MANAGER,
            )
        else:
            # BUBBLE
            tail_image = pygame.transform.flip(tail_image, True, False)
            self.selected_cat_elements[f"rel_bg{cat_num}"] = UIModifiedImage(
                ui_scale(pygame.Rect((0, 20), (140, 185))),
                get_box(BoxStyles.ROUNDED_BOX, (140, 185)),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"relation_display{cat_num}"
            ] = UIRelationDisplay(
                (25, 30),
                self.opposite_relationship,
                romance=allow_romance,
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
            )

            # BUBBLE TAIL
            tail_image = pygame.transform.flip(tail_image, True, False)
            self.selected_cat_elements[f"bubble_tail{cat_num}"] = UIModifiedImage(
                ui_scale(pygame.Rect((5, 5), (52, 32))),
                tail_image,
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={"left_target": self.selected_cat_elements[f"rel_bg{cat_num}"]},
                manager=MANAGER,
            )

            # CAT IMAGE
            self.selected_cat_elements[
                f"cat_image{cat_num}"
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (100, 100))),
                pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "left_target": self.selected_cat_elements[f"bubble_tail{cat_num}"]
                },
                manager=MANAGER,
            )

            short_name = shorten_text_to_fit(str(cat.name), 200, 7)
            self.selected_cat_elements[
                f"cat_name{cat_num}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((13, 0), (190, 30))),
                short_name,
                object_id="#text_box_30_horizcenter",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_image{cat_num}"],
                    "left_target": self.selected_cat_elements[f"rel_bg{cat_num}"],
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details1_{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self._get_cat_details1(cat, other_cat),
                ui_scale(pygame.Rect((13, 0), (95, -1))),
                object_id="#text_box_22_horizright_spacing_95",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_name{cat_num}"],
                    "left_target": self.selected_cat_elements[f"rel_bg{cat_num}"],
                },
                manager=MANAGER,
            )
            self.selected_cat_elements[
                f"cat_details2_{cat_num}"
            ] = pygame_gui.elements.UITextBox(
                self._get_cat_details2(cat, other_cat),
                ui_scale(pygame.Rect((0, 0), (95, -1))),
                object_id="#text_box_22_horizright_spacing_95",
                container=self.selected_cat_elements[f"cat_container{cat_num}"],
                anchors={
                    "top_target": self.selected_cat_elements[f"cat_name{cat_num}"],
                    "left_target": self.selected_cat_elements[
                        f"cat_details1_{cat_num}"
                    ],
                },
                manager=MANAGER,
            )

    @staticmethod
    def _get_cat_details1(cat, other_cat) -> str:
        """
        Returns a string with the cat's details: gender, relation to other cat, age, and trait
        """
        output = ""
        # gender
        output += f"{cat.genderalign}<br>"

        # age
        output += f"{i18n.t('general.moons_age', count=cat.moons)}<br>"

        # trait
        output += f"{i18n.t(f'cat.personality.{cat.personality.trait}')}<br><br>"

        # show relation
        if other_cat:
            relation = ""
            if other_cat.ID in cat.mate:
                relation = f"{i18n.t('general.mate', count=1)}<br>"
            elif cat.is_parent(other_cat):
                relation = f"{i18n.t('general.parent')}<br>"
            elif other_cat.is_parent(cat):
                relation = f"{i18n.t('general.child')}<br>"
            elif cat.is_sibling(other_cat):
                relation = f"{i18n.t('general.sibling')}<br>"
            # any relations more complex just get "related" text for my sanity
            elif cat.is_related(other_cat, False):
                relation = f"{i18n.t('general.related_text')}<br>"

            if relation:
                output += f"{i18n.t('windows.relation_connection', relation=relation)}"

        return output

    def _get_cat_details2(self, cat, other_cat) -> str:
        """
        Returns a string with the cat's details: gender, relation to other cat, age, and trait
        """
        output = ""

        # STATUS
        output += self._get_status_info(cat)
        output += "<br><br>"

        # BACKSTORY
        bs_text = ""
        # if cat has never been part of the player clan, then they get no backstory yet
        if (
            cat.status.alive_in_player_clan
            or CatGroup.PLAYER_CLAN_ID not in cat.status.all_groups
        ):
            if cat.backstory:
                for category, values in BACKSTORIES["backstory_categories"].items():
                    if cat.backstory in values:
                        bs_text = i18n.t(f"cat.backstories.{category}")
                        break
            else:
                bs_text = i18n.t("cat.backstories.clanborn_backstories")
        if bs_text:
            output += bs_text

        return output

    @staticmethod
    def _get_status_info(cat):
        output = ""
        if cat.dead:
            old_clan = cat.status.get_last_living_group()
            if old_clan == CatGroup.PLAYER_CLAN_ID:
                name = game.clan.name
            # if they had an old clan that wasn't the player's, find it!
            elif old_clan:
                name = [
                    c
                    for c in game.clan.all_other_clans
                    if c.group_ID == cat.status.get_last_living_group()
                ][0].name
            # otherwise they had no clan
            else:
                name = None

        # if cat is alive and in another clan, find that clan's name
        elif cat.status.is_other_clancat:
            name = [
                c
                for c in game.clan.all_other_clans
                if c.group_ID == cat.status.group_ID
            ][0].name
        # otherwise, assume the cat takes the player clan's name
        # it's okay if this is an outsider, if they don't actually have a group to refer to then they won't use this variable
        else:
            name = game.clan.name

        if cat.status.is_exiled():
            if not name:
                name = [
                    c
                    for c in game.clan.all_other_clans
                    if c.group_ID == cat.status.get_last_living_group()
                ]
            if not name:
                name = game.clan.name

        cat_clan = name

        if cat.status.is_lost():
            output += f"<font color='#FF0000'>{i18n.t('general.lost', count=1)}</font>"
            # NEWLINE ----------
            output += "\n"
        elif cat.status.is_exiled():
            output += f"<font color='#FF0000'>{i18n.t('general.exiled', count=1)} {cat_clan}</font>"
            # NEWLINE ----------
            output += "\n"

        if cat == game.clan.instructor:
            output += i18n.t(f"general.guide")
            output += "\n"

        if cat.dead:
            if cat == game.clan.instructor or cat.status.is_outsider:
                output += i18n.t(
                    f"general.past_no_group",
                    rank=i18n.t(f"general.{cat.status.rank}", count=1),
                )
            else:
                output += i18n.t(
                    "general.past_group",
                    group=cat_clan,
                    rank=i18n.t(f"general.{cat.status.rank}", count=1),
                )
        elif cat.status.is_outsider:
            output += i18n.t(f"general.{cat.status.rank}", count=1)
        else:
            output += i18n.t(
                "general.living_group",
                group=cat_clan,
                rank=i18n.t(f"general.{cat.status.rank}", count=1),
            )

        return output
