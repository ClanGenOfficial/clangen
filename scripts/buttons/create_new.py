"""Custom file to create new buttons. This file is not to be used in the game, but rather to be ran via `python scripts/buttons/create_new.py`"""
import json

# https://stackoverflow.com/a/54577313
class CompactJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that puts small lists on single lines."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indentation_level = 0

    def encode(self, o):
        """Encode JSON object *o* with respect to single line lists."""

        if isinstance(o, (list, tuple)):
            if self._is_single_line_list(o):
                return "[" + ", ".join(json.dumps(el) for el in o) + "]"
            else:
                self.indentation_level += 1
                output = [self.indent_str + self.encode(el) for el in o]
                self.indentation_level -= 1
                return "[\n" + ",\n".join(output) + "\n" + self.indent_str + "]"

        elif isinstance(o, dict):
            self.indentation_level += 1
            output = [self.indent_str + f"{json.dumps(k)}: {self.encode(v)}" for k, v in o.items()]
            self.indentation_level -= 1
            return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"

        else:
            return json.dumps(o)

    def _is_single_line_list(self, o):
        if isinstance(o, (list, tuple)):
            return not any(isinstance(el, (list, tuple, dict)) for el in o)\
                   and len(o) <= 4\
                   and len(str(o)) - 4 <= 60

    @property
    def indent_str(self) -> str:
        return " " * self.indentation_level * self.indent
    
    def iterencode(self, o, **kwargs):
        """Required to also work with `json.dump`."""
        return self.encode(o)

def create_button(id: str, 
                      text: str, 
                      rounded_corners: list[bool, bool, bool, bool] = [True, True, True, True],
                      is_hanging: bool = False,
                      shadow_sides: list[bool, bool, bool, bool] = [True, True, False, False],
                      ) -> None:
    """Allows you to create a new button and add the data automatically to styles.json and buttons.en-us.json.

    Args:
        id (str): The #id of the button.
        text (str): The text of the button.
        rounded_corners (list[bool, bool, bool, bool], optional): Determines what corners are rounded. Starts at the top left and goes clockwise. Defaults to [True, True, True, True].
        is_hanging (bool, optional): Determines if a button is "hanging" from the top, used for languages. Defaults to False.
        shadow_sides (list[bool, bool, bool, bool], optional): Determines what sides have shadows. Starts at the left and goes clockwise. Defaults to [True, True, False, False].
    """

    if not id.startswith("#"):
        id = f"#{id}"

    with open("resources/styles.json", "r") as fp:
        styles = json.load(fp)
    styles["rounded"][id] = rounded_corners
    styles["shadow"][id] = shadow_sides
    styles["hanging"][id] = is_hanging
    
    with open("languages/buttons/buttons.en-us.json", "r") as fp:
        buttons = json.load(fp)
    buttons['en-us'][id] = text
    
    with open("resources/styles.json", "w") as fp:
        json.dump(styles, fp, indent=4, cls=CompactJSONEncoder)
    
    with open("languages/buttons/buttons.en-us.json", "w") as fp:
        json.dump(buttons, fp, indent=4, cls=CompactJSONEncoder)
    
def handle_creation() -> None:
    id = input("ID: ")
    if not id.startswith("#"):
        id = f"#{id}"
    
    text = input("Text: ")
    rounded_corners = input("Rounded Corners (starting top left, clockwise) (True, True, True, True): ").split(", ")
    shadow_sides = input("Shadows (starting left, clockwise) (True, True, False, False): ").split(", ")
    is_hanging = input("Is Hanging (true/False): ")
    
    if rounded_corners == ['']: rounded_corners = [True, True, True, True]
    else: rounded_corners = [bool(i) if str(i).lower() in ['true', '1'] else False for i in rounded_corners]

    if is_hanging == '': is_hanging = False
    else: is_hanging = bool(is_hanging) if str(is_hanging).lower() in ['true', '1', 'y'] else False

    if shadow_sides == ['']: shadow_sides = [True, True, False, False]
    else: shadow_sides = [bool(i) if str(i).lower() in ['true', '1'] else False for i in shadow_sides]

    create_button(id, text, rounded_corners, is_hanging, shadow_sides)
    return


def main() -> None:
    while True:
        try: 
            handle_creation()
            cont = input("Button created successfully! Would you like to create another button? (y/N): ")
            if cont.lower() not in ['y', 'yes']: break
        except KeyboardInterrupt:
            break
    
    return

if __name__ == "__main__":
    main()