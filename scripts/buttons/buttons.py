import i18n
import pygame
import pygame_gui
import re
import warnings
from os import listdir
from typing import Union, Optional, Dict


from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import MANAGER, game
from scripts.buttons.color_palette import Palette
from scripts.ui.elements.buttons.UISpriteButton import UISpriteButton
try:
    import ujson
except:
    import json as ujson

pygame.font.init()
DEBUG = True

class _Language:
    """Class for rendering button text in other languages, from languages/buttons/(lang).json"""
    LANGUAGE: str = "en-us"
    supported_languages: list[str] = [x.removesuffix('.json').lstrip("buttons.") for x in listdir('languages/buttons/')]

    i18n.load_path.append('languages/buttons')
    i18n.set('file_format', 'json')
    i18n.set('locale', LANGUAGE)
    # global dictionary for symbol lookup
    dict_global = {
        "#cat_tab_3_blank_button": "",
        "#cat_tab_4_blank_button": "",
        "#random_dice_button": "{DICE}",
        "#paw_patrol_button": "{PATROL_PAW}",
        "#claws_patrol_button": "{PATROL_CLAW}",
        "#mouse_patrol_button": "{PATROL_MOUSE}",
        "#herb_patrol_button": "{PATROL_HERB}",
        "#patrol_last_page": "{ARROW_LEFT_SHORT}",
        "#patrol_next_page": "{ARROW_RIGHT_SHORT}",
        "#arrow_right_button": "{ARROW_RIGHT_SHORT}",
        "#arrow_left_button": "{ARROW_LEFT_SHORT}",
        "#your_clan_button": "{YOUR_CLAN}",
        "#outside_clan_button": "{OUTSIDE_CLAN}",
        "#starclan_button": "{STARCLAN}",
        "#unknown_residence_button": "{UNKNOWN_RESIDENCE}",
        "#dark_forest_button": "{DARK_FOREST}",
        "#leader_ceremony_button": "{LEADER_CEREMONY}",
        "#mediation_button": "{MEDIATION}",
        "#exit_window_button": "{EXIT}",
    }

    @staticmethod
    def set_language(language: str) -> None:
        """Sets the language to be used for button text

        Args:
            language (str): The language to use, must be in languages/buttons/
        """
        if language not in _Language.supported_languages:
            raise ValueError("Language not supported")
        _Language.LANGUAGE = language
        i18n.set('locale', language)
        ButtonCache.clear_cache()
        # bodged together reload script
        game.all_screens[game.current_screen].exit_screen()
        game.all_screens[game.current_screen].screen_switches()

    @staticmethod
    def get_language() -> str:
        """Returns the currently set language

        Returns:
            str: The currently set language
        """
        return _Language.LANGUAGE

    @staticmethod
    def check(object_id: Union[str, None]) -> str:
        """Checks if the object_id is in the dictionary, and returns the appropriate string (if found)

        Args:
            object_id (str): The object_id to search for, present in UIButton

        Returns:
            str: The found language string
            default: ''
        """
        if object_id is None:
            return ''
        search_term = f"buttons.{object_id}"
        translated = i18n.t(search_term, locale=_Language.LANGUAGE)
        if translated != search_term:
            return translated
        # backup search for global
        search = _Language.dict_global.get(object_id)
        if search is not None:
            return search

        if "checkbox" in object_id:
            return '' # silently return just so it doesn't yell at you, checkbox is supposed to be blank :)
        if _Language.LANGUAGE == 'en-us':
            warnings.warn(f'text (en-us) for {object_id} not found!')
        else:
            warnings.warn(f'Translation for "{object_id}" in {_Language.LANGUAGE} not found! Using fallback language "en-us"')
            return i18n.t(search_term, locale='en-us')
        return ''

class _Style:
    text_color = (239, 229, 206)
    font = pygame.font.Font('resources/fonts/clangen.ttf', 18)

    _styles = ujson.load(open("resources/styles.json", "r", encoding="utf-8"))
    styles_round = _styles["rounded"]
    styles_hanging = _styles["hanging"]
    styles_shadow = _styles["shadow"]
    @staticmethod
    def check_round(object_id: str) -> list:
        """Checks the stylesheet to find if #object_id has rounded corners, if any

        Args:
            object_id (str): #object_id from UIButton

        Returns:
            list: List for rounded_corners, if found. 
            default: [True, True, True, True]
        """
        style = _Style.styles_round.get(object_id)
        if style is not None:
            if isinstance(style, list) and len(style) == 4:
                return style
            elif isinstance(style, bool):
                return [style, style, style, style]
        return [True, True, True, True]
    @staticmethod
    def check_hanging(object_id) -> bool:
        if object_id is None:
            return False
        style = _Style.styles_hanging.get(object_id)
        if style is not None:
            return style
        return False
    @staticmethod
    def check_shadow(object_id) -> list:
        if object_id is None:
            return [True, True, False, False]
        style = _Style.styles_shadow.get(object_id)
        if style is not None:
            if isinstance(style, list) and len(style) == 4:
                return style
        return [True, True, False, False]

class ButtonCache:
    """Custom class that allows for caching of pygame.Surface objects, and their attributes"""
    _storage = []
    @staticmethod
    # pylint: disable=unused-argument
    def load_button(object_id: str = "",
                    hover: bool = False,
                    unavailable: bool = False) -> Union[None, pygame.Surface]:
        """Attempts to load a button surface from the cache

        Args:
            size (tuple): The size of the surface to search for
            text (str, optional): The text on the surface. Defaults to "".
            hover (bool, optional): If the button is in the hovered state. Defaults to False.
            unavailable (bool, optional): If the button is disabled. Defaults to False.
            rounded_corners (Union[bool, list], optional): List of which corners should be rounded on the button, following 9-slice. Defaults to [True, True, True, True].
            shadows (Union[bool, list], optional): List of which edges should have shadows, following 9-slice. Defaults to [True, True, False, False].
            hanging (bool, optional): If the image should have 2 "ropes" on either side. Defaults to False.

        Returns:
            Union[bool, pygame.Surface]: The cached button surface
            default: None
        """
        kwargs = locals()
        keys = ["size", "text", "hover", "unavailable", "rounded_corners", "shadows", "hanging"]
        obj = [
               item for item in ButtonCache._storage
               if all(key in kwargs and kwargs[key] == item[key] for key in keys)]
        del kwargs, keys
        if len(obj) != 0:
            return obj[0]
        del obj
        return None
    @staticmethod
    def store_button(surface,
                     object_id: str = "",
                     hover: bool = False,
                     unavailable: bool = False) -> pygame.Surface:
        """Stores a surface to the cache list

        Args:
            surface (pygame.Surface): The surface to store
            size (tuple): The size of the surface to save, old feature but still used
            text (str, optional): The text on the surface. Defaults to "".
            hover (bool, optional): If the button is in the hovered state. Defaults to False.
            unavailable (bool, optional): If the button is disabled. Defaults to False.
            rounded_corners (Union[bool, list], optional): List of which corners should be rounded on the button, following 9-slice. Defaults to [True, True, True, True].
            shadows (Union[bool, list], optional): List of which edges should have shadows, following 9-slice. Defaults to [True, True, False, False].
            hanging (bool, optional): If the image should have 2 "ropes" on either side. Defaults to False.

        Returns:
            pygame.Surface: The stored surface, just to make calls easier for me
        """
        store = {
            "surface": surface,
            "hover": hover,
            "unavailable": unavailable,
            "object_id": object_id
        }
        ButtonCache._storage.append(store)
        del store
        return surface

    @staticmethod
    def clear_cache():
        ButtonCache._storage = []

class Constructor:
    @staticmethod
    def corner(palette, shadow_corner1: bool, shadow_corner2: bool, rounded: bool = True):
        surface = pygame.Surface((10, 8), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        if rounded:
            # outline
            pygame.draw.rect(surface, palette[0], (6, 2, 4, 2))
            pygame.draw.rect(surface, palette[0], (4, 4, 2, 2))
            pygame.draw.rect(surface, palette[0], (2, 6, 2, 2))
            # inline
            pygame.draw.rect(surface, palette[1], (6, 4, 4, 2))
            pygame.draw.rect(surface, palette[1], (4, 6, 2, 2))
            # fill
            if shadow_corner1 and shadow_corner2:
                pygame.draw.rect(surface, palette[3], (6, 6, 4, 2))
            else:
                pygame.draw.rect(surface, palette[2], (6, 6, 4, 2))
            return surface

        # outline
        pygame.draw.rect(surface, palette[0], (0, 0, 10, 2))
        pygame.draw.rect(surface, palette[0], (0, 0, 2, 8))
        # inline
        pygame.draw.rect(surface, palette[1], (2, 2, 8, 2))
        pygame.draw.rect(surface, palette[1], (2, 2, 2, 6))
        # fill
        pygame.draw.rect(surface, palette[2], (4, 4, 6, 2))
        if shadow_corner1:
            pygame.draw.rect(surface, palette[3], (4, 4, 6, 2))
        if shadow_corner2:
            pygame.draw.rect(surface, palette[3], (4, 4, 2, 4))
        return surface

    @staticmethod
    def edge(palette, length: int, rotate: bool = False, flip: bool = False, shadow = False):
        odd = False
        if round(length / 2) != int(length / 2):
            if not rotate:
                length += 1
                odd = True
        if length <= 0:
            length = 0
        surface = pygame.Surface((length, 6), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        # outline
        pygame.draw.rect(surface, palette[0], (0, 0, length, 2))
        # inline
        pygame.draw.rect(surface, palette[1], (0, 2, length if not odd else length-1, 2))
        # fill
        if shadow:
            pygame.draw.rect(surface, palette[3], (0, 4, length if not odd else length-1, 2))
        else:
            pygame.draw.rect(surface, palette[2], (0, 4, length if not odd else length-1, 2))

        if rotate and flip:
            surface = pygame.transform.rotate(surface, 90)
            surface = pygame.transform.flip(surface, True, False)
        elif rotate:
            surface = pygame.transform.rotate(surface, 90)
        elif flip:
            surface = pygame.transform.flip(surface, False, True)

        return surface

class BuildCache:
    _edges = {}
    _corners = {}
    @staticmethod
    def load_edge(palette: list, length: int, rotate: bool = False, flip: bool = False, shadow = False):
        if BuildCache._edges.get(hash((tuple(palette), length, rotate, flip, shadow))):
            return BuildCache._edges[hash((tuple(palette), length, rotate, flip, shadow))]

        edge = Constructor.edge(palette, length, rotate, flip, shadow)
        BuildCache._edges[hash((tuple(palette), length, rotate, flip, shadow))] = edge
        return edge

    @staticmethod
    def load_corner(palette: list, shadow_corner1: bool, shadow_corner2: bool, rounded: bool = True):
        if BuildCache._corners.get(hash((tuple(palette), shadow_corner1, shadow_corner2, rounded))):
            return BuildCache._corners[hash((tuple(palette), shadow_corner1, shadow_corner2, rounded))]

        corner = Constructor.corner(palette, shadow_corner1, shadow_corner2, rounded)
        BuildCache._corners[hash((tuple(palette), shadow_corner1, shadow_corner2, rounded))] = corner
        return corner

    @staticmethod
    def clear_cache():
        BuildCache._edges = {}
        BuildCache._corners = {}

theme = ujson.load(open("resources/theme/image_buttons.json"))
def get_image(image_id: str, combined_element_ids):
    # taken directly from pygame_gui.core.UIAppearanceTheme, modified for our use
    combined_element_ids = [id for id in combined_element_ids if '#' in id]
    if isinstance(combined_element_ids, str):
        combined_element_ids = [combined_element_ids]
    for combined_element_id in combined_element_ids:
        if (combined_element_id in theme and
            image_id in theme[combined_element_id].get('images')):
            # return theme[combined_element_id][image_id].surface
            return pygame.image.load(theme[combined_element_id]["images"][image_id]["path"]).convert_alpha()

    raise LookupError('Unable to find any image with id: ' + str(image_id) +
                        ' with combined_element_ids: ' + str(combined_element_ids))

class UIButton(UISpriteButton):
    def __init__(self, relative_rect, text = "", visible=1, starting_height=1, object_id=None,
                 manager=MANAGER, container=None, tool_tip_text=None):
        self.relative_rect = relative_rect
        self.id = object_id
        self.rounded_corners = _Style.check_round(object_id)
        self.hanging = _Style.check_hanging(object_id)
        self.shadows = _Style.check_shadow(object_id)
        self.hash = hash(self.id)

        self.state = "default"
        if text != "":
            self.text = text
        else:
            self.text = _Language.check(object_id)
        cache = ButtonCache.load_button(object_id=object_id, hover=False, unavailable=False)
        if cache:
            sprite = cache['surface']
        else:
            sprite = ButtonCache.store_button(
                        Button.new(size=relative_rect.size,
                                   text=self.text,
                                   rounded_corners=self.rounded_corners,
                                   hanging=self.hanging,
                                   shadows=self.shadows,
                                   object_id=object_id),
                        object_id, hover=False, unavailable=False)
        self.image = pyggui_UIImage(relative_rect,
                                    pygame.transform.scale(sprite, relative_rect.size),
                                    visible=visible,
                                    manager=manager,
                                    container=container,
                                    object_id=object_id,
                                    starting_height=starting_height)
        self.image.disable()
        # The transparent button. This a subclass that UIButton that also hold the cat_id.
        self.button = BaseButton(relative_rect, visible=visible,
                                starting_height=starting_height+1,
                                manager=manager, tool_tip_text=tool_tip_text,
                                internal=self, container=container)
        self.visible = visible
    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == "visible":
            self.image.visible = value
            self.button.visible = value
        elif name == "dynamic_dimensions_orig_top_left":
            self.image.dynamic_dimensions_orig_top_left = value
            self.button.dynamic_dimensions_orig_top_left = value
        elif name == "_rect":
            self.image._rect = value
            self.button._rect = value
        elif name == "blit_data":
            self.image.blit_data = value
            self.button.blit_data = value

    def rebuild(self):
        self.image.rebuild()
        self.button.rebuild()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not "id" in other.__dict__:
            return False
        return self.id == other.id
    
    @property
    def is_enabled(self):
        return self.button.is_enabled
    
class UIImageButton(pygame_gui.elements.UIButton):
    """Subclass of pygame_gui's button class. This allows for auto-scaling of the
        button image."""

    def _set_any_images_from_theme(self):
        changed = False
        normal_image = None
        self.ui_theme.load_theme("resources/theme/image_buttons.json")
        try:
            normal_image = get_image('normal_image', self.combined_element_ids)
            normal_image = pygame.transform.scale(normal_image, self.relative_rect.size)  # auto-rescale the image
            normal_image = normal_image.premul_alpha()
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
            hovered_image = get_image('hovered_image', self.combined_element_ids)
            hovered_image = pygame.transform.scale(hovered_image, self.relative_rect.size)  # auto-rescale the image
            hovered_image = hovered_image.premul_alpha()
        except LookupError:
            hovered_image = self.normal_image
        finally:
            if hovered_image != self.hovered_image:
                self.hovered_image = hovered_image
                changed = True

        selected_image = None
        try:
            selected_image = get_image('selected_image', self.combined_element_ids)
            selected_image = pygame.transform.scale(selected_image, self.relative_rect.size)  # auto-rescale the image
            selected_image = selected_image.premul_alpha()
        except LookupError:
            selected_image = self.normal_image
        finally:
            if selected_image != self.selected_image:
                self.selected_image = selected_image
                changed = True

        disabled_image = None
        try:
            disabled_image = get_image('disabled_image', self.combined_element_ids)
            disabled_image = pygame.transform.scale(disabled_image, self.relative_rect.size)  # auto-rescale the image
            disabled_image = disabled_image.premul_alpha()
        except LookupError:
            disabled_image = self.normal_image
        finally:
            if disabled_image != self.disabled_image:
                self.disabled_image = disabled_image
                changed = True

        return changed


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


class BaseButton(pygame_gui.elements.UIButton):
    def __init__(self,
                 relative_rect,
                 visible=True,
                 starting_height=1,
                 manager=MANAGER,
                 tool_tip_text=None,
                 container=None,
                 internal: UIButton=None) -> None:
        self.id = internal.id
        self.rounded_corners = internal.rounded_corners
        self.hanging = internal.hanging
        self.shadows = internal.shadows
        self.internal = internal
        self.hover = False
        super().__init__(relative_rect,
                         "", object_id="#cat_button", 
                         visible=visible,
                         starting_height=starting_height,
                         manager=manager,
                         tool_tip_text=tool_tip_text,
                         container=container)
    def on_hovered(self):
        self.hover = True
        cache = ButtonCache.load_button(
            object_id=self.internal.id, hover=True, unavailable=False
        )
        if cache:
            sprite = cache['surface']
        else:
            sprite = ButtonCache.store_button(
                Button.new(size=self.relative_rect.size,
                           text=self.internal.text, hover=True,
                           rounded_corners=self.rounded_corners,
                           hanging=self.hanging, shadows=self.shadows,
                           object_id=self.internal.id),
                object_id=self.internal.id, hover=True, unavailable=False
            )
        self.internal.image.set_image(pygame.transform.scale(sprite, self.relative_rect.size))
        super().on_hovered()
    def while_hovered(self):
        self.hover = True
    def disable(self):
        self.hover = False
        cache = ButtonCache.load_button(
            object_id=self.internal.id, unavailable=True
        )
        if cache:
            sprite = cache['surface']
        else:
            sprite = ButtonCache.store_button(
                Button.new(size=self.relative_rect.size,
                           text=self.internal.text, unavailable=True,
                           rounded_corners=self.rounded_corners,
                           hanging=self.hanging, shadows=self.shadows,
                           object_id=self.internal.id),
                object_id=self.internal.id, hover=False, unavailable=True
            )
        self.internal.image.set_image(pygame.transform.scale(sprite, self.relative_rect.size))
        super().disable()
    def enable(self):
        cache = ButtonCache.load_button(
            object_id=self.internal.id, hover=self.hover, unavailable=False
        )
        if cache:
            sprite = cache['surface']
        else:
            sprite = ButtonCache.store_button(
                Button.new(size=self.relative_rect.size,
                           text=self.internal.text, hover=self.hover,
                           rounded_corners=self.rounded_corners,
                           hanging=self.hanging, shadows=self.shadows,
                           object_id=self.internal.id),
                object_id=self.internal.id, hover=self.hover, unavailable=False
            )
        self.internal.image.set_image(pygame.transform.scale(sprite, self.relative_rect.size))
        super().enable()
    def on_unhovered(self):
        self.hover = False
        cache = ButtonCache.load_button(
            object_id=self.internal.id, hover=False, unavailable=False
        )
        if cache:
            sprite = cache['surface']
        else:
            sprite = ButtonCache.store_button(
                Button.new(size=self.relative_rect.size,
                           text=self.internal.text, hover=False,
                           rounded_corners=self.rounded_corners,
                           hanging=self.hanging, shadows=self.shadows,
                           object_id=self.internal.id),
                object_id=self.internal.id, hover=False, unavailable=False
            )
        self.internal.image.set_image(pygame.transform.scale(sprite, self.relative_rect.size))
        super().on_unhovered()
    def rebuild(self):
        for key in ['normal_bg', 'hovered_bg', 'disabled_bg', 'selected_bg', 'active_bg',  
                    'normal_text', 'hovered_text', 'disabled_text', 'selected_text','active_text', 
                    'normal_text_shadow', 'hovered_text_shadow', 'disabled_text_shadow', 
                    'selected_text_shadow', 'active_text_shadow', 'normal_border', 'hovered_border', 
                    'disabled_border', 'selected_border', 'active_border', 'link_text', 'link_hover', 'link_selected', 'text_shadow']:
            self.colours[key] = pygame.Color(0, 0, 0, 0) # yes i know this solution is hacky give me a BREAK
        super().rebuild()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, BaseButton):
            return False
        return self.id == other.id

class _Symbol:
    """Custom class for rendering symbols from an image file"""
    _color = pygame.Color(_Style.text_color)
    custom = {}
    symbols = {
        "{DICE}": "resources/images/symbols/random_dice.png",
        "{ARROW_LEFT_SHORT}": "resources/images/symbols/arrow_short.png",
        "{ARROW_LEFT_MED}": "resources/images/symbols/arrow_medium.png",
        "{PATROL_CLAW}": "resources/images/symbols/patrol_claws.png",
        "{PATROL_PAW}": "resources/images/symbols/patrol_paw.png",
        "{PATROL_MOUSE}": "resources/images/symbols/patrol_mouse.png",
        "{PATROL_HERB}": "resources/images/symbols/patrol_herb.png",
        "{YOUR_CLAN}": "resources/images/symbols/your_clan.png",
        "{OUTSIDE_CLAN}": "resources/images/symbols/outside_clan.png",
        "{STARCLAN}": "resources/images/symbols/starclan.png",
        "{UNKNOWN_RESIDENCE}": "resources/images/symbols/unknown_residence.png",
        "{DARK_FOREST}": "resources/images/symbols/dark_forest.png",
        "{LEADER_CEREMONY}": "resources/images/symbols/leader_ceremony.png",
        "{MEDIATION}": "resources/images/symbols/mediation.png",
        "{MEDIATION_APPRENTICE}: ": "resources/images/symbols/mediation_apprentice.png",
        "{EXIT}": "resources/images/symbols/exit.png",
        "{CHECKMARK}": "resources/images/symbols/checkbox_checkmark.png"
    }
    flipped_symbols = {
        "{ARROW_RIGHT_SHORT}": "resources/images/symbols/arrow_short.png",
        "{ARROW_RIGHT_MED}": "resources/images/symbols/arrow_medium.png"
    }

    @staticmethod
    def __init__(web: bool = False) -> None:
        """Populates _Symbol.custom with the appropriate custom symbols"""
        if web:
            load = _Symbol._web_load
        else:
            load = _Symbol.load

        for k,v in _Symbol.symbols.items():
            _Symbol.custom[k] = load(v)

        for k,v in _Symbol.flipped_symbols.items():
            _Symbol.custom[k] = pygame.transform.flip(load(v), True, False)

    @staticmethod
    def load(image_path: str) -> pygame.Surface:
        """Loads an image and replaces (0, 0, 0) with the desired color

        Args:
            image_path (str): relative path to the image

        Returns:
            pygame.Surface: updated image to match color
        """
        surface = pygame.image.load(image_path).convert_alpha()
        pixel_array = pygame.PixelArray(surface)
        pixel_array.replace((0, 0, 0, 255), _Symbol._color)
        pixel_array.close()
        del pixel_array
        return surface

    @staticmethod
    def _web_load(image_path: str) -> pygame.Surface:
        """Alternative method of loading an image, specifically because web doesn't like PixelArray

        Args:
            image_path (str): relative path to the image

        Returns:
            pygame.Surface
        """
        surface = pygame.image.load(image_path).convert_alpha()
        if any(name in image_path for name in ["dark_forest", "checkbox"]):
            return surface
        surface.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        surface.fill(_Style.text_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
        return surface

class RectButton:
    def __init__(self,
                 size: tuple[int, int],
                 text: str = "",
                 hover: bool = False,
                 unavailable: bool = False,
                 rounded_corners: Union[tuple[bool], list[bool]] = [True, True, True, True],
                 shadows: Union[tuple[bool], list[bool]] = [True, True, True, True],
                 hanging: bool = False) -> None:
        self.size = size
        if hanging:
            self.size[1] -= 6

        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface = self.surface.convert_alpha()
        self.hover = hover
        self.unavailable = unavailable
        self.rounded_corners = rounded_corners
        self.shadow = shadows
        self.hanging = hanging
        self.symbol = False

        if unavailable:
            self.palette = Palette.unavailable
        elif hover:
            self.palette = Palette.hover
        else:
            self.palette = Palette.palette

        self.text = self._render_text(text)
        self._build()

    def _render_text(self, text) -> pygame.Surface:
        if _Symbol.custom.get(text):
            self.symbol = True
            return _Symbol.custom[text]
        texts = []
        height = 0
        width = 0
        for line in text.split("\n"):
            height_temp = 0 # define temporary width and height, for searching through formatted
            width_temp = 0
            formatted = ['']
            regex = re.split(r"({|})", line)
            for e,char in enumerate(regex): # search for any {SYMBOLS}
                if char == '':
                    pass
                elif char == '{':
                    formatted.append('')
                    formatted[-1] += char
                elif regex[e-1] == '{':
                    formatted[-1] += char
                elif char == '}':
                    formatted[-1] += char
                    formatted.append('')
                else:
                    formatted[-1] += char
            formatted = list(filter(None, formatted))
            surfaces = []
            for item in formatted:
                if _Symbol.custom.get(item):
                    text = _Symbol.custom[item]
                    text_ = pygame.Surface((text.get_width(), text.get_height() + 4), pygame.SRCALPHA)
                    text_ = text_.convert_alpha()
                    text_.blit(text, (0, 0))
                    text = text_
                    del text_
                else:
                    text = _Style.font.render(item, False, _Style.text_color)

                surfaces.append(text)
                width_temp += text.get_width()
                if text.get_height() > height_temp:
                    height_temp = text.get_height()
            text_surface = pygame.Surface((width_temp, height_temp), pygame.SRCALPHA)
            text_surface = text_surface.convert_alpha()
            current_width = 0
            for surface in surfaces:
                text_surface.blit(surface, (current_width, 0))
                current_width += surface.get_width()

            texts.append(text_surface)
            height += height_temp
            if text_surface.get_width() > width:
                width = text_surface.get_width()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        current_height = 0
        for text in texts:
            surface.blit(text, (width / 2 - text.get_width() / 2, current_height))
            current_height += text.get_height()
        return surface

    def _build(self):
        # fill [5]
        pygame.draw.rect(self.surface, self.palette[2], (4, 4, self.size[0]-8, self.size[1]-8))
        # corners [1, 3, 7, 9]
        self.surface.blit(BuildCache.load_corner(self.palette, self.shadow[0], self.shadow[1], rounded=self.rounded_corners[0]), (0, 0))
        self.surface.blit(pygame.transform.flip(BuildCache.load_corner(self.palette, self.shadow[0], self.shadow[2], rounded=self.rounded_corners[1]), True, False), (self.size[0]-10, 0))
        self.surface.blit(pygame.transform.flip(BuildCache.load_corner(self.palette, self.shadow[3], self.shadow[1], rounded=self.rounded_corners[2]), False, True), (0, self.size[1] - 8))
        self.surface.blit(pygame.transform.flip(BuildCache.load_corner(self.palette, self.shadow[3], self.shadow[2], rounded=self.rounded_corners[3]), True, True), (self.size[0]-10, self.size[1] - 8))

        # edges [2, 4, 6, 8]
        self.surface.blit(BuildCache.load_edge(self.palette, self.size[0]-20, shadow=self.shadow[0]), (10, 0))
        self.surface.blit(BuildCache.load_edge(self.palette, self.size[1]-16, rotate=True, shadow=self.shadow[1]), (0, 8))
        self.surface.blit(BuildCache.load_edge(self.palette, self.size[1]-16, rotate=True, flip=True, shadow=self.shadow[2]), (self.size[0]-6, 8))
        self.surface.blit(BuildCache.load_edge(self.palette, self.size[0]-20, flip=True, shadow=self.shadow[3]), (10, self.size[1]-6))

        # text & hang
        if self.hanging:
            self._hang()
            text_rect = self.text.get_rect(center=(self.size[0] / 2 + 1, self.size[1] / 2 + 2 + 6))
        elif self.symbol:
            text_rect = self.text.get_rect(center=(self.size[0] / 2, self.size[1] / 2))
        else:
            text_rect = self.text.get_rect(center=(self.size[0] / 2 + 1, self.size[1] / 2 + 2))

        if text_rect.width > self.size[0]:
            # raise ValueError(f'Text width is too large to fit in the button! Minimum width is {text_rect.width}, recommended {text_rect.width + 12}')
            pass
        if text_rect.width > self.size[0] - 8 and DEBUG:
            warnings.warn(f'Text width is too small to fit in the button comfortably, minimum width is {text_rect.width + 12}')
        self.surface.blit(self.text, text_rect)

    def _hang(self):
        surface = pygame.Surface((self.size[0], self.size[1]+6), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        surface.blit(self.surface, (0, 6))

        connector = pygame.Surface((10, 6))
        pygame.draw.rect(connector, Palette.palette[2], (0, 0, 10, 6))
        pygame.draw.rect(connector, Palette.palette[4], (2, 0, 6, 6))
        pygame.draw.rect(connector, Palette.palette[3], (4, 0, 2, 6))

        surface.blit(connector, (12, 0))
        surface.blit(connector, (self.size[0]-22, 0))
        self.surface = surface

class SquareButton(RectButton):
    def _corner(self, shadow_corner1: bool, shadow_corner2: bool, rounded: bool = True):
        surface = pygame.Surface((10, 8), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        if rounded:
            # outline
            pygame.draw.rect(surface, self.palette[0], (4, 0, 6, 2))
            pygame.draw.rect(surface, self.palette[0], (2, 2, 2, 2))
            pygame.draw.rect(surface, self.palette[0], (0, 4, 2, 4))
            # fill
            pygame.draw.rect(surface, self.palette[2], (4, 4, 4, 4))
            # inline
            pygame.draw.rect(surface, self.palette[1], (4, 2, 6, 2))
            pygame.draw.rect(surface, self.palette[1], (2, 4, 4, 2))
            pygame.draw.rect(surface, self.palette[1], (2, 4, 2, 4))
            # shadow
            if shadow_corner1:
                pygame.draw.rect(surface, self.palette[3], (6, 4, 4, 2))
                pygame.draw.rect(surface, self.palette[3], (4, 6, 2, 2))
            elif shadow_corner2:
                pygame.draw.rect(surface, self.palette[3], (4, 6, 2, 2))
                pygame.draw.rect(surface, self.palette[3], (6, 4, 2, 2))
            return surface

        # outline
        pygame.draw.rect(surface, self.palette[0], (0, 0, 10, 2))
        pygame.draw.rect(surface, self.palette[0], (0, 0, 2, 8))
        # inline
        pygame.draw.rect(surface, self.palette[1], (2, 2, 8, 2))
        pygame.draw.rect(surface, self.palette[1], (2, 2, 2, 6))
        # fill
        pygame.draw.rect(surface, self.palette[2], (4, 4, 6, 2))
        if shadow_corner1:
            pygame.draw.rect(surface, self.palette[3], (4, 4, 6, 2))
        if shadow_corner2:
            pygame.draw.rect(surface, self.palette[3], (4, 4, 2, 4))
        return surface

class Button:
    # list of custom buttons to instead route through CustomButton.handle
    custom = [
        "#checked_checkbox", "#unchecked_checkbox"
    ]
    @staticmethod
    def new(size: tuple,
            text: str = "",
            hover: bool = False,
            unavailable: bool = False,
            rounded_corners: Union[bool, list] = [True, True, True, True],
            shadows: Union[bool, list] = [True, True, False, False],
            hanging: bool = False,
            object_id: str = "") -> pygame.Surface:
        if object_id in Button.custom:
            return CustomButton.handle(object_id, size, text, hover, unavailable, rounded_corners, shadows, hanging)
        if isinstance(rounded_corners, bool):
            rounded_corners = [rounded_corners]*4
        elif not isinstance(rounded_corners, list) and len(rounded_corners) != 4:
            raise ValueError("rounded_corners must be of type bool or list[bool; 4]")

        if isinstance(shadows,  bool):
            shadows = [shadows]*4
        elif not isinstance(shadows, list) and len(shadows) != 4:
            raise ValueError("shadows must be of type bool or list[bool; 4]")
        if size[0] == size[1]:
            button = SquareButton(size, text, hover, unavailable, rounded_corners, shadows, hanging)
        else:
            button = RectButton(size, text, hover, unavailable, rounded_corners, shadows, hanging)
        return button.surface

class CustomButton:
    @staticmethod
    def handle(object_id: str,
               size: tuple,
               text: str = "",
               hover: bool = False,
               unavailable: bool = False,
               rounded_corners: Union[bool, list] = [True, True, True, True],
               shadows: Union[bool, list] = [True, True, False, False],
               hanging: bool = False) -> pygame.Surface:
        if object_id == "#checked_checkbox":
            return CustomButton.checkbox(checked=True, hover=hover, unavailable=unavailable)
        if object_id == "#unchecked_checkbox":
            return CustomButton.checkbox(checked=False, hover=hover, unavailable=unavailable)
        raise ValueError("object_id not recognized")

    @staticmethod
    def checkbox(checked: bool = False,
                 hover: bool = False,
                 unavailable: bool = False) -> pygame.Surface:
        surface = pygame.Surface((34, 34), pygame.SRCALPHA).convert_alpha()
        inner_button = Button.new((22, 22), "", unavailable=unavailable, hover=hover, shadows=[True, False, True, False])
        surface.blit(inner_button, (6, 6))
        if checked:
            surface.blit(_Symbol.custom["{CHECKMARK}"], (10, 2))
        return surface

class pyggui_UIImage(pygame_gui.elements.UIImage):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 image_surface: pygame.surface.Surface,
                 manager: Optional[pygame_gui.core.interfaces.IUIManagerInterface] = None,
                 image_is_alpha_premultiplied: bool = False,
                 container: Optional[pygame_gui.core.interfaces.IContainerLikeInterface] = None,
                 parent_element: Optional[pygame_gui.core.UIElement] = None,
                 object_id: Optional[Union[pygame_gui.core.ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, pygame_gui.core.UIElement]]] = None,
                 visible: int = 1,
                 starting_height: int = 1):

        super(pygame_gui.elements.UIImage, self).__init__(relative_rect, manager, container,
                         starting_height=starting_height,
                         layer_thickness=1,

                         anchors=anchors,
                         visible=visible)

        super(pygame_gui.elements.UIImage, self)._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='image')

        self.original_image = None

        super().set_image(image_surface, image_is_alpha_premultiplied)
        
