import pygame_gui

class CatButton(pygame_gui.elements.UIButton):
    """Basic UIButton subclass for at sprite buttons. It stores the cat ID. """

    def __init__(self, relative_rect, cat_id=None, visible=True, cat_object=None, starting_height=1, manager=None, tool_tip_text=None, container=None):
        self.cat_id = cat_id
        self.cat_object = cat_object
        super().__init__(relative_rect, "", object_id="#cat_button", visible=visible,
                         starting_height=starting_height, manager=manager, tool_tip_text=tool_tip_text, container=container)

    def return_cat_id(self):
        return self.cat_id

    def return_cat_object(self):
        return self.cat_object

    def set_id(self, id):
        self.cat_id = id