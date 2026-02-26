import html

import pygame
import pygame_gui
from pygame_gui.core import TextBoxLayout
from pygame_gui.core.text import HTMLParser
from pygame_gui.core.utility import translate


class UITextBoxTweaked(pygame_gui.elements.UITextBox):
    """The default class has 1.25 line spacing. It would be fairly easy to allow the user to change that,
    but it doesn't allow it... for some reason This class only exists as a way to specify the line spacing. Please
    only use if you want to have control over the line spacing."""

    def __init__(
        self,
        html_text: str,
        relative_rect,
        manager=None,
        line_spacing: float = 1,
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
        allow_split_dashes: bool = True,
    ):
        self.line_spaceing = line_spacing

        super().__init__(
            html_text,
            relative_rect,
            manager=manager,
            container=container,
            starting_height=starting_height,
            wrap_to_height=wrap_to_height,
            parent_element=parent_element,
            anchors=anchors,
            object_id=object_id,
            visible=visible,
            pre_parsing_enabled=pre_parsing_enabled,
            text_kwargs=text_kwargs,
            allow_split_dashes=allow_split_dashes,
        )

    # 99% of this is copy-pasted from the original function.
    def _reparse_and_rebuild(self):
        self.parser = HTMLParser(
            self.ui_theme,
            self.combined_element_ids,
            self.link_style,
            line_spacing=self.line_spaceing,
        )  # THIS IS THE ONLY LINE CHANGED WITH THIS SUBCLASS
        self.rebuild()

    # 99% of this is copy-pasted from the original function.
    def parse_html_into_style_data(self):
        """
        Parses HTML styled string text into a format more useful for styling pygame.freetype
        rendered text.
        """
        feed_input = self.html_text
        if self.plain_text_display_only:
            feed_input = html.escape(
                feed_input
            )  # might have to add true to second param here for quotes
        feed_input = self._pre_parse_text(
            translate(feed_input, **self.text_kwargs) + self.appended_text
        )
        self.parser.feed(feed_input)

        default_font = self.ui_theme.get_font_dictionary().find_font(
            font_name=self.parser.default_style["font_name"],
            font_size=self.parser.default_style["font_size"],
            bold=self.parser.default_style["bold"],
            italic=self.parser.default_style["italic"],
        )
        default_font_data = {
            "font": default_font,
            "font_colour": self.parser.default_style["font_colour"],
            "bg_colour": self.parser.default_style["bg_colour"],
        }
        self.text_box_layout = TextBoxLayout(
            self.parser.layout_rect_queue,
            pygame.Rect((0, 0), (self.text_wrap_rect[2], self.text_wrap_rect[3])),
            pygame.Rect((0, 0), (self.text_wrap_rect[2], self.text_wrap_rect[3])),
            line_spacing=self.line_spaceing,
            # THIS IS THE ONLY LINE CHANGED WITH THIS SUBCLASS
            default_font_data=default_font_data,
            allow_split_dashes=self.allow_split_dashes,
        )
        self.parser.empty_layout_queue()
        if self.text_wrap_rect[3] == -1:
            self.text_box_layout.view_rect.height = (
                self.text_box_layout.layout_rect.height
            )

        self._align_all_text_rows()
        self.text_box_layout.finalise_to_new()
