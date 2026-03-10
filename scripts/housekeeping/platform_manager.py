import pygame
import sys
import os
import time
import logging
from typing import Protocol

IS_IOS = getattr(sys, "platform", "") == "ios"

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

    def configure_logging(self):
        """Configures system-wide logging, including stdout/stderr redirection if appropriate."""
        ...

    def user_data_dir(self, appname=None, appauthor=None, version=None, roaming=False) -> str:
        """Returns the platform-specific directory for user data."""
        ...

    def always_use_fullscreen(self) -> bool:
        """Returns True if the platform requires the application to always be in fullscreen mode."""
        ...

    def allow_quit_button(self) -> bool:
        """Returns True if the platform allows an explicit 'Quit' button in the UI."""
        ...

    def is_source_build(self) -> bool:
        """Returns True if the application is running from source code, rather than a bundle."""
        ...

    def setup_environment(self, directory: str):
        """Performs early-boot environment setup, such as changing the working directory."""
        ...


class DesktopManager:
    """Default manager for desktop platforms (Windows, macOS, Linux)."""

    def __init__(self):
        self.is_backgrounded = False

    def handle_event(self, event, music_manager) -> bool:
        return False

    def update(self):
        pass

    def configure_logging(self):
        from scripts.housekeeping.datadir import get_log_dir
        from scripts.housekeeping.stream_duplexer import UnbufferedStreamDuplexer
        from scripts.housekeeping.log_cleanup import prune_logs

        timestr = time.strftime("%Y%m%d_%H%M%S")

        try:
            stdout_file = open(get_log_dir() + f"/stdout_{timestr}.log", "a", encoding="utf-8")
            stderr_file = open(get_log_dir() + f"/stderr_{timestr}.log", "a", encoding="utf-8")
            sys.stdout = UnbufferedStreamDuplexer(sys.stdout, stdout_file)
            sys.stderr = UnbufferedStreamDuplexer(sys.stderr, stderr_file)
        except (IOError, PermissionError):
            # If we can't open the files, just continue with normal stdout/stderr
            pass

        formatter = logging.Formatter(
            "%(name)s - %(levelname)s - %(filename)s / %(funcName)s / %(lineno)d - %(message)s"
        )

        # Logging for file
        log_file_name = get_log_dir() + f"/clangen_{timestr}.log"
        try:
            file_handler = logging.FileHandler(log_file_name)
            file_handler.setFormatter(formatter)
            # Only log errors to file
            file_handler.setLevel(logging.ERROR)
            logging.root.addHandler(file_handler)
        except (IOError, PermissionError):
            pass

        # Logging for console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logging.root.addHandler(stream_handler)

        prune_logs(logs_to_keep=10, retain_empty_logs=False)

    def user_data_dir(self, appname=None, appauthor=None, version=None, roaming=False) -> str:
        from platformdirs import user_data_dir as _user_data_dir
        return _user_data_dir(appname, appauthor, version, roaming)

    def always_use_fullscreen(self) -> bool:
        return False

    def allow_quit_button(self) -> bool:
        return True

    def is_source_build(self) -> bool:
        return not getattr(sys, "frozen", False)

    def setup_environment(self, directory: str):
        if directory:
            os.chdir(directory)


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

    def configure_logging(self):
        """On iOS, we just use the normal console (stdout/stderr) and don't write to files."""
        formatter = logging.Formatter(
            "%(name)s - %(levelname)s - %(filename)s / %(funcName)s / %(lineno)d - %(message)s"
        )

        # Logging for console only
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logging.root.addHandler(stream_handler)

    def user_data_dir(self, appname=None, appauthor=None, version=None, roaming=False) -> str:
        # Try to get the iCloud Ubiquity container
        try:
            from rubicon.objc import ObjCClass
            NSFileManager = ObjCClass('NSFileManager')
            fileManager = NSFileManager.defaultManager

            # This returns the URL for the iCloud container defined in your entitlements
            url = fileManager.URLForUbiquityContainerIdentifier_(None)
            if url:
                # Append 'Documents' to the iCloud path.
                # Files in the 'Documents' subfolder of the ubiquity container
                # are automatically visible in the user's iCloud Drive.
                icloud_path = os.path.join(str(url.path), "Documents")
                if not os.path.exists(icloud_path):
                    os.makedirs(icloud_path, exist_ok=True)
                return icloud_path
        except Exception as e:
            # Fallback if rubicon is missing or iCloud is disabled
            print(f"iCloud not available, using local storage: {e}")

        # Fallback to local app Documents directory (On My iPad)
        return os.path.join(os.environ.get("HOME", "."), "Documents")

    def always_use_fullscreen(self) -> bool:
        return True

    def allow_quit_button(self) -> bool:
        return False

    def is_source_build(self) -> bool:
        return False

    def setup_environment(self, directory: str):
        pass

# TODO: I'll clean this up a bit later, eventually this can also manage other platform-specific features like file storage paths, etc.
# TODO: Also add "require_fullscreen" check to remove IS_IOS throughout the codebase.
def get_platform_manager() -> PlatformManager:
    """Factory function to get the appropriate PlatformManager for the current OS."""
    if IS_IOS:
        return IOSManager()
    return DesktopManager()

def user_data_dir(appname=None, appauthor=None, version=None, roaming=False) -> str:
    """Convenience function to get the user data directory from the platform manager."""
    return get_platform_manager().user_data_dir(appname, appauthor, version, roaming)
