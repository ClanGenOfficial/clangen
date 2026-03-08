import pygame
from typing import Protocol

class PlatformManager(Protocol):
    """Protocol for platform-specific lifecycle and hardware interactions."""
    is_backgrounded: bool

    def handle_event(self, event, music_manager) -> bool:
        """
        Handles platform-specific events.
        Returns True if the event was a backgrounding/foregrounding event, indicating it was consumed.
        """
        ...

    def update(self):
        """Updates platform-specific state, such as native keyboard tracking."""
        ...


class DesktopManager:
    """Default manager for desktop platforms (Windows, macOS, Linux)."""
    
    def __init__(self):
        self.is_backgrounded = False

    def handle_event(self, event, music_manager) -> bool:
        return False

    def update(self):
        pass


class IOSManager:
    """Manager for iOS specific lifecycle and keyboard events."""
    
    def __init__(self):
        self.is_backgrounded = False
        self.last_focus_set = set()

    def handle_event(self, event, music_manager) -> bool:
        if event.type == pygame.APP_WILLENTERBACKGROUND:
            self.is_backgrounded = True
            if music_manager:
                pygame.mixer.music.pause()
                pygame.mixer.pause()  # Pause sound effects
            return True
            
        elif event.type == pygame.APP_DIDENTERFOREGROUND:
            self.is_backgrounded = False
            if music_manager and not music_manager.muted:
                pygame.mixer.music.unpause()
            pygame.mixer.unpause()  # Resume sound effects
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_keyboard_tap(event)
            
        return False

    def _handle_keyboard_tap(self, event):
        """Re-opens the keyboard if a focused text entry is tapped again."""
        from scripts.game_structure.screen_settings import MANAGER
        focus_set = MANAGER.get_focus_set()
        if focus_set:
            mouse_pos = pygame.mouse.get_pos()
            for element in focus_set:
                if type(element).__name__ in ('UITextEntryLine', 'UITextEntryBox'):
                    if hasattr(element, 'hover_point') and element.hover_point(mouse_pos[0], mouse_pos[1]):
                        pygame.key.start_text_input()
                        try:
                            pygame.key.set_text_input_rect(element.get_abs_rect())
                        except:
                            pass

    def update(self):
        """Updates mobile specific state, like text input focus tracking."""
        from scripts.game_structure.screen_settings import MANAGER
        focus_set = MANAGER.get_focus_set()
        
        # Detect focus changes
        if focus_set != self.last_focus_set:
            self.last_focus_set = focus_set
            
            if focus_set:
                text_entry_focused = False
                target_element = None
                for element in focus_set:
                    if type(element).__name__ in ('UITextEntryLine', 'UITextEntryBox'):
                        text_entry_focused = True
                        target_element = element
                        break
                
                if text_entry_focused:
                    pygame.key.start_text_input()
                    try:
                        pygame.key.set_text_input_rect(target_element.get_abs_rect())
                    except:
                        pass
                else:
                    pygame.key.stop_text_input()
            else:
                pygame.key.stop_text_input()


# TODO: I'll clean this up a bit later, eventually this can also manage other platform-specific features like file storage paths, etc.
# TODO: Also add "require_fullscreen" check to remove IS_IOS throughout the codebase.
def get_platform_manager() -> PlatformManager:
    """Factory function to get the appropriate PlatformManager for the current OS."""
    from scripts.housekeeping.platform import IS_IOS
    if IS_IOS:
        return IOSManager()
    return DesktopManager()
