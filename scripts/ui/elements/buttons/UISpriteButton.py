import pygame
import pygame_gui

from scripts.ui.elements.buttons.catbutton import CatButton

class UISpriteButton():
    """This is for use with the cat sprites. It wraps together a UIImage and Transparent Button.
        For most functions, this can be used exactly like other pygame_gui elements. """

    def __init__(self, relative_rect, sprite, cat_id=None, visible=1, cat_object=None, starting_height=1,
                 manager=None, container=None, tool_tip_text=None):

        # We have to scale the image before putting it into the image object. Otherwise, the method of upscaling that UIImage uses will make the pixel art fuzzy
        self.image = pygame_gui.elements.UIImage(relative_rect, pygame.transform.scale(sprite, relative_rect.size),
                                                 visible=visible, manager=manager, container=container,
                                                 )
        self.image.disable()
        # The transparent button. This a subclass that UIButton that also hold the cat_id.
        self.button = CatButton(relative_rect, visible=visible, cat_id=cat_id, cat_object=cat_object,
                                starting_height=starting_height, manager=manager, tool_tip_text=tool_tip_text,
                                container=container)

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