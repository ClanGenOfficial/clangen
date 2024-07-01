import io

import pygame


def load_and_scale_svg(filename, scale):
    svg_string = open(filename, "rt").read()
    start = svg_string.find("<svg")
    if start > 0:
        svg_string = (
            svg_string[: start + 4]
            + f' transform="scale({scale})"'
            + svg_string[start + 4 :]
        )
    return pygame.image.load(io.BytesIO(svg_string.encode())).convert_alpha()
