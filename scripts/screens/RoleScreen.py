#!/usr/bin/env python3
# -*- coding: ascii -*-
import os

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow


class RoleScreen(Screens):
    the_cat = None
    selected_cat_elements = {}
    buttons = {}
    next_cat = None
    previous_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.promote_leader:
                if self.the_cat == game.clan.deputy:
                    game.clan.deputy = None
                game.clan.new_leader(self.the_cat)
                if game.sort_type == "rank":
                    Cat.sort_cats()
                self.update_selected_cat()
            elif event.ui_element == self.promote_deputy:
                game.clan.deputy = self.the_cat
                self.the_cat.status_change("deputy", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_warrior:
                self.the_cat.status_change("warrior", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_med_cat:
                self.the_cat.status_change("medicine cat", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.retire:
                self.the_cat.status_change("elder", resort=True)
                # Since you can't "unretire" a cat, apply the skill and trait change
                # here
                self.update_selected_cat()
            elif event.ui_element == self.switch_mediator:
                self.the_cat.status_change("mediator", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_warrior_app:
                self.the_cat.status_change("apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_med_app:
                self.the_cat.status_change("medicine cat apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_mediator_app:
                self.the_cat.status_change("mediator apprentice", resort=True)
                self.update_selected_cat()

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if event.key == pygame.K_ESCAPE:
                self.change_screen("profile screen")
            elif event.key == pygame.K_RIGHT:
                game.switches["cat"] = self.next_cat
                self.update_selected_cat()
            elif event.key == pygame.K_LEFT:
                game.switches["cat"] = self.previous_cat
                self.update_selected_cat()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "Next Cat " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            get_arrow(2, arrow_left=True) + " Previous Cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # Create the buttons
        self.bar = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((48, 350), (704, 10))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/bar.png"),
                ui_scale_dimensions((704, 10)),
            ),
            manager=MANAGER,
        )

        self.blurb_background = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 195), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )

        # LEADERSHIP
        self.promote_leader = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "promote to leader",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_top",
            anchors={"top_target": self.bar},
        )
        self.promote_deputy = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "promote to deputy",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.promote_leader},
        )

        # ADULT CAT ROLES
        self.switch_warrior = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "switch to warrior",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
        )
        self.retire = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "retire",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_warrior},
        )
        self.switch_med_cat = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 52))),
            "switch to medicine\ncat",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_mediator = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 36))),
            "switch to mediator",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_med_cat},
        )

        # In-TRAINING ROLES:
        self.switch_warrior_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 52))),
            "switch to warrior\napprentice",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_med_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 52))),
            "switch to medicine\ncat apprentice",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_warrior_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_mediator_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 52))),
            "switch to mediator\napprentice",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_med_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )

        self.update_selected_cat()

    def update_selected_cat(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.the_cat = Cat.fetch_cat(game.switches["cat"])
        if not self.the_cat:
            return

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((245, 40), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 150, 13)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((387, 70), (175, -1))),
            short_name,
            object_id=get_text_box_theme("#text_box_30"),
        )

        text = f"<b>{self.the_cat.status}</b>\n{self.the_cat.personality.trait}\n"

        text += f"{self.the_cat.moons} "

        if self.the_cat.moons == 1:
            text += "moon  |  "
        else:
            text += "moons  |  "

        text += self.the_cat.genderalign + "\n"

        if self.the_cat.mentor:
            text += "mentor: "
            mentor = Cat.fetch_cat(self.the_cat.mentor)
            if mentor:
                text += str(mentor.name)

        if self.the_cat.apprentice:
            if len(self.the_cat.apprentice) > 1:
                text += "apprentices: "
            else:
                text += "apprentice: "

            text += ", ".join(
                [
                    str(Cat.fetch_cat(x).name)
                    for x in self.the_cat.apprentice
                    if Cat.fetch_cat(x)
                ]
            )

        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(
            text,
            ui_scale(pygame.Rect((395, 100), (160, 94))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
            line_spacing=0.95,
        )

        self.selected_cat_elements["role_blurb"] = pygame_gui.elements.UITextBox(
            self.get_role_blurb(),
            ui_scale(pygame.Rect((170, 200), (560, 135))),
            object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        main_dir = "resources/images/"
        paths = {
            "leader": "leader_icon.png",
            "deputy": "deputy_icon.png",
            "medicine cat": "medic_icon.png",
            "medicine cat apprentice": "medic_app_icon.png",
            "mediator": "mediator_icon.png",
            "mediator apprentice": "mediator_app_icon.png",
            "warrior": "warrior_icon.png",
            "apprentice": "warrior_app_icon.png",
            "kitten": "kit_icon.png",
            "newborn": "kit_icon.png",
            "elder": "elder_icon.png",
        }

        if self.the_cat.status in paths:
            icon_path = os.path.join(main_dir, paths[self.the_cat.status])
        else:
            icon_path = os.path.join(main_dir, "buttonrank.png")

        self.selected_cat_elements["role_icon"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((82, 231), (78, 78))),
            pygame.transform.scale(
                image_cache.load_image(icon_path),
                ui_scale_dimensions((78, 78)),
            ),
        )

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.update_disabled_buttons()

    def update_disabled_buttons(self):
        # Previous and next cat button
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

        if game.clan.leader:
            leader_invalid = game.clan.leader.dead or game.clan.leader.outside
        else:
            leader_invalid = True

        if game.clan.deputy:
            deputy_invalid = game.clan.deputy.dead or game.clan.deputy.outside
        else:
            deputy_invalid = True

        if self.the_cat.status == "apprentice":
            # LEADERSHIP
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.enable()
        elif self.the_cat.status == "warrior":
            # LEADERSHIP
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid:
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "deputy":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "medicine cat":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "mediator":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid:
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "elder":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid:
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "medicine cat apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
        elif self.the_cat.status == "mediator apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "leader":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        else:
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()

    def get_role_blurb(self):
        if self.the_cat.status == "warrior":
            output = (
                f"{self.the_cat.name} is a <b>warrior</b>. Warriors are adult cats who feed and protect their "
                f"Clan. They are trained to hunt and fight in addition to the ways of the Warrior Code. "
                f"Warriors are essential to the survival of a Clan, and usually make up the bulk of it's members. "
            )
        elif self.the_cat.status == "leader":
            output = (
                f"{self.the_cat.name} is the <b>leader</b> of {game.clan.name}Clan. The guardianship of all "
                f"Clan cats has been entrusted to them by StarClan. The leader is the highest "
                f"authority in the Clan. The leader holds Clan meetings, determines mentors for "
                f"new apprentices, and names new warriors. To help them protect the Clan, "
                f'StarClan has given them nine lives. They typically take the suffix "star".'
            )
        elif self.the_cat.status == "deputy":
            output = (
                f"{self.the_cat.name} is {game.clan.name}Clan's <b>deputy</b>. "
                f"The deputy is the second in command, "
                f"just below the leader. They advise the leader and organize daily patrols, "
                f"alongside normal warrior duties. Typically, a deputy is personally appointed by the current "
                f"leader. As dictated by the Warrior Code, all deputies must train at least one apprentice "
                f"before appointment.  "
                f"The deputy succeeds the leader if they die or retire. "
            )
        elif self.the_cat.status == "medicine cat":
            output = (
                f"{self.the_cat.name} is a <b>medicine cat</b>. Medicine cats are the healers of the Clan. "
                f"They treat "
                f"injuries and illnesses with herbal remedies. Unlike warriors, medicine cats are not expected "
                f"to hunt and fight for the Clan. In addition to their healing duties, medicine cats also have "
                f"a special connection to StarClan. Every half-moon, they travel to their Clan's holy place "
                f"to commune with StarClan. "
            )
        elif self.the_cat.status == "mediator":
            output = (
                f"{self.the_cat.name} is a <b>mediator</b>. Mediators are not typically required "
                f"to hunt or fight for "
                f"the Clan. Rather, mediators are charged with handling disagreements between "
                f"Clanmates and disputes between Clans. Some mediators train as apprentices to serve their Clan, "
                f"while others may choose to become mediators later in life. "
            )
        elif self.the_cat.status == "elder":
            output = (
                f"{self.the_cat.name} is an <b>elder</b>. They have spent many moons serving their Clan, "
                f"and have earned "
                f"many moons of rest. Elders are essential to passing down the oral tradition of the Clan. "
                f"Sometimes, cats may retire due to disability or injury. Whatever the "
                f"circumstance of their retirement, elders are held in high esteem in the Clan, and always eat "
                f"before Warriors and Medicine Cats. "
            )
        elif self.the_cat.status == "apprentice":
            output = (
                f"{self.the_cat.name} is an <b>apprentice</b>, in training to become a warrior. "
                f"Kits can be made warrior apprentices at six moons of age, where they will learn how "
                f"to hunt and fight for their Clan. Typically, the training of an apprentice is entrusted "
                f"to an single warrior - their mentor. To build character, apprentices are often assigned "
                f'the unpleasant and grunt tasks of Clan life. Apprentices take the suffix "paw", '
                f"to represent the path their paws take towards adulthood. "
            )
        elif self.the_cat.status == "medicine cat apprentice":
            output = (
                f"{self.the_cat.name} is a <b>medicine cat apprentice</b>, training to become a full medicine cat. "
                f"Kits can be made medicine cat apprentices at six moons of age, where they will learn how to "
                f"heal their Clanmates and commune with StarClan. Medicine cat apprentices are typically chosen "
                f"for their interest in healing and/or their connecting to StarClan. Apprentices take the suffix "
                f"-paw, to represent the path their paws take towards adulthood."
            )
        elif self.the_cat.status == "mediator apprentice":
            output = (
                f"{self.the_cat.name} is a <b>mediator apprentice</b>, training to become a full mediator. "
                f"Mediators are in charge of handling disagreements both within the Clan and between Clans. "
                f"Mediator apprentices are often chosen for their quick thinking and steady personality. "
                f'Apprentices take the suffix "paw", '
                f"to represent the path their paws take towards adulthood. "
            )
        elif self.the_cat.status == "kitten":
            output = (
                f"{self.the_cat.name} is a <b>kitten</b>. All cats below the age of six moons are "
                f"considered kits. Kits "
                f"are prohibited from leaving camp in order to protect them from the dangers of the wild. "
                f"Although they don't have any official duties in the Clan, they are expected to learn the "
                f"legends and traditions of their Clan. They are protected by every cat in the Clan and always "
                f'eat first. Kit take the suffix "kit".'
            )
        elif self.the_cat.status == "newborn":
            output = (
                f"{self.the_cat.name} is a <b>newborn kitten</b>. All cats below the age of six moons are "
                f"considered kits. Kits "
                f"are prohibited from leaving camp in order to protect them from the dangers of the wild. "
                f"Although they don't have any official duties in the Clan, they are expected to learn the "
                f"legends and traditions of their Clan. They are protected by every cat in the Clan and always "
                f'eat first. Kit take the suffix "kit".'
            )
        else:
            output = f"{self.the_cat.name} has an unknown rank. I guess they want to make their own way in life! "

        return output

    def exit_screen(self):
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.bar.kill()
        del self.bar
        self.promote_leader.kill()
        del self.promote_leader
        self.promote_deputy.kill()
        del self.promote_deputy
        self.switch_warrior.kill()
        del self.switch_warrior
        self.switch_med_cat.kill()
        del self.switch_med_cat
        self.switch_mediator.kill()
        del self.switch_mediator
        self.retire.kill()
        del self.retire
        self.switch_med_app.kill()
        del self.switch_med_app
        self.switch_warrior_app.kill()
        del self.switch_warrior_app
        self.switch_mediator_app.kill()
        del self.switch_mediator_app
        self.blurb_background.kill()
        del self.blurb_background

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}
