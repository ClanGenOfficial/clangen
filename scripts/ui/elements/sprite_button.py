import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.game_input import INPUT_ACTION_PRESSED, INPUT_ACTION_RELEASED, Action
from scripts.game_structure.game import game_setting_get
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.cat_button import CatButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.scale import ui_scale_value, ui_scale


class UISpriteButton:
    """This is for use with the cat sprites. It wraps together a UIImage and Transparent Button.
    For most functions, this can be used exactly like other pygame_gui elements."""

    def __init__(
        self,
        relative_rect: pygame.Rect,
        sprite: pygame.Surface,
        cat_id=None,
        visible=1,
        cat_object=None,
        starting_height=1,
        manager: IUIManagerInterface = None,
        container=None,
        object_id=None,
        tool_tip_object_id=None,
        tool_tip_text=None,
        text_kwargs=None,
        tool_tip_text_kwargs=None,
        anchors=None,
        mask=None,
        mask_padding=None,
    ):
        self.visible = visible
        self.is_focused = False
        self.is_enabled = True

        # The transparent button. This a subclass that UIButton that also hold the cat_id.
        self.button = CatButton(
            relative_rect,
            "",
            text_kwargs=text_kwargs,
            object_id=ObjectID("#cat_button", object_id),
            visible=visible,
            cat_id=cat_id,
            cat_object=cat_object,
            starting_height=starting_height,
            manager=manager,
            tool_tip_text=tool_tip_text,
            tool_tip_object_id=tool_tip_object_id,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            container=container,
            anchors=anchors,
            mask=mask,
            mask_padding=mask_padding,
        )
        input_sprite = sprite.premul_alpha()
        # if it's going to be small on the screen, smoothscale out the crunch
        input_sprite = (
            pygame.transform.smoothscale(input_sprite, relative_rect.size)
            if (
                (
                    relative_rect.height <= ui_scale_value(sprite.get_height())
                    or relative_rect.width <= ui_scale_value(sprite.get_height())
                )
                and not game_setting_get("no sprite antialiasing")
            )
            else pygame.transform.scale(input_sprite, relative_rect.size)
        )
        self.image = pygame_gui.elements.UIImage(
            relative_rect,
            input_sprite,
            visible=visible,
            manager=manager,
            container=container,
            object_id=object_id,
            anchors=anchors,
            starting_height=starting_height,
        )
        del input_sprite
        self.target_indicator = pygame_gui.elements.UIImage(
            pygame.Rect(
                (relative_rect.x, relative_rect.y),
                (relative_rect.width, relative_rect.height),
            ),
            get_box(BoxStyles.TARGET_BOX, (60, 60)),
            container=container,
            starting_height=1,
            manager=MANAGER,
            visible=False,
            anchors={"centerx": "centerx"},
        )
        self.button.join_focus_sets(self.image)
        self.image.check_hover = self.__image_check_hover

    def __image_check_hover(self, time_delta: float, hovered_higher_element: bool):
        return False

    def return_cat_id(self):
        return self.button.return_cat_id()

    def return_cat_object(self):
        return self.button.return_cat_object()

    def focus(self):
        self.is_focused = True
        self.button.focus()
        self.target_indicator.show()

    def unfocus(self):
        self.is_focused = False
        self.button.unfocus()
        self.target_indicator.hide()

    def enable(self):
        self.is_enabled = True
        self.button.enable()
        self.target_indicator.disable()

    def disable(self):
        self.is_enabled = False
        self.button.disable()
        self.target_indicator.enable()

    def hide(self):
        self.visible = False
        self.image.hide()
        self.button.hide()
        self.target_indicator.hide()

    def show(self):
        self.visible = True
        self.image.show()
        self.button.show()
        self.target_indicator.show()

    def kill(self):
        self.button.kill()
        self.image.kill()
        self.target_indicator.kill()
        del self

    def set_image(self, new_image):
        self.image.set_image(new_image)

    """This is to simplify event handling. Rather that writing 
            'if event.ui_element = cat_sprite_object.button'
            you can treat is as any other single pygame UI element and write:
            'if event.ui_element = cat_sprite_object. """

    def __eq__(self, __o: object) -> bool:
        if self.button == __o:
            return True
        else:
            return False

    def get_abs_rect(self):
        return self.button.get_abs_rect()

    def on_hovered(self):
        self.button.on_hovered()
