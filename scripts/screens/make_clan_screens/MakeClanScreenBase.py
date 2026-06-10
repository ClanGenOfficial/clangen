import dataclasses
from dataclasses import dataclass, field
from random import choice
from re import sub
from typing import Optional
from uuid import uuid4

import pygame
import pygame_gui

from scripts.cat import save_load
from scripts.cat.cats import Cat
from scripts.cat.names import names
from scripts.clan import Clan
from scripts.events_module.patrol.patrol import Patrol
from scripts.game_structure import game
from scripts.game_structure.game import switch_get_value, Switch, game_setting_get
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.screens.enums import GameScreen
from scripts.screens.screens_core import screens_core
from scripts.screens.screens_core.screens_core import rebuild_top_menu_buttons
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale
from scripts.ui.theme import get_text_box_theme


def _clan_name_exists(new_clan_name: str):
    return new_clan_name.casefold() in (
        clan.casefold() for clan in switch_get_value(Switch.clan_list)
    )


def _generate_unique_clan_name(new_clan_name: str):
    return f"{new_clan_name}_{uuid4()}"


@dataclass
class ClanInfo:
    """
    Dataclass for holding all the info we collect during clan creation. Attributes match the attributes used when intializing a Clan object.
    """

    # we do this as a dataclass to make it a bit more future-proofed for any eventual additions to this info
    # this way it's much easier to change names of attributes or add new ones OR know if you've fucked smth up
    display_name: str = ""
    leader: Optional[Cat] = None
    deputy: Optional[Cat] = None
    medicine_cat: Optional[Cat] = None
    starting_members: list = field(default_factory=list)
    biome: str = ""
    camp_bg: str = "camp1"
    symbol: str = ""
    starting_season: str = "Newleaf"
    game_mode: str = "classic"

    def clear(self):
        """
        Return all the attributes back to their default values
        """
        self.display_name = ""
        self.leader = None
        self.deputy = None
        self.medicine_cat = None
        self.starting_members = []
        self.biome = ""
        self.camp_bg = "camp1"
        self.symbol = ""
        self.starting_season = "Newleaf"
        self.game_mode = "classic"

    def update(self, saved_info: dict):
        self.display_name = saved_info["display_name"]
        self.leader = saved_info["leader"]
        self.deputy = saved_info["deputy"]
        self.medicine_cat = saved_info["medicine_cat"]
        self.starting_members = saved_info["starting_members"]
        self.biome = saved_info["biome"]
        self.camp_bg = saved_info["camp_bg"]
        self.symbol = saved_info["symbol"]
        self.starting_season = saved_info["starting_season"]
        self.game_mode = saved_info["game_mode"]

    def get_dict(self) -> dict:
        """
        Returns all the attributes as a dict. We gotta use this instead of the dataclasses.as_dict() because Cat objects aren't pickable
        """
        return {
            "display_name": self.display_name,
            "leader": self.leader,
            "deputy": self.deputy,
            "medicine_cat": self.medicine_cat,
            "starting_members": self.starting_members,
            "biome": self.biome,
            "camp_bg": self.camp_bg,
            "symbol": self.symbol,
            "starting_season": self.starting_season,
            "game_mode": self.game_mode,
        }

    def no_cats_chosen(self) -> bool:
        return (
            not self.leader
            and not self.deputy
            and not self.medicine_cat
            and not self.starting_members
        )

    def has_minimum_cats(self) -> bool:
        return (
            self.leader
            and self.deputy
            and self.medicine_cat
            and len(self.starting_members) >= 4
        )

    def has_maximum_cats(self) -> bool:
        return (
            self.leader
            and self.deputy
            and self.medicine_cat
            and len(self.starting_members) >= 7
        )

    def has_high_ranks_filled(self) -> bool:
        return all([self.leader, self.deputy, self.medicine_cat])


class MakeClanScreenBase(Screens):
    def __init__(self, name="make_clan_screen"):
        super().__init__(name)

        self.elements: dict = {}
        self.clan_info: ClanInfo = ClanInfo()

    def screen_switches(self):
        super().screen_switches()
        self.set_mute_button_position("topright")
        self.show_mute_buttons()
        self.set_bg("default", "mainmenu_bg")

        # grab clan_info from the switch
        if switch_get_value(Switch.clan_creation_info):
            self.clan_info.update(switch_get_value(Switch.clan_creation_info))

        # Buttons that appear on every screen.
        self.elements["menu_warning"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.menu_warning",
            ui_scale(pygame.Rect((25, 25), (600, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
        )
        self.elements["main_menu"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 50), (153, 30))),
            "buttons.main_menu",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_squoval",
            starting_height=1,
        )
        self.elements["previous_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((253, 620), (147, 30))),
            "buttons.previous_step",
            get_button_dict(ButtonStyles.MENU_LEFT, (147, 30)),
            object_id="@buttonstyles_menu_left",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 620), (147, 30))),
            "buttons.next_step",
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["main_menu"]:
                self.clan_info.clear()
                self.change_screen(GameScreen.START)

        return super().handle_event(event)

    def exit_screen(self):
        # set switch value so it can be retrieved during the next step
        switch_set_value(Switch.clan_creation_info, self.clan_info.get_dict())

        # kill elements
        for ele in self.elements.values():
            ele.kill()
        self.elements.clear()
        return super().exit_screen()

    def save_clan(self):
        game.mediated.clear()
        game.patrolled.clear()
        game.just_died.clear()
        game.dead_cats_to_grieve.clear()
        save_load.faded_ids.clear()
        Cat.outside_cats.clear()
        Patrol.used_patrols.clear()

        # extra sanitization for filenames
        save_id = sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", self.clan_info.display_name)
        # if the name is in use, we create a unique save id
        if _clan_name_exists(save_id):
            save_id = _generate_unique_clan_name(save_id)

        game.clan = Clan(
            save_id=save_id,
            **self.clan_info.get_dict(),
        )
        game.clan.create_clan()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        game.clan.herb_supply.start_storage(len(self.clan_info.starting_members))
        game.clan.save_herb_supply(game.clan)
        game.clan.grief_strings.clear()
        Cat.sort_cats()
        rebuild_top_menu_buttons()

    def random_biome_selection(self):
        # Select a random biome and background
        possible_biomes = ["Forest", "Mountainous", "Plains", "Beach"]
        # ensuring that the new random camp will not be the same one
        if self.clan_info.biome:
            possible_biomes.remove(self.clan_info.biome)
        chosen_biome = choice(possible_biomes)
        return chosen_biome

    def random_clan_name(self):
        clan_names = (
            names.names_dict["normal_prefixes"] + names.names_dict["clan_prefixes"]
        )
        if self.clan_info.display_name:
            clan_names.remove(self.clan_info.display_name)

        return choice(clan_names)

    def get_camp_art_path(self, campnum) -> Optional[str]:
        if not campnum:
            return None

        leaf = self.clan_info.starting_season.replace("-", "")

        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = leaf.casefold()
        light_dark = "dark" if game_setting_get("dark mode") else "light"

        biome = self.clan_info.biome.lower()

        return (
            f"{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png"
        )

    def get_camp_bg(self, src=None):
        camp_num = self.clan_info.camp_bg[-1]
        if src is None:
            src = pygame.image.load(self.get_camp_art_path(camp_num)).convert_alpha()

        name = "_".join(
            [
                str(self.clan_info.biome),
                str(camp_num),
                self.clan_info.starting_season,
            ]
        )
        if name not in self.game_bgs:
            self.game_bgs[name] = screens_core.default_game_bgs[self.theme]["default"]
            self.fullscreen_bgs[name] = screens_core.process_blur_bg(src)

        self.set_bg(name)
