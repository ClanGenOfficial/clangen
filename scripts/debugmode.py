import pygame
import pygame_gui

from ast import literal_eval

from scripts.game_structure.game_essentials import MANAGER, game

from scripts.utility import get_text_box_theme

class debugConsole(pygame_gui.windows.UIConsoleWindow):
    def __init__(self, rect, manager, debug_class):
        self.debug_class = debug_class
        self.accepted_eval_warning = False
        super().__init__(rect, manager, window_title="Debug Console", object_id="#debug_console", visible=0)
    
    def process_event(self, event):
        if event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED:
            command = event.command.split(" ")
            args = command[1:]
            command = command[0]

            # TODO: Use a switch statement here once we phase out python 3.7    pylint: disable=fixme

            if command == "help":
                self.add_output_line_to_log("Available commands:")
                self.add_output_line_to_log("help")
                self.add_output_line_to_log("toggle <setting>")
                self.add_output_line_to_log("set <setting> <value>")
                self.add_output_line_to_log("eval <code>")
                self.add_output_line_to_log("understandrisks")
                self.add_output_line_to_log("")
                self.add_output_line_to_log("Available settings:")
                for setting in self.debug_class.settings:
                    self.add_output_line_to_log(setting)

            elif command == "toggle":
                for arg in args:
                    if arg in self.debug_class.settings:
                        self.debug_class.settings[arg] = not self.debug_class.settings[arg]
                        self.add_output_line_to_log(f"{arg} {'enabled' if self.debug_class.settings[arg] else 'disabled'}")
                    else:
                        self.add_output_line_to_log(f"Unknown setting {arg}")

            elif command == "set":
                if len(args) == 2:
                    if args[0] in self.debug_class.settings:
                        try:
                            self.debug_class.settings[args[0]] = literal_eval(args[1])
                            self.add_output_line_to_log(f"{args[0]} set to {args[1]}")
                        except:
                            self.add_output_line_to_log(f"Invalid value {args[1]}")
                    else:
                        self.add_output_line_to_log(f"Unknown setting {args[0]}")
                else:
                    self.add_output_line_to_log("Invalid syntax")
            
            elif command == "eval":
                if not self.accepted_eval_warning:
                    self.add_output_line_to_log("WARNING: This command can be used to run code in your game. Only use this if you know what you're doing.")
                    self.add_output_line_to_log("If you have been told to use this by anyone other than the official clangen discord contributors, BLOCK THEM IMMEDIATELY.")
                    self.add_output_line_to_log("If you are not sure what this means, DO NOT USE THIS COMMAND.")
                    self.add_output_line_to_log("To disable this warning, type \"understandrisks\".")
                    self.accepted_eval_warning = True
                else:
                    try:
                        output = eval(" ".join(args)) # pylint: disable=eval-used
                        self.add_output_line_to_log(output)
                    except Exception as e:
                        self.add_output_line_to_log("Eval failed: " + str(e))
            elif command == "understandrisks":
                self.add_output_line_to_log("You have disabled the warning for the eval command. Any code you run is your responsibility.")
                self.accepted_eval_warning = True
            

            else:
                self.add_output_line_to_log(f"Unknown command {command}")
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            cmds = ["help", "toggle", "set", "eval", "understandrisks"]
            if len(self.command_entry.text) != 0:
                for cmd in cmds:
                    if cmd.startswith(self.command_entry.text):
                        self.command_entry.set_text(f"{cmd}")
                        break

        
        return super().process_event(event)

    


class debugMode:
    def __init__(self):
        self.settings = {
            "showcoords": False,
            "showbounds": False,
            "visualdebugmode": False,
            "showfps": False
        }

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



        self.console = debugConsole(pygame.Rect((0, 0), (1600, 300)), MANAGER, self)


        self.coords_display.text_colour = (255, 0, 0)
        self.coords_display.disable()
        self.coords_display.rebuild()
        self.coords_display.hide()
    

    def toggle_console(self):
        if self.console.visible == 0:
            self.console.show()
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
        if self.settings['showcoords']:
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
        

        if self.settings['showfps']:
            if self.fps_display.visible == 0:
                self.fps_display.show()
            
            self.fps_display.set_text(f"{round(clock.get_fps(), 2)} fps")
        else:
            if self.fps_display.visible == 1:
                self.fps_display.hide()
                self.fps_display.set_text("(0, 0)")
        
        # Showbounds



        # visual_debug_mode
        if self.settings['visualdebugmode']:
            if not MANAGER.visual_debug_active:
                MANAGER.set_visual_debug_mode(True)
        else:
            if MANAGER.visual_debug_active:
                MANAGER.set_visual_debug_mode(False)

    
    def update2(self, screen):

        if self.settings['showbounds']:
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