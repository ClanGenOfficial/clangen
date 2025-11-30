from typing import Optional, Tuple

import pygame
import pygame_gui

import scripts.game_structure.screen_settings
from scripts.game_structure import image_cache, constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UISurfaceImageButton, UIImageButton
from scripts.housekeeping.version import get_version_info
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import (
    ui_scale,
    ui_scale_offset,
    ui_scale_dimensions,
    ui_scale_blit,
    get_text_box_theme,
    ui_scale_value,
)

game_frame: Optional[pygame.Surface] = None
core_vignette = pygame.image.load("resources/images/vignette.png")
vignette: Optional[pygame.Surface] = None
dropshadow: Optional[pygame.Surface] = None
fade: Optional[pygame.Surface] = None

menu_buttons = dict()

default_game_bgs = None
default_fullscreen_bgs = None

version_number = None
dev_watermark = None


def rebuild_core(*, should_rebuild_bgs=True):
    global menu_buttons
    global default_game_bgs
    global default_fullscreen_bgs
    global version_number
    global dev_watermark

    # menu buttons are used very often, so they are generated here.
    menu_buttons = dict()

    # they have to be added individually as some of them rely on others in anchors
    menu_buttons["events_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((246, 60), (82, 30))),
        "screens.core.events",
        get_button_dict(ButtonStyles.MENU_LEFT, (82, 30)),
        visible=False,
        manager=MANAGER,
        object_id=pygame_gui.core.ObjectID("#events_button", "@buttonstyles_menu_left"),
        starting_height=5,
    )
    menu_buttons["camp_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((0, 60), (58, 30))),
        "screens.core.camp",
        get_button_dict(ButtonStyles.MENU_MIDDLE, (58, 30)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_menu_middle",
        starting_height=5,
        anchors={"left": "left", "left_target": menu_buttons["events_screen"]},
    )
    menu_buttons["catlist_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((0, 60), (88, 30))),
        "screens.core.cat_list",
        get_button_dict(ButtonStyles.MENU_MIDDLE, (88, 30)),
        visible=False,
        object_id="@buttonstyles_menu_middle",
        starting_height=5,
        anchors={"left": "left", "left_target": menu_buttons["camp_screen"]},
    )
    menu_buttons["patrol_screen"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((0, 60), (80, 30))),
        "screens.core.patrol",
        get_button_dict(ButtonStyles.MENU_RIGHT, (80, 30)),
        visible=False,
        manager=MANAGER,
        object_id="#patrol_button",
        starting_height=5,
        anchors={"left": "left", "left_target": menu_buttons["catlist_screen"]},
    )
    menu_buttons["main_menu"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((25, 25), (153, 30))),
        "buttons.main_menu",
        get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_squoval",
        starting_height=5,
    )

    # used so we can anchor to the right with numbers that make sense
    scale_rect = ui_scale(pygame.Rect((0, 0), (118, 30)))
    scale_rect.topright = ui_scale_offset((-25, 25))
    menu_buttons["allegiances"] = UISurfaceImageButton(
        scale_rect,
        "screens.core.allegiances",
        get_button_dict(ButtonStyles.SQUOVAL, (118, 30)),
        visible=False,
        manager=MANAGER,
        object_id=pygame_gui.core.ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"top": "top", "right": "right"},
    )

    # used so we can anchor to the right with numbers that make sense
    scale_rect = ui_scale(pygame.Rect((0, 0), (85, 30)))
    scale_rect.topright = ui_scale_offset((-25, 5))
    menu_buttons["clan_settings"] = UISurfaceImageButton(
        scale_rect,
        "screens.core.settings",
        get_button_dict(ButtonStyles.SQUOVAL, (85, 30)),
        visible=False,
        manager=MANAGER,
        object_id=pygame_gui.core.ObjectID(class_id="@image_button", object_id=None),
        starting_height=5,
        anchors={"top_target": menu_buttons["allegiances"], "right": "right"},
    )
    del scale_rect

    heading_rect = ui_scale(pygame.Rect((0, 0), (190, 35)))
    heading_rect.bottomleft = ui_scale_dimensions((0, 0))
    menu_buttons["name_background"] = pygame_gui.elements.UIImage(
        heading_rect,
        pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(),
            ui_scale_dimensions((190, 35)),
        ),
        visible=False,
        manager=MANAGER,
        starting_height=5,
        anchors={
            "bottom": "bottom",
            "bottom_target": menu_buttons["camp_screen"],
            "centerx": "centerx",
        },
    )
    # it has to be at least 193 to make "cats outside the clan" fit
    heading_rect = ui_scale(pygame.Rect((0, 0), (193, 35)))
    heading_rect.bottomleft = ui_scale_offset((0, 1))  # yes, this is intentional.
    menu_buttons["heading"] = pygame_gui.elements.UITextBox(
        "",
        heading_rect,
        visible=False,
        manager=MANAGER,
        object_id=pygame_gui.core.ObjectID(
            "#text_box_34_horizcenter_vertcenter", "#dark"
        ),
        starting_height=5,
        anchors={
            "bottom": "bottom",
            "bottom_target": menu_buttons["camp_screen"],
            "centerx": "centerx",
        },
    )
    del heading_rect

    menu_buttons["moons_n_seasons"] = pygame_gui.elements.UIScrollingContainer(
        ui_scale(pygame.Rect((25, 60), (153, 75))),
        visible=False,
        allow_scroll_x=False,
        manager=MANAGER,
        starting_height=5,
    )
    menu_buttons["moons_n_seasons_arrow"] = UIImageButton(
        ui_scale(pygame.Rect((174, 80), (22, 34))),
        "",
        visible=False,
        manager=MANAGER,
        object_id="#arrow_mns_button",
        starting_height=5,
    )

    rebuild_den_dropdown()

    rebuild_mute("default")

    version_number = pygame_gui.elements.UILabel(
        ui_scale(pygame.Rect((50, 50), (-1, -1))),
        get_version_info().version_number[0:8],
        object_id=get_text_box_theme(),
        anchors={"bottom": "bottom", "right": "right"},
    )
    # Adjust position
    version_number.set_relative_position(
        ui_scale_offset(
            (
                800 - version_number.get_relative_rect()[2],
                700 - version_number.get_relative_rect()[3],
            )
        )
    )

    if get_version_info().is_source_build or get_version_info().is_dev():
        dev_watermark = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((525, 660), (300, 50))),
            "screens.core.dev_watermark",
            object_id="#dev_watermark",
            text_kwargs={"ver": version_number.text},
        )
        version_number.kill()
        version_number = None

    if should_rebuild_bgs:
        rebuild_bgs()


def rebuild_den_dropdown(left_align: bool = True, game_mode: str = "expanded"):
    """
    Rebuild the den dropdown
    :param left_align: Set True if the buttons should be on the left-hand side of the screen, False if they should be on the right-hand side
    """

    if "dens_bar" in menu_buttons:
        menu_buttons["dens_bar"].kill()

    x_pos = 40
    if not left_align:
        x_pos = 755

    if game_mode != "classic":
        menu_buttons["dens_bar"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x_pos, 5), (10, 170))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/vertical_bar.png"
                ).convert_alpha(),
                ui_scale_dimensions((10, 160)),
            ),
            visible=False,
            starting_height=5,
            manager=MANAGER,
            anchors={
                "top_target": menu_buttons["main_menu"]
                if left_align
                else menu_buttons["clan_settings"]
            },
        )
    else:
        menu_buttons["dens_bar"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x_pos, 5), (10, 140))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/vertical_bar.png"
                ).convert_alpha(),
                ui_scale_dimensions((10, 160)),
            ),
            visible=False,
            starting_height=5,
            manager=MANAGER,
            anchors={
                "top_target": menu_buttons["main_menu"]
                if left_align
                else menu_buttons["clan_settings"]
            },
        )

    x_pos = 25
    if not left_align:
        x_pos = 704

    if "dens" in menu_buttons:
        menu_buttons["dens"].kill()
    menu_buttons["dens"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((x_pos, 5), (71, 30))),
        "screens.core.dens",
        get_button_dict(ButtonStyles.SQUOVAL, (71, 30)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_squoval",
        starting_height=6,
        anchors={
            "top_target": menu_buttons["main_menu"]
            if left_align
            else menu_buttons["clan_settings"]
        },
    )

    if not left_align:
        x_pos = 663
    if "lead_den" in menu_buttons:
        menu_buttons["lead_den"].kill()
    menu_buttons["lead_den"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((x_pos, 10), (112, 28))),
        "screens.core.leader_den",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (112, 28)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_rounded_rect",
        starting_height=6,
        anchors={
            "top_target": menu_buttons["dens"],
        },
    )

    if not left_align:
        x_pos = 625
    if "med_cat_den" in menu_buttons:
        menu_buttons["med_cat_den"].kill()
    menu_buttons["med_cat_den"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((x_pos, 10), (151, 28))),
        "screens.core.medicine_cat_den",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (151, 28)),
        object_id="@buttonstyles_rounded_rect",
        visible=False,
        manager=MANAGER,
        starting_height=6,
        anchors={"top_target": menu_buttons["lead_den"]},
    )

    if not left_align:
        x_pos = 654
    if "warrior_den" in menu_buttons:
        menu_buttons["warrior_den"].kill()
    menu_buttons["warrior_den"] = UISurfaceImageButton(
        ui_scale(pygame.Rect((x_pos, 10), (121, 28))),
        "screens.core.warriors_den",
        get_button_dict(ButtonStyles.ROUNDED_RECT, (121, 28)),
        object_id="@buttonstyles_rounded_rect",
        visible=False,
        manager=MANAGER,
        starting_height=6,
        anchors={"top_target": menu_buttons["med_cat_den"]},
    )

    if "clearing" in menu_buttons:
        menu_buttons["clearing"].kill()

    if game_mode != "classic":
        if not left_align:
            x_pos = 694
        menu_buttons["clearing"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((x_pos, 10), (81, 28))),
            "screens.core.clearing",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (81, 28)),
            visible=False,
            manager=MANAGER,
            object_id="@buttonstyles_rounded_rect",
            starting_height=6,
            anchors={"top_target": menu_buttons["warrior_den"]},
        )


def rebuild_mute(location: str):
    if "mute_button" in menu_buttons:
        menu_buttons["mute_button"].kill()
        menu_buttons["unmute_button"].kill()

    mute_pos = ui_scale(pygame.Rect((0, 0), (34, 34)))

    if location in ("bottomright", "default"):
        mute_pos.bottomright = ui_scale_offset((-25, -25))
        anchors = {"bottom": "bottom", "right": "right"}
    elif location == "topright":
        mute_pos.topright = ui_scale_offset((-25, 25))
        anchors = {"top": "top", "right": "right"}
    elif location == "bottomleft":
        mute_pos.bottomleft = ui_scale_offset((25, -25))
        anchors = {"bottom": "bottom", "left": "left"}
    elif location == "topleft":
        mute_pos.topleft = ui_scale_offset((25, 25))
        anchors = {"top": "top", "left": "left"}
    else:
        return

    menu_buttons["mute_button"] = UISurfaceImageButton(
        mute_pos,
        Icon.SPEAKER,
        get_button_dict(ButtonStyles.ICON, (34, 34)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_icon",
        starting_height=6,
        anchors=anchors,
    )

    menu_buttons["unmute_button"] = UISurfaceImageButton(
        mute_pos,
        Icon.MUTE,
        get_button_dict(ButtonStyles.ICON, (34, 34)),
        visible=False,
        manager=MANAGER,
        object_id="@buttonstyles_icon",
        starting_height=6,
        anchors=anchors,
    )


def rebuild_bgs():
    global default_fullscreen_bgs
    global default_game_bgs
    global game_frame
    global vignette
    global dropshadow
    global fade

    if (
        vignette is None
        or scripts.game_structure.screen_settings.screen.get_size()
        != vignette.get_size()
    ):
        game_frame = get_box(
            BoxStyles.FRAME,
            (820, 720),
        )

        vignette = pygame.transform.scale(
            core_vignette, scripts.game_structure.screen_settings.screen.get_size()
        ).convert_alpha()

        dropshadow = pygame.Surface(
            scripts.game_structure.screen_settings.screen.get_size(),
            flags=pygame.SRCALPHA,
        )

        fade = pygame.Surface(scripts.game_structure.screen_settings.screen.get_size())
        fade.fill(pygame.Color(113, 113, 111))  # middle grey

        game_box = pygame.Surface(
            (
                scripts.game_structure.screen_settings.screen_x + ui_scale_value(30),
                scripts.game_structure.screen_settings.screen_y + ui_scale_value(30),
            ),
            pygame.SRCALPHA,
        )
        feather_surface(game_box, 15)
        dropshadow.blit(game_box, ui_scale_blit((-15, -15)))
        del game_box

    bg = pygame.Surface(scripts.game_structure.screen_settings.game_screen_size)
    bg.fill(constants.CONFIG["theme"]["light_mode_background"])
    bg_dark = pygame.Surface(scripts.game_structure.screen_settings.game_screen_size)
    bg_dark.fill(constants.CONFIG["theme"]["dark_mode_background"])

    default_game_bgs = {
        "light": {"default": bg},
        "dark": {"default": bg_dark},
    }

    temp_screen_size = scripts.game_structure.screen_settings.screen.get_size()

    default_fullscreen_bgs = {
        "light": {
            "default": pygame.transform.scale(bg, temp_screen_size),
            "mainmenu_bg": pygame.transform.scale(
                pygame.image.load("resources/images/menu_logoless.png").convert(),
                temp_screen_size,
            ),
            "starclan": pygame.transform.scale(
                pygame.image.load("resources/images/starclanbg.png").convert_alpha(),
                temp_screen_size,
            ),
            "darkforest": pygame.transform.scale(
                pygame.image.load("resources/images/darkforestbg.png").convert_alpha(),
                temp_screen_size,
            ),
            "unknown_residence": pygame.transform.scale(
                pygame.image.load("resources/images/urbg.png").convert(),
                temp_screen_size,
            ),
        },
        "dark": {
            "default": pygame.transform.scale(bg_dark, temp_screen_size),
            "mainmenu_bg": pygame.transform.scale(
                pygame.image.load("resources/images/menu_logoless.png").convert(),
                temp_screen_size,
            ),
            "starclan": pygame.transform.scale(
                pygame.image.load("resources/images/starclanbg.png").convert_alpha(),
                temp_screen_size,
            ),
            "darkforest": pygame.transform.scale(
                pygame.image.load("resources/images/darkforestbg.png").convert_alpha(),
                temp_screen_size,
            ),
            "unknown_residence": pygame.transform.scale(
                pygame.image.load("resources/images/urbg.png").convert(),
                temp_screen_size,
            ),
        },
    }

    for theme in ("light", "dark"):
        for name, bg in default_fullscreen_bgs[theme].items():
            if name not in (
                "default",
                "mainmenu_bg",
                "darkforest",
                "unknown_residence",
                "starclan",
            ):
                default_fullscreen_bgs[theme][name] = process_blur_bg(
                    default_fullscreen_bgs[theme][name], theme=theme
                )
            elif name == "default":
                default_fullscreen_bgs[theme][name] = process_blur_bg(
                    default_fullscreen_bgs[theme][name],
                    theme=theme,
                    vignette_strength=0,
                    fade_color=None,
                )
            elif name in ("mainmenu_bg", "darkforest", "unknown_residence"):
                default_fullscreen_bgs[theme][name] = process_blur_bg(
                    default_fullscreen_bgs[theme][name], theme=theme, blur_radius=10
                )
            elif name == "starclan":
                default_fullscreen_bgs[theme][name] = process_blur_bg(
                    default_fullscreen_bgs[theme][name], theme=theme, blur_radius=2
                )

    camp_bgs = get_camp_bgs()

    for theme in ("light", "dark"):
        for name, camp_bg in camp_bgs[theme].items():
            default_fullscreen_bgs[theme][name] = process_blur_bg(camp_bg, theme=theme)


def get_camp_bgs():
    camp_bg_base_dir = "resources/images/camp_bg/"
    leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
    available_biome = ["forest", "mountainous", "plains", "beach"]

    try:
        camp_nr = game.clan.camp_bg
        biome = game.clan.biome.lower()
    except AttributeError:
        camp_nr = "camp1"
        biome = available_biome[0]

    all_backgrounds = []
    for light_dark in ("light", "dark"):
        for leaf in leaves:
            platform_dir = (
                f"{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png"
            )
            all_backgrounds.append(platform_dir)

    return {
        "light": {
            "Newleaf": pygame.transform.scale(
                pygame.image.load(all_backgrounds[0]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
            "Greenleaf": pygame.transform.scale(
                pygame.image.load(all_backgrounds[1]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
            "Leaf-bare": pygame.transform.scale(
                pygame.image.load(all_backgrounds[2]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
            "Leaf-fall": pygame.transform.scale(
                pygame.image.load(all_backgrounds[3]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
        },
        "dark": {
            "Newleaf": pygame.transform.scale(
                pygame.image.load(all_backgrounds[4]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
            "Greenleaf": pygame.transform.scale(
                pygame.image.load(all_backgrounds[5]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
            "Leaf-bare": pygame.transform.scale(
                pygame.image.load(all_backgrounds[6]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
            "Leaf-fall": pygame.transform.scale(
                pygame.image.load(all_backgrounds[7]).convert(),
                scripts.game_structure.screen_settings.screen.get_size(),
            ),
        },
    }


def process_blur_bg(
    bg,
    theme: str = None,
    blur_radius: Optional[int] = 5,
    vignette_strength: Optional[int] = None,
    fade_color: Optional[Tuple[int, int, int]] = None,
) -> pygame.Surface:
    global vignette
    global fade
    global dropshadow
    if theme is None:
        theme = "dark" if game_setting_get("dark mode") else "light"

    fade.fill(constants.CONFIG["theme"]["fullscreen_background"][theme]["fade_color"])
    vignette.set_alpha(
        constants.CONFIG["theme"]["fullscreen_background"][theme]["vignette_alpha"]
    )
    dropshadow.set_alpha(
        constants.CONFIG["theme"]["fullscreen_background"][theme]["dropshadow_alpha"]
    )

    if vignette_strength is not None:
        vignette.set_alpha(vignette_strength)

    bg = pygame.transform.scale(
        bg, scripts.game_structure.screen_settings.screen.get_size()
    ).convert_alpha()

    if blur_radius is not None:
        bg = pygame.transform.box_blur(bg, blur_radius)

    bg.blits(
        (
            (fade, (0, 0), None, pygame.BLEND_MULT),
            (vignette, (0, 0), None),
            (dropshadow, (0, 0), None),
            (game_frame, ui_scale_blit((-10, -10))),
        )
    )

    return bg


def feather_surface(surface, feather_width):
    """
    Run a per-pixel effect to make a fun fade-to-transparent border
    :param surface: The surface to add a feathered edge to
    :param feather_width: How fat to make the edge
    :return: None
    """
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            distance = min(x, y, width - x - 1, height - y - 1)
            if distance < feather_width:
                alpha = int(255 * (distance / feather_width))
                surface.set_at((x, y), (0, 0, 0, alpha))


rebuild_core()
