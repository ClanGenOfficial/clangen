from typing import Optional

from pygame_gui.core import UIElement

from scripts.game_input import Action
from scripts.game_structure.game import switch_get_value, Switch
from scripts.ui.scale import ui_scale_value


Y_VARIANCE = 25


def add_to_map(
    current_map: list[list[UIElement]], new_elements: list[UIElement]
) -> list[list]:
    """
    Takes the given elements and adds them to the map.
    The matrix map is a list of lists. Each list is a new "row" within the map.
    We compile the map by checking the y and x coord positioning of each element. Elements with similar y coords will be
    placed in the same row, and their order within that row determined by their x coord (lowest to highest).
    :param current_map: The current matrix map
    :param new_elements: The list of interactable elements to add
    :return: The new map
    """
    # making a copy so we aren't modifying the original list since we're just gonna be returning a new list
    current_map = current_map.copy()

    for element in new_elements:
        # first, find the current y positions represented
        current_rows_by_y_pos: dict[int, list] = {}
        already_present = False
        for row in current_map:
            if element in row:
                already_present = True  # don't add an element that's already there
                break
            for item in row:
                if not item:
                    continue
                current_rows_by_y_pos[item.get_abs_rect().y] = row
                break

        if already_present:
            continue

        # then position of the new element
        position = element.get_abs_rect()

        # first we check if a new row is needed
        new_row = True
        target_row = None
        for row in current_rows_by_y_pos:
            # we allow a 50 px range so that elements which are slightly different y coordinates
            # but still visibly feel side-by-side will be treated as part of the same row
            if (
                (row - ui_scale_value(Y_VARIANCE))
                <= element.get_abs_rect().y
                <= row + ui_scale_value(Y_VARIANCE)
            ):
                new_row = False
                target_row = row
                break
        # now if we need a new row, we find where it should fit
        if new_row:
            # sort within the current row positions
            row_positions = list(current_rows_by_y_pos.keys())
            row_positions.append(position.y)
            row_positions.sort()
            # insert it into the actual map according to how we've sorted
            new_row_index = row_positions.index(position.y)
            current_map.insert(new_row_index, adjust_row([], element))
        # otherwise add the element to an existing row
        else:
            current_rows_by_y_pos[target_row] = adjust_row(
                current_rows_by_y_pos[target_row], element
            )

    return current_map


def remove_from_map(
    current_map: list[list], elements_to_remove: list[UIElement]
) -> list[list]:
    """
    Takes the given elements and removes them from the map
    :param current_map: The current matrix map
    :param elements_to_remove: The list of interactable elements to remove
    :return: The new map
    """
    for element in elements_to_remove:
        # first find where the element is positioned
        element_row: Optional[int] = None
        for row in current_map:
            if element in row:
                element_row = current_map.index(row)
                break

        # if the element isn't present, we warn
        if element_row is None:
            continue

        # then remove it
        index = current_map[element_row].index(element)
        current_map[element_row][index] = None

        # check if it empties a row, if it does, remove the row
        if not current_map[element_row]:
            current_map.pop(element_row)

    return current_map


def adjust_row(
    row: list[Optional[UIElement]], element: UIElement
) -> list[Optional[UIElement]]:
    if not row:  # if row is empty
        row = [None for x in range(int(ui_scale_value(800) / ui_scale_value(10)) + 1)]

    index = int(element.get_abs_rect().x / ui_scale_value(10))

    row.insert(index, element)
    row.pop(index + 1)

    return row


def find_next_focus(
    current_map: list[list], direction: Action, prev_focus_element: UIElement
) -> UIElement:
    """
    Moves focus from one element to the next logical element.
    :param current_map: The current matrix map
    :param direction: The direction in which to look for the next element
    :param prev_focus_element: The element currently in focus that should lose focus
    :return: UIElement that has received focus
    """
    new_row = None
    new_col = None

    # find current location on the map
    prior_row = None
    prior_col = None
    for index, row in enumerate(current_map):
        if prev_focus_element in row:
            prior_row = index
            prior_col = current_map[index].index(prev_focus_element)
            break

    if (
        prior_row is None or prior_col is None
    ):  # specifically NONE, using `if not x or x` will falsely pick up 0 indexes
        raise Exception(
            f"{prev_focus_element} not found in the matrix map. Use self.add_to_map() to add it. If this element shouldn't be interactable, then it was mistakenly given focus!"
        )  # uh oh it must not be in the map and that's a problem!

    # where are we going?
    # if going left or right, let's check if we can!
    change_to_higher_row = False
    change_to_lower_row = False
    if direction in (Action.LEFT, Action.RIGHT):
        # we need to see if there's a valid element to switch to
        if not _valid_row(current_map, prev_focus_element, prior_row):
            # there isn't! so we need to change our row too
            if direction == Action.LEFT:
                # left will go upward
                change_to_higher_row = True
            else:
                # right will go downward
                change_to_lower_row = True

    # going UP!
    if direction == Action.UP or change_to_higher_row:
        while not _valid_row(current_map, prev_focus_element, new_row):
            # find the new row, wrapping if necessary
            if prior_row - 1 < 0:
                new_row = len(current_map) - 1
                # we also move the column to be the farthest right
                new_col = len(current_map[new_row]) - 1
            else:
                new_row = prior_row - 1

            # if we're changing bc of a wrap, we want to predetermine the column
            if change_to_higher_row:
                new_col = len(current_map[new_row]) - 1
                change_to_higher_row = False
            else:
                new_col = prior_col

            prior_row = new_row

    # going DOWN!
    elif direction == Action.DOWN or change_to_lower_row:
        while not _valid_row(current_map, prev_focus_element, new_row):
            # find the new row, wrapping if necessary
            if prior_row + 1 > len(current_map) - 1:
                new_row = 0
                # we also move the column to be the farthest left
                new_col = 0
            else:
                new_row = prior_row + 1

            # if we're changing bc of a wrap, we want to predetermine the column
            if change_to_lower_row:
                new_col = 0
            else:
                new_col = prior_col

            prior_row = new_row

    # if no new row, then the new row is our old one!
    if new_row is None:  # has to be `is None` so that it doesn't pick up 0 indexes
        new_row = prior_row

    # Now to find our new column!
    # going LEFT!
    if direction == Action.LEFT and new_col is None:
        # find the new col, wrapping if necessary
        while _element_is_not_valid(current_map, new_row, new_col):
            if prior_col - 1 < 0:
                new_col = len(current_map[new_row]) - 1
            else:
                new_col = prior_col - 1

            prior_col = new_col

    # going RIGHT!
    elif direction == Action.RIGHT and new_col is None:
        while _element_is_not_valid(current_map, new_row, new_col):
            # find the new col, wrapping if necessary
            if prior_col + 1 > len(current_map[new_row]) - 1:
                new_col = 0
            else:
                new_col = prior_col + 1

            prior_col = new_col

    # if neither, then we keep our column the same IF POSSIBLE
    else:
        if _element_is_not_valid(current_map, new_row, new_col):
            while _element_is_not_valid(current_map, new_row, new_col):
                # find the new col, wrapping if necessary
                if prior_col + 1 > len(current_map[new_row]) - 1:
                    new_col = 0
                else:
                    new_col = prior_col + 1

                prior_col = new_col
        else:
            new_col = prior_col

    new_element = current_map[new_row][new_col]

    _set_focus(new_focus=new_element, old_focus=prev_focus_element)

    # return the element at the newly found indexes!
    return new_element


def _set_focus(new_focus: UIElement, old_focus: Optional[UIElement] = None):
    """
    Sets the given element as focused and unfocuses the prior element.
    :param new_focus: The element to focus
    :param old_focus: The element to unfocus
    """
    if switch_get_value(Switch.keybinds_live):
        if old_focus:
            old_focus.unfocus()
        new_focus.focus()


def _valid_row(current_map, disallowed_element, possible_row) -> list:
    """
    Checks if the given row has a valid element option in it
    :param current_map: The current matrix map
    :param disallowed_element: Generally the currently focused element, this is an element we should ignore the presence of when trying to find a valid row
    :param possible_row: The row we are searching
    :return: The row with all invalid elements removed
    """
    # has to be written this way so that it doesn't misinterpret 0 index rows
    if possible_row is None:
        return []

    row_without_cur_element = current_map[possible_row].copy()
    if disallowed_element in row_without_cur_element:
        row_without_cur_element.remove(disallowed_element)
    for ele in row_without_cur_element.copy():
        if ele is None:
            row_without_cur_element.remove(ele)
            continue
        # remove any disabled or hidden ones, as we don't want to focus those
        if not ele.is_enabled:
            row_without_cur_element.remove(ele)
        if not ele.visible:
            row_without_cur_element.remove(ele)

    return row_without_cur_element


def _element_is_not_valid(current_map, new_row, new_col):
    # needs to be `is None` to avoid picking up 0 index
    if new_col is None or current_map[new_row][new_col] is None:
        return True

    # since new_col is an index, we need to - 1 the len to make them "match"
    # what we're trying to do here is check if the new_col will be a valid index of the new_row
    if len(current_map[new_row]) - 1 < new_col:
        return True

    if (
        not current_map[new_row][new_col].is_enabled
        or not current_map[new_row][new_col].visible
    ):
        return True
    return False
