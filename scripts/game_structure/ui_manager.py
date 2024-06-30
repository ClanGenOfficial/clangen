import os
import io
from typing import Tuple, Optional, Union, List

import pygame
import pygame_gui
from pygame_gui import PackageResource
from pygame_gui.core import UIContainer, UIWindowStack
from pygame_gui.core.resource_loaders import IResourceLoader


class UIManager(pygame_gui.UIManager):
    def __init__(
        self,
        window_resolution: Tuple[int, int],
        offset: Tuple[int, int] = None,
        theme_path: Optional[
            Union[str, os.PathLike, io.StringIO, PackageResource, dict]
        ] = None,
        enable_live_theme_updates: bool = True,
        resource_loader: Optional[IResourceLoader] = None,
        starting_language: str = "en",
        translation_directory_paths: Optional[List[str]] = None,
    ):
        super().__init__(
            window_resolution,
            theme_path,
            enable_live_theme_updates,
            resource_loader,
            starting_language,
            translation_directory_paths,
        )
        self.offset = offset

        self.root_container.kill()
        self.root_container = None
        self.root_container = UIContainer(
            pygame.Rect(offset, self.window_resolution),
            self,
            starting_height=1,
            container=None,
            parent_element=None,
            object_id="#root_container",
        )
        self.root_container.set_focus_set(None)

        self.ui_window_stack = None
        self.ui_window_stack = UIWindowStack(
            self.window_resolution, self.root_container
        )
