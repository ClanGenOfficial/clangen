from pygame_gui.core.text.html_parser import HTMLParser
from typing import Dict, Optional, Tuple, Union

import pygame
import pygame_gui
from scripts.web import is_web
from pygame_gui.core.interfaces import IUIManagerInterface, IContainerLikeInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core import ObjectID
from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.utility import translate
import html


class UITextBox(pygame_gui.elements.UITextBox):
    """
    Shim UITextBox that works on web
    """
    def __init__(self,
                 html_text: str,
                 relative_rect: Union[pygame.Rect, Tuple[int, int, int, int]],
                 manager: Optional[IUIManagerInterface] = None,
                 wrap_to_height: bool = False,
                 starting_height: int = 1,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1,
                 *,
                 pre_parsing_enabled: bool = True,
                 text_kwargs: Optional[Dict[str, str]] = None,
                 allow_split_dashes: bool = True,
                 plain_text_display_only: bool = False,
                 should_html_unescape_input_text: bool = False):
    
        if is_web:
            # pylint: disable=unexpected-keyword-arg
            super().__init__(
            html_text=html_text,
                relative_rect=relative_rect,
                manager=manager,
                wrap_to_height=wrap_to_height,
                layer_starting_height=starting_height,
                container=container,
                parent_element=parent_element,
                object_id=object_id,
                anchors=anchors,
                visible=visible,
                pre_parsing_enabled=pre_parsing_enabled,
                text_kwargs=text_kwargs,
                allow_split_dashes=allow_split_dashes,
                plain_text_display_only=plain_text_display_only,
                should_html_unescape_input_text=should_html_unescape_input_text
            )
        else:
            super().__init__(
                html_text=html_text,
                relative_rect=relative_rect,
                manager=manager,
                wrap_to_height=wrap_to_height,
                starting_height=starting_height,
                container=container,
                parent_element=parent_element,
                object_id=object_id,
                anchors=anchors,
                visible=visible,
                pre_parsing_enabled=pre_parsing_enabled,
                text_kwargs=text_kwargs,
                allow_split_dashes=allow_split_dashes,
                plain_text_display_only=plain_text_display_only,
                should_html_unescape_input_text=should_html_unescape_input_text
            )   


class UITextBoxTweaked(UITextBox):
    """The default class has 1.25 line spacing. It would be fairly easy to allow the user to change that,
    but it doesn't allow it... for some reason This class only exists as a way to specify the line spacing. Please
    only use if you want to have control over the line spacing. """

    def __init__(self,
                 html_text: str,
                 relative_rect,
                 manager = None,
                 line_spacing = 1,
                 wrap_to_height: bool = False,
                 starting_height: int = 1,
                 container=None,
                 parent_element=None,
                 object_id=None,
                 anchors=None,
                 visible: int = 1,
                 *,
                 pre_parsing_enabled: bool = True,
                 text_kwargs=None,
                 allow_split_dashes: bool = True):

        self.line_spaceing = line_spacing

        super().__init__(html_text, relative_rect, manager=manager, container=container,
                         starting_height=starting_height,
                         wrap_to_height=wrap_to_height,
                         parent_element=parent_element,
                         anchors=anchors,
                         object_id=object_id,
                         visible=visible,
                         pre_parsing_enabled=pre_parsing_enabled,
                         text_kwargs=text_kwargs,
                         allow_split_dashes=allow_split_dashes
                         )

    # 99% of this is copy-pasted from the original function.
    def _reparse_and_rebuild(self):
        self.parser = HTMLParser(self.ui_theme, self.combined_element_ids,
                                 self.link_style,
                                 line_spacing=self.line_spaceing)  # THIS IS THE ONLY LINE CHANGED WITH THIS SUBCLASS
        self.rebuild()

    # 99% of this is copy-pasted from the original function.
    def parse_html_into_style_data(self):
        """
        Parses HTML styled string text into a format more useful for styling pygame.freetype
        rendered text.
        """
        feed_input = self.html_text
        if self.plain_text_display_only:
            feed_input = html.escape(feed_input)  # might have to add true to second param here for quotes
        feed_input = self._pre_parse_text(translate(feed_input, **self.text_kwargs) + self.appended_text)
        self.parser.feed(feed_input)

        default_font = self.ui_theme.get_font_dictionary().find_font(
            font_name=self.parser.default_style['font_name'],
            font_size=self.parser.default_style['font_size'],
            bold=self.parser.default_style['bold'],
            italic=self.parser.default_style['italic'])
        default_font_data = {"font": default_font,
                             "font_colour": self.parser.default_style['font_colour'],
                             "bg_colour": self.parser.default_style['bg_colour']
                             }
        self.text_box_layout = TextBoxLayout(self.parser.layout_rect_queue,
                                             pygame.Rect((0, 0), (self.text_wrap_rect[2],
                                                                  self.text_wrap_rect[3])),
                                             pygame.Rect((0, 0), (self.text_wrap_rect[2],
                                                                  self.text_wrap_rect[3])),
                                             line_spacing=self.line_spaceing,
                                             # THIS IS THE ONLY LINE CHANGED WITH THIS SUBCLASS
                                             default_font_data=default_font_data,
                                             allow_split_dashes=self.allow_split_dashes)
        self.parser.empty_layout_queue()
        if self.text_wrap_rect[3] == -1:
            self.text_box_layout.view_rect.height = self.text_box_layout.layout_rect.height

        self._align_all_text_rows()
        self.text_box_layout.finalise_to_new()

class UIImageTextBox():
    """Wraps together an image and an text box. Creates text boxes with an image background"""

    def __init__(self,
                 html_text: str,
                 image,
                 relative_rect,
                 manager=None,
                 line_spacing=1.25,
                 wrap_to_height: bool = False,
                 starting_height: int = 1,
                 container=None,
                 object_id=None,
                 anchors=None,
                 visible: int = 1,
                 *,
                 pre_parsing_enabled: bool = True,
                 text_kwargs=None,
                 allow_split_dashes: bool = True) -> None:
        # FIXME: layer_starting_height throws a TypeError, not sure if this is a valid argument.
        #self.image = pygame_gui.elements.UIImage(relative_rect,
        #                                         image,
        #                                         layer_starting_height=layer_starting_height,
        #                                         container=container,
        #                                         anchors=anchors,
        #                                         visible=visible)
        # FIXME: This doesn't work as intended.
        self.image = pygame_gui.elements.UIImage(relative_rect,
                                                 image,
                                                 container=container,
                                                 anchors=anchors,
                                                 visible=visible)
            
        self.text_box = UITextBoxTweaked(html_text, relative_rect, object_id=object_id,
                                         starting_height=starting_height,
                                         container=container, anchors=anchors, visible=visible, text_kwargs=text_kwargs,
                                         allow_split_dashes=allow_split_dashes, wrap_to_height=wrap_to_height,
                                         line_spacing=line_spacing,
                                         manager=manager, pre_parsing_enabled=pre_parsing_enabled)

    def hide(self):
        self.image.hide()
        self.text_box.hide()

    def show(self):
        self.image.show()
        self.text_box.show()

    def kill(self):
        self.text_box.kill()
        self.image.kill()
        del self

    def set_image(self, new_image):
        self.image.set_image(new_image)