import os
import io
from typing import Tuple, Optional, Union, List

import pygame
import pygame_gui
from pygame_gui import PackageResource
from pygame_gui.core import UIContainer, UIWindowStack
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IUIElementInterface, IUIManagerInterface
from pygame_gui.core.resource_loaders import IResourceLoader


class UIManager(pygame_gui.UIManager):
    def __init__(
        self,
        window_resolution: Tuple[int, int],
        offset: Tuple[int, int] = None,
        screen_scale: float = 1,
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
        self.screen_scale = screen_scale

        self.root_container.kill()
        self.root_container = None
        self.root_container = UIManagerContainer(
            pygame.Rect((0, 0), self.window_resolution),
            self,
            starting_height=1,
            container=None,
            parent_element=None,
            object_id="#root_container",
            screen_scale=screen_scale,
        )
        self.root_container.set_focus_set(None)
        self.root_container.set_position(offset)

        self.ui_window_stack = None
        self.ui_window_stack = UIWindowStack(
            self.window_resolution, self.root_container
        )


class UIManagerContainer(pygame_gui.core.UIContainer):
    """For exclusive use by the UIManager to ensure we blit backgrounds to the right place"""

    def __init__(
        self,
        relative_rect: RectLike,
        manager: IUIManagerInterface,
        starting_height: int,
        container,
        parent_element,
        object_id,
        screen_scale: float,
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
        )
        self.screen_scale = screen_scale

    # def add_element(self, element: IUIElementInterface):
    #     """
    #     Add a UIElement to the container. The UI's relative_rect parameter will be relative to
    #     this container.
    #
    #     :param element: A UIElement to add to this container.
    #
    #     """
    #     element.rect = pygame.Rect(
    #         element.rect[0] * self.screen_scale,
    #         element.rect[1] * self.screen_scale,
    #         element.rect[2],
    #         element.rect[3],
    #     )
    #     element.change_layer(self._layer + element.get_starting_height())
    #     self.elements.append(element)
    #     self.calc_add_element_changes_thickness(element)
    #     if not self.is_enabled:
    #         element.disable()
    #     if not self.visible:
    #         if hasattr(element, "hide"):
    #             element.hide()
