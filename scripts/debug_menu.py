"""
Debug menu
"""

import pygame
import pygame_gui

from typing import List
from scripts.game_structure.game_essentials import MANAGER, game

from scripts.utility import get_text_box_theme
from scripts.debug_commands import commandList
from scripts.debug_commands.utils import setDebugClass


class debugConsole(pygame_gui.windows.UIConsoleWindow):
    def __init__(self, rect, manager):
        setDebugClass(self)
        super().__init__(rect, manager, window_title="Debug Console",
                         object_id="#debug_console", visible=0)

        # Force it to print help txt
        ev = pygame.event.Event(
            pygame_gui.UI_CONSOLE_COMMAND_ENTERED, {"command": "help"})
        self.process_event(ev)

    def process_event(self, event):
        if event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED:
            command: List[str] = event.command.split(" ")
            args = command[1:]
            command = command[0]

            commandFound = False
            for cmd in commandList:
                if command in cmd._aliases:  # pylint: disable=protected-access
                    commandFound = True
                    if not cmd.bypassConjoinedStrings:
                        _args = []
                        curArgGroup = ""
                        inGroup = False
                        for arg in args:
                            if not inGroup:
                                if arg.startswith("\""):
                                    inGroup = True
                                    curArgGroup = arg[1:]
                                else:
                                    _args.append(arg)
                            else:
                                if arg.endswith("\""):
                                    inGroup = False
                                    curArgGroup += " " + arg[:-1]
                                    _args.append(curArgGroup)
                                else:
                                    curArgGroup += " " + arg
                        args = _args
                    if len(args) > 0:
                        for subcommand in cmd.subCommands:
                            if args[0] in subcommand._aliases:  # pylint: disable=protected-access
                                args = args[1:]
                                cmd = subcommand
                                break
                    try:
                        cmd.callback(args)
                    except Exception as e:
                        self.add_output_line_to_log(
                            f"Error while executing command {command}: {e}")
                        raise e
                    break
            if command in ["cls", "clear"]:
                self._clear()
            elif not commandFound:
                self.add_output_line_to_log(f"Command {command} not found")

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if len(self.command_entry.text) != 0:
                for cmd in commandList:
                    for alias in cmd._aliases:  # pylint: disable=protected-access
                        if alias.startswith(self.command_entry.text):
                            self.command_entry.set_text(f"{alias}")
                            break

        return super().process_event(event)

    def _clear(self):
        self.clear_log()

class debugMode:
    def __init__(self):

        self.coords_display = pygame_gui.elements.UILabel(
            pygame.Rect((0, 0), (-1, -1)),
            "(0, 0)",
            object_id=get_text_box_theme()
        )

        self.fps_display = pygame_gui.elements.UILabel(
            pygame.Rect((0, 0), (-1, -1)),
            "0 fps",
            object_id=get_text_box_theme()
        )

        self.console = debugConsole(pygame.Rect((0, 0), (pygame.display.get_surface(
        ).get_width(), pygame.display.get_surface().get_height())), MANAGER)

        self.coords_display.text_colour = (255, 0, 0)
        self.coords_display.disable()
        self.coords_display.rebuild()
        self.coords_display.hide()

    def toggle_console(self):
        if self.console.visible == 0:
            self.console.show()
            self.console.command_entry.focus()
            self.console.set_blocking(True)
            game.switches['window_open'] = True
        else:
            self.console.hide()
            self.console.set_blocking(False)
            game.switches['window_open'] = False

    def update1(self, clock):
        """
        This is called BEFORE pygame_gui updates elements
        """

        # Showcoords
        if game.debug_settings['showcoords']:
            if self.coords_display.visible == 0:
                self.coords_display.show()

            _ = pygame.mouse.get_pos()
            if game.settings['fullscreen']:
                self.coords_display.set_text(f"({_[0]}, {_[1]})")
            else:
                self.coords_display.set_text(f"({_[0]*2}, {_[1]*2})")
            self.coords_display.set_position(_)
            del _
        else:
            if self.coords_display.visible == 1:
                self.coords_display.hide()
                self.coords_display.set_text("(0, 0)")
                self.coords_display.set_position((0, 0))

        if game.debug_settings['showfps']:
            if self.fps_display.visible == 0:
                self.fps_display.show()

            self.fps_display.set_text(f"{round(clock.get_fps(), 2)} fps")
        else:
            if self.fps_display.visible == 1:
                self.fps_display.hide()
                self.fps_display.set_text("(0, 0)")

        # Showbounds

        # visual_debug_mode
        if game.debug_settings['visualdebugmode']:
            if not MANAGER.visual_debug_active:
                MANAGER.set_visual_debug_mode(True)
        else:
            if MANAGER.visual_debug_active:
                MANAGER.set_visual_debug_mode(False)

    def update2(self, screen):

        if game.debug_settings['showbounds']:
            elements = MANAGER.ui_group.visible
            for surface in elements:
                rect = surface[1]
                if rect in [self.coords_display.rect, self.console.rect]:
                    continue
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, (0, 255, 0), rect, 1)
                else:
                    pygame.draw.rect(screen, (255, 0, 0), rect, 1)


debugmode = debugMode()
