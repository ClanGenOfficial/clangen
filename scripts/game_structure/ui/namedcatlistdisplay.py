import pygame
import pygame_gui
from pygame_gui.core import UIContainer
from pygame_gui.core.gui_type_hints import RectLike

from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import UIBasicCatListDisplay, UIImageButton
from scripts.utility import scale, shorten_text_to_fit


class UINamedCatListDisplay(UIBasicCatListDisplay):
    """
    Creates and displays a list of click-able cat sprites.
    :param relative_rect: The starting size and relative position of the container.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param object_id: An object ID for this element.
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param cat_list: the list of cat objects that need to display
    :param cats_displayed: the number of cats to display on one page
    :param x_px_between: the pixel space between each cat sprite on the x-axis
    :param y_px_between: the pixel space between each cat sprite on the y-axis
    :param columns: the number of cats in a row before a new row is created
    :param next_button: the next_button ui_element
    :param prev_button: the prev_button ui_element
    :param current_page: the currently displayed page of the cat list
    :param text_theme: the theme to use when creating name text
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        container: UIContainer,
        starting_height: int,
        object_id: str,
        manager,
        cat_list: list,
        cats_displayed: int,
        x_px_between: int,
        y_px_between: int,
        columns: int,
        text_theme: str,
        current_page: int,
        next_button: UIImageButton,
        prev_button: UIImageButton,
        first_button: UIImageButton = None,
        last_button: UIImageButton = None,
        visible: bool = True,
    ):

        self.x_px_between = x_px_between
        self.y_px_between = y_px_between
        self.text_theme = text_theme

        self.cat_names = {}

        super().__init__(
            relative_rect,
            container,
            starting_height,
            object_id,
            manager,
            cat_list,
            cats_displayed,
            x_px_between,
            columns,
            current_page,
            next_button,
            prev_button,
            first_button,
            last_button,
            visible=visible,
        )

    def clear_display(self):
        for ele in self.cat_sprites:
            self.cat_sprites[ele].kill()
        for ele in self.cat_names:
            self.cat_names[ele].kill()
        for ele in self.favor_indicator:
            self.favor_indicator[ele].kill()
        self.next_button = None
        self.prev_button = None
        self.first_button = None
        self.last_button = None

    def _display_cats(self):
        """
        creates the cat display
        """
        self.current_page = max(1, min(self.current_page, len(self.cat_chunks)))

        self._update_arrow_buttons()

        display_cats = []
        if self.cat_chunks:
            self.total_pages = len(self.cat_chunks)
            display_cats = self.cat_chunks[self.current_page - 1]

        for ele in self.cat_sprites:
            self.cat_sprites[ele].kill()
        for ele in self.cat_names:
            self.cat_names[ele].kill()
        for ele in self.favor_indicator:
            self.favor_indicator[ele].kill()

        pos_x = self.x_px_between
        pos_y = self.y_px_between

        for i, kitty in enumerate(display_cats):
            if game.clan.clan_settings["show fav"] and kitty.favourite:
                self.create_favor_indicator(i, pos_x, pos_y)

            self.create_cat_button(i, kitty, pos_x, pos_y)

            self.cat_names[f"name{i}"] = pygame_gui.elements.UILabel(
                scale(
                    pygame.Rect(
                        (pos_x - self.x_px_between / 2, pos_y + 100),
                        (100 + self.x_px_between, 60),
                    )
                ),
                shorten_text_to_fit(str(kitty.name), 220, 30),
                container=self,
                object_id=self.text_theme,
            )

            # changing position
            pos_x += self.x_px_between
            if pos_x > (self.x_px_between * self.columns):
                pos_x = self.x_px_between
                pos_y += self.y_px_between
