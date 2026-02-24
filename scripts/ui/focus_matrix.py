from pygame_gui.core import UIElement


def create_map(element_list: list[UIElement]) -> list[list]:
    """
    Takes the given elements and creates the matrix map of their positions on screen
    :param element_list: The list of interactable elements to map
    :return: The matrix map
    """
    # first we sort out the elements into their rows based on their y pos
    row_mapping: dict[int, list] = {}
    for element in element_list:
        if not row_mapping.get(element.get_abs_rect().y):
            row_mapping[element.get_abs_rect().y] = [element]
        else:
            row_mapping[element.get_abs_rect().y].append(element)

    # then we sort them by their x pos
    for row in row_mapping:
        row_mapping[row].sort(key=lambda x: x.get_abs_rect().x)

    # and now we compile the matrix and return
    return [row for row in row_mapping.values()]


def add_to_map(current_map: list[list], new_elements: list[UIElement]) -> list[list]:
    """
    Takes the given elements and adds them to the map
    :param current_map: The current matrix map
    :param new_elements: The list of interactable elements to add
    :return: The new map
    """
    for element in new_elements:
        # first, find the current y positions represented
        current_rows: dict[int, list] = {}
        for row in current_map:
            current_rows[row[0].get_abs_rect().y] = row

        # then position of the new element
        position = element.get_abs_rect()

        # add the element to an existing row if it's y pos is already represented
        if position.y in current_rows:
            current_rows[position.y].append(element)
            current_rows[position.y].sort(key=lambda x: x.get_abs_rect().x)
        # otherwise, we need to find where it fits into the current matrix
        else:
            # sort within the current row positions
            row_positions = list(current_rows.keys())
            row_positions.append(position.y)
            row_positions.sort()
            # insert it into the actual map according to how we've sorted
            new_row_index = row_positions.index(position.y)
            current_map.insert(new_row_index, [element])

    return current_map