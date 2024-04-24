import pygame

class Palette():
    """Internal class that allows for easy access to default color palettes"""
    transparent = (0, 0, 0, 0)
    palette = [
        (47, 41, 24, 255), (121, 96, 69, 255), (101, 89, 52, 255), (88, 79, 46, 255), (130, 102, 87, 255)
    ]
    hover = [
        (13, 11, 4, 255), (41, 27, 15, 255), (30, 24, 9, 255), (23, 18, 7, 255), (47, 31, 23, 255)
    ]
    unavailable = [
        (58, 56, 51, 255), (112, 107, 100, 255), (92, 88, 80, 255), (78, 75, 68, 255), (126, 119, 115, 255)
    ]
    g = ["outline", "inline", "fill", "shadow", "highlight"]
    @staticmethod
    def recolor(from_surface: pygame.Surface,
                to_palette: list[tuple],
                id: str) -> pygame.Surface:
        pixel_array = pygame.PixelArray(from_surface.copy())
        for e, _ in enumerate(to_palette):
            pixel_array.replace(Palette.palette[e], to_palette[e], distance=0.04)
        surf = pixel_array.make_surface()
        pixel_array.close()
        return surf