from math import floor
from typing import Union


def get_arrow(arrow_length: Union[int, float], arrow_left=True):
    if arrow_length == 1:
        return "\u2192" if not arrow_left else "\u2190"

    arrow_body = "\U0001F89C"
    arrow_body_half = "\U0001F89E"
    if not arrow_left:
        arrow_tail = "\u250F"
        arrow_head = "\u2B95"
    else:
        arrow_tail = "\u2513"
        arrow_head = "\u2B05"

    if 1 < arrow_length < 2:
        arrow_length = 2
        print(
            "Invalid arrow length - due to limitations in the font, arrow lengths "
            "between 1 and 2 are impossible. Rounded up to length 2. Sorry!"
        )

    if arrow_length <= 2:
        return arrow_tail + arrow_head if not arrow_left else arrow_head + arrow_tail

    arrow_length = arrow_length - 2
    middle = ""
    if arrow_length % 1 != 0:
        middle += arrow_body_half
        arrow_length = floor(arrow_length)

    return (
        arrow_tail + arrow_body * arrow_length + middle + arrow_head
        if not arrow_left
        else arrow_head + arrow_body * arrow_length + middle + arrow_tail
    )
