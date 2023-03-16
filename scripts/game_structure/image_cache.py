import pygame
from scripts.mods.resources import pyg_img_load, mod_open, mod_open

_images = {}
def load_image(path):
    """
    If not in the cache already, loads the image from path as a surface.
    Otherwise, the image is retrieved from the cache.
    """
    if path not in _images:
        _images[path] = pyg_img_load(path)
    return _images[path]
