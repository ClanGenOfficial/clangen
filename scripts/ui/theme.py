from pygame_gui.core import ObjectID

from scripts.game_structure.game import game_setting_get


def get_text_box_theme(theme_name=None):
    """Updates the name of the theme based on dark or light mode"""
    if game_setting_get("dark mode"):
        return ObjectID("#dark", theme_name)
    else:
        return theme_name
