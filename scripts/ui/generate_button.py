import pygame

buttonstyles = {
    "general": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/general_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/general_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/general_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/general_disabled.png"
        ).convert_alpha(),
    },
}


def generate_button(base: pygame.Surface, width: int, scale=1):

    height = base.height
    left = base.subsurface((0, 0), (height, height))
    middle = base.subsurface((height, 0), (height, height))
    right = base.subsurface((height * 2, 0), (height, height))
    width_bookends = height * 2

    if width - width_bookends > 0:
        middle = pygame.transform.scale(middle, (width - width_bookends, middle.height))
    else:
        middle = pygame.transform.scale(middle, (1, middle.height))
    surface = pygame.Surface(
        (left.width * 2 + middle.width, left.height), pygame.SRCALPHA
    )
    surface.convert_alpha()
    surface.fblits(
        (
            (left, (0, 0)),
            (middle, (left.width, 0)),
            (right, (left.width + middle.width, 0)),
        )
    )

    if scale != 1:
        surface = pygame.transform.scale(
            surface, (surface.width * scale, surface.height * scale)
        )
    return surface


def get_button_dict(style: str, width: int, scale=1):
    return {
        "normal": generate_button(buttonstyles[style]["normal"], width, scale),
        "hovered": generate_button(buttonstyles[style]["hovered"], width, scale),
        "selected": generate_button(buttonstyles[style]["selected"], width, scale),
        "disabled": generate_button(buttonstyles[style]["disabled"], width, scale),
    }
