# pylint: disable=line-too-long
"""

TODO: Docs


"""


# pylint: enable=line-too-long
class Single_Event:
    """A class to hold info regarding a single event"""

    def __init__(self, text, types=None, cats_involved=None, cat_dict=None):
        """text: The event text.
        types: Which types of event, in a list or tuple. Current options are:
                "relation", "ceremony", "birth_death", "health", "other_clans", "misc"
        cat_involved: list or tuples of the IDs of cats involved in the event
        cat_dict: dict suitable for event_text_adjust containing the
        """

        self.text = text

        if isinstance(types, str):
            self.types = []
            self.types.append(types)
        elif isinstance(types, list) or isinstance(types, tuple):
            self.types = list(types)
        else:
            self.types = []

        self.cat_dict = cat_dict if cat_dict else {}

        if isinstance(cats_involved, str):
            self.cats_involved = []
            self.cats_involved.append(cats_involved)
        elif isinstance(cats_involved, list) or isinstance(cats_involved, tuple):
            self.cats_involved = list(cats_involved)
        else:
            self.cats_involved = []

        # if cats involved wasn't specified but cats dict was, use that as cats involved
        if self.cat_dict and self.cats_involved == []:
            self.cats_involved = [cat.ID for cat in self.cat_dict.values()]

    def to_dict(self):
        """
        Convert Single_Event to dictionary.
        """
        cat_dict = self.cat_dict.copy() if self.cat_dict else {}
        if self.cat_dict:
            for abbr, kitty in self.cat_dict.items():
                cat_dict[abbr] = kitty.ID

        return {
            "text": self.text,
            "types": self.types,
            "cats_involved": self.cats_involved,
            "cat_dict": cat_dict,
        }

    @staticmethod
    def from_dict(dict, Cat):
        """
        Return new Single_Event based on dict.

        dict: The dictionary to convert to Single_Event.
        """

        if "text" not in dict:
            return None

        cat_dict = dict.get("cat_dict", None)
        if cat_dict:
            for abbr, kitty in cat_dict.copy().items():
                cat_dict[abbr] = Cat.fetch_cat(kitty)

        return Single_Event(
            text=dict["text"],
            types=dict.get("types", None),
            cats_involved=dict.get("cats_involved", None),
            cat_dict=cat_dict,
        )
