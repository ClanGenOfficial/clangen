from threading import Thread
from typing import List

import pygame
import pygame_gui

from scripts import events
from scripts.cat.cats import Cat
from scripts.cat.save_load import save_cats
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure.game.settings import game_settings_save
from scripts.game_structure.game.switches import (
    switch_set_value,
    Switch,
    switch_get_value,
)
from scripts.game_structure import game
from scripts.game_structure.propagating_thread import PropagatingThread
from scripts.screens import all_screens, EventsScreen
from scripts.screens.enums import GameScreen


class ReloadClanCommand(Command):
    name = "reload"
    description = "Reloads current clan, defaults to reloading without saving."
    aliases = ["r"]
    usage = "[save]"

    def callback(self, args: List[str]):
        if len(args) == 0:
            game.all_screens[game.current_screen].change_screen(game.current_screen)
            switch_set_value(Switch.switch_clan, True)
            add_output_line_to_log("Reload successful!")
        elif len(args) > 0 and args[0] == "save":
            save_cats(switch_get_value(Switch.clan_save_id), Cat, game)
            game.clan.save_clan()
            game.clan.save_pregnancy(game.clan)
            game.save_events()
            game_settings_save(game.current_screen)
            game.all_screens[game.current_screen].change_screen(game.current_screen)
            switch_set_value(Switch.switch_clan, True)
            add_output_line_to_log("Reload successful!")
        else:
            add_output_line_to_log(
                "Unable to reload clan, arguments might not be correct."
            )


class MoonSkipCommand(Command):
    name = "skip"
    description = "Batch skip some amount of moons"
    usage = "<moons: int>"
    aliases = ["moon", "ms", "s"]

    def callback(self, args: List[str]):
        if len(args) <= 0:
            add_output_line_to_log("Missing required argument: moons")
            return

        add_output_line_to_log(
            "Depending on how large your save is or how many moons you skipped, this could take a while..."
        )

        for i in range(int(args[0])):
            events.one_moon()

        # reload current screen
        all_screens.get_screen(switch_get_value(Switch.cur_screen)).change_screen(
            switch_get_value(Switch.cur_screen)
        )
        add_output_line_to_log("Completed batch skip!")


class ClanCommand(Command):
    name = "clan"
    description = "Manage current loaded clan"
    aliases = ["cl"]

    sub_commands = [ReloadClanCommand(), MoonSkipCommand()]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
