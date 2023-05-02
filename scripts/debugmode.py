import pygame
import pygame_gui

from ast import literal_eval

from scripts.game_structure.game_essentials import MANAGER, game

from scripts.utility import get_text_box_theme

class debugConsole(pygame_gui.windows.UIConsoleWindow):
    def __init__(self, rect, manager, debug_class):
        self.debug_class = debug_class
        super().__init__(rect, manager)
    
    def process_event(self, event):
        if event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED:
            command = event.command.split(" ")
            args = command[1:]
            command = command[0]


            if command == "help":
                print("Available commands:")
                print("help")
                print("toggle <setting>")
                print("set <setting> <value>")

            if command == "toggle":
                for arg in args:
                    if arg in self.debug_class.settings:
                        self.debug_class.settings[arg] = not self.debug_class.settings[arg]
                        print(f"{arg} {'enabled' if self.debug_class.settings[arg] else 'disabled'}")
                    else:
                        print(f"Unknown setting {arg}")

            if command == "set":
                if len(args) == 2:
                    if args[0] in self.debug_class.settings:
                        try:
                            self.debug_class.settings[args[0]] = literal_eval(args[1])
                            print(f"{args[0]} set to {args[1]}")
                        except:
                            print(f"Invalid value {args[1]}")
                    else:
                        print(f"Unknown setting {args[0]}")
                else:
                    print("Invalid syntax")
        
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



        self.console = debugConsole(pygame.Rect((0, 0), (400, 400)), MANAGER, self)

        self.console.hide()

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