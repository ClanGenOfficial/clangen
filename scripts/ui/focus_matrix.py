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


