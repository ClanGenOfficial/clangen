"""
Stores the DebugMenu class and the DebugMode class
"""

import pygame
import pygame_gui
import html

from pygame_gui.elements import UIWindow, UITextBox, UITextEntryLine
from scripts.utility import ui_scale
from scripts.debug_commands import commandList
from scripts.debug_commands.utils import set_debug_class
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER, offset, screen_scale
from scripts.utility import get_text_box_theme


class DebugMenu(UIWindow):
    """
    The ClanGen debug menu, useful for debugging.
    """

    def __init__(self, rect, manager):
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title="Debug Console",
            object_id="#debug_console",
            resizable=False,
            always_on_top=True,
            visible=0,
        )
        self.set_blocking(False)
        set_debug_class(self)

        self.log = UITextBox(
            "",
            relative_rect=ui_scale(
                pygame.Rect(
                    (2, 2),
                    (
                        self.get_container().get_size()[0] - 4,
                        self.get_container().get_size()[1] - 36,
                    ),
                )
            ),
            container=self,
            object_id="#log",
            manager=MANAGER,
        )

        self.command_line = UITextEntryLine(
            relative_rect=ui_scale(
                pygame.Rect((2, -32), (self.get_container().get_size()[0] - 4, 30))
            ),
            container=self,
            anchors={"top": "bottom"},
        )

        # self.submit_command = UIButton(

        # )

        self.change_layer(1000)

        ev = pygame.event.Event(
            pygame_gui.UI_CONSOLE_COMMAND_ENTERED, {"command": "help"}
        )
        self.process_event(ev)

    def process_command(self, raw_command: str):
        """
        Processes a string containing the command and it's arguments and calls
        the appropriate command's callback.
        """
        command_list = raw_command.split(" ")
        args = command_list[1:]
        command = command_list[0]

        commandFound = False
        for cmd in commandList:
            if command in cmd._aliases:  # pylint: disable=protected-access
                commandFound = True
                if not cmd.bypass_conjoined_strings:
                    _args = []
                    curArgGroup = ""
                    inGroup = False
                    for arg in args:
                        if not inGroup:
                            if arg.startswith('"'):
                                inGroup = True
                                curArgGroup = arg[1:]
                            else:
                                _args.append(arg)
                        else:
                            if arg.endswith('"'):
                                inGroup = False
                                curArgGroup += " " + arg[:-1]
                                _args.append(curArgGroup)
                            else:
                                curArgGroup += " " + arg
                    args = _args
                if len(args) > 0:
                    for subcommand in cmd.sub_commands:
                        if (
                            args[0]
                            in subcommand._aliases  # pylint: disable=protected-access
                        ):  # pylint: disable=protected-access
                            args = args[1:]
                            cmd = subcommand
                            break
                try:
                    cmd.callback(args)
                except Exception as e:
                    self.push_line(f"Error while executing command {command}: {e}")
                    raise e
                break
        if command in ["self", "clear"]:
            self.log.set_text("")
        elif not commandFound:
            self.push_line(f"Command {command} not found")

    def process_event(self, event: pygame.Event):
        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED
            and event.ui_element == self.command_line
        ):
            pygame.event.post(
                pygame.Event(
                    pygame_gui.UI_CONSOLE_COMMAND_ENTERED,
                    {"command": self.command_line.get_text()},
                )
            )
            self.command_line.clear()
        if event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED:
            self.process_command(event.command)
        return super().process_event(event)

    def push_line(self, line: str):
        """
        Appends a string and a newline to the command log.
        """
        self.log.append_html_text(html.escape(line + "\n"))

    def push_multiline(self, lines: str):
        """
        Appends multiple lines to the command log.
        """
        for line in lines.split("\n"):
            self.push_line(line)


class DebugMode:
    """
    A utility class that stores the debug menu and other debugging related
    UI elements.
    """

    debug_menu: DebugMenu = None
    coords_display = None
    fps_display = None

    def __init__(self):
        self.rebuild_console()

    def toggle_debug_mode(self):
        """
        Toggles the debug menu.
        """
        if self.debug_menu.visible == 0:
            self.debug_menu.show()
            self.debug_menu.command_line.focus()
        else:
            self.debug_menu.hide()

    def rebuild_console(self):
        """
        Rebuilds the debug menu and other debugging related UI elements.
        """
        self.coords_display = pygame_gui.elements.UILabel(
            pygame.Rect((0, 0), (-1, -1)),
            "(0, 0)",
            object_id=get_text_box_theme(),
        )

        self.coords_display.change_layer(9000)
        self.coords_display.text_colour = (255, 0, 0)
        self.coords_display.disable()
        self.coords_display.rebuild()
        self.coords_display.hide()

        self.fps_display = pygame_gui.elements.UILabel(
            pygame.Rect((0, 0), (-1, -1)), "0 fps", object_id=get_text_box_theme()
        )

        self.debug_menu = DebugMenu(
            pygame.Rect(
                (0, 0),
                (
                    pygame.display.get_surface().get_width() / 1.35,
                    pygame.display.get_surface().get_height() / 1.35,
                ),
            ),
            MANAGER,
        )

    def pre_update(self, clock):
        """
        Updates *before* the UI has been drawn.
        """

        # Showcoords
        if game.debug_settings["showcoords"]:
            if self.coords_display.visible == 0:
                self.coords_display.show()

            _ = pygame.mouse.get_pos()
            self.coords_display.set_text(
                f"({round(_[0] - offset[0] // screen_scale)}, "
                f"{round(_[1] - offset[1] // screen_scale)})"
            )
            self.coords_display.set_position((_[0] + 10, _[1] + 10))
            del _
        else:
            if self.coords_display.visible == 1:
                self.coords_display.hide()
                self.coords_display.set_text("(0, 0)")
                self.coords_display.set_position((0, 0))

        if game.debug_settings["showfps"]:
            if self.fps_display.visible == 0:
                self.fps_display.show()

            self.fps_display.set_text(f"{round(clock.get_fps(), 2)} fps")
        else:
            if self.fps_display.visible == 1:
                self.fps_display.hide()
                self.fps_display.set_text("(0, 0)")

        # Showbounds

        # visual_debug_mode
        if game.debug_settings["visualdebugmode"]:
            if not MANAGER.visual_debug_active:
                MANAGER.set_visual_debug_mode(True)
        else:
            if MANAGER.visual_debug_active:
                MANAGER.set_visual_debug_mode(False)

    def post_update(self, screen):
        """
        Updates *after* the UI has been drawn.
        """
        self.debug_menu.window_stack.move_window_to_front(self.debug_menu)
        if game.debug_settings["showbounds"]:
            elements = MANAGER.ui_group.visible
            for surface in elements:
                rect = surface[1]
                if rect in [self.coords_display.rect, self.debug_menu.rect]:
                    continue
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, (0, 255, 0), rect, 1)
                else:
                    pygame.draw.rect(screen, (255, 0, 0), rect, 1)


debug_mode = DebugMode()
