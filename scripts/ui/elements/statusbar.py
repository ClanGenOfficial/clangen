import pygame
import pygame_gui
from scripts.ui import image_cache

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