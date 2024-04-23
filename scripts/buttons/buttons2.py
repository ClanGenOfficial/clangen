"""Python module for generating a button surface, based off of image_button.UISpriteButton"""
# pylint: disable=too-many-arguments, line-too-long, pointless-string-statement, missing-function-docstring
"""Editing Guide:
Text / Symbol color: 
    COLOR
    default: (239, 229, 206)
Add a symbol:
    _Symbol.__init__: _Symbol.custom["{<SYMBOL_NAME>}"] = _Symbol.load(<path_to_symbol_image>)
    Symbol color should be (0, 0, 0) so it will update with COLOR
Edit text:
    languages/english/buttons.json
Edit style (if button is rounded, hanging, etc):
    * You should only add a value to this if it doesn't follow the standard shape!
    * Rounded on all 4 corners, not hanging
    resources/styles.json
    value for 'rounded':
        list[4]: [corner1, corner3, corner7, corner9]
        list[4]: [corner_top_left, corner_top_right, corner_bottom_left, corner_bottom_right]
        bool:    all_corners
    value for 'hanging':
        bool:    if hanging
Add language:
    _Language:
        i.    Create file, languages/<language name>/buttons.json, copying from languages/english/buttons.json
        ii.   Add new variable, recommended naming scheme 'dict_<language abbr.>' 
              or 'dict_<language abbr.>-<country abbr.>'
        iii.  Add new 'elif' statement to _Language.check, following the other pattern.
                `search = _Language.<dictionary>.get(object_id)`
        iv.   Change _Language.LANGUAGE to your desired language
        v.    (optional) (not implemented) Add a button for your language on the options screen

    Be prepared to abbreviate certain words, or remove others all together! There is currently no feature yet to
    increase button size.
    Supported characters:
        [A-Za-z0-9] ! @ # $ % ^ & * ( ) - _ = + , . < > / ? { } | \\ [ ] ~ ` ; :
        ¡ ¿ ± µ ÷
        Ç ç ñ
        á â ã ä æ 
        é ê ë 
        í 
        ó ô õ ö
        ú û ü
        / capital variants of accented characters (excluding æ)
    In progress:
        missing vowel accents (for french)
        ß (optional, can be replaced with 'ss')
    Possible:
        Japanese kana?
        non-standard symbols
        missing consonant accents
    Unlikely / impossible with current font:
        Chinese characters, Japanese kanji
        Other writing systems
Change default color palette(s):
    Palette:
        Palette.palette:      Standard color palette
        Palette.hover:        Palette for when the button is hovered
        Palette.unavailable:  Used when button is already selected / disabled
    Format:
        Following names from https://clangen.foxes.lol/button_colors
        Fallback link: https://media.discordapp.net/attachments/1004154598975610982/1092270184137494599/image.png
        list[5] (list[6] in the future)

        palette[0]:  Transparent. (0, 0, 0, 0) I don't know why this is in here, honestly
        palette[1]:  Button outline color
        palette[2]:  Button "inline" color; not the fill but also not the shadow
        palette[3]:  Button fill
        palette[4]:  Button shadow      
"""
import pygame
import pygame_gui
import warnings
import re
import i18n
from typing import Union, Tuple, Dict, Optional
import scripts.game_structure.image_button
from scripts.game_structure.game_essentials import MANAGER
# from scripts.platformwrapper import is_web

try:
    import ujson
except:
    import json as ujson

pygame.font.init()
DEBUG = False
FONT = pygame.font.Font('resources/fonts/clangen.ttf', 16)
COLOR = (239, 229, 206)

# if is_web:
#     FONT = pygame.font.SysFont(None, 24)

class _Language():
    """Class for rendering button text in other languages, from languages/.*/buttons.json"""
    LANGUAGE = "en-us"
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
            language (str): The language to use, must be in languages/
        """
        supported_languages = ["en-us", "pt-br"]
        if language not in supported_languages:
            raise ValueError("Language not supported")
        _Language.LANGUAGE = language
        i18n.set('locale', language)

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
            warnings.warn('text (en-us) for not found! ' + object_id)
        else:
            warnings.warn(f'Translation for "{object_id}" in {_Language.LANGUAGE} not found! Using fallback language "en-us"')
            return i18n.t(search_term, locale='en-us')
        return ''

class _Symbol():
    """Custom class for rendering symbols from an image file"""
    _color = pygame.Color(COLOR)
    custom = {}
    @staticmethod
    def __init__() -> None:
        """Populates _Symbol.custom with the appropriate custom symbols"""
        _Symbol.custom["{DICE}"] = _Symbol.load("resources/images/symbols/random_dice.png")
        _Symbol.custom["{ARROW_LEFT_SHORT}"] = _Symbol.load("resources/images/symbols/arrow_short.png")
        _Symbol.custom["{ARROW_RIGHT_SHORT}"] = pygame.transform.flip(_Symbol.load("resources/images/symbols/arrow_short.png"), True, False)
        _Symbol.custom["{ARROW_LEFT_MED}"] = _Symbol.load("resources/images/symbols/arrow_medium.png")
        _Symbol.custom["{ARROW_RIGHT_MED}"] = pygame.transform.flip(_Symbol.load("resources/images/symbols/arrow_medium.png"), True, False)
        _Symbol.custom["{PATROL_CLAW}"] = _Symbol.load("resources/images/symbols/patrol_claws.png")
        _Symbol.custom["{PATROL_PAW}"] = _Symbol.load("resources/images/symbols/patrol_paw.png")
        _Symbol.custom["{PATROL_MOUSE}"] = _Symbol.load("resources/images/symbols/patrol_mouse.png")
        _Symbol.custom["{PATROL_HERB}"] = _Symbol.load("resources/images/symbols/patrol_herb.png")
        _Symbol.custom["{YOUR_CLAN}"] = _Symbol.load("resources/images/symbols/your_clan.png")
        _Symbol.custom["{OUTSIDE_CLAN}"] = _Symbol.load("resources/images/symbols/outside_clan.png")
        _Symbol.custom["{STARCLAN}"] = _Symbol.load("resources/images/symbols/starclan.png")
        _Symbol.custom["{UNKNOWN_RESIDENCE}"] = _Symbol.load("resources/images/symbols/unknown_residence.png")
        _Symbol.custom["{DARK_FOREST}"] = _Symbol.load("resources/images/symbols/dark_forest.png")
        _Symbol.custom["{LEADER_CEREMONY}"] = _Symbol.load("resources/images/symbols/leader_ceremony.png")
        _Symbol.custom["{MEDIATION}"] = _Symbol.load("resources/images/symbols/mediation.png")
        _Symbol.custom["{EXIT}"] = _Symbol.load("resources/images/symbols/exit.png")
        _Symbol.custom["{CHECKMARK}"] = _Symbol.load("resources/images/symbols/checkbox_checkmark.png")

    @staticmethod
    def populate() -> None:
        """Temporary class for populating _Symbol.custom on the web build, testing a different recolor method"""
        _Symbol.custom["{DICE}"] = _Symbol._web_load("resources/images/symbols/random_dice.png")
        _Symbol.custom["{ARROW_LEFT_SHORT}"] = _Symbol._web_load("resources/images/symbols/arrow_short.png")
        _Symbol.custom["{ARROW_RIGHT_SHORT}"] = pygame.transform.flip(_Symbol._web_load("resources/images/symbols/arrow_short.png"), True, False)
        _Symbol.custom["{ARROW_LEFT_MED}"] = _Symbol._web_load("resources/images/symbols/arrow_medium.png")
        _Symbol.custom["{ARROW_RIGHT_MED}"] = pygame.transform.flip(_Symbol._web_load("resources/images/symbols/arrow_medium.png"), True, False)
        _Symbol.custom["{PATROL_CLAW}"] = _Symbol._web_load("resources/images/symbols/patrol_claws.png")
        _Symbol.custom["{PATROL_PAW}"] = _Symbol._web_load("resources/images/symbols/patrol_paw.png")
        _Symbol.custom["{PATROL_MOUSE}"] = _Symbol._web_load("resources/images/symbols/patrol_mouse.png")
        _Symbol.custom["{PATROL_HERB}"] = _Symbol._web_load("resources/images/symbols/patrol_herb.png")
        _Symbol.custom["{YOUR_CLAN}"] = _Symbol._web_load("resources/images/symbols/your_clan.png")
        _Symbol.custom["{OUTSIDE_CLAN}"] = _Symbol._web_load("resources/images/symbols/outside_clan.png")
        _Symbol.custom["{STARCLAN}"] = _Symbol._web_load("resources/images/symbols/starclan.png")
        _Symbol.custom["{UNKNOWN_RESIDENCE}"] = _Symbol._web_load("resources/images/symbols/unknown_residence.png")
        _Symbol.custom["{DARK_FOREST}"] = _Symbol._web_load("resources/images/symbols/dark_forest.png")
        _Symbol.custom["{LEADER_CEREMONY}"] = _Symbol._web_load("resources/images/symbols/leader_ceremony.png")
        _Symbol.custom["{MEDIATION}"] = _Symbol._web_load("resources/images/symbols/mediation.png")
        _Symbol.custom["{EXIT}"] = _Symbol._web_load("resources/images/symbols/exit.png")
        _Symbol.custom["{CHECKMARK}"] = _Symbol._web_load("resources/images/symbols/checkbox_checkmark.png")

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
        image = surface.copy()
        image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        image.fill(COLOR[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
        return image

class _Style():
    """Class for parsing resources/styles.json, and determining custom styles from the #object_id"""
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

class Palette():
    """Internal class that allows for easy access to default color palettes"""
    palette = [
        (0, 0, 0, 0), (47, 41, 24, 255), (121, 96, 69, 255), (101, 89, 52, 255), (87, 76, 45, 255)
    ]
    hover = [
        (0, 0, 0, 0), (14, 11, 4, 255), (41, 27, 15, 255), (30, 24, 9, 255), (23, 18, 7, 255)
    ]
    unavailable = [
        (0, 0, 0, 0), (58, 56, 51, 255), (112, 107, 100, 255), (92, 88, 80, 255), (80, 78, 70, 255)
    ]

class ButtonCache():
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
        # if is_web:
        #     return surface
        store = {
            "surface": surface,
            "hover": hover,
            "unavailable": unavailable,
            "object_id": object_id
        }
        ButtonCache._storage.append(store)
        del store
        return surface

class UIButton(scripts.game_structure.image_button.UISpriteButton):
    """TODO: document"""
    def __init__(self, relative_rect, text = "", visible=1, starting_height=1, object_id=None,
                 manager=MANAGER, container=None, tool_tip_text=None):
        """TODO: document"""
        self.relative_rect = relative_rect
        self.id = object_id
        self.rounded_corners = _Style.check_round(object_id)
        self.hanging = _Style.check_hanging(object_id)
        self.shadows = _Style.check_shadow(object_id)

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
        self.button = CatButton(relative_rect, visible=visible,
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

class CatButton(pygame_gui.elements.UIButton):
    """TODO: document"""

    def __init__(self,
                 relative_rect,
                 visible=True,
                 starting_height=1,
                 manager=MANAGER,
                 tool_tip_text=None,
                 container=None,
                 internal=None) -> None:
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
        for key in ["normal_bg", "hovered_bg", "disabled_bg", "selected_bg", "active_bg", 
                    "normal_text", "hovered_text", "selected_text", "disabled_text", 
                    "link_text", "link_hover", "link_selected", "text_shadow", 
                    "normal_border", "hovered_border", "disabled_border", "active_border", "selected_border", 
                    "normal_text_shadow"]:
            self.colours[key] = pygame.Color(0, 0, 0, 0) # yes i know this solution is hacky give me a BREAK
        super().rebuild()

# if is_web:
#     _Symbol.populate()
# else:
_Symbol.__init__()

class RectButton():
    """TODO: document"""
    def __init__(self,
                 size: tuple,
                 text: str = "",
                 hover: bool = False,
                 unavailable: bool = False,
                 rounded_corners: list = [True, True, True, True],
                 shadows: list = [True, True, False, False],
                 hanging: bool = False):
        """TODO: document"""
        if hanging:
            self.size = (size[0], size[1] - 6)
        else:
            self.size = (size[0], size[1])
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface = self.surface.convert_alpha()
        self.hover = hover
        self.unavailable = unavailable
        self.hanging = hanging
        self.symbol = False
        if unavailable:
            self.palette = Palette.unavailable
        elif hover:
            self.palette = Palette.hover
        else:
            self.palette = Palette.palette
        self.rounded_corners = rounded_corners
        self.shadow = shadows
        self.text = self._build_text(text)
        self._build()

    def _corner(self, shadow_corner1: bool, shadow_corner2: bool, rounded: bool = True):
        """TODO: document"""
        surface = pygame.Surface((10, 8), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        if rounded:
            # outline
            pygame.draw.rect(surface, self.palette[1], (6, 2, 4, 2))
            pygame.draw.rect(surface, self.palette[1], (4, 4, 2, 2))
            pygame.draw.rect(surface, self.palette[1], (2, 6, 2, 2))
            # inline
            pygame.draw.rect(surface, self.palette[2], (6, 4, 4, 2))
            pygame.draw.rect(surface, self.palette[2], (4, 6, 2, 2))
            # fill
            if shadow_corner1 and shadow_corner2:
                pygame.draw.rect(surface, self.palette[4], (6, 6, 4, 2))
            else:
                pygame.draw.rect(surface, self.palette[3], (6, 6, 4, 2))
            return surface

        # outline
        pygame.draw.rect(surface, self.palette[1], (0, 0, 10, 2))
        pygame.draw.rect(surface, self.palette[1], (0, 0, 2, 8))
        # inline
        pygame.draw.rect(surface, self.palette[2], (2, 2, 8, 2))
        pygame.draw.rect(surface, self.palette[2], (2, 2, 2, 6))
        # fill
        pygame.draw.rect(surface, self.palette[3], (4, 4, 6, 2))
        if shadow_corner1:
            pygame.draw.rect(surface, self.palette[4], (4, 4, 6, 2))
        if shadow_corner2:
            pygame.draw.rect(surface, self.palette[4], (4, 4, 2, 4))
        return surface

    def _edge(self, length: int, rotate: bool = False, flip: bool = False, shadow = False):
        """TODO: document"""
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
        pygame.draw.rect(surface, self.palette[1], (0, 0, length, 2))
        # inline
        pygame.draw.rect(surface, self.palette[2], (0, 2, length if not odd else length-1, 2))
        # fill
        if shadow:
            pygame.draw.rect(surface, self.palette[4], (0, 4, length if not odd else length-1, 2))
        else:
            pygame.draw.rect(surface, self.palette[3], (0, 4, length if not odd else length-1, 2))

        if rotate and flip:
            surface = pygame.transform.rotate(surface, 90)
            surface = pygame.transform.flip(surface, True, False)
        elif rotate:
            surface = pygame.transform.rotate(surface, 90)
        elif flip:
            surface = pygame.transform.flip(surface, False, True)

        return surface

    def _build_text(self, text):
        """TODO: document"""
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
            for e,char in enumerate(regex):
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
                    text = FONT.render(item, False, COLOR)

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
        """TODO: document"""
        # fill [5]
        pygame.draw.rect(self.surface, self.palette[3], (4, 4, self.size[0]-8, self.size[1]-8))
        # corners [1, 3, 7, 9]
        self.surface.blit(self._corner(self.shadow[0], self.shadow[1], rounded=self.rounded_corners[0]), (0, 0))
        self.surface.blit(pygame.transform.flip(self._corner(self.shadow[0], self.shadow[2], rounded=self.rounded_corners[1]), True, False), (self.size[0]-10, 0))
        self.surface.blit(pygame.transform.flip(self._corner(self.shadow[3], self.shadow[1], rounded=self.rounded_corners[2]), False, True), (0, self.size[1] - 8))
        self.surface.blit(pygame.transform.flip(self._corner(self.shadow[3], self.shadow[2], rounded=self.rounded_corners[3]), True, True), (self.size[0]-10, self.size[1] - 8))

        # edges [2, 4, 6, 8]
        self.surface.blit(self._edge(self.size[0]-20, shadow=self.shadow[0]), (10, 0))
        self.surface.blit(self._edge(self.size[1]-16, rotate=True, shadow=self.shadow[1]), (0, 8))
        self.surface.blit(self._edge(self.size[1]-16, rotate=True, flip=True, shadow=self.shadow[2]), (self.size[0]-6, 8))
        self.surface.blit(self._edge(self.size[0]-20, flip=True, shadow=self.shadow[3]), (10, self.size[1]-6))

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
        # yell at you if the text will be offset by 1px
        # if text_rect.width % 2 != 0 and self.size[0] % 2 == 0 and DEBUG:
        #     warnings.warn('Text has an odd width! Consider using an odd width instead of an even one.', Warning, stacklevel=5)
        # elif text_rect.width % 2 == 0 and self.size[0] % 2 != 0 and DEBUG:
        #     warnings.warn('Text has an even width! Consider using an even width instead of an odd one.', Warning, stacklevel=5)
        self.surface.blit(self.text, text_rect)

    def _hang(self):
        """TODO: document"""
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
    """TODO: document"""
    def _corner(self, shadow_corner1: bool, shadow_corner2: bool, rounded: bool = True):
        """TODO: document"""
        surface = pygame.Surface((10, 8), pygame.SRCALPHA)
        surface = surface.convert_alpha()
        if rounded:
            # outline
            pygame.draw.rect(surface, self.palette[1], (4, 0, 6, 2))
            pygame.draw.rect(surface, self.palette[1], (2, 2, 2, 2))
            pygame.draw.rect(surface, self.palette[1], (0, 4, 2, 4))
            # fill
            pygame.draw.rect(surface, self.palette[3], (4, 4, 4, 4))
            # inline
            pygame.draw.rect(surface, self.palette[2], (4, 2, 6, 2))
            pygame.draw.rect(surface, self.palette[2], (2, 4, 4, 2))
            pygame.draw.rect(surface, self.palette[2], (2, 4, 2, 4))
            # shadow
            if shadow_corner1:
                pygame.draw.rect(surface, self.palette[4], (6, 4, 4, 2))
                pygame.draw.rect(surface, self.palette[4], (4, 6, 2, 2))
            elif shadow_corner2:
                pygame.draw.rect(surface, self.palette[4], (4, 6, 2, 2))
                pygame.draw.rect(surface, self.palette[4], (6, 4, 2, 2))
            return surface

        # outline
        pygame.draw.rect(surface, self.palette[1], (0, 0, 10, 2))
        pygame.draw.rect(surface, self.palette[1], (0, 0, 2, 8))
        # inline
        pygame.draw.rect(surface, self.palette[2], (2, 2, 8, 2))
        pygame.draw.rect(surface, self.palette[2], (2, 2, 2, 6))
        # fill
        pygame.draw.rect(surface, self.palette[3], (4, 4, 6, 2))
        if shadow_corner1:
            pygame.draw.rect(surface, self.palette[4], (4, 4, 6, 2))
        if shadow_corner2:
            pygame.draw.rect(surface, self.palette[4], (4, 4, 2, 4))
        return surface

class Button():
    custom = [
        "#checked_checkbox", "#unchecked_checkbox"
    ]
    """TODO: document"""
    @staticmethod
    def new(size: tuple,
            text: str = "",
            hover: bool = False,
            unavailable: bool = False,
            rounded_corners: Union[bool, list] = [True, True, True, True],
            shadows: Union[bool, list] = [True, True, False, False],
            hanging: bool = False,
            object_id: str = "") -> pygame.Surface:
        """TODO: document"""
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

class CustomButton():
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
    @staticmethod
    def checkbox(checked: bool = False, 
                 hover: bool = False,
                 unavailable: bool = False) -> pygame.Surface:
        surface = pygame.Surface((34, 34), pygame.SRCALPHA)
        surface = surface.convert_alpha()
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