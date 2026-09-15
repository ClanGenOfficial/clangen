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


class UISpriteButton(CatButton):
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
        self.cat_image = pygame_gui.elements.UIImage(
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

        # The transparent button. This a subclass of UIButton that also holds the cat_id.
        super().__init__(
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

        self.join_focus_sets(self.cat_image)

    def focus(self):
        super().focus()
        self.target_indicator.show()

    def unfocus(self):
        super().unfocus()
        self.target_indicator.hide()

    def enable(self):
        super().enable()
        self.target_indicator.disable()

    def disable(self):
        super().disable()
        self.target_indicator.enable()

    def hide(self):
        super().hide()
        self.cat_image.hide()
        self.target_indicator.hide()

    def show(self):
        super().show()
        self.cat_image.show()
        self.target_indicator.hide()

    def kill(self):
        self.cat_image.kill()
        self.target_indicator.kill()
        super().kill()
        del self

    def set_image(self, new_image):
        self.cat_image.set_image(new_image)
