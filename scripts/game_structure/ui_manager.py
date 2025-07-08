import io
import os
from typing import Tuple, Optional, Union, List, Dict

import pygame
import pygame_gui
from pygame_gui import PackageResource
from pygame_gui.core import UIWindowStack, ObjectID
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import (
    IUIElementInterface,
    IUIManagerInterface,
    IUITooltipInterface,
)
from pygame_gui.core.resource_loaders import IResourceLoader
from pygame_gui.elements import UITooltip


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
        self.root_container.is_window_root_container = True

        self.ui_window_stack = None
        self.ui_window_stack = UIWindowStack(
            self.window_resolution, self.root_container
        )

    def create_tool_tip(
        self,
        text: str,
        position: Tuple[int, int],
        hover_distance: Tuple[int, int],
        parent_element: IUIElementInterface,
        object_id: ObjectID,
        *,
        wrap_width: Optional[int] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
    ) -> IUITooltipInterface:
        """
        Creates a tool tip ands returns it. Have hidden this away in the manager, so we can call it
        from other UI elements and create tool tips without creating cyclical import problems.

        :param text: The tool tips text, can utilise the HTML subset used in all UITextBoxes.
        :param position: The screen position to create the tool tip for.
        :param hover_distance: The distance we should hover away from our target position.
        :param parent_element: The UIElement that spawned this tool tip.
        :param object_id: the object_id of the tooltip.
        :param wrap_width: an optional width for the tool tip, will overwrite any value from the theme file.
        :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                            useful when you have multiple translations that need variables inserted
                            in the middle.

        :return: A tool tip placed somewhere on the screen.
        """
        tool_tip = UITooltip(
            text,
            hover_distance,
            self,
            text_kwargs=text_kwargs,
            parent_element=parent_element,
            object_id=object_id,
            wrap_width=wrap_width,
        )
        tool_tip.find_valid_position(pygame.math.Vector2(position[0], position[1]))
        return tool_tip

    def set_offset(self, offset: Tuple[int, int]):
        """
        Sets the screen offset.

        :param offset: the offset to set
        """
        self.offset = offset
        self.root_container.set_position(offset)
        self.ui_window_stack.root_container.set_position(offset)


class UIManagerContainer(
    pygame_gui.core.UIContainer,
    pygame_gui.core.UIElement,
    pygame_gui.core.interfaces.IUIContainerInterface,
    pygame_gui.core.interfaces.IContainerLikeInterface,
):
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
