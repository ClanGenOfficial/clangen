import pygame
import pygame_gui
from pygame_gui.core.text.html_parser import HTMLParser
from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.utility import translate
from scripts.game_structure import image_cache
import html


class UIImageButton(pygame_gui.elements.UIButton):
    """Subclass of pygame_gui's button class. This allows for auto-scaling of the
        button image."""

    def _set_any_images_from_theme(self):

        changed = False
        normal_image = None
        try:
            normal_image = self.ui_theme.get_image('normal_image', self.combined_element_ids)
            normal_image = pygame.transform.scale(normal_image, self.relative_rect.size)  # auto-rescale the image
        except LookupError:
            normal_image = None
        finally:
            if normal_image != self.normal_image:
                self.normal_image = normal_image
                self.hovered_image = normal_image
                self.selected_image = normal_image
                self.disabled_image = normal_image
                changed = True

        hovered_image = None
        try:
            hovered_image = self.ui_theme.get_image('hovered_image', self.combined_element_ids)
            hovered_image = pygame.transform.scale(hovered_image, self.relative_rect.size)  # auto-rescale the image
        except LookupError:
            hovered_image = self.normal_image
        finally:
            if hovered_image != self.hovered_image:
                self.hovered_image = hovered_image
                changed = True

        selected_image = None
        try:
            selected_image = self.ui_theme.get_image('selected_image', self.combined_element_ids)
            selected_image = pygame.transform.scale(selected_image, self.relative_rect.size)  # auto-rescale the image
        except LookupError:
            selected_image = self.normal_image
        finally:
            if selected_image != self.selected_image:
                self.selected_image = selected_image
                changed = True

        disabled_image = None
        try:
            disabled_image = self.ui_theme.get_image('disabled_image', self.combined_element_ids)
            disabled_image = pygame.transform.scale(disabled_image, self.relative_rect.size)  # auto-rescale the image
        except LookupError:
            disabled_image = self.normal_image
        finally:
            if disabled_image != self.disabled_image:
                self.disabled_image = disabled_image
                changed = True

        return changed


class UISpriteButton():
    '''This is for use with the cat sprites. It wraps together a UIImage and Transparent Button.
        For most functions, this can be used exactly like other pygame_gui elements. '''

    def __init__(self, relative_rect, sprite, cat_id=None, visible=1, cat_object=None, starting_height=1,
                 manager=None):

        # We have to scale the image before putting it into the image object. Otherwise, the method of upscaling that UIImage uses will make the pixel art fuzzy
        self.image = pygame_gui.elements.UIImage(relative_rect, pygame.transform.scale(sprite, relative_rect.size),
                                                 visible=visible, manager=manager)
        self.image.disable()
        # The transparent button. This a subclass that UIButton that aslo hold the cat_id.
        self.button = CatButton(relative_rect, visible=visible, cat_id=cat_id, cat_object=cat_object,
                                starting_height=starting_height, manager=manager)

    def return_cat_id(self):
        return self.button.return_cat_id()

    def return_cat_object(self):
        return self.button.return_cat_object()

    def enable(self):
        self.button.enable()

    def disable(self):
        self.button.disable()

    def hide(self):
        self.image.hide()
        self.button.hide()

    def show(self):
        self.image.show()
        self.button.show()

    def kill(self):
        self.button.kill()
        self.image.kill()
        del self

    def set_image(self, new_image):
        self.image.set_image(new_image)

    '''This is to simplify event handling. Rather that writing 
            'if event.ui_element = cat_sprite_object.button'
            you can treat is as any other single pygame UI element and write:
            'if event.ui_element = cat_sprite_object. '''

    def __eq__(self, __o: object) -> bool:
        if self.button == __o:
            return True
        else:
            return False


class CatButton(pygame_gui.elements.UIButton):
    '''Basic UIButton subclass for at sprite buttons. It stores the cat ID. '''

    def __init__(self, relative_rect, cat_id=None, visible=True, cat_object=None, starting_height=1, manager=None):
        self.cat_id = cat_id
        self.cat_object = cat_object
        super().__init__(relative_rect, "", object_id="#image_button", visible=visible,
                         starting_height=starting_height, manager=manager)

    def return_cat_id(self):
        return self.cat_id

    def return_cat_object(self):
        return self.cat_object

    def set_id(self, id):
        self.cat_id = id


class UITextBoxTweaked(pygame_gui.elements.UITextBox):
    """The default class has 1.25 line spacing. It would be fairly easy to allow the user to change that,
    but it doesn't allow it... for some reason This class only exists as a way to specify the line spacing. Please
    only use if you want to have control over the line spacing. """

    def __init__(self,
                 html_text: str,
                 relative_rect,
                 manager = None,
                 line_spacing = 1,
                 wrap_to_height: bool = False,
                 layer_starting_height: int = 1,
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
                         layer_starting_height=layer_starting_height,
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
                 layer_starting_height: int = 1,
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
                                         layer_starting_height=layer_starting_height,
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

class UIRelationStatusBar():
    """ Wraps together a status bar """

    def __init__(self,
                 relative_rect,
                 percent_full=0,
                 positive_trait=True,
                 dark_mode=False,
                 manager=None,
                 style="bars"):

        # Change the color of the bar depending on the value and if it's a negative or positive trait
        if percent_full > 49:
            if positive_trait:
                theme = "#relation_bar_pos"
            else:
                theme = "#relation_bar_neg"
        else:
            theme = "#relation_bar"

        # Determine dark mode or light mode
        if dark_mode:
            theme += "_dark"

        self.status_bar = pygame_gui.elements.UIStatusBar(relative_rect, object_id=theme, manager=manager)
        self.status_bar.percent_full = percent_full / 100

        # Now to make the overlay
        overlay_path = "resources/images/"
        if style == "bars":
            if dark_mode:
                overlay_path += "relations_border_bars_dark.png"
            else:
                overlay_path += "relations_border_bars.png"
        elif style == "dots":
            if dark_mode:
                overlay_path += "relations_border_dots_dark.png"
            else:
                overlay_path += "relations_border_dots.png"

        image = pygame.transform.scale(image_cache.load_image(overlay_path).convert_alpha(), (relative_rect[2], relative_rect[3]))

        self.overlay = pygame_gui.elements.UIImage(relative_rect, image, manager=manager)

    def kill(self):
        self.status_bar.kill()
        self.overlay.kill()
        del self


class IDImageButton(UIImageButton):
    """Class to handle the "involved cats" button on the events page. It stores the IDs of the cat's involved."""

    def __init__(self,
                 relative_rect,
                 text="",
                 ids=None,
                 object_id=None,
                 container=None,
                 manager=None,
                 layer_starting_height=1):

        if ids:
            self.ids = ids
        else:
            self.ids = None

        super().__init__(relative_rect, text, object_id=object_id, container=container,
                         starting_height=layer_starting_height, manager=manager)
        # This button will auto-disable if no ids are entered.
        if not self.ids:
            self.disable()

